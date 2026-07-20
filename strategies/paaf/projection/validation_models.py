"""Validation Projection view models (derived; not Domain)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping

# Presentation aliases for EvidenceRecord.decision — not new Domain values.
_DECISION_TO_STATUS: Mapping[str, str] = {
    "KEEP": "ACCEPTED",
    "HOLD": "HOLD",
    "REVERT": "REJECTED",
}


def status_for_decision(decision: str) -> str:
    """Map Domain decision → comparison status label."""

    return _DECISION_TO_STATUS.get(decision, decision)


@dataclass(frozen=True)
class EvidenceSnapshot:
    """Copied fields from EvidenceRecord for comparison / query."""

    experiment_id: str
    evidence_id: str
    subject_kind: str
    subject_id: str
    subject_version: str
    decision: str
    status: str
    classification: str
    symbol: str
    evidence_type: str
    created_at: datetime
    metrics: Mapping[str, float]
    parent: str
    feature_artifact_uri: str
    artifact_hash: str


@dataclass(frozen=True)
class ValidationComparisonView:
    """Side-by-side comparison of existing Evidence records."""

    built_at: datetime
    entries: tuple[EvidenceSnapshot, ...]
    decision_counts: Mapping[str, int]
    status_counts: Mapping[str, int]


@dataclass(frozen=True)
class PromotionReadinessView:
    """Visibility only — never auto-promotes."""

    experiment_id: str
    evidence_id: str
    current: str
    evidence_label: str
    blocking: tuple[str, ...]
    suggested_next: str
    may_auto_promote: bool
