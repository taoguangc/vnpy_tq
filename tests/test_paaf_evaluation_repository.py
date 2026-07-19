"""Evaluation persistence and fingerprint contract tests."""

from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from strategies.paaf.evaluation import (
    EvaluationResult,
    MetricDefinition,
    MetricRecord,
    OutcomeDefinition,
    OutcomeRecord,
    fingerprint_evaluation_body,
)
from strategies.paaf.evidence import (
    ArtifactReference,
    EvidenceRecord,
    EvidenceRepository,
    ExperimentManifest,
)


CREATED_AT = datetime(2026, 7, 19, 10, 0, tzinfo=timezone.utc)


def _manifest(experiment_id: str = "EXP-001") -> ExperimentManifest:
    return ExperimentManifest(
        experiment_id=experiment_id,
        sensor_id="fixture_sensor",
        sensor_version="1.0",
        parameters={"window": 14},
        parameter_fingerprint="sha256:params",
        code_revision="git:abc",
        data_fingerprint="sha256:data",
        environment_fingerprint="sha256:env",
        artifact_refs=(
            ArtifactReference(
                artifact_id="features-001",
                uri="artifacts/features-001/data.bin",
                content_hash="sha256:fixture",
                artifact_type="feature_results",
            ),
        ),
    )


def _outcome_definition() -> OutcomeDefinition:
    return OutcomeDefinition(
        outcome_id="OUT-FUTURE-VALUE",
        name="future_value",
        window={"bars_forward": 30, "bar": "1m"},
    )


def _metric_definition() -> MetricDefinition:
    return MetricDefinition(
        metric_id="MET-FIXTURE-MEAN",
        name="fixture_mean",
        formula_id="fixture_mean_v1",
    )


def _evaluation(
    *,
    evaluation_id: str = "EVAL-001",
    experiment_id: str = "EXP-001",
    evidence_id: str | None = None,
    decision: str = "HOLD",
) -> EvaluationResult:
    return EvaluationResult(
        evaluation_id=evaluation_id,
        experiment_id=experiment_id,
        evidence_id=evidence_id,
        hypothesis="Fixture observation predicts fixture outcome.",
        decision=decision,
        outcome_refs=("OUT-FUTURE-VALUE",),
        metric_refs=("MET-FIXTURE-MEAN",),
        outcomes=(
            OutcomeRecord(
                definition_id="OUT-FUTURE-VALUE",
                values={"mean": 0.17},
                sample_n=123.5,
            ),
        ),
        metrics=(
            MetricRecord(
                metric_id="MET-FIXTURE-MEAN",
                value=0.17,
                sample_n=123.5,
            ),
        ),
        created_at=CREATED_AT,
    )


def _evidence(
    *,
    evidence_id: str = "EV-001",
    experiment_id: str = "EXP-001",
    evaluation_id: str | None = None,
) -> EvidenceRecord:
    metadata = {"evaluation_id": evaluation_id} if evaluation_id else {}
    return EvidenceRecord(
        evidence_id=evidence_id,
        experiment_id=experiment_id,
        subject_kind="feature_sensor",
        subject_id="fixture_sensor",
        subject_version="1.0",
        hypothesis="Fixture hypothesis.",
        decision="HOLD",
        feature_artifact_uri="artifacts/features-001/data.bin",
        artifact_hash="sha256:fixture",
        created_at=CREATED_AT,
        metadata=metadata,
    )


class TestEvaluationFingerprint(unittest.TestCase):
    def test_evaluation_body_fingerprint_excludes_created_at(self) -> None:
        left = _evaluation()
        right = EvaluationResult(
            evaluation_id="EVAL-001",
            experiment_id="EXP-001",
            evidence_id=None,
            hypothesis="Fixture observation predicts fixture outcome.",
            decision="HOLD",
            outcome_refs=("OUT-FUTURE-VALUE",),
            metric_refs=("MET-FIXTURE-MEAN",),
            outcomes=left.outcomes,
            metrics=left.metrics,
            created_at=datetime(2026, 7, 20, 10, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(
            fingerprint_evaluation_body(left),
            fingerprint_evaluation_body(right),
        )

    def test_evaluation_body_fingerprint_changes_with_metric_value(self) -> None:
        base = _evaluation()
        changed = EvaluationResult(
            evaluation_id="EVAL-001",
            experiment_id="EXP-001",
            evidence_id=None,
            hypothesis=base.hypothesis,
            decision="HOLD",
            outcome_refs=base.outcome_refs,
            metric_refs=base.metric_refs,
            outcomes=base.outcomes,
            metrics=(
                MetricRecord(
                    metric_id="MET-FIXTURE-MEAN",
                    value=0.99,
                    sample_n=123.5,
                ),
            ),
            created_at=CREATED_AT,
        )
        self.assertNotEqual(
            fingerprint_evaluation_body(base),
            fingerprint_evaluation_body(changed),
        )


class TestEvaluationRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.repository = EvidenceRepository(self.root)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _seed_definitions(self, experiment_id: str = "EXP-001") -> None:
        self.repository.save_manifest(_manifest(experiment_id))
        self.repository.save_outcome_definition(
            experiment_id,
            _outcome_definition(),
        )
        self.repository.save_metric_definition(
            experiment_id,
            _metric_definition(),
        )

    def test_definition_round_trip(self) -> None:
        self._seed_definitions()
        outcome = self.repository.load_outcome_definition(
            "EXP-001",
            "OUT-FUTURE-VALUE",
        )
        metric = self.repository.load_metric_definition(
            "EXP-001",
            "MET-FIXTURE-MEAN",
        )
        self.assertEqual(outcome, _outcome_definition())
        self.assertEqual(metric, _metric_definition())
        self.assertTrue(
            (
                self.root
                / "EXP-001"
                / "definitions"
                / "outcomes"
                / "OUT-FUTURE-VALUE.json"
            ).is_file()
        )

    def test_evaluation_round_trip(self) -> None:
        self._seed_definitions()
        evaluation = _evaluation()
        self.repository.save_evaluation(evaluation)
        loaded = self.repository.load_evaluation("EXP-001", "EVAL-001")
        self.assertEqual(loaded, evaluation)
        self.assertTrue(self.repository.evaluation_exists("EXP-001", "EVAL-001"))

    def test_missing_definition_rejects_evaluation(self) -> None:
        self.repository.save_manifest(_manifest())
        with self.assertRaises(FileNotFoundError):
            self.repository.save_evaluation(_evaluation())

    def test_append_only_definitions_and_evaluations(self) -> None:
        self._seed_definitions()
        with self.assertRaises(FileExistsError):
            self.repository.save_outcome_definition(
                "EXP-001",
                _outcome_definition(),
            )
        evaluation = _evaluation()
        self.repository.save_evaluation(evaluation)
        with self.assertRaises(FileExistsError):
            self.repository.save_evaluation(evaluation)

    def test_evidence_mismatch_is_rejected(self) -> None:
        self._seed_definitions()
        self.repository.save_evidence(
            _evidence(evidence_id="EV-001", evaluation_id="EVAL-001")
        )
        with self.assertRaisesRegex(ValueError, "evidence_id 不一致"):
            self.repository.save_evaluation(
                _evaluation(evidence_id="EV-002")
            )

    def test_evidence_linked_to_other_evaluation_is_rejected(self) -> None:
        self._seed_definitions()
        self.repository.save_evidence(
            _evidence(evidence_id="EV-001", evaluation_id="EVAL-OLD")
        )
        with self.assertRaisesRegex(ValueError, "其它 EvaluationResult"):
            self.repository.save_evaluation(
                _evaluation(evidence_id="EV-001")
            )

    def test_save_evaluation_does_not_mutate_evidence(self) -> None:
        self._seed_definitions()
        evidence = _evidence(evidence_id="EV-001")
        self.repository.save_evidence(evidence)
        before = (
            self.root / "EXP-001" / "evidence" / "EV-001.json"
        ).read_text(encoding="utf-8")

        self.repository.save_evaluation(_evaluation(evidence_id="EV-001"))

        after = (
            self.root / "EXP-001" / "evidence" / "EV-001.json"
        ).read_text(encoding="utf-8")
        self.assertEqual(before, after)
        self.assertEqual(
            self.repository.load_evidence("EXP-001", "EV-001"),
            evidence,
        )

    def test_experiments_are_path_isolated(self) -> None:
        self._seed_definitions("EXP-A")
        self._seed_definitions("EXP-B")
        self.repository.save_evaluation(_evaluation(experiment_id="EXP-A"))
        self.repository.save_evaluation(_evaluation(experiment_id="EXP-B"))
        self.assertEqual(
            self.repository.load_evaluation("EXP-A", "EVAL-001").experiment_id,
            "EXP-A",
        )
        self.assertEqual(
            self.repository.load_evaluation("EXP-B", "EVAL-001").experiment_id,
            "EXP-B",
        )

    def test_path_traversal_ids_are_rejected(self) -> None:
        self._seed_definitions()
        with self.assertRaisesRegex(ValueError, "路径"):
            self.repository.evaluation_exists("EXP-001", "../EVAL")


if __name__ == "__main__":
    unittest.main()
