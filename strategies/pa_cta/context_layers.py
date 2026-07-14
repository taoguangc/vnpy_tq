# -*- coding: utf-8 -*-
"""15m 快层 / 慢层连续背景因子。

设计原则：
  - 保留离散 market_context 作路由标签；
  - 快层（默认 10 根 15m）刻画当前入场环境；
  - 慢层（默认 30 根，可 20～40）刻画趋势持续性与波动异常；
  - OPP08 / OPP16 读取连续因子，而非只依赖硬状态名。

本模块为纯函数；策略侧默认只刷新与记账，拒单门禁默认关。
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from strategies.pa_cta.regime_gate import compute_chop_index, compute_trend_r2


@dataclass(frozen=True, slots=True)
class FastLayerFactors:
    """快层：约 2.5 小时（10×15m）入场环境。"""

    n_bars: int
    trend_r2: float
    chop: float
    ema_slope_atr: float  # (ema[-1]-ema[-n]) / atr
    close_vs_ema_atr: float
    er: float  # efficiency ratio
    atr_vs_median: float  # 当前 atr / 快窗中位 TR
    ready: bool = False


@dataclass(frozen=True, slots=True)
class SlowLayerFactors:
    """慢层：约 5～10 小时（20～40×15m）趋势与波动。"""

    n_bars: int
    trend_r2: float
    chop: float
    ema_slope_atr: float
    close_vs_ema_atr: float
    er: float
    atr_vs_median: float  # 当前 atr / 慢窗中位 TR（>1 波动偏高）
    atr_percentile: float  # 当前 TR 在慢窗内的分位 0～1
    ready: bool = False


@dataclass(frozen=True, slots=True)
class ContextLayerSnapshot:
    fast: FastLayerFactors
    slow: SlowLayerFactors
    # 合成：慢层确认后的方向质量（[-1,1]）
    trend_quality: float
    # 波动异常：慢层 ATR 相对中位偏离（0=正常）
    vol_abnormality: float
    # OPP 可读连续适配分（0～1，越高越适合）
    opp08_fit: float
    opp16_fit: float

    def to_dict(self) -> dict:
        d = {
            "trend_quality": self.trend_quality,
            "vol_abnormality": self.vol_abnormality,
            "opp08_fit": self.opp08_fit,
            "opp16_fit": self.opp16_fit,
        }
        for prefix, layer in (("fast", self.fast), ("slow", self.slow)):
            for k, v in asdict(layer).items():
                d[f"{prefix}_{k}"] = v
        return d


def _empty_fast(n: int) -> FastLayerFactors:
    return FastLayerFactors(
        n_bars=n, trend_r2=0.0, chop=100.0, ema_slope_atr=0.0,
        close_vs_ema_atr=0.0, er=0.0, atr_vs_median=1.0, ready=False,
    )


def _empty_slow(n: int) -> SlowLayerFactors:
    return SlowLayerFactors(
        n_bars=n, trend_r2=0.0, chop=100.0, ema_slope_atr=0.0,
        close_vs_ema_atr=0.0, er=0.0, atr_vs_median=1.0,
        atr_percentile=0.5, ready=False,
    )


def empty_snapshot(
    *,
    fast_n: int = 10,
    slow_n: int = 30,
) -> ContextLayerSnapshot:
    return ContextLayerSnapshot(
        fast=_empty_fast(fast_n),
        slow=_empty_slow(slow_n),
        trend_quality=0.0,
        vol_abnormality=0.0,
        opp08_fit=0.5,
        opp16_fit=0.5,
    )


def _efficiency_ratio(closes: np.ndarray, period: int) -> float:
    if period < 2 or len(closes) < period:
        return 0.0
    y = np.asarray(closes[-period:], dtype=np.float64)
    if not np.all(np.isfinite(y)):
        return 0.0
    net = abs(float(y[-1] - y[0]))
    path = float(np.sum(np.abs(np.diff(y))))
    if path <= 1e-12:
        return 0.0
    return max(0.0, min(1.0, net / path))


def _ema_slope_atr(ema: np.ndarray, atr: float, n: int) -> float:
    if atr <= 1e-12 or len(ema) < n or not np.isfinite(ema[-1]) or not np.isfinite(ema[-n]):
        return 0.0
    return float(ema[-1] - ema[-n]) / atr


def _tr_series(high: np.ndarray, low: np.ndarray, close: np.ndarray) -> np.ndarray:
    h = np.asarray(high, dtype=np.float64)
    l = np.asarray(low, dtype=np.float64)
    c = np.asarray(close, dtype=np.float64)
    tr = np.empty(len(c), dtype=np.float64)
    tr[0] = h[0] - l[0]
    if len(c) > 1:
        hl = h[1:] - l[1:]
        hc = np.abs(h[1:] - c[:-1])
        lc = np.abs(l[1:] - c[:-1])
        tr[1:] = np.maximum(hl, np.maximum(hc, lc))
    return tr


def compute_fast_layer(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    ema: np.ndarray,
    atr: float,
    *,
    n_bars: int = 10,
) -> FastLayerFactors:
    n = int(n_bars)
    if n < 3 or len(close) < n or len(ema) < n or atr <= 0:
        return _empty_fast(n)
    tr = _tr_series(high[-n:], low[-n:], close[-n:])
    med_tr = float(np.median(tr)) if len(tr) else 0.0
    atr_vs = (atr / med_tr) if med_tr > 1e-12 else 1.0
    return FastLayerFactors(
        n_bars=n,
        trend_r2=compute_trend_r2(close, period=n),
        chop=compute_chop_index(high, low, close, period=min(n, max(n - 1, 2))),
        ema_slope_atr=_ema_slope_atr(ema, atr, n),
        close_vs_ema_atr=(float(close[-1]) - float(ema[-1])) / atr if np.isfinite(ema[-1]) else 0.0,
        er=_efficiency_ratio(close, n),
        atr_vs_median=float(atr_vs),
        ready=True,
    )


def compute_slow_layer(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    ema: np.ndarray,
    atr: float,
    *,
    n_bars: int = 30,
) -> SlowLayerFactors:
    n = int(n_bars)
    n = max(20, min(40, n))
    if len(close) < n or len(ema) < n or atr <= 0:
        return _empty_slow(n)
    tr = _tr_series(high[-n:], low[-n:], close[-n:])
    med_tr = float(np.median(tr)) if len(tr) else 0.0
    atr_vs = (atr / med_tr) if med_tr > 1e-12 else 1.0
    cur_tr = float(tr[-1]) if len(tr) else 0.0
    if len(tr) >= 3:
        pct = float(np.searchsorted(np.sort(tr), cur_tr) / len(tr))
    else:
        pct = 0.5
    chop_p = min(14, n)
    return SlowLayerFactors(
        n_bars=n,
        trend_r2=compute_trend_r2(close, period=n),
        chop=compute_chop_index(high, low, close, period=chop_p),
        ema_slope_atr=_ema_slope_atr(ema, atr, n),
        close_vs_ema_atr=(float(close[-1]) - float(ema[-1])) / atr if np.isfinite(ema[-1]) else 0.0,
        er=_efficiency_ratio(close, n),
        atr_vs_median=float(atr_vs),
        atr_percentile=max(0.0, min(1.0, pct)),
        ready=True,
    )


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def synthesize_snapshot(
    fast: FastLayerFactors,
    slow: SlowLayerFactors,
) -> ContextLayerSnapshot:
    """合成趋势质量、波动异常与 OPP 适配分。"""
    if not fast.ready and not slow.ready:
        return empty_snapshot(fast_n=fast.n_bars, slow_n=slow.n_bars)

    # 趋势质量：慢层方向为主，快层同向加分
    slow_dir = np.sign(slow.ema_slope_atr) if slow.ready else 0.0
    fast_dir = np.sign(fast.ema_slope_atr) if fast.ready else 0.0
    persist = 0.0
    if slow.ready:
        persist = 0.5 * slow.trend_r2 + 0.3 * slow.er + 0.2 * max(0.0, 1.0 - slow.chop / 100.0)
        persist *= abs(slow_dir)  # 无方向则质量归零附近
        if fast.ready and fast_dir == slow_dir and slow_dir != 0:
            persist = min(1.0, persist + 0.15 * fast.er)
        trend_quality = float(slow_dir) * _clip01(persist)
    else:
        trend_quality = float(fast_dir) * _clip01(0.5 * fast.trend_r2 + 0.5 * fast.er) if fast.ready else 0.0

    vol_abn = 0.0
    if slow.ready:
        # |atr/median - 1| 与分位两端共同刻画异常
        vol_abn = abs(slow.atr_vs_median - 1.0)
        if slow.atr_percentile <= 0.15 or slow.atr_percentile >= 0.85:
            vol_abn = max(vol_abn, abs(slow.atr_percentile - 0.5))

    # OPP08：需要持续性趋势 + 快层同向 + 波动不过度压缩
    tq = abs(trend_quality)
    align = 1.0 if (fast.ready and slow.ready and fast_dir == slow_dir and slow_dir != 0) else (
        0.6 if slow.ready and slow_dir != 0 else 0.3
    )
    not_too_tight = 1.0
    if slow.ready and slow.atr_percentile < 0.2:
        not_too_tight = 0.4
    opp08_fit = _clip01(0.55 * tq + 0.25 * align + 0.20 * not_too_tight)

    # OPP16：弱趋势/震荡或延伸后更适合；强持续趋势降分
    mean_revert_env = 0.0
    if slow.ready:
        mean_revert_env = _clip01(0.5 * (slow.chop / 100.0) + 0.3 * (1.0 - slow.er) + 0.2 * (1.0 - slow.trend_r2))
    elif fast.ready:
        mean_revert_env = _clip01(0.5 * (fast.chop / 100.0) + 0.5 * (1.0 - fast.er))
    extension = 0.0
    if fast.ready:
        extension = _clip01(abs(fast.close_vs_ema_atr) / 2.0)
    opp16_fit = _clip01(0.55 * mean_revert_env + 0.25 * extension + 0.20 * (1.0 - tq))

    return ContextLayerSnapshot(
        fast=fast,
        slow=slow,
        trend_quality=float(max(-1.0, min(1.0, trend_quality))),
        vol_abnormality=float(vol_abn),
        opp08_fit=opp08_fit,
        opp16_fit=opp16_fit,
    )


def compute_context_layers(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    ema: np.ndarray,
    atr: float,
    *,
    fast_n: int = 10,
    slow_n: int = 30,
) -> ContextLayerSnapshot:
    fast = compute_fast_layer(high, low, close, ema, atr, n_bars=fast_n)
    slow = compute_slow_layer(high, low, close, ema, atr, n_bars=slow_n)
    return synthesize_snapshot(fast, slow)


def layer_gate_blocks(
    snapshot: ContextLayerSnapshot,
    *,
    setup: str,
    direction: int,
    min_opp08_fit: float = 0.45,
    min_opp16_fit: float = 0.40,
    require_slow_ready: bool = True,
) -> str:
    """可选软门禁：返回空串=通过，否则为拦截原因。默认不在生产路径调用。"""
    name = setup or ""
    if require_slow_ready and not snapshot.slow.ready:
        return ""  # 数据不足时不拦，避免冷启动误杀
    if name.startswith("OPP08_"):
        if snapshot.opp08_fit < min_opp08_fit:
            return "context_layer_opp08_fit"
        # 方向与慢层趋势质量同号更佳
        if abs(snapshot.trend_quality) >= 0.25:
            if direction > 0 and snapshot.trend_quality < 0:
                return "context_layer_opp08_counter"
            if direction < 0 and snapshot.trend_quality > 0:
                return "context_layer_opp08_counter"
    elif name.startswith("OPP16_"):
        if snapshot.opp16_fit < min_opp16_fit:
            return "context_layer_opp16_fit"
    return ""
