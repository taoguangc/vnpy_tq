# -*- coding: utf-8 -*-
"""OPP08 强突破。"""
from __future__ import annotations


class Opp08Mixin:
    def _process_strong_breakout(
        self, bar, effective_context, atr_5, tick, stop_buffer, bar_range,
        ema_20, prev_high, recent_5bar_low, is_strong_bar, is_oo,
        is_long_climax, is_short_climax,
    ) -> bool:
        if effective_context == "STRONG_BULL":
            if (bar.close_price > ema_20 and is_strong_bar
                    and bar.close_price > bar.open_price
                    and bar.close_price > prev_high and not is_long_climax):
                self._arm_fast_track(
                    direction=1, opportunity="OPP08_5M_STRONG_BREAKOUT_LONG",
                    trigger=bar.high_price + tick,
                    stop=self._cap_long_stop(bar.low_price - stop_buffer, bar.close_price, atr_5),
                )
                return True
        elif effective_context == "STRONG_BEAR":
            if (bar.close_price < ema_20 and is_strong_bar
                    and bar.close_price < bar.open_price):
                self._arm_fast_track(
                    direction=-1, opportunity="OPP08_5M_STRONG_BREAKOUT_SHORT",
                    trigger=bar.low_price - tick,
                    stop=self._cap_short_stop(bar.high_price + stop_buffer, bar.close_price, atr_5),
                )
                return True
        elif effective_context == "BEAR_CHANNEL":
            if (self.machine_state == "IDLE" and not is_oo and is_strong_bar
                    and bar_range > atr_5 * 1.5 and not is_short_climax
                    and bar.close_price < bar.open_price
                    and bar.low_price < recent_5bar_low
                    and bar.close_price < ema_20):
                self._arm_fast_track(
                    direction=-1, opportunity="OPP08_5M_STRONG_BREAKOUT_SHORT",
                    trigger=bar.low_price - tick,
                    stop=self._cap_short_stop(bar.high_price + stop_buffer, bar.close_price, atr_5),
                )
                return True
        return False
