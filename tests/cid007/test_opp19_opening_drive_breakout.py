"""Unit smoke for OPP19 OD-Breakout detector（OPP19_MS_V0_1）."""
from __future__ import annotations

import unittest
from datetime import datetime

from strategies.paaf.detectors.opp19_opening_drive_breakout import (
    OPP19OpeningDriveBreakoutDetector,
    OdState,
)
from strategies.paaf.domain import Context, Direction, MarketState


class _FakeAm:
    def __init__(self, *, o, h, l, c, atr: float):
        self.open = [o]
        self.high = [h]
        self.low = [l]
        self.close = [c]
        self._atr = atr
        self.inited = True
        self.count = 30

    def atr(self, period: int) -> float:
        del period
        return self._atr


class TestOpp19OpeningDriveBreakout(unittest.TestCase):
    def setUp(self) -> None:
        self.det = OPP19OpeningDriveBreakoutDetector(opening_drive_bars=3)
        self.ctx = Context(symbol="TEST", market_state=MarketState.UNKNOWN)

    def test_collect_then_long_breakout(self) -> None:
        # Start session collect at 09:00
        self.det.note_bar_datetime(datetime(2024, 1, 2, 9, 0))
        am0 = _FakeAm(o=100, h=101, l=99, c=100.5, atr=2.0)
        self.assertIsNone(self.det.detect(am0, self.ctx))
        self.assertEqual(self.det._fsm, OdState.COLLECTING)

        # Collect bar 2
        self.det.note_bar_datetime(datetime(2024, 1, 2, 9, 5))
        am1 = _FakeAm(o=100, h=102, l=98.5, c=101, atr=2.0)
        self.assertIsNone(self.det.detect(am1, self.ctx))

        # Collect bar 3 → RANGE_SET（range=102-98.5=3.5 > 0.4）
        self.det.note_bar_datetime(datetime(2024, 1, 2, 9, 10))
        am2 = _FakeAm(o=100, h=102, l=98.5, c=101, atr=2.0)
        self.assertIsNone(self.det.detect(am2, self.ctx))
        self.assertEqual(self.det._fsm, OdState.RANGE_SET)

        # Breakout long: strong bar close > OR high 102
        self.det.note_bar_datetime(datetime(2024, 1, 2, 9, 15))
        # range=6 body=5.5 ratio≈0.92; atr=2 → strong; close=107 > 102
        am3 = _FakeAm(o=101.5, h=108, l=101, c=107, atr=2.0)
        result = self.det.detect(am3, self.ctx)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.direction, Direction.LONG)
        self.assertEqual(result.entry, 108.0)
        self.assertEqual(result.stop, 101.0)

    def test_ignores_without_bar_datetime(self) -> None:
        am = _FakeAm(o=100, h=101, l=99, c=100, atr=2.0)
        self.assertIsNone(self.det.detect(am, self.ctx))


if __name__ == "__main__":
    unittest.main()
