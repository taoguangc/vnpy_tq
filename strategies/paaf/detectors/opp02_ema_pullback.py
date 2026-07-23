"""OPP02 EMA-pullback Candidate Detector; observations only, never trading.

PAAF rewrite of legacy Opp02Mixin morphology（OPP02_MS_V0_1）.
Context is ignored in detect().
always_in replaced by close-vs-EMA side proxy.
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

OPP02_DETECTOR_ID = "OPP02"
OPP02_DETECTOR_VERSION = "1.0.0"
OPP02_OPPORTUNITY_ID = "OPP02"
DEFAULT_ATR_PERIOD = 14
DEFAULT_EMA_PERIOD = 20
DEFAULT_EMA_PULLBACK_TOUCH_ATR = 1.0
DEFAULT_EMA_PULLBACK_MIN_BODY_RATIO = 0.35
DEFAULT_WICK_MAX_FRACTION = 0.45


class OPP02EmaPullbackDetector(BaseDetector):
    """EMA-side pullback touch + directional body; no Context filter."""

    metadata = DetectorMetadata(
        name=OPP02_DETECTOR_ID,
        version=OPP02_DETECTOR_VERSION,
        description="EMA-pullback Candidate; E0 observation only（OPP02_MS_V0_1）",
        status="Candidate",
        category="Trend",
        timeframe="5m",
        evidence_level="E0",
    )

    def __init__(
        self,
        *,
        atr_period: int = DEFAULT_ATR_PERIOD,
        ema_period: int = DEFAULT_EMA_PERIOD,
        ema_pullback_touch_atr: float = DEFAULT_EMA_PULLBACK_TOUCH_ATR,
        ema_pullback_min_body_ratio: float = DEFAULT_EMA_PULLBACK_MIN_BODY_RATIO,
        wick_max_fraction: float = DEFAULT_WICK_MAX_FRACTION,
    ) -> None:
        if not isinstance(atr_period, int) or atr_period < 2:
            raise ValueError("atr_period 必须是 >= 2 的 int")
        if not isinstance(ema_period, int) or ema_period < 2:
            raise ValueError("ema_period 必须是 >= 2 的 int")
        if ema_pullback_touch_atr <= 0:
            raise ValueError("ema_pullback_touch_atr 必须 > 0")
        if not 0 < ema_pullback_min_body_ratio <= 1:
            raise ValueError("ema_pullback_min_body_ratio 必须在 (0, 1]")
        if not 0 < wick_max_fraction <= 1:
            raise ValueError("wick_max_fraction 必须在 (0, 1]")
        self._atr_period = atr_period
        self._ema_period = ema_period
        self._touch_atr = float(ema_pullback_touch_atr)
        self._min_body = float(ema_pullback_min_body_ratio)
        self._wick_max = float(wick_max_fraction)

    def detect(
        self,
        am: Any,
        context: Context,
    ) -> Optional[DetectionResult]:
        del context  # OPP02_MS: no Context gate
        if not am_is_inited(am):
            return None
        need = max(self._atr_period, self._ema_period) + 2
        bars = bars_from_am(am, need)
        if len(bars) < 1:
            return None

        atr = self._read_atr(am)
        ema = self._read_ema(am)
        if atr is None or ema is None or atr <= 0 or ema <= 0:
            return None

        bar = bars[-1]
        bar_range = bar.high - bar.low
        if bar_range <= 0:
            return None
        body = abs(bar.close - bar.open)
        body_ratio = body / bar_range
        if body_ratio < self._min_body:
            return None

        touch_band = atr * self._touch_atr

        # Long: close above EMA · low touches EMA band · bullish · limited upper wick
        if bar.close > ema:
            touched = bar.low <= ema + touch_band
            upper_wick = bar.high - max(bar.open, bar.close)
            if (
                touched
                and bar.close > bar.open
                and upper_wick < bar_range * self._wick_max
            ):
                return self._result(
                    Direction.LONG,
                    entry=bar.high,
                    stop=bar.low,
                    reason="ema-pullback long: close>EMA + touch + bullish body",
                    atr=atr,
                    ema=ema,
                )

        # Short: close below EMA · high touches EMA band · bearish · limited lower wick
        if bar.close < ema:
            touched = bar.high >= ema - touch_band
            lower_wick = min(bar.open, bar.close) - bar.low
            if (
                touched
                and bar.close < bar.open
                and lower_wick < bar_range * self._wick_max
            ):
                return self._result(
                    Direction.SHORT,
                    entry=bar.low,
                    stop=bar.high,
                    reason="ema-pullback short: close<EMA + touch + bearish body",
                    atr=atr,
                    ema=ema,
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
        if value != value:
            return None
        return value

    def _read_ema(self, am: Any) -> Optional[float]:
        fn = getattr(am, "ema", None)
        if not callable(fn):
            return None
        try:
            value = float(fn(self._ema_period))
        except (TypeError, ValueError):
            return None
        if value != value:
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
        ema: float,
    ) -> DetectionResult:
        return DetectionResult(
            detector_id=OPP02_DETECTOR_ID,
            detector_version=OPP02_DETECTOR_VERSION,
            opportunity_id=OPP02_OPPORTUNITY_ID,
            status=DetectorStatus.EXPERIMENT,
            direction=direction,
            confidence=1.0,
            tags=(DetectorTag.TREND, "custom:ema_pullback"),
            entry=entry,
            stop=stop,
            reason=reason,
            metadata={
                "atr_period": self._atr_period,
                "ema_period": self._ema_period,
                "ema_pullback_touch_atr": self._touch_atr,
                "ema_pullback_min_body_ratio": self._min_body,
                "wick_max_fraction": self._wick_max,
                "atr": atr,
                "ema": ema,
                "timeframe": "5m",
            },
            pattern_state=PatternState(
                name="ema_pullback",
                confidence=1.0,
                metadata={"direction": direction.value},
            ),
        )


OPP02_DESCRIPTOR = DetectorDescriptor(
    id=OPP02_DETECTOR_ID,
    version=OPP02_DETECTOR_VERSION,
    status=DetectorStatus.EXPERIMENT,
    capability=DetectorCapability(
        directions=(Direction.LONG, Direction.SHORT),
        requires=frozenset(),
        produces=frozenset({DetectorTag.TREND, "custom:ema_pullback"}),
        timeframe="5m",
    ),
    factory=OPP02EmaPullbackDetector,
    tags=(DetectorTag.TREND, "custom:ema_pullback"),
    metadata={
        "purpose": "cid008_opp02_candidate",
        "alpha_claim": False,
        "spec": "OPP02_MS_V0_1",
    },
)
