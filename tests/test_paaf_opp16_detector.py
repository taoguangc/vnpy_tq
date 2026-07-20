"""OPP16 Candidate Detector contract tests."""

from __future__ import annotations

from types import SimpleNamespace
import unittest

from strategies.paaf.domain import Context, DetectorStatus, DetectorTag, Direction
from strategies.paaf.detectors.opp16_two_bar_reversal import (
    DEFAULT_BODY_RATIO,
    OPP16_DESCRIPTOR,
    OPP16TwoBarReversalDetector,
)


def _window(
    opens: tuple[float, ...],
    highs: tuple[float, ...],
    lows: tuple[float, ...],
    closes: tuple[float, ...],
) -> SimpleNamespace:
    return SimpleNamespace(
        open=opens,
        high=highs,
        low=lows,
        close=closes,
        count=len(closes),
        inited=True,
    )


class TestOPP16TwoBarReversalDetector(unittest.TestCase):
    def setUp(self) -> None:
        self.detector = OPP16TwoBarReversalDetector()
        self.context = Context(symbol="rb")

    def test_descriptor_is_experiment_candidate(self) -> None:
        self.assertEqual(OPP16_DESCRIPTOR.id, "OPP16")
        self.assertEqual(OPP16_DESCRIPTOR.version, "1.0.0")
        self.assertIs(OPP16_DESCRIPTOR.status, DetectorStatus.EXPERIMENT)
        self.assertEqual(OPP16_DESCRIPTOR.capability.timeframe, "5m")
        self.assertIn(DetectorTag.REVERSAL, OPP16_DESCRIPTOR.tags)

    def test_long_and_short_mirror(self) -> None:
        long_hit = self.detector.detect(
            _window(
                opens=(110.0, 104.0),
                highs=(110.0, 108.0),
                lows=(100.0, 103.0),
                closes=(100.0, 107.0),
            ),
            self.context,
        )
        short_hit = self.detector.detect(
            _window(
                opens=(100.0, 106.0),
                highs=(110.0, 107.0),
                lows=(100.0, 102.0),
                closes=(110.0, 103.0),
            ),
            self.context,
        )

        self.assertIsNotNone(long_hit)
        self.assertIsNotNone(short_hit)
        assert long_hit is not None and short_hit is not None
        self.assertIs(long_hit.direction, Direction.LONG)
        self.assertIs(short_hit.direction, Direction.SHORT)
        self.assertEqual(long_hit.stop, 103.0)
        self.assertEqual(short_hit.stop, 107.0)
        self.assertEqual(long_hit.entry, 107.0)
        self.assertEqual(short_hit.entry, 103.0)

    def test_body_ratio_and_mid_gate(self) -> None:
        weak_body = self.detector.detect(
            _window(
                opens=(104.0, 104.0),
                highs=(110.0, 108.0),
                lows=(100.0, 103.0),
                closes=(100.0, 107.0),
            ),
            self.context,
        )
        below_mid = self.detector.detect(
            _window(
                opens=(110.0, 104.0),
                highs=(110.0, 106.0),
                lows=(100.0, 103.0),
                closes=(100.0, 104.0),
            ),
            self.context,
        )
        zero_range = self.detector.detect(
            _window(
                opens=(100.0, 101.0),
                highs=(100.0, 102.0),
                lows=(100.0, 100.0),
                closes=(100.0, 101.5),
            ),
            self.context,
        )

        self.assertIsNone(weak_body)
        self.assertIsNone(below_mid)
        self.assertIsNone(zero_range)

    def test_default_body_ratio_matches_spec(self) -> None:
        self.assertEqual(DEFAULT_BODY_RATIO, 0.5)
        with self.assertRaisesRegex(ValueError, "body_ratio"):
            OPP16TwoBarReversalDetector(body_ratio=0.0)


if __name__ == "__main__":
    unittest.main()
