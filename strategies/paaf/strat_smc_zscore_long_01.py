"""STRAT_SMC_ZSCORE_LONG_01@0.1.0 — PAAF orchestration for VWAP Z-score long.

CID_014 · Candidate Identity Freeze target.
Strategy owns 1m session VWAP ledger; morphology in SMCZScoreLongDetector.
Signal on 5m; stop/target/time-stop on 1m.
"""

from __future__ import annotations

from datetime import time
from zoneinfo import ZoneInfo

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
from strategies.paaf.detectors.smc_zscore_long import (
    DEFAULT_MIN_RISK_TICKS,
    DEFAULT_STOP_BUFFER,
    DEFAULT_STOP_LOOKBACK,
    DEFAULT_VWAP_LENGTH,
    DEFAULT_ZSCORE_THRESHOLD,
    SMCZScoreLongDetector,
)
from strategies.paaf.domain import Direction as PaafDirection
from strategies.paaf.engines.context_engine import ContextEngine

CST = ZoneInfo("Asia/Shanghai")
_VWAP_RESET = time(21, 0)


class StratSmcZscoreLong01Strategy(CtaTemplate):
    """CID_014 orchestrator v0.1.0 — no pattern logic inlined."""

    author = "vnpy_tq"

    strategy_id = "STRAT_SMC_ZSCORE_LONG_01"
    strategy_version = "0.1.0"

    zscore_threshold = DEFAULT_ZSCORE_THRESHOLD
    vwap_length = DEFAULT_VWAP_LENGTH
    stop_lookback = DEFAULT_STOP_LOOKBACK
    stop_buffer = DEFAULT_STOP_BUFFER
    min_risk_ticks = DEFAULT_MIN_RISK_TICKS
    risk_reward = 1.0
    max_hold_bars = 50
    fixed_size = 1

    parameters = [
        "zscore_threshold",
        "vwap_length",
        "stop_lookback",
        "stop_buffer",
        "min_risk_ticks",
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
        self.detector = SMCZScoreLongDetector(
            zscore_threshold=float(self.zscore_threshold),
            vwap_length=int(self.vwap_length),
            stop_lookback=int(self.stop_lookback),
            stop_buffer=float(self.stop_buffer),
            min_risk_ticks=float(self.min_risk_ticks),
        )
        self._vwap_cum_volume = 0.0
        self._vwap_cum_turnover = 0.0
        self._session_vwap = 0.0

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
            f"(CID_014; detector=SMC_ZSCORE_LONG@1.0.0; signal=5m; risk=1m)"
        )
        self.load_bar(30)

    def on_start(self) -> None:
        tick = float(self.get_pricetick() or 1.0)
        self.detector.set_pricetick(tick)
        self.write_log(f"{self.strategy_id} started pricetick={tick}")

    def on_stop(self) -> None:
        self.write_log(
            f"{self.strategy_id} stopped | closed_trades={len(self._trade_log)}"
        )

    def on_bar(self, bar: BarData) -> None:
        self._update_session_vwap(bar)
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

        self.detector.note_session_vwap(self._session_vwap)
        context = self.context_engine.update(self.am, symbol=self.vt_symbol)
        result = self.detector.detect(self.am, context)
        if result is not None:
            self._submit_stop_entry(result)

    def _update_session_vwap(self, bar: BarData) -> None:
        dt = bar.datetime
        if dt.tzinfo is None:
            local = dt.replace(tzinfo=CST)
        else:
            local = dt.astimezone(CST)
        t = local.time().replace(second=0, microsecond=0)
        if t == _VWAP_RESET:
            self._vwap_cum_volume = 0.0
            self._vwap_cum_turnover = 0.0
            self._session_vwap = 0.0

        vol = float(bar.volume or 0.0)
        if vol <= 0:
            return
        turnover = float(bar.turnover) if bar.turnover else float(bar.close_price) * vol
        self._vwap_cum_volume += vol
        self._vwap_cum_turnover += turnover
        if self._vwap_cum_volume > 0:
            self._session_vwap = self._vwap_cum_turnover / self._vwap_cum_volume

    def on_rollover_adjust(self, event: RolloverEvent) -> None:
        shift = float(event.price_shift)
        if abs(shift) < 1e-9:
            return
        for attr in (
            "entry_price",
            "stop_price",
            "target_price",
            "_entry_fill",
            "_session_vwap",
            "_vwap_cum_turnover",
        ):
            value = float(getattr(self, attr, 0.0) or 0.0)
            if abs(value) > 1e-12:
                # turnover shift approximate: add shift * volume when volume>0
                if attr == "_vwap_cum_turnover" and self._vwap_cum_volume > 0:
                    setattr(self, attr, value + shift * self._vwap_cum_volume)
                elif attr != "_vwap_cum_turnover":
                    setattr(self, attr, value + shift)
        if self._vwap_cum_volume > 0:
            self._session_vwap = self._vwap_cum_turnover / self._vwap_cum_volume
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
