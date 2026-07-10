# -*- coding: utf-8 -*-
"""Brooks PA 单棒/多棒 K 线形态 — 纯函数，与 wedge.py 同模式。"""
from __future__ import annotations

from dataclasses import dataclass

from vnpy_ctastrategy import BarData


@dataclass(frozen=True, slots=True)
class PatternThresholds:
    """形态判定阈值（由策略 setting 注入）。"""

    bar_outside_prev_ratio: float
    bar_trend_body_ratio: float
    bar_spike_tail_body_ratio: float
    reversal_shadow_min_ratio: float
    reversal_close_quarter: float
    reversal_min_body_ratio: float
    boundary_reversal_shadow_ratio: float
    boundary_reversal_close_ratio: float
    strong_bar_body_ratio: float
    strong_bar_atr_mult: float


@dataclass(frozen=True, slots=True)
class BarMetrics:
    """单根 K 线 OHLC 派生量（一次计算，供多形态复用）。"""

    open: float
    high: float
    low: float
    close: float
    bar_range: float
    body: float
    body_ratio: float
    upper_shadow: float
    lower_shadow: float

    @classmethod
    def from_bar(cls, bar: BarData) -> BarMetrics:
        o = float(bar.open_price)
        h = float(bar.high_price)
        low = float(bar.low_price)
        c = float(bar.close_price)
        bar_range = h - low
        body = abs(c - o)
        if bar_range <= 0:
            body_ratio = 0.0
        else:
            body_ratio = body / bar_range
        upper_shadow = h - max(o, c)
        lower_shadow = min(o, c) - low
        return cls(
            open=o,
            high=h,
            low=low,
            close=c,
            bar_range=bar_range,
            body=body,
            body_ratio=body_ratio,
            upper_shadow=upper_shadow,
            lower_shadow=lower_shadow,
        )


def classify_bar_shape(
    bar: BarMetrics,
    prev: BarMetrics | None,
    th: PatternThresholds,
) -> str:
    """单棒形态标签：OUTSIDE_UP / UP_TREND / DOJI / …"""
    if bar.bar_range <= 0:
        return ""
    if prev is not None and prev.bar_range > 0:
        if bar.bar_range >= prev.bar_range * th.bar_outside_prev_ratio:
            if bar.close > prev.high and bar.close > bar.open:
                return "OUTSIDE_UP"
            if bar.close < prev.low and bar.close < bar.open:
                return "OUTSIDE_DOWN"
    if bar.body_ratio >= th.bar_trend_body_ratio:
        tail_cap = bar.bar_range * (1 - th.bar_trend_body_ratio) * 0.5
        if bar.close > bar.open and bar.lower_shadow <= tail_cap:
            return "UP_TREND"
        if bar.close < bar.open and bar.upper_shadow <= tail_cap:
            return "DOWN_TREND"
    if bar.body > 0 and bar.body_ratio < 0.5:
        if (
            bar.upper_shadow >= bar.body * th.bar_spike_tail_body_ratio
            and bar.upper_shadow > bar.lower_shadow
        ):
            return "SPIKE_UP"
        if (
            bar.lower_shadow >= bar.body * th.bar_spike_tail_body_ratio
            and bar.lower_shadow > bar.upper_shadow
        ):
            return "SPIKE_DOWN"
    if bar.body_ratio < 0.1:
        return "DOJI"
    return ""


def is_outside_outside(
    highs: tuple[float, float, float],
    lows: tuple[float, float, float],
) -> bool:
    """双外吞（outside-outside）：h1>h2>h3 且 l1<l2<l3（index 1=当前）。"""
    h1, h2, h3 = highs
    l1, l2, l3 = lows
    return h1 > h2 and l1 < l2 and h2 > h3 and l2 < l3


def is_bull_reversal(bar: BarMetrics, bar_range: float, th: PatternThresholds) -> bool:
    return (
        bar.lower_shadow >= bar_range * th.reversal_shadow_min_ratio
        and bar.close >= bar.high - bar_range * th.reversal_close_quarter
        and bar.body >= bar_range * th.reversal_min_body_ratio
    )


def is_bear_reversal(bar: BarMetrics, bar_range: float, th: PatternThresholds) -> bool:
    return (
        bar.upper_shadow >= bar_range * th.reversal_shadow_min_ratio
        and bar.close <= bar.low + bar_range * th.reversal_close_quarter
        and bar.body >= bar_range * th.reversal_min_body_ratio
    )


def is_boundary_bull_reversal(bar: BarMetrics, bar_range: float, th: PatternThresholds) -> bool:
    return (
        bar.lower_shadow >= bar_range * th.boundary_reversal_shadow_ratio
        and bar.close >= bar.high - bar_range * th.boundary_reversal_close_ratio
    )


def is_boundary_bear_reversal(bar: BarMetrics, bar_range: float, th: PatternThresholds) -> bool:
    return (
        bar.upper_shadow >= bar_range * th.boundary_reversal_shadow_ratio
        and bar.close <= bar.low + bar_range * th.boundary_reversal_close_ratio
    )


def is_quality_day_high_short(
    bar: BarMetrics,
    bar_range: float,
    is_boundary_bear: bool,
) -> bool:
    return (
        is_boundary_bear
        and bar.upper_shadow >= bar_range * 0.40
        and bar.close <= bar.high - bar_range * 0.35
    )


def is_strong_bar(bar: BarMetrics, bar_range: float, atr_5: float, th: PatternThresholds) -> bool:
    return (
        bar.body >= bar_range * th.strong_bar_body_ratio
        and bar_range > atr_5 * th.strong_bar_atr_mult
    )
