# -*- coding: utf-8 -*-
"""OPP19 Opening Drive。"""
from __future__ import annotations

from datetime import time


class Opp19Mixin:
    def _reset_opening_drive(self) -> None:
        self._od_state = "IDLE"
        self._od_high = 0.0
        self._od_low = 0.0
        self._od_bars_collected = 0
        self._od_session_date = None
        self._od_bar1_shape = ""
        self._od_bar1_mid = 0.0
        self._od_bar1_range = 0.0

    def _opening_drive_breakout_context_ok(
        self, direction: int, effective_context: str
    ) -> bool:
        """OPP19 BREAKOUT context 软禁：逆强势背景不做开盘区间突破。"""
        if direction > 0 and effective_context == "STRONG_BEAR":
            return False
        if direction < 0 and effective_context == "STRONG_BULL":
            return False
        return True

    def _opening_rev_allows_entry(
        self, direction: int, effective_context: str, atr_5: float,
    ) -> bool:
        """OPP19 OD_REV：过滤逆势 always_in、强趋势反向 fade、首棒振幅异常。"""
        if not self.opp19_rev_gate_enabled:
            return True
        if direction > 0:
            if self.opp19_rev_always_in_gate and self.always_in == "SHORT":
                return False
            if (self.opp19_rev_block_strong_counter
                    and effective_context == "STRONG_BEAR"):
                return False
        elif direction < 0:
            if self.opp19_rev_always_in_gate and self.always_in == "LONG":
                return False
            if (self.opp19_rev_block_strong_counter
                    and effective_context == "STRONG_BULL"):
                return False
        if self._od_bar1_range > 0 and atr_5 > 0:
            bar1_atr = self._od_bar1_range / atr_5
            if bar1_atr < self.opp19_rev_min_bar1_range_atr:
                return False
            if bar1_atr > self.opp19_rev_max_bar1_range_atr:
                return False
        allowed = {
            s.strip()
            for s in str(self.opp19_rev_contexts or "").split(",")
            if s.strip()
        }
        if allowed and effective_context not in allowed:
            return False
        return True

    def _opening_rev_in_time_window(
        self, bar_time: time, *, is_morning: bool, is_night: bool,
    ) -> bool:
        """开盘反转仅在 session 前 N 分钟内 arm（防 FAST_TRACK 止损单迟填）。"""
        if is_morning:
            return bar_time <= time(9, int(self.opp19_rev_morning_cutoff_minute))
        if is_night:
            return bar_time <= time(21, int(self.opp19_rev_night_cutoff_minute))
        return False

    def _arm_opening_rev(
        self, bar, *, direction: int, opportunity: str, atr_5: float,
        tick: float, stop_buffer: float, effective_context: str,
    ) -> bool:
        """OD_REV：PENDING_CONFIRM + 门禁 + 时间窗（替代 FAST_TRACK 迟填）。"""
        bar_time = bar.datetime.time()
        is_morning = time(9, 0) <= bar_time <= time(11, 30)
        is_night = time(21, 0) <= bar_time <= time(23, 0)
        if str(self.opp19_rev_arm_mode).upper() != "FAST_TRACK":
            if not self._opening_rev_in_time_window(
                    bar_time, is_morning=is_morning, is_night=is_night):
                return False
        if not self._opening_rev_allows_entry(direction, effective_context, atr_5):
            return False
        if str(self.opp19_rev_arm_mode).upper() == "FAST_TRACK":
            if direction > 0:
                stop = self._cap_long_stop(
                    bar.low_price - stop_buffer, bar.close_price, atr_5)
                self._arm_fast_track(
                    direction=1, opportunity=opportunity,
                    trigger=bar.high_price + tick, stop=stop,
                    invalid_line=bar.low_price)
            else:
                stop = self._cap_short_stop(
                    bar.high_price + stop_buffer, bar.close_price, atr_5)
                self._arm_fast_track(
                    direction=-1, opportunity=opportunity,
                    trigger=bar.low_price - tick, stop=stop,
                    invalid_line=bar.high_price)
        else:
            if direction > 0:
                stop = self._cap_long_stop(
                    bar.low_price - stop_buffer, bar.close_price, atr_5)
                self._arm_pending_confirm(
                    direction=1, opportunity=opportunity,
                    trigger=bar.high_price + tick, stop=stop,
                    invalid_line=bar.low_price)
            else:
                stop = self._cap_short_stop(
                    bar.high_price + stop_buffer, bar.close_price, atr_5)
                self._arm_pending_confirm(
                    direction=-1, opportunity=opportunity,
                    trigger=bar.low_price - tick, stop=stop,
                    invalid_line=bar.high_price)
        self._reset_opening_drive()
        return True

    def _process_opening_drive(
        self, bar, effective_context, atr_5, tick, stop_buffer, bar_range, body,
        is_strong_bar, is_oo,
    ) -> bool:
        if is_oo or bar_range <= tick or atr_5 <= 0:
            return False
        bar_time = bar.datetime.time()
        bar_date = bar.datetime.date()
        is_morning = time(9, 0) <= bar_time <= time(11, 30)
        is_night = time(21, 0) <= bar_time <= time(23, 0)
        if not (is_morning or is_night):
            if self._od_state != "IDLE":
                self._reset_opening_drive()
            return False
        session_changed = bar_date != self._od_session_date
        new_morning = is_morning and bar_time < time(9, 20) and self._od_state == "IDLE"
        new_night = is_night and bar_time < time(21, 20) and self._od_state == "IDLE"
        if session_changed or new_morning or new_night:
            self._reset_opening_drive()
            self._od_state = "COLLECTING"
            self._od_session_date = bar_date
            self._od_high = bar.high_price
            self._od_low = bar.low_price
            self._od_bars_collected = 1
            if self.opening_rev_enabled and bar_range > 0:
                if body / bar_range >= self.opening_rev_body_ratio:
                    if bar.close_price > bar.open_price:
                        self._od_bar1_shape = "UP"
                    elif bar.close_price < bar.open_price:
                        self._od_bar1_shape = "DOWN"
                    if self._od_bar1_shape:
                        self._od_bar1_mid = (bar.high_price + bar.low_price) / 2.0
                        self._od_bar1_range = bar_range
            return False
        if self._od_state == "IDLE":
            return False
        # COLLECTING
        if self._od_state == "COLLECTING":
            # Path B: Opening Reversal
            if (self.opening_rev_enabled and self.machine_state == "IDLE"
                    and self._od_bars_collected <= 2 and self._od_bar1_shape):
                body_ratio = body / bar_range if bar_range > 0 else 0.0
                if (self._od_bar1_shape == "DOWN" and bar.close_price > bar.open_price
                        and body_ratio >= self.opening_rev_body_ratio
                        and bar.close_price > self._od_bar1_mid):
                    if self._arm_opening_rev(
                            bar, direction=1,
                            opportunity="OPP19_5M_OD_REV_LONG",
                            atr_5=atr_5, tick=tick, stop_buffer=stop_buffer,
                            effective_context=effective_context):
                        return True
                if (self._od_bar1_shape == "UP" and bar.close_price < bar.open_price
                        and body_ratio >= self.opening_rev_body_ratio
                        and bar.close_price < self._od_bar1_mid):
                    if self._arm_opening_rev(
                            bar, direction=-1,
                            opportunity="OPP19_5M_OD_REV_SHORT",
                            atr_5=atr_5, tick=tick, stop_buffer=stop_buffer,
                            effective_context=effective_context):
                        return True
            # Path A: Range collection
            self._od_high = max(self._od_high, bar.high_price)
            self._od_low = min(self._od_low, bar.low_price)
            self._od_bars_collected += 1
            if self._od_bars_collected >= self.opening_drive_bars:
                if self._od_high - self._od_low >= atr_5 * self.opening_drive_range_atr_min:
                    self._od_state = "RANGE_SET"
                else:
                    self._reset_opening_drive()
            return False
        # RANGE_SET
        if self._od_state == "RANGE_SET":
            self._od_bars_collected += 1
            if self._od_bars_collected > 24:
                self._reset_opening_drive()
                return False
            body_ratio = body / bar_range if bar_range > 0 else 0.0
            # EXP-007：OPP19 突破 R² 门禁（替代 Setup AFF 时启用）
            if (self.opp19_breakout_r2_gate_enabled
                    and self._trend_regime_blocks_continuation(self.opp19_breakout_r2_min)):
                return False
            if (self.opp19_breakout_aff_gate_enabled
                    and self._aff_alpha_strength < self.opp19_breakout_aff_alpha_min):
                return False
            if (bar.close_price > self._od_high and bar.close_price > bar.open_price
                    and body_ratio >= self.opening_drive_min_body and is_strong_bar):
                if self._opening_drive_breakout_context_ok(1, effective_context):
                    self._arm_fast_track(
                        direction=1, opportunity="OPP19_5M_OD_BREAKOUT_LONG",
                        trigger=bar.high_price + tick,
                        stop=self._cap_long_stop(bar.low_price - stop_buffer, bar.close_price, atr_5))
                    self._reset_opening_drive()
                    return True
            if (bar.close_price < self._od_low and bar.close_price < bar.open_price
                    and body_ratio >= self.opening_drive_min_body and is_strong_bar):
                if self._opening_drive_breakout_context_ok(-1, effective_context):
                    self._arm_fast_track(
                        direction=-1, opportunity="OPP19_5M_OD_BREAKOUT_SHORT",
                        trigger=bar.low_price - tick,
                        stop=self._cap_short_stop(bar.high_price + stop_buffer, bar.close_price, atr_5))
                    self._reset_opening_drive()
                    return True
        return False
