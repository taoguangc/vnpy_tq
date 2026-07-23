"""STRAT_SESS_OPP19_REV_01@0.1.0 — PAAF orchestration for OPP19 OD-Reversal.

CID_011 · Candidate Identity Freeze target.
Strategy only orchestrates: Context → OPP19_REV Detector → levels → Execution → log.
Morphology + FSM live in OPP19OpeningDriveReversalDetector.

Signal on 5m（BarGenerator）; stop/target/time-stop managed on 1m.
"""

from __future__ import annotations

from vnpy.trader.constant import Direction, Offset
from vnpy_ctastrategy import (
    ArrayManager,
    BarData,
    BarGenerator,
    CtaTemplate,
    StopOrder,
    TradeData,
)

from scripts.tq_rollover_data import RolloverEvent
from strategies.paaf.detectors.opp19_opening_drive_reversal import (
    DEFAULT_ATR_PERIOD,
    DEFAULT_MAX_BAR1_RANGE_ATR,
    DEFAULT_MIN_BAR1_RANGE_ATR,
    DEFAULT_MORNING_CUTOFF_MINUTE,
    DEFAULT_NIGHT_CUTOFF_MINUTE,
    DEFAULT_OPENING_REV_BODY_RATIO,
    OPP19OpeningDriveReversalDetector,
)
from strategies.paaf.domain import Direction as PaafDirection
from strategies.paaf.engines.context_engine import ContextEngine


class StratSessOpp19Rev01Strategy(CtaTemplate):
    """CID_011 orchestrator v0.1.0 — no pattern logic inlined."""

    author = "vnpy_tq"

    strategy_id = "STRAT_SESS_OPP19_REV_01"
    strategy_version = "0.1.0"

    atr_period = DEFAULT_ATR_PERIOD
    opening_rev_body_ratio = DEFAULT_OPENING_REV_BODY_RATIO
    morning_cutoff_minute = DEFAULT_MORNING_CUTOFF_MINUTE
    night_cutoff_minute = DEFAULT_NIGHT_CUTOFF_MINUTE
    min_bar1_range_atr = DEFAULT_MIN_BAR1_RANGE_ATR
    max_bar1_range_atr = DEFAULT_MAX_BAR1_RANGE_ATR
    risk_reward = 1.0
    max_hold_bars = 50
    fixed_size = 1

    parameters = [
        "atr_period",
        "opening_rev_body_ratio",
        "morning_cutoff_minute",
        "night_cutoff_minute",
        "min_bar1_range_atr",
        "max_bar1_range_atr",
        "risk_reward",
        "max_hold_bars",
        "fixed_size",
    ]

    hold_bars = 0
    variables = ["hold_bars"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bg = BarGenerator(self.on_bar, 5, self.on_5min_bar)
        self.am = ArrayManager(200)
        self.context_engine = ContextEngine(symbol=str(vt_symbol or ""))
        self.detector = OPP19OpeningDriveReversalDetector(
            atr_period=int(self.atr_period),
            opening_rev_body_ratio=float(self.opening_rev_body_ratio),
            morning_cutoff_minute=int(self.morning_cutoff_minute),
            night_cutoff_minute=int(self.night_cutoff_minute),
            min_bar1_range_atr=float(self.min_bar1_range_atr),
            max_bar1_range_atr=float(self.max_bar1_range_atr),
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

    def on_init(self) -> None:
        self.write_log(
            f"{self.strategy_id}@{self.strategy_version} initialized "
            f"(CID_011; detector=OPP19_REV@1.0.0; signal=5m; risk=1m)"
        )
        self.load_bar(30)

    def on_start(self) -> None:
        self.write_log(f"{self.strategy_id} started")

    def on_stop(self) -> None:
        self.write_log(
            f"{self.strategy_id} stopped | closed_trades={len(self._trade_log)}"
        )

    def on_bar(self, bar: BarData) -> None:
        self.bg.update_bar(bar)
        if self.pos != 0:
            self.cancel_all()
            self._manage_position(bar)
        self.put_event()

    def on_5min_bar(self, bar: BarData) -> None:
        self.am.update_bar(bar)
        if not self.am.inited:
            return
        if self.pos != 0:
            return

        context = self.context_engine.update(self.am, symbol=self.vt_symbol)
        self.detector.note_bar_datetime(bar.datetime)
        result = self.detector.detect(self.am, context)
        if result is not None:
            self._submit_stop_entry(result)

    def on_rollover_adjust(self, event: RolloverEvent) -> None:
        shift = float(event.price_shift)
        if abs(shift) < 1e-9:
            return
        for attr in (
            "entry_price",
            "stop_price",
            "target_price",
            "_entry_fill",
        ):
            value = float(getattr(self, attr, 0.0) or 0.0)
            if abs(value) > 1e-12:
                setattr(self, attr, value + shift)
        # OR levels in detector FSM also shift if active
        self.detector.adjust_levels(shift)
        self.write_log(f"on_rollover_adjust shift={shift}")

    def _submit_stop_entry(self, result) -> None:
        if result.entry is None or result.stop is None:
            return
        entry = float(result.entry)
        stop = float(result.stop)
        target = result.target
        if target is None:
            risk = abs(entry - stop)
            if risk <= 0:
                return
            if result.direction is PaafDirection.LONG:
                target = entry + float(self.risk_reward) * risk
            elif result.direction is PaafDirection.SHORT:
                target = entry - float(self.risk_reward) * risk
            else:
                return
        self.cancel_all()
        self.entry_price = entry
        self.stop_price = stop
        self.target_price = float(target)
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

        if self.hold_bars >= int(self.max_hold_bars):
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
