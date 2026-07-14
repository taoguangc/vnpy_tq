# -*- coding: utf-8
"""Market State 分层汇总 + 允许矩阵 gate。"""
from __future__ import annotations

import pandas as pd

from research.event_engine.market_state import SETUP_ALLOWED_STATES, state_segments
from research.event_engine.schema import DEFAULT_COST_TICKS
from research.event_engine.summary import verdict_row


def build_state_summary(
    events: pd.DataFrame,
    setup: str,
    *,
    tick: float,
    cost_ticks: float = DEFAULT_COST_TICKS,
    primary_horizon: int = 10,
) -> pd.DataFrame:
    rows = [verdict_row(events, tick=tick, cost_ticks=cost_ticks, label="ALL", primary_horizon=primary_horizon)]
    if not events.empty:
        for label, sub in state_segments(events):
            rows.append(
                verdict_row(sub, tick=tick, cost_ticks=cost_ticks, label=label, primary_horizon=primary_horizon)
            )
    return pd.DataFrame(rows)


def state_matrix_report(summary: pd.DataFrame, setup: str) -> dict:
    allowed_states = SETUP_ALLOWED_STATES.get(setup, frozenset())
    out: dict = {
        "setup": setup,
        "allowed_states": sorted(allowed_states),
        "matrix_pass": False,
    }
    if summary.empty:
        return out

    all_row = summary[summary["segment"] == "ALL"]
    allow_row = summary[summary["segment"] == "ALLOWED"]
    if not all_row.empty:
        out["all_n"] = int(all_row.iloc[0]["n"])
        out["all_net_h10"] = all_row.iloc[0].get("net_after_cost_10")
    if not allow_row.empty and allow_row.iloc[0]["n"] > 0:
        r = allow_row.iloc[0]
        out["allowed_n"] = int(r["n"])
        out["allowed_net_h10"] = r.get("net_after_cost_10")
        out["allowed_gate"] = bool(r.get("gate_pass"))
        out["matrix_pass"] = bool(r.get("gate_pass"))
        if "all_net_h10" in out:
            a, b = out["all_net_h10"], out["allowed_net_h10"]
            if a == a and b == b:
                out["lift_allowed_vs_all"] = float(b) - float(a)
    denied = summary[summary["segment"] == "DENIED"]
    if not denied.empty:
        out["denied_n"] = int(denied.iloc[0]["n"])
        out["denied_net_h10"] = denied.iloc[0].get("net_after_cost_10")
    return out
