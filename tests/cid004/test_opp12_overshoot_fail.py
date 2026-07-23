"""Unit smoke for OPP12 overshoot-fail detector（OPP12_MS_V0_1）."""
from __future__ import annotations

import unittest
from types import SimpleNamespace

from strategies.paaf.adapters import PaafBar
from strategies.paaf.detectors.opp12_overshoot_fail import OPP12OvershootFailDetector
from strategies.paaf.domain import Context, Direction, MarketState


class _FakeAm:
    def __init__(self, bars: list[PaafBar], *, atr: float, ema: float):
        self._bars = bars
        self._atr = atr
        self._ema = ema
        self.count = len(bars)
        self.inited = True

    def atr(self, period: int) -> float:
        del period
        return self._atr

    def ema(self, period: int) -> float:
        del period
        return self._ema


def _bar(o: float, h: float, l: float, c: float) -> PaafBar:
    return PaafBar(open=o, high=h, low=l, close=c)


class TestOpp12OvershootFailDetector(unittest.TestCase):
    def setUp(self) -> None:
        self.det = OPP12OvershootFailDetector()
        self.ctx = Context(symbol="TEST", market_state=MarketState.UNKNOWN)

    def test_long_overshoot_fail(self) -> None:
        # depth = ema-close = 100-97 = 3; atr=2 → band [2.4, 5.0]
        # bull reversal: long lower shadow, close near high, body ok, close>open
        signal = _bar(96.0, 98.0, 94.0, 97.5)
        pad = [_bar(100, 101, 99, 100) for _ in range(25)]
        am = _FakeAm(pad + [signal], atr=2.0, ema=100.0)
        # Monkeypatch bars_from_am via am protocol used by detector — detector
        # calls bars_from_am(am, need) which reads am arrays. Provide array attrs.
        am.close = [b.close for b in am._bars]
        am.open = [b.open for b in am._bars]
        am.high = [b.high for b in am._bars]
        am.low = [b.low for b in am._bars]
        # bars_from_am needs length alignment — patch detector path using real am shape

        from strategies.paaf.adapters import vnpy_adapter as va

        original = va.bars_from_am

        def _fake_bars(am_obj, lookback=None):
            bars = list(am_obj._bars)
            if lookback is None:
                return bars
            return bars[-lookback:]

        va.bars_from_am = _fake_bars
        try:
            result = self.det.detect(am, self.ctx)
        finally:
            va.bars_from_am = original

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.direction, Direction.LONG)
        self.assertEqual(result.entry, 98.0)
        self.assertEqual(result.stop, 94.0)

    def test_ignores_context(self) -> None:
        self.assertTrue(callable(self.det.detect))


if __name__ == "__main__":
    unittest.main()
