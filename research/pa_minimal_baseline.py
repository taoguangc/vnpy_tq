# -*- coding: utf-8 -*-
"""pa_minimal 第二阶段：冻结 M0-BASE 基线、cohort 与 IS/OOS 协议。

另含稳定 Alpha 研究不可变协议 ALPHA_PROTOCOL_V1（见 research/ALPHA_PROTOCOL.md）。
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from strategies.pa_cta.symbol_config import CROSS_SYMBOL_UNIVERSE
from strategies.pa_minimal.symbol_config import MINIMAL_BASE_PROFILE, resolve_minimal_profile

# 与 EXP-M0-ISOOS / plan 一致
WINDOW_START = datetime(2023, 5, 17)
WINDOW_END = datetime(2026, 5, 16, 23, 59, 59)
IS_START = datetime(2023, 5, 17)
IS_END = datetime(2024, 12, 31, 23, 59, 59)
OOS_START = datetime(2025, 1, 1)
OOS_END = datetime(2026, 5, 16, 23, 59, 59)

OOS_MIN_N = 8
OOS_PROMOTE_N = 15

SIZING_TIERS: tuple[tuple[str, int], ...] = (
    ("LOW", 10),
    ("MID", 25),
    ("CURRENT", 50),
)

COST_RATE = 0.00003

# ---------------------------------------------------------------------------
# ALPHA_PROTOCOL_V1 — 稳定 Alpha 研究冻结协议（不可调阈值）
# ---------------------------------------------------------------------------
ALPHA_PROTOCOL_VERSION = "ALPHA_PROTOCOL_V1"
ALPHA_OPP_CODES: tuple[str, ...] = (
    "OPP02",
    "OPP08",
    "OPP12",
    "OPP13",
    "OPP15",
    "OPP16",
    "OPP17",
    "OPP19",
)
ALPHA_SYMBOL_UNIVERSE: tuple[str, ...] = tuple(CROSS_SYMBOL_UNIVERSE)
ALPHA_PRIMARY_HORIZON_M = 40
ALPHA_HORIZONS_M: tuple[int, ...] = (10, 20, 40, 80)
ALPHA_EMBARGO_MINUTES = 80
# 2025–2026 已被反复查看 → 仅开发验证；真正 CONFIRMED 须新数据
ALPHA_FORWARD_HOLDOUT_START = datetime(2026, 5, 17)
ALPHA_CONFIRM_MIN_TRADES = 30
ALPHA_CONFIRM_MIN_MONTHS = 6

# 全 OPP shadow：开全部检测器，禁止真实武装/成交
ALPHA_SHADOW_OVERRIDES: dict[str, Any] = {
    "alpha_shadow_mode": True,
    "ema_pullback_enabled": True,       # OPP02
    "two_bar_rev_enabled": True,        # OPP16
    "overshoot_fail_enabled": True,     # OPP12
    "day_boundary_enabled": True,       # OPP13
    "wedge_enabled": True,              # OPP15
    "climax_rev_enabled": True,         # OPP17
    "opening_drive_enabled": True,      # OPP19
    "opening_rev_enabled": True,
    "candidate_ledger_enabled": True,
    "shadow_ledger_enabled": False,
    "dryscan_compare_enabled": False,
    "context_layer_gate_enabled": False,
}

# 暂定稳定候选门禁（PROMOTE_TO_CTA）
ALPHA_GATE_MIN_OOS_N = 50
ALPHA_GATE_MIN_SYMBOLS = 4
ALPHA_GATE_MIN_HALF_FOLDS = 4
ALPHA_GATE_BOOTSTRAP_LB = 0.0
ALPHA_GATE_BOOTSTRAP_Q = 0.10
ALPHA_GATE_FOLD_POS_RATIO = 0.70
ALPHA_GATE_LOSO_NONNEG = 5
ALPHA_GATE_MAX_CONCENTRATION = 0.35

# CTA KEEP 门禁
CTA_KEEP_MIN_RT = 30
CTA_KEEP_MIN_PF = 1.15

_DETECTOR_FILES: tuple[str, ...] = (
    "strategies/pa_minimal/detectors/schema.py",
    "strategies/pa_minimal/detectors/opp02.py",
    "strategies/pa_minimal/detectors/opp08.py",
    "strategies/pa_minimal/detectors/opp12.py",
    "strategies/pa_minimal/detectors/opp13.py",
    "strategies/pa_minimal/detectors/opp15.py",
    "strategies/pa_minimal/detectors/opp16.py",
    "strategies/pa_minimal/detectors/opp17.py",
    "strategies/pa_minimal/detectors/opp19.py",
)


def _file_fingerprint(root: Path, rel: str) -> str:
    path = root / rel
    raw = path.read_bytes() if path.exists() else b""
    return hashlib.sha256(raw).hexdigest()[:16]


def opp_code_fingerprint(root: Path) -> str:
    """8 个 OPP 检测器源码联合指纹（阈值冻结校验用）。"""
    h = hashlib.sha256()
    for rel in _DETECTOR_FILES:
        h.update(rel.encode())
        h.update((root / rel).read_bytes() if (root / rel).exists() else b"")
    return h.hexdigest()[:16]


def param_fingerprint(profile: dict | None = None) -> str:
    return _profile_fingerprint(profile or MINIMAL_BASE_PROFILE)


def build_alpha_protocol_manifest(root: Path) -> dict[str, Any]:
    """不可变协议快照：窗口 / 成本 / 品种池 / OPP 与参数指纹。"""
    profile = resolve_minimal_profile("rb", root)
    return {
        "version": ALPHA_PROTOCOL_VERSION,
        "frozen_at": datetime.now().isoformat(timespec="seconds"),
        "window": {
            "start": str(WINDOW_START.date()),
            "end": str(WINDOW_END.date()),
            "note": "开发验证窗；不得标 CONFIRMED_ALPHA",
        },
        "forward_holdout_start": str(ALPHA_FORWARD_HOLDOUT_START.date()),
        "symbols": list(ALPHA_SYMBOL_UNIVERSE),
        "opp_codes": list(ALPHA_OPP_CODES),
        "opp_code_fingerprint": opp_code_fingerprint(root),
        "param_fingerprint": param_fingerprint(profile),
        "detector_files": {rel: _file_fingerprint(root, rel) for rel in _DETECTOR_FILES},
        "cost": {
            "rate": COST_RATE,
            "slippage_ticks_from_profile": True,
            "sizing": "1_lot_economic_edge",
        },
        "horizons_m": list(ALPHA_HORIZONS_M),
        "primary_horizon_m": ALPHA_PRIMARY_HORIZON_M,
        "embargo_minutes": ALPHA_EMBARGO_MINUTES,
        "shadow_overrides": dict(ALPHA_SHADOW_OVERRIDES),
        "gates": {
            "min_oos_n": ALPHA_GATE_MIN_OOS_N,
            "min_symbols": ALPHA_GATE_MIN_SYMBOLS,
            "min_half_folds": ALPHA_GATE_MIN_HALF_FOLDS,
            "bootstrap_q": ALPHA_GATE_BOOTSTRAP_Q,
            "bootstrap_lb": ALPHA_GATE_BOOTSTRAP_LB,
            "fold_pos_ratio": ALPHA_GATE_FOLD_POS_RATIO,
            "loso_nonneg": ALPHA_GATE_LOSO_NONNEG,
            "max_concentration": ALPHA_GATE_MAX_CONCENTRATION,
        },
        "cta_keep": {
            "min_rt": CTA_KEEP_MIN_RT,
            "min_pf": CTA_KEEP_MIN_PF,
            "oos_pnl_gt_0": True,
        },
        "labels_allowed": ["REJECT", "PROVISIONAL", "PROMOTE_TO_CTA"],
        "confirmed_requires": {
            "holdout_start": str(ALPHA_FORWARD_HOLDOUT_START.date()),
            "min_trades": ALPHA_CONFIRM_MIN_TRADES,
            "min_months": ALPHA_CONFIRM_MIN_MONTHS,
        },
        "audit_notes": [
            "OPP13 day_high FIRST_TEST 返回 True 会提前结束同 bar 其他 OPP 扫描（live）；shadow 模式不提前返回。",
            "OPP19 _process_opening_drive 在 _arm_fast_track 后恒返回 True，即使门禁未过；shadow 用 alpha_shadow_mode 禁止 commit。",
            "OPP15/13 状态推进与 detectors 并存：状态机负责武装副作用，detectors 负责只读命中。",
            "DIRECT（OPP15 B'）与 PENDING_CONFIRM/FAST_TRACK 成交语义不同；shadow 用 trigger≈入场价估计边际。",
            "同 bar 撮合：信号在 5m，风控在 1m；候选 forward 自信号时刻下一根 1m 起算。",
        ],
    }


def cohort_path(out_dir: Path, symbol: str) -> Path:
    return out_dir / f"frozen_cohort_{symbol.lower()}.csv"


def manifest_path(out_dir: Path, symbol: str) -> Path:
    return out_dir / f"frozen_manifest_{symbol.lower()}.json"


def _profile_fingerprint(profile: dict) -> str:
    keys = sorted(MINIMAL_BASE_PROFILE.keys())
    blob = json.dumps({k: profile.get(k, MINIMAL_BASE_PROFILE.get(k)) for k in keys}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def build_manifest(symbol: str, root: Path, cohort_df: pd.DataFrame) -> dict[str, Any]:
    profile = resolve_minimal_profile(symbol, root)
    by_setup = cohort_df["setup"].value_counts().to_dict() if "setup" in cohort_df.columns else {}
    return {
        "version": "phase2-v1",
        "symbol": symbol.lower(),
        "frozen_at": datetime.now().isoformat(timespec="seconds"),
        "window": {"start": str(WINDOW_START.date()), "end": str(WINDOW_END.date())},
        "is_oos": {
            "is_start": str(IS_START.date()),
            "is_end": str(IS_END.date()),
            "oos_start": str(OOS_START.date()),
            "oos_end": str(OOS_END.date()),
        },
        "baseline": "M0-BASE",
        "profile_fingerprint": _profile_fingerprint(profile),
        "cost": {
            "rate": COST_RATE,
            "slippage": float(profile["slippage"]),
            "contract_size": float(profile["size"]),
            "pricetick": float(profile["pricetick"]),
            "risk_capital": float(profile.get("risk_capital", 10_000)),
            "risk_pct_per_trade": float(profile.get("risk_pct_per_trade", 0.05)),
            "max_position_default": int(profile.get("max_position", 50)),
        },
        "cohort": {
            "n_total": int(len(cohort_df)),
            "n_gate_pass": int(cohort_df["gate_pass"].sum()) if "gate_pass" in cohort_df.columns else int(len(cohort_df)),
            "by_setup": {str(k): int(v) for k, v in by_setup.items()},
        },
    }


def export_frozen_cohort(
    records: list[dict],
    *,
    symbol: str,
    root: Path,
    out_dir: Path,
) -> tuple[Path, Path]:
    """导出 gate_pass 候选为冻结 cohort + manifest。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    gate = [r for r in records if r.get("gate_pass")]
    df = pd.DataFrame(gate)
    cpath = cohort_path(out_dir, symbol)
    df.to_csv(cpath, index=False, encoding="utf-8-sig")
    manifest = build_manifest(symbol, root, df)
    mpath = manifest_path(out_dir, symbol)
    mpath.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return cpath, mpath


def load_frozen_cohort(out_dir: Path, symbol: str) -> pd.DataFrame:
    path = cohort_path(out_dir, symbol)
    if not path.exists():
        raise FileNotFoundError(f"冻结 cohort 不存在: {path}")
    return pd.read_csv(path)


def split_by_time(df: pd.DataFrame, time_col: str = "time") -> tuple[pd.DataFrame, pd.DataFrame]:
    """按信号时间切 IS/OOS。"""
    if time_col not in df.columns:
        return df.iloc[0:0], df.iloc[0:0]
    ts = pd.to_datetime(df[time_col])
    if ts.dt.tz is not None:
        is_start = pd.Timestamp(IS_START, tz=ts.dt.tz)
        is_end = pd.Timestamp(IS_END, tz=ts.dt.tz)
        oos_start = pd.Timestamp(OOS_START, tz=ts.dt.tz)
        oos_end = pd.Timestamp(OOS_END, tz=ts.dt.tz)
    else:
        is_start = pd.Timestamp(IS_START)
        is_end = pd.Timestamp(IS_END)
        oos_start = pd.Timestamp(OOS_START)
        oos_end = pd.Timestamp(OOS_END)
    is_mask = (ts >= is_start) & (ts <= is_end)
    oos_mask = (ts >= oos_start) & (ts <= oos_end)
    return df.loc[is_mask].copy(), df.loc[oos_mask].copy()


def gate_verdict(
    *,
    is_delta: float,
    oos_delta: float,
    is_n: int,
    oos_n: int,
    baseline_pf: float,
    variant_pf: float,
    trades_retained: float,
) -> str:
    """OOS 门禁判定：KEEP / HOLD / REVERT / UNKNOWN。"""
    if oos_n < OOS_MIN_N:
        return "UNKNOWN"
    if trades_retained < 0.5:
        return "REVERT"
    if oos_delta <= 0 or variant_pf < baseline_pf:
        return "REVERT"
    if is_delta <= 0:
        return "HOLD"
    if oos_n >= OOS_PROMOTE_N:
        return "KEEP"
    return "HOLD"
