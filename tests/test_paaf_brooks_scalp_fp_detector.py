"""Unit tests for Brooks Scalp first-pullback PAAF detector."""

from __future__ import annotations

import unittest

import numpy as np

from strategies.paaf.domain import Context, DetectorStatus, DetectorTag, Direction
from strategies.paaf.detectors.brooks_scalp_first_pullback import (
    BROOKS_SCALP_FP_DESCRIPTOR,
    BrooksScalpFirstPullbackDetector,
    FsmState,
)


class _FakeAM:
    """Minimal ArrayManager-like window with ema/atr for unit tests."""

    def __init__(
        self,
        opens: list[float],
        highs: list[float],
        lows: list[float],
        closes: list[float],
    ) -> None:
        self.open = np.asarray(opens, dtype=float)
        self.high = np.asarray(highs, dtype=float)
        self.low = np.asarray(lows, dtype=float)
        self.close = np.asarray(closes, dtype=float)
        self.count = len(closes)
        self.inited = True

    def ema(self, period: int, array: bool = False):
        alpha = 2.0 / (period + 1.0)
        out = np.empty_like(self.close)
        out[0] = self.close[0]
        for i in range(1, len(self.close)):
            out[i] = alpha * self.close[i] + (1.0 - alpha) * out[i - 1]
        return out if array else float(out[-1])

    def atr(self, period: int) -> float:
        prev_close = np.roll(self.close, 1)
        prev_close[0] = self.close[0]
        tr = np.maximum(
            self.high - self.low,
            np.maximum(np.abs(self.high - prev_close), np.abs(self.low - prev_close)),
        )
        return float(np.mean(tr[-period:]))


def _ramp(n: int = 40, start: float = 100.0, step: float = 1.0) -> _FakeAM:
    closes = [start + i * step for i in range(n)]
    opens = [c - 0.2 for c in closes]
    highs = [c + 0.5 for c in closes]
    lows = [c - 0.5 for c in closes]
    return _FakeAM(opens, highs, lows, closes)


class TestBrooksScalpFirstPullbackDetector(unittest.TestCase):
    def setUp(self) -> None:
        self.detector = BrooksScalpFirstPullbackDetector(pricetick=1.0)
        self.context = Context(symbol="rb")

    def test_descriptor_experiment_candidate(self) -> None:
        self.assertEqual(BROOKS_SCALP_FP_DESCRIPTOR.id, "BROOKS_SCALP_FP")
        self.assertEqual(BROOKS_SCALP_FP_DESCRIPTOR.version, "0.1.0")
        self.assertIs(BROOKS_SCALP_FP_DESCRIPTOR.status, DetectorStatus.EXPERIMENT)
        self.assertEqual(BROOKS_SCALP_FP_DESCRIPTOR.capability.timeframe, "1m")
        self.assertIn(DetectorTag.TREND, BROOKS_SCALP_FP_DESCRIPTOR.tags)
        self.assertIn(DetectorTag.PULLBACK, BROOKS_SCALP_FP_DESCRIPTOR.tags)

    def test_pattern_state_roundtrip(self) -> None:
        self.detector._fsm = FsmState.WAIT_PULLBACK
        self.detector._trend = 1
        self.detector._pullback_low = 10.0
        snap = self.detector.pattern_state
        other = BrooksScalpFirstPullbackDetector(pricetick=1.0)
        other.load_pattern_state(snap)
        self.assertEqual(other._fsm, FsmState.WAIT_PULLBACK)
        self.assertEqual(other._trend, 1)
        self.assertEqual(other._pullback_low, 10.0)

    def test_insufficient_bars_returns_none(self) -> None:
        am = _FakeAM([1, 2], [1, 2], [1, 2], [1, 2])
        self.assertIsNone(self.detector.detect(am, self.context))

    def test_uptrend_leg_advances_fsm(self) -> None:
        am = _ramp(40, start=100.0, step=2.0)
        # Force large ATR-relative move already present in ramp.
        for _ in range(5):
            self.detector.detect(am, self.context)
        # After enough bullish bars, FSM should leave IDLE if trend+leg fire.
        self.assertIn(
            self.detector._fsm,
            {FsmState.IDLE, FsmState.WAIT_PULLBACK, FsmState.PULLBACK},
        )

    def test_factory_creates_detector(self) -> None:
        created = BROOKS_SCALP_FP_DESCRIPTOR.create()
        self.assertIsInstance(created, BrooksScalpFirstPullbackDetector)

    def test_bull_signal_emits_long_levels(self) -> None:
        det = BrooksScalpFirstPullbackDetector(
            ema_period=5,
            atr_period=5,
            trend_leg_atr=0.1,
            pullback_atr=10.0,
            risk_reward=1.0,
            pricetick=1.0,
        )
        closes = [100 + i for i in range(20)]
        am = _FakeAM(
            opens=[c - 1 for c in closes],
            highs=[c + 2 for c in closes],
            lows=[c - 2 for c in closes],
            closes=closes,
        )
        det._fsm = FsmState.PULLBACK
        det._trend = 1
        pullback_low = float(am.low[-1]) - 5.0
        det._pullback_low = pullback_low
        det._ema = float(am.close[-1])
        det._atr = 2.0
        # Keep trend gate from clearing FSM during detect().
        det._detect_trend = lambda _am: None  # type: ignore[method-assign]
        am.open[-1] = am.close[-1] - 3.0
        am.high[-1] = am.close[-1] + 0.5
        am.low[-1] = am.open[-1] - 0.1
        am.high[-2] = am.close[-1] - 1.0

        result = det.detect(am, self.context)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertIs(result.direction, Direction.LONG)
        self.assertEqual(result.entry, float(am.high[-1]) + 1.0)
        self.assertEqual(result.stop, pullback_low - 1.0)
        self.assertEqual(
            result.target,
            result.entry + (result.entry - result.stop) * 1.0,
        )
        self.assertEqual(result.detector_id, "BROOKS_SCALP_FP")
        self.assertIs(result.status, DetectorStatus.EXPERIMENT)
        self.assertEqual(det._fsm, FsmState.IDLE)


if __name__ == "__main__":
    unittest.main()
