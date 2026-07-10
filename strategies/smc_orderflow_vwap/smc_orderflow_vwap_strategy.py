"""SMC + Order Flow + VWAP/Z-Score 融合机构交易策略。

周期：15M 宏观结构过滤（默认）+ 5M 微观统计与订单流触发；可选 60M 对照。
适配：中国商品期货交易日（夜盘 21:00 为 VWAP 重置起点）与日内 Scale Out。
"""
from __future__ import annotations

from datetime import datetime, time
from zoneinfo import ZoneInfo

import numpy as np

from vnpy.trader.constant import Direction, Interval
from vnpy.trader.utility import ArrayManager, BarGenerator
from vnpy_ctastrategy import (
    BarData,
    CtaTemplate,
    OrderData,
    StopOrder,
    TickData,
    TradeData,
)

from strategies.smc_orderflow_vwap.session_bar_generator import SessionAwareBarGenerator

CST = ZoneInfo("Asia/Shanghai")


def bar_cst(bar: BarData) -> datetime:
    """将 Bar 时间统一为 Asia/Shanghai。"""
    dt = bar.datetime
    if dt.tzinfo is None:
        return dt.replace(tzinfo=CST)
    return dt.astimezone(CST)


def is_new_trading_day_bar(bar: BarData) -> bool:
    """国内期货新交易日首根 K 线：夜盘 21:00（含 20:59 预热 bar 的下一根）。"""
    dt = bar_cst(bar)
    return dt.hour == 21 and dt.minute == 0


class SmcOrderFlowVwapStrategy(CtaTemplate):
    """SMC 结构 + VWAP Z-Score + 订单流 Delta 三维共振策略（当前仅多头）。"""

    author = "Tao Freeman"

    zscore_threshold = 2.5
    vwap_length = 60
    fixed_size = 4
    slippage = 2
    ob_stop_buffer = 2
    min_risk_ticks = 5
    scale_out_remain_stop = "breakeven_plus"
    scale_out_stop_buffer = 1
    scale_out_mode = "fixed"
    scale_out_min_profit_ticks = 15
    use_bar_delta_proxy = True
    pa_reversal_lower_shadow_ratio = 0.35
    pa_zone_max_wait_bars = 16
    pa_two_bar_rev_enabled = True
    pa_two_bar_rev_body_ratio = 0.45
    setup_b_stat_enabled = False
    setup_c_structure_enabled = False
    setup_b_stop_lookback = 5
    macro_tf = "15m"
    smc_pool_bars = 12
    smc_min_bars = 16

    order_block_low = 0.0
    order_block_high = 0.0
    smc_structure_signal = 0
    vwap_cum_volume = 0.0
    vwap_cum_turnover = 0.0
    current_vwap = 0.0
    current_zscore = 0.0
    bar_5m_delta = 0.0

    entry_price = 0.0
    entry_pos = 0
    half_close_triggered = False

    parameters = [
        "zscore_threshold",
        "vwap_length",
        "fixed_size",
        "slippage",
        "ob_stop_buffer",
        "min_risk_ticks",
        "scale_out_remain_stop",
        "scale_out_stop_buffer",
        "scale_out_mode",
        "scale_out_min_profit_ticks",
        "use_bar_delta_proxy",
        "pa_reversal_lower_shadow_ratio",
        "pa_zone_max_wait_bars",
        "pa_two_bar_rev_enabled",
        "pa_two_bar_rev_body_ratio",
        "setup_b_stat_enabled",
        "setup_c_structure_enabled",
        "setup_b_stop_lookback",
        "macro_tf",
        "smc_pool_bars",
        "smc_min_bars",
    ]
    variables = [
        "order_block_low",
        "order_block_high",
        "smc_structure_signal",
        "current_vwap",
        "current_zscore",
        "bar_5m_delta",
        "entry_price",
        "half_close_triggered",
        "pa_confirm_state",
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg_5min = BarGenerator(self.on_bar, 5, self.on_5min_bar)
        self.bg_15min = BarGenerator(self.on_bar, 15, self.on_15min_bar)
        self.bg_60min = BarGenerator(
            self.on_bar, 1, self.on_1hour_bar, interval=Interval.HOUR,
        )
        self.bg_5min_sa = SessionAwareBarGenerator(self.bg_5min)
        self.bg_15min_sa = SessionAwareBarGenerator(self.bg_15min)
        self.bg_60min_sa = SessionAwareBarGenerator(self.bg_60min)

        self.am_5 = ArrayManager(size=120)
        self.am_15 = ArrayManager(size=120)
        self.am_60 = ArrayManager(size=80)

        self.last_tick_price = 0.0
        self.last_bar_close = 0.0
        self.active_stop_order_ids: list[str] = []

        self.delta_history: list[float] = []
        self.max_delta_len = 10

        self._entry_branch_events: list[tuple[datetime, str]] = []
        self._pending_stop_price = 0.0
        self._structural_stop_price = 0.0

        self.pa_confirm_state = "IDLE"
        self.pa_zone_wait_bars = 0
        self.pa_zone_zscore = 0.0

    def on_init(self) -> None:
        self.write_log("SMC-OrderFlow-VWAP 策略初始化（离线模式依赖 1m Bar 预热）")

    def on_start(self) -> None:
        self.write_log(
            f"策略启动，宏观 {self.macro_tf.upper()} + 5M 统计边界"
            f"（休市断 bar 已启用）"
        )

    def on_stop(self) -> None:
        self.cancel_all()
        self.write_log("策略停止")

    def record_entry_branch_event(self, bar: BarData, branch: str) -> None:
        self._entry_branch_events.append((bar_cst(bar), branch))

    def on_tick(self, tick: TickData) -> None:
        """Tick 级订单流 Delta（实盘 / Tick 回测时启用）。"""
        if self.last_tick_price <= 0:
            self.last_tick_price = tick.last_price
            return

        tick_volume = float(tick.last_volume or 0)
        if tick_volume <= 0:
            self.last_tick_price = tick.last_price
            return

        if tick.last_price > self.last_tick_price:
            self.bar_5m_delta += tick_volume
        elif tick.last_price < self.last_tick_price:
            self.bar_5m_delta -= tick_volume
        elif tick.ask_price_1 > 0 and tick.last_price >= tick.ask_price_1:
            self.bar_5m_delta += tick_volume
        elif tick.bid_price_1 > 0 and tick.last_price <= tick.bid_price_1:
            self.bar_5m_delta -= tick_volume

        self.last_tick_price = tick.last_price

    def on_bar(self, bar: BarData) -> None:
        """1 分钟基础通道：交易日 VWAP 账本 + Delta 代理 + 多周期合成。"""
        if is_new_trading_day_bar(bar):
            self.vwap_cum_volume = 0.0
            self.vwap_cum_turnover = 0.0
            self.write_log("【交易日交替】夜盘 21:00，VWAP 累计账本重置")

        bar_vol = float(bar.volume)
        if bar_vol > 0:
            self.vwap_cum_volume += bar_vol
            turnover = float(bar.turnover) if bar.turnover else bar.close_price * bar_vol
            self.vwap_cum_turnover += turnover
            self.current_vwap = self.vwap_cum_turnover / self.vwap_cum_volume

        if self.use_bar_delta_proxy:
            self._accumulate_bar_delta_proxy(bar)

        self.bg_5min_sa.update_bar(bar)
        if self.macro_tf == "60m":
            self.bg_60min_sa.update_bar(bar)
        else:
            self.bg_15min_sa.update_bar(bar)
        self.last_bar_close = bar.close_price

    def _accumulate_bar_delta_proxy(self, bar: BarData) -> None:
        """1m 离线代理：按 K 线方向将成交量归入主动买/卖（非真实 Footprint）。"""
        vol = float(bar.volume)
        if vol <= 0:
            return
        if bar.close_price > bar.open_price:
            self.bar_5m_delta += vol
        elif bar.close_price < bar.open_price:
            self.bar_5m_delta -= vol
        elif self.last_bar_close > 0:
            if bar.close_price > self.last_bar_close:
                self.bar_5m_delta += vol
            elif bar.close_price < self.last_bar_close:
                self.bar_5m_delta -= vol

    def _calc_stop_price(self, bar: BarData, entry_price: float) -> float | None:
        """结构止损：OB 下沿；猎杀入场时取更低 recent 5M low。无效风险距离则拒绝。"""
        if self.order_block_low <= 0:
            return None

        stop_price = self.order_block_low - self.ob_stop_buffer
        if bar.close_price < self.order_block_low:
            hunt_stop = float(np.min(self.am_5.low[-3:])) - self.ob_stop_buffer
            stop_price = min(stop_price, hunt_stop)

        if entry_price <= stop_price + self.min_risk_ticks:
            return None
        return stop_price

    def on_15min_bar(self, bar: BarData) -> None:
        """维度一：15M SMC 流动性掠夺 + 多头 OB（默认宏观层）。"""
        self._update_smc_structure(self.am_15, bar, "15M")

    def on_1hour_bar(self, bar: BarData) -> None:
        """维度一：60M SMC（macro_tf=60m 对照用）。"""
        self._update_smc_structure(self.am_60, bar, "60M")

    def _update_smc_structure(
        self, am: ArrayManager, bar: BarData, tf_label: str,
    ) -> None:
        """SMC 流动性猎杀 + OB 生命周期（宏观周期共用逻辑）。"""
        am.update_bar(bar)
        if not am.inited:
            return

        min_bars = self.smc_min_bars
        if len(am.low) < min_bars:
            return

        if self.order_block_low > 0 and bar.close_price < self.order_block_low:
            self.write_log(
                f"【{tf_label} SMC结构破灭】收盘价 {bar.close_price:.1f} "
                f"跌破下沿 {self.order_block_low:.1f}，OB 彻底销毁。"
            )
            self.order_block_low = 0.0
            self.order_block_high = 0.0

        pool_bars = self.smc_pool_bars
        if len(am.low) < pool_bars + 2:
            return

        lowest_pool = float(np.min(am.low[-pool_bars - 2:-2]))
        sweep_low = float(am.low[-2])
        sweep_close = float(am.close[-2])
        sweep_open = float(am.open[-2])

        if sweep_low < lowest_pool and sweep_close > lowest_pool:
            self.order_block_low = min(sweep_open, sweep_close)
            self.order_block_high = float(am.high[-2])
            self.write_log(
                f"【{tf_label} SMC】检测到流动性猎杀，确立新机构多头 OB: "
                f"[{self.order_block_low:.1f} - {self.order_block_high:.1f}]"
            )

    def on_5min_bar(self, bar: BarData) -> None:
        """维度二/三：5M Z-Score + Delta多棒背离确认 + Scale Out。"""
        self.am_5.update_bar(bar)
        if not self.am_5.inited:
            self.bar_5m_delta = 0.0
            return

        self._update_zscore(bar)

        if self.pos == 0:
            self.entry_price = 0.0
            self.entry_pos = 0
            self.half_close_triggered = False
            self.active_stop_order_ids.clear()

        bar_time = bar_cst(bar).time()
        if self._handle_scale_out(bar, bar_time):
            self._maintain_delta_history()
            return

        if self.order_block_low > 0 and bar.close_price <= self.order_block_high:
            self.smc_structure_signal = 1
        else:
            self.smc_structure_signal = 0

        if self.pos == 0:
            if self.pa_confirm_state == "ZONE_WATCH":
                self._process_pa_zone_watch(bar)
            elif self._has_entry_signal():
                if self._is_bull_reversal_bar(bar):
                    self._try_enter_zone_watch(bar)
                else:
                    fast_filled = self._try_fast_entry(bar)
                    if not fast_filled and self.pos == 0:
                        self._try_enter_zone_watch(bar)
            else:
                filled = self._try_setup_c_structure(bar)
                if not filled and self.pos == 0:
                    self._try_setup_b_stat(bar)

        if (
            self.order_block_low > 0
            and self.pos == 0
            and bar.close_price > self.order_block_high
        ):
            self.write_log(
                f"【SMC流动性缓解】价格成功涨破 OB 上沿 {self.order_block_high:.1f}，"
                f"该OB完成使命撤离内存。"
            )
            self.order_block_low = 0.0
            self.order_block_high = 0.0
            self.smc_structure_signal = 0
            if self.pa_confirm_state != "IDLE":
                self._reset_pa_state()

        self._maintain_delta_history()
        self.put_event()

    def _is_bull_reversal_bar(self, bar: BarData) -> bool:
        """Brooks 式反转棒：阳线收盘 + 下影线占比达标（对照 pa_lean OPP12 超调衰竭）。"""
        bar_range = bar.high_price - bar.low_price
        if bar_range <= 0:
            return False
        lower_shadow = min(bar.open_price, bar.close_price) - bar.low_price
        return (
            bar.close_price > bar.open_price
            and lower_shadow >= bar_range * self.pa_reversal_lower_shadow_ratio
        )

    def _has_entry_signal(self) -> bool:
        """三维共振（Setup A）：OB 区内 + Z-Score 超跌 + Delta 转正。"""
        return (
            self.smc_structure_signal == 1
            and self.current_zscore < -self.zscore_threshold
            and self.bar_5m_delta > 0
        )

    def _calc_structural_stop_fallback(
        self, bar: BarData, entry_price: float,
    ) -> float | None:
        """无 OB 时的结构止损兜底：近 N 根 5M 低点。"""
        if len(self.am_5.low) < self.setup_b_stop_lookback:
            return None
        stop_price = float(
            np.min(self.am_5.low[-self.setup_b_stop_lookback:])
        ) - self.ob_stop_buffer
        if entry_price <= stop_price + self.min_risk_ticks:
            return None
        return stop_price

    def _try_setup_c_structure(self, bar: BarData) -> bool:
        """Setup C（纯结构单）：OB 区内 + PA 反转棒 + Delta 转正，不要求 Z-Score 极值。"""
        if not self.setup_c_structure_enabled:
            return False
        if not (
            self.smc_structure_signal == 1
            and self._is_bull_reversal_bar(bar)
            and self.bar_5m_delta > 0
        ):
            return False

        entry_price = bar.close_price + self.slippage
        stop_price = self._calc_stop_price(bar, entry_price)
        if stop_price is None:
            return False

        self._pending_stop_price = stop_price
        self.record_entry_branch_event(bar, "setup_c_structure")
        self.buy(entry_price, self.fixed_size)
        self.write_log(
            f"【Setup C-纯结构单】反转棒 + Delta {self.bar_5m_delta:.0f}（未达 Z-Score "
            f"阈值 {self.current_zscore:.2f}）| 入场 {entry_price:.1f} | "
            f"结构止损 {stop_price:.1f}"
        )
        return True

    def _try_setup_b_stat(self, bar: BarData) -> bool:
        """Setup B（纯统计单）：Z-Score 超跌 + Delta 转正，不要求当前处于 OB 区间内。"""
        if not self.setup_b_stat_enabled:
            return False
        if not (
            self.current_zscore < -self.zscore_threshold
            and self.bar_5m_delta > 0
        ):
            return False

        entry_price = bar.close_price + self.slippage
        if self.order_block_low > 0:
            stop_price = self._calc_stop_price(bar, entry_price)
        else:
            stop_price = self._calc_structural_stop_fallback(bar, entry_price)
        if stop_price is None:
            return False

        self._pending_stop_price = stop_price
        self.record_entry_branch_event(bar, "setup_b_stat")
        self.buy(entry_price, self.fixed_size)
        self.write_log(
            f"【Setup B-纯统计单】Z-Score {self.current_zscore:.2f} + "
            f"Delta {self.bar_5m_delta:.0f}（不要求 OB 区间）| 入场 {entry_price:.1f} | "
            f"结构止损 {stop_price:.1f}"
        )
        return True

    def _try_fast_entry(self, bar: BarData) -> bool:
        """快通道：极值棒非反转棒时，单棒直接入场。"""
        if not self._has_entry_signal():
            return False
        if self._is_bull_reversal_bar(bar):
            return False

        entry_price = bar.close_price + self.slippage
        stop_price = self._calc_stop_price(bar, entry_price)
        if stop_price is None:
            return False

        self._pending_stop_price = stop_price
        self.record_entry_branch_event(bar, "fast_reversal")
        self.buy(entry_price, self.fixed_size)
        self.write_log(
            f"【快通道入场】Z-Score {self.current_zscore:.2f} | "
            f"Delta {self.bar_5m_delta:.0f} | 入场 {entry_price:.1f} | "
            f"结构止损 {stop_price:.1f} | 风险 {entry_price - stop_price:.1f} tick"
        )
        return True

    def _try_enter_zone_watch(self, bar: BarData) -> None:
        """慢通道阶段一：极值棒为反转棒（或快通道未成交）时标记观察区。"""
        if not self._has_entry_signal():
            return

        self.pa_confirm_state = "ZONE_WATCH"
        self.pa_zone_wait_bars = 0
        self.pa_zone_zscore = self.current_zscore
        self.write_log(
            f"【慢通道-观察区激活】Z-Score {self.current_zscore:.2f} | "
            f"Delta {self.bar_5m_delta:.0f} | 次棒起等待反转棒或 OPP16（非反转棒）"
        )

    def _is_opp16_two_bar_rev_long(self, bar: BarData) -> bool:
        """OPP16 简化版：前棒空头趋势棒 + 本棒收过前棒中点（对照 pa_lean）。"""
        if not self.pa_two_bar_rev_enabled or len(self.am_5.close) < 2:
            return False
        prev_close = float(self.am_5.close[-2])
        prev_open = float(self.am_5.open[-2])
        prev_high = float(self.am_5.high[-2])
        prev_low = float(self.am_5.low[-2])
        prev_range = prev_high - prev_low
        if prev_range <= 0:
            return False
        prev_body_ratio = abs(prev_close - prev_open) / prev_range
        if prev_body_ratio < self.pa_two_bar_rev_body_ratio:
            return False
        if prev_close >= prev_open:
            return False
        prev_mid = (prev_high + prev_low) / 2.0
        return bar.close_price > prev_mid

    def _resolve_slow_entry_branch(self, bar: BarData) -> str | None:
        """慢通道扳机：反转棒 / OPP16 分列；OPP16 仅评估非反转棒。"""
        if self.bar_5m_delta <= 0:
            return None
        if self._is_bull_reversal_bar(bar):
            return "slow_reversal"
        if self._is_opp16_two_bar_rev_long(bar):
            return "slow_opp16"
        return None

    def _try_slow_channel_entry(self, bar: BarData, branch: str) -> bool:
        entry_price = bar.close_price + self.slippage
        stop_price = self._calc_stop_price(bar, entry_price)
        if stop_price is None:
            return False
        self._pending_stop_price = stop_price
        self.record_entry_branch_event(bar, branch)
        self.buy(entry_price, self.fixed_size)
        label = "反转棒" if branch == "slow_reversal" else "OPP16两棒反转"
        self.write_log(
            f"【慢通道-{label}入场】观察区 Z {self.pa_zone_zscore:.2f} | "
            f"入场 {entry_price:.1f} | 结构止损 {stop_price:.1f} | "
            f"风险 {entry_price - stop_price:.1f} tick"
        )
        return True

    def _process_pa_zone_watch(self, bar: BarData) -> None:
        """慢通道阶段二：观察区内等待反转棒或 OPP16，出现即收盘入场。"""
        self.pa_zone_wait_bars += 1

        branch = self._resolve_slow_entry_branch(bar)
        if branch is not None:
            if self._try_slow_channel_entry(bar, branch):
                self._reset_pa_state()
            return

        if (
            self.pa_zone_wait_bars > self.pa_zone_max_wait_bars
            or self.order_block_low <= 0
            or self.smc_structure_signal == 0
        ):
            self.write_log(
                f"【观察区撤销】等待 {self.pa_zone_wait_bars} 棒未出现合格反转棒，"
                f"或结构已失效"
            )
            self._reset_pa_state()

    def _reset_pa_state(self) -> None:
        self.pa_confirm_state = "IDLE"
        self.pa_zone_wait_bars = 0
        self.pa_zone_zscore = 0.0

    def _maintain_delta_history(self) -> None:
        """推入历史队列并清空单根 5M Delta 计数。"""
        self.delta_history.append(self.bar_5m_delta)
        if len(self.delta_history) > self.max_delta_len:
            self.delta_history.pop(0)
        self.bar_5m_delta = 0.0

    def _update_zscore(self, bar: BarData) -> None:
        if self.current_vwap <= 0:
            self.current_zscore = 0.0
            return

        length = min(self.vwap_length, len(self.am_5.close))
        if length < 10:
            return

        deviations = self.am_5.close[-length:] - self.current_vwap
        std_dev = float(np.std(deviations))
        if std_dev > 0:
            self.current_zscore = (bar.close_price - self.current_vwap) / std_dev
        else:
            self.current_zscore = 0.0

    def _should_scale_out(self, bar: BarData, bar_time: time) -> bool:
        """按 scale_out_mode 判断是否触发平半仓。"""
        mode = self.scale_out_mode
        if mode == "none":
            return False
        if mode == "vwap":
            if self.current_vwap <= 0 or self.entry_price <= 0:
                return False
            return bar.close_price >= self.current_vwap
        if mode == "profit_gated":
            if bar_time.hour != 14 or bar_time.minute != 50:
                return False
            return (bar.close_price - self.entry_price) >= self.scale_out_min_profit_ticks
        # 触发点提前到 14:50（而非日盘收盘前最后一根 14:55），
        # 因为平仓为限价单，需等下一根 bar 撮合；若在 14:55 触发，
        # 回测中日盘已无下一根 bar，委托会被撮合到 21:00 夜盘开盘，
        # 完全丧失"日内了结、规避隔夜风险"的本意（已用诊断脚本复现）。
        return bar_time.hour == 14 and bar_time.minute == 50

    def _resolve_remain_stop_price(self) -> float:
        """平半后余仓止损价。"""
        if self.scale_out_remain_stop == "structure":
            return self._structural_stop_price
        if self.scale_out_remain_stop == "breakeven_plus":
            return self.entry_price + self.scale_out_stop_buffer
        return self.entry_price

    def _handle_scale_out(self, bar: BarData, bar_time: time) -> bool:
        """平半仓：触发条件由 scale_out_mode 控制，余仓止损按 scale_out_remain_stop。"""
        if self.pos <= 0 or self.half_close_triggered:
            return False
        if not self._should_scale_out(bar, bar_time):
            return False

        self.half_close_triggered = True
        total = abs(int(self.pos))
        half_vol = total // 2
        remaining = total - half_vol

        self._cancel_active_stop_orders()
        if half_vol > 0:
            self.sell(bar.close_price - self.slippage, half_vol)
            self.write_log(
                f"【Scale Out】模式 {self.scale_out_mode} | 平半仓 {half_vol} 手"
            )

        if remaining > 0 and self.entry_price > 0:
            stop_price = self._resolve_remain_stop_price()
            if stop_price > 0:
                order_ids = self.sell(stop_price, remaining, stop=True)
                self.active_stop_order_ids.extend(order_ids)
                self.write_log(
                    f"【余仓止损】模式 {self.scale_out_remain_stop} | "
                    f"剩余 {remaining} 手 @ {stop_price:.1f}"
                )

        return True

    def on_trade(self, trade: TradeData) -> None:
        if trade.direction == Direction.LONG and self.pos > 0 and self.entry_price == 0.0:
            self.entry_price = trade.price
            self.entry_pos = int(self.pos)

            stop_price = self._pending_stop_price
            if stop_price <= 0 and self.order_block_low > 0:
                stop_price = self.order_block_low - self.ob_stop_buffer
            if stop_price > 0 and self.entry_price > stop_price + self.min_risk_ticks:
                self._structural_stop_price = stop_price
                order_ids = self.sell(stop_price, abs(self.pos), stop=True)
                self.active_stop_order_ids.extend(order_ids)
                self.write_log(
                    f"【建仓】均价 {self.entry_price:.1f}，结构止损 {stop_price:.1f}"
                )
            self._pending_stop_price = 0.0

        self.put_event()

    def on_order(self, order: OrderData) -> None:
        pass

    def on_stop_order(self, stop_order: StopOrder) -> None:
        pass

    def _cancel_active_stop_orders(self) -> None:
        if not self.active_stop_order_ids:
            return
        for vt_orderid in list(self.active_stop_order_ids):
            self.cancel_order(vt_orderid)
        self.active_stop_order_ids.clear()
