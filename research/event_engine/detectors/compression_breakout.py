# -*- coding: utf-8
"""S1 Compression Breakout — 压缩态窄区间后的突破（信号 bar = 突破 K）。"""
from __future__ import annotations

import pandas as pd

from research.event_engine.schema import EventRecord

SETUP = "S1_COMPRESSION_BREAKOUT"
RANGE_WINDOW = 10
ATR_RANK_WINDOW = 200
ATR_COMPRESS_PERCENTILE = 0.20
MAX_RANGE_ATR = 1.5
BODY_RATIO_MIN = 0.5


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy().reset_index(drop=True)
    h = out["high"].astype(float)
    lo = out["low"].astype(float)
    o = out["open"].astype(float)
    c = out["close"].astype(float)

    prev_c = c.shift(1)
    tr = pd.concat([(h - lo), (h - prev_c).abs(), (lo - prev_c).abs()], axis=1).max(axis=1)
    out["atr20"] = tr.rolling(20, min_periods=20).mean()
    out["body"] = (c - o).abs()
    rng = (h - lo).clip(lower=1e-9)
    out["range"] = rng
    out["body_ratio"] = out["body"] / rng

    out["prev_range_high"] = h.shift(1).rolling(RANGE_WINDOW, min_periods=RANGE_WINDOW).max()
    out["prev_range_low"] = lo.shift(1).rolling(RANGE_WINDOW, min_periods=RANGE_WINDOW).min()
    out["range_width"] = (
        h.rolling(RANGE_WINDOW, min_periods=RANGE_WINDOW).max()
        - lo.rolling(RANGE_WINDOW, min_periods=RANGE_WINDOW).min()
    )
    out["atr_q20"] = out["atr20"].rolling(
        ATR_RANK_WINDOW, min_periods=ATR_RANK_WINDOW
    ).quantile(ATR_COMPRESS_PERCENTILE)
    # 压缩/窄区间在突破前一根评估，避免突破 K 自身放大 range 导致漏检
    out["prior_atr_compressed"] = out["atr20"].shift(1) <= out["atr_q20"].shift(1)
    out["prior_range_width"] = out["range_width"].shift(1)
    return out


def detect_events(
    df: pd.DataFrame,
    *,
    symbol: str,
) -> list[EventRecord]:
    rows: list[EventRecord] = []
    n = len(df)
    start = max(ATR_RANK_WINDOW, RANGE_WINDOW + 1)

    for i in range(start, n):
        row = df.iloc[i]
        atr = float(row["atr20"])
        if pd.isna(atr) or atr <= 0:
            continue
        if not bool(row["prior_atr_compressed"]):
            continue
        prior_width = row["prior_range_width"]
        if pd.isna(prior_width) or float(prior_width) > MAX_RANGE_ATR * atr:
            continue

        prev_high = row["prev_range_high"]
        prev_low = row["prev_range_low"]
        if pd.isna(prev_high) or pd.isna(prev_low):
            continue

        body_ratio = float(row["body_ratio"])
        if body_ratio < BODY_RATIO_MIN:
            continue

        direction = 0
        close = float(row["close"])
        open_ = float(row["open"])

        if close > float(prev_high) and close > open_:
            direction = 1
        elif close < float(prev_low) and close < open_:
            direction = -1

        if direction == 0:
            continue

        rows.append(
            EventRecord(
                symbol=symbol,
                datetime=row["dt_cst"],
                setup=SETUP,
                direction=direction,
                entry_price=close,
                extra={
                    "atr20": atr,
                    "prior_range_width": float(prior_width),
                    "prior_range_width_atr": float(prior_width) / atr,
                    "body_ratio": body_ratio,
                    "one_r": float(row["range"]),
                    "hour_cst": int(pd.Timestamp(row["dt_cst"]).hour),
                },
            )
        )
    return rows


def segment_events(events: pd.DataFrame):
    if events.empty:
        return
    yield "LONG", events[events["direction"] == 1]
    yield "SHORT", events[events["direction"] == -1]
    if "prior_range_width_atr" in events.columns:
        try:
            for q, sub in events.groupby(
                pd.qcut(events["prior_range_width_atr"], 4, duplicates="drop"), observed=True
            ):
                yield f"PriorRange Q{q}", sub
        except ValueError:
            pass
    if "hour_cst" in events.columns:
        for hour, sub in events.groupby("hour_cst"):
            yield f"Hour {hour:02d}", sub
