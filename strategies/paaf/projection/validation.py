"""Validation Projection — compare / find / readiness over existing Evidence."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from types import MappingProxyType

from strategies.paaf.evidence.models import EvidenceRecord
from strategies.paaf.projection.read_view import EvidenceReadView
from strategies.paaf.projection.validation_models import (
    EvidenceSnapshot,
    PromotionReadinessView,
    ValidationComparisonView,
    status_for_decision,
)


def _snapshot_from_evidence(evidence: EvidenceRecord) -> EvidenceSnapshot:
    metadata = evidence.metadata
    return EvidenceSnapshot(
        experiment_id=evidence.experiment_id,
        evidence_id=evidence.evidence_id,
        subject_kind=evidence.subject_kind,
        subject_id=evidence.subject_id,
        subject_version=evidence.subject_version,
        decision=evidence.decision,
        status=status_for_decision(evidence.decision),
        classification=evidence.subject_kind,
        symbol=str(metadata.get("symbol", "")),
        evidence_type=str(metadata.get("evidence_type", "")),
        created_at=evidence.created_at,
        metrics=dict(evidence.metrics),
        parent=str(metadata.get("parent", "")),
        feature_artifact_uri=evidence.feature_artifact_uri,
        artifact_hash=evidence.artifact_hash,
    )


def _iter_snapshots(view: EvidenceReadView) -> tuple[EvidenceSnapshot, ...]:
    items: list[EvidenceSnapshot] = []
    for experiment_id in view.list_experiment_ids():
        for evidence_id in view.list_evidence_ids(experiment_id):
            evidence = view.load_evidence(experiment_id, evidence_id)
            items.append(_snapshot_from_evidence(evidence))
    return tuple(
        sorted(items, key=lambda item: (item.experiment_id, item.evidence_id))
    )


def build_validation_comparison(
    source: EvidenceReadView | object,
    *,
    experiment_ids: tuple[str, ...] | None = None,
    built_at: datetime | None = None,
) -> ValidationComparisonView:
    """Aggregate existing Evidence into a comparison view (no recompute)."""

    view = EvidenceReadView.wrap(source)
    stamp = built_at or datetime.now(timezone.utc)
    if stamp.tzinfo is None:
        raise ValueError("built_at 必须包含时区")

    snapshots = _iter_snapshots(view)
    if experiment_ids is not None:
        wanted = frozenset(experiment_ids)
        snapshots = tuple(
            item for item in snapshots if item.experiment_id in wanted
        )

    decision_counts: dict[str, int] = defaultdict(int)
    status_counts: dict[str, int] = defaultdict(int)
    for item in snapshots:
        decision_counts[item.decision] += 1
        status_counts[item.status] += 1

    return ValidationComparisonView(
        built_at=stamp,
        entries=snapshots,
        decision_counts=MappingProxyType(dict(decision_counts)),
        status_counts=MappingProxyType(dict(status_counts)),
    )


def find_evidence(
    source: EvidenceReadView | object,
    *,
    experiment_id: str | None = None,
    symbol: str | None = None,
    evidence_type: str | None = None,
    classification: str | None = None,
    status: str | None = None,
) -> tuple[EvidenceSnapshot, ...]:
    """Minimal cross-experiment filter over copied Evidence fields."""

    view = EvidenceReadView.wrap(source)
    results: list[EvidenceSnapshot] = []
    for item in _iter_snapshots(view):
        if experiment_id is not None and item.experiment_id != experiment_id:
            continue
        if symbol is not None and item.symbol != symbol:
            continue
        if evidence_type is not None and item.evidence_type != evidence_type:
            continue
        if classification is not None and item.classification != classification:
            continue
        if status is not None and item.status != status and item.decision != status:
            continue
        results.append(item)
    return tuple(results)


def _blocking_for(evidence: EvidenceRecord) -> tuple[str, ...]:
    blockers: list[str] = []
    meta_block = evidence.metadata.get("blocking", "")
    if meta_block:
        blockers.append(meta_block)
    if evidence.decision == "HOLD":
        blockers.append("decision is HOLD")
    elif evidence.decision == "REVERT":
        blockers.append("decision is REVERT (Negative Evidence)")
    if evidence.decision != "KEEP":
        blockers.append("Baseline / E4 promotion gate not satisfied by this Evidence")
    else:
        blockers.append("KEEP is not automatic promotion; Baseline gate still required")
    return tuple(blockers)


def _suggested_next(evidence: EvidenceRecord) -> str:
    explicit = evidence.metadata.get("suggested_next", "")
    if explicit:
        return explicit
    if evidence.decision == "REVERT":
        return "Do not promote; archive as Negative Evidence"
    if evidence.decision == "HOLD":
        return "Do not promote; new experiment required for unresolved hypothesis"
    return "Do not auto-promote; require Baseline gate and user confirmation"


def build_promotion_readiness(
    source: EvidenceReadView | object,
    *,
    experiment_id: str,
    evidence_id: str,
) -> PromotionReadinessView:
    """Describe promotion readiness from existing fields only."""

    view = EvidenceReadView.wrap(source)
    evidence = view.load_evidence(experiment_id, evidence_id)
    label = evidence.metadata.get("evidence_type", "")
    if not label:
        label = evidence.decision
    return PromotionReadinessView(
        experiment_id=evidence.experiment_id,
        evidence_id=evidence.evidence_id,
        current=evidence.decision,
        evidence_label=label,
        blocking=_blocking_for(evidence),
        suggested_next=_suggested_next(evidence),
        may_auto_promote=False,
    )
