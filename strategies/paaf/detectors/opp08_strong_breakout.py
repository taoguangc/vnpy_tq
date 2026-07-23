"""OPP08 strong-breakout Candidate Detector; observations only, never trading.

PAAF rewrite of legacy Opp08Mixin morphology（OPP08_MS_V0_1）.
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

OPP08_DETECTOR_ID = "OPP08"
OPP08_DETECTOR_VERSION = "1.0.0"
OPP08_OPPORTUNITY_ID = "OPP08"
DEFAULT_ATR_PERIOD = 14
DEFAULT_EMA_PERIOD = 20
DEFAULT_STRONG_BAR_ATR_MULT = 1.0
DEFAULT_STRONG_BAR_BODY_RATIO = 0.6


class OPP08StrongBreakoutDetector(BaseDetector):
    """EMA-side strong bar beyond prior extreme; no Context filter."""

    metadata = DetectorMetadata(
        name=OPP08_DETECTOR_ID,
        version=OPP08_DETECTOR_VERSION,
        description="Strong-breakout Candidate; E0 observation only（OPP08_MS_V0_1）",
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
        strong_bar_atr_mult: float = DEFAULT_STRONG_BAR_ATR_MULT,
        strong_bar_body_ratio: float = DEFAULT_STRONG_BAR_BODY_RATIO,
    ) -> None:
        if not isinstance(atr_period, int) or atr_period < 2:
            raise ValueError("atr_period 必须是 >= 2 的 int")
        if not isinstance(ema_period, int) or ema_period < 2:
            raise ValueError("ema_period 必须是 >= 2 的 int")
        if strong_bar_atr_mult <= 0:
            raise ValueError("strong_bar_atr_mult 必须 > 0")
        if not 0 < strong_bar_body_ratio <= 1:
            raise ValueError("strong_bar_body_ratio 必须在 (0, 1]")
        self._atr_period = atr_period
        self._ema_period = ema_period
        self._strong_atr = float(strong_bar_atr_mult)
        self._strong_body = float(strong_bar_body_ratio)

    def detect(
        self,
        am: Any,
        context: Context,
    ) -> Optional[DetectionResult]:
        del context  # OPP08_MS: no Context gate
        if not am_is_inited(am):
            return None
        need = max(self._atr_period, self._ema_period) + 2
        bars = bars_from_am(am, need)
        if len(bars) < 2:
            return None

        atr = self._read_atr(am)
        ema = self._read_ema(am)
        if atr is None or ema is None or atr <= 0:
            return None

        prev = bars[-2]
        bar = bars[-1]
        bar_range = bar.high - bar.low
        if bar_range <= 0:
            return None
        body = abs(bar.close - bar.open)
        if not self._is_strong_bar(body, bar_range, atr):
            return None

        # Long: bullish strong bar above EMA and prior high
        if (
            bar.close > bar.open
            and bar.close > ema
            and bar.close > prev.high
        ):
            return self._result(
                Direction.LONG,
                entry=bar.high,
                stop=bar.low,
                reason="strong-breakout long: EMA side + close > prior high",
                atr=atr,
                ema=ema,
            )

        # Short: bearish strong bar below EMA and prior low（symmetric）
        if (
            bar.close < bar.open
            and bar.close < ema
            and bar.close < prev.low
        ):
            return self._result(
                Direction.SHORT,
                entry=bar.low,
                stop=bar.high,
                reason="strong-breakout short: EMA side + close < prior low",
                atr=atr,
                ema=ema,
            )
        return None

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
            detector_id=OPP08_DETECTOR_ID,
            detector_version=OPP08_DETECTOR_VERSION,
            opportunity_id=OPP08_OPPORTUNITY_ID,
            status=DetectorStatus.EXPERIMENT,
            direction=direction,
            confidence=1.0,
            tags=(DetectorTag.TREND, "custom:strong_breakout"),
            entry=entry,
            stop=stop,
            reason=reason,
            metadata={
                "atr_period": self._atr_period,
                "ema_period": self._ema_period,
                "strong_bar_atr_mult": self._strong_atr,
                "strong_bar_body_ratio": self._strong_body,
                "atr": atr,
                "ema": ema,
                "timeframe": "5m",
            },
            pattern_state=PatternState(
                name="strong_breakout",
                confidence=1.0,
                metadata={"direction": direction.value},
            ),
        )


OPP08_DESCRIPTOR = DetectorDescriptor(
    id=OPP08_DETECTOR_ID,
    version=OPP08_DETECTOR_VERSION,
    status=DetectorStatus.EXPERIMENT,
    capability=DetectorCapability(
        directions=(Direction.LONG, Direction.SHORT),
        requires=frozenset(),
        produces=frozenset({DetectorTag.TREND, "custom:strong_breakout"}),
        timeframe="5m",
    ),
    factory=OPP08StrongBreakoutDetector,
    tags=(DetectorTag.TREND, "custom:strong_breakout"),
    metadata={
        "purpose": "cid006_opp08_candidate",
        "alpha_claim": False,
        "spec": "OPP08_MS_V0_1",
    },
)
