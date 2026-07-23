"""OPP13 day-boundary single-touch Candidate Detector; observations only.

PAAF rewrite of legacy Opp13Mixin Path A（OPP13_MS_V0_1）.
Double-top / volume / Context OUT OF SCOPE.
Cross-bar day levels are explicit PatternState on the instance.
"""

from __future__ import annotations

from datetime import datetime, time
from typing import Any, Mapping, Optional

from strategies.paaf.adapters import am_is_inited
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

OPP13_DETECTOR_ID = "OPP13"
OPP13_DETECTOR_VERSION = "1.0.0"
OPP13_OPPORTUNITY_ID = "OPP13"
DEFAULT_DAY_BOUNDARY_TOLERANCE = 5.0
DEFAULT_SHADOW_RATIO = 0.45
DEFAULT_CLOSE_RATIO = 0.30
DEFAULT_PRICETICK = 1.0
DAY_RESET_TIME = time(9, 6)


class OPP13DayBoundaryTouchDetector(BaseDetector):
    """Day-high/low single-touch fail; no Context / double-top / volume."""

    metadata = DetectorMetadata(
        name=OPP13_DETECTOR_ID,
        version=OPP13_DETECTOR_VERSION,
        description="Day-boundary single-touch Candidate; E0（OPP13_MS_V0_1）",
        status="Candidate",
        category="Reversal",
        timeframe="5m",
        evidence_level="E0",
    )

    def __init__(
        self,
        *,
        day_boundary_tolerance: float = DEFAULT_DAY_BOUNDARY_TOLERANCE,
        boundary_reversal_shadow_ratio: float = DEFAULT_SHADOW_RATIO,
        boundary_reversal_close_ratio: float = DEFAULT_CLOSE_RATIO,
        pricetick: float = DEFAULT_PRICETICK,
    ) -> None:
        if day_boundary_tolerance <= 0:
            raise ValueError("day_boundary_tolerance 必须 > 0")
        if not 0 < boundary_reversal_shadow_ratio <= 1:
            raise ValueError("boundary_reversal_shadow_ratio 必须在 (0, 1]")
        if not 0 < boundary_reversal_close_ratio <= 1:
            raise ValueError("boundary_reversal_close_ratio 必须在 (0, 1]")
        if pricetick <= 0:
            raise ValueError("pricetick 必须 > 0")

        self._tol_ticks = float(day_boundary_tolerance)
        self._shadow = float(boundary_reversal_shadow_ratio)
        self._close_ratio = float(boundary_reversal_close_ratio)
        self._tick = float(pricetick)

        self._day_high = 0.0
        self._day_low = 0.0
        self._bar_dt: Optional[datetime] = None

    def note_bar_datetime(self, bar_dt: datetime) -> None:
        """Strategy injects completed 5m bar datetime."""
        self._bar_dt = bar_dt

    def set_pricetick(self, pricetick: float) -> None:
        if pricetick <= 0:
            raise ValueError("pricetick 必须 > 0")
        self._tick = float(pricetick)

    def adjust_levels(self, shift: float) -> None:
        """CbC price shift for day high/low."""
        if abs(shift) < 1e-12:
            return
        if abs(self._day_high) > 1e-12:
            self._day_high += shift
        if abs(self._day_low) > 1e-12:
            self._day_low += shift

    @property
    def pattern_state(self) -> PatternState:
        return self._build_pattern_state(confidence=1.0)

    def load_pattern_state(self, state: PatternState | Mapping[str, Any]) -> None:
        data = state.to_dict() if isinstance(state, PatternState) else dict(state)
        meta = dict(data.get("metadata") or {})
        self._day_high = float(meta.get("day_high", 0.0))
        self._day_low = float(meta.get("day_low", 0.0))

    def detect(
        self,
        am: Any,
        context: Context,
    ) -> Optional[DetectionResult]:
        del context  # OPP13_MS: no Context gate
        if not am_is_inited(am):
            return None
        if self._bar_dt is None:
            return None
        if int(getattr(am, "count", 0) or 0) < 1:
            return None

        o = float(am.open[-1])
        h = float(am.high[-1])
        low = float(am.low[-1])
        c = float(am.close[-1])
        bar_range = h - low
        if bar_range <= 0:
            return None

        self._update_day_levels(h, low)

        tol = self._tol_ticks * self._tick
        upper_shadow = h - max(o, c)
        lower_shadow = min(o, c) - low

        # Short: day-high single touch
        if (
            self._day_high > 0
            and abs(h - self._day_high) <= tol
            and c < o
            and upper_shadow >= bar_range * self._shadow
            and c <= low + bar_range * self._close_ratio
        ):
            return self._result(
                Direction.SHORT,
                entry=low,
                stop=h + self._tick,
                reason="day-boundary short: single-touch day high fail",
            )

        # Long: day-low single touch
        if (
            self._day_low > 0
            and abs(low - self._day_low) <= tol
            and c > o
            and lower_shadow >= bar_range * self._shadow
            and c >= h - bar_range * self._close_ratio
        ):
            return self._result(
                Direction.LONG,
                entry=h,
                stop=low - self._tick,
                reason="day-boundary long: single-touch day low fail",
            )
        return None

    def _update_day_levels(self, high: float, low: float) -> None:
        assert self._bar_dt is not None
        t = self._bar_dt.time().replace(second=0, microsecond=0)
        if t == DAY_RESET_TIME or self._day_high <= 0:
            self._day_high = high
            self._day_low = low
        else:
            self._day_high = max(self._day_high, high)
            self._day_low = min(self._day_low, low)

    def _build_pattern_state(self, *, confidence: float) -> PatternState:
        return PatternState(
            name="day_boundary_touch",
            confidence=confidence,
            metadata={
                "day_high": self._day_high,
                "day_low": self._day_low,
            },
        )

    def _result(
        self,
        direction: Direction,
        *,
        entry: float,
        stop: float,
        reason: str,
    ) -> DetectionResult:
        return DetectionResult(
            detector_id=OPP13_DETECTOR_ID,
            detector_version=OPP13_DETECTOR_VERSION,
            opportunity_id=OPP13_OPPORTUNITY_ID,
            status=DetectorStatus.EXPERIMENT,
            direction=direction,
            confidence=1.0,
            tags=(DetectorTag.REVERSAL, "custom:day_boundary_touch"),
            entry=entry,
            stop=stop,
            reason=reason,
            metadata={
                "day_boundary_tolerance": self._tol_ticks,
                "boundary_reversal_shadow_ratio": self._shadow,
                "boundary_reversal_close_ratio": self._close_ratio,
                "day_high": self._day_high,
                "day_low": self._day_low,
                "pricetick": self._tick,
                "timeframe": "5m",
            },
            pattern_state=self._build_pattern_state(confidence=1.0),
        )


OPP13_DESCRIPTOR = DetectorDescriptor(
    id=OPP13_DETECTOR_ID,
    version=OPP13_DETECTOR_VERSION,
    status=DetectorStatus.EXPERIMENT,
    capability=DetectorCapability(
        directions=(Direction.LONG, Direction.SHORT),
        requires=frozenset(),
        produces=frozenset({DetectorTag.REVERSAL, "custom:day_boundary_touch"}),
        timeframe="5m",
    ),
    factory=OPP13DayBoundaryTouchDetector,
    tags=(DetectorTag.REVERSAL, "custom:day_boundary_touch"),
    metadata={
        "purpose": "cid010_opp13_candidate",
        "alpha_claim": False,
        "spec": "OPP13_MS_V0_1",
    },
)
