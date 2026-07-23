"""OPP19 opening-drive breakout Candidate Detector; observations only.

PAAF rewrite of legacy Opp19Mixin Path A（OPP19_MS_V0_1）.
OD_REV path is OUT OF SCOPE. Context is ignored in detect().
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

OPP19_DETECTOR_ID = "OPP19"
OPP19_DETECTOR_VERSION = "1.0.0"
OPP19_OPPORTUNITY_ID = "OPP19"
DEFAULT_ATR_PERIOD = 14
DEFAULT_OPENING_DRIVE_BARS = 6
DEFAULT_OPENING_DRIVE_MIN_BODY = 0.50
DEFAULT_OPENING_DRIVE_RANGE_ATR_MIN = 0.2
DEFAULT_STRONG_BAR_ATR_MULT = 1.0
DEFAULT_STRONG_BAR_BODY_RATIO = 0.6
DEFAULT_RANGE_SET_MAX_BARS = 24


class OdState(str, Enum):
    IDLE = "IDLE"
    COLLECTING = "COLLECTING"
    RANGE_SET = "RANGE_SET"


class OPP19OpeningDriveBreakoutDetector(BaseDetector):
    """Session OR-range breakout after N opening bars; no Context / OD_REV."""

    metadata = DetectorMetadata(
        name=OPP19_DETECTOR_ID,
        version=OPP19_DETECTOR_VERSION,
        description="Opening-drive breakout Candidate; E0（OPP19_MS_V0_1）",
        status="Candidate",
        category="Session",
        timeframe="5m",
        evidence_level="E0",
    )

    def __init__(
        self,
        *,
        atr_period: int = DEFAULT_ATR_PERIOD,
        opening_drive_bars: int = DEFAULT_OPENING_DRIVE_BARS,
        opening_drive_min_body: float = DEFAULT_OPENING_DRIVE_MIN_BODY,
        opening_drive_range_atr_min: float = DEFAULT_OPENING_DRIVE_RANGE_ATR_MIN,
        strong_bar_atr_mult: float = DEFAULT_STRONG_BAR_ATR_MULT,
        strong_bar_body_ratio: float = DEFAULT_STRONG_BAR_BODY_RATIO,
        range_set_max_bars: int = DEFAULT_RANGE_SET_MAX_BARS,
    ) -> None:
        if not isinstance(atr_period, int) or atr_period < 2:
            raise ValueError("atr_period 必须是 >= 2 的 int")
        if opening_drive_bars < 2:
            raise ValueError("opening_drive_bars 必须 >= 2")
        if not 0 < opening_drive_min_body <= 1:
            raise ValueError("opening_drive_min_body 必须在 (0, 1]")
        if opening_drive_range_atr_min <= 0:
            raise ValueError("opening_drive_range_atr_min 必须 > 0")
        if strong_bar_atr_mult <= 0:
            raise ValueError("strong_bar_atr_mult 必须 > 0")
        if not 0 < strong_bar_body_ratio <= 1:
            raise ValueError("strong_bar_body_ratio 必须在 (0, 1]")
        if range_set_max_bars < opening_drive_bars:
            raise ValueError("range_set_max_bars 必须 >= opening_drive_bars")

        self._atr_period = atr_period
        self._od_bars = int(opening_drive_bars)
        self._min_body = float(opening_drive_min_body)
        self._range_atr_min = float(opening_drive_range_atr_min)
        self._strong_atr = float(strong_bar_atr_mult)
        self._strong_body = float(strong_bar_body_ratio)
        self._range_set_max = int(range_set_max_bars)

        self._fsm = OdState.IDLE
        self._od_high = 0.0
        self._od_low = 0.0
        self._od_bars_collected = 0
        self._od_session_date: Optional[date] = None
        self._bar_dt: Optional[datetime] = None

    def note_bar_datetime(self, bar_dt: datetime) -> None:
        """Strategy injects completed 5m bar datetime（ArrayManager 无逐 bar 时间）."""
        self._bar_dt = bar_dt

    def adjust_or_levels(self, shift: float) -> None:
        """CbC price shift for active OR levels（explicit surface, not Strategy FSM）."""
        if abs(shift) < 1e-12:
            return
        if abs(self._od_high) > 1e-12:
            self._od_high += shift
        if abs(self._od_low) > 1e-12:
            self._od_low += shift

    @property
    def pattern_state(self) -> PatternState:
        return self._build_pattern_state(confidence=1.0)

    def load_pattern_state(self, state: PatternState | Mapping[str, Any]) -> None:
        data = state.to_dict() if isinstance(state, PatternState) else dict(state)
        meta = dict(data.get("metadata") or {})
        self._fsm = OdState(str(meta.get("fsm", OdState.IDLE.value)))
        self._od_high = float(meta.get("od_high", 0.0))
        self._od_low = float(meta.get("od_low", 0.0))
        self._od_bars_collected = int(meta.get("od_bars_collected", 0))
        session = meta.get("od_session_date")
        self._od_session_date = date.fromisoformat(session) if session else None

    def detect(
        self,
        am: Any,
        context: Context,
    ) -> Optional[DetectionResult]:
        del context  # OPP19_MS: no Context gate
        if not am_is_inited(am):
            return None
        if self._bar_dt is None:
            return None

        atr = self._read_atr(am)
        if atr is None or atr <= 0:
            return None

        o = float(am.open[-1])
        h = float(am.high[-1])
        l = float(am.low[-1])
        c = float(am.close[-1])
        bar_range = h - l
        if bar_range <= 0:
            return None
        body = abs(c - o)
        body_ratio = body / bar_range

        bar_time = self._bar_dt.time()
        bar_date = self._bar_dt.date()
        is_morning = time(9, 0) <= bar_time <= time(11, 30)
        is_night = time(21, 0) <= bar_time <= time(23, 0)
        if not (is_morning or is_night):
            if self._fsm is not OdState.IDLE:
                self._reset()
            return None

        session_changed = bar_date != self._od_session_date
        new_morning = is_morning and bar_time < time(9, 20) and self._fsm is OdState.IDLE
        new_night = is_night and bar_time < time(21, 20) and self._fsm is OdState.IDLE
        if session_changed or new_morning or new_night:
            self._reset()
            self._fsm = OdState.COLLECTING
            self._od_session_date = bar_date
            self._od_high = h
            self._od_low = l
            self._od_bars_collected = 1
            return None

        if self._fsm is OdState.IDLE:
            return None

        if self._fsm is OdState.COLLECTING:
            self._od_high = max(self._od_high, h)
            self._od_low = min(self._od_low, l)
            self._od_bars_collected += 1
            if self._od_bars_collected >= self._od_bars:
                if self._od_high - self._od_low >= atr * self._range_atr_min:
                    self._fsm = OdState.RANGE_SET
                else:
                    self._reset()
            return None

        if self._fsm is OdState.RANGE_SET:
            self._od_bars_collected += 1
            if self._od_bars_collected > self._range_set_max:
                self._reset()
                return None
            if not self._is_strong_bar(body, bar_range, atr):
                return None
            if (
                c > self._od_high
                and c > o
                and body_ratio >= self._min_body
            ):
                self._reset()
                return self._result(
                    Direction.LONG,
                    entry=h,
                    stop=l,
                    reason="od-breakout long: close > OR high + strong body",
                    atr=atr,
                )
            if (
                c < self._od_low
                and c < o
                and body_ratio >= self._min_body
            ):
                self._reset()
                return self._result(
                    Direction.SHORT,
                    entry=l,
                    stop=h,
                    reason="od-breakout short: close < OR low + strong body",
                    atr=atr,
                )
        return None

    def _reset(self) -> None:
        self._fsm = OdState.IDLE
        self._od_high = 0.0
        self._od_low = 0.0
        self._od_bars_collected = 0
        self._od_session_date = None

    def _is_strong_bar(self, body: float, bar_range: float, atr: float) -> bool:
        return (
            body >= bar_range * self._strong_body
            and bar_range > atr * self._strong_atr
        )

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
            name="opening_drive_breakout",
            confidence=confidence,
            metadata={
                "fsm": self._fsm.value,
                "od_high": self._od_high,
                "od_low": self._od_low,
                "od_bars_collected": self._od_bars_collected,
                "od_session_date": (
                    self._od_session_date.isoformat() if self._od_session_date else None
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
            detector_id=OPP19_DETECTOR_ID,
            detector_version=OPP19_DETECTOR_VERSION,
            opportunity_id=OPP19_OPPORTUNITY_ID,
            status=DetectorStatus.EXPERIMENT,
            direction=direction,
            confidence=1.0,
            tags=(DetectorTag.TREND, "custom:opening_drive_breakout"),
            entry=entry,
            stop=stop,
            reason=reason,
            metadata={
                "atr_period": self._atr_period,
                "opening_drive_bars": self._od_bars,
                "opening_drive_min_body": self._min_body,
                "opening_drive_range_atr_min": self._range_atr_min,
                "strong_bar_atr_mult": self._strong_atr,
                "strong_bar_body_ratio": self._strong_body,
                "atr": atr,
                "timeframe": "5m",
            },
            pattern_state=self._build_pattern_state(confidence=1.0),
        )


OPP19_DESCRIPTOR = DetectorDescriptor(
    id=OPP19_DETECTOR_ID,
    version=OPP19_DETECTOR_VERSION,
    status=DetectorStatus.EXPERIMENT,
    capability=DetectorCapability(
        directions=(Direction.LONG, Direction.SHORT),
        requires=frozenset(),
        produces=frozenset({DetectorTag.TREND, "custom:opening_drive_breakout"}),
        timeframe="5m",
    ),
    factory=OPP19OpeningDriveBreakoutDetector,
    tags=(DetectorTag.TREND, "custom:opening_drive_breakout"),
    metadata={
        "purpose": "cid007_opp19_od_breakout_candidate",
        "alpha_claim": False,
        "spec": "OPP19_MS_V0_1",
        "od_rev": False,
    },
)
