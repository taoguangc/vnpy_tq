"""STRAT_TREND_BROOKS_SCALP_02 — PAAF orchestration for first-pullback.

Lineage: PRC-BROOKS_SCALP-v1 · parent CID_001 / STRAT_CAND_001
Strategy only orchestrates: Context → Detector → Risk levels → Execution → log.
Morphology lives in BrooksScalpFirstPullbackDetector.
"""

from __future__ import annotations

from vnpy.trader.constant import Direction, Offset
from vnpy_ctastrategy import (
    ArrayManager,
    BarData,
    CtaTemplate,
    StopOrder,
    TradeData,
)

from strategies.paaf.detectors.brooks_scalp_first_pullback import (
    BrooksScalpFirstPullbackDetector,
)
from strategies.paaf.domain import Direction as PaafDirection
from strategies.paaf.engines.context_engine import ContextEngine


class BrooksScalpPaafStrategy(CtaTemplate):
    """PAAF rewrite orchestrator（v0.1.0）— no pattern logic inlined."""

    author = "vnpy_tq"

    strategy_id = "STRAT_TREND_BROOKS_SCALP_02"
    strategy_version = "0.1.0"

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

    hold_bars = 0
    fsm = "IDLE"
    trend = 0

    variables = ["hold_bars", "fsm", "trend"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.am = ArrayManager(200)
        self.context_engine = ContextEngine(symbol=str(vt_symbol or ""))
        self.detector = BrooksScalpFirstPullbackDetector(
            ema_period=self.ema_period,
            atr_period=self.atr_period,
            trend_leg_atr=self.trend_leg_atr,
            pullback_atr=self.pullback_atr,
            risk_reward=self.risk_reward,
            pricetick=1.0,
        )

        self.entry_price = 0.0
        self.stop_price = 0.0
        self.target_price = 0.0
        self._entry_dt = None
        self._entry_side = 0
        self._entry_fill = 0.0
        self._trip_mfe = 0.0
        self._trip_mae = 0.0
        self._trade_log: list[dict] = []
        self._tick_bound = False

    def on_init(self) -> None:
        self.write_log(
            f"{self.strategy_id}@{self.strategy_version} initialized "
            f"(parent=CID_001; detector=BROOKS_SCALP_FP@0.1.0)"
        )
        self.load_bar(30)

    def on_start(self) -> None:
        self.write_log(f"{self.strategy_id} started")

    def on_stop(self) -> None:
        self.write_log(
            f"{self.strategy_id} stopped | closed_trades={len(self._trade_log)}"
        )

    def on_bar(self, bar: BarData) -> None:
        self._ensure_pricetick()
        self.am.update_bar(bar)
        if not self.am.inited:
            return

        context = self.context_engine.update(self.am, symbol=self.vt_symbol)
        result = self.detector.detect(self.am, context)
        ps = self.detector.pattern_state
        self.fsm = str(ps.metadata.get("fsm", "IDLE"))
        self.trend = int(ps.metadata.get("trend", 0))

        if self.pos == 0:
            if self.trend == 0:
                self.cancel_all()
            if result is not None:
                self._submit_stop_entry(result)
        else:
            self.cancel_all()
            self._manage_position(bar)

        self.put_event()

    def _ensure_pricetick(self) -> None:
        if self._tick_bound:
            return
        tick = float(self.get_pricetick() or 0.0)
        if tick <= 0:
            tick = 1.0
        self.detector.set_pricetick(tick)
        self._tick_bound = True

    def _submit_stop_entry(self, result) -> None:
        if result.entry is None or result.stop is None or result.target is None:
            return
        self.cancel_all()
        self.entry_price = float(result.entry)
        self.stop_price = float(result.stop)
        self.target_price = float(result.target)
        size = int(self.fixed_size)
        if result.direction is PaafDirection.LONG:
            self.buy(self.entry_price, size, stop=True)
        elif result.direction is PaafDirection.SHORT:
            self.short(self.entry_price, size, stop=True)
        self.write_log(
            f"signal {result.direction.value} entry={self.entry_price} "
            f"stop={self.stop_price} target={self.target_price} "
            f"reason={result.reason}"
        )

    def _manage_position(self, bar: BarData) -> None:
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
        tick = float(self.get_pricetick() or 1.0)
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
                "strategy_id": self.strategy_id,
                "strategy_version": self.strategy_version,
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
            if self._entry_dt is None:
                self._entry_dt = trade.datetime
            self._entry_fill = trade.price
            self._trip_mfe = 0.0
            self._trip_mae = 0.0
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder) -> None:
        pass
