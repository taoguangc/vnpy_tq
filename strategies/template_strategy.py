"""商品期货 CTA 策略骨架模板。

这是一个空骨架，仅搭建 vnpy_ctastrategy 标准结构（参数占位 + 生命周期钩子 +
BarGenerator/ArrayManager 样板代码），不包含任何具体交易逻辑。

请复制本文件并重命名（如 my_strategy.py），在 on_bar 中填充自己的信号逻辑后，
通过 scripts/run_backtest.py 中的 STRATEGY_CLASS 指向新策略类进行回测。
"""
from __future__ import annotations

from vnpy_ctastrategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)


class TemplateStrategy(CtaTemplate):
    """空骨架策略：仅维护 K 线合成与技术指标缓存，不发出任何交易信号。"""

    author = "vnpy_tq"

    # ========== 策略参数（示例占位，按需增删） ==========
    fast_window = 10
    slow_window = 20

    # ========== 策略变量（会展示在 UI / 记录到日志） ==========
    fast_ma = 0.0
    slow_ma = 0.0

    parameters = ["fast_window", "slow_window"]
    variables = ["fast_ma", "slow_ma"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager()

    def on_init(self) -> None:
        """策略初始化回调：一般用于加载历史数据预热指标。"""
        self.write_log("策略初始化")
        self.load_bar(10)

    def on_start(self) -> None:
        """策略启动回调。"""
        self.write_log("策略启动")

    def on_stop(self) -> None:
        """策略停止回调。"""
        self.write_log("策略停止")

    def on_tick(self, tick: TickData) -> None:
        """Tick 推送回调：转发给 BarGenerator 合成分钟线。"""
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData) -> None:
        """K 线推送回调：在此处填充具体交易信号逻辑。"""
        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        # TODO: 在此处实现具体交易逻辑，例如：
        # self.fast_ma = am.sma(self.fast_window)
        # self.slow_ma = am.sma(self.slow_window)
        # if self.fast_ma > self.slow_ma and self.pos == 0:
        #     self.buy(bar.close_price, 1)
        # elif self.fast_ma < self.slow_ma and self.pos > 0:
        #     self.sell(bar.close_price, abs(self.pos))

        self.put_event()

    def on_order(self, order: OrderData) -> None:
        """委托状态更新回调。"""
        pass

    def on_trade(self, trade: TradeData) -> None:
        """成交回调。"""
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder) -> None:
        """本地停止单状态更新回调。"""
        pass
