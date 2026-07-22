"""Causal ContextState publisher — bar_timestamp <= t only; no future leakage."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal
from typing import Any

import numpy as np
import pandas as pd

from context_engine.schema import CONTEXT_VERSION, SCHEMA_VERSION, ContextState

SMA_N = 20
WARMUP_BARS = SMA_N


def _round6(x: float) -> float:
    return float(Decimal(str(x)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_EVEN))


@dataclass
class PublisherConfig:
    instrument: str
    manifest_id: str | None = None
    context_version: str = CONTEXT_VERSION


class ContextStatePublisher:
    """Incremental publisher. Only uses bars with timestamp <= current bar."""

    def __init__(self, config: PublisherConfig) -> None:
        self.config = config
        self._highs: list[float] = []
        self._lows: list[float] = []
        self._timestamps: list[pd.Timestamp] = []
        self._missing_gap_count = 0

    def reset(self) -> None:
        self._highs.clear()
        self._lows.clear()
        self._timestamps.clear()
        self._missing_gap_count = 0

    def update_bar(
        self,
        *,
        timestamp: pd.Timestamp,
        high: float,
        low: float,
        close: float | None = None,
        volume: float | None = None,
        force_validity: str | None = None,
        fault_reason: str | None = None,
    ) -> ContextState:
        del close, volume  # reserved; primary path uses high/low only
        # Publication boundary: reject future relative to last accepted bar
        if self._timestamps and timestamp < self._timestamps[-1]:
            return self._invalid(
                timestamp,
                reason="non_monotonic_timestamp",
                publication_boundary_ok=False,
            )

        if self._timestamps:
            # gap detection (missing bar heuristic): large jump in index handled by harness
            pass

        self._timestamps.append(timestamp)
        self._highs.append(float(high) if np.isfinite(high) else float("nan"))
        self._lows.append(float(low) if np.isfinite(low) else float("nan"))

        n = len(self._highs)
        hi = self._highs[-1]
        lo = self._lows[-1]
        finite_ok = np.isfinite(hi) and np.isfinite(lo) and hi >= lo
        warmup_complete = n >= WARMUP_BARS

        if force_validity == "INVALID" or fault_reason in {
            "duplicate_timestamp",
            "future_data",
            "rollover_mismatch",
            "session_mismatch",
            "forbidden_diagnostics",
        }:
            return self._invalid(
                timestamp,
                reason=fault_reason or "forced_invalid",
                publication_boundary_ok=fault_reason != "future_data",
            )

        if not finite_ok or not warmup_complete:
            context_state = "invalid"
            validity = "INVALID"
            range_ratio = None
            sma_ready = False
        else:
            ranges = np.asarray(self._highs[-SMA_N:], dtype=float) - np.asarray(
                self._lows[-SMA_N:], dtype=float
            )
            if not np.all(np.isfinite(ranges)):
                context_state = "invalid"
                validity = "INVALID"
                range_ratio = None
                sma_ready = False
            else:
                sma = float(ranges.mean())
                cur_range = float(hi - lo)
                if sma <= 0 or not np.isfinite(sma):
                    context_state = "invalid"
                    validity = "INVALID"
                    range_ratio = None
                    sma_ready = False
                else:
                    range_ratio = cur_range / sma
                    context_state = "compression" if range_ratio < 1.0 else "expansion"
                    validity = "DEGRADED" if force_validity == "DEGRADED" else "VALID"
                    sma_ready = True

        if force_validity == "DEGRADED" and validity == "VALID":
            validity = "DEGRADED"

        finite_input_ratio = 1.0 if finite_ok else 0.0
        publication_boundary_ok = True
        conf = _round6(
            float(
                np.mean(
                    [
                        1.0 if warmup_complete else 0.0,
                        finite_input_ratio,
                        1.0 if publication_boundary_ok else 0.0,
                        0.0 if validity == "INVALID" else 1.0,
                    ]
                )
            )
        )

        diagnostics: dict[str, Any] = {
            "missing_bars": int(self._missing_gap_count),
            "data_quality": "good" if finite_ok else "bad",
            "warmup_complete": bool(warmup_complete),
            "finite_input_ratio": _round6(finite_input_ratio),
            "publication_boundary_ok": publication_boundary_ok,
            "sma_range_ready": bool(sma_ready),
        }
        if range_ratio is not None:
            diagnostics["range_ratio"] = _round6(float(range_ratio))
        if fault_reason:
            diagnostics["fault_reason_code"] = fault_reason
            diagnostics["data_quality"] = "degraded"

        return ContextState(
            timestamp=self._fmt_ts(timestamp),
            instrument=self.config.instrument,
            context_version=self.config.context_version,
            validity=validity,  # type: ignore[arg-type]
            descriptive_state={"context_state": context_state},
            confidence=conf,
            diagnostics=diagnostics,
            manifest_id=self.config.manifest_id,
            schema_version=SCHEMA_VERSION,
        )

    def note_missing_bar(self) -> None:
        self._missing_gap_count += 1

    def _invalid(
        self,
        timestamp: pd.Timestamp,
        *,
        reason: str,
        publication_boundary_ok: bool,
    ) -> ContextState:
        conf = _round6(
            float(
                np.mean(
                    [
                        0.0,
                        0.0,
                        1.0 if publication_boundary_ok else 0.0,
                        0.0,
                    ]
                )
            )
        )
        return ContextState(
            timestamp=self._fmt_ts(timestamp),
            instrument=self.config.instrument,
            context_version=self.config.context_version,
            validity="INVALID",
            descriptive_state={"context_state": "invalid"},
            confidence=conf,
            diagnostics={
                "missing_bars": int(self._missing_gap_count),
                "data_quality": "bad",
                "warmup_complete": False,
                "finite_input_ratio": 0.0,
                "publication_boundary_ok": publication_boundary_ok,
                "sma_range_ready": False,
                "fault_reason_code": reason,
            },
            manifest_id=self.config.manifest_id,
            schema_version=SCHEMA_VERSION,
        )

    @staticmethod
    def _fmt_ts(timestamp: pd.Timestamp) -> str:
        ts = pd.Timestamp(timestamp)
        if ts.tzinfo is None:
            return ts.isoformat()
        return ts.isoformat()


def publish_batch(
    df: pd.DataFrame,
    *,
    instrument: str,
    manifest_id: str | None = None,
) -> list[ContextState]:
    """Batch replay = sequential update (deterministic causal path)."""
    pub = ContextStatePublisher(
        PublisherConfig(instrument=instrument, manifest_id=manifest_id)
    )
    out: list[ContextState] = []
    for row in df.itertuples(index=False):
        out.append(
            pub.update_bar(
                timestamp=pd.Timestamp(row.dt_cst),
                high=float(row.high),
                low=float(row.low),
                close=float(row.close) if hasattr(row, "close") else None,
                volume=float(row.volume) if hasattr(row, "volume") else None,
            )
        )
    return out


def publish_streaming(
    df: pd.DataFrame,
    *,
    instrument: str,
    manifest_id: str | None = None,
) -> list[ContextState]:
    """Streaming replay uses the same update_bar path (parity identity)."""
    return publish_batch(df, instrument=instrument, manifest_id=manifest_id)
