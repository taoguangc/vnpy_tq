"""Unit smoke for SMC bullish Order-Block detector（SMC_OB_LONG_MS_V0_1）."""
from __future__ import annotations

import unittest

from strategies.paaf.detectors.smc_order_block_long import SMCOrderBlockLongDetector
from strategies.paaf.domain import Context, Direction, MarketState


class _FakeAm:
    def __init__(self, opens, highs, lows, closes):
        n = len(closes)
        self.count = n
        self.inited = True
        self.open = list(opens)
        self.high = list(highs)
        self.low = list(lows)
        self.close = list(closes)


def _flat_history(n: int, px: float = 100.0):
    return [px] * n, [px + 1] * n, [px - 1] * n, [px] * n


class TestSMCOrderBlockLongDetector(unittest.TestCase):
    def setUp(self) -> None:
        self.det = SMCOrderBlockLongDetector(
            smc_pool_bars=12,
            smc_min_bars=16,
            ob_stop_buffer=2.0,
            pricetick=1.0,
        )
        self.ctx = Context(symbol="TEST", market_state=MarketState.UNKNOWN)

    def test_sweep_then_reclaim_long(self) -> None:
        # 14 flat bars as pool base, then sweep at index -2, current reclaim
        # Build: 14 bars at 100, then sweep bar (low=90, close=101, high=105),
        # then reclaim bar close>ob_high
        n_pool = 12
        # need pool+2 = 14 before current; use 16 total min
        opens = [100.0] * 14
        highs = [101.0] * 14
        lows = [99.0] * 14
        closes = [100.0] * 14
        # sweep bar will be [-2] after we append current — so append sweep then current
        opens.append(100.0)  # sweep open
        highs.append(105.0)
        lows.append(90.0)  # below pool min 99
        closes.append(101.0)  # close back above pool min
        # current reclaim bar
        opens.append(102.0)
        highs.append(110.0)
        lows.append(101.0)
        closes.append(108.0)  # > ob_high=105

        am = _FakeAm(opens, highs, lows, closes)
        # First detect: may set OB from sweep and also reclaim on same bar
        result = self.det.detect(am, self.ctx)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.direction, Direction.LONG)
        self.assertEqual(result.entry, 110.0)
        self.assertEqual(result.stop, 98.0)  # min(100,101)=100? ob_low=min(100,101)=100 → 100-2=98
        # wait: sweep open=100 close=101 → ob_low=100, stop=98. Yes.
        self.assertEqual(self.det._fsm, "IDLE")

    def test_pattern_state_roundtrip(self) -> None:
        self.det._fsm = "OB_SET"
        self.det._ob_low = 90.0
        self.det._ob_high = 100.0
        other = SMCOrderBlockLongDetector()
        other.load_pattern_state(self.det.pattern_state)
        self.assertEqual(other._fsm, "OB_SET")
        self.assertEqual(other._ob_low, 90.0)


if __name__ == "__main__":
    unittest.main()
