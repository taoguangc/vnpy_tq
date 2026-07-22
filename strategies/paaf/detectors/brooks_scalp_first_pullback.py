"""Brooks Scalp first-pullback Candidate Detector（PAAF rewrite）.

Hypothesis class（from CID_001 / PRC-BROOKS_SCALP-v1）:
  1m trend-leg → pullback → stop-entry levels（1R）

Does not order, read position, or mutate Strategy.
Cross-bar FSM is explicit PatternState on the instance.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Mapping, Optional, Sequence

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

DETECTOR_ID = "BROOKS_SCALP_FP"
DETECTOR_VERSION = "0.1.0"
OPPORTUNITY_ID = "BROOKS_SCALP_FP"

DEFAULT_EMA_PERIOD = 20
DEFAULT_ATR_PERIOD = 20
DEFAULT_TREND_LEG_ATR = 1.0
DEFAULT_PULLBACK_ATR = 0.2
DEFAULT_RISK_REWARD = 1.0
DEFAULT_PRICETICK = 1.0


class FsmState(str, Enum):
    IDLE = "IDLE"
    WAIT_PULLBACK = "WAIT_PULLBACK"
    PULLBACK = "PULLBACK"


class BrooksScalpFirstPullbackDetector(BaseDetector):
    """Pure detection of first-pullback entry levels on 1m windows."""

    metadata = DetectorMetadata(
        name=DETECTOR_ID,
        version=DETECTOR_VERSION,
        description=(
            "PAAF rewrite of brooks_scalp first-pullback; "
            "E0 Candidate; no Alpha claim"
        ),
        status="Candidate",
        category="Trend",
        timeframe="1m",
        evidence_level="E0",
    )

    def __init__(
        self,
        *,
        ema_period: int = DEFAULT_EMA_PERIOD,
        atr_period: int = DEFAULT_ATR_PERIOD,
        trend_leg_atr: float = DEFAULT_TREND_LEG_ATR,
        pullback_atr: float = DEFAULT_PULLBACK_ATR,
        risk_reward: float = DEFAULT_RISK_REWARD,
        pricetick: float = DEFAULT_PRICETICK,
    ) -> None:
        if ema_period < 2 or atr_period < 2:
            raise ValueError("ema_period / atr_period 必须 >= 2")
        if trend_leg_atr <= 0 or pullback_atr <= 0 or risk_reward <= 0:
            raise ValueError("atr 倍数与 risk_reward 必须 > 0")
        if pricetick <= 0:
            raise ValueError("pricetick 必须 > 0")

        self._ema_period = int(ema_period)
        self._atr_period = int(atr_period)
        self._trend_leg_atr = float(trend_leg_atr)
        self._pullback_atr = float(pullback_atr)
        self._risk_reward = float(risk_reward)
        self._pricetick = float(pricetick)

        self._fsm = FsmState.IDLE
        self._trend = 0
        self._pullback_low = 0.0
        self._pullback_high = 0.0
        self._ema = 0.0
        self._atr = 0.0

    def set_pricetick(self, pricetick: float) -> None:
        if pricetick <= 0:
            raise ValueError("pricetick 必须 > 0")
        self._pricetick = float(pricetick)

    @property
    def pattern_state(self) -> PatternState:
        return self._build_pattern_state(confidence=1.0)

    def load_pattern_state(self, state: PatternState | Mapping[str, Any]) -> None:
        """Restore explicit FSM from PatternState / dict."""

        data = state.to_dict() if isinstance(state, PatternState) else dict(state)
        meta = dict(data.get("metadata") or {})
        self._fsm = FsmState(str(meta.get("fsm", FsmState.IDLE.value)))
        self._trend = int(meta.get("trend", 0))
        self._pullback_low = float(meta.get("pullback_low", 0.0))
        self._pullback_high = float(meta.get("pullback_high", 0.0))
        self._ema = float(meta.get("ema", 0.0))
        self._atr = float(meta.get("atr", 0.0))

    def detect(
        self,
        am: Any,
        context: Context,
    ) -> Optional[DetectionResult]:
        del context  # rewrite v0.1: Context not in signal path
        if not am_is_inited(am):
            return None
        if not self._update_indicators(am):
            return None

        self._detect_trend(am)
        if self._trend == 0:
            self._fsm = FsmState.IDLE
            return None

        if self._fsm is FsmState.IDLE:
            if self._check_trend_leg(am):
                self._fsm = FsmState.WAIT_PULLBACK
            return None

        if self._fsm is FsmState.WAIT_PULLBACK:
            if self._check_pullback(am):
                self._fsm = FsmState.PULLBACK
                self._pullback_low = float(am.low[-1])
                self._pullback_high = float(am.high[-1])
            return None

        # PULLBACK
        if self._trend == 1:
            self._pullback_low = min(self._pullback_low, float(am.low[-1]))
            if self._bull_signal(am):
                return self._emit_long(am)
        elif self._trend == -1:
            self._pullback_high = max(self._pullback_high, float(am.high[-1]))
            if self._bear_signal(am):
                return self._emit_short(am)
        return None

    def _emit_long(self, am: Any) -> Optional[DetectionResult]:
        tick = self._pricetick
        entry = float(am.high[-1]) + tick
        stop = self._pullback_low - tick
        risk = entry - stop
        self._fsm = FsmState.IDLE
        if risk <= tick:
            return None
        target = entry + risk * self._risk_reward
        return self._result(
            Direction.LONG,
            entry=entry,
            stop=stop,
            target=target,
            reason="first_pullback_long_stop_entry",
        )

    def _emit_short(self, am: Any) -> Optional[DetectionResult]:
        tick = self._pricetick
        entry = float(am.low[-1]) - tick
        stop = self._pullback_high + tick
        risk = stop - entry
        self._fsm = FsmState.IDLE
        if risk <= tick:
            return None
        target = entry - risk * self._risk_reward
        return self._result(
            Direction.SHORT,
            entry=entry,
            stop=stop,
            target=target,
            reason="first_pullback_short_stop_entry",
        )

    def _result(
        self,
        direction: Direction,
        *,
        entry: float,
        stop: float,
        target: float,
        reason: str,
    ) -> DetectionResult:
        return DetectionResult(
            detector_id=DETECTOR_ID,
            detector_version=DETECTOR_VERSION,
            opportunity_id=OPPORTUNITY_ID,
            status=DetectorStatus.EXPERIMENT,
            direction=direction,
            confidence=1.0,
            tags=(DetectorTag.TREND, DetectorTag.PULLBACK, "custom:first_pullback"),
            entry=entry,
            stop=stop,
            target=target,
            reason=reason,
            metadata={
                "ema_period": self._ema_period,
                "atr_period": self._atr_period,
                "trend_leg_atr": self._trend_leg_atr,
                "pullback_atr": self._pullback_atr,
                "risk_reward": self._risk_reward,
                "pricetick": self._pricetick,
                "timeframe": "1m",
                "lineage_parent": "CID_001_BROOKS_SCALP_V0_1",
                "strategy_id_target": "STRAT_TREND_BROOKS_SCALP_02",
            },
            pattern_state=self._build_pattern_state(confidence=1.0),
        )

    def _build_pattern_state(self, *, confidence: float) -> PatternState:
        return PatternState(
            name="brooks_scalp_first_pullback_fsm",
            confidence=confidence,
            metadata={
                "fsm": self._fsm.value,
                "trend": self._trend,
                "pullback_low": self._pullback_low,
                "pullback_high": self._pullback_high,
                "ema": self._ema,
                "atr": self._atr,
            },
        )

    def _update_indicators(self, am: Any) -> bool:
        need = max(self._ema_period, self._atr_period, 6) + 1
        n = _window_len(am)
        if n < need:
            return False
        self._ema = float(am.ema(self._ema_period))
        self._atr = float(am.atr(self._atr_period))
        if self._atr <= 0:
            return False
        return True

    def _detect_trend(self, am: Any) -> None:
        close = am.close
        ema_array = am.ema(self._ema_period, array=True)
        ema_now = float(ema_array[-1])
        ema_prev = float(ema_array[-6])
        bull_bars = sum(1 for i in range(-5, 0) if float(close[i]) > float(ema_array[i]))
        bear_bars = sum(1 for i in range(-5, 0) if float(close[i]) < float(ema_array[i]))
        if float(close[-1]) > ema_now and ema_now > ema_prev and bull_bars >= 4:
            self._trend = 1
        elif float(close[-1]) < ema_now and ema_now < ema_prev and bear_bars >= 4:
            self._trend = -1
        else:
            self._trend = 0

    def _check_trend_leg(self, am: Any) -> bool:
        move = abs(float(am.close[-1]) - float(am.close[-6]))
        return move > self._atr * self._trend_leg_atr

    def _check_pullback(self, am: Any) -> bool:
        if self._trend == 1:
            distance = abs(float(am.low[-1]) - self._ema)
        else:
            distance = abs(float(am.high[-1]) - self._ema)
        return distance < self._atr * self._pullback_atr

    def _bull_signal(self, am: Any) -> bool:
        high = float(am.high[-1])
        low = float(am.low[-1])
        close = float(am.close[-1])
        open_ = float(am.open[-1])
        if high == low:
            return False
        body_ratio = abs(close - open_) / (high - low)
        return close > open_ and close > float(am.high[-2]) and body_ratio > 0.4

    def _bear_signal(self, am: Any) -> bool:
        high = float(am.high[-1])
        low = float(am.low[-1])
        close = float(am.close[-1])
        open_ = float(am.open[-1])
        if high == low:
            return False
        body_ratio = abs(close - open_) / (high - low)
        return close < open_ and close < float(am.low[-2]) and body_ratio > 0.4


def _window_len(am: Any) -> int:
    count = getattr(am, "count", None)
    if isinstance(count, int) and count >= 0:
        return count
    close = getattr(am, "close", None)
    if isinstance(close, Sequence):
        return len(close)
    return 0


BROOKS_SCALP_FP_DESCRIPTOR = DetectorDescriptor(
    id=DETECTOR_ID,
    version=DETECTOR_VERSION,
    status=DetectorStatus.EXPERIMENT,
    capability=DetectorCapability(
        directions=(Direction.LONG, Direction.SHORT),
        requires=frozenset(),
        produces=frozenset(
            {DetectorTag.TREND, DetectorTag.PULLBACK, "custom:first_pullback"}
        ),
        timeframe="1m",
    ),
    factory=BrooksScalpFirstPullbackDetector,
    tags=(DetectorTag.TREND, DetectorTag.PULLBACK, "custom:first_pullback"),
    metadata={
        "purpose": "prc_brooks_scalp_v1_rewrite",
        "alpha_claim": False,
        "strategy_id_target": "STRAT_TREND_BROOKS_SCALP_02",
        "lineage_parent": "CID_001_BROOKS_SCALP_V0_1",
    },
)
