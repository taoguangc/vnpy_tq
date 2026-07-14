# -*- coding: utf-8 -*-
"""OPP16 两棒反转 — 纯检测器（从 shadow_dry_scan._match_opp16 提取）。"""
from __future__ import annotations

from typing import Protocol

from strategies.pa_minimal.detectors.schema import PatternMatch


class _Opp16Context(Protocol):
    two_bar_rev_context: str
    two_bar_rev_body_ratio: float
    prev_bar_shape: str
    opp16_strict_shape: bool
    am_5min: object

    def _cap_long_stop(self, raw_stop: float, close: float, atr: float) -> float: ...
    def _cap_short_stop(self, raw_stop: float, close: float, atr: float) -> float: ...


def match_opp16(
    strategy: _Opp16Context,
    bar,
    ctx: str,
    *,
    atr_5: float,
    tick: float,
    stop_buffer: float,
    bar_range: float,
) -> list[PatternMatch]:
    if bar_range <= tick or strategy.am_5min.count < 2:
        return []
    allowed = {s.strip() for s in strategy.two_bar_rev_context.split(",") if s.strip()}
    if ctx not in allowed:
        return []
    prev_close = float(strategy.am_5min.close[-2])
    prev_open = float(strategy.am_5min.open[-2])
    prev_high = float(strategy.am_5min.high[-2])
    prev_low = float(strategy.am_5min.low[-2])
    prev_range = prev_high - prev_low
    if prev_range <= 0:
        return []
    prev_body_ratio = abs(prev_close - prev_open) / prev_range
    prev_mid = (prev_high + prev_low) / 2.0
    prev_shape = getattr(strategy, "_opp16_prev_shape", None) or strategy.prev_bar_shape or ""
    strong_shapes = ("UP_TREND", "DOWN_TREND", "OUTSIDE_UP", "OUTSIDE_DOWN")
    is_strong = (
        prev_body_ratio >= strategy.two_bar_rev_body_ratio
        and prev_shape in strong_shapes)
    strict = bool(getattr(strategy, "opp16_strict_shape", False))
    if strict:
        if not is_strong:
            return []
    elif prev_body_ratio < strategy.two_bar_rev_body_ratio:
        return []
    out: list[PatternMatch] = []
    if prev_close < prev_open and bar.close_price > prev_mid:
        out.append(PatternMatch(
            "OPP16_5M_TWO_BAR_REV_LONG", 1,
            bar.high_price + tick,
            strategy._cap_long_stop(bar.low_price - stop_buffer, bar.close_price, atr_5),
            "PENDING_CONFIRM",
        ))
    if prev_close > prev_open and bar.close_price < prev_mid:
        out.append(PatternMatch(
            "OPP16_5M_TWO_BAR_REV_SHORT", -1,
            bar.low_price - tick,
            strategy._cap_short_stop(bar.high_price + stop_buffer, bar.close_price, atr_5),
            "PENDING_CONFIRM",
        ))
    return out
