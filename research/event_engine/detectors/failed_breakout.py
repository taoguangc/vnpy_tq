# -*- coding: utf-8
"""S3 Failed Breakout 事件检测。"""
from __future__ import annotations

import numpy as np
import pandas as pd

from research.event_engine.schema import EventRecord

LOOKBACK = 20
SETUP = "S3_FAILED_BREAKOUT"


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy().reset_index(drop=True)
    h = out["high"].astype(float)
    lo = out["low"].astype(float)
    o = out["open"].astype(float)
    c = out["close"].astype(float)

    out["prev_20_high"] = h.shift(1).rolling(LOOKBACK, min_periods=LOOKBACK).max()
    out["prev_20_low"] = lo.shift(1).rolling(LOOKBACK, min_periods=LOOKBACK).min()

    out["body"] = (c - o).abs()
    rng = (h - lo).clip(lower=1e-9)
    out["range"] = rng
    out["body_ratio"] = out["body"] / rng
    out["upper_wick"] = h - np.maximum(o, c)
    out["lower_wick"] = np.minimum(o, c) - lo
    out["upper_wick_ratio"] = out["upper_wick"] / rng
    out["lower_wick_ratio"] = out["lower_wick"] / rng

    prev_c = c.shift(1)
    tr = pd.concat([(h - lo), (h - prev_c).abs(), (lo - prev_c).abs()], axis=1).max(axis=1)
    out["atr20"] = tr.rolling(20, min_periods=20).mean()
    out["ema20"] = c.ewm(span=20, adjust=False).mean()
    out["climax_up"] = (c - out["ema20"]) / out["atr20"]
    out["climax_down"] = (out["ema20"] - c) / out["atr20"]
    return out


def detect_events(
    df: pd.DataFrame,
    *,
    symbol: str,
) -> list[EventRecord]:
    rows: list[EventRecord] = []
    n = len(df)

    for i in range(LOOKBACK, n):
        row = df.iloc[i]
        prev_high = row["prev_20_high"]
        prev_low = row["prev_20_low"]
        if pd.isna(prev_high) or pd.isna(prev_low):
            continue

        direction = 0
        breakout_size = 0.0
        wick_ratio = 0.0

        if (
            row["high"] > prev_high
            and row["close"] < prev_high
            and row["upper_wick"] > row["body"]
        ):
            direction = -1
            breakout_size = float(row["high"] - prev_high)
            wick_ratio = float(row["upper_wick_ratio"])
        elif (
            row["low"] < prev_low
            and row["close"] > prev_low
            and row["lower_wick"] > row["body"]
        ):
            direction = 1
            breakout_size = float(prev_low - row["low"])
            wick_ratio = float(row["lower_wick_ratio"])

        if direction == 0:
            continue

        one_r = float(row["range"])
        rows.append(
            EventRecord(
                symbol=symbol,
                datetime=row["dt_cst"],
                setup=SETUP,
                direction=direction,
                entry_price=float(row["close"]),
                extra={
                    "breakout_size": breakout_size,
                    "body_ratio": float(row["body_ratio"]),
                    "wick_ratio": wick_ratio,
                    "one_r": one_r,
                    "climax_up": float(row["climax_up"]) if not pd.isna(row["climax_up"]) else np.nan,
                    "climax_down": float(row["climax_down"]) if not pd.isna(row["climax_down"]) else np.nan,
                    "hour_cst": int(pd.Timestamp(row["dt_cst"]).hour),
                },
            )
        )
    return rows


def segment_events(events: pd.DataFrame):
    from research.event_engine.summary import failed_breakout_segments

    return failed_breakout_segments(events)
