"""SMC bullish Order-Block Candidate Detector; observations only.

PAAF rewrite of legacy SmcOrderFlowVwapStrategy OB sweep path
（SMC_OB_LONG_MS_V0_1）. VWAP/Delta/Setup B/C OUT OF SCOPE.
Cross-bar OB state is explicit PatternState.
"""

from __future__ import annotations

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

SMC_OB_LONG_DETECTOR_ID = "SMC_OB_LONG"
SMC_OB_LONG_DETECTOR_VERSION = "1.0.0"
SMC_OB_LONG_OPPORTUNITY_ID = "SMC_OB_LONG"
DEFAULT_SMC_POOL_BARS = 12
DEFAULT_SMC_MIN_BARS = 16
DEFAULT_OB_STOP_BUFFER = 2.0
DEFAULT_PRICETICK = 1.0
_FSM_IDLE = "IDLE"
_FSM_OB_SET = "OB_SET"


class SMCOrderBlockLongDetector(BaseDetector):
    """Bullish OB after sweep · LONG on close reclaim above ob_high."""

    metadata = DetectorMetadata(
        name=SMC_OB_LONG_DETECTOR_ID,
        version=SMC_OB_LONG_DETECTOR_VERSION,
        description="SMC bullish OB Candidate; E0（SMC_OB_LONG_MS_V0_1）",
        status="Candidate",
        category="Structure",
        timeframe="5m",
        evidence_level="E0",
    )

    def __init__(
        self,
        *,
        smc_pool_bars: int = DEFAULT_SMC_POOL_BARS,
        smc_min_bars: int = DEFAULT_SMC_MIN_BARS,
        ob_stop_buffer: float = DEFAULT_OB_STOP_BUFFER,
        pricetick: float = DEFAULT_PRICETICK,
    ) -> None:
        if smc_pool_bars <= 0:
            raise ValueError("smc_pool_bars 必须 > 0")
        if smc_min_bars < smc_pool_bars + 2:
            raise ValueError("smc_min_bars 必须 ≥ smc_pool_bars + 2")
        if ob_stop_buffer < 0:
            raise ValueError("ob_stop_buffer 必须 ≥ 0")
        if pricetick <= 0:
            raise ValueError("pricetick 必须 > 0")

        self._pool = int(smc_pool_bars)
        self._min_bars = int(smc_min_bars)
        self._buf = float(ob_stop_buffer)
        self._tick = float(pricetick)

        self._fsm = _FSM_IDLE
        self._ob_low = 0.0
        self._ob_high = 0.0

    def set_pricetick(self, pricetick: float) -> None:
        if pricetick <= 0:
            raise ValueError("pricetick 必须 > 0")
        self._tick = float(pricetick)

    def adjust_levels(self, shift: float) -> None:
        """CbC price shift for active OB."""
        if abs(shift) < 1e-12:
            return
        if self._fsm == _FSM_OB_SET:
            self._ob_low += shift
            self._ob_high += shift

    @property
    def pattern_state(self) -> PatternState:
        return self._build_pattern_state(confidence=1.0)

    def load_pattern_state(self, state: PatternState | Mapping[str, Any]) -> None:
        data = state.to_dict() if isinstance(state, PatternState) else dict(state)
        meta = dict(data.get("metadata") or {})
        self._fsm = str(meta.get("fsm", _FSM_IDLE))
        self._ob_low = float(meta.get("ob_low", 0.0))
        self._ob_high = float(meta.get("ob_high", 0.0))

    def detect(
        self,
        am: Any,
        context: Context,
    ) -> Optional[DetectionResult]:
        del context  # SMC_OB_LONG_MS: no Context gate
        if not am_is_inited(am):
            return None
        count = int(getattr(am, "count", 0) or 0)
        if count < self._min_bars:
            return None
        if count < self._pool + 2:
            return None

        close = float(am.close[-1])
        high = float(am.high[-1])

        if self._fsm == _FSM_OB_SET and close < self._ob_low:
            self._reset_ob()

        if self._fsm == _FSM_IDLE:
            self._try_set_ob_from_sweep(am)

        if self._fsm == _FSM_OB_SET and close > self._ob_high:
            stop = self._ob_low - self._buf * self._tick
            result = self._result(
                Direction.LONG,
                entry=high,
                stop=stop,
                reason="smc OB long: close reclaim above ob_high",
            )
            self._reset_ob()
            return result
        return None

    def _try_set_ob_from_sweep(self, am: Any) -> None:
        lows = [float(x) for x in am.low[-(self._pool + 2) : -2]]
        if not lows:
            return
        pool_min = min(lows)
        sweep_low = float(am.low[-2])
        sweep_close = float(am.close[-2])
        sweep_open = float(am.open[-2])
        sweep_high = float(am.high[-2])
        if sweep_low < pool_min and sweep_close > pool_min:
            self._ob_low = min(sweep_open, sweep_close)
            self._ob_high = sweep_high
            self._fsm = _FSM_OB_SET

    def _reset_ob(self) -> None:
        self._fsm = _FSM_IDLE
        self._ob_low = 0.0
        self._ob_high = 0.0

    def _build_pattern_state(self, *, confidence: float) -> PatternState:
        return PatternState(
            name="smc_ob_long",
            confidence=confidence,
            metadata={
                "fsm": self._fsm,
                "ob_low": self._ob_low,
                "ob_high": self._ob_high,
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
            detector_id=SMC_OB_LONG_DETECTOR_ID,
            detector_version=SMC_OB_LONG_DETECTOR_VERSION,
            opportunity_id=SMC_OB_LONG_OPPORTUNITY_ID,
            status=DetectorStatus.EXPERIMENT,
            direction=direction,
            confidence=1.0,
            tags=(DetectorTag.LIQUIDITY, "custom:smc_ob_long"),
            entry=entry,
            stop=stop,
            reason=reason,
            metadata={
                "smc_pool_bars": self._pool,
                "smc_min_bars": self._min_bars,
                "ob_stop_buffer": self._buf,
                "ob_low": self._ob_low,
                "ob_high": self._ob_high,
                "pricetick": self._tick,
                "timeframe": "5m",
            },
            pattern_state=self._build_pattern_state(confidence=1.0),
        )


SMC_OB_LONG_DESCRIPTOR = DetectorDescriptor(
    id=SMC_OB_LONG_DETECTOR_ID,
    version=SMC_OB_LONG_DETECTOR_VERSION,
    status=DetectorStatus.EXPERIMENT,
    capability=DetectorCapability(
        directions=(Direction.LONG,),
        requires=frozenset(),
        produces=frozenset({DetectorTag.LIQUIDITY, "custom:smc_ob_long"}),
        timeframe="5m",
    ),
    factory=SMCOrderBlockLongDetector,
    tags=(DetectorTag.LIQUIDITY, "custom:smc_ob_long"),
    metadata={
        "purpose": "cid013_smc_ob_long_candidate",
        "alpha_claim": False,
        "spec": "SMC_OB_LONG_MS_V0_1",
    },
)
