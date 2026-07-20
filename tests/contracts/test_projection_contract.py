"""Projection Layer Contract Tests (Decision 018 / PROJECTION_LAYER_SPEC).

Sprint 1 DoD: Compliance, Zero Knowledge Duplication, Read-only, Baseline.
"""

from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from strategies.paaf.evidence.memory_repository import MemoryEvidenceRepository
from strategies.paaf.evidence.models import (
    ArtifactReference,
    EvidenceRecord,
    ExperimentManifest,
)
from strategies.paaf.evidence.repository import EvidenceRepository
from strategies.paaf.projection import (
    PORTFOLIO_BUCKETS,
    EvidenceReadView,
    ProjectionBuilder,
)

CREATED_AT = datetime(2026, 7, 19, 10, 0, tzinfo=timezone.utc)
BUILT_AT = datetime(2026, 7, 20, 12, 0, tzinfo=timezone.utc)


def _manifest(experiment_id: str) -> ExperimentManifest:
    return ExperimentManifest(
        experiment_id=experiment_id,
        sensor_id="sensor",
        sensor_version="1.0",
        parameters={"k": 1},
        parameter_fingerprint="sha256:params",
        code_revision="git:abc",
        data_fingerprint="sha256:data",
        environment_fingerprint="sha256:env",
        artifact_refs=(
            ArtifactReference(
                artifact_id="art-1",
                uri="artifacts/art-1.parquet",
                content_hash="sha256:art",
                artifact_type="feature_results",
            ),
        ),
    )


def _evidence(
    *,
    experiment_id: str,
    evidence_id: str,
    subject_kind: str,
    subject_id: str,
    decision: str,
    metrics: dict[str, float] | None = None,
) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=evidence_id,
        experiment_id=experiment_id,
        subject_kind=subject_kind,
        subject_id=subject_id,
        subject_version="1.0",
        hypothesis="h",
        decision=decision,
        feature_artifact_uri="artifacts/art-1.parquet",
        artifact_hash="sha256:art",
        created_at=CREATED_AT,
        metrics=metrics or {},
    )


def _seed(store: object) -> None:
    store.save_manifest(_manifest("EXP-DATA"))
    store.save_manifest(_manifest("EXP-FEAT"))
    store.save_manifest(_manifest("EXP-DET"))
    store.save_evidence(
        _evidence(
            experiment_id="EXP-DATA",
            evidence_id="EV-D1",
            subject_kind="dataset",
            subject_id="roll_audit",
            decision="HOLD",
            metrics={"gap_ratio": 0.12},
        )
    )
    store.save_evidence(
        _evidence(
            experiment_id="EXP-FEAT",
            evidence_id="EV-F1",
            subject_kind="feature_sensor",
            subject_id="atr_compression",
            decision="HOLD",
            metrics={"sr_60": 0.41},
        )
    )
    store.save_evidence(
        _evidence(
            experiment_id="EXP-FEAT",
            evidence_id="EV-F2",
            subject_kind="feature_sensor",
            subject_id="volume_ratio",
            decision="REVERT",
            metrics={"sr_60": -0.02},
        )
    )
    store.save_evidence(
        _evidence(
            experiment_id="EXP-DET",
            evidence_id="EV-DET1",
            subject_kind="detector",
            subject_id="OPP16",
            decision="HOLD",
        )
    )


class ProjectionContractAssertions:
    """Shared DoD assertions over Memory and Filesystem backends."""

    store: object

    def test_portfolio_buckets_frozen_and_complete(self) -> None:
        self.assertEqual(
            PORTFOLIO_BUCKETS,
            ("DATA", "FEATURE", "PATTERN", "DETECTOR", "EXECUTION"),
        )
        builder = ProjectionBuilder(self.store)
        portfolio = builder.build_portfolio(built_at=BUILT_AT)
        self.assertEqual(set(portfolio.buckets), set(PORTFOLIO_BUCKETS))
        self.assertEqual(portfolio.experiment_count, 3)
        self.assertEqual(portfolio.evidence_count, 4)
        self.assertEqual(portfolio.buckets["DATA"].evidence_count, 1)
        self.assertEqual(portfolio.buckets["FEATURE"].evidence_count, 2)
        self.assertEqual(portfolio.buckets["DETECTOR"].evidence_count, 1)
        self.assertEqual(portfolio.buckets["PATTERN"].evidence_count, 0)
        self.assertEqual(portfolio.buckets["EXECUTION"].evidence_count, 0)

    def test_negative_and_hold_evidence_not_omitted(self) -> None:
        portfolio = ProjectionBuilder(self.store).build_portfolio(built_at=BUILT_AT)
        feat = portfolio.buckets["FEATURE"]
        self.assertEqual(feat.decision_counts.get("HOLD"), 1)
        self.assertEqual(feat.decision_counts.get("REVERT"), 1)
        decisions = {ref.decision for ref in feat.refs}
        self.assertEqual(decisions, {"HOLD", "REVERT"})

    def test_zero_knowledge_duplication_copies_metrics_verbatim(self) -> None:
        portfolio = ProjectionBuilder(self.store).build_portfolio(built_at=BUILT_AT)
        by_id = {
            ref.evidence_id: ref
            for bucket in portfolio.buckets.values()
            for ref in bucket.refs
        }
        self.assertEqual(by_id["EV-F1"].metrics["sr_60"], 0.41)
        self.assertEqual(by_id["EV-F2"].metrics["sr_60"], -0.02)
        self.assertEqual(by_id["EV-D1"].metrics["gap_ratio"], 0.12)
        # Projection must not invent a composite score.
        for ref in by_id.values():
            self.assertNotIn("score", ref.metrics)
            self.assertNotIn("portfolio_score", ref.metrics)

    def test_read_view_rejects_write_back(self) -> None:
        view = EvidenceReadView.wrap(self.store)
        with self.assertRaises(PermissionError):
            view.save_manifest(_manifest("EXP-X"))
        with self.assertRaises(PermissionError):
            view.save_evidence(
                _evidence(
                    experiment_id="EXP-DATA",
                    evidence_id="EV-NEW",
                    subject_kind="dataset",
                    subject_id="x",
                    decision="HOLD",
                )
            )
        for name in ("update", "replace", "overwrite", "delete"):
            with self.subTest(op=name):
                with self.assertRaises(PermissionError):
                    getattr(view, name)()

    def test_builder_does_not_call_save_on_store(self) -> None:
        tracked = _TrackingStore(self.store)
        ProjectionBuilder(tracked).build_portfolio(built_at=BUILT_AT)
        self.assertEqual(tracked.save_manifest_calls, 0)
        self.assertEqual(tracked.save_evidence_calls, 0)


class _TrackingStore:
    """Delegates reads; counts write attempts."""

    def __init__(self, inner: object) -> None:
        self._inner = inner
        self.save_manifest_calls = 0
        self.save_evidence_calls = 0

    def list_experiment_ids(self) -> tuple[str, ...]:
        return self._inner.list_experiment_ids()  # type: ignore[attr-defined]

    def list_evidence_ids(self, experiment_id: str) -> tuple[str, ...]:
        return self._inner.list_evidence_ids(experiment_id)  # type: ignore[attr-defined]

    def load_manifest(self, experiment_id: str) -> ExperimentManifest:
        return self._inner.load_manifest(experiment_id)  # type: ignore[attr-defined]

    def manifest_exists(self, experiment_id: str) -> bool:
        return self._inner.manifest_exists(experiment_id)  # type: ignore[attr-defined]

    def load_evidence(
        self,
        experiment_id: str,
        evidence_id: str,
    ) -> EvidenceRecord:
        return self._inner.load_evidence(experiment_id, evidence_id)  # type: ignore[attr-defined]

    def evidence_exists(self, experiment_id: str, evidence_id: str) -> bool:
        return self._inner.evidence_exists(experiment_id, evidence_id)  # type: ignore[attr-defined]

    def save_manifest(self, manifest: ExperimentManifest) -> None:
        self.save_manifest_calls += 1
        self._inner.save_manifest(manifest)  # type: ignore[attr-defined]

    def save_evidence(self, evidence: EvidenceRecord) -> None:
        self.save_evidence_calls += 1
        self._inner.save_evidence(evidence)  # type: ignore[attr-defined]


class TestMemoryProjectionContract(ProjectionContractAssertions, unittest.TestCase):
    def setUp(self) -> None:
        self.store = MemoryEvidenceRepository()
        _seed(self.store)


class TestFilesystemProjectionContract(ProjectionContractAssertions, unittest.TestCase):
    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.store = EvidenceRepository(Path(self._temp.name))
        _seed(self.store)

    def tearDown(self) -> None:
        self._temp.cleanup()


class TestProjectionReplaceability(unittest.TestCase):
    def test_same_portfolio_shape_across_backends(self) -> None:
        memory = MemoryEvidenceRepository()
        _seed(memory)
        mem_view = ProjectionBuilder(memory).build_portfolio(built_at=BUILT_AT)

        with tempfile.TemporaryDirectory() as tmp:
            fs = EvidenceRepository(Path(tmp))
            _seed(fs)
            fs_view = ProjectionBuilder(fs).build_portfolio(built_at=BUILT_AT)

        self.assertEqual(mem_view.experiment_count, fs_view.experiment_count)
        self.assertEqual(mem_view.evidence_count, fs_view.evidence_count)
        for bucket in PORTFOLIO_BUCKETS:
            self.assertEqual(
                mem_view.buckets[bucket].evidence_count,
                fs_view.buckets[bucket].evidence_count,
            )
            self.assertEqual(
                dict(mem_view.buckets[bucket].decision_counts),
                dict(fs_view.buckets[bucket].decision_counts),
            )


if __name__ == "__main__":
    unittest.main()
