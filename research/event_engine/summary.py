# -*- coding: utf-8
"""Event Study 汇总与 gate 判定。"""
from __future__ import annotations

import numpy as np
import pandas as pd

from research.event_engine.schema import (
    DEFAULT_COST_TICKS,
    DEFAULT_COST_TICKS_ALT,
    FWD_HORIZONS,
    GATE_MIN_N,
)


def _tick_cols(events: pd.DataFrame, tick: float) -> pd.DataFrame:
    ev = events.copy()
    for h in FWD_HORIZONS:
        col = f"future_{h}"
        if col in ev.columns:
            ev[f"{col}_ticks"] = ev[col] / tick
    for col in ("mfe", "mae", "one_r", "breakout_size"):
        if col in ev.columns:
            ev[f"{col}_ticks"] = ev[col] / tick
    return ev


def verdict_row(
    events: pd.DataFrame,
    *,
    tick: float,
    cost_ticks: float,
    label: str,
    primary_horizon: int = 10,
) -> dict:
    empty = {
        "segment": label,
        "n": 0,
        "gate_pass": False,
        "pass_n": False,
        "pass_net": False,
    }
    for h in FWD_HORIZONS:
        empty[f"avg_future_{h}"] = np.nan
        empty[f"net_after_cost_{h}"] = np.nan
    empty.update(
        {
            "avg_mfe": np.nan,
            "avg_mae": np.nan,
            "p_mfe_gt_1r": np.nan,
            "pass_q1": False,
            "pass_q2": False,
            "pass_q3": False,
            "pass_cost": False,
        }
    )
    if events.empty:
        return empty

    ev = _tick_cols(events, tick)
    row: dict = {"segment": label, "n": len(ev)}

    for h in FWD_HORIZONS:
        col = f"future_{h}_ticks"
        avg = float(ev[col].mean()) if col in ev.columns else np.nan
        row[f"avg_future_{h}"] = avg
        row[f"net_after_cost_{h}"] = avg - cost_ticks if avg == avg else np.nan

    avg_mfe = float(ev["mfe_ticks"].mean()) if "mfe_ticks" in ev.columns else np.nan
    avg_mae = float(ev["mae_ticks"].mean()) if "mae_ticks" in ev.columns else np.nan
    p_mfe_1r = float(ev["mfe_gt_1r"].mean()) if "mfe_gt_1r" in ev.columns else np.nan

    ph = primary_horizon
    avg_primary = row.get(f"avg_future_{ph}", np.nan)
    net_primary = row.get(f"net_after_cost_{ph}", np.nan)

    row.update(
        {
            "avg_mfe": avg_mfe,
            "avg_mae": avg_mae,
            "p_mfe_gt_1r": p_mfe_1r,
            "pass_q1": bool(avg_primary > 0) if avg_primary == avg_primary else False,
            "pass_q2": bool(avg_mfe > avg_mae) if avg_mfe == avg_mfe and avg_mae == avg_mae else False,
            "pass_q3": bool(p_mfe_1r > 0.55) if p_mfe_1r == p_mfe_1r else False,
            "pass_cost": bool(net_primary > 0) if net_primary == net_primary else False,
            "pass_n": len(ev) >= GATE_MIN_N,
            "pass_net": bool(net_primary > 0) if net_primary == net_primary else False,
            "gate_pass": len(ev) >= GATE_MIN_N and net_primary == net_primary and net_primary > 0,
        }
    )
    return row


def build_summary(
    events: pd.DataFrame,
    *,
    tick: float,
    cost_ticks: float = DEFAULT_COST_TICKS,
    primary_horizon: int = 10,
    segment_fn=None,
) -> pd.DataFrame:
    rows = [verdict_row(events, tick=tick, cost_ticks=cost_ticks, label="ALL", primary_horizon=primary_horizon)]
    if segment_fn is not None and not events.empty:
        for label, sub in segment_fn(events):
            rows.append(
                verdict_row(sub, tick=tick, cost_ticks=cost_ticks, label=label, primary_horizon=primary_horizon)
            )
    return pd.DataFrame(rows)


def gate_report(summary: pd.DataFrame, *, cost_ticks_alt: float = DEFAULT_COST_TICKS_ALT) -> dict:
    if summary.empty:
        return {"gate": "NO_DATA", "n": 0, "net_h10": np.nan}
    r = summary.iloc[0]
    return {
        "gate": "PASS" if r.get("gate_pass") else "FAIL",
        "n": int(r.get("n", 0)),
        "net_h10": r.get("net_after_cost_10"),
        "net_h10_alt_cost": (
            float(r.get("avg_future_10", np.nan)) - cost_ticks_alt
            if r.get("avg_future_10") == r.get("avg_future_10")
            else np.nan
        ),
        "pass_n": bool(r.get("pass_n")),
        "pass_net": bool(r.get("pass_net")),
    }


def failed_breakout_segments(events: pd.DataFrame):
    """Round 2 分层（Failed Breakout 专用）。"""
    if events.empty:
        return

    yield "SHORT fade", events[events["direction"] == -1]
    yield "LONG fade", events[events["direction"] == 1]

    def _climax_bucket(row: pd.Series) -> str:
        if row["direction"] < 0:
            d = row.get("climax_up")
        else:
            d = row.get("climax_down")
        if pd.isna(d):
            return "NA"
        ad = abs(d)
        if ad < 1:
            return "0-1 ATR"
        if ad < 2:
            return "1-2 ATR"
        if ad < 3:
            return "2-3 ATR"
        return "3+ ATR"

    ev = events.copy()
    ev["climax_bucket"] = ev.apply(_climax_bucket, axis=1)
    for bucket, sub in ev.groupby("climax_bucket"):
        yield f"Climax {bucket}", sub

    if "breakout_ticks" in ev.columns:
        try:
            for q, sub in ev.groupby(pd.qcut(ev["breakout_ticks"], 4, duplicates="drop"), observed=True):
                yield f"Breakout Q{q}", sub
        except ValueError:
            pass

    if "wick_ratio" in ev.columns:
        try:
            for q, sub in ev.groupby(pd.qcut(ev["wick_ratio"], 4, duplicates="drop"), observed=True):
                yield f"Wick Q{q}", sub
        except ValueError:
            pass

    if "hour_cst" in ev.columns:
        for hour, sub in ev.groupby("hour_cst"):
            yield f"Hour {hour:02d}", sub
