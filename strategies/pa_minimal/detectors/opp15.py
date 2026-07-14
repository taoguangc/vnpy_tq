# -*- coding: utf-8 -*-
"""OPP15 楔形反转 — 纯检测器（从 shadow_dry_scan._match_opp15_trigger 提取）。"""
from __future__ import annotations

from typing import Protocol

from strategies.pa_minimal.detectors.schema import PatternMatch


class _Opp15Context(Protocol):
    wedge_setup_active: bool
    _wedge_direction: int
    wedge_confirmed_p3_high: float
    wedge_arm_time: object
    wedge_arm_trigger_max_bars: int
    wedge_trigger_line: float
    am_5min: object
    wedge_current_alpha: float
    wedge_b_prime_alpha: float
    wedge_p3_body_floor: float

    def _pd_blocks_short_target(self, close: float, atr: float) -> bool: ...
    def _pd_blocks_long_target(self, close: float, atr: float) -> bool: ...
    def _cap_short_stop(self, raw_stop: float, close: float, atr: float) -> float: ...


def match_opp15_trigger(
    strategy: _Opp15Context,
    bar,
    *,
    atr_5: float,
    tick: float,
    is_strong_bar: bool,
) -> list[PatternMatch]:
    if not strategy.wedge_setup_active or strategy._wedge_direction == 0:
        return []
    d = strategy._wedge_direction
    out: list[PatternMatch] = []
    if d == -1:
        p3_price = strategy.wedge_confirmed_p3_high
        if bar.high_price > p3_price + tick:
            return []
        bars_since = (
            int((bar.datetime - strategy.wedge_arm_time).total_seconds() / 300)
            if strategy.wedge_arm_time else 0
        )
        if bars_since > strategy.wedge_arm_trigger_max_bars:
            return []
        trigger_line = strategy.wedge_trigger_line
        if strategy.am_5min.count >= 2:
            trigger_line = min(float(strategy.am_5min.low[-1]), float(strategy.am_5min.low[-2]))
        p3_stop = p3_price + tick
        if (is_strong_bar and bar.close_price < bar.open_price
                and trigger_line > 0 and bar.close_price < trigger_line
                and not strategy._pd_blocks_short_target(bar.close_price, atr_5)):
            out.append(PatternMatch(
                "OPP15_5M_WEDGE_REVERSAL", -1,
                bar.low_price - tick,
                strategy._cap_short_stop(p3_stop, bar.close_price, atr_5),
                "FAST_TRACK",
            ))
        if (strategy.wedge_current_alpha < strategy.wedge_b_prime_alpha
                and bar.close_price < bar.open_price
                and strategy.wedge_p3_body_floor > 0
                and bar.close_price < strategy.wedge_p3_body_floor
                and bars_since <= strategy.wedge_arm_trigger_max_bars
                and not strategy._pd_blocks_short_target(bar.close_price, atr_5)):
            out.append(PatternMatch(
                "OPP15_5M_WEDGE_B_PRIME", -1,
                bar.close_price - tick, p3_stop,
                "DIRECT", is_direct=True,
            ))
        return out
    p3_price = strategy.wedge_confirmed_p3_high
    if bar.low_price < p3_price - tick:
        return []
    bars_since = (
        int((bar.datetime - strategy.wedge_arm_time).total_seconds() / 300)
        if strategy.wedge_arm_time else 0
    )
    if bars_since > strategy.wedge_arm_trigger_max_bars:
        return []
    if (strategy.wedge_current_alpha < strategy.wedge_b_prime_alpha
            and bar.close_price > bar.open_price
            and strategy.wedge_p3_body_floor > 0
            and bar.close_price > strategy.wedge_p3_body_floor
            and bars_since <= strategy.wedge_arm_trigger_max_bars
            and not strategy._pd_blocks_long_target(bar.close_price, atr_5)):
        out.append(PatternMatch(
            "OPP15_5M_WEDGE_B_PRIME_LONG", 1,
            bar.close_price + tick, p3_price - tick,
            "DIRECT", is_direct=True,
        ))
    return out
