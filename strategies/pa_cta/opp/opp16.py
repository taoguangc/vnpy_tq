# -*- coding: utf-8 -*-
"""OPP16 Two-Bar Reversal。"""
from __future__ import annotations


class Opp16Mixin:
    def _process_two_bar_reversal(
        self, bar, effective_context, atr_5, tick, stop_buffer, bar_range, body,
    ) -> bool:
        if bar_range <= tick or self.am_5min.count < 2:
            return False
        allowed_ctx = {s.strip() for s in self.two_bar_rev_context.split(",") if s.strip()}
        if effective_context not in allowed_ctx:
            return False
        prev_close = float(self.am_5min.close[-2])
        prev_open = float(self.am_5min.open[-2])
        prev_high = float(self.am_5min.high[-2])
        prev_low = float(self.am_5min.low[-2])
        prev_range = prev_high - prev_low
        if prev_range <= 0:
            return False
        prev_body_ratio = abs(prev_close - prev_open) / prev_range
        prev_mid = (prev_high + prev_low) / 2.0
        prev_shape = self.prev_bar_shape or ""
        is_strong_trend_bar = (
            prev_body_ratio >= self.two_bar_rev_body_ratio
            and prev_shape in ("UP_TREND", "DOWN_TREND", "OUTSIDE_UP", "OUTSIDE_DOWN"))
        if not is_strong_trend_bar and prev_body_ratio < self.two_bar_rev_body_ratio:
            return False
        # A: 空头趋势棒 → 后棒越过中点向上 → 做多
        if prev_close < prev_open and bar.close_price > prev_mid:
            stop = self._cap_long_stop(bar.low_price - stop_buffer, bar.close_price, atr_5)
            self._arm_pending_confirm(
                direction=1, opportunity="OPP16_5M_TWO_BAR_REV_LONG",
                trigger=bar.high_price + tick, stop=stop, invalid_line=bar.low_price)
            return True
        # B: 多头趋势棒 → 后棒越过中点向下 → 做空
        if prev_close > prev_open and bar.close_price < prev_mid:
            stop = self._cap_short_stop(bar.high_price + stop_buffer, bar.close_price, atr_5)
            self._arm_pending_confirm(
                direction=-1, opportunity="OPP16_5M_TWO_BAR_REV_SHORT",
                trigger=bar.low_price - tick, stop=stop, invalid_line=bar.high_price)
            return True
        return False
