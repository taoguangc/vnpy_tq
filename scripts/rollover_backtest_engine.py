"""换月回测引擎：切点主动平旧开新，成本进成交记录。"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date as Date, datetime
from typing import TYPE_CHECKING

import pandas as pd
from vnpy.trader.constant import Direction, Offset
from vnpy.trader.object import BarData, TradeData
from vnpy.trader.utility import round_to
from vnpy_ctastrategy.backtesting import BacktestingEngine, DailyResult

from scripts.tq_rollover_data import RolloverEvent

if TYPE_CHECKING:
    from vnpy_ctastrategy import CtaTemplate

ROLLOVER_GATEWAY = "ROLLOVER"


@dataclass
class RolloverSimStats:
    """换月模拟统计。"""

    count: int = 0
    contracts_rolled: int = 0
    total_gap_pnl: float = 0.0
    total_rollover_slippage: float = 0.0
    total_rollover_commission: float = 0.0
    events: list[dict] = field(default_factory=list)
    missed_switches: list[dict] = field(default_factory=list)
    holiday_gap_events: list[dict] = field(default_factory=list)


class RolloverBacktestingEngine(BacktestingEngine):
    """在 ``new_bar`` 前检测换月切点，有持仓则按旧/新合约盘口价平旧开新。"""

    def __init__(self) -> None:
        super().__init__()
        self.rollover_events: dict[datetime, RolloverEvent] = {}
        self._rollover_by_pair: dict[tuple[str, str], RolloverEvent] = {}
        self.rollover_stats = RolloverSimStats()
        self._prev_yymm: str | None = None
        self._warned_no_adjust_hook = False
        self._rollover_cost_by_date: dict[Date, tuple[float, float]] = {}

    def clear_data(self) -> None:
        """重置引擎数据；同时清空换月自身状态，避免复用实例跨轮串数据。"""
        super().clear_data()
        self.rollover_stats = RolloverSimStats()
        self._prev_yymm = None
        self._warned_no_adjust_hook = False
        self._rollover_cost_by_date = {}

    def set_rollover_events(self, events: list[RolloverEvent]) -> None:
        self.rollover_events = {e.switch_time: e for e in events}
        self._rollover_by_pair = {(e.from_yymm, e.to_yymm): e for e in events}

    def new_bar(self, bar: BarData) -> None:
        yymm = getattr(bar, "yymm", None)
        if (
            self._prev_yymm
            and yymm
            and yymm != self._prev_yymm
        ):
            if abs(getattr(self.strategy, "pos", 0)) > 1e-9:
                event = self.rollover_events.get(bar.datetime)
                if event is not None:
                    self._execute_rollover(event)
                else:
                    fallback = self._rollover_by_pair.get((self._prev_yymm, yymm))
                    if fallback is not None:
                        gap_days = (bar.datetime.date() - fallback.switch_time.date()).days
                        self.rollover_stats.holiday_gap_events.append(
                            {
                                "from": self._prev_yymm,
                                "to": yymm,
                                "planned_switch": fallback.switch_time.isoformat(),
                                "actual_switch": bar.datetime.isoformat(),
                                "gap_days": gap_days,
                            }
                        )
                        self.output(
                            f"[INFO] 换月 {self._prev_yymm}->{yymm} 计划切点 "
                            f"{fallback.switch_time} 因节假日/休市无对应 bar，"
                            f"顺延至 {bar.datetime}（延迟 {gap_days} 天）执行移仓"
                        )
                        self._execute_rollover(fallback, exec_time=bar.datetime)
                    else:
                        self.rollover_stats.missed_switches.append(
                            {
                                "from": self._prev_yymm,
                                "to": yymm,
                                "bar_datetime": bar.datetime.isoformat(),
                                "pos": float(self.strategy.pos),
                            }
                        )
                        self.output(
                            f"[WARN] 换月检测到 yymm 切换 {self._prev_yymm}->{yymm} "
                            f"于 {bar.datetime}，但未匹配到 RolloverEvent（切点时间戳可能不一致），"
                            f"持仓 {self.strategy.pos} 未执行移仓"
                        )
        if yymm:
            self._prev_yymm = yymm
        super().new_bar(bar)

    def _execute_rollover(
        self, event: RolloverEvent, *, exec_time: datetime | None = None,
    ) -> None:
        strategy: CtaTemplate = self.strategy
        pos = float(strategy.pos)
        if abs(pos) < 1e-9:
            return

        rollover_dt = exec_time or event.switch_time
        volume = abs(pos)
        self.bar = BarData(
            gateway_name="ROLLOVER",
            symbol=self.symbol,
            exchange=self.exchange,
            datetime=rollover_dt,
            interval=self.interval,
            volume=0,
            turnover=0,
            open_interest=0,
            open_price=event.new_open,
            high_price=max(event.old_close, event.new_open),
            low_price=min(event.old_close, event.new_open),
            close_price=event.new_open,
        )
        self.datetime = rollover_dt

        strategy._rollover_in_progress = True  # type: ignore[attr-defined]

        if pos > 0:
            self._force_trade(Direction.SHORT, Offset.CLOSE, event.old_close, volume)
            self._force_trade(Direction.LONG, Offset.OPEN, event.new_open, volume)
        else:
            self._force_trade(Direction.LONG, Offset.CLOSE, event.old_close, volume)
            self._force_trade(Direction.SHORT, Offset.OPEN, event.new_open, volume)

        strategy._rollover_in_progress = False  # type: ignore[attr-defined]

        rollover_slip = event.slippage_cost * volume * self.size
        rollover_comm = event.commission_cost * volume * self.size
        cost_date = rollover_dt.date()
        prev_slip, prev_comm = self._rollover_cost_by_date.get(cost_date, (0.0, 0.0))
        self._rollover_cost_by_date[cost_date] = (
            prev_slip + rollover_slip,
            prev_comm + rollover_comm,
        )
        self.rollover_stats.total_rollover_slippage += rollover_slip
        self.rollover_stats.total_rollover_commission += rollover_comm

        purged = self._purge_stale_orders()
        if purged:
            self.output(
                f"[INFO] 换月 {event.from_yymm}->{event.to_yymm} 强制撤销 {purged} 笔 "
                f"旧合约挂单（价格刻度已失效）"
            )

        if hasattr(strategy, "on_rollover_adjust"):
            strategy.on_rollover_adjust(event)  # type: ignore[attr-defined]
        elif not self._warned_no_adjust_hook:
            self._warned_no_adjust_hook = True
            self.output(
                f"[WARN] 策略 {strategy.strategy_name} 未实现 on_rollover_adjust，"
                f"换月后策略内部价格状态（止损/目标价等）不会随合约切换平移，"
                f"可能导致后续判断使用旧合约价格刻度"
            )

        gap_pnl = -event.price_shift * pos * self.size
        self.rollover_stats.count += 1
        self.rollover_stats.contracts_rolled += round(volume)
        self.rollover_stats.total_gap_pnl += gap_pnl
        self.rollover_stats.events.append(
            {
                "switch": event.switch_time.isoformat(),
                "executed_at": rollover_dt.isoformat(),
                "from": event.from_yymm,
                "to": event.to_yymm,
                "pos": pos,
                "old_close": event.old_close,
                "new_open": event.new_open,
                "price_shift": event.price_shift,
                "gap_pnl": gap_pnl,
                "rollover_slippage": rollover_slip,
                "rollover_commission": rollover_comm,
            }
        )

    def calculate_result(self) -> pd.DataFrame:
        """逐日盯市；换月成交用 rollover_cost_detail，不走引擎默认 rate/slippage。"""
        self.output("开始计算逐日盯市盈亏")

        if not self.trades:
            self.output("回测成交记录为空")

        for trade in self.trades.values():
            if not trade.datetime:
                continue
            d: Date = trade.datetime.date()
            daily_result: DailyResult = self.daily_results[d]
            daily_result.add_trade(trade)

        pre_close: float = 0
        start_pos: float = 0

        for daily_result in self.daily_results.values():
            self._calculate_daily_pnl_with_rollover_cost(
                daily_result, pre_close, start_pos,
            )
            pre_close = daily_result.close_price
            start_pos = daily_result.end_pos

        results: defaultdict = defaultdict(list)
        for daily_result in self.daily_results.values():
            for key, value in daily_result.__dict__.items():
                results[key].append(value)

        if results:
            self.daily_df = pd.DataFrame.from_dict(results).set_index("date")

        self.output("逐日盯市盈亏计算完成")
        return self.daily_df

    def _calculate_daily_pnl_with_rollover_cost(
        self,
        daily_result: DailyResult,
        pre_close: float,
        start_pos: float,
    ) -> None:
        """换月成交计仓位盈亏，滑点/手续费取自 rollover_cost_detail（元/吨）。"""
        if pre_close:
            daily_result.pre_close = pre_close
        else:
            daily_result.pre_close = 1

        daily_result.start_pos = start_pos
        daily_result.end_pos = start_pos
        daily_result.holding_pnl = (
            daily_result.start_pos
            * (daily_result.close_price - daily_result.pre_close)
            * self.size
        )
        daily_result.trade_count = len(daily_result.trades)

        for trade in daily_result.trades:
            pos_change = trade.volume if trade.direction == Direction.LONG else -trade.volume
            daily_result.end_pos += pos_change
            turnover = trade.volume * self.size * trade.price
            daily_result.trading_pnl += pos_change * (
                daily_result.close_price - trade.price
            ) * self.size
            daily_result.turnover += turnover
            if trade.gateway_name != ROLLOVER_GATEWAY:
                daily_result.slippage += trade.volume * self.size * self.slippage
                daily_result.commission += turnover * self.rate

        extra_slip, extra_comm = self._rollover_cost_by_date.get(daily_result.date, (0.0, 0.0))
        daily_result.slippage += extra_slip
        daily_result.commission += extra_comm

        daily_result.total_pnl = daily_result.trading_pnl + daily_result.holding_pnl
        daily_result.net_pnl = (
            daily_result.total_pnl
            - daily_result.commission
            - daily_result.slippage
        )

    def _purge_stale_orders(self) -> int:
        """换月后旧合约挂单价格刻度失效，强制撤销并回调策略。"""
        purged = len(self.active_stop_orders) + len(self.active_limit_orders)
        if purged:
            self.cancel_all(self.strategy)
        return purged

    def _force_trade(
        self,
        direction: Direction,
        offset: Offset,
        price: float,
        volume: float,
    ) -> None:
        price = round_to(price, self.pricetick)
        rounded_volume = round(volume, 6)
        if abs(rounded_volume - volume) > 1e-6:
            self.output(
                f"[WARN] 换月强平手数四舍五入偏差 {volume} -> {rounded_volume}，"
                f"若非期货整数手请核查仓位精度"
            )
        volume = rounded_volume
        if volume <= 0:
            return

        self.trade_count += 1
        pos_change = volume if direction == Direction.LONG else -volume

        trade = TradeData(
            symbol=self.symbol,
            exchange=self.exchange,
            orderid=f"ROLLOVER_{self.trade_count}",
            tradeid=str(self.trade_count),
            direction=direction,
            offset=offset,
            price=price,
            volume=volume,
            datetime=self.datetime or datetime.now(),
            gateway_name=ROLLOVER_GATEWAY,
        )
        self.strategy.pos += pos_change
        self.strategy.on_trade(trade)
        self.trades[trade.vt_tradeid] = trade
