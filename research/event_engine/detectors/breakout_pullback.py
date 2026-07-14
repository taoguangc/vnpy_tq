# -*- coding: utf-8
"""BP Breakout Pullback Continuation — 迁移自 experiments/E1_breakout_pullback_rb。"""
from __future__ import annotations

from enum import IntEnum

import pandas as pd

from research.event_engine.schema import EventRecord

SETUP = "BP_BREAKOUT_PULLBACK"
LOOKBACK = 20
PULLBACK_MAX_BARS = 15
READY_MAX_BARS = 5


class LongState(IntEnum):
    IDLE = 0
    WATCH = 1
    PULLBACK = 2
    READY = 3


class ShortState(IntEnum):
    IDLE = 0
    WATCH = 1
    PULLBACK = 2
    READY = 3


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy().reset_index(drop=True)
    h = out["high"].astype(float)
    lo = out["low"].astype(float)
    c = out["close"].astype(float)
    o = out["open"].astype(float)
    prev_c = c.shift(1)
    tr = pd.concat([(h - lo), (h - prev_c).abs(), (lo - prev_c).abs()], axis=1).max(axis=1)
    out["atr20"] = tr.rolling(20, min_periods=20).mean()
    out["ema20"] = c.ewm(span=20, adjust=False).mean()
    out["ema_slope10"] = (out["ema20"] - out["ema20"].shift(10)) / out["atr20"]
    out["prev_20_high"] = h.shift(1).rolling(LOOKBACK, min_periods=LOOKBACK).max()
    out["prev_20_low"] = lo.shift(1).rolling(LOOKBACK, min_periods=LOOKBACK).min()
    out["range"] = h - lo
    out["high_lag1"] = h.shift(1)
    out["low_lag1"] = lo.shift(1)
    return out


def _emit(
    rows: list[EventRecord],
    *,
    row: pd.Series,
    symbol: str,
    direction: int,
    bo_size: float,
    pb_bars: int,
    pb_depth_atr: float,
) -> None:
    rows.append(
        EventRecord(
            symbol=symbol,
            datetime=row["dt_cst"],
            setup=SETUP,
            direction=direction,
            entry_price=float(row["close"]),
            extra={
                "breakout_size": bo_size,
                "pullback_bars": pb_bars,
                "pullback_depth_atr": pb_depth_atr,
                "ema_slope": float(row["ema_slope10"]) if row["ema_slope10"] == row["ema_slope10"] else 0.0,
                "signal_bar_range": float(row["range"]),
                "one_r": float(row["range"]),
                "hour_cst": int(pd.Timestamp(row["dt_cst"]).hour),
            },
        )
    )


def detect_events(
    df: pd.DataFrame,
    *,
    symbol: str,
    tick: float = 1.0,
) -> list[EventRecord]:
    rows: list[EventRecord] = []
    n = len(df)
    lf_state = LongState.IDLE
    sf_state = ShortState.IDLE
    bo_level_l = 0.0
    bo_size_l = 0.0
    bars_since_bo_l = 0
    pb_bars_l = 0
    pb_depth_l = 0.0
    lf_ready = 0

    bo_level_s = 0.0
    bo_size_s = 0.0
    bars_since_bo_s = 0
    pb_bars_s = 0
    pb_depth_s = 0.0
    sf_ready = 0

    for i in range(LOOKBACK, n):
        row = df.iloc[i]
        if pd.isna(row["prev_20_high"]) or pd.isna(row["atr20"]):
            lf_state = LongState.IDLE
            sf_state = ShortState.IDLE
            continue

        high = float(row["high"])
        low = float(row["low"])
        close = float(row["close"])
        open_ = float(row["open"])
        atr = float(row["atr20"])
        prev_high = float(row["prev_20_high"])
        prev_low = float(row["prev_20_low"])
        ema20 = float(row["ema20"])
        prev_high1 = float(row["high_lag1"])
        prev_low1 = float(row["low_lag1"])

        # ---- Long BP ----
        if lf_state == LongState.IDLE:
            if high > prev_high and close > prev_high:
                lf_state = LongState.WATCH
                bo_level_l = prev_high
                bo_size_l = high - prev_high
                bars_since_bo_l = 0
                pb_bars_l = 0
                pb_depth_l = 0.0
        elif lf_state == LongState.WATCH:
            bars_since_bo_l += 1
            if close < bo_level_l - tick:
                lf_state = LongState.IDLE
            elif low < close and (close < open_ or low < ema20):
                lf_state = LongState.PULLBACK
                pb_bars_l = 1
                if atr > 0:
                    pb_depth_l = max(0.0, (bo_level_l - low) / atr)
            elif bars_since_bo_l > PULLBACK_MAX_BARS:
                lf_state = LongState.IDLE
        elif lf_state == LongState.PULLBACK:
            bars_since_bo_l += 1
            pb_bars_l += 1
            if atr > 0:
                pb_depth_l = max(pb_depth_l, (bo_level_l - low) / atr)
            if close < bo_level_l - tick:
                lf_state = LongState.IDLE
            elif close >= open_ or close >= ema20:
                lf_state = LongState.READY
                lf_ready = 0
            elif bars_since_bo_l > PULLBACK_MAX_BARS:
                lf_state = LongState.IDLE
        elif lf_state == LongState.READY:
            bars_since_bo_l += 1
            lf_ready += 1
            if high > prev_high1 + tick:
                _emit(
                    rows,
                    row=row,
                    symbol=symbol,
                    direction=1,
                    bo_size=bo_size_l,
                    pb_bars=pb_bars_l,
                    pb_depth_atr=pb_depth_l,
                )
                lf_state = LongState.IDLE
            elif lf_ready > READY_MAX_BARS or bars_since_bo_l > PULLBACK_MAX_BARS + READY_MAX_BARS:
                lf_state = LongState.IDLE
            elif close < bo_level_l - tick:
                lf_state = LongState.IDLE

        # ---- Short BP ----
        if sf_state == ShortState.IDLE:
            if low < prev_low and close < prev_low:
                sf_state = ShortState.WATCH
                bo_level_s = prev_low
                bo_size_s = prev_low - low
                bars_since_bo_s = 0
                pb_bars_s = 0
                pb_depth_s = 0.0
        elif sf_state == ShortState.WATCH:
            bars_since_bo_s += 1
            if close > bo_level_s + tick:
                sf_state = ShortState.IDLE
            elif high > close and (close > open_ or high > ema20):
                sf_state = ShortState.PULLBACK
                pb_bars_s = 1
                if atr > 0:
                    pb_depth_s = max(0.0, (high - bo_level_s) / atr)
            elif bars_since_bo_s > PULLBACK_MAX_BARS:
                sf_state = ShortState.IDLE
        elif sf_state == ShortState.PULLBACK:
            bars_since_bo_s += 1
            pb_bars_s += 1
            if atr > 0:
                pb_depth_s = max(pb_depth_s, (high - bo_level_s) / atr)
            if close > bo_level_s + tick:
                sf_state = ShortState.IDLE
            elif close <= open_ or close <= ema20:
                sf_state = ShortState.READY
                sf_ready = 0
            elif bars_since_bo_s > PULLBACK_MAX_BARS:
                sf_state = ShortState.IDLE
        elif sf_state == ShortState.READY:
            bars_since_bo_s += 1
            sf_ready += 1
            if low < prev_low1 - tick:
                _emit(
                    rows,
                    row=row,
                    symbol=symbol,
                    direction=-1,
                    bo_size=bo_size_s,
                    pb_bars=pb_bars_s,
                    pb_depth_atr=pb_depth_s,
                )
                sf_state = ShortState.IDLE
            elif sf_ready > READY_MAX_BARS or bars_since_bo_s > PULLBACK_MAX_BARS + READY_MAX_BARS:
                sf_state = ShortState.IDLE
            elif close > bo_level_s + tick:
                sf_state = ShortState.IDLE

    return rows


def segment_events(events: pd.DataFrame):
    if events.empty:
        return
    yield "LONG", events[events["direction"] == 1]
    yield "SHORT", events[events["direction"] == -1]
    for col, prefix in (
        ("breakout_size", "BreakoutSize"),
        ("pullback_depth_atr", "PullbackDepth"),
        ("pullback_bars", "PullbackBars"),
    ):
        if col not in events.columns:
            continue
        try:
            for q, sub in events.groupby(
                pd.qcut(events[col], 4, duplicates="drop"), observed=True
            ):
                yield f"{prefix} Q{q}", sub
        except ValueError:
            pass
