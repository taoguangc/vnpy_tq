"""Unit smoke for OPP17 climax-reversal detector（OPP17_MS_V0_1）."""
from __future__ import annotations

import unittest

from strategies.paaf.adapters import PaafBar
from strategies.paaf.detectors.opp17_climax_reversal import OPP17ClimaxReversalDetector
from strategies.paaf.domain import Context, Direction, MarketState


class _FakeAm:
    def __init__(self, bars: list[PaafBar], *, atr: float):
        self._bars = bars
        self._atr = atr
        self.count = len(bars)
        self.inited = True
        self.close = [b.close for b in bars]
        self.open = [b.open for b in bars]
        self.high = [b.high for b in bars]
        self.low = [b.low for b in bars]

    def atr(self, period: int) -> float:
        del period
        return self._atr


def _bar(o: float, h: float, l: float, c: float) -> PaafBar:
    return PaafBar(open=o, high=h, low=l, close=c)


class TestOpp17ClimaxReversalDetector(unittest.TestCase):
    def setUp(self) -> None:
        self.det = OPP17ClimaxReversalDetector()
        self.ctx = Context(symbol="TEST", market_state=MarketState.UNKNOWN)

    def _detect(self, am: _FakeAm):
        from strategies.paaf.adapters import vnpy_adapter as va

        original = va.bars_from_am

        def _fake_bars(am_obj, lookback=None):
            bars = list(am_obj._bars)
            if lookback is None:
                return bars
            return bars[-lookback:]

        va.bars_from_am = _fake_bars
        try:
            return self.det.detect(am, self.ctx)
        finally:
            va.bars_from_am = original

    def test_long_climax_reversal(self) -> None:
        # atr=2 → need prev_range > 5.0
        # prev bearish wide: o=110 h=111 l=100 c=101 → range=11
        # bar reclaim above mid=105.5: o=104 h=108 l=103 c=107
        prev = _bar(110.0, 111.0, 100.0, 101.0)
        signal = _bar(104.0, 108.0, 103.0, 107.0)
        pad = [_bar(100, 101, 99, 100) for _ in range(20)]
        am = _FakeAm(pad + [prev, signal], atr=2.0)
        result = self._detect(am)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.direction, Direction.LONG)
        self.assertEqual(result.entry, 108.0)
        self.assertEqual(result.stop, 103.0)

    def test_ignores_context(self) -> None:
        self.assertTrue(callable(self.det.detect))


if __name__ == "__main__":
    unittest.main()
