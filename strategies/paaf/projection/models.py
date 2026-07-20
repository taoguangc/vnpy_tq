"""Frozen view models for Portfolio Projection (derived; not Domain)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping

PORTFOLIO_BUCKETS: tuple[str, ...] = (
    "DATA",
    "FEATURE",
    "PATTERN",
    "DETECTOR",
    "EXECUTION",
)

# Projection classification only — does not extend Domain subject_kind.
_SUBJECT_KIND_TO_BUCKET: Mapping[str, str] = {
    "dataset": "DATA",
    "feature_sensor": "FEATURE",
    "opportunity": "PATTERN",
    "detector": "DETECTOR",
}


def bucket_for_subject_kind(subject_kind: str) -> str:
    """Map Domain subject_kind → Portfolio bucket; unknown stays unmapped."""

    return _SUBJECT_KIND_TO_BUCKET.get(subject_kind, "")


@dataclass(frozen=True)
class PortfolioEvidenceRef:
    """Reference to an existing EvidenceRecord; values copied, not recomputed."""

    experiment_id: str
    evidence_id: str
    subject_kind: str
    subject_id: str
    subject_version: str
    decision: str
    created_at: datetime
    bucket: str
    metrics: Mapping[str, float]


@dataclass(frozen=True)
class PortfolioBucketSummary:
    """Counts derived by grouping existing decisions; no new scores."""

    bucket: str
    evidence_count: int
    decision_counts: Mapping[str, int]
    refs: tuple[PortfolioEvidenceRef, ...]


@dataclass(frozen=True)
class PortfolioProjection:
    """Read-only Research Portfolio snapshot (Decision 017 buckets)."""

    built_at: datetime
    experiment_count: int
    evidence_count: int
    buckets: Mapping[str, PortfolioBucketSummary]
