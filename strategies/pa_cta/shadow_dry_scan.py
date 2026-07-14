# -*- coding: utf-8 -*-
"""Phase-2.1：production OPP dry-scan（只读 pattern 匹配，不改交易状态）。"""
from __future__ import annotations

from dataclasses import dataclass

from strategies.pa_cta.bar_patterns import (
    BarMetrics,
    is_quality_day_high_short,
)


@dataclass(frozen=True)
class PatternMatch:
    setup: str
    direction: int
    trigger: float
    stop: float
    arm_mode: str
    include_opp13_volume: bool = False
    is_direct: bool = False


def collect_production_matches(
    strategy,
    bar,
    *,
    effective_context: str,
    atr_5: float,
    tick: float,
    stop_buffer: float,
    ema_20: float,
    bar_range: float,
    body: float,
    prev_high: float,
    recent_5bar_low: float,
    is_strong_bar: bool,
    is_bull_reversal: bool,
    is_bear_reversal: bool,
    is_boundary_bull: bool,
    is_boundary_bear: bool,
    is_oo: bool,
    is_long_climax: bool,
    is_short_climax: bool,
    boundary_tol: float,
    day_high_touch_tol: float,
    lh_max_drop: float,
    upper_shadow: float,
    lower_shadow: float,
) -> list[PatternMatch]:
    """按 production 路由顺序收集本 bar 所有 pattern 命中（只读，无副作用）。"""
    matches: list[PatternMatch] = []
    matches.extend(
        _match_opp15_trigger(strategy, bar, atr_5, tick, is_strong_bar=is_strong_bar)
    )
    matches.extend(
        _match_opp08(
            strategy, bar, effective_context, atr_5, tick, stop_buffer,
            ema_20, prev_high, recent_5bar_low, is_strong_bar, is_oo,
            is_long_climax, is_short_climax, bar_range,
        )
    )
    if effective_context in ("BULL_CHANNEL", "BEAR_CHANNEL"):
        matches.extend(
            _match_opp12(
                strategy, bar, atr_5, tick, ema_20,
                is_bull_reversal, is_bear_reversal, is_oo,
            )
        )
    if effective_context == "WIDE_RANGE":
        matches.extend(
            _match_opp13_boundary(
                strategy, bar, atr_5, tick, bar_range, upper_shadow, lower_shadow,
                is_boundary_bull, is_boundary_bear, boundary_tol, is_oo,
            )
        )
        matches.extend(
            _match_opp13_double_top(
                strategy, bar, atr_5, tick, bar_range, is_boundary_bear,
                effective_context, day_high_touch_tol, lh_max_drop,
            )
        )
    if strategy.two_bar_rev_enabled:
        matches.extend(
            _match_opp16(strategy, bar, effective_context, atr_5, tick, stop_buffer, bar_range)
        )
    if strategy.ema_pullback_enabled:
        matches.extend(
            _match_opp02(
                strategy, bar, atr_5, tick, stop_buffer, bar_range, body, ema_20, is_oo,
            )
        )
    if strategy.climax_rev_enabled:
        matches.extend(
            _match_opp17(strategy, bar, effective_context, atr_5, tick, stop_buffer, bar_range, is_oo)
        )
    if strategy.opening_drive_enabled:
        matches.extend(
            _match_opp19(
                strategy, bar, effective_context, atr_5, tick, stop_buffer,
                bar_range, body, is_strong_bar, is_oo,
            )
        )
    return matches


def _match_opp08(
    strategy, bar, ctx, atr_5, tick, stop_buffer, ema_20, prev_high,
    recent_5bar_low, is_strong_bar, is_oo, is_long_climax, is_short_climax, bar_range,
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


def _match_opp12(
    strategy, bar, atr_5, tick, ema_20, is_bull_reversal, is_bear_reversal, is_oo,
) -> list[PatternMatch]:
    if is_oo:
        return []
    out: list[PatternMatch] = []
    overshoot_depth = ema_20 - bar.close_price
    if (atr_5 * strategy.overshoot_atr_mult <= overshoot_depth
            <= atr_5 * strategy.overshoot_max_atr_mult
            and is_bull_reversal and bar.close_price > bar.open_price
            and not strategy._pd_blocks_long_target(bar.close_price, atr_5)):
        out.append(PatternMatch(
            "OPP12_5M_OVERSHOOT_FAIL_LONG", 1,
            bar.high_price,
            strategy._cap_long_stop(bar.low_price - tick, bar.close_price, atr_5),
            "PENDING_CONFIRM",
        ))
    if (bar.close_price > ema_20 + atr_5 * strategy.overshoot_atr_mult
            and is_bear_reversal
            and not strategy._pd_blocks_short_target(bar.close_price, atr_5)):
        out.append(PatternMatch(
            "OPP12_5M_OVERSHOOT_FAIL_SHORT", -1,
            bar.low_price,
            strategy._cap_short_stop(bar.high_price + tick, bar.close_price, atr_5),
            "PENDING_CONFIRM",
        ))
    return out


def _match_opp13_boundary(
    strategy, bar, atr_5, tick, bar_range, upper_shadow, lower_shadow,
    is_boundary_bull, is_boundary_bear, boundary_tol, is_oo,
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


def _match_opp13_double_top(
    strategy, bar, atr_5, tick, bar_range, is_boundary_bear,
    effective_context, day_high_touch_tol, lh_max_drop,
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


def _match_opp16(strategy, bar, ctx, atr_5, tick, stop_buffer, bar_range) -> list[PatternMatch]:
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
    prev_shape = strategy.prev_bar_shape or ""
    is_strong = (
        prev_body_ratio >= strategy.two_bar_rev_body_ratio
        and prev_shape in ("UP_TREND", "DOWN_TREND", "OUTSIDE_UP", "OUTSIDE_DOWN"))
    if not is_strong and prev_body_ratio < strategy.two_bar_rev_body_ratio:
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


def _match_opp02(strategy, bar, atr_5, tick, stop_buffer, bar_range, body, ema_20, is_oo) -> list[PatternMatch]:
    if is_oo or bar_range <= tick or ema_20 <= 0 or atr_5 <= 0:
        return []
    if strategy.opp02_r2_gate_enabled and strategy._trend_regime_blocks_continuation(strategy.opp02_r2_min):
        return []
    if strategy.opp02_aff_gate_enabled and strategy._aff_alpha_strength < strategy.opp02_aff_alpha_min:
        return []
    touch_band = atr_5 * strategy.ema_pullback_touch_atr
    body_ratio = body / bar_range if bar_range > 0 else 0.0
    out: list[PatternMatch] = []
    if strategy.always_in == "LONG":
        touched = bar.low_price <= ema_20 + touch_band
        sig = (bar.close_price > bar.open_price
               and body_ratio >= strategy.ema_pullback_min_body_ratio
               and bar.high_price - max(bar.open_price, bar.close_price) < bar_range * 0.45)
        if touched and sig and not strategy._pd_blocks_long_target(bar.close_price, atr_5):
            out.append(PatternMatch(
                "OPP02_5M_EMA_PULLBACK_LONG", 1,
                bar.high_price + tick,
                strategy._cap_long_stop(bar.low_price - stop_buffer, bar.close_price, atr_5),
                "PENDING_CONFIRM",
            ))
    if strategy.always_in == "SHORT":
        touched = bar.high_price >= ema_20 - touch_band
        sig = (bar.close_price < bar.open_price
               and body_ratio >= strategy.ema_pullback_min_body_ratio
               and min(bar.open_price, bar.close_price) - bar.low_price < bar_range * 0.45)
        if touched and sig and not strategy._pd_blocks_short_target(bar.close_price, atr_5):
            out.append(PatternMatch(
                "OPP02_5M_EMA_PULLBACK_SHORT", -1,
                bar.low_price - tick,
                strategy._cap_short_stop(bar.high_price + stop_buffer, bar.close_price, atr_5),
                "PENDING_CONFIRM",
            ))
    return out


def _match_opp17(strategy, bar, ctx, atr_5, tick, stop_buffer, bar_range, is_oo) -> list[PatternMatch]:
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


def _match_opp19(
    strategy, bar, ctx, atr_5, tick, stop_buffer, bar_range, body, is_strong_bar, is_oo,
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


def _match_opp15_trigger(strategy, bar, atr_5, tick, *, is_strong_bar) -> list[PatternMatch]:
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
