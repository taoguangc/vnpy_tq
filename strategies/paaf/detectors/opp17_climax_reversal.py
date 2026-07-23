"""OPP17 climax-reversal Candidate Detector; observations only, never trading.

PAAF rewrite of legacy Opp17Mixin morphology（OPP17_MS_V0_1）.
Context is ignored in detect().
"""

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

OPP17_DETECTOR_ID = "OPP17"
OPP17_DETECTOR_VERSION = "1.0.0"
OPP17_OPPORTUNITY_ID = "OPP17"
DEFAULT_ATR_PERIOD = 14
DEFAULT_CLIMAX_RANGE_ATR = 2.5


class OPP17ClimaxReversalDetector(BaseDetector):
    """Prior-bar climax range + mid reclaim; no Context filter."""

    metadata = DetectorMetadata(
        name=OPP17_DETECTOR_ID,
        version=OPP17_DETECTOR_VERSION,
        description="Climax-reversal Candidate; E0 observation only（OPP17_MS_V0_1）",
        status="Candidate",
        category="Reversal",
        timeframe="5m",
        evidence_level="E0",
    )

    def __init__(
        self,
        *,
        atr_period: int = DEFAULT_ATR_PERIOD,
        climax_range_atr: float = DEFAULT_CLIMAX_RANGE_ATR,
    ) -> None:
        if not isinstance(atr_period, int) or atr_period < 2:
            raise ValueError("atr_period 必须是 >= 2 的 int")
        if climax_range_atr <= 0:
            raise ValueError("climax_range_atr 必须 > 0")
        self._atr_period = atr_period
        self._climax_range_atr = float(climax_range_atr)

    def detect(
        self,
        am: Any,
        context: Context,
    ) -> Optional[DetectionResult]:
        del context  # OPP17_MS: no Context gate
        if not am_is_inited(am):
            return None
        need = self._atr_period + 2
        bars = bars_from_am(am, need)
        if len(bars) < 2:
            return None

        atr = self._read_atr(am)
        if atr is None or atr <= 0:
            return None

        prev = bars[-2]
        bar = bars[-1]
        bar_range = bar.high - bar.low
        if bar_range <= 0:
            return None

        prev_range = prev.high - prev.low
        if prev_range <= 0 or prev_range <= self._climax_range_atr * atr:
            return None

        prev_mid = (prev.high + prev.low) / 2.0

        # Long: prior bearish climax bar + reclaim above prior mid
        if prev.close < prev.open and bar.close > prev_mid:
            return self._result(
                Direction.LONG,
                entry=bar.high,
                stop=bar.low,
                reason="climax-rev long: prior bear range + close above mid",
                atr=atr,
                prev_range=prev_range,
                prev_mid=prev_mid,
            )

        # Short: prior bullish climax bar + reject below prior mid
        if prev.close > prev.open and bar.close < prev_mid:
            return self._result(
                Direction.SHORT,
                entry=bar.low,
                stop=bar.high,
                reason="climax-rev short: prior bull range + close below mid",
                atr=atr,
                prev_range=prev_range,
                prev_mid=prev_mid,
            )
        return None

    def _read_atr(self, am: Any) -> Optional[float]:
        fn = getattr(am, "atr", None)
        if not callable(fn):
            return None
        try:
            value = float(fn(self._atr_period))
        except (TypeError, ValueError):
            return None
        if value != value:  # NaN
            return None
        return value

    def _result(
        self,
        direction: Direction,
        *,
        entry: float,
        stop: float,
        reason: str,
        atr: float,
        prev_range: float,
        prev_mid: float,
    ) -> DetectionResult:
        return DetectionResult(
            detector_id=OPP17_DETECTOR_ID,
            detector_version=OPP17_DETECTOR_VERSION,
            opportunity_id=OPP17_OPPORTUNITY_ID,
            status=DetectorStatus.EXPERIMENT,
            direction=direction,
            confidence=1.0,
            tags=(DetectorTag.REVERSAL, "custom:climax_reversal"),
            entry=entry,
            stop=stop,
            reason=reason,
            metadata={
                "atr_period": self._atr_period,
                "climax_range_atr": self._climax_range_atr,
                "atr": atr,
                "prev_range": prev_range,
                "prev_mid": prev_mid,
                "timeframe": "5m",
            },
            pattern_state=PatternState(
                name="climax_reversal",
                confidence=1.0,
                metadata={"direction": direction.value},
            ),
        )


OPP17_DESCRIPTOR = DetectorDescriptor(
    id=OPP17_DETECTOR_ID,
    version=OPP17_DETECTOR_VERSION,
    status=DetectorStatus.EXPERIMENT,
    capability=DetectorCapability(
        directions=(Direction.LONG, Direction.SHORT),
        requires=frozenset(),
        produces=frozenset({DetectorTag.REVERSAL, "custom:climax_reversal"}),
        timeframe="5m",
    ),
    factory=OPP17ClimaxReversalDetector,
    tags=(DetectorTag.REVERSAL, "custom:climax_reversal"),
    metadata={
        "purpose": "cid005_opp17_candidate",
        "alpha_claim": False,
        "spec": "OPP17_MS_V0_1",
    },
)
