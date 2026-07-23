"""Unit smoke for OPP02 EMA-pullback detector（OPP02_MS_V0_1）."""
from __future__ import annotations

import unittest

from strategies.paaf.adapters import PaafBar
from strategies.paaf.detectors.opp02_ema_pullback import OPP02EmaPullbackDetector
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


class TestOpp02EmaPullbackDetector(unittest.TestCase):
    def setUp(self) -> None:
        self.det = OPP02EmaPullbackDetector()
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

    def test_long_ema_pullback(self) -> None:
        # atr=2 → touch_band=2; ema=100
        # close>ema · low touches · bullish · upper wick < 0.45*range
        # o=100.5 h=102 l=99.5 c=101.5 → range=2.5 body=1.0 ratio=0.4
        # upper wick = 102-101.5=0.5 < 2.5*0.45
        signal = _bar(100.5, 102.0, 99.5, 101.5)
        pad = [_bar(100, 101, 99, 100) for _ in range(20)]
        am = _FakeAm(pad + [signal], atr=2.0, ema=100.0)
        result = self._detect(am)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.direction, Direction.LONG)
        self.assertEqual(result.entry, 102.0)
        self.assertEqual(result.stop, 99.5)

    def test_short_ema_pullback(self) -> None:
        signal = _bar(99.5, 100.5, 98.0, 98.5)
        pad = [_bar(100, 101, 99, 100) for _ in range(20)]
        am = _FakeAm(pad + [signal], atr=2.0, ema=100.0)
        result = self._detect(am)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.direction, Direction.SHORT)
        self.assertEqual(result.entry, 98.0)
        self.assertEqual(result.stop, 100.5)

    def test_ignores_context(self) -> None:
        self.assertTrue(callable(self.det.detect))


if __name__ == "__main__":
    unittest.main()
