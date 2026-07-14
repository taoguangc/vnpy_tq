# -*- coding: utf-8
"""S2 First Pullback — BrooksScalp v0.1 FSM 事件检测（纯信号，无下单）。"""
from __future__ import annotations

from enum import IntEnum

import numpy as np
import pandas as pd

from research.event_engine.schema import EventRecord

SETUP = "S2_FIRST_PULLBACK"
EMA_PERIOD = 20
ATR_PERIOD = 20
TREND_LEG_ATR = 1.0
PULLBACK_ATR = 0.2
SIGNAL_BODY_RATIO = 0.4


class State(IntEnum):
    IDLE = 0
    WAIT_PULLBACK = 1
    PULLBACK = 2


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy().reset_index(drop=True)
    c = out["close"].astype(float)
    h = out["high"].astype(float)
    lo = out["low"].astype(float)
    o = out["open"].astype(float)

    prev_c = c.shift(1)
    tr = pd.concat([(h - lo), (h - prev_c).abs(), (lo - prev_c).abs()], axis=1).max(axis=1)
    out["atr20"] = tr.rolling(ATR_PERIOD, min_periods=ATR_PERIOD).mean()
    out["ema20"] = c.ewm(span=EMA_PERIOD, adjust=False).mean()
    out["ema20_lag5"] = out["ema20"].shift(5)
    out["close_lag5"] = c.shift(5)
    out["high_lag1"] = h.shift(1)
    out["low_lag1"] = lo.shift(1)
    out["range"] = h - lo
    out["body_ratio"] = (c - o).abs() / out["range"].clip(lower=1e-9)

    bull = (c > out["ema20"]).astype(int)
    bear = (c < out["ema20"]).astype(int)
    out["bull_bars5"] = bull.rolling(5, min_periods=5).sum()
    out["bear_bars5"] = bear.rolling(5, min_periods=5).sum()
    out["trend_leg_move"] = (c - out["close_lag5"]).abs()
    return out


def _trend_at_row(row: pd.Series) -> int:
    if pd.isna(row["ema20_lag5"]) or pd.isna(row["atr20"]):
        return 0
    close = float(row["close"])
    ema_now = float(row["ema20"])
    ema_prev = float(row["ema20_lag5"])
    if close > ema_now and ema_now > ema_prev and int(row["bull_bars5"]) >= 4:
        return 1
    if close < ema_now and ema_now < ema_prev and int(row["bear_bars5"]) >= 4:
        return -1
    return 0


def detect_events(
    df: pd.DataFrame,
    *,
    symbol: str,
) -> list[EventRecord]:
    rows: list[EventRecord] = []
    n = len(df)
    warmup = max(EMA_PERIOD, ATR_PERIOD) + 6

    state = State.IDLE
    trend = 0
    pullback_low = 0.0
    pullback_high = 0.0
    trend_leg_move = 0.0
    pullback_depth_atr = 0.0

    for i in range(warmup, n):
        row = df.iloc[i]
        atr = float(row["atr20"])
        if pd.isna(atr) or atr <= 0:
            state = State.IDLE
            continue

        trend_now = _trend_at_row(row)
        if trend_now == 0:
            state = State.IDLE
            trend = 0
            continue

        if state == State.IDLE:
            move = float(row["trend_leg_move"])
            if move > atr * TREND_LEG_ATR:
                state = State.WAIT_PULLBACK
                trend = trend_now
                trend_leg_move = move
                pullback_depth_atr = 0.0

        elif state == State.WAIT_PULLBACK:
            if trend != trend_now:
                state = State.IDLE
                continue
            if trend == 1:
                dist = abs(float(row["low"]) - float(row["ema20"]))
            else:
                dist = abs(float(row["high"]) - float(row["ema20"]))
            if dist < atr * PULLBACK_ATR:
                state = State.PULLBACK
                pullback_low = float(row["low"])
                pullback_high = float(row["high"])
                if trend == 1:
                    pullback_depth_atr = dist / atr
                else:
                    pullback_depth_atr = dist / atr

        elif state == State.PULLBACK:
            if trend != trend_now:
                state = State.IDLE
                continue

            high = float(row["high"])
            low = float(row["low"])
            close = float(row["close"])
            open_ = float(row["open"])
            body_ratio = float(row["body_ratio"])

            if trend == 1:
                pullback_low = min(pullback_low, low)
                pullback_depth_atr = max(pullback_depth_atr, (float(row["ema20"]) - pullback_low) / atr)
                signal = (
                    high > low
                    and close > open_
                    and close > float(row["high_lag1"])
                    and body_ratio > SIGNAL_BODY_RATIO
                )
                direction = 1
            else:
                pullback_high = max(pullback_high, high)
                pullback_depth_atr = max(pullback_depth_atr, (pullback_high - float(row["ema20"])) / atr)
                signal = (
                    high > low
                    and close < open_
                    and close < float(row["low_lag1"])
                    and body_ratio > SIGNAL_BODY_RATIO
                )
                direction = -1

            if signal:
                rows.append(
                    EventRecord(
                        symbol=symbol,
                        datetime=row["dt_cst"],
                        setup=SETUP,
                        direction=direction,
                        entry_price=close,
                        extra={
                            "trend_leg_move": trend_leg_move,
                            "trend_leg_atr": trend_leg_move / atr,
                            "pullback_depth_atr": pullback_depth_atr,
                            "body_ratio": body_ratio,
                            "one_r": float(row["range"]),
                            "hour_cst": int(pd.Timestamp(row["dt_cst"]).hour),
                        },
                    )
                )
                state = State.IDLE
                trend = 0

    return rows


def segment_events(events: pd.DataFrame):
    if events.empty:
        return
    yield "LONG", events[events["direction"] == 1]
    yield "SHORT", events[events["direction"] == -1]
    if "pullback_depth_atr" in events.columns:
        try:
            for q, sub in events.groupby(
                pd.qcut(events["pullback_depth_atr"], 4, duplicates="drop"), observed=True
            ):
                yield f"PullbackDepth Q{q}", sub
        except ValueError:
            pass
    if "trend_leg_atr" in events.columns:
        try:
            for q, sub in events.groupby(
                pd.qcut(events["trend_leg_atr"], 4, duplicates="drop"), observed=True
            ):
                yield f"TrendLeg Q{q}", sub
        except ValueError:
            pass
