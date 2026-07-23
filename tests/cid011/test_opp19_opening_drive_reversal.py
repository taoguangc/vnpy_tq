"""Unit smoke for OPP19 OD-Reversal detector（OPP19_REV_MS_V0_1）."""
from __future__ import annotations

import unittest
from datetime import datetime

from strategies.paaf.detectors.opp19_opening_drive_reversal import (
    OPP19OpeningDriveReversalDetector,
    RevState,
)
from strategies.paaf.domain import Context, Direction, MarketState


class _FakeAm:
    def __init__(self, o: float, h: float, l: float, c: float, *, atr: float = 2.0):
        self.count = 20
        self.inited = True
        self.open = [o]
        self.high = [h]
        self.low = [l]
        self.close = [c]
        self._atr = atr

    def atr(self, period: int) -> float:
        del period
        return self._atr


class TestOpp19OpeningDriveReversalDetector(unittest.TestCase):
    def setUp(self) -> None:
        self.det = OPP19OpeningDriveReversalDetector()
        self.ctx = Context(symbol="TEST", market_state=MarketState.UNKNOWN)

    def test_requires_bar_datetime(self) -> None:
        am = _FakeAm(100, 105, 99, 104)
        self.assertIsNone(self.det.detect(am, self.ctx))

    def test_fade_down_bar1_long(self) -> None:
        # Session open 09:00 — DOWN bar1 (body/range >= 0.45)
        # o=105 h=106 l=100 c=100.5 → range=6 body=4.5 ratio=0.75 DOWN
        self.det.note_bar_datetime(datetime(2024, 1, 2, 9, 0))
        am1 = _FakeAm(105.0, 106.0, 100.0, 100.5, atr=4.0)
        self.assertIsNone(self.det.detect(am1, self.ctx))
        self.assertEqual(self.det._fsm, RevState.BAR1_SET)
        self.assertEqual(self.det._bar1_shape, "DOWN")

        # Bar2 reverse long: bullish through mid
        # mid=(106+100)/2=103; o=102 h=108 l=101.5 c=107
        # bar1_range/atr = 6/4 = 1.5 ∈ [0.3, 2.5]
        self.det.note_bar_datetime(datetime(2024, 1, 2, 9, 5))
        am2 = _FakeAm(102.0, 108.0, 101.5, 107.0, atr=4.0)
        result = self.det.detect(am2, self.ctx)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.direction, Direction.LONG)
        self.assertEqual(result.entry, 108.0)
        self.assertEqual(result.stop, 101.5)
        self.assertEqual(self.det._fsm, RevState.IDLE)

    def test_pattern_state_roundtrip(self) -> None:
        self.det._fsm = RevState.BAR1_SET
        self.det._bar1_shape = "UP"
        self.det._bar1_mid = 100.0
        other = OPP19OpeningDriveReversalDetector()
        other.load_pattern_state(self.det.pattern_state)
        self.assertEqual(other._fsm, RevState.BAR1_SET)
        self.assertEqual(other._bar1_shape, "UP")


if __name__ == "__main__":
    unittest.main()
