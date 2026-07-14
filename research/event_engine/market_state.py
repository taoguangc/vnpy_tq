# -*- coding: utf-8
"""Phase 4 — 四态 Market State + Setup 允许矩阵。"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from research.event_engine.bars import resample_ohlc
from research.event_engine.schema import EventRecord

STATES = ("TREND", "RANGE", "COMPRESSION", "CLIMAX")

COMPRESSION_THRESHOLD = 0.6
CLIMAX_ATR_THRESHOLD = 2.0
TREND_ER_THRESHOLD = 0.35
TREND_ENV_THRESHOLD = 0.75

# 路线图：S1→COMPRESSION, S2→TREND, S3→CLIMAX
SETUP_ALLOWED_STATES: dict[str, frozenset[str]] = {
    "compression_breakout": frozenset({"COMPRESSION"}),
    "first_pullback": frozenset({"TREND"}),
    "failed_breakout": frozenset({"CLIMAX"}),
}

SETUP_ALIASES: dict[str, str] = {
    "S1_COMPRESSION_BREAKOUT": "compression_breakout",
    "S2_FIRST_PULLBACK": "first_pullback",
    "S3_FAILED_BREAKOUT": "failed_breakout",
}


def normalize_setup_key(setup: str) -> str:
    return SETUP_ALIASES.get(setup.strip(), setup.strip())


def setup_allowed(setup: str, state: str) -> bool:
    key = normalize_setup_key(setup)
    allowed = SETUP_ALLOWED_STATES.get(key)
    if allowed is None:
        return True
    return state in allowed


@dataclass(frozen=True)
class StateRule:
    compression_min: float = COMPRESSION_THRESHOLD
    climax_atr_min: float = CLIMAX_ATR_THRESHOLD
    trend_er_min: float = TREND_ER_THRESHOLD
    trend_env_min: float = TREND_ENV_THRESHOLD


DEFAULT_RULE = StateRule()


def classify_market_state(features: dict[str, float], *, rule: StateRule = DEFAULT_RULE) -> str:
    comp = float(features.get("compression_score", 0.0) or 0.0)
    er = float(features.get("er", 0.0) or 0.0)
    env = float(features.get("env_score", 0.0) or 0.0)
    climax = float(features.get("climax_atr", 0.0) or 0.0)

    if comp >= rule.compression_min:
        return "COMPRESSION"
    if climax >= rule.climax_atr_min:
        return "CLIMAX"
    if env >= rule.trend_env_min or er >= rule.trend_er_min:
        return "TREND"
    return "RANGE"


def attach_market_state(
    records: list[EventRecord],
    bars_1m: pd.DataFrame,
    *,
    rule: StateRule = DEFAULT_RULE,
) -> list[EventRecord]:
    if not records:
        return records

    bars_15m = resample_ohlc(bars_1m, "15min")
    if len(bars_15m) < 30:
        return records

    idx_15 = bars_15m.index
    c15 = bars_15m["close"].astype(float)
    ema20 = c15.ewm(span=20, adjust=False).mean()
    h15 = bars_15m["high"].astype(float)
    l15 = bars_15m["low"].astype(float)
    prev_c = c15.shift(1)
    tr = pd.concat([(h15 - l15), (h15 - prev_c).abs(), (l15 - prev_c).abs()], axis=1).max(axis=1)
    atr15 = tr.rolling(20, min_periods=20).mean()
    climax_series = (c15 - ema20).abs() / atr15.clip(lower=1e-9)

    for rec in records:
        ts = pd.Timestamp(rec.datetime)
        if ts.tzinfo is None:
            ts = ts.tz_localize("Asia/Shanghai")
        else:
            ts = ts.tz_convert("Asia/Shanghai")

        end_15 = int(idx_15.searchsorted(ts, side="right"))
        if end_15 < 30:
            rec.extra["market_state"] = "RANGE"
            rec.extra["setup_allowed"] = 0
            continue

        i = end_15 - 1
        if i < len(climax_series) and climax_series.iloc[i] == climax_series.iloc[i]:
            rec.features["climax_atr"] = float(climax_series.iloc[i])

        state = classify_market_state(rec.features, rule=rule)
        rec.extra["market_state"] = state
        rec.extra["setup_allowed"] = 1 if setup_allowed(rec.setup, state) else 0

    return records


def label_events_dataframe(events: pd.DataFrame, setup: str) -> pd.DataFrame:
    if events.empty:
        out = events.copy()
        out["market_state"] = pd.Series(dtype=str)
        out["setup_allowed"] = pd.Series(dtype=bool)
        return out

    out = events.copy()
    states: list[str] = []
    allowed: list[bool] = []
    for _, row in out.iterrows():
        feats = {
            k.replace("feat_", ""): float(row[k])
            for k in out.columns
            if k.startswith("feat_") and row[k] == row[k]
        }
        if "market_state" in row.index and isinstance(row.get("market_state"), str):
            st = str(row["market_state"])
        else:
            st = classify_market_state(feats)
        states.append(st)
        allowed.append(setup_allowed(setup, st))

    out["market_state"] = states
    out["setup_allowed"] = allowed
    return out


def state_segments(events: pd.DataFrame):
    if events.empty or "market_state" not in events.columns:
        return
    for state in STATES:
        sub = events[events["market_state"] == state]
        if not sub.empty:
            yield f"STATE_{state}", sub
    if "setup_allowed" in events.columns:
        allow = events["setup_allowed"].astype(bool)
        yield "ALLOWED", events[allow]
        yield "DENIED", events[~allow]
