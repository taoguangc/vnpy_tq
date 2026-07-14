# -*- coding: utf-8
"""Phase-4 setup 风险软收缩：Bayesian / 分层收缩，替代小样本硬禁菜单。

原则（见 research/experiments.md EXP-029）：
  - 样本不足 → 统一 0.5 风险乘子，不禁单
  - 跨窗口/跨品种同类有效 → 逐步升至 1.0
  - 仅 OOS 明确负期望 → 才标记禁用候选
  - 「未知」≠「应禁」
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class ShrinkageConfig:
    """分层收缩超参。"""

    prior_strength_local: float = 15.0
    prior_strength_class: float = 25.0
    prior_strength_global: float = 40.0
    unknown_mult: float = 0.5
    mult_floor: float = 0.5
    mult_ceiling: float = 1.0
    min_n_unknown: int = 10
    min_n_disable: int = 15
    min_n_full: int = 30
    oos_negative_r: float = -0.20
    positive_r_for_boost: float = 0.05


@dataclass
class SetupObs:
    setup: str
    mean_r: float
    n: int
    net_pnl: float = 0.0


@dataclass
class ShrinkageResult:
    setup: str
    setup_class: str
    n_local: int
    n_class: int
    mean_r_local: float
    mean_r_class: float
    mean_r_global: float
    shrunk_r: float
    risk_mult: float
    action: str
    disable_candidate: bool = False


def setup_class_prefix(setup: str) -> str:
    """OPP13_5M_RANGE_FAIL_LOW → OPP13_。"""
    name = setup or ""
    parts = name.split("_")
    if parts and parts[0].startswith("OPP"):
        return f"{parts[0]}_"
    return name


def _weighted_mean(items: Sequence[tuple[float, int]]) -> tuple[float, int]:
    if not items:
        return 0.0, 0
    total_n = sum(n for _, n in items)
    if total_n <= 0:
        return 0.0, 0
    mean = sum(m * n for m, n in items) / total_n
    return mean, total_n


def _shrink(obs_mean: float, n: int, parent_mean: float, k: float) -> float:
    if n <= 0:
        return parent_mean
    w = n / (n + max(k, 1e-6))
    return w * obs_mean + (1.0 - w) * parent_mean


def aggregate_observations(
    records: Iterable[Mapping[str, object]],
    *,
    r_key: str = "r_multiple",
    setup_key: str = "setup",
    pnl_key: str = "net_pnl",
) -> list[SetupObs]:
    """从 trade_log / round_trips 聚合 per-setup 观测。"""
    acc_r: dict[str, list[float]] = {}
    acc_pnl: dict[str, float] = {}
    for rec in records:
        setup = str(rec.get(setup_key) or "UNKNOWN")
        if setup == "UNKNOWN":
            continue
        r = rec.get(r_key)
        if r is None:
            init_r = float(rec.get("initial_r_yuan") or 0.0)
            net = float(rec.get(pnl_key) or rec.get("gross_pnl") or 0.0)
            r = net / init_r if init_r > 0 else 0.0
        acc_r.setdefault(setup, []).append(float(r))
        acc_pnl[setup] = acc_pnl.get(setup, 0.0) + float(rec.get(pnl_key) or 0.0)
    out: list[SetupObs] = []
    for setup, rs in acc_r.items():
        out.append(SetupObs(setup=setup, mean_r=float(sum(rs) / len(rs)), n=len(rs), net_pnl=acc_pnl.get(setup, 0.0)))
    return out


def compute_class_pools(local: Sequence[SetupObs]) -> dict[str, tuple[float, int]]:
    buckets: dict[str, list[tuple[float, int]]] = {}
    for obs in local:
        cls = setup_class_prefix(obs.setup)
        buckets.setdefault(cls, []).append((obs.mean_r, obs.n))
    return {cls: _weighted_mean(items) for cls, items in buckets.items()}


def compute_global_pool(
    local: Sequence[SetupObs],
    extra_pools: Sequence[Sequence[SetupObs]] = (),
) -> tuple[float, int]:
    items: list[tuple[float, int]] = [(o.mean_r, o.n) for o in local]
    for pool in extra_pools:
        items.extend((o.mean_r, o.n) for o in pool)
    return _weighted_mean(items)


def shrink_setup_table(
    local: Sequence[SetupObs],
    *,
    class_pools: Mapping[str, tuple[float, int]] | None = None,
    global_pool: tuple[float, int] | None = None,
    oos_local: Sequence[SetupObs] | None = None,
    cfg: ShrinkageConfig | None = None,
) -> dict[str, ShrinkageResult]:
    """分层收缩：local → class → global。"""
    cfg = cfg or ShrinkageConfig()
    local_list = list(local)
    cls_pools = dict(class_pools or compute_class_pools(local_list))
    g_mean, g_n = global_pool if global_pool else compute_global_pool(local_list)

    oos_map = {o.setup: o for o in (oos_local or [])}

    results: dict[str, ShrinkageResult] = {}
    seen: set[str] = set()
    for obs in local_list:
        seen.add(obs.setup)
        cls = setup_class_prefix(obs.setup)
        c_mean, c_n = cls_pools.get(cls, (g_mean, 0))
        stage1 = _shrink(obs.mean_r, obs.n, c_mean, cfg.prior_strength_class)
        shrunk_r = _shrink(stage1, obs.n + c_n, g_mean, cfg.prior_strength_global)

        oos = oos_map.get(obs.setup)
        disable_candidate = False
        if oos and oos.n >= cfg.min_n_disable and oos.mean_r <= cfg.oos_negative_r:
            disable_candidate = True

        risk_mult, action = _risk_mult_from_shrunk(
            shrunk_r=shrunk_r,
            n_local=obs.n,
            n_class=c_n,
            disable_candidate=disable_candidate,
            cfg=cfg,
        )
        results[obs.setup] = ShrinkageResult(
            setup=obs.setup,
            setup_class=cls,
            n_local=obs.n,
            n_class=c_n,
            mean_r_local=obs.mean_r,
            mean_r_class=c_mean,
            mean_r_global=g_mean,
            shrunk_r=shrunk_r,
            risk_mult=risk_mult,
            action=action,
            disable_candidate=disable_candidate,
        )

    for setup, oos in oos_map.items():
        if setup in seen:
            continue
        cls = setup_class_prefix(setup)
        c_mean, c_n = cls_pools.get(cls, (g_mean, 0))
        shrunk_r = _shrink(oos.mean_r, oos.n, _shrink(c_mean, c_n, g_mean, cfg.prior_strength_class), cfg.prior_strength_global)
        disable_candidate = oos.n >= cfg.min_n_disable and oos.mean_r <= cfg.oos_negative_r
        risk_mult, action = _risk_mult_from_shrunk(
            shrunk_r=shrunk_r, n_local=0, n_class=c_n,
            disable_candidate=disable_candidate, cfg=cfg,
        )
        results[setup] = ShrinkageResult(
            setup=setup, setup_class=cls, n_local=0, n_class=c_n,
            mean_r_local=0.0, mean_r_class=c_mean, mean_r_global=g_mean,
            shrunk_r=shrunk_r, risk_mult=risk_mult, action=action,
            disable_candidate=disable_candidate,
        )
    return results


def _risk_mult_from_shrunk(
    *,
    shrunk_r: float,
    n_local: int,
    n_class: int,
    disable_candidate: bool,
    cfg: ShrinkageConfig,
) -> tuple[float, str]:
    if disable_candidate:
        return 0.0, "DISABLE_CANDIDATE"

    effective_n = n_local if n_local > 0 else n_class
    if effective_n < cfg.min_n_unknown:
        return cfg.unknown_mult, "UNKNOWN_HALF"

    if shrunk_r <= 0:
        mult = cfg.mult_floor
        return mult, "SHRINK_LOW"

    boost = min(1.0, effective_n / max(cfg.min_n_full, 1))
    if shrunk_r >= cfg.positive_r_for_boost and n_class >= cfg.min_n_unknown:
        mult = cfg.mult_floor + (cfg.mult_ceiling - cfg.mult_floor) * boost
        return min(cfg.mult_ceiling, mult), "BOOST"

    mult = cfg.mult_floor + (cfg.mult_ceiling - cfg.mult_floor) * 0.5 * boost
    return mult, "SHRINK_MID"


def parse_shrinkage_overrides(raw: str) -> list[tuple[str, float]]:
    """解析 profile 字符串：``OPP13_=0.5,OPP15_=0.5,default=0.5``。"""
    if not raw or not str(raw).strip():
        return []
    out: list[tuple[str, float]] = []
    for part in str(raw).split(","):
        part = part.strip()
        if not part or "=" not in part:
            continue
        key, val = part.split("=", 1)
        key = key.strip()
        try:
            out.append((key, float(val.strip())))
        except ValueError:
            continue
    return out


def lookup_shrinkage_mult(setup: str, overrides: Sequence[tuple[str, float]], default: float) -> float:
    name = setup or ""
    for prefix, mult in overrides:
        if prefix.lower() == "default":
            continue
        p = prefix.rstrip("*").rstrip("_")
        if name.startswith(p) or name.startswith(f"{p}_"):
            return mult
    for prefix, mult in overrides:
        if prefix.lower() == "default":
            return mult
    return default


def overrides_from_results(
    results: Mapping[str, ShrinkageResult],
    *,
    aggregate_class: bool = True,
) -> str:
    """生成可写入 profile 的 overrides 字符串（类级聚合）。"""
    if aggregate_class:
        by_cls: dict[str, list[float]] = {}
        for res in results.values():
            by_cls.setdefault(res.setup_class, []).append(res.risk_mult)
        parts = []
        for cls in sorted(by_cls):
            mult = min(by_cls[cls])
            parts.append(f"{cls.rstrip('_')}={mult:.2f}")
        return ",".join(parts)
    return ",".join(f"{k}={v.risk_mult:.2f}" for k, v in sorted(results.items()))


def results_to_json(results: Mapping[str, ShrinkageResult]) -> str:
    payload = {
        k: {
            "setup_class": v.setup_class,
            "n_local": v.n_local,
            "n_class": v.n_class,
            "mean_r_local": round(v.mean_r_local, 4),
            "shrunk_r": round(v.shrunk_r, 4),
            "risk_mult": v.risk_mult,
            "action": v.action,
            "disable_candidate": v.disable_candidate,
        }
        for k, v in results.items()
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
