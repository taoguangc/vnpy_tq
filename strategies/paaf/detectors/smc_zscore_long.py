"""SMC VWAP Z-score oversold Candidate Detector; observations only.

PAAF rewrite of legacy Setup B（SMC_ZSCORE_LONG_MS_V0_1）.
OB / Delta / Setup A/C OUT OF SCOPE.
Session VWAP is Strategy-injected; z uses explicit am window.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional

import numpy as np

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

SMC_ZSCORE_LONG_DETECTOR_ID = "SMC_ZSCORE_LONG"
SMC_ZSCORE_LONG_DETECTOR_VERSION = "1.0.0"
SMC_ZSCORE_LONG_OPPORTUNITY_ID = "SMC_ZSCORE_LONG"
DEFAULT_ZSCORE_THRESHOLD = 2.5
DEFAULT_VWAP_LENGTH = 60
DEFAULT_STOP_LOOKBACK = 5
DEFAULT_STOP_BUFFER = 2.0
DEFAULT_MIN_RISK_TICKS = 5.0
DEFAULT_PRICETICK = 1.0


class SMCZScoreLongDetector(BaseDetector):
    """VWAP Z-score oversold long; no OB / Delta / Context gate."""

    metadata = DetectorMetadata(
        name=SMC_ZSCORE_LONG_DETECTOR_ID,
        version=SMC_ZSCORE_LONG_DETECTOR_VERSION,
        description="SMC VWAP Z-score long Candidate; E0（SMC_ZSCORE_LONG_MS_V0_1）",
        status="Candidate",
        category="MeanReversion",
        timeframe="5m",
        evidence_level="E0",
    )

    def __init__(
        self,
        *,
        zscore_threshold: float = DEFAULT_ZSCORE_THRESHOLD,
        vwap_length: int = DEFAULT_VWAP_LENGTH,
        stop_lookback: int = DEFAULT_STOP_LOOKBACK,
        stop_buffer: float = DEFAULT_STOP_BUFFER,
        min_risk_ticks: float = DEFAULT_MIN_RISK_TICKS,
        pricetick: float = DEFAULT_PRICETICK,
    ) -> None:
        if zscore_threshold <= 0:
            raise ValueError("zscore_threshold 必须 > 0")
        if vwap_length < 10:
            raise ValueError("vwap_length 必须 ≥ 10")
        if stop_lookback <= 0:
            raise ValueError("stop_lookback 必须 > 0")
        if stop_buffer < 0:
            raise ValueError("stop_buffer 必须 ≥ 0")
        if min_risk_ticks < 0:
            raise ValueError("min_risk_ticks 必须 ≥ 0")
        if pricetick <= 0:
            raise ValueError("pricetick 必须 > 0")

        self._z_th = float(zscore_threshold)
        self._vwap_len = int(vwap_length)
        self._lookback = int(stop_lookback)
        self._buf = float(stop_buffer)
        self._min_risk = float(min_risk_ticks)
        self._tick = float(pricetick)
        self._session_vwap = 0.0
        self._last_z = 0.0

    def note_session_vwap(self, vwap: float) -> None:
        """Strategy injects session VWAP from 1m ledger."""
        self._session_vwap = float(vwap)

    def set_pricetick(self, pricetick: float) -> None:
        if pricetick <= 0:
            raise ValueError("pricetick 必须 > 0")
        self._tick = float(pricetick)

    def adjust_levels(self, shift: float) -> None:
        """CbC: shift injected VWAP if active."""
        if abs(shift) < 1e-12:
            return
        if abs(self._session_vwap) > 1e-12:
            self._session_vwap += shift

    @property
    def pattern_state(self) -> PatternState:
        return PatternState(
            name="smc_zscore_long",
            confidence=1.0,
            metadata={
                "session_vwap": self._session_vwap,
                "last_z": self._last_z,
            },
        )

    def load_pattern_state(self, state: PatternState | Mapping[str, Any]) -> None:
        data = state.to_dict() if isinstance(state, PatternState) else dict(state)
        meta = dict(data.get("metadata") or {})
        self._session_vwap = float(meta.get("session_vwap", 0.0))
        self._last_z = float(meta.get("last_z", 0.0))

    def detect(
        self,
        am: Any,
        context: Context,
    ) -> Optional[DetectionResult]:
        del context
        if not am_is_inited(am):
            return None
        count = int(getattr(am, "count", 0) or 0)
        if count < 10 or count < self._lookback:
            return None
        if self._session_vwap <= 0:
            return None

        length = min(self._vwap_len, count)
        if length < 10:
            return None

        closes = np.asarray([float(x) for x in am.close[-length:]], dtype=float)
        deviations = closes - self._session_vwap
        std_dev = float(np.std(deviations))
        close = float(am.close[-1])
        high = float(am.high[-1])
        if std_dev <= 0:
            self._last_z = 0.0
            return None

        z = (close - self._session_vwap) / std_dev
        self._last_z = z
        if z >= -self._z_th:
            return None

        lows = [float(x) for x in am.low[-self._lookback :]]
        stop = min(lows) - self._buf * self._tick
        entry = high
        if entry <= stop + self._min_risk * self._tick:
            return None

        return DetectionResult(
            detector_id=SMC_ZSCORE_LONG_DETECTOR_ID,
            detector_version=SMC_ZSCORE_LONG_DETECTOR_VERSION,
            opportunity_id=SMC_ZSCORE_LONG_OPPORTUNITY_ID,
            status=DetectorStatus.EXPERIMENT,
            direction=Direction.LONG,
            confidence=1.0,
            tags=(DetectorTag.REVERSAL, "custom:smc_zscore_long"),
            entry=entry,
            stop=stop,
            reason=f"smc z-score long: z={z:.3f} < -{self._z_th}",
            metadata={
                "zscore": z,
                "zscore_threshold": self._z_th,
                "session_vwap": self._session_vwap,
                "vwap_length": self._vwap_len,
                "stop_lookback": self._lookback,
                "stop_buffer": self._buf,
                "min_risk_ticks": self._min_risk,
                "pricetick": self._tick,
                "timeframe": "5m",
            },
            pattern_state=self.pattern_state,
        )


SMC_ZSCORE_LONG_DESCRIPTOR = DetectorDescriptor(
    id=SMC_ZSCORE_LONG_DETECTOR_ID,
    version=SMC_ZSCORE_LONG_DETECTOR_VERSION,
    status=DetectorStatus.EXPERIMENT,
    capability=DetectorCapability(
        directions=(Direction.LONG,),
        requires=frozenset(),
        produces=frozenset({DetectorTag.REVERSAL, "custom:smc_zscore_long"}),
        timeframe="5m",
    ),
    factory=SMCZScoreLongDetector,
    tags=(DetectorTag.REVERSAL, "custom:smc_zscore_long"),
    metadata={
        "purpose": "cid014_smc_zscore_long_candidate",
        "alpha_claim": False,
        "spec": "SMC_ZSCORE_LONG_MS_V0_1",
    },
)
