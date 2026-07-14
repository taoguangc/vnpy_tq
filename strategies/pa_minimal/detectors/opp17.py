# -*- coding: utf-8 -*-
"""OPP17 高潮反转 — 纯检测器（从 shadow_dry_scan._match_opp17 提取）。"""
from __future__ import annotations

from typing import Protocol

from strategies.pa_minimal.detectors.schema import PatternMatch


class _Opp17Context(Protocol):
    climax_rev_context: str
    climax_rev_range_atr: float
    am_5min: object

    def _cap_long_stop(self, raw_stop: float, close: float, atr: float) -> float: ...
    def _cap_short_stop(self, raw_stop: float, close: float, atr: float) -> float: ...


def match_opp17(
    strategy: _Opp17Context,
    bar,
    ctx: str,
    *,
    atr_5: float,
    tick: float,
    stop_buffer: float,
    bar_range: float,
    is_oo: bool,
) -> list[PatternMatch]:
    if is_oo or bar_range <= tick or atr_5 <= 0:
        return []
    allowed = {s.strip() for s in strategy.climax_rev_context.split(",") if s.strip()}
    if ctx not in allowed:
        return []
    prev_high = float(strategy.am_5min.high[-2])
    prev_low = float(strategy.am_5min.low[-2])
    prev_close = float(strategy.am_5min.close[-2])
    prev_open = float(strategy.am_5min.open[-2])
    prev_range = prev_high - prev_low
    if prev_range <= 0 or prev_range <= strategy.climax_rev_range_atr * atr_5:
        return []
    prev_mid = (prev_high + prev_low) / 2.0
    out: list[PatternMatch] = []
    if prev_close < prev_open and bar.close_price > prev_mid:
        out.append(PatternMatch(
            "OPP17_5M_CLIMAX_REV_LONG", 1,
            bar.high_price + tick,
            strategy._cap_long_stop(bar.low_price - stop_buffer, bar.close_price, atr_5),
            "PENDING_CONFIRM",
        ))
    if prev_close > prev_open and bar.close_price < prev_mid:
        out.append(PatternMatch(
            "OPP17_5M_CLIMAX_REV_SHORT", -1,
            bar.low_price - tick,
            strategy._cap_short_stop(bar.high_price + stop_buffer, bar.close_price, atr_5),
            "PENDING_CONFIRM",
        ))
    return out
