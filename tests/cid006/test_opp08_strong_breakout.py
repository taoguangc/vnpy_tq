"""Unit smoke for OPP08 strong-breakout detector（OPP08_MS_V0_1）."""
from __future__ import annotations

import unittest

from strategies.paaf.adapters import PaafBar
from strategies.paaf.detectors.opp08_strong_breakout import OPP08StrongBreakoutDetector
from strategies.paaf.domain import Context, Direction, MarketState


class _FakeAm:
    def __init__(self, bars: list[PaafBar], *, atr: float, ema: float):
        self._bars = bars
        self._atr = atr
        self._ema = ema
        self.count = len(bars)
        self.inited = True
        self.close = [b.close for b in bars]
        self.open = [b.open for b in bars]
        self.high = [b.high for b in bars]
        self.low = [b.low for b in bars]

    def atr(self, period: int) -> float:
        del period
        return self._atr

    def ema(self, period: int) -> float:
        del period
        return self._ema


def _bar(o: float, h: float, l: float, c: float) -> PaafBar:
    return PaafBar(open=o, high=h, low=l, close=c)


class TestOpp08StrongBreakoutDetector(unittest.TestCase):
    def setUp(self) -> None:
        self.det = OPP08StrongBreakoutDetector()
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

    def test_long_strong_breakout(self) -> None:
        # atr=2 → need range > 2; body/range >= 0.6
        # prev high=100; signal o=100 h=106 l=99.5 c=105.5 → range=6.5 body=5.5
        # ema=100; close > ema and > prev.high
        prev = _bar(99.0, 100.0, 98.0, 99.5)
        signal = _bar(100.0, 106.0, 99.5, 105.5)
        pad = [_bar(100, 101, 99, 100) for _ in range(20)]
        am = _FakeAm(pad + [prev, signal], atr=2.0, ema=100.0)
        result = self._detect(am)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.direction, Direction.LONG)
        self.assertEqual(result.entry, 106.0)
        self.assertEqual(result.stop, 99.5)

    def test_ignores_context(self) -> None:
        self.assertTrue(callable(self.det.detect))


if __name__ == "__main__":
    unittest.main()
