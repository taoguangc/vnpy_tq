"""Unit smoke for OPP13 day-boundary single-touch detector（OPP13_MS_V0_1）."""
from __future__ import annotations

import unittest
from datetime import datetime

from strategies.paaf.detectors.opp13_day_boundary_touch import (
    OPP13DayBoundaryTouchDetector,
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


class TestOpp13DayBoundaryTouchDetector(unittest.TestCase):
    def setUp(self) -> None:
        self.det = OPP13DayBoundaryTouchDetector(pricetick=1.0)
        self.ctx = Context(symbol="TEST", market_state=MarketState.UNKNOWN)

    def test_requires_bar_datetime(self) -> None:
        am = _FakeAm(100, 105, 99, 100)
        self.assertIsNone(self.det.detect(am, self.ctx))

    def test_short_day_high_touch(self) -> None:
        # Seed day levels at 09:06
        self.det.note_bar_datetime(datetime(2024, 1, 2, 9, 6))
        seed = _FakeAm(100, 110, 100, 105)
        self.assertIsNone(self.det.detect(seed, self.ctx))
        self.assertEqual(self.det._day_high, 110.0)

        # Later: touch day high with bearish rejection
        # high=110, o=109, c=104, l=103 → range=7 upper=1? wait
        # upper = h - max(o,c) = 110 - 109 = 1; need >= 0.45*7=3.15 FAIL
        # Better: o=108.5 h=110 l=100 c=101 → range=10 upper=1.5 fail
        # o=107 h=110 l=100 c=101 → range=10 upper=3 >=4.5? 3<4.5 fail
        # o=105 h=110 l=100 c=101 → range=10 upper=5 >=4.5; close 101 <= 100+3=103 OK
        self.det.note_bar_datetime(datetime(2024, 1, 2, 10, 0))
        am = _FakeAm(105.0, 110.0, 100.0, 101.0)
        result = self.det.detect(am, self.ctx)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.direction, Direction.SHORT)
        self.assertEqual(result.entry, 100.0)
        self.assertEqual(result.stop, 111.0)

    def test_pattern_state_roundtrip(self) -> None:
        self.det._day_high = 120.0
        self.det._day_low = 90.0
        other = OPP13DayBoundaryTouchDetector()
        other.load_pattern_state(self.det.pattern_state)
        self.assertEqual(other._day_high, 120.0)
        self.assertEqual(other._day_low, 90.0)


if __name__ == "__main__":
    unittest.main()
