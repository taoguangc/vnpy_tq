"""STRAT_TREND_BROOKS_SCALP_02@0.2.0 — positioning / capital-safety lineage.

Parent: @0.1.1（rollover）· morphology BROOKS_SCALP_FP@0.1.0 unchanged.
Adds risk-fraction sizing, hard max lots, cost-aware equity kill-switch.
Not for PnL optimization.
"""
from __future__ import annotations

from vnpy.trader.constant import Offset
from vnpy_ctastrategy import TradeData

from strategies.paaf.brooks_scalp_paaf_strategy_v011 import BrooksScalpPaafStrategyV011
from strategies.paaf.domain import Direction as PaafDirection


class BrooksScalpPaafStrategyV020(BrooksScalpPaafStrategyV011):
    """v0.2.0 orchestrator: v0.1.1 + capital-safety controls."""

    strategy_version = "0.2.0"

    # Positioning parameters（capital safety — not return tuning）
    sizing_mode = "RISK_FRACTION_OF_CAPITAL"  # or FIXED_LOTS
    risk_per_trade = 0.005  # 0.5% of equity estimate at entry
    hard_max_lots = 1
    capital_floor_ratio = 0.50  # halt new entries if equity_est <= ratio * initial

    parameters = [
        "ema_period",
        "atr_period",
        "trend_leg_atr",
        "pullback_atr",
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
        "fsm",
        "trend",
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
            f"(positioning lineage; parent=0.1.1; detector=BROOKS_SCALP_FP@0.1.0; "
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
        """One-sided commission + slippage in cash（matches CTA backtest formulas）."""
        vol = abs(float(volume))
        size = self._contract_size()
        turnover = float(price) * vol * size
        return turnover * self._engine_rate() + vol * size * self._engine_slippage()

    def _round_trip_cost_est(self, entry: float) -> float:
        """Conservative open+close cost at entry price（sizing gate）."""
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
            # stop loss cash + estimated round-trip friction per lot
            risk_per_lot = stop_dist * csize + self._round_trip_cost_est(entry)
            if risk_per_lot <= 0 or risk_cash <= 0:
                lots = 0
            else:
                lots = int(risk_cash // risk_per_lot)
        lots = max(0, min(int(self.hard_max_lots), lots))
        return lots

    def on_bar(self, bar) -> None:
        self._ensure_pricetick()
        self._bind_capital()
        self.am.update_bar(bar)
        if not self.am.inited:
            return

        self._refresh_kill_switch(bar)

        context = self.context_engine.update(self.am, symbol=self.vt_symbol)
        result = self.detector.detect(self.am, context)
        ps = self.detector.pattern_state
        self.fsm = str(ps.metadata.get("fsm", "IDLE"))
        self.trend = int(ps.metadata.get("trend", 0))

        if self.pos == 0:
            if self.trend == 0:
                self.cancel_all()
            if result is not None and not self.entries_halted:
                self._submit_stop_entry(result)
        else:
            self.cancel_all()
            if self.entries_halted:
                if self.pos != 0:
                    self._close_at_market(bar, "KILL_SWITCH")
            else:
                self._manage_position(bar)

        self.put_event()

    def _submit_stop_entry(self, result) -> None:
        if result.entry is None or result.stop is None or result.target is None:
            return
        self.cancel_all()
        self.entry_price = float(result.entry)
        self.stop_price = float(result.stop)
        self.target_price = float(result.target)
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
        # Always deduct fill friction（open and close）
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
