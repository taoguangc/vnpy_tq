# -*- coding: utf-8 -*-
"""OPP17 Climax Reversal。"""
from __future__ import annotations


class Opp17Mixin:
    def _process_climax_reversal(
        self, bar, effective_context, atr_5, tick, stop_buffer, bar_range, is_oo,
    ) -> bool:
        if is_oo or bar_range <= tick or atr_5 <= 0:
            return False
        allowed_ctx = {s.strip() for s in self.climax_rev_context.split(",") if s.strip()}
        if effective_context not in allowed_ctx:
            return False
        prev_high = float(self.am_5min.high[-2])
        prev_low = float(self.am_5min.low[-2])
        prev_close = float(self.am_5min.close[-2])
        prev_open = float(self.am_5min.open[-2])
        prev_range = prev_high - prev_low
        if prev_range <= 0 or prev_range <= self.climax_rev_range_atr * atr_5:
            return False
        prev_mid = (prev_high + prev_low) / 2.0
        if prev_close < prev_open and bar.close_price > prev_mid:
            stop = self._cap_long_stop(bar.low_price - stop_buffer, bar.close_price, atr_5)
            self._arm_pending_confirm(
                direction=1, opportunity="OPP17_5M_CLIMAX_REV_LONG",
                trigger=bar.high_price + tick, stop=stop, invalid_line=bar.low_price)
            return True
        if prev_close > prev_open and bar.close_price < prev_mid:
            stop = self._cap_short_stop(bar.high_price + stop_buffer, bar.close_price, atr_5)
            self._arm_pending_confirm(
                direction=-1, opportunity="OPP17_5M_CLIMAX_REV_SHORT",
                trigger=bar.low_price - tick, stop=stop, invalid_line=bar.high_price)
            return True
        return False
