"""OPP16 two-bar reversal Candidate Detector; observations only, never trading."""

from __future__ import annotations

from typing import Any, Optional

from strategies.paaf.adapters import am_is_inited, bars_from_am
from strategies.paaf.base_detector import BaseDetector
from strategies.paaf.domain import (
    Context,
    DetectionResult,
    DetectorStatus,
    DetectorTag,
    Direction,
    PatternState,
)
from strategies.paaf.metadata import DetectorMetadata
from strategies.paaf.registry import DetectorCapability, DetectorDescriptor

OPP16_DETECTOR_ID = "OPP16"
OPP16_DETECTOR_VERSION = "1.0.0"
OPP16_OPPORTUNITY_ID = "OPP16"
DEFAULT_BODY_RATIO = 0.5


class OPP16TwoBarReversalDetector(BaseDetector):
    """Bare two-bar reversal on completed bars; no Context filter."""

    metadata = DetectorMetadata(
        name=OPP16_DETECTOR_ID,
        version=OPP16_DETECTOR_VERSION,
        description="Bare two-bar reversal Candidate; E0 observation only",
        status="Candidate",
        category="Reversal",
        timeframe="5m",
        evidence_level="E0",
    )

    def __init__(self, *, body_ratio: float = DEFAULT_BODY_RATIO) -> None:
        if (
            isinstance(body_ratio, bool)
            or not isinstance(body_ratio, (int, float))
            or not 0.0 < float(body_ratio) <= 1.0
        ):
            raise ValueError("body_ratio 必须在 (0, 1]")
        self._body_ratio = float(body_ratio)

    def detect(
        self,
        am: Any,
        context: Context,
    ) -> Optional[DetectionResult]:
        del context  # EXP001: no Context gate
        if not am_is_inited(am):
            return None
        bars = bars_from_am(am, 2)
        if len(bars) < 2:
            return None

        prev, bar = bars[0], bars[1]
        prev_range = prev.high - prev.low
        if prev_range <= 0:
            return None
        prev_body_ratio = abs(prev.close - prev.open) / prev_range
        if prev_body_ratio < self._body_ratio:
            return None

        prev_mid = (prev.high + prev.low) / 2.0
        if prev.close < prev.open and bar.close > prev_mid:
            return self._result(
                Direction.LONG,
                entry=bar.close,
                stop=bar.low,
                reason="two-bar reversal long: bearish prev, close above mid",
                prev_body_ratio=prev_body_ratio,
            )
        if prev.close > prev.open and bar.close < prev_mid:
            return self._result(
                Direction.SHORT,
                entry=bar.close,
                stop=bar.high,
                reason="two-bar reversal short: bullish prev, close below mid",
                prev_body_ratio=prev_body_ratio,
            )
        return None

    def _result(
        self,
        direction: Direction,
        *,
        entry: float,
        stop: float,
        reason: str,
        prev_body_ratio: float,
    ) -> DetectionResult:
        return DetectionResult(
            detector_id=OPP16_DETECTOR_ID,
            detector_version=OPP16_DETECTOR_VERSION,
            opportunity_id=OPP16_OPPORTUNITY_ID,
            status=DetectorStatus.EXPERIMENT,
            direction=direction,
            confidence=1.0,
            tags=(DetectorTag.REVERSAL, "custom:two_bar"),
            entry=entry,
            stop=stop,
            reason=reason,
            metadata={
                "body_ratio_threshold": self._body_ratio,
                "prev_body_ratio": prev_body_ratio,
                "timeframe": "5m",
            },
            pattern_state=PatternState(
                name="two_bar_reversal",
                confidence=1.0,
                metadata={"direction": direction.value},
            ),
        )


OPP16_DESCRIPTOR = DetectorDescriptor(
    id=OPP16_DETECTOR_ID,
    version=OPP16_DETECTOR_VERSION,
    status=DetectorStatus.EXPERIMENT,
    capability=DetectorCapability(
        directions=(Direction.LONG, Direction.SHORT),
        requires=frozenset(),
        produces=frozenset({DetectorTag.REVERSAL, "custom:two_bar"}),
        timeframe="5m",
    ),
    factory=OPP16TwoBarReversalDetector,
    tags=(DetectorTag.REVERSAL, "custom:two_bar"),
    metadata={
        "purpose": "opp16_exp001_candidate",
        "alpha_claim": False,
        "body_ratio": DEFAULT_BODY_RATIO,
    },
)
