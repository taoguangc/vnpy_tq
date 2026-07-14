# -*- coding: utf-8
"""Quality Score 分层汇总。"""
from __future__ import annotations

import pandas as pd

from research.event_engine.quality_score import quality_segments
from research.event_engine.schema import DEFAULT_COST_TICKS
from research.event_engine.summary import build_summary, verdict_row


def build_quality_summary(
    events: pd.DataFrame,
    *,
    tick: float,
    cost_ticks: float = DEFAULT_COST_TICKS,
    primary_horizon: int = 10,
) -> pd.DataFrame:
    rows = [verdict_row(events, tick=tick, cost_ticks=cost_ticks, label="ALL", primary_horizon=primary_horizon)]
    if not events.empty and "quality_score" in events.columns:
        for label, sub in quality_segments(events):
            rows.append(
                verdict_row(sub, tick=tick, cost_ticks=cost_ticks, label=label, primary_horizon=primary_horizon)
            )
        hi = events[events["size_bucket"].isin(["FULL", "HALF"])]
        rows.append(
            verdict_row(
                hi,
                tick=tick,
                cost_ticks=cost_ticks,
                label="TRADEABLE(FULL+HALF)",
                primary_horizon=primary_horizon,
            )
        )
    return pd.DataFrame(rows)


def quality_lift_report(summary: pd.DataFrame) -> dict:
    if summary.empty:
        return {"lift": "NO_DATA"}
    all_row = summary[summary["segment"] == "ALL"]
    full_row = summary[summary["segment"] == "Q_FULL"]
    trade_row = summary[summary["segment"] == "TRADEABLE(FULL+HALF)"]
    out: dict = {"lift": "NONE"}
    if not all_row.empty:
        out["all_n"] = int(all_row.iloc[0]["n"])
        out["all_net_h10"] = all_row.iloc[0].get("net_after_cost_10")
    if not full_row.empty and full_row.iloc[0]["n"] > 0:
        out["full_n"] = int(full_row.iloc[0]["n"])
        out["full_net_h10"] = full_row.iloc[0].get("net_after_cost_10")
        out["full_gate"] = bool(full_row.iloc[0].get("gate_pass"))
    if not trade_row.empty and trade_row.iloc[0]["n"] > 0:
        out["tradeable_n"] = int(trade_row.iloc[0]["n"])
        out["tradeable_net_h10"] = trade_row.iloc[0].get("net_after_cost_10")
        out["tradeable_gate"] = bool(trade_row.iloc[0].get("gate_pass"))
    if "all_net_h10" in out and "full_net_h10" in out:
        a, f = out["all_net_h10"], out["full_net_h10"]
        if a == a and f == f:
            out["lift_full_vs_all"] = float(f) - float(a)
            out["lift"] = "POSITIVE" if f > a else "NEGATIVE"
    return out
