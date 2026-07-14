# -*- coding: utf-8 -*-
"""OPP13 区间失败 — 纯检测器（从 shadow_dry_scan._match_opp13 提取）。"""
from __future__ import annotations

from typing import Protocol

from strategies.pa_cta.bar_patterns import BarMetrics, is_quality_day_high_short
from strategies.pa_minimal.detectors.schema import PatternMatch


class _Opp13BoundaryContext(Protocol):
    day_high: float
    day_low: float
    always_in: str
    market_context: str
    am_5min: object

    def _pd_blocks_short_target(self, close: float, atr: float) -> bool: ...
    def _pd_blocks_long_target(self, close: float, atr: float) -> bool: ...
    def _late_phase_blocks_entry(self, direction: int, context: str, setup: str) -> bool: ...


class _Opp13DoubleTopContext(Protocol):
    day_high_test_state: str
    day_high_test_bar_count: int
    day_high_second_test_max_bars: int
    first_test_high: float
    always_in: str
    trend_phase: str
    trend_direction: int

    def _pd_blocks_short_target(self, close: float, atr: float) -> bool: ...


def match_opp13_boundary(
    strategy: _Opp13BoundaryContext,
    bar,
    *,
    atr_5: float,
    tick: float,
    bar_range: float,
    upper_shadow: float,
    lower_shadow: float,
    is_boundary_bull: bool,
    is_boundary_bear: bool,
    boundary_tol: float,
    is_oo: bool,
) -> list[PatternMatch]:
    if is_oo:
        return []
    out: list[PatternMatch] = []
    if abs(bar.high_price - strategy.day_high) <= boundary_tol and is_boundary_bear:
        if (bar.close_price < bar.open_price and upper_shadow >= bar_range * 0.4
                and not strategy._pd_blocks_short_target(bar.close_price, atr_5)):
            if not (strategy.always_in == "LONG"
                    and strategy.market_context not in ("WIDE_RANGE",)):
                if not strategy._late_phase_blocks_entry(
                        -1, strategy.market_context, "OPP13_5M_RANGE_FAIL_HIGH"):
                    bulldozer = False
                    if strategy.am_5min.count >= 4:
                        p1r = float(strategy.am_5min.high[-2]) - float(strategy.am_5min.low[-2])
                        p2r = float(strategy.am_5min.high[-3]) - float(strategy.am_5min.low[-3])
                        p1s = (float(strategy.am_5min.close[-2]) - float(strategy.am_5min.open[-2])) > p1r * 0.5
                        p2s = (float(strategy.am_5min.close[-3]) - float(strategy.am_5min.open[-3])) > p2r * 0.5
                        bulldozer = p1s and p2s
                    if not bulldozer:
                        out.append(PatternMatch(
                            "OPP13_5M_RANGE_FAIL_HIGH", -1,
                            bar.low_price, bar.high_price + tick,
                            "PENDING_CONFIRM", include_opp13_volume=True,
                        ))
    if abs(bar.low_price - strategy.day_low) <= boundary_tol and is_boundary_bull:
        if (bar.close_price > bar.open_price and lower_shadow >= bar_range * 0.4
                and not strategy._pd_blocks_long_target(bar.close_price, atr_5)
                and strategy.always_in != "SHORT"):
            if not strategy._late_phase_blocks_entry(
                    1, strategy.market_context, "OPP13_5M_RANGE_FAIL_LOW"):
                bearish = False
                if strategy.am_5min.count >= 4:
                    p1r = float(strategy.am_5min.high[-2]) - float(strategy.am_5min.low[-2])
                    p2r = float(strategy.am_5min.high[-3]) - float(strategy.am_5min.low[-3])
                    p1b = (float(strategy.am_5min.open[-2]) - float(strategy.am_5min.close[-2])) > p1r * 0.5
                    p2b = (float(strategy.am_5min.open[-3]) - float(strategy.am_5min.close[-3])) > p2r * 0.5
                    bearish = p1b and p2b
                if not bearish:
                    out.append(PatternMatch(
                        "OPP13_5M_RANGE_FAIL_LOW", 1,
                        bar.high_price, bar.low_price - tick,
                        "PENDING_CONFIRM", include_opp13_volume=True,
                    ))
    return out


def match_opp13_double_top(
    strategy: _Opp13DoubleTopContext,
    bar,
    *,
    atr_5: float,
    tick: float,
    bar_range: float,
    is_boundary_bear: bool,
    effective_context: str,
    day_high_touch_tol: float,
    lh_max_drop: float,
) -> list[PatternMatch]:
    """仅二次测试入场条件（不模拟 FIRST_TEST 状态迁移）。"""
    if strategy.day_high_test_state != "FIRST_TEST":
        return []
    lh_ok = (
        strategy.day_high_test_bar_count <= strategy.day_high_second_test_max_bars
        and strategy.first_test_high > 0
        and bar.high_price <= strategy.first_test_high
        and bar.high_price >= strategy.first_test_high - lh_max_drop
    )
    if not (lh_ok and is_quality_day_high_short(
            BarMetrics.from_bar(bar), bar_range, is_boundary_bear)):
        return []
    if effective_context not in ("STRONG_BEAR", "BEAR_CHANNEL", "WIDE_RANGE"):
        return []
    if strategy.always_in == "LONG" and effective_context != "WIDE_RANGE":
        return []
    if (strategy.trend_phase == "LATE" and strategy.trend_direction == -1
            and effective_context != "WIDE_RANGE"):
        return []
    if strategy._pd_blocks_short_target(bar.close_price, atr_5):
        return []
    return [PatternMatch(
        "OPP13_5M_RANGE_FAIL_HIGH", -1,
        bar.low_price, bar.high_price + tick,
        "PENDING_CONFIRM", include_opp13_volume=True,
    )]
