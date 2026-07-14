# -*- coding: utf-8 -*-
"""OPP12 超调衰竭（BULL/BEAR_CHANNEL 共用）。"""
from __future__ import annotations


class Opp12Mixin:
    def _try_overshoot_fail(self, bar, atr_5, tick, stop_buffer, bar_range, ema_20,
                            is_bull_reversal, is_bear_reversal, is_oo) -> None:
        if is_oo:
            return
        overshoot_depth = ema_20 - bar.close_price
        if (atr_5 * self.overshoot_atr_mult <= overshoot_depth <= atr_5 * self.overshoot_max_atr_mult
                and is_bull_reversal and bar.close_price > bar.open_price
                and not self._pd_blocks_long_target(bar.close_price, atr_5)):
            self._arm_pending_confirm(
                direction=1, opportunity="OPP12_5M_OVERSHOOT_FAIL_LONG",
                trigger=bar.high_price,
                stop=self._cap_long_stop(bar.low_price - tick, bar.close_price, atr_5),
                invalid_line=bar.low_price)
            return
        if (bar.close_price > ema_20 + atr_5 * self.overshoot_atr_mult
                and is_bear_reversal
                and not self._pd_blocks_short_target(bar.close_price, atr_5)):
            self._arm_pending_confirm(
                direction=-1, opportunity="OPP12_5M_OVERSHOOT_FAIL_SHORT",
                trigger=bar.low_price,
                stop=self._cap_short_stop(bar.high_price + tick, bar.close_price, atr_5),
                invalid_line=bar.high_price)
