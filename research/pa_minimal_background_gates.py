# -*- coding: utf-8 -*-
"""pa_minimal 第二阶段：背景门禁（成本覆盖率 + 会话分段）。"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from research.pa_minimal_baseline import gate_verdict, split_by_time


def apply_cost_coverage_gate(
    features: pd.DataFrame,
    *,
    max_cost_over_1r: float = 0.35,
) -> pd.Series:
    """拒绝预期 1R 不足以覆盖成本的信号。"""
    if "cost_over_1r" not in features.columns:
        return pd.Series(True, index=features.index)
    return features["cost_over_1r"].fillna(0.0) <= max_cost_over_1r


def apply_session_gate(
    features: pd.DataFrame,
    allowed_sessions: set[str],
) -> pd.Series:
    if "session" not in features.columns:
        return pd.Series(True, index=features.index)
    return features["session"].isin(allowed_sessions)


def session_expectancy(features: pd.DataFrame) -> pd.DataFrame:
    """各会话桶成本后期望。"""
    if features.empty or "session" not in features.columns:
        return pd.DataFrame()
    work = features.dropna(subset=["net_1lot_after_cost"]).copy()
    return (
        work.groupby(["setup", "session"], observed=True)
        .agg(
            n=("net_1lot_after_cost", "count"),
            avg_net=("net_1lot_after_cost", "mean"),
            hit_1r=("hit_1r", "mean"),
            avg_cost_cov=("cost_over_1r", "mean"),
        )
        .reset_index()
    )


def pick_session_gate(features: pd.DataFrame, min_n: int = 8) -> set[str]:
    """选 IS 中 avg_net>0 且 n>=min_n 的会话桶（单变量预注册）。"""
    is_df, _ = split_by_time(features, "time")
    exp = session_expectancy(is_df)
    if exp.empty:
        return set()
    good = exp[(exp["n"] >= min_n) & (exp["avg_net"] > 0)]
    return set(good["session"].unique())


def evaluate_background_gate(
    features: pd.DataFrame,
    gate_mask: pd.Series,
    *,
    baseline_net_col: str = "net_1lot_after_cost",
) -> dict[str, Any]:
    """IS/OOS 上单变量背景门禁评估。"""
    work = features.copy()
    work["gated_in"] = gate_mask.values
    is_df, oos_df = split_by_time(work, "time")

    def _sum(df: pd.DataFrame, mask: pd.Series | None = None) -> dict[str, float]:
        sub = df[mask] if mask is not None else df
        sub = sub.dropna(subset=[baseline_net_col])
        if sub.empty:
            return {"n": 0, "net": 0.0, "pf": float("nan")}
        net = float(sub[baseline_net_col].sum())
        wins = sub[sub[baseline_net_col] > 0][baseline_net_col].sum()
        losses = abs(sub[sub[baseline_net_col] < 0][baseline_net_col].sum())
        pf = float(wins / losses) if losses > 1e-9 else float("inf")
        return {"n": int(len(sub)), "net": net, "pf": pf}

    base_is = _sum(is_df)
    base_oos = _sum(oos_df)
    gate_is = _sum(is_df, is_df["gated_in"])
    gate_oos = _sum(oos_df, oos_df["gated_in"])
    retained = gate_is["n"] / base_is["n"] if base_is["n"] else 0.0
    verdict = gate_verdict(
        is_delta=gate_is["net"] - base_is["net"],
        oos_delta=gate_oos["net"] - base_oos["net"],
        is_n=int(gate_is["n"]),
        oos_n=int(gate_oos["n"]),
        baseline_pf=base_oos["pf"],
        variant_pf=gate_oos["pf"],
        trades_retained=retained,
    )
    return {
        "base_is": base_is,
        "base_oos": base_oos,
        "gate_is": gate_is,
        "gate_oos": gate_oos,
        "retained_pct": retained,
        "verdict": verdict,
    }


def run_background_gates(features: pd.DataFrame) -> pd.DataFrame:
    """逐一测试成本覆盖率与会话门禁。"""
    rows = []
    cost_mask = apply_cost_coverage_gate(features)
    cost_eval = evaluate_background_gate(features, cost_mask)
    rows.append({"gate": "cost_coverage", "max_cost_over_1r": 0.35, **cost_eval})

    allowed = pick_session_gate(features)
    if allowed:
        sess_mask = apply_session_gate(features, allowed)
        sess_eval = evaluate_background_gate(features, sess_mask)
        rows.append({"gate": "session", "allowed": ",".join(sorted(allowed)), **sess_eval})
    else:
        rows.append({"gate": "session", "allowed": "", "verdict": "UNKNOWN", "retained_pct": 0.0})

    flat = []
    for r in rows:
        flat.append({
            "gate": r["gate"],
            "verdict": r.get("verdict", "UNKNOWN"),
            "retained_pct": r.get("retained_pct", 0.0),
            "is_n": r.get("gate_is", {}).get("n", 0),
            "is_net": r.get("gate_is", {}).get("net", 0.0),
            "oos_n": r.get("gate_oos", {}).get("n", 0),
            "oos_net": r.get("gate_oos", {}).get("net", 0.0),
            "base_oos_net": r.get("base_oos", {}).get("net", 0.0),
        })
    return pd.DataFrame(flat)
