"""RolloverBacktestingEngine 节假日换月兜底逻辑单测。

模拟场景：rollover_map 记录的 switch_time 为节假日前夜盘时刻，但该时刻
无对应 1m bar（夜盘停牌）。策略在该切点前后持仓，验证引擎能顺延至节后
第一根 bar 完成移仓，而不是静默跳过（missed_switches）。

用法：.venv/Scripts/python.exe scripts/test_rollover_holiday_gap.py
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData

from scripts.rollover_backtest_engine import RolloverBacktestingEngine
from scripts.tq_rollover_data import RolloverEvent

CST = ZoneInfo("Asia/Shanghai")


class _FakeStrategy:
    """最小策略桩：仅提供引擎移仓逻辑依赖的属性/方法。"""

    def __init__(self) -> None:
        self.pos = 0.0
        self.strategy_name = "fake"
        self.trades = []
        self.inited = True
        self.trading = True

    def on_trade(self, trade) -> None:
        self.trades.append(trade)

    def on_bar(self, bar) -> None:
        pass

    def on_order(self, order) -> None:
        pass

    def on_stop_order(self, stop_order) -> None:
        pass


def _make_bar(dt: datetime, yymm: str, price: float) -> BarData:
    bar = BarData(
        gateway_name="TEST",
        symbol="rb",
        exchange=Exchange.SHFE,
        datetime=dt,
        interval=Interval.MINUTE,
        open_price=price,
        high_price=price,
        low_price=price,
        close_price=price,
        volume=1,
    )
    bar.yymm = yymm  # type: ignore[attr-defined]
    return bar


def test_holiday_gap_fallback() -> None:
    engine = RolloverBacktestingEngine()
    engine.symbol = "rb"
    engine.exchange = Exchange.SHFE
    engine.interval = Interval.MINUTE
    engine.size = 10
    engine.pricetick = 1.0
    engine.strategy = _FakeStrategy()
    engine.strategy.pos = 1.0  # 持有多头 1 手，切点必须移仓

    planned_switch = datetime(2025, 4, 3, 21, 0, tzinfo=CST)  # 清明节前夜盘（假设当晚停牌）
    event = RolloverEvent(
        switch_time=planned_switch,
        from_yymm="2505",
        to_yymm="2510",
        old_close=3500.0,
        new_open=3520.0,
        price_diff=20.0,
        slippage_cost=1.0,
        commission_cost=0.5,
        total_adjustment=21.5,
    )
    engine.set_rollover_events([event])

    prev_bar = _make_bar(datetime(2025, 4, 3, 14, 59, tzinfo=CST), "2505", 3500.0)
    engine.new_bar(prev_bar)
    assert engine.rollover_stats.count == 0, "换月前不应触发移仓"

    next_bar = _make_bar(datetime(2025, 4, 7, 9, 0, tzinfo=CST), "2510", 3520.0)
    engine.new_bar(next_bar)

    assert engine.rollover_stats.count == 1, (
        f"预期节假日缺口应顺延执行 1 次移仓，实际 {engine.rollover_stats.count}"
    )
    assert not engine.rollover_stats.missed_switches, (
        f"不应出现 missed_switches，实际 {engine.rollover_stats.missed_switches}"
    )
    assert len(engine.rollover_stats.holiday_gap_events) == 1, "应记录 1 条 holiday_gap_events"

    gap = engine.rollover_stats.holiday_gap_events[0]
    assert gap["from"] == "2505" and gap["to"] == "2510"
    assert gap["actual_switch"] == next_bar.datetime.isoformat()
    assert gap["gap_days"] == 4

    assert engine.strategy.pos == 1.0, "移仓后仓位应保持不变（平旧开新等量）"
    print("[PASS] test_holiday_gap_fallback")


def test_exact_match_no_fallback() -> None:
    """精确匹配 switch_time 时，不应触发 holiday_gap_events 分支。"""
    engine = RolloverBacktestingEngine()
    engine.symbol = "rb"
    engine.exchange = Exchange.SHFE
    engine.interval = Interval.MINUTE
    engine.size = 10
    engine.pricetick = 1.0
    engine.strategy = _FakeStrategy()
    engine.strategy.pos = -1.0

    switch_time = datetime(2025, 6, 10, 21, 0, tzinfo=CST)
    event = RolloverEvent(
        switch_time=switch_time,
        from_yymm="2506",
        to_yymm="2511",
        old_close=3600.0,
        new_open=3610.0,
        price_diff=10.0,
        slippage_cost=1.0,
        commission_cost=0.5,
        total_adjustment=11.5,
    )
    engine.set_rollover_events([event])

    engine.new_bar(_make_bar(datetime(2025, 6, 10, 14, 59, tzinfo=CST), "2506", 3600.0))
    engine.new_bar(_make_bar(switch_time, "2511", 3610.0))

    assert engine.rollover_stats.count == 1
    assert not engine.rollover_stats.holiday_gap_events, "精确匹配不应进入兜底分支"
    assert not engine.rollover_stats.missed_switches
    print("[PASS] test_exact_match_no_fallback")


def test_truly_missing_pair_still_reported() -> None:
    """rollover_events 中完全不存在的 (from, to) 组合应仍归入 missed_switches。"""
    engine = RolloverBacktestingEngine()
    engine.symbol = "rb"
    engine.exchange = Exchange.SHFE
    engine.interval = Interval.MINUTE
    engine.size = 10
    engine.pricetick = 1.0
    engine.strategy = _FakeStrategy()
    engine.strategy.pos = 1.0
    engine.set_rollover_events([])

    engine.new_bar(_make_bar(datetime(2025, 4, 3, 14, 59, tzinfo=CST), "2505", 3500.0))
    engine.new_bar(_make_bar(datetime(2025, 4, 7, 9, 0, tzinfo=CST), "2510", 3520.0))

    assert engine.rollover_stats.count == 0
    assert len(engine.rollover_stats.missed_switches) == 1
    assert not engine.rollover_stats.holiday_gap_events
    print("[PASS] test_truly_missing_pair_still_reported")


def test_rollover_cost_applied_to_pnl() -> None:
    """rollover_cost_detail 的滑点/手续费应计入逐日 net_pnl，且不走引擎默认费率。"""
    engine = RolloverBacktestingEngine()
    engine.symbol = "rb"
    engine.exchange = Exchange.SHFE
    engine.interval = Interval.MINUTE
    engine.size = 10
    engine.pricetick = 1.0
    engine.rate = 1e-4
    engine.slippage = 1.0
    engine.strategy = _FakeStrategy()
    engine.strategy.pos = 1.0

    switch_time = datetime(2025, 6, 10, 21, 0, tzinfo=CST)
    event = RolloverEvent(
        switch_time=switch_time,
        from_yymm="2506",
        to_yymm="2511",
        old_close=3600.0,
        new_open=3610.0,
        price_diff=10.0,
        slippage_cost=2.0,
        commission_cost=0.6,
        total_adjustment=12.6,
    )
    engine.set_rollover_events([event])

    engine.new_bar(_make_bar(datetime(2025, 6, 10, 14, 59, tzinfo=CST), "2506", 3600.0))
    engine.new_bar(_make_bar(switch_time, "2511", 3610.0))

    assert engine.rollover_stats.total_rollover_slippage == 20.0
    assert engine.rollover_stats.total_rollover_commission == 6.0

    engine.calculate_result()
    d = switch_time.date()
    row = engine.daily_df.loc[d]
    assert row["slippage"] == 20.0
    assert row["commission"] == 6.0
    # 若走引擎默认费率，commission 约为 7.2（双笔 turnover×rate）
    rollover_trades = [t for t in engine.trades.values() if t.gateway_name == "ROLLOVER"]
    assert len(rollover_trades) == 2
    print("[PASS] test_rollover_cost_applied_to_pnl")


if __name__ == "__main__":
    test_holiday_gap_fallback()
    test_exact_match_no_fallback()
    test_truly_missing_pair_still_reported()
    test_rollover_cost_applied_to_pnl()
    print("全部通过")
