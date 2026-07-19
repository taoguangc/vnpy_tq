"""Deterministic fingerprints for Evaluation contracts."""

from __future__ import annotations

from typing import Any

from strategies.paaf.evidence.hashing import hash_canonical_json
from strategies.paaf.evaluation.models import (
    EvaluationResult,
    MetricDefinition,
    OutcomeDefinition,
)


def fingerprint_outcome_definition(definition: OutcomeDefinition) -> str:
    return hash_canonical_json(definition.to_dict())


def fingerprint_metric_definition(definition: MetricDefinition) -> str:
    return hash_canonical_json(definition.to_dict())


def fingerprint_evaluation_body(result: EvaluationResult) -> str:
    """Fingerprint evaluation meaning; excludes created_at and runtime paths."""

    payload: dict[str, Any] = result.to_dict()
    payload.pop("created_at", None)
    return hash_canonical_json(payload)
