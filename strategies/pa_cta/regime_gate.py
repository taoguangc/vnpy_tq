# -*- coding: utf-8 -*-
"""15m 趋势/震荡 regime：R² 与 Choppiness Index（Setup 层趋势延续门禁用）。"""
from __future__ import annotations

import math

import numpy as np


def compute_trend_r2(closes: np.ndarray, period: int = 20) -> float:
    """近 period 根收盘对时间的线性 R²，0=无方向/震荡，1=强线性推进。"""
    if period < 3 or len(closes) < period:
        return 0.0
    y = np.asarray(closes[-period:], dtype=np.float64)
    if not np.all(np.isfinite(y)):
        return 0.0
    y_mean = float(y.mean())
    ss_tot = float(np.sum((y - y_mean) ** 2))
    if ss_tot <= 1e-12:
        return 0.0
    x = np.arange(period, dtype=np.float64)
    slope, intercept = np.polyfit(x, y, 1)
    y_pred = slope * x + intercept
    ss_res = float(np.sum((y - y_pred) ** 2))
    return max(0.0, min(1.0, 1.0 - ss_res / ss_tot))


def compute_chop_index(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    period: int = 14,
) -> float:
    """Choppiness Index：高值=震荡，低值=趋势。无数据时返回 100（保守视为 chop）。"""
    if period < 2 or len(close) < period:
        return 100.0
    h = np.asarray(high[-period:], dtype=np.float64)
    l = np.asarray(low[-period:], dtype=np.float64)
    c = np.asarray(close[-period:], dtype=np.float64)
    if not (np.all(np.isfinite(h)) and np.all(np.isfinite(l)) and np.all(np.isfinite(c))):
        return 100.0
    hl_range = float(np.max(h) - np.min(l))
    if hl_range <= 1e-12:
        return 100.0
    tr = np.empty(period, dtype=np.float64)
    tr[0] = h[0] - l[0]
    if period > 1:
        hl = h[1:] - l[1:]
        hc = np.abs(h[1:] - c[:-1])
        lc = np.abs(l[1:] - c[:-1])
        tr[1:] = np.maximum(hl, np.maximum(hc, lc))
    tr_sum = float(tr.sum())
    if tr_sum <= 1e-12:
        return 100.0
    return 100.0 * math.log10(tr_sum / hl_range) / math.log10(period)
