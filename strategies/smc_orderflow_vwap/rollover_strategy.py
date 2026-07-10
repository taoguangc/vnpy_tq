"""SMC-OrderFlow-VWAP 换月适配：平旧开新时平移价格刻度并重挂止损。"""
from __future__ import annotations

from vnpy.trader.constant import Direction, Offset

from scripts.tq_rollover_data import RolloverEvent
from strategies.smc_orderflow_vwap.smc_orderflow_vwap_strategy import SmcOrderFlowVwapStrategy


class SmcOrderFlowVwapRolloverStrategy(SmcOrderFlowVwapStrategy):
    """TQ 分月 raw + 换月引擎；换月时平移 OB/入场/止损价格刻度。"""

    def on_rollover_adjust(self, event: RolloverEvent) -> None:
        shift = event.price_shift
        if abs(shift) < 1e-9:
            return

        if self.order_block_low > 0:
            self.order_block_low += shift
        if self.order_block_high > 0:
            self.order_block_high += shift
        if self.entry_price > 0:
            self.entry_price += shift
        if self._pending_stop_price > 0:
            self._pending_stop_price += shift
        if self._structural_stop_price > 0:
            self._structural_stop_price += shift

        self._cancel_active_stop_orders()
        if self.pos > 0 and self._structural_stop_price > 0:
            stop_price = self._structural_stop_price
            if self.entry_price > stop_price + self.min_risk_ticks:
                order_ids = self.sell(stop_price, abs(self.pos), stop=True)
                self.active_stop_order_ids.extend(order_ids)
                self.write_log(
                    f"【换月】价格刻度平移 {shift:+.1f}，"
                    f"重挂结构止损 {stop_price:.1f}"
                )

    def on_trade(self, trade) -> None:
        if getattr(self, "_rollover_in_progress", False):
            if trade.offset in (Offset.CLOSE, Offset.CLOSETODAY):
                self.write_log(
                    f"换月平旧 @ {trade.price:.1f} "
                    f"({trade.datetime.strftime('%Y-%m-%d %H:%M')})"
                )
                return
            if trade.offset == Offset.OPEN:
                self.write_log(
                    f"换月开新 @ {trade.price:.1f} "
                    f"({trade.datetime.strftime('%Y-%m-%d %H:%M')})"
                )
                return
        super().on_trade(trade)
