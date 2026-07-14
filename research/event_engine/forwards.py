# -*- coding: utf-8
"""统一 forward return / MFE / MAE 标注。"""
from __future__ import annotations

import numpy as np
import pandas as pd

from research.event_engine.schema import FWD_HORIZONS, MFE_WINDOW, EventRecord


def attach_forwards(
    records: list[EventRecord],
    bars_1m: pd.DataFrame,
    *,
    horizons: tuple[int, ...] = FWD_HORIZONS,
    mfe_window: int = MFE_WINDOW,
) -> list[EventRecord]:
    if not records or bars_1m.empty:
        return records

    b1 = bars_1m.sort_values("dt_cst").reset_index(drop=True)
    ends = pd.to_datetime(b1["dt_cst"]).tolist()
    closes = b1["close"].astype(float).to_numpy()
    highs = b1["high"].astype(float).to_numpy()
    lows = b1["low"].astype(float).to_numpy()
    max_k = max(*horizons, mfe_window)

    out: list[EventRecord] = []
    for rec in records:
        ts = pd.Timestamp(rec.datetime)
        if ts.tzinfo is None:
            ts = ts.tz_localize("Asia/Shanghai")
        idx = int(np.searchsorted(ends, ts, side="right"))
        if idx + max_k >= len(b1):
            continue
        entry = float(rec.entry_price)
        direction = int(rec.direction)
        for k in horizons:
            val = direction * (closes[idx + k - 1] - entry)
            rec.set_forward(k, float(val))
        mfe = mae = 0.0
        for j in range(1, mfe_window + 1):
            bar_i = idx + j
            if direction < 0:
                mfe = max(mfe, entry - lows[bar_i])
                mae = max(mae, highs[bar_i] - entry)
            else:
                mfe = max(mfe, highs[bar_i] - entry)
                mae = max(mae, entry - lows[bar_i])
        rec.mfe = mfe
        rec.mae = mae
        out.append(rec)
    return out
