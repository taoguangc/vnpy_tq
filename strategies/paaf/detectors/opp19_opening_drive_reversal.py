"""OPP19 opening-drive REVERSAL Candidate Detector; observations only.

PAAF rewrite of legacy Opp19Mixin OD_REV path（OPP19_REV_MS_V0_1）.
OD-Breakout is OUT OF SCOPE（separate CID_007 identity）.
Context is ignored in detect().
Cross-bar FSM is explicit PatternState on the instance.
"""

from __future__ import annotations

from datetime import date, datetime, time
from enum import Enum
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

OPP19_REV_DETECTOR_ID = "OPP19_REV"
OPP19_REV_DETECTOR_VERSION = "1.0.0"
OPP19_REV_OPPORTUNITY_ID = "OPP19_REV"
DEFAULT_ATR_PERIOD = 14
DEFAULT_OPENING_REV_BODY_RATIO = 0.45
DEFAULT_MORNING_CUTOFF_MINUTE = 25
DEFAULT_NIGHT_CUTOFF_MINUTE = 25
DEFAULT_MIN_BAR1_RANGE_ATR = 0.30
DEFAULT_MAX_BAR1_RANGE_ATR = 2.50


class RevState(str, Enum):
    IDLE = "IDLE"
    BAR1_SET = "BAR1_SET"


class OPP19OpeningDriveReversalDetector(BaseDetector):
    """Session opening bar1 fade; no Context / OD-Breakout."""

    metadata = DetectorMetadata(
        name=OPP19_REV_DETECTOR_ID,
        version=OPP19_REV_DETECTOR_VERSION,
        description="Opening-drive reversal Candidate; E0（OPP19_REV_MS_V0_1）",
        status="Candidate",
        category="Session",
        timeframe="5m",
        evidence_level="E0",
    )

    def __init__(
        self,
        *,
        atr_period: int = DEFAULT_ATR_PERIOD,
        opening_rev_body_ratio: float = DEFAULT_OPENING_REV_BODY_RATIO,
        morning_cutoff_minute: int = DEFAULT_MORNING_CUTOFF_MINUTE,
        night_cutoff_minute: int = DEFAULT_NIGHT_CUTOFF_MINUTE,
        min_bar1_range_atr: float = DEFAULT_MIN_BAR1_RANGE_ATR,
        max_bar1_range_atr: float = DEFAULT_MAX_BAR1_RANGE_ATR,
    ) -> None:
        if not isinstance(atr_period, int) or atr_period < 2:
            raise ValueError("atr_period 必须是 >= 2 的 int")
        if not 0 < opening_rev_body_ratio <= 1:
            raise ValueError("opening_rev_body_ratio 必须在 (0, 1]")
        if not 0 <= morning_cutoff_minute <= 59:
            raise ValueError("morning_cutoff_minute 必须在 [0, 59]")
        if not 0 <= night_cutoff_minute <= 59:
            raise ValueError("night_cutoff_minute 必须在 [0, 59]")
        if min_bar1_range_atr <= 0 or max_bar1_range_atr <= min_bar1_range_atr:
            raise ValueError("bar1 ATR band 无效")

        self._atr_period = atr_period
        self._body_ratio = float(opening_rev_body_ratio)
        self._am_cut = int(morning_cutoff_minute)
        self._pm_cut = int(night_cutoff_minute)
        self._min_bar1 = float(min_bar1_range_atr)
        self._max_bar1 = float(max_bar1_range_atr)

        self._fsm = RevState.IDLE
        self._bar1_shape = ""
        self._bar1_mid = 0.0
        self._bar1_range = 0.0
        self._bars_collected = 0
        self._session_date: Optional[date] = None
        self._bar_dt: Optional[datetime] = None

    def note_bar_datetime(self, bar_dt: datetime) -> None:
        """Strategy injects completed 5m bar datetime."""
        self._bar_dt = bar_dt

    def adjust_levels(self, shift: float) -> None:
        """CbC price shift for bar1 mid."""
        if abs(shift) < 1e-12:
            return
        if abs(self._bar1_mid) > 1e-12:
            self._bar1_mid += shift

    @property
    def pattern_state(self) -> PatternState:
        return self._build_pattern_state(confidence=1.0)

    def load_pattern_state(self, state: PatternState | Mapping[str, Any]) -> None:
        data = state.to_dict() if isinstance(state, PatternState) else dict(state)
        meta = dict(data.get("metadata") or {})
        self._fsm = RevState(str(meta.get("fsm", RevState.IDLE.value)))
        self._bar1_shape = str(meta.get("bar1_shape", ""))
        self._bar1_mid = float(meta.get("bar1_mid", 0.0))
        self._bar1_range = float(meta.get("bar1_range", 0.0))
        self._bars_collected = int(meta.get("bars_collected", 0))
        session = meta.get("session_date")
        self._session_date = date.fromisoformat(session) if session else None

    def detect(
        self,
        am: Any,
        context: Context,
    ) -> Optional[DetectionResult]:
        del context  # OPP19_REV_MS: no Context gate
        if not am_is_inited(am):
            return None
        if self._bar_dt is None:
            return None

        atr = self._read_atr(am)
        if atr is None or atr <= 0:
            return None

        o = float(am.open[-1])
        h = float(am.high[-1])
        low = float(am.low[-1])
        c = float(am.close[-1])
        bar_range = h - low
        if bar_range <= 0:
            return None
        body = abs(c - o)
        body_ratio = body / bar_range

        bar_time = self._bar_dt.time()
        bar_date = self._bar_dt.date()
        is_morning = time(9, 0) <= bar_time <= time(11, 30)
        is_night = time(21, 0) <= bar_time <= time(23, 0)
        if not (is_morning or is_night):
            if self._fsm is not RevState.IDLE:
                self._reset()
            return None

        session_changed = bar_date != self._session_date
        new_morning = is_morning and bar_time < time(9, 20) and self._fsm is RevState.IDLE
        new_night = is_night and bar_time < time(21, 20) and self._fsm is RevState.IDLE
        if session_changed or new_morning or new_night:
            self._reset()
            self._session_date = bar_date
            # First bar of session may also be bar1
            return self._maybe_set_bar1(
                o=o, h=h, low=low, c=c, bar_range=bar_range, body_ratio=body_ratio
            )

        if self._fsm is RevState.IDLE:
            return None

        if self._fsm is RevState.BAR1_SET:
            self._bars_collected += 1
            if self._bars_collected > 2:
                self._reset()
                return None
            if not self._in_signal_window(bar_time, is_morning=is_morning, is_night=is_night):
                return None
            if not self._bar1_atr_ok(atr):
                return None

            # Reverse vs bar1
            if (
                self._bar1_shape == "DOWN"
                and c > o
                and body_ratio >= self._body_ratio
                and c > self._bar1_mid
            ):
                result = self._result(
                    Direction.LONG,
                    entry=h,
                    stop=low,
                    reason="od-rev long: fade DOWN bar1 through mid",
                    atr=atr,
                )
                self._reset()
                return result
            if (
                self._bar1_shape == "UP"
                and c < o
                and body_ratio >= self._body_ratio
                and c < self._bar1_mid
            ):
                result = self._result(
                    Direction.SHORT,
                    entry=low,
                    stop=h,
                    reason="od-rev short: fade UP bar1 through mid",
                    atr=atr,
                )
                self._reset()
                return result
        return None

    def _maybe_set_bar1(
        self,
        *,
        o: float,
        h: float,
        low: float,
        c: float,
        bar_range: float,
        body_ratio: float,
    ) -> None:
        if body_ratio < self._body_ratio:
            self._fsm = RevState.IDLE
            self._bars_collected = 1
            return None
        if c > o:
            shape = "UP"
        elif c < o:
            shape = "DOWN"
        else:
            self._fsm = RevState.IDLE
            self._bars_collected = 1
            return None
        self._fsm = RevState.BAR1_SET
        self._bar1_shape = shape
        self._bar1_mid = (h + low) / 2.0
        self._bar1_range = bar_range
        self._bars_collected = 1
        return None

    def _in_signal_window(
        self, bar_time: time, *, is_morning: bool, is_night: bool
    ) -> bool:
        if is_morning:
            return bar_time <= time(9, self._am_cut)
        if is_night:
            return bar_time <= time(21, self._pm_cut)
        return False

    def _bar1_atr_ok(self, atr: float) -> bool:
        if self._bar1_range <= 0 or atr <= 0:
            return False
        ratio = self._bar1_range / atr
        return self._min_bar1 <= ratio <= self._max_bar1

    def _reset(self) -> None:
        self._fsm = RevState.IDLE
        self._bar1_shape = ""
        self._bar1_mid = 0.0
        self._bar1_range = 0.0
        self._bars_collected = 0

    def _read_atr(self, am: Any) -> Optional[float]:
        fn = getattr(am, "atr", None)
        if not callable(fn):
            return None
        try:
            value = float(fn(self._atr_period))
        except (TypeError, ValueError):
            return None
        if value != value:
            return None
        return value

    def _build_pattern_state(self, *, confidence: float) -> PatternState:
        return PatternState(
            name="od_reversal",
            confidence=confidence,
            metadata={
                "fsm": self._fsm.value,
                "bar1_shape": self._bar1_shape,
                "bar1_mid": self._bar1_mid,
                "bar1_range": self._bar1_range,
                "bars_collected": self._bars_collected,
                "session_date": (
                    self._session_date.isoformat() if self._session_date else None
                ),
            },
        )

    def _result(
        self,
        direction: Direction,
        *,
        entry: float,
        stop: float,
        reason: str,
        atr: float,
    ) -> DetectionResult:
        return DetectionResult(
            detector_id=OPP19_REV_DETECTOR_ID,
            detector_version=OPP19_REV_DETECTOR_VERSION,
            opportunity_id=OPP19_REV_OPPORTUNITY_ID,
            status=DetectorStatus.EXPERIMENT,
            direction=direction,
            confidence=1.0,
            tags=(DetectorTag.REVERSAL, "custom:od_reversal"),
            entry=entry,
            stop=stop,
            reason=reason,
            metadata={
                "atr_period": self._atr_period,
                "opening_rev_body_ratio": self._body_ratio,
                "morning_cutoff_minute": self._am_cut,
                "night_cutoff_minute": self._pm_cut,
                "min_bar1_range_atr": self._min_bar1,
                "max_bar1_range_atr": self._max_bar1,
                "atr": atr,
                "bar1_shape": self._bar1_shape,
                "bar1_mid": self._bar1_mid,
                "timeframe": "5m",
            },
            pattern_state=self._build_pattern_state(confidence=1.0),
        )


OPP19_REV_DESCRIPTOR = DetectorDescriptor(
    id=OPP19_REV_DETECTOR_ID,
    version=OPP19_REV_DETECTOR_VERSION,
    status=DetectorStatus.EXPERIMENT,
    capability=DetectorCapability(
        directions=(Direction.LONG, Direction.SHORT),
        requires=frozenset(),
        produces=frozenset({DetectorTag.REVERSAL, "custom:od_reversal"}),
        timeframe="5m",
    ),
    factory=OPP19OpeningDriveReversalDetector,
    tags=(DetectorTag.REVERSAL, "custom:od_reversal"),
    metadata={
        "purpose": "cid011_opp19_rev_candidate",
        "alpha_claim": False,
        "spec": "OPP19_REV_MS_V0_1",
    },
)
