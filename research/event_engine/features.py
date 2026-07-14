# -*- coding: utf-8
"""事件时刻 regime / AFF 特征（15m）。"""
from __future__ import annotations

import numpy as np
import pandas as pd

from research.event_engine.bars import resample_ohlc
from research.event_engine.schema import EventRecord
from strategies.pa_cta.aff_gate import compute_aff_snapshot

ATR_WINDOW = 14


def _atr_sma(high, low, close, period: int) -> float:
    n = len(close)
    if n < period:
        return 0.0
    tr = np.empty(n, dtype=np.float64)
    tr[0] = high[0] - low[0]
    if n > 1:
        hl = high[1:] - low[1:]
        hc = np.abs(high[1:] - close[:-1])
        lc = np.abs(low[1:] - close[:-1])
        tr[1:] = np.maximum(hl, np.maximum(hc, lc))
    kernel = np.ones(period, dtype=np.float64) / period
    atr_tail = np.convolve(tr, kernel, mode="valid")
    return float(atr_tail[-1]) if len(atr_tail) else 0.0


def attach_regime_features(
    records: list[EventRecord],
    bars_1m: pd.DataFrame,
) -> list[EventRecord]:
    if not records:
        return records

    bars_5m = resample_ohlc(bars_1m, "5min")
    bars_15m = resample_ohlc(bars_1m, "15min")
    if len(bars_15m) < 30:
        return records

    idx_15 = bars_15m.index
    idx_5 = bars_5m.index

    for rec in records:
        ts = pd.Timestamp(rec.datetime)
        if ts.tzinfo is None:
            ts = ts.tz_localize("Asia/Shanghai")
        else:
            ts = ts.tz_convert("Asia/Shanghai")

        end_15 = int(idx_15.searchsorted(ts, side="right"))
        end_5 = int(idx_5.searchsorted(ts, side="right"))
        if end_15 < 30:
            continue

        b15 = bars_15m.iloc[:end_15]
        b5 = bars_5m.iloc[:end_5]

        snap = compute_aff_snapshot(
            b15["close"].to_numpy(),
            b15["high"].to_numpy(),
            b15["low"].to_numpy(),
            b15["open"].to_numpy(),
        )
        atr_5 = _atr_sma(
            b5["high"].to_numpy(), b5["low"].to_numpy(), b5["close"].to_numpy(), ATR_WINDOW
        )
        atr_15 = _atr_sma(
            b15["high"].to_numpy(), b15["low"].to_numpy(), b15["close"].to_numpy(), ATR_WINDOW
        )
        atr_ratio = round(atr_5 / atr_15, 3) if atr_15 > 0 and atr_5 > 0 else 0.0

        rec.features.update(
            {
                "compression_score": snap.compression_score,
                "alpha_strength": snap.alpha_strength,
                "env_score": snap.env_score,
                "er": snap.er,
                "atr_ratio": atr_ratio,
            }
        )
    return records
