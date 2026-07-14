# -*- coding: utf-8 -*-
"""OPP19 开盘驱动 — 纯检测器（从 shadow_dry_scan._match_opp19 提取）。"""
from __future__ import annotations

from typing import Protocol

from strategies.pa_minimal.detectors.schema import PatternMatch


class _Opp19Context(Protocol):
    _od_state: str
    opening_rev_enabled: bool
    _od_bars_collected: int
    _od_bar1_shape: str
    _od_bar1_mid: float
    opening_rev_body_ratio: float
    opp19_rev_arm_mode: str
    _od_high: float
    _od_low: float
    opp19_breakout_r2_gate_enabled: bool
    opp19_breakout_r2_min: float
    opp19_breakout_aff_gate_enabled: bool
    opp19_breakout_aff_alpha_min: float
    opening_drive_min_body: float
    _aff_alpha_strength: float

    def _opening_rev_allows_entry(self, direction: int, ctx: str, atr: float) -> bool: ...
    def _opening_rev_in_time_window(
        self, bar_time: object, *, is_morning: bool, is_night: bool,
    ) -> bool: ...
    def _trend_regime_blocks_continuation(self, min_r2: float) -> bool: ...
    def _opening_drive_breakout_context_ok(self, direction: int, ctx: str) -> bool: ...
    def _cap_long_stop(self, raw_stop: float, close: float, atr: float) -> float: ...
    def _cap_short_stop(self, raw_stop: float, close: float, atr: float) -> float: ...


def match_opp19(
    strategy: _Opp19Context,
    bar,
    ctx: str,
    *,
    atr_5: float,
    tick: float,
    stop_buffer: float,
    bar_range: float,
    body: float,
    is_strong_bar: bool,
    is_oo: bool,
) -> list[PatternMatch]:
    """只读：基于当前 OD 状态判断本 bar 是否可触发（不推进 COLLECTING）。"""
    if is_oo or bar_range <= tick or atr_5 <= 0:
        return []
    from datetime import time

    bar_time = bar.datetime.time()
    is_morning = time(9, 0) <= bar_time <= time(11, 30)
    is_night = time(21, 0) <= bar_time <= time(23, 0)
    if not (is_morning or is_night):
        return []
    out: list[PatternMatch] = []
    body_ratio = body / bar_range if bar_range > 0 else 0.0
    if (strategy._od_state == "COLLECTING"
            and strategy.opening_rev_enabled
            and strategy._od_bars_collected <= 2
            and strategy._od_bar1_shape):
        if (strategy._od_bar1_shape == "DOWN" and bar.close_price > bar.open_price
                and body_ratio >= strategy.opening_rev_body_ratio
                and bar.close_price > strategy._od_bar1_mid):
            if strategy._opening_rev_allows_entry(1, ctx, atr_5):
                if (str(strategy.opp19_rev_arm_mode).upper() == "FAST_TRACK"
                        or strategy._opening_rev_in_time_window(
                            bar_time, is_morning=is_morning, is_night=is_night)):
                    mode = ("FAST_TRACK" if str(strategy.opp19_rev_arm_mode).upper() == "FAST_TRACK"
                            else "PENDING_CONFIRM")
                    out.append(PatternMatch(
                        "OPP19_5M_OD_REV_LONG", 1,
                        bar.high_price + tick,
                        strategy._cap_long_stop(bar.low_price - stop_buffer, bar.close_price, atr_5),
                        mode,
                    ))
        if (strategy._od_bar1_shape == "UP" and bar.close_price < bar.open_price
                and body_ratio >= strategy.opening_rev_body_ratio
                and bar.close_price < strategy._od_bar1_mid):
            if strategy._opening_rev_allows_entry(-1, ctx, atr_5):
                if (str(strategy.opp19_rev_arm_mode).upper() == "FAST_TRACK"
                        or strategy._opening_rev_in_time_window(
                            bar_time, is_morning=is_morning, is_night=is_night)):
                    mode = ("FAST_TRACK" if str(strategy.opp19_rev_arm_mode).upper() == "FAST_TRACK"
                            else "PENDING_CONFIRM")
                    out.append(PatternMatch(
                        "OPP19_5M_OD_REV_SHORT", -1,
                        bar.low_price - tick,
                        strategy._cap_short_stop(bar.high_price + stop_buffer, bar.close_price, atr_5),
                        mode,
                    ))
    if strategy._od_state == "RANGE_SET":
        if strategy._od_bars_collected > 24:
            return out
        if (strategy.opp19_breakout_r2_gate_enabled
                and strategy._trend_regime_blocks_continuation(strategy.opp19_breakout_r2_min)):
            return out
        if (strategy.opp19_breakout_aff_gate_enabled
                and strategy._aff_alpha_strength < strategy.opp19_breakout_aff_alpha_min):
            return out
        if (bar.close_price > strategy._od_high and bar.close_price > bar.open_price
                and body_ratio >= strategy.opening_drive_min_body and is_strong_bar
                and strategy._opening_drive_breakout_context_ok(1, ctx)):
            out.append(PatternMatch(
                "OPP19_5M_OD_BREAKOUT_LONG", 1,
                bar.high_price + tick,
                strategy._cap_long_stop(bar.low_price - stop_buffer, bar.close_price, atr_5),
                "FAST_TRACK",
            ))
        if (bar.close_price < strategy._od_low and bar.close_price < bar.open_price
                and body_ratio >= strategy.opening_drive_min_body and is_strong_bar
                and strategy._opening_drive_breakout_context_ok(-1, ctx)):
            out.append(PatternMatch(
                "OPP19_5M_OD_BREAKOUT_SHORT", -1,
                bar.low_price - tick,
                strategy._cap_short_stop(bar.high_price + stop_buffer, bar.close_price, atr_5),
                "FAST_TRACK",
            ))
    return out
