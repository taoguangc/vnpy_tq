"""OPP13 day-high double-top Candidate Detector; observations only.

PAAF rewrite of legacy Opp13Mixin._try_day_high_double_top（OPP13_DT_MS_V0_1）.
Single-touch Path A / Context / volume OUT OF SCOPE.
Cross-bar day levels + FIRST_TEST FSM are explicit PatternState.
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

OPP13_DT_DETECTOR_ID = "OPP13_DT"
OPP13_DT_DETECTOR_VERSION = "1.0.0"
OPP13_DT_OPPORTUNITY_ID = "OPP13_DT"
DEFAULT_DAY_HIGH_SECOND_TEST_TICKS = 3.0
DEFAULT_DAY_HIGH_SECOND_TEST_MAX_BARS = 12
DEFAULT_DAY_HIGH_LH_MAX_TICKS = 10.0
DEFAULT_QUALITY_SHADOW_RATIO = 0.40
DEFAULT_QUALITY_CLOSE_FROM_HIGH_RATIO = 0.35
DEFAULT_BOUNDARY_SHADOW_RATIO = 0.45
DEFAULT_BOUNDARY_CLOSE_RATIO = 0.30
DEFAULT_PRICETICK = 1.0
DAY_RESET_TIME = time(9, 6)
_FSM_IDLE = "IDLE"
_FSM_FIRST_TEST = "FIRST_TEST"


class OPP13DayHighDoubleTopDetector(BaseDetector):
    """Day-high FIRST_TEST → LH second-test short; no Context / single-touch."""

    metadata = DetectorMetadata(
        name=OPP13_DT_DETECTOR_ID,
        version=OPP13_DT_DETECTOR_VERSION,
        description="Day-high double-top Candidate; E0（OPP13_DT_MS_V0_1）",
        status="Candidate",
        category="Reversal",
        timeframe="5m",
        evidence_level="E0",
    )

    def __init__(
        self,
        *,
        day_high_second_test_ticks: float = DEFAULT_DAY_HIGH_SECOND_TEST_TICKS,
        day_high_second_test_max_bars: int = DEFAULT_DAY_HIGH_SECOND_TEST_MAX_BARS,
        day_high_lh_max_ticks: float = DEFAULT_DAY_HIGH_LH_MAX_TICKS,
        quality_shadow_ratio: float = DEFAULT_QUALITY_SHADOW_RATIO,
        quality_close_from_high_ratio: float = DEFAULT_QUALITY_CLOSE_FROM_HIGH_RATIO,
        boundary_reversal_shadow_ratio: float = DEFAULT_BOUNDARY_SHADOW_RATIO,
        boundary_reversal_close_ratio: float = DEFAULT_BOUNDARY_CLOSE_RATIO,
        pricetick: float = DEFAULT_PRICETICK,
    ) -> None:
        if day_high_second_test_ticks <= 0:
            raise ValueError("day_high_second_test_ticks 必须 > 0")
        if day_high_second_test_max_bars <= 0:
            raise ValueError("day_high_second_test_max_bars 必须 > 0")
        if day_high_lh_max_ticks <= 0:
            raise ValueError("day_high_lh_max_ticks 必须 > 0")
        for name, value in (
            ("quality_shadow_ratio", quality_shadow_ratio),
            ("quality_close_from_high_ratio", quality_close_from_high_ratio),
            ("boundary_reversal_shadow_ratio", boundary_reversal_shadow_ratio),
            ("boundary_reversal_close_ratio", boundary_reversal_close_ratio),
        ):
            if not 0 < float(value) <= 1:
                raise ValueError(f"{name} 必须在 (0, 1]")
        if pricetick <= 0:
            raise ValueError("pricetick 必须 > 0")

        self._touch_ticks = float(day_high_second_test_ticks)
        self._max_bars = int(day_high_second_test_max_bars)
        self._lh_ticks = float(day_high_lh_max_ticks)
        self._q_shadow = float(quality_shadow_ratio)
        self._q_close = float(quality_close_from_high_ratio)
        self._b_shadow = float(boundary_reversal_shadow_ratio)
        self._b_close = float(boundary_reversal_close_ratio)
        self._tick = float(pricetick)

        self._day_high = 0.0
        self._day_low = 0.0
        self._fsm = _FSM_IDLE
        self._first_test_high = 0.0
        self._bar_count = 0
        self._bar_dt: Optional[datetime] = None

    def note_bar_datetime(self, bar_dt: datetime) -> None:
        """Strategy injects completed 5m bar datetime."""
        self._bar_dt = bar_dt

    def set_pricetick(self, pricetick: float) -> None:
        if pricetick <= 0:
            raise ValueError("pricetick 必须 > 0")
        self._tick = float(pricetick)

    def adjust_levels(self, shift: float) -> None:
        """CbC price shift for day levels and first-test high."""
        if abs(shift) < 1e-12:
            return
        if abs(self._day_high) > 1e-12:
            self._day_high += shift
        if abs(self._day_low) > 1e-12:
            self._day_low += shift
        if abs(self._first_test_high) > 1e-12:
            self._first_test_high += shift

    @property
    def pattern_state(self) -> PatternState:
        return self._build_pattern_state(confidence=1.0)

    def load_pattern_state(self, state: PatternState | Mapping[str, Any]) -> None:
        data = state.to_dict() if isinstance(state, PatternState) else dict(state)
        meta = dict(data.get("metadata") or {})
        self._day_high = float(meta.get("day_high", 0.0))
        self._day_low = float(meta.get("day_low", 0.0))
        self._fsm = str(meta.get("fsm", _FSM_IDLE))
        self._first_test_high = float(meta.get("first_test_high", 0.0))
        self._bar_count = int(meta.get("bar_count", 0))

    def detect(
        self,
        am: Any,
        context: Context,
    ) -> Optional[DetectionResult]:
        del context  # OPP13_DT_MS: no Context gate
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

        if self._fsm == _FSM_FIRST_TEST:
            self._bar_count += 1
            if self._bar_count > self._max_bars:
                self._reset_fsm()

        touch_tol = self._touch_ticks * self._tick
        lh_max = self._lh_ticks * self._tick
        quality = self._is_quality_day_high_short(o, h, low, c, bar_range)

        if (
            self._fsm == _FSM_IDLE
            and self._day_high > 0
            and abs(h - self._day_high) <= touch_tol
            and quality
        ):
            self._fsm = _FSM_FIRST_TEST
            self._first_test_high = h
            self._bar_count = 0
            return None

        if self._fsm == _FSM_FIRST_TEST and quality:
            lh_ok = (
                self._bar_count <= self._max_bars
                and self._first_test_high > 0
                and h <= self._first_test_high
                and h >= self._first_test_high - lh_max
            )
            if lh_ok:
                result = self._result(
                    Direction.SHORT,
                    entry=low,
                    stop=h + self._tick,
                    reason="day-high double-top: LH second-test short",
                )
                self._reset_fsm()
                return result
        return None

    def _is_quality_day_high_short(
        self,
        o: float,
        h: float,
        low: float,
        c: float,
        bar_range: float,
    ) -> bool:
        upper_shadow = h - max(o, c)
        boundary = (
            upper_shadow >= bar_range * self._b_shadow
            and c <= low + bar_range * self._b_close
        )
        quality = (
            upper_shadow >= bar_range * self._q_shadow
            and c <= h - bar_range * self._q_close
        )
        return boundary and quality

    def _update_day_levels(self, high: float, low: float) -> None:
        assert self._bar_dt is not None
        t = self._bar_dt.time().replace(second=0, microsecond=0)
        if t == DAY_RESET_TIME or self._day_high <= 0:
            self._day_high = high
            self._day_low = low
            self._reset_fsm()
        else:
            self._day_high = max(self._day_high, high)
            self._day_low = min(self._day_low, low)

    def _reset_fsm(self) -> None:
        self._fsm = _FSM_IDLE
        self._first_test_high = 0.0
        self._bar_count = 0

    def _build_pattern_state(self, *, confidence: float) -> PatternState:
        return PatternState(
            name="day_high_double_top",
            confidence=confidence,
            metadata={
                "day_high": self._day_high,
                "day_low": self._day_low,
                "fsm": self._fsm,
                "first_test_high": self._first_test_high,
                "bar_count": self._bar_count,
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
            detector_id=OPP13_DT_DETECTOR_ID,
            detector_version=OPP13_DT_DETECTOR_VERSION,
            opportunity_id=OPP13_DT_OPPORTUNITY_ID,
            status=DetectorStatus.EXPERIMENT,
            direction=direction,
            confidence=1.0,
            tags=(DetectorTag.REVERSAL, "custom:day_high_double_top"),
            entry=entry,
            stop=stop,
            reason=reason,
            metadata={
                "day_high_second_test_ticks": self._touch_ticks,
                "day_high_second_test_max_bars": self._max_bars,
                "day_high_lh_max_ticks": self._lh_ticks,
                "quality_shadow_ratio": self._q_shadow,
                "quality_close_from_high_ratio": self._q_close,
                "boundary_reversal_shadow_ratio": self._b_shadow,
                "boundary_reversal_close_ratio": self._b_close,
                "day_high": self._day_high,
                "day_low": self._day_low,
                "first_test_high": self._first_test_high,
                "pricetick": self._tick,
                "timeframe": "5m",
            },
            pattern_state=self._build_pattern_state(confidence=1.0),
        )


OPP13_DT_DESCRIPTOR = DetectorDescriptor(
    id=OPP13_DT_DETECTOR_ID,
    version=OPP13_DT_DETECTOR_VERSION,
    status=DetectorStatus.EXPERIMENT,
    capability=DetectorCapability(
        directions=(Direction.SHORT,),
        requires=frozenset(),
        produces=frozenset({DetectorTag.REVERSAL, "custom:day_high_double_top"}),
        timeframe="5m",
    ),
    factory=OPP13DayHighDoubleTopDetector,
    tags=(DetectorTag.REVERSAL, "custom:day_high_double_top"),
    metadata={
        "purpose": "cid012_opp13_dt_candidate",
        "alpha_claim": False,
        "spec": "OPP13_DT_MS_V0_1",
    },
)
