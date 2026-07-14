# -*- coding: utf-8 -*-
"""OPP13 日边界反转（WIDE_RANGE: 日高/日低单触 + 日高双顶）。"""
from __future__ import annotations

from strategies.pa_cta.bar_patterns import BarMetrics, is_quality_day_high_short


class Opp13Mixin:
    def _reset_day_high_test(self) -> None:
        self.day_high_test_state = "IDLE"
        self.day_high_test_bar_count = 0
        self.first_test_high = 0.0

    def _arm_opp13_pending(
        self, bar, *, direction, opportunity, trigger, stop, invalid_line=0.0,
    ) -> None:
        """OPP13 专用 arm：叠加量能筛选后再走 PENDING_CONFIRM。"""
        self._try_production_arm(
            direction=direction,
            opportunity=opportunity,
            trigger=trigger,
            stop=stop,
            invalid_line=invalid_line,
            arm_mode="PENDING_CONFIRM",
            include_opp13_volume=True,
        )

    def _try_day_boundary_reversal(
        self, bar, atr_5, tick, bar_range, upper_shadow, lower_shadow,
        is_boundary_bull, is_boundary_bear, boundary_tol, is_oo,
    ) -> bool:
        if is_oo:
            return False
        # Path A: 日高单触空
        if abs(bar.high_price - self.day_high) <= boundary_tol and is_boundary_bear:
            if (bar.close_price < bar.open_price and upper_shadow >= bar_range * 0.4
                    and not self._pd_blocks_short_target(bar.close_price, atr_5)):
                if (self.always_in == "LONG"
                        and self.market_context not in ("WIDE_RANGE",)):
                    if self.shadow_ledger_enabled:
                        self._shadow_bar_first_attempt = "OPP13_ALWAYS_IN_BLOCK"
                    return True
                if self._late_phase_blocks_entry(
                        -1, self.market_context, "OPP13_5M_RANGE_FAIL_HIGH"):
                    self._late_phase_block_count += 1
                    if self.shadow_ledger_enabled:
                        self._shadow_bar_first_attempt = "OPP13_LATE_PHASE_BLOCK"
                    return True
                bulldozer_pulse = False
                if self.am_5min.count >= 4:
                    p1r = float(self.am_5min.high[-2]) - float(self.am_5min.low[-2])
                    p2r = float(self.am_5min.high[-3]) - float(self.am_5min.low[-3])
                    p1s = (float(self.am_5min.close[-2]) - float(self.am_5min.open[-2])) > p1r * 0.5
                    p2s = (float(self.am_5min.close[-3]) - float(self.am_5min.open[-3])) > p2r * 0.5
                    bulldozer_pulse = p1s and p2s
                if not bulldozer_pulse:
                    self._arm_opp13_pending(
                        bar,
                        direction=-1, opportunity="OPP13_5M_RANGE_FAIL_HIGH",
                        trigger=bar.low_price, stop=bar.high_price + tick,
                        invalid_line=bar.high_price)
                elif self.shadow_ledger_enabled:
                    self._shadow_bar_first_attempt = "OPP13_BULLDOZER_SKIP"
                return True
        # Path A: 日低单触多
        if abs(bar.low_price - self.day_low) <= boundary_tol and is_boundary_bull:
            if (bar.close_price > bar.open_price and lower_shadow >= bar_range * 0.4
                    and not self._pd_blocks_long_target(bar.close_price, atr_5)
                    and self.always_in != "SHORT"):
                if self._late_phase_blocks_entry(
                        1, self.market_context, "OPP13_5M_RANGE_FAIL_LOW"):
                    self._late_phase_block_count += 1
                    if self.shadow_ledger_enabled:
                        self._shadow_bar_first_attempt = "OPP13_LATE_PHASE_BLOCK"
                    return True
                bearish_pulse = False
                if self.am_5min.count >= 4:
                    p1r = float(self.am_5min.high[-2]) - float(self.am_5min.low[-2])
                    p2r = float(self.am_5min.high[-3]) - float(self.am_5min.low[-3])
                    p1b = (float(self.am_5min.open[-2]) - float(self.am_5min.close[-2])) > p1r * 0.5
                    p2b = (float(self.am_5min.open[-3]) - float(self.am_5min.close[-3])) > p2r * 0.5
                    bearish_pulse = p1b and p2b
                if not bearish_pulse:
                    self._arm_opp13_pending(
                        bar,
                        direction=1, opportunity="OPP13_5M_RANGE_FAIL_LOW",
                        trigger=bar.high_price, stop=bar.low_price - tick,
                        invalid_line=bar.low_price)
                elif self.shadow_ledger_enabled:
                    self._shadow_bar_first_attempt = "OPP13_BEARISH_PULSE_SKIP"
                return True
        return False

    def _try_day_high_double_top(
        self, bar, atr_5, tick, bar_range, upper_shadow, is_boundary_bear,
        effective_context, day_high_touch_tol, lh_max_drop,
    ) -> bool:
        if self.day_high_test_state == "FIRST_TEST":
            self.day_high_test_bar_count += 1
            if self.day_high_test_bar_count > self.day_high_second_test_max_bars:
                self._reset_day_high_test()
        # 首次触达日高 → FIRST_TEST
        if (self.day_high_test_state == "IDLE" and self.machine_state == "IDLE"
                and abs(bar.high_price - self.day_high) <= day_high_touch_tol
                and is_quality_day_high_short(
                    BarMetrics.from_bar(bar), bar_range, is_boundary_bear)):
            self.day_high_test_state = "FIRST_TEST"
            self.first_test_high = bar.high_price
            self.day_high_test_bar_count = 0
            if self.shadow_ledger_enabled:
                self._shadow_bar_first_attempt = "OPP13_DAY_HIGH_FIRST_TEST"
            return True
        # 二次测试（LH）+ 质量空棒 → 入场
        if self.day_high_test_state == "FIRST_TEST":
            lh_ok = (self.day_high_test_bar_count <= self.day_high_second_test_max_bars
                     and self.first_test_high > 0
                     and bar.high_price <= self.first_test_high
                     and bar.high_price >= self.first_test_high - lh_max_drop)
            if lh_ok and is_quality_day_high_short(
                    BarMetrics.from_bar(bar), bar_range, is_boundary_bear):
                if effective_context in ("STRONG_BEAR", "BEAR_CHANNEL", "WIDE_RANGE"):
                    if not (self.always_in == "LONG" and effective_context != "WIDE_RANGE"):
                        if not (self.trend_phase == "LATE" and self.trend_direction == -1
                                and effective_context != "WIDE_RANGE"):
                            if not self._pd_blocks_short_target(bar.close_price, atr_5):
                                self._arm_opp13_pending(
                                    bar,
                                    direction=-1, opportunity="OPP13_5M_RANGE_FAIL_HIGH",
                                    trigger=bar.low_price, stop=bar.high_price + tick,
                                    invalid_line=bar.high_price)
                if (self.shadow_ledger_enabled
                        and not getattr(self, "_shadow_bar_first_attempt", "")):
                    self._shadow_bar_first_attempt = "OPP13_DAY_HIGH_SECOND_TEST"
                self._reset_day_high_test()
                return True
        return False
