"""Validation Projection Contract Tests (Sprint 2 / Baseline v1)."""

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
from strategies.paaf.projection import EvidenceReadView, ProjectionBuilder

CREATED_AT = datetime(2026, 7, 19, 10, 0, tzinfo=timezone.utc)
BUILT_AT = datetime(2026, 7, 20, 15, 0, tzinfo=timezone.utc)


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
    metadata: dict[str, str] | None = None,
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
        metadata=metadata or {},
    )


def _seed(store: object) -> None:
    store.save_manifest(_manifest("OPP16_EXP001"))
    store.save_manifest(_manifest("ATR_EXP001"))
    store.save_evidence(
        _evidence(
            experiment_id="OPP16_EXP001",
            evidence_id="EV-RB",
            subject_kind="detector",
            subject_id="OPP16",
            decision="HOLD",
            metrics={"mean_ex": -0.00013},
            metadata={
                "symbol": "rb",
                "evidence_type": "negative",
                "blocking": "Cross-symbol validation missing",
                "suggested_next": "New multi-symbol experiment required",
            },
        )
    )
    store.save_evidence(
        _evidence(
            experiment_id="OPP16_EXP001",
            evidence_id="EV-HC",
            subject_kind="detector",
            subject_id="OPP16",
            decision="REVERT",
            metrics={"mean_ex": -0.001},
            metadata={"symbol": "hc", "evidence_type": "negative"},
        )
    )
    store.save_evidence(
        _evidence(
            experiment_id="ATR_EXP001",
            evidence_id="EV-ATR",
            subject_kind="feature_sensor",
            subject_id="atr_compression",
            decision="HOLD",
            metrics={"sr_60": 0.41},
            metadata={"symbol": "rb", "evidence_type": "inconclusive"},
        )
    )


class ValidationContractAssertions:
    store: object

    def test_comparison_aggregates_without_rescoring(self) -> None:
        builder = ProjectionBuilder(self.store)
        view = builder.build_validation_comparison(built_at=BUILT_AT)
        self.assertEqual(len(view.entries), 3)
        self.assertEqual(view.decision_counts.get("HOLD"), 2)
        self.assertEqual(view.decision_counts.get("REVERT"), 1)
        self.assertEqual(view.status_counts.get("HOLD"), 2)
        self.assertEqual(view.status_counts.get("REJECTED"), 1)
        by_id = {item.evidence_id: item for item in view.entries}
        self.assertEqual(by_id["EV-RB"].metrics["mean_ex"], -0.00013)
        self.assertEqual(by_id["EV-ATR"].metrics["sr_60"], 0.41)
        for item in view.entries:
            self.assertNotIn("score", item.metrics)
            self.assertNotIn("portfolio_score", item.metrics)

    def test_comparison_can_filter_experiments(self) -> None:
        view = ProjectionBuilder(self.store).build_validation_comparison(
            experiment_ids=("OPP16_EXP001",),
            built_at=BUILT_AT,
        )
        self.assertEqual(len(view.entries), 2)
        self.assertTrue(
            all(item.experiment_id == "OPP16_EXP001" for item in view.entries)
        )

    def test_minimal_cross_experiment_query(self) -> None:
        builder = ProjectionBuilder(self.store)
        by_symbol = builder.find_evidence(symbol="rb")
        self.assertEqual({item.evidence_id for item in by_symbol}, {"EV-RB", "EV-ATR"})
        by_type = builder.find_evidence(evidence_type="negative")
        self.assertEqual({item.evidence_id for item in by_type}, {"EV-RB", "EV-HC"})
        by_class = builder.find_evidence(classification="detector")
        self.assertEqual(len(by_class), 2)
        by_status = builder.find_evidence(status="REJECTED")
        self.assertEqual([item.evidence_id for item in by_status], ["EV-HC"])

    def test_promotion_readiness_is_visibility_only(self) -> None:
        readiness = ProjectionBuilder(self.store).build_promotion_readiness(
            experiment_id="OPP16_EXP001",
            evidence_id="EV-RB",
        )
        self.assertEqual(readiness.current, "HOLD")
        self.assertFalse(readiness.may_auto_promote)
        self.assertIn("Cross-symbol validation missing", readiness.blocking)
        self.assertEqual(
            readiness.suggested_next,
            "New multi-symbol experiment required",
        )

    def test_read_only_and_no_save_during_validation_build(self) -> None:
        view = EvidenceReadView.wrap(self.store)
        with self.assertRaises(PermissionError):
            view.save_evidence(
                _evidence(
                    experiment_id="OPP16_EXP001",
                    evidence_id="EV-X",
                    subject_kind="detector",
                    subject_id="OPP16",
                    decision="HOLD",
                )
            )
        before = self.store.list_evidence_ids("OPP16_EXP001")
        ProjectionBuilder(self.store).build_validation_comparison(built_at=BUILT_AT)
        after = self.store.list_evidence_ids("OPP16_EXP001")
        self.assertEqual(before, after)


class TestMemoryValidationContract(ValidationContractAssertions, unittest.TestCase):
    def setUp(self) -> None:
        self.store = MemoryEvidenceRepository()
        _seed(self.store)


class TestFilesystemValidationContract(ValidationContractAssertions, unittest.TestCase):
    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.store = EvidenceRepository(Path(self._temp.name))
        _seed(self.store)

    def tearDown(self) -> None:
        self._temp.cleanup()


if __name__ == "__main__":
    unittest.main()
