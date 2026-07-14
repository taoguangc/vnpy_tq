# -*- coding: utf-8 -*-
"""pa_minimal 稳定 Alpha：时间折 / 留一品种 / 区块 bootstrap / 集中度门禁。

标签仅允许：REJECT | PROVISIONAL | PROMOTE_TO_CTA
禁止直接输出「稳定 alpha」或 CONFIRMED_ALPHA（须未来 holdout，见 ALPHA_PROTOCOL.md）。
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from research.pa_minimal_baseline import (
    ALPHA_EMBARGO_MINUTES,
    ALPHA_GATE_BOOTSTRAP_LB,
    ALPHA_GATE_BOOTSTRAP_Q,
    ALPHA_GATE_FOLD_POS_RATIO,
    ALPHA_GATE_LOSO_NONNEG,
    ALPHA_GATE_MAX_CONCENTRATION,
    ALPHA_GATE_MIN_HALF_FOLDS,
    ALPHA_GATE_MIN_OOS_N,
    ALPHA_GATE_MIN_SYMBOLS,
    ALPHA_OPP_CODES,
    ALPHA_PRIMARY_HORIZON_M,
    ALPHA_PROTOCOL_VERSION,
    OOS_END,
    OOS_START,
    WINDOW_END,
    WINDOW_START,
)

NET_R_COL = f"fwd_{ALPHA_PRIMARY_HORIZON_M}m_net_r"
NET_YUAN_COL = f"fwd_{ALPHA_PRIMARY_HORIZON_M}m_net"


def setup_family(setup: str) -> str:
    s = str(setup).upper()
    for code in ALPHA_OPP_CODES:
        if s.startswith(code):
            return code
    return "OTHER"


def half_year_label(ts: pd.Timestamp) -> str:
    y = int(ts.year)
    h = 1 if int(ts.month) <= 6 else 2
    return f"{y}H{h}"


def prepare_candidates(df: pd.DataFrame, *, gate_pass_only: bool = True) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    out = df.copy()
    out["time"] = pd.to_datetime(out["time"], errors="coerce")
    out = out.dropna(subset=["time"])
    out["opp_family"] = out["setup"].map(setup_family)
    out["direction"] = out["direction"].astype(int)
    out["symbol"] = out["symbol"].astype(str).str.lower()
    out["half_fold"] = out["time"].map(half_year_label)
    out["ym"] = out["time"].dt.strftime("%Y-%m")
    if gate_pass_only and "gate_pass" in out.columns:
        out = out.loc[out["gate_pass"].astype(bool)].copy()
    # 开发窗裁剪
    t0 = pd.Timestamp(WINDOW_START)
    t1 = pd.Timestamp(WINDOW_END)
    if out["time"].dt.tz is not None:
        t0 = t0.tz_localize(out["time"].dt.tz)
        t1 = t1.tz_localize(out["time"].dt.tz)
    out = out.loc[(out["time"] >= t0) & (out["time"] <= t1)].copy()
    if NET_R_COL not in out.columns:
        out[NET_R_COL] = 0.0
    if NET_YUAN_COL not in out.columns:
        out[NET_YUAN_COL] = 0.0
    return out.reset_index(drop=True)


def apply_embargo(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    """测试折内去掉与训练末信号重叠的 embargo 窗口候选。"""
    if train.empty or test.empty:
        return test
    last_train = train["time"].max()
    cut = last_train + pd.Timedelta(minutes=ALPHA_EMBARGO_MINUTES)
    return test.loc[test["time"] >= cut].copy()


def rolling_half_year_folds(df: pd.DataFrame) -> list[tuple[str, pd.DataFrame, pd.DataFrame]]:
    folds = sorted(df["half_fold"].unique())
    out: list[tuple[str, pd.DataFrame, pd.DataFrame]] = []
    for i in range(len(folds) - 1):
        tr_lab, te_lab = folds[i], folds[i + 1]
        train = df.loc[df["half_fold"] == tr_lab]
        test = apply_embargo(train, df.loc[df["half_fold"] == te_lab])
        out.append((f"{tr_lab}->{te_lab}", train, test))
    return out


def block_bootstrap_mean_lb(
    values: np.ndarray,
    blocks: np.ndarray,
    *,
    q: float = ALPHA_GATE_BOOTSTRAP_Q,
    n_boot: int = 1000,
    seed: int = 42,
) -> float:
    """按月区块 bootstrap，返回均值的下侧分位。"""
    if len(values) == 0:
        return float("nan")
    rng = np.random.default_rng(seed)
    uniq = np.unique(blocks)
    if len(uniq) == 0:
        return float("nan")
    block_map = {b: values[blocks == b] for b in uniq}
    means = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        drawn = []
        for b in rng.choice(uniq, size=len(uniq), replace=True):
            drawn.append(block_map[b])
        sample = np.concatenate(drawn) if drawn else np.array([0.0])
        means[i] = float(np.mean(sample)) if len(sample) else 0.0
    return float(np.quantile(means, q))


def concentration_share(df: pd.DataFrame, group_col: str, value_col: str) -> float:
    pos = df.loc[df[value_col] > 0, [group_col, value_col]]
    if pos.empty:
        return 0.0
    by = pos.groupby(group_col)[value_col].sum()
    total = float(by.sum())
    if total <= 0:
        return 0.0
    return float(by.max() / total)


@dataclass
class StabilityResult:
    opp_family: str
    direction: int
    label: str
    n: int = 0
    n_symbols: int = 0
    n_half_folds: int = 0
    mean_net_r: float = 0.0
    mean_net_yuan: float = 0.0
    bootstrap_lb: float = float("nan")
    fold_pos_ratio: float = 0.0
    loso_nonneg: int = 0
    max_symbol_share: float = 0.0
    max_month_share: float = 0.0
    drop_top1_trade_mean_r: float = 0.0
    drop_top1_month_mean_r: float = 0.0
    reasons: list[str] = field(default_factory=list)
    fold_means: dict[str, float] = field(default_factory=dict)
    loso_means: dict[str, float] = field(default_factory=dict)

    def to_row(self) -> dict[str, Any]:
        d = asdict(self)
        d["reasons"] = ";".join(self.reasons)
        d["fold_means"] = json_dumps(self.fold_means)
        d["loso_means"] = json_dumps(self.loso_means)
        return d


def json_dumps(obj: dict) -> str:
    import json

    return json.dumps({str(k): round(float(v), 4) for k, v in obj.items()}, ensure_ascii=False)


def evaluate_slice(df: pd.DataFrame, opp_family: str, direction: int) -> StabilityResult:
    sub = df.loc[(df["opp_family"] == opp_family) & (df["direction"] == direction)].copy()
    res = StabilityResult(opp_family=opp_family, direction=direction, label="REJECT")
    if sub.empty:
        res.reasons.append("empty")
        return res

    res.n = int(len(sub))
    res.n_symbols = int(sub["symbol"].nunique())
    res.n_half_folds = int(sub["half_fold"].nunique())
    res.mean_net_r = float(sub[NET_R_COL].mean())
    res.mean_net_yuan = float(sub[NET_YUAN_COL].mean())
    res.bootstrap_lb = block_bootstrap_mean_lb(
        sub[NET_R_COL].to_numpy(dtype=float),
        sub["ym"].to_numpy(),
    )
    res.max_symbol_share = concentration_share(sub, "symbol", NET_YUAN_COL)
    res.max_month_share = concentration_share(sub, "ym", NET_YUAN_COL)

    # 半年滚动折：各测试折均值
    fold_means: dict[str, float] = {}
    for name, _tr, te in rolling_half_year_folds(sub):
        if te.empty:
            continue
        fold_means[name] = float(te[NET_R_COL].mean())
    res.fold_means = fold_means
    if fold_means:
        pos = sum(1 for v in fold_means.values() if v > 0)
        res.fold_pos_ratio = pos / len(fold_means)
    else:
        res.fold_pos_ratio = 0.0

    # leave-one-symbol-out：留出品种上的均值
    symbols = sorted(sub["symbol"].unique())
    loso: dict[str, float] = {}
    for held in symbols:
        held_df = sub.loc[sub["symbol"] == held]
        loso[held] = float(held_df[NET_R_COL].mean()) if not held_df.empty else 0.0
    res.loso_means = loso
    res.loso_nonneg = sum(1 for v in loso.values() if v >= 0)

    # 去最大 1 笔 / 最大 1 月
    if res.n >= 2:
        drop_trade = sub.drop(index=sub[NET_YUAN_COL].idxmax())
        res.drop_top1_trade_mean_r = float(drop_trade[NET_R_COL].mean())
    else:
        res.drop_top1_trade_mean_r = res.mean_net_r
    if sub["ym"].nunique() >= 2:
        top_m = sub.groupby("ym")[NET_YUAN_COL].sum().idxmax()
        drop_m = sub.loc[sub["ym"] != top_m]
        res.drop_top1_month_mean_r = float(drop_m[NET_R_COL].mean())
    else:
        res.drop_top1_month_mean_r = res.mean_net_r

    reasons: list[str] = []
    # OOS 子集：优先用日历 OOS；若不足则用全窗但标注
    oos0 = pd.Timestamp(OOS_START)
    oos1 = pd.Timestamp(OOS_END)
    if sub["time"].dt.tz is not None:
        oos0 = oos0.tz_localize(sub["time"].dt.tz)
        oos1 = oos1.tz_localize(sub["time"].dt.tz)
    oos = sub.loc[(sub["time"] >= oos0) & (sub["time"] <= oos1)]
    oos_n = int(len(oos)) if not oos.empty else 0
    pooled_n = oos_n if oos_n >= ALPHA_GATE_MIN_OOS_N else res.n
    if oos_n < ALPHA_GATE_MIN_OOS_N:
        reasons.append(f"oos_n={oos_n}<{ALPHA_GATE_MIN_OOS_N}_use_pooled")

    ok = True
    if pooled_n < ALPHA_GATE_MIN_OOS_N:
        ok = False
        reasons.append(f"n<{ALPHA_GATE_MIN_OOS_N}")
    if res.n_symbols < ALPHA_GATE_MIN_SYMBOLS:
        ok = False
        reasons.append(f"symbols<{ALPHA_GATE_MIN_SYMBOLS}")
    if res.n_half_folds < ALPHA_GATE_MIN_HALF_FOLDS:
        ok = False
        reasons.append(f"folds<{ALPHA_GATE_MIN_HALF_FOLDS}")
    if not (res.mean_net_r > 0):
        ok = False
        reasons.append("mean_net_r<=0")
    if not (res.bootstrap_lb > ALPHA_GATE_BOOTSTRAP_LB):
        ok = False
        reasons.append("bootstrap_lb<=0")
    if res.fold_pos_ratio < ALPHA_GATE_FOLD_POS_RATIO:
        ok = False
        reasons.append(f"fold_pos<{ALPHA_GATE_FOLD_POS_RATIO}")
    if res.loso_nonneg < ALPHA_GATE_LOSO_NONNEG:
        ok = False
        reasons.append(f"loso_nonneg<{ALPHA_GATE_LOSO_NONNEG}")
    if res.max_symbol_share > ALPHA_GATE_MAX_CONCENTRATION:
        ok = False
        reasons.append("symbol_concentration")
    if res.max_month_share > ALPHA_GATE_MAX_CONCENTRATION:
        ok = False
        reasons.append("month_concentration")
    if not (res.drop_top1_trade_mean_r > 0 and res.drop_top1_month_mean_r > 0):
        ok = False
        reasons.append("fragile_to_top1")

    res.reasons = reasons
    if ok:
        res.label = "PROMOTE_TO_CTA"
    elif res.mean_net_r > 0 and res.n >= 30 and res.n_symbols >= 3:
        res.label = "PROVISIONAL"
        res.reasons.append("partial_pass")
    else:
        res.label = "REJECT"
    return res


def run_stability_screen(df: pd.DataFrame, *, gate_pass_only: bool = True) -> pd.DataFrame:
    prep = prepare_candidates(df, gate_pass_only=gate_pass_only)
    rows: list[dict[str, Any]] = []
    if prep.empty:
        return pd.DataFrame()
    families = [f for f in ALPHA_OPP_CODES if f in set(prep["opp_family"])]
    for fam in families:
        for direction in (1, -1):
            rows.append(evaluate_slice(prep, fam, direction).to_row())
    out = pd.DataFrame(rows)
    out.insert(0, "protocol", ALPHA_PROTOCOL_VERSION)
    out.insert(1, "primary_horizon_m", ALPHA_PRIMARY_HORIZON_M)
    # 排名：PROMOTE > PROVISIONAL > REJECT，再按 mean_net_r
    rank_map = {"PROMOTE_TO_CTA": 0, "PROVISIONAL": 1, "REJECT": 2}
    out["_rk"] = out["label"].map(rank_map).fillna(9)
    out = out.sort_values(["_rk", "mean_net_r"], ascending=[True, False]).drop(columns=["_rk"])
    return out.reset_index(drop=True)


def pick_top_promote(report: pd.DataFrame) -> dict[str, Any] | None:
    if report is None or report.empty:
        return None
    promo = report.loc[report["label"] == "PROMOTE_TO_CTA"]
    if promo.empty:
        return None
    row = promo.iloc[0]
    return {
        "opp_family": str(row["opp_family"]),
        "direction": int(row["direction"]),
        "mean_net_r": float(row["mean_net_r"]),
        "n": int(row["n"]),
    }
