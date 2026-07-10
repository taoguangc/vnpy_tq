"""Brooks Scalp v0.1 — 1m First Pullback + Stop Entry + 1R + 时间止损。

FSM: IDLE → WAIT_PULLBACK → PULLBACK → (Stop Entry) → 持仓管理。
纯 1 分钟回测：无 BarGenerator，信号与风控均在 on_bar。
"""
from __future__ import annotations

from enum import Enum

from vnpy.trader.constant import Direction, Offset
from vnpy_ctastrategy import (
    ArrayManager,
    BarData,
    CtaTemplate,
    StopOrder,
    TradeData,
)


class State(Enum):
    IDLE = 0
    WAIT_PULLBACK = 1
    PULLBACK = 2


class BrooksScalpV01(CtaTemplate):
    """Brooks 机械 First Pullback  scalp 骨架（v0.1，供迭代至 v0.2+）。"""

    author = "vnpy_tq"

    ema_period = 20
    atr_period = 20
    trend_leg_atr = 1.0
    pullback_atr = 0.2
    risk_reward = 1.0
    max_hold_bars = 10
    fixed_size = 1

    parameters = [
        "ema_period",
        "atr_period",
        "trend_leg_atr",
        "pullback_atr",
        "risk_reward",
        "max_hold_bars",
        "fixed_size",
    ]

    ema20 = 0.0
    atr20 = 0.0
    state = State.IDLE.value
    trend = 0
    hold_bars = 0

    variables = [
        "ema20",
        "atr20",
        "state",
        "trend",
        "hold_bars",
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.am = ArrayManager(200)

        self.pullback_low = 0.0
        self.pullback_high = 0.0
        self.entry_price = 0.0
        self.stop_price = 0.0
        self.target_price = 0.0

        self._entry_dt = None
        self._entry_side = 0
        self._entry_fill = 0.0
        self._trip_mfe = 0.0
        self._trip_mae = 0.0
        self._trade_log: list[dict] = []

    def on_init(self) -> None:
        self.write_log("BrooksScalpV01 initialized")
        self.load_bar(30)

    def on_start(self) -> None:
        self.write_log("BrooksScalpV01 started")

    def on_stop(self) -> None:
        self.write_log(
            f"BrooksScalpV01 stopped | closed_trades={len(self._trade_log)}"
        )

    def on_bar(self, bar: BarData) -> None:
        self.cancel_all()

        self.am.update_bar(bar)
        if not self.am.inited:
            return

        self._update_indicators()

        if self.pos == 0:
            self.detect_setup(bar)
        else:
            self.manage_position(bar)

        self.put_event()

    def _update_indicators(self) -> None:
        self.ema20 = self.am.ema(self.ema_period)
        self.atr20 = self.am.atr(self.atr_period)

    def detect_setup(self, bar: BarData) -> None:
        self._detect_trend()

        if self.trend == 0:
            self.state = State.IDLE.value
            return

        if self.state == State.IDLE.value:
            if self._check_trend_leg():
                self.state = State.WAIT_PULLBACK.value

        elif self.state == State.WAIT_PULLBACK.value:
            if self._check_pullback():
                self.state = State.PULLBACK.value
                self.pullback_low = self.am.low[-1]
                self.pullback_high = self.am.high[-1]

        elif self.state == State.PULLBACK.value:
            if self.trend == 1:
                self.pullback_low = min(self.pullback_low, self.am.low[-1])
                if self._bull_signal():
                    self._send_long_stop_entry(bar)
                    self.state = State.IDLE.value
            elif self.trend == -1:
                self.pullback_high = max(self.pullback_high, self.am.high[-1])
                if self._bear_signal():
                    self._send_short_stop_entry(bar)
                    self.state = State.IDLE.value

    def _detect_trend(self) -> None:
        close = self.am.close
        ema_array = self.am.ema(self.ema_period, array=True)
        ema_now = ema_array[-1]
        ema_prev = ema_array[-6]

        bull_bars = sum(close[-5:] > ema_array[-5:])
        bear_bars = sum(close[-5:] < ema_array[-5:])

        if close[-1] > ema_now and ema_now > ema_prev and bull_bars >= 4:
            self.trend = 1
        elif close[-1] < ema_now and ema_now < ema_prev and bear_bars >= 4:
            self.trend = -1
        else:
            self.trend = 0

    def _check_trend_leg(self) -> bool:
        move = abs(self.am.close[-1] - self.am.close[-6])
        return move > self.atr20 * self.trend_leg_atr

    def _check_pullback(self) -> bool:
        if self.trend == 1:
            distance = abs(self.am.low[-1] - self.ema20)
        else:
            distance = abs(self.am.high[-1] - self.ema20)
        return distance < self.atr20 * self.pullback_atr

    def _bull_signal(self) -> bool:
        high = self.am.high[-1]
        low = self.am.low[-1]
        close = self.am.close[-1]
        open_ = self.am.open[-1]
        if high == low:
            return False
        body_ratio = abs(close - open_) / (high - low)
        return close > open_ and close > self.am.high[-2] and body_ratio > 0.4

    def _bear_signal(self) -> bool:
        high = self.am.high[-1]
        low = self.am.low[-1]
        close = self.am.close[-1]
        open_ = self.am.open[-1]
        if high == low:
            return False
        body_ratio = abs(close - open_) / (high - low)
        return close < open_ and close < self.am.low[-2] and body_ratio > 0.4

    def _send_long_stop_entry(self, bar: BarData) -> None:
        tick = self.pricetick or 1.0
        self.entry_price = bar.high_price + tick
        self.stop_price = self.pullback_low - tick
        risk = self.entry_price - self.stop_price
        if risk <= tick:
            return
        self.target_price = self.entry_price + risk * self.risk_reward
        self.buy(self.entry_price, self.fixed_size, stop=True)

    def _send_short_stop_entry(self, bar: BarData) -> None:
        tick = self.pricetick or 1.0
        self.entry_price = bar.low_price - tick
        self.stop_price = self.pullback_high + tick
        risk = self.stop_price - self.entry_price
        if risk <= tick:
            return
        self.target_price = self.entry_price - risk * self.risk_reward
        self.short(self.entry_price, self.fixed_size, stop=True)

    def manage_position(self, bar: BarData) -> None:
        self.hold_bars += 1
        self._update_excursion(bar)

        if self.pos > 0:
            if self._check_long_stop(bar):
                return
            if self._check_long_target(bar):
                return
        elif self.pos < 0:
            if self._check_short_stop(bar):
                return
            if self._check_short_target(bar):
                return

        if self.hold_bars >= self.max_hold_bars:
            self._close_at_market(bar, "TIME_STOP")

    def _update_excursion(self, bar: BarData) -> None:
        if self._entry_fill <= 0:
            return
        if self.pos > 0:
            self._trip_mfe = max(self._trip_mfe, bar.high_price - self._entry_fill)
            self._trip_mae = max(self._trip_mae, self._entry_fill - bar.low_price)
        elif self.pos < 0:
            self._trip_mfe = max(self._trip_mfe, self._entry_fill - bar.low_price)
            self._trip_mae = max(self._trip_mae, bar.high_price - self._entry_fill)

    def _check_long_stop(self, bar: BarData) -> bool:
        if bar.low_price > self.stop_price:
            return False
        fill = min(bar.open_price, self.stop_price)
        self.sell(fill, abs(self.pos))
        self._record_exit(bar, "STOP")
        return True

    def _check_long_target(self, bar: BarData) -> bool:
        if bar.high_price < self.target_price:
            return False
        fill = max(bar.open_price, self.target_price)
        self.sell(fill, abs(self.pos))
        self._record_exit(bar, "TARGET")
        return True

    def _check_short_stop(self, bar: BarData) -> bool:
        if bar.high_price < self.stop_price:
            return False
        fill = max(bar.open_price, self.stop_price)
        self.cover(fill, abs(self.pos))
        self._record_exit(bar, "STOP")
        return True

    def _check_short_target(self, bar: BarData) -> bool:
        if bar.low_price > self.target_price:
            return False
        fill = min(bar.open_price, self.target_price)
        self.cover(fill, abs(self.pos))
        self._record_exit(bar, "TARGET")
        return True

    def _close_at_market(self, bar: BarData, reason: str) -> None:
        if self.pos > 0:
            self.sell(bar.close_price, abs(self.pos))
        elif self.pos < 0:
            self.cover(bar.close_price, abs(self.pos))
        self._record_exit(bar, reason)

    def _record_exit(self, bar: BarData, reason: str) -> None:
        tick = self.pricetick or 1.0
        holding_min = 0.0
        if self._entry_dt is not None:
            holding_min = (bar.datetime - self._entry_dt).total_seconds() / 60.0
        self._trade_log.append(
            {
                "direction": "多" if self._entry_side > 0 else "空",
                "entry_time": self._entry_dt,
                "exit_time": bar.datetime,
                "exit_reason": reason,
                "mfe_ticks": self._trip_mfe / tick if tick > 0 else 0.0,
                "mae_ticks": self._trip_mae / tick if tick > 0 else 0.0,
                "holding_minutes": holding_min,
            }
        )
        self.hold_bars = 0
        self._entry_side = 0
        self._entry_dt = None
        self._entry_fill = 0.0
        self._trip_mfe = 0.0
        self._trip_mae = 0.0

    def on_trade(self, trade: TradeData) -> None:
        if trade.offset == Offset.OPEN:
            self.hold_bars = 0
            self._entry_side = 1 if trade.direction == Direction.LONG else -1
            self._entry_dt = trade.datetime
            self._entry_fill = trade.price
            self._trip_mfe = 0.0
            self._trip_mae = 0.0
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder) -> None:
        pass
