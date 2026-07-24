"""Unit smoke for SMC VWAP Z-score long detector."""
from __future__ import annotations

import unittest

from strategies.paaf.detectors.smc_zscore_long import SMCZScoreLongDetector
from strategies.paaf.domain import Context, Direction, MarketState


class _FakeAm:
    def __init__(self, closes, highs=None, lows=None):
        n = len(closes)
        self.count = n
        self.inited = True
        self.close = list(closes)
        self.high = list(highs if highs is not None else [c + 1 for c in closes])
        self.low = list(lows if lows is not None else [c - 1 for c in closes])
        self.open = list(closes)


class TestSMCZScoreLongDetector(unittest.TestCase):
    def setUp(self) -> None:
        self.det = SMCZScoreLongDetector(
            zscore_threshold=2.5,
            vwap_length=20,
            stop_lookback=5,
            stop_buffer=2.0,
            min_risk_ticks=5.0,
            pricetick=1.0,
        )
        self.ctx = Context(symbol="TEST", market_state=MarketState.UNKNOWN)

    def test_requires_vwap(self) -> None:
        am = _FakeAm([100.0] * 20)
        self.assertIsNone(self.det.detect(am, self.ctx))

    def test_oversold_long(self) -> None:
        # Flat history around 100, last bar deeply below vwap=100
        closes = [100.0] * 19 + [85.0]
        highs = [101.0] * 19 + [95.0]
        lows = [99.0] * 19 + [84.0]
        am = _FakeAm(closes, highs, lows)
        self.det.note_session_vwap(100.0)
        result = self.det.detect(am, self.ctx)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.direction, Direction.LONG)
        self.assertEqual(result.entry, 95.0)


if __name__ == "__main__":
    unittest.main()
