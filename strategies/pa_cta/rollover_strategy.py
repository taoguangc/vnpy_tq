# -*- coding: utf-8 -*-
"""Brooks PA CTA 换月适配：平旧开新时保留 setup，并平移止损/目标价。"""
from __future__ import annotations

from vnpy.trader.constant import Direction, Offset

from scripts.tq_rollover_data import RolloverEvent
from strategies.pa_cta.strategy import BrooksPaCtaStrategy


class BrooksPaCtaRolloverStrategy(BrooksPaCtaStrategy):
    """TQ 分月 raw + 换月引擎；换月不断 setup，只平移价格刻度。"""

    def on_rollover_adjust(self, event: RolloverEvent) -> None:
        shift = event.price_shift
        if abs(shift) < 1e-9:
            return
        if self.stop_price > 0:
            self.stop_price += shift
        if self.mm_target_price > 0:
            self.mm_target_price += shift
        if self.signal_bar_invalid_line > 0:
            self.signal_bar_invalid_line += shift
        if self.entry_price > 0:
            self.entry_price += shift
        if self.highest_high_since_entry > 0:
            self.highest_high_since_entry += shift
        if self.lowest_low_since_entry > 0:
            self.lowest_low_since_entry += shift

    def on_trade(self, trade) -> None:
        if getattr(self, "_rollover_in_progress", False) and trade.offset in (
            Offset.CLOSE,
            Offset.CLOSETODAY,
        ):
            snap = self._entry_snapshot or {}
            closing_setup = snap.get("setup") or self.active_setup_name or "UNKNOWN"
            entry_px = float(snap.get("entry_price") or self.entry_price or trade.price)
            if trade.direction == Direction.LONG:
                pnl = (entry_px - trade.price) * trade.volume * self.contract_size
            else:
                pnl = (trade.price - entry_px) * trade.volume * self.contract_size
            self._realized_pnl += pnl
            self._setup_pnl[closing_setup] = (
                self._setup_pnl.get(closing_setup, 0.0) + pnl
            )
            self.write_log(
                f"换月平旧 {closing_setup} @ {trade.price:.1f} pnl={pnl:+.0f} "
                f"({trade.datetime.strftime('%Y-%m-%d %H:%M')})"
            )
            self.pending_exit_order = None
            self.remaining_position = int(self.pos)
            return
        super().on_trade(trade)
