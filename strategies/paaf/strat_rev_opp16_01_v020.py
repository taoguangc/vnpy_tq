"""STRAT_REV_OPP16_01@0.2.0 — positioning / capital-safety lineage.

Parent: @0.1.1（adapter repair）· morphology OPP16@1.0.0 unchanged.
Adds risk-fraction sizing, hard max lots, cost-aware equity kill-switch.
Signal remains 5m（BarGenerator）；kill / exits on 1m.

≠ PnL optimization · ≠ H_EDGE reopen · ≠ mutate @0.1.1 Verified bytes.
"""

from __future__ import annotations

from vnpy.trader.constant import Offset
from vnpy_ctastrategy import TradeData

from strategies.paaf.domain import Direction as PaafDirection
from strategies.paaf.strat_rev_opp16_01_v011 import StratRevOpp1601StrategyV011


class StratRevOpp1601StrategyV020(StratRevOpp1601StrategyV011):
    """v0.2.0 orchestrator: v0.1.1 + capital-safety controls."""

    strategy_version = "0.2.0"

    sizing_mode = "RISK_FRACTION_OF_CAPITAL"  # or FIXED_LOTS
    risk_per_trade = 0.005  # 0.5% of equity estimate at entry
    hard_max_lots = 1
    capital_floor_ratio = 0.50

    parameters = [
        "body_ratio",
        "risk_reward",
        "max_hold_bars",
        "fixed_size",
        "sizing_mode",
        "risk_per_trade",
        "hard_max_lots",
        "capital_floor_ratio",
    ]

    entries_halted = False
    equity_est = 0.0
    initial_capital = 0.0
    skip_zero_lot = 0
    kill_events = 0

    variables = [
        "hold_bars",
        "entries_halted",
        "equity_est",
        "skip_zero_lot",
        "kill_events",
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self._capital_gate_log: list[dict] = []
        self._sizing_bound = False

    def on_init(self) -> None:
        self.write_log(
            f"{self.strategy_id}@{self.strategy_version} initialized "
            f"(CID_003 positioning lineage; parent=0.1.1; detector=OPP16@1.0.0; "
            f"sizing_mode={self.sizing_mode}; risk_per_trade={self.risk_per_trade}; "
            f"hard_max_lots={self.hard_max_lots}; capital_floor_ratio={self.capital_floor_ratio})"
        )
        self.load_bar(30)

    def on_start(self) -> None:
        self._bind_capital()
        self.write_log(
            f"{self.strategy_id}@{self.strategy_version} started | "
            f"initial_capital={self.initial_capital:.2f} equity_est={self.equity_est:.2f}"
        )

    def _bind_capital(self) -> None:
        if self._sizing_bound:
            return
        capital = float(getattr(self.cta_engine, "capital", 0) or 0)
        if capital <= 0:
            capital = 200_000.0
        self.initial_capital = capital
        self.equity_est = capital
        self.entries_halted = False
        self._sizing_bound = True

    def _contract_size(self) -> float:
        return float(getattr(self.cta_engine, "size", 1) or 1)

    def _engine_rate(self) -> float:
        return float(getattr(self.cta_engine, "rate", 0) or 0)

    def _engine_slippage(self) -> float:
        return float(getattr(self.cta_engine, "slippage", 0) or 0)

    def _fill_cost(self, price: float, volume: float) -> float:
        vol = abs(float(volume))
        size = self._contract_size()
        turnover = float(price) * vol * size
        return turnover * self._engine_rate() + vol * size * self._engine_slippage()

    def _round_trip_cost_est(self, entry: float) -> float:
        return 2.0 * self._fill_cost(entry, 1.0)

    def _capital_floor(self) -> float:
        return float(self.initial_capital) * float(self.capital_floor_ratio)

    def _refresh_kill_switch(self, bar) -> None:
        self._bind_capital()
        floor = self._capital_floor()
        if (not self.entries_halted) and self.equity_est <= floor:
            self.entries_halted = True
            self.kill_events += 1
            self._capital_gate_log.append(
                {
                    "event": "EQUITY_KILL_SWITCH",
                    "datetime": getattr(bar, "datetime", None),
                    "equity_est": self.equity_est,
                    "floor": floor,
                }
            )
            self.write_log(
                f"EQUITY_KILL_SWITCH equity_est={self.equity_est:.2f} "
                f"floor={floor:.2f} — flatten + new entries halted"
            )
            self.cancel_all()
            if self.pos > 0:
                self.sell(bar.close_price, abs(self.pos))
                self._record_exit(bar, "KILL_SWITCH")
            elif self.pos < 0:
                self.cover(bar.close_price, abs(self.pos))
                self._record_exit(bar, "KILL_SWITCH")

    def _compute_lots(self, entry: float, stop: float) -> int:
        mode = str(self.sizing_mode or "FIXED_LOTS").upper()
        if mode == "FIXED_LOTS":
            lots = int(self.fixed_size)
        else:
            stop_dist = abs(float(entry) - float(stop))
            csize = self._contract_size()
            risk_cash = max(0.0, float(self.equity_est) * float(self.risk_per_trade))
            risk_per_lot = stop_dist * csize + self._round_trip_cost_est(entry)
            if risk_per_lot <= 0 or risk_cash <= 0:
                lots = 0
            else:
                lots = int(risk_cash // risk_per_lot)
        lots = max(0, min(int(self.hard_max_lots), lots))
        return lots

    def on_bar(self, bar) -> None:
        self._bind_capital()
        self.bg.update_bar(bar)
        self._refresh_kill_switch(bar)
        if self.pos != 0:
            self.cancel_all()
            if self.entries_halted:
                self._close_at_market(bar, "KILL_SWITCH")
            else:
                self._manage_position(bar)
        self.put_event()

    def on_5min_bar(self, bar) -> None:
        self.am.update_bar(bar)
        if not self.am.inited:
            return
        if self.pos != 0:
            return
        if self.entries_halted:
            return

        context = self.context_engine.update(self.am, symbol=self.vt_symbol)
        result = self.detector.detect(self.am, context)
        if result is not None:
            self._submit_stop_entry(result)

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
        lots = self._compute_lots(self.entry_price, self.stop_price)
        if lots <= 0:
            self.skip_zero_lot += 1
            self._capital_gate_log.append(
                {
                    "event": "SKIP_ZERO_LOT",
                    "entry": self.entry_price,
                    "stop": self.stop_price,
                    "equity_est": self.equity_est,
                    "contract_size": self._contract_size(),
                }
            )
            return
        if result.direction is PaafDirection.LONG:
            self.buy(self.entry_price, lots, stop=True)
        elif result.direction is PaafDirection.SHORT:
            self.short(self.entry_price, lots, stop=True)
        self.write_log(
            f"signal {result.direction.value} lots={lots} entry={self.entry_price} "
            f"stop={self.stop_price} target={self.target_price} "
            f"reason={result.reason} equity_est={self.equity_est:.2f}"
        )

    def on_trade(self, trade: TradeData) -> None:
        self._bind_capital()
        self.equity_est = float(self.equity_est) - self._fill_cost(
            float(trade.price), float(trade.volume)
        )
        if trade.offset != Offset.OPEN:
            entry = float(self._entry_fill or 0.0)
            side = int(self._entry_side or 0)
            if entry > 0 and side != 0:
                signed = 1.0 if side > 0 else -1.0
                vol = abs(float(trade.volume))
                gross = (float(trade.price) - entry) * signed * vol * self._contract_size()
                self.equity_est = float(self.equity_est) + float(gross)
        super().on_trade(trade)
