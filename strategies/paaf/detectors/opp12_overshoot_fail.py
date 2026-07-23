"""OPP12 overshoot-fail Candidate Detector; observations only, never trading.

PAAF rewrite of legacy Opp12Mixin morphology（OPP12_MS_V0_1）.
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

OPP12_DETECTOR_ID = "OPP12"
OPP12_DETECTOR_VERSION = "1.0.0"
OPP12_OPPORTUNITY_ID = "OPP12"
DEFAULT_ATR_PERIOD = 14
DEFAULT_EMA_PERIOD = 20
DEFAULT_OVERSHOOT_ATR_MULT = 1.2
DEFAULT_OVERSHOOT_MAX_ATR_MULT = 2.5
DEFAULT_REVERSAL_SHADOW_MIN_RATIO = 0.40
DEFAULT_REVERSAL_CLOSE_QUARTER = 0.25
DEFAULT_REVERSAL_MIN_BODY_RATIO = 0.15


class OPP12OvershootFailDetector(BaseDetector):
    """EMA overshoot + reversal-bar fail; no Context filter."""

    metadata = DetectorMetadata(
        name=OPP12_DETECTOR_ID,
        version=OPP12_DETECTOR_VERSION,
        description="Overshoot-fail Candidate; E0 observation only（OPP12_MS_V0_1）",
        status="Candidate",
        category="Reversal",
        timeframe="5m",
        evidence_level="E0",
    )

    def __init__(
        self,
        *,
        atr_period: int = DEFAULT_ATR_PERIOD,
        ema_period: int = DEFAULT_EMA_PERIOD,
        overshoot_atr_mult: float = DEFAULT_OVERSHOOT_ATR_MULT,
        overshoot_max_atr_mult: float = DEFAULT_OVERSHOOT_MAX_ATR_MULT,
        reversal_shadow_min_ratio: float = DEFAULT_REVERSAL_SHADOW_MIN_RATIO,
        reversal_close_quarter: float = DEFAULT_REVERSAL_CLOSE_QUARTER,
        reversal_min_body_ratio: float = DEFAULT_REVERSAL_MIN_BODY_RATIO,
    ) -> None:
        if not isinstance(atr_period, int) or atr_period < 2:
            raise ValueError("atr_period 必须是 >= 2 的 int")
        if not isinstance(ema_period, int) or ema_period < 2:
            raise ValueError("ema_period 必须是 >= 2 的 int")
        if overshoot_atr_mult <= 0 or overshoot_max_atr_mult < overshoot_atr_mult:
            raise ValueError("overshoot ATR 倍数无效")
        self._atr_period = atr_period
        self._ema_period = ema_period
        self._overshoot_atr_mult = float(overshoot_atr_mult)
        self._overshoot_max_atr_mult = float(overshoot_max_atr_mult)
        self._rev_shadow = float(reversal_shadow_min_ratio)
        self._rev_close_q = float(reversal_close_quarter)
        self._rev_body = float(reversal_min_body_ratio)

    def detect(
        self,
        am: Any,
        context: Context,
    ) -> Optional[DetectionResult]:
        del context  # OPP12_MS: no Context gate
        if not am_is_inited(am):
            return None
        need = max(self._atr_period, self._ema_period) + 2
        bars = bars_from_am(am, need)
        if len(bars) < need:
            return None

        atr = self._read_atr(am)
        ema = self._read_ema(am)
        if atr is None or ema is None or atr <= 0:
            return None

        bar = bars[-1]
        bar_range = bar.high - bar.low
        if bar_range <= 0:
            return None

        body = abs(bar.close - bar.open)
        upper = bar.high - max(bar.open, bar.close)
        lower = min(bar.open, bar.close) - bar.low

        if self._is_bull_reversal(bar, bar_range, body, lower):
            depth = ema - bar.close
            lo = atr * self._overshoot_atr_mult
            hi = atr * self._overshoot_max_atr_mult
            if lo <= depth <= hi and bar.close > bar.open:
                return self._result(
                    Direction.LONG,
                    entry=bar.high,
                    stop=bar.low,
                    reason="overshoot-fail long: depth in band + bull reversal",
                    atr=atr,
                    ema=ema,
                    depth=depth,
                )

        if self._is_bear_reversal(bar, bar_range, body, upper):
            if bar.close > ema + atr * self._overshoot_atr_mult:
                return self._result(
                    Direction.SHORT,
                    entry=bar.low,
                    stop=bar.high,
                    reason="overshoot-fail short: close above EMA band + bear reversal",
                    atr=atr,
                    ema=ema,
                    depth=bar.close - ema,
                )
        return None

    def _is_bull_reversal(
        self, bar: Any, bar_range: float, body: float, lower: float
    ) -> bool:
        return (
            lower >= bar_range * self._rev_shadow
            and bar.close >= bar.high - bar_range * self._rev_close_q
            and body >= bar_range * self._rev_body
        )

    def _is_bear_reversal(
        self, bar: Any, bar_range: float, body: float, upper: float
    ) -> bool:
        return (
            upper >= bar_range * self._rev_shadow
            and bar.close <= bar.low + bar_range * self._rev_close_q
            and body >= bar_range * self._rev_body
        )

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
        depth: float,
    ) -> DetectionResult:
        return DetectionResult(
            detector_id=OPP12_DETECTOR_ID,
            detector_version=OPP12_DETECTOR_VERSION,
            opportunity_id=OPP12_OPPORTUNITY_ID,
            status=DetectorStatus.EXPERIMENT,
            direction=direction,
            confidence=1.0,
            tags=(DetectorTag.REVERSAL, "custom:overshoot_fail"),
            entry=entry,
            stop=stop,
            reason=reason,
            metadata={
                "atr_period": self._atr_period,
                "ema_period": self._ema_period,
                "overshoot_atr_mult": self._overshoot_atr_mult,
                "overshoot_max_atr_mult": self._overshoot_max_atr_mult,
                "atr": atr,
                "ema": ema,
                "depth": depth,
                "timeframe": "5m",
            },
            pattern_state=PatternState(
                name="overshoot_fail",
                confidence=1.0,
                metadata={"direction": direction.value},
            ),
        )


OPP12_DESCRIPTOR = DetectorDescriptor(
    id=OPP12_DETECTOR_ID,
    version=OPP12_DETECTOR_VERSION,
    status=DetectorStatus.EXPERIMENT,
    capability=DetectorCapability(
        directions=(Direction.LONG, Direction.SHORT),
        requires=frozenset(),
        produces=frozenset({DetectorTag.REVERSAL, "custom:overshoot_fail"}),
        timeframe="5m",
    ),
    factory=OPP12OvershootFailDetector,
    tags=(DetectorTag.REVERSAL, "custom:overshoot_fail"),
    metadata={
        "purpose": "cid004_opp12_candidate",
        "alpha_claim": False,
        "spec": "OPP12_MS_V0_1",
    },
)
