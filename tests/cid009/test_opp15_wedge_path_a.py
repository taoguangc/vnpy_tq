"""Unit smoke for OPP15 wedge Path-A detector（OPP15_MS_V0_1）."""
from __future__ import annotations

import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from strategies.paaf.detectors.opp15_wedge_path_a import (
    OPP15WedgePathADetector,
    WedgeState,
)
from strategies.paaf.domain import Context, Direction, MarketState


class _FakeAm:
    def __init__(self, bars: list[tuple[float, float, float, float]], *, atr: float):
        # bars: (o,h,l,c) oldest→newest
        self._bars = bars
        self._atr = atr
        self.count = len(bars)
        self.size = max(len(bars), 200)
        self.inited = True
        self.open = self._series(0)
        self.high = self._series(1)
        self.low = self._series(2)
        self.close = self._series(3)

    def _series(self, idx: int):
        class _S:
            def __init__(self, vals):
                self._vals = vals

            def __getitem__(self, i):
                return self._vals[i]

        vals = [b[idx] for b in self._bars]
        return _S(vals)

    def atr(self, period: int) -> float:
        del period
        return self._atr


class TestOpp15WedgePathADetector(unittest.TestCase):
    def setUp(self) -> None:
        self.det = OPP15WedgePathADetector()
        self.ctx = Context(symbol="TEST", market_state=MarketState.UNKNOWN)
        self.t0 = datetime(2024, 1, 2, 10, 0)

    def test_requires_bar_datetime(self) -> None:
        am = _FakeAm([(100, 101, 99, 100)] * 20, atr=2.0)
        self.assertIsNone(self.det.detect(am, self.ctx))

    def test_path_a_short_after_arm(self) -> None:
        # Pad so count>=7; last two lows for trigger; signal bar strong bearish
        pad = [(100.0, 101.0, 99.0, 100.0)] * 17
        # lows at -3,-2 set trigger = min(98, 97)=97; signal closes below
        older = (100.0, 102.0, 98.0, 99.0)
        newer = (100.0, 101.0, 97.0, 98.0)
        # strong short: atr=2 → range>2; o=100 h=100.5 l=94 c=95 → range=6.5 body=5
        signal = (100.0, 100.5, 94.0, 95.0)
        am = _FakeAm(pad + [older, newer, signal], atr=2.0)

        with patch(
            "strategies.paaf.detectors.opp15_wedge_path_a.scan_latest_bearish_wedge",
            return_value={
                "status": "wedge_valid:hh3",
                "p3_idx": 10,
                "p3_high": 105.0,
                "alpha": 0.9,
            },
        ), patch(
            "strategies.paaf.detectors.opp15_wedge_path_a.scan_latest_bullish_wedge",
            return_value={"status": "no_structure"},
        ):
            self.det.note_bar_datetime(self.t0)
            am_arm = _FakeAm(pad + [older, newer, (100.0, 101.0, 99.0, 100.0)], atr=2.0)
            self.assertIsNone(self.det.detect(am_arm, self.ctx))
            self.assertEqual(self.det._fsm, WedgeState.ARMED)
            self.assertEqual(self.det._direction, -1)

            self.det.note_bar_datetime(self.t0 + timedelta(minutes=5))
            result = self.det.detect(am, self.ctx)

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.direction, Direction.SHORT)
        self.assertEqual(result.entry, 94.0)
        self.assertEqual(result.stop, 106.0)  # p3 + tick
        self.assertEqual(self.det._fsm, WedgeState.IDLE)

    def test_pattern_state_roundtrip(self) -> None:
        self.det._fsm = WedgeState.ARMED
        self.det._direction = -1
        self.det._p3_price = 100.0
        self.det._trigger_line = 98.0
        self.det._arm_time = self.t0
        state = self.det.pattern_state
        other = OPP15WedgePathADetector()
        other.load_pattern_state(state)
        self.assertEqual(other._fsm, WedgeState.ARMED)
        self.assertEqual(other._p3_price, 100.0)


if __name__ == "__main__":
    unittest.main()
