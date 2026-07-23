"""Unit smoke for OPP13 day-high double-top detector（OPP13_DT_MS_V0_1）."""
from __future__ import annotations

import unittest
from datetime import datetime

from strategies.paaf.detectors.opp13_day_high_double_top import (
    OPP13DayHighDoubleTopDetector,
)
from strategies.paaf.domain import Context, Direction, MarketState


class _FakeAm:
    def __init__(self, o: float, h: float, l: float, c: float):
        self.count = 1
        self.inited = True
        self.open = [o]
        self.high = [h]
        self.low = [l]
        self.close = [c]


class TestOpp13DayHighDoubleTopDetector(unittest.TestCase):
    def setUp(self) -> None:
        self.det = OPP13DayHighDoubleTopDetector(pricetick=1.0)
        self.ctx = Context(symbol="TEST", market_state=MarketState.UNKNOWN)

    def test_requires_bar_datetime(self) -> None:
        am = _FakeAm(100, 105, 99, 100)
        self.assertIsNone(self.det.detect(am, self.ctx))

    def test_first_test_then_lh_short(self) -> None:
        # Seed day levels at 09:06
        self.det.note_bar_datetime(datetime(2024, 1, 2, 9, 6))
        seed = _FakeAm(100, 110, 100, 105)
        self.assertIsNone(self.det.detect(seed, self.ctx))
        self.assertEqual(self.det._day_high, 110.0)

        # First quality touch → FIRST_TEST only
        # o=105 h=110 l=100 c=101 → range=10
        # upper=5 ≥ 4.5 and ≥ 4.0; close 101 ≤ 100+3 and ≤ 110-3.5=106.5
        self.det.note_bar_datetime(datetime(2024, 1, 2, 10, 0))
        first = _FakeAm(105.0, 110.0, 100.0, 101.0)
        self.assertIsNone(self.det.detect(first, self.ctx))
        self.assertEqual(self.det._fsm, "FIRST_TEST")
        self.assertEqual(self.det._first_test_high, 110.0)

        # LH second test within 10 ticks · quality short → SIGNAL
        # o=104 h=109 l=99 c=100 → range=10 upper=5; high LH vs 110
        self.det.note_bar_datetime(datetime(2024, 1, 2, 10, 5))
        second = _FakeAm(104.0, 109.0, 99.0, 100.0)
        result = self.det.detect(second, self.ctx)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.direction, Direction.SHORT)
        self.assertEqual(result.entry, 99.0)
        self.assertEqual(result.stop, 110.0)
        self.assertEqual(self.det._fsm, "IDLE")

    def test_pattern_state_roundtrip(self) -> None:
        self.det._day_high = 120.0
        self.det._day_low = 90.0
        self.det._fsm = "FIRST_TEST"
        self.det._first_test_high = 119.0
        self.det._bar_count = 3
        other = OPP13DayHighDoubleTopDetector()
        other.load_pattern_state(self.det.pattern_state)
        self.assertEqual(other._day_high, 120.0)
        self.assertEqual(other._fsm, "FIRST_TEST")
        self.assertEqual(other._first_test_high, 119.0)
        self.assertEqual(other._bar_count, 3)


if __name__ == "__main__":
    unittest.main()
