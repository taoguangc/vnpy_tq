# -*- coding: utf-8 -*-
"""AFF 规则版门禁：15m Compression × ER → alpha_strength（NumPy 实现，无 pandas）。"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

_ATR_PERIOD = 14
_BB_PERIOD = 20


def env_score(er: float, er_thresholds: dict | None = None) -> float:
    """AFF 环境强度（自 aff.core.alpha_strength 内联，避免 aff 包依赖）。"""
    if er_thresholds is None:
        er_thresholds = {
            "very_weak": 0.20,
            "weak": 0.25,
            "moderate": 0.30,
            "strong": 0.35,
        }
    if er < er_thresholds["very_weak"]:
        return 0.0
    if er < er_thresholds["weak"]:
        return 0.25
    if er < er_thresholds["moderate"]:
        return 0.50
    if er < er_thresholds["strong"]:
        return 0.75
    return 1.00


@dataclass(frozen=True)
class AffSnapshot:
    alpha_strength: float = 0.0
    compression_score: float = 0.0
    env_score: float = 0.0
    er: float = 0.0


def _as_f64(arr) -> np.ndarray:
    return np.asarray(arr, dtype=np.float64)


def _compression_score(atr_c: int, bb_c: int, nr7_c: int) -> float:
    """与 aff.core.factors.compression_score 权重一致。"""
    score = 0.0
    if atr_c:
        score += 0.6
    if bb_c:
        score += 0.3
    if nr7_c:
        score += 0.1
    return score


def _calc_atr_sma(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int) -> np.ndarray:
    """与 aff.core.indicators.calc_atr 一致：TR + SMA，前 period-1 为 nan。"""
    n = len(close)
    tr = np.empty(n, dtype=np.float64)
    tr[0] = high[0] - low[0]
    if n > 1:
        hl = high[1:] - low[1:]
        hc = np.abs(high[1:] - close[:-1])
        lc = np.abs(low[1:] - close[:-1])
        tr[1:] = np.maximum(hl, np.maximum(hc, lc))
    atr = np.full(n, np.nan, dtype=np.float64)
    if n >= period:
        kernel = np.ones(period, dtype=np.float64) / period
        atr[period - 1:] = np.convolve(tr, kernel, mode="valid")
    return np.nan_to_num(atr, nan=0.0)


def _bb_width_series(close: np.ndarray, period: int) -> np.ndarray:
    """与 aff.core.indicators.bb_width 一致：2*std/mid，ddof=1。"""
    n = len(close)
    out = np.full(n, np.nan, dtype=np.float64)
    if n < period:
        return out
    windows = sliding_window_view(close, period)
    mids = windows.mean(axis=1)
    stds = windows.std(axis=1, ddof=1)
    valid = mids > 0
    width = np.full(len(mids), np.nan, dtype=np.float64)
    width[valid] = 2.0 * stds[valid] / mids[valid]
    out[period - 1:] = width
    return out


def _rolling_quantile_tail(arr: np.ndarray, window: int, q: float, min_periods: int) -> float | None:
    """对齐 pandas rolling(window, min_periods).quantile：窗口内非 NaN 数须达 min_periods。"""
    tail = arr[-window:]
    valid = tail[~np.isnan(tail)]
    if len(valid) < min_periods:
        return None
    return float(np.quantile(valid, q, method="linear"))


def _efficiency_ratio(close: np.ndarray, period: int) -> float:
    """与 aff.core.indicators.efficiency_ratio 末值一致。"""
    if len(close) < period + 1:
        return 0.0
    direction = abs(close[-1] - close[-period - 1])
    volatility = float(np.abs(np.diff(close[-(period + 1):])).sum())
    if volatility <= 0:
        return 0.0
    return direction / volatility


def _nr7_flag(high: np.ndarray, low: np.ndarray) -> int:
    """与 aff.core.indicators.nr7 末值一致。"""
    bar_range = high - low
    if len(bar_range) < 7:
        return 0
    return int(bar_range[-1] == bar_range[-7:].min())


def compute_aff_snapshot(
    closes,
    highs,
    lows,
    opens,
    *,
    er_period: int = 20,
    quantile_window: int = 200,
    min_bars: int = 30,
    atr_period: int = _ATR_PERIOD,
    bb_period: int = _BB_PERIOD,
) -> AffSnapshot:
    """从 15m OHLC 序列计算 AFF alpha（无未来函数，仅用历史 bar）。"""
    del opens  # 保留签名兼容；当前公式未使用 open
    close = _as_f64(closes)
    high = _as_f64(highs)
    low = _as_f64(lows)
    n = len(close)
    if n < min_bars:
        return AffSnapshot()

    window = min(n, quantile_window)

    atr = _calc_atr_sma(high, low, close, atr_period)
    atr_last = float(atr[-1])

    atr_thresh = _rolling_quantile_tail(atr, window, 0.2, min_bars)
    atr_c = int(atr_last < atr_thresh) if atr_thresh is not None else 0

    bb_width = _bb_width_series(close, bb_period)
    bb_last = bb_width[-1]
    bb_thresh = _rolling_quantile_tail(bb_width, window, 0.2, min_bars)
    bb_c = (
        int(bb_last < bb_thresh)
        if bb_thresh is not None and not np.isnan(bb_last)
        else 0
    )

    nr7_c = _nr7_flag(high, low)
    comp = _compression_score(atr_c, bb_c, nr7_c)
    er = _efficiency_ratio(close, er_period)
    env = float(env_score(er))
    alpha = env * comp

    return AffSnapshot(
        alpha_strength=alpha,
        compression_score=comp,
        env_score=env,
        er=er,
    )
