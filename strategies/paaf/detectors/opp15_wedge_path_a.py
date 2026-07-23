"""OPP15 wedge Path-A Candidate Detector; observations only.

PAAF rewrite of legacy Opp15Mixin Path A（OPP15_MS_V0_1）.
Path B' / MTF OUT OF SCOPE. Context ignored in detect().
Cross-bar FSM is explicit PatternState on the instance.
"""

from __future__ import annotations

from datetime import datetime
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
from strategies.paaf.morphology.wedge import (
    WedgeBar,
    scan_latest_bearish_wedge,
    scan_latest_bullish_wedge,
)
from strategies.paaf.registry import DetectorCapability, DetectorDescriptor

OPP15_DETECTOR_ID = "OPP15"
OPP15_DETECTOR_VERSION = "1.0.0"
OPP15_OPPORTUNITY_ID = "OPP15"
DEFAULT_ATR_PERIOD = 14
DEFAULT_WEDGE_N_MIN = 3
DEFAULT_WEDGE_ALPHA = 0.85
DEFAULT_ARM_MAX_BARS = 4
DEFAULT_STRONG_BAR_ATR_MULT = 1.0
DEFAULT_STRONG_BAR_BODY_RATIO = 0.6
DEFAULT_PRICETICK = 1.0


class WedgeState(str, Enum):
    IDLE = "IDLE"
    ARMED = "ARMED"


class OPP15WedgePathADetector(BaseDetector):
    """5m HH3/LL3 arm → strong-bar reverse through trigger; no Context."""

    metadata = DetectorMetadata(
        name=OPP15_DETECTOR_ID,
        version=OPP15_DETECTOR_VERSION,
        description="Wedge Path-A Candidate; E0（OPP15_MS_V0_1）",
        status="Candidate",
        category="Reversal",
        timeframe="5m",
        evidence_level="E0",
    )

    def __init__(
        self,
        *,
        atr_period: int = DEFAULT_ATR_PERIOD,
        wedge_n_min: int = DEFAULT_WEDGE_N_MIN,
        wedge_alpha_threshold: float = DEFAULT_WEDGE_ALPHA,
        wedge_arm_trigger_max_bars: int = DEFAULT_ARM_MAX_BARS,
        strong_bar_atr_mult: float = DEFAULT_STRONG_BAR_ATR_MULT,
        strong_bar_body_ratio: float = DEFAULT_STRONG_BAR_BODY_RATIO,
        pricetick: float = DEFAULT_PRICETICK,
    ) -> None:
        if not isinstance(atr_period, int) or atr_period < 2:
            raise ValueError("atr_period 必须是 >= 2 的 int")
        if wedge_n_min < 1:
            raise ValueError("wedge_n_min 必须 >= 1")
        if not 0 < wedge_alpha_threshold <= 1:
            raise ValueError("wedge_alpha_threshold 必须在 (0, 1]")
        if wedge_arm_trigger_max_bars < 1:
            raise ValueError("wedge_arm_trigger_max_bars 必须 >= 1")
        if strong_bar_atr_mult <= 0:
            raise ValueError("strong_bar_atr_mult 必须 > 0")
        if not 0 < strong_bar_body_ratio <= 1:
            raise ValueError("strong_bar_body_ratio 必须在 (0, 1]")
        if pricetick <= 0:
            raise ValueError("pricetick 必须 > 0")

        self._atr_period = atr_period
        self._n_min = int(wedge_n_min)
        self._alpha = float(wedge_alpha_threshold)
        self._arm_max = int(wedge_arm_trigger_max_bars)
        self._strong_atr = float(strong_bar_atr_mult)
        self._strong_body = float(strong_bar_body_ratio)
        self._tick = float(pricetick)

        self._fsm = WedgeState.IDLE
        self._direction = 0
        self._p3_price = 0.0
        self._trigger_line = 0.0
        self._arm_time: Optional[datetime] = None
        self._bar_dt: Optional[datetime] = None

    def note_bar_datetime(self, bar_dt: datetime) -> None:
        """Strategy injects completed 5m bar datetime."""
        self._bar_dt = bar_dt

    def set_pricetick(self, pricetick: float) -> None:
        if pricetick <= 0:
            raise ValueError("pricetick 必须 > 0")
        self._tick = float(pricetick)

    def adjust_levels(self, shift: float) -> None:
        """CbC price shift for armed p3 / trigger levels."""
        if abs(shift) < 1e-12:
            return
        if abs(self._p3_price) > 1e-12:
            self._p3_price += shift
        if abs(self._trigger_line) > 1e-12:
            self._trigger_line += shift

    @property
    def pattern_state(self) -> PatternState:
        return self._build_pattern_state(confidence=1.0)

    def load_pattern_state(self, state: PatternState | Mapping[str, Any]) -> None:
        data = state.to_dict() if isinstance(state, PatternState) else dict(state)
        meta = dict(data.get("metadata") or {})
        self._fsm = WedgeState(str(meta.get("fsm", WedgeState.IDLE.value)))
        self._direction = int(meta.get("direction", 0))
        self._p3_price = float(meta.get("p3_price", 0.0))
        self._trigger_line = float(meta.get("trigger_line", 0.0))
        arm = meta.get("arm_time")
        self._arm_time = datetime.fromisoformat(arm) if arm else None

    def detect(
        self,
        am: Any,
        context: Context,
    ) -> Optional[DetectionResult]:
        del context  # OPP15_MS: no Context gate
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

        if self._fsm is WedgeState.ARMED:
            return self._process_armed(
                am, atr=atr, o=o, h=h, low=low, c=c, bar_range=bar_range
            )

        self._try_arm(am, atr=atr)
        return None

    def _try_arm(self, am: Any, *, atr: float) -> None:
        bars = self._bars_from_am(am)
        if len(bars) < 7:
            return

        # Prefer HH3 then LL3（legacy scanned both under context gates; we scan both）
        bear = scan_latest_bearish_wedge(
            bars,
            atr,
            tick_size=self._tick,
            n_min=self._n_min,
            alpha_threshold=self._alpha,
        )
        if (
            bear.get("status") == "wedge_valid:hh3"
            and self._can_arm_after_p3(bars, int(bear.get("p3_idx", -1)))
        ):
            p3 = float(bear.get("p3_high", 0.0) or 0.0)
            if p3 > 0:
                self._fsm = WedgeState.ARMED
                self._direction = -1
                self._p3_price = p3
                self._arm_time = self._bar_dt
                self._trigger_line = self._trigger_from_am(am, direction=-1)
                return

        bull = scan_latest_bullish_wedge(
            bars,
            atr,
            tick_size=self._tick,
            n_min=self._n_min,
            alpha_threshold=self._alpha,
        )
        if (
            bull.get("status") == "wedge_valid:ll3"
            and self._can_arm_after_p3(bars, int(bull.get("p3_idx", -1)))
        ):
            p3 = float(bull.get("p3_low", 0.0) or 0.0)
            if p3 > 0:
                self._fsm = WedgeState.ARMED
                self._direction = 1
                self._p3_price = p3
                self._arm_time = self._bar_dt
                self._trigger_line = self._trigger_from_am(am, direction=1)

    def _process_armed(
        self,
        am: Any,
        *,
        atr: float,
        o: float,
        h: float,
        low: float,
        c: float,
        bar_range: float,
    ) -> Optional[DetectionResult]:
        tick = self._tick
        p3 = self._p3_price
        d = self._direction

        if d == -1 and h > p3 + tick:
            self._reset()
            return None
        if d == 1 and low < p3 - tick:
            self._reset()
            return None

        bars_since = 0
        if self._arm_time is not None and self._bar_dt is not None:
            bars_since = int((self._bar_dt - self._arm_time).total_seconds() / 300)
        if bars_since > self._arm_max:
            self._reset()
            return None

        self._trigger_line = self._trigger_from_am(am, direction=d)
        if self._trigger_line <= 0:
            return None

        if not self._is_strong_bar(abs(c - o), bar_range, atr):
            return None

        if d == -1:
            if c < o and c < self._trigger_line:
                result = self._result(
                    Direction.SHORT,
                    entry=low,
                    stop=p3 + tick,
                    reason="wedge Path-A short: HH3 arm + strong reverse",
                    atr=atr,
                )
                self._reset()
                return result
        elif d == 1:
            if c > o and c > self._trigger_line:
                result = self._result(
                    Direction.LONG,
                    entry=h,
                    stop=p3 - tick,
                    reason="wedge Path-A long: LL3 arm + strong reverse",
                    atr=atr,
                )
                self._reset()
                return result
        return None

    @staticmethod
    def _can_arm_after_p3(bars: list[WedgeBar], p3_idx: int) -> bool:
        if p3_idx < 0:
            return False
        return len(bars) - 1 >= p3_idx + 2

    def _trigger_from_am(self, am: Any, *, direction: int) -> float:
        """Trigger from two completed lows/highs BEFORE the signal bar.

        Declared vs legacy: legacy used min(low[-1], low[-2]) including the
        current bar, which makes close < trigger impossible. Path A intent is
        reverse through the prior pullback extreme.
        """
        count = int(getattr(am, "count", 0) or 0)
        if count < 3:
            return 0.0
        if direction < 0:
            return min(float(am.low[-2]), float(am.low[-3]))
        if direction > 0:
            return max(float(am.high[-2]), float(am.high[-3]))
        return 0.0

    def _bars_from_am(self, am: Any) -> list[WedgeBar]:
        n = min(int(am.count), int(getattr(am, "size", am.count)))
        out: list[WedgeBar] = []
        for i in range(n):
            neg = n - i
            out.append(
                WedgeBar(
                    open_price=float(am.open[-neg]),
                    high_price=float(am.high[-neg]),
                    low_price=float(am.low[-neg]),
                    close_price=float(am.close[-neg]),
                    index=i,
                )
            )
        return out

    def _is_strong_bar(self, body: float, bar_range: float, atr: float) -> bool:
        return (
            body >= bar_range * self._strong_body
            and bar_range > atr * self._strong_atr
        )

    def _reset(self) -> None:
        self._fsm = WedgeState.IDLE
        self._direction = 0
        self._p3_price = 0.0
        self._trigger_line = 0.0
        self._arm_time = None

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
            name="wedge_path_a",
            confidence=confidence,
            metadata={
                "fsm": self._fsm.value,
                "direction": self._direction,
                "p3_price": self._p3_price,
                "trigger_line": self._trigger_line,
                "arm_time": self._arm_time.isoformat() if self._arm_time else None,
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
            detector_id=OPP15_DETECTOR_ID,
            detector_version=OPP15_DETECTOR_VERSION,
            opportunity_id=OPP15_OPPORTUNITY_ID,
            status=DetectorStatus.EXPERIMENT,
            direction=direction,
            confidence=1.0,
            tags=(DetectorTag.REVERSAL, "custom:wedge_path_a"),
            entry=entry,
            stop=stop,
            reason=reason,
            metadata={
                "atr_period": self._atr_period,
                "wedge_n_min": self._n_min,
                "wedge_alpha_threshold": self._alpha,
                "wedge_arm_trigger_max_bars": self._arm_max,
                "strong_bar_atr_mult": self._strong_atr,
                "strong_bar_body_ratio": self._strong_body,
                "atr": atr,
                "p3_price": self._p3_price,
                "trigger_line": self._trigger_line,
                "timeframe": "5m",
            },
            pattern_state=self._build_pattern_state(confidence=1.0),
        )


OPP15_DESCRIPTOR = DetectorDescriptor(
    id=OPP15_DETECTOR_ID,
    version=OPP15_DETECTOR_VERSION,
    status=DetectorStatus.EXPERIMENT,
    capability=DetectorCapability(
        directions=(Direction.LONG, Direction.SHORT),
        requires=frozenset(),
        produces=frozenset({DetectorTag.REVERSAL, "custom:wedge_path_a"}),
        timeframe="5m",
    ),
    factory=OPP15WedgePathADetector,
    tags=(DetectorTag.REVERSAL, "custom:wedge_path_a"),
    metadata={
        "purpose": "cid009_opp15_candidate",
        "alpha_claim": False,
        "spec": "OPP15_MS_V0_1",
    },
)
