# -*- coding: utf-8 -*-
"""OPP08 强突破 — 纯检测器（从 shadow_dry_scan._match_opp08 提取）。"""
from __future__ import annotations

from typing import Protocol

from strategies.pa_minimal.detectors.schema import PatternMatch


class _StopCap(Protocol):
    def _cap_long_stop(self, raw_stop: float, close: float, atr: float) -> float: ...
    def _cap_short_stop(self, raw_stop: float, close: float, atr: float) -> float: ...


def match_opp08(
    strategy: _StopCap,
    bar,
    ctx: str,
    *,
    atr_5: float,
    tick: float,
    stop_buffer: float,
    ema_20: float,
    prev_high: float,
    recent_5bar_low: float,
    is_strong_bar: bool,
    is_oo: bool,
    is_long_climax: bool,
    is_short_climax: bool,
    bar_range: float,
) -> list[PatternMatch]:
    out: list[PatternMatch] = []
    if ctx == "STRONG_BULL":
        if (bar.close_price > ema_20 and is_strong_bar
                and bar.close_price > bar.open_price
                and bar.close_price > prev_high and not is_long_climax):
            out.append(PatternMatch(
                "OPP08_5M_STRONG_BREAKOUT_LONG", 1,
                bar.high_price + tick,
                strategy._cap_long_stop(bar.low_price - stop_buffer, bar.close_price, atr_5),
                "FAST_TRACK",
            ))
    elif ctx == "STRONG_BEAR":
        if (bar.close_price < ema_20 and is_strong_bar
                and bar.close_price < bar.open_price):
            out.append(PatternMatch(
                "OPP08_5M_STRONG_BREAKOUT_SHORT", -1,
                bar.low_price - tick,
                strategy._cap_short_stop(bar.high_price + stop_buffer, bar.close_price, atr_5),
                "FAST_TRACK",
            ))
    elif ctx == "BEAR_CHANNEL":
        if (not is_oo and is_strong_bar
                and bar_range > atr_5 * 1.5 and not is_short_climax
                and bar.close_price < bar.open_price
                and bar.low_price < recent_5bar_low
                and bar.close_price < ema_20):
            out.append(PatternMatch(
                "OPP08_5M_STRONG_BREAKOUT_SHORT", -1,
                bar.low_price - tick,
                strategy._cap_short_stop(bar.high_price + stop_buffer, bar.close_price, atr_5),
                "FAST_TRACK",
            ))
    return out
