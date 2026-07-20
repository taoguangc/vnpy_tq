"""Portfolio Projection builder — aggregate only; never derive Evidence."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from types import MappingProxyType

from strategies.paaf.evidence.models import EvidenceRecord
from strategies.paaf.projection.models import (
    PORTFOLIO_BUCKETS,
    PortfolioBucketSummary,
    PortfolioEvidenceRef,
    PortfolioProjection,
    bucket_for_subject_kind,
)
from strategies.paaf.projection.read_view import EvidenceReadView


def _ref_from_evidence(evidence: EvidenceRecord) -> PortfolioEvidenceRef | None:
    bucket = bucket_for_subject_kind(evidence.subject_kind)
    if not bucket:
        return None
    return PortfolioEvidenceRef(
        experiment_id=evidence.experiment_id,
        evidence_id=evidence.evidence_id,
        subject_kind=evidence.subject_kind,
        subject_id=evidence.subject_id,
        subject_version=evidence.subject_version,
        decision=evidence.decision,
        created_at=evidence.created_at,
        bucket=bucket,
        metrics=dict(evidence.metrics),
    )


def build_portfolio_projection(
    source: EvidenceReadView | object,
    *,
    built_at: datetime | None = None,
) -> PortfolioProjection:
    """Read Domain records and derive Portfolio view (pure aggregation)."""

    view = EvidenceReadView.wrap(source)
    stamp = built_at or datetime.now(timezone.utc)
    if stamp.tzinfo is None:
        raise ValueError("built_at 必须包含时区")

    by_bucket: dict[str, list[PortfolioEvidenceRef]] = {
        name: [] for name in PORTFOLIO_BUCKETS
    }
    experiment_ids = view.list_experiment_ids()
    evidence_total = 0

    for experiment_id in experiment_ids:
        for evidence_id in view.list_evidence_ids(experiment_id):
            evidence = view.load_evidence(experiment_id, evidence_id)
            evidence_total += 1
            ref = _ref_from_evidence(evidence)
            if ref is None:
                continue
            by_bucket[ref.bucket].append(ref)

    buckets: dict[str, PortfolioBucketSummary] = {}
    for name in PORTFOLIO_BUCKETS:
        refs = tuple(
            sorted(
                by_bucket[name],
                key=lambda item: (item.experiment_id, item.evidence_id),
            )
        )
        decision_counts: dict[str, int] = defaultdict(int)
        for ref in refs:
            decision_counts[ref.decision] += 1
        buckets[name] = PortfolioBucketSummary(
            bucket=name,
            evidence_count=len(refs),
            decision_counts=MappingProxyType(dict(decision_counts)),
            refs=refs,
        )

    return PortfolioProjection(
        built_at=stamp,
        experiment_count=len(experiment_ids),
        evidence_count=evidence_total,
        buckets=MappingProxyType(buckets),
    )
