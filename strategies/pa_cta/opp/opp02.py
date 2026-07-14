# -*- coding: utf-8 -*-
"""OPP02 EMA Pullback。"""
from __future__ import annotations


class Opp02Mixin:
    def _process_ema_pullback(
        self, bar, effective_context, atr_5, tick, stop_buffer, bar_range, body, ema_20, is_oo,
    ) -> bool:
        if is_oo or bar_range <= tick or ema_20 <= 0 or atr_5 <= 0:
            return False
        # EXP-007：15m R² 趋势门禁（替代 Setup AFF 时启用）
        if self.opp02_r2_gate_enabled and self._trend_regime_blocks_continuation(self.opp02_r2_min):
            return False
        if self.opp02_aff_gate_enabled and self._aff_alpha_strength < self.opp02_aff_alpha_min:
            return False
        touch_band = atr_5 * self.ema_pullback_touch_atr
        body_ratio = body / bar_range if bar_range > 0 else 0.0
        if self.always_in == "LONG":
            touched_ema = bar.low_price <= ema_20 + touch_band
            sig_long = (bar.close_price > bar.open_price
                        and body_ratio >= self.ema_pullback_min_body_ratio
                        and bar.high_price - max(bar.open_price, bar.close_price) < bar_range * 0.45)
            if touched_ema and sig_long and not self._pd_blocks_long_target(bar.close_price, atr_5):
                stop = self._cap_long_stop(bar.low_price - stop_buffer, bar.close_price, atr_5)
                self._arm_pending_confirm(
                    direction=1, opportunity="OPP02_5M_EMA_PULLBACK_LONG",
                    trigger=bar.high_price + tick, stop=stop, invalid_line=bar.low_price)
                return True
        if self.always_in == "SHORT":
            touched_ema = bar.high_price >= ema_20 - touch_band
            sig_short = (bar.close_price < bar.open_price
                         and body_ratio >= self.ema_pullback_min_body_ratio
                         and min(bar.open_price, bar.close_price) - bar.low_price < bar_range * 0.45)
            if touched_ema and sig_short and not self._pd_blocks_short_target(bar.close_price, atr_5):
                stop = self._cap_short_stop(bar.high_price + stop_buffer, bar.close_price, atr_5)
                self._arm_pending_confirm(
                    direction=-1, opportunity="OPP02_5M_EMA_PULLBACK_SHORT",
                    trigger=bar.low_price - tick, stop=stop, invalid_line=bar.high_price)
                return True
        return False
