"""ContextState.v1 — A1 Published State schema (computational only)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

SCHEMA_VERSION = "ContextState.v1"
CONTEXT_VERSION = "A1-CTX-PS-v1.0.0"

Validity = Literal["VALID", "DEGRADED", "INVALID"]
PrimaryState = Literal["compression", "expansion", "invalid"]

FORBIDDEN_DIAG_KEYS = frozenset(
    {
        "expected_direction",
        "future_volatility",
        "trade_quality",
        "edge_score",
        "trade_signal",
        "long_bias",
        "short_bias",
        "expected_return",
        "direction_prediction",
        "buy_signal",
        "sell_signal",
        "alpha_state",
        "market_regime",
        "trade_bias",
    }
)

ALLOWED_DIAG_KEYS = frozenset(
    {
        "missing_bars",
        "data_quality",
        "calculation_time_ms",
        "warmup_complete",
        "fault_reason_code",
        "finite_input_ratio",
        "publication_boundary_ok",
        "range_ratio",
        "vol_regime_subtag",
        "liq_regime_subtag",
        "sma_range_ready",
    }
)


@dataclass(frozen=True)
class ContextState:
    timestamp: str
    instrument: str
    context_version: str
    validity: Validity
    descriptive_state: dict[str, str]
    confidence: float
    diagnostics: dict[str, Any] = field(default_factory=dict)
    # C-LINEAGE (optional on object; always written into artifacts)
    manifest_id: str | None = None
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        bad = FORBIDDEN_DIAG_KEYS.intersection(self.diagnostics)
        if bad:
            raise ValueError(f"diagnostics contain forbidden keys: {sorted(bad)}")
        cs = self.descriptive_state.get("context_state")
        if cs not in ("compression", "expansion", "invalid"):
            raise ValueError(f"invalid context_state: {cs}")

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        # round confidence already applied at construction
        return d

    def exact_key(self) -> tuple:
        """Fields compared with exact equality (parity)."""
        return (
            self.timestamp,
            self.instrument,
            self.context_version,
            self.validity,
            self.descriptive_state.get("context_state"),
            self.schema_version,
            json.dumps(
                {k: self.diagnostics[k] for k in sorted(self.diagnostics) if k != "calculation_time_ms"},
                sort_keys=True,
                default=str,
            ),
        )


def schema_document() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "context_version": CONTEXT_VERSION,
        "fields": [
            "timestamp",
            "instrument",
            "context_version",
            "validity",
            "descriptive_state",
            "confidence",
            "diagnostics",
            "manifest_id",
            "schema_version",
        ],
        "validity_enum": ["VALID", "DEGRADED", "INVALID"],
        "context_state_enum_primary": ["compression", "expansion", "invalid"],
        "confidence_semantics": "computational_confidence_only",
        "forbidden_diagnostics": sorted(FORBIDDEN_DIAG_KEYS),
        "allowed_diagnostics": sorted(ALLOWED_DIAG_KEYS),
        "decision_019": "filter|risk_modifier|monitoring — not signal|sizing_alpha",
    }
