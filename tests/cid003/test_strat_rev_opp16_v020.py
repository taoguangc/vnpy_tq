"""Unit tests for StratRevOpp1601StrategyV020 capital-safety sizing."""

from __future__ import annotations

import unittest

from strategies.paaf.strat_rev_opp16_01_v020 import StratRevOpp1601StrategyV020


class _Eng:
    capital = 200_000
    size = 100
    rate = 0.0
    slippage = 0.0


class TestStratRevOpp1601StrategyV020(unittest.TestCase):
    def setUp(self) -> None:
        self.s = StratRevOpp1601StrategyV020(_Eng(), "t", "i.DCE", {})
        self.s._bind_capital()

    def test_version_and_defaults(self) -> None:
        self.assertEqual(self.s.strategy_version, "0.2.0")
        self.assertEqual(self.s.strategy_id, "STRAT_REV_OPP16_01")
        self.assertEqual(self.s.sizing_mode, "RISK_FRACTION_OF_CAPITAL")
        self.assertEqual(self.s.hard_max_lots, 1)
        self.assertEqual(self.s.capital_floor_ratio, 0.5)
        self.assertIn("risk_per_trade", self.s.parameters)
        self.assertIn("hard_max_lots", self.s.parameters)

    def test_risk_fraction_zero_when_stop_too_wide(self) -> None:
        self.assertEqual(self.s._compute_lots(800.0, 700.0), 0)

    def test_risk_fraction_hard_cap(self) -> None:
        self.assertEqual(self.s._compute_lots(800.0, 799.0), 1)

    def test_risk_fraction_includes_friction(self) -> None:
        self.s.cta_engine.slippage = 1.0
        self.assertEqual(self.s._compute_lots(800.0, 799.0), 1)
        self.assertEqual(self.s._compute_lots(800.0, 791.0), 0)

    def test_fixed_lots_mode(self) -> None:
        self.s.sizing_mode = "FIXED_LOTS"
        self.s.fixed_size = 1
        self.assertEqual(self.s._compute_lots(800.0, 700.0), 1)

    def test_kill_switch_trips_at_floor(self) -> None:
        class Bar:
            datetime = None
            close_price = 800.0

        self.s.equity_est = 100_000.0
        self.s.pos = 0
        logs: list[str] = []
        self.s.write_log = logs.append  # type: ignore[method-assign]
        self.s.cancel_all = lambda: None  # type: ignore[method-assign]
        self.s._refresh_kill_switch(Bar())
        self.assertTrue(self.s.entries_halted)
        self.assertEqual(self.s.kill_events, 1)
        self.assertEqual(self.s._capital_gate_log[-1]["event"], "EQUITY_KILL_SWITCH")

    def test_parent_versions_untouched(self) -> None:
        from strategies.paaf.strat_rev_opp16_01 import StratRevOpp1601Strategy
        from strategies.paaf.strat_rev_opp16_01_v011 import StratRevOpp1601StrategyV011

        self.assertEqual(StratRevOpp1601Strategy.strategy_version, "0.1.0")
        self.assertEqual(StratRevOpp1601StrategyV011.strategy_version, "0.1.1")


if __name__ == "__main__":
    unittest.main()
