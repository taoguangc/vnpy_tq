# -*- coding: utf-8
"""Phase 5 — Adaptive Sizing（研究层，加权 forward 期望）。"""
from __future__ import annotations

import numpy as np
import pandas as pd

from research.event_engine.quality_score import FULL_THRESHOLD, HALF_THRESHOLD

BUCKET_MULT = {
    "FULL": 1.0,
    "HALF": 0.5,
    "SKIP": 0.0,
}

# setup 允许态内仍可用 state 微调（v0：允许态=1.0，拒绝=0）
STATE_MULT = {
    "TREND": 1.0,
    "RANGE": 0.75,
    "COMPRESSION": 1.0,
    "CLIMAX": 1.0,
}


def quality_bucket(score: float, *, full: float = FULL_THRESHOLD, half: float = HALF_THRESHOLD) -> str:
    if score != score:
        return "SKIP"
    if score >= full:
        return "FULL"
    if score >= half:
        return "HALF"
    return "SKIP"


def compute_size_mult(row: pd.Series) -> float:
    allowed = bool(row.get("setup_allowed", False))
    if not allowed:
        return 0.0
    state = str(row.get("market_state", "RANGE"))
    state_m = STATE_MULT.get(state, 0.75)
    if "size_bucket" in row.index and pd.notna(row.get("size_bucket")):
        bucket = str(row["size_bucket"])
    elif "quality_score" in row.index:
        bucket = quality_bucket(float(row["quality_score"]))
    else:
        bucket = "FULL"
    q_m = BUCKET_MULT.get(bucket, 0.0)
    return q_m * state_m


def attach_sizing(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        out = events.copy()
        out["size_mult"] = pd.Series(dtype=float)
        return out
    out = events.copy()
    out["size_mult"] = out.apply(compute_size_mult, axis=1)
    return out


def weighted_forward_ticks(events: pd.DataFrame, horizon: int = 10, *, tick: float = 1.0) -> dict:
    col = f"future_{horizon}"
    if events.empty or col not in events.columns or "size_mult" not in events.columns:
        return {"n_active": 0, "risk_units": 0.0, "avg_f": np.nan, "weighted_avg_f": np.nan}

    active = events[events["size_mult"] > 0].copy()
    if active.empty:
        return {"n_active": 0, "risk_units": 0.0, "avg_f": np.nan, "weighted_avg_f": np.nan}

    f_ticks = active[col] / tick
    w = active["size_mult"]
    risk_units = float(w.sum())
    return {
        "n_active": len(active),
        "risk_units": risk_units,
        "avg_f": float(f_ticks.mean()),
        "weighted_avg_f": float((f_ticks * w).sum() / risk_units) if risk_units > 0 else np.nan,
    }


def build_sizing_summary(
    events: pd.DataFrame,
    *,
    tick: float,
    cost_ticks: float = 3.0,
    horizons: tuple[int, ...] = (5, 10, 20),
) -> pd.DataFrame:
    rows: list[dict] = []

    def _row(label: str, sub: pd.DataFrame) -> dict:
        base = {"segment": label, "n": len(sub), "risk_units": 0.0}
        if sub.empty:
            for h in horizons:
                base[f"avg_future_{h}"] = np.nan
                base[f"net_after_cost_{h}"] = np.nan
            base["weighted_net_h10"] = np.nan
            base["n_active"] = 0
            return base

        if "size_mult" not in sub.columns:
            sub = attach_sizing(sub)

        base["risk_units"] = float(sub["size_mult"].sum())
        for h in horizons:
            col = f"future_{h}"
            if col in sub.columns:
                avg = float(sub[col].mean() / tick)
                base[f"avg_future_{h}"] = avg
                base[f"net_after_cost_{h}"] = avg - cost_ticks
            else:
                base[f"avg_future_{h}"] = np.nan
                base[f"net_after_cost_{h}"] = np.nan

        w10 = weighted_forward_ticks(sub, 10, tick=tick)
        base["weighted_avg_f10"] = w10["weighted_avg_f"]
        base["weighted_net_h10"] = (
            w10["weighted_avg_f"] - cost_ticks if w10["weighted_avg_f"] == w10["weighted_avg_f"] else np.nan
        )
        base["n_active"] = int(w10["n_active"])
        return base

    rows.append(_row("ALL", events))
    if not events.empty and "size_mult" in events.columns:
        active = events[events["size_mult"] > 0]
        rows.append(_row("SIZED(active)", active))
        rows.append(_row("FULL_only", events[events["size_mult"] >= 0.99]))
        rows.append(_row("HALF_or_less", events[(events["size_mult"] > 0) & (events["size_mult"] < 0.99)]))
        rows.append(_row("ZERO(skip/deny)", events[events["size_mult"] <= 0]))

    return pd.DataFrame(rows)


def sizing_gate_report(summary: pd.DataFrame, *, min_risk_units: float = 30.0) -> dict:
    if summary.empty:
        return {"gate": "NO_DATA"}
    sized = summary[summary["segment"] == "SIZED(active)"]
    all_row = summary[summary["segment"] == "ALL"]
    out: dict = {"gate": "FAIL", "min_risk_units": min_risk_units}
    if not all_row.empty:
        out["all_net_h10"] = all_row.iloc[0].get("net_after_cost_10")
    if sized.empty:
        out["reason"] = "no_sized_segment"
        return out
    r = sized.iloc[0]
    n_act = r.get("n_active", 0)
    out["n_active"] = int(n_act) if n_act == n_act else 0
    out["risk_units"] = float(r["risk_units"])
    out["weighted_net_h10"] = r.get("weighted_net_h10")
    out["avg_net_h10"] = r.get("net_after_cost_10")
    if out["risk_units"] >= min_risk_units and r.get("weighted_net_h10") == r.get("weighted_net_h10"):
        out["gate"] = "PASS" if r["weighted_net_h10"] > 0 else "FAIL"
    else:
        out["reason"] = "insufficient_risk_units"
    if "all_net_h10" in out and out.get("weighted_net_h10") == out.get("weighted_net_h10"):
        out["lift_vs_all"] = float(out["weighted_net_h10"]) - float(out["all_net_h10"])
    return out
