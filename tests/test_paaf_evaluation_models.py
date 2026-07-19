"""Generic Evidence Evaluation model contract tests."""

from __future__ import annotations

import json
import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

from strategies.paaf.evaluation import (
    EvaluationResult,
    MetricDefinition,
    MetricRecord,
    OutcomeDefinition,
    OutcomeRecord,
)
from strategies.paaf.evidence import EvidenceRecord


CREATED_AT = datetime(2026, 7, 19, 10, 0, tzinfo=timezone.utc)


def _outcome_definition(**overrides: object) -> OutcomeDefinition:
    values: dict[str, object] = {
        "outcome_id": "OUT-FUTURE-VALUE",
        "name": "future_value",
        "window": {"bars_forward": 30, "bar": "1m"},
        "unit": "ratio",
        "description": "Fixture outcome; no market implementation.",
    }
    values.update(overrides)
    return OutcomeDefinition(**values)  # type: ignore[arg-type]


def _outcome_record(**overrides: object) -> OutcomeRecord:
    values: dict[str, object] = {
        "definition_id": "OUT-FUTURE-VALUE",
        "values": {"mean": 0.17, "bucket": "fixture"},
        "sample_n": 123.5,
        "artifact_refs": ("features-001",),
    }
    values.update(overrides)
    return OutcomeRecord(**values)  # type: ignore[arg-type]


def _metric_definition(**overrides: object) -> MetricDefinition:
    values: dict[str, object] = {
        "metric_id": "MET-FIXTURE-MEAN",
        "name": "fixture_mean",
        "formula_id": "fixture_mean_v1",
        "higher_is_better": None,
    }
    values.update(overrides)
    return MetricDefinition(**values)  # type: ignore[arg-type]


def _metric_record(**overrides: object) -> MetricRecord:
    values: dict[str, object] = {
        "metric_id": "MET-FIXTURE-MEAN",
        "value": 0.17,
        "sample_n": 123.5,
    }
    values.update(overrides)
    return MetricRecord(**values)  # type: ignore[arg-type]


def _evaluation(**overrides: object) -> EvaluationResult:
    values: dict[str, object] = {
        "evaluation_id": "EVAL-001",
        "experiment_id": "EXP-001",
        "evidence_id": None,
        "hypothesis": "Fixture observation predicts fixture outcome.",
        "decision": "HOLD",
        "outcome_refs": ("OUT-FUTURE-VALUE",),
        "metric_refs": ("MET-FIXTURE-MEAN",),
        "outcomes": (_outcome_record(),),
        "metrics": (_metric_record(),),
        "created_at": CREATED_AT,
        "metadata": {"author": "caller"},
    }
    values.update(overrides)
    return EvaluationResult(**values)  # type: ignore[arg-type]


class TestEvaluationDefinitions(unittest.TestCase):
    def test_outcome_definition_is_immutable_and_round_trips(self) -> None:
        original = _outcome_definition()
        with self.assertRaises(FrozenInstanceError):
            original.name = "changed"  # type: ignore[misc]
        with self.assertRaises(TypeError):
            original.window["bars_forward"] = 60  # type: ignore[index]

        payload = json.loads(json.dumps(original.to_dict()))
        self.assertEqual(OutcomeDefinition.from_dict(payload), original)

    def test_metric_definition_is_identity_not_formula_code(self) -> None:
        original = _metric_definition()
        payload = json.loads(json.dumps(original.to_dict()))

        self.assertEqual(MetricDefinition.from_dict(payload), original)
        self.assertEqual(original.formula_id, "fixture_mean_v1")
        self.assertFalse(callable(original.formula_id))

    def test_definition_required_fields_and_schema_are_validated(self) -> None:
        with self.assertRaisesRegex(ValueError, "outcome_id"):
            _outcome_definition(outcome_id="")
        with self.assertRaisesRegex(ValueError, "formula_id"):
            _metric_definition(formula_id=" ")
        with self.assertRaisesRegex(ValueError, "schema"):
            _metric_definition(schema_version="2.0")


class TestEvaluationRecords(unittest.TestCase):
    def test_outcome_record_is_separate_from_definition(self) -> None:
        record = _outcome_record()

        self.assertEqual(record.definition_id, _outcome_definition().outcome_id)
        self.assertFalse(hasattr(record, "name"))
        with self.assertRaises(TypeError):
            record.values["mean"] = 1.0  # type: ignore[index]

    def test_records_round_trip_json(self) -> None:
        outcome = _outcome_record()
        metric = _metric_record()

        self.assertEqual(
            OutcomeRecord.from_dict(
                json.loads(json.dumps(outcome.to_dict()))
            ),
            outcome,
        )
        self.assertEqual(
            MetricRecord.from_dict(
                json.loads(json.dumps(metric.to_dict()))
            ),
            metric,
        )

    def test_sample_n_supports_effective_fractional_count(self) -> None:
        self.assertEqual(_outcome_record().sample_n, 123.5)
        self.assertEqual(_metric_record(sample_n=120).sample_n, 120.0)

    def test_nonfinite_values_and_negative_sample_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "有限"):
            _metric_record(value=float("nan"))
        with self.assertRaisesRegex(ValueError, "非负"):
            _outcome_record(sample_n=-1)

    def test_trading_semantics_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "交易语义"):
            _outcome_record(values={"direction": "LONG"})


class TestEvaluationResult(unittest.TestCase):
    def test_is_immutable_and_round_trips_json(self) -> None:
        original = _evaluation()
        with self.assertRaises(FrozenInstanceError):
            original.decision = "KEEP"  # type: ignore[misc]
        with self.assertRaises(TypeError):
            original.metadata["author"] = "changed"  # type: ignore[index]

        payload = json.loads(json.dumps(original.to_dict()))
        self.assertEqual(EvaluationResult.from_dict(payload), original)

    def test_optional_evidence_reference_and_keep_gate(self) -> None:
        self.assertIsNone(_evaluation().evidence_id)
        with self.assertRaisesRegex(ValueError, "KEEP.*evidence_id"):
            _evaluation(decision="KEEP", evidence_id=None)

        keep = _evaluation(decision="KEEP", evidence_id="EV-001")
        self.assertEqual(keep.evidence_id, "EV-001")

    def test_unregistered_record_ids_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "outcome_refs"):
            _evaluation(outcome_refs=("OUT-OTHER",))
        with self.assertRaisesRegex(ValueError, "metric_refs"):
            _evaluation(metric_refs=("MET-OTHER",))

    def test_duplicate_record_ids_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "重复"):
            _evaluation(
                outcomes=(_outcome_record(), _outcome_record()),
            )

    def test_metadata_rejects_trading_semantics(self) -> None:
        with self.assertRaisesRegex(ValueError, "交易语义"):
            _evaluation(metadata={"weight": "0.5"})

    def test_timezone_decision_and_schema_are_validated(self) -> None:
        with self.assertRaisesRegex(ValueError, "时区"):
            _evaluation(created_at=datetime(2026, 7, 19, 10, 0))
        with self.assertRaisesRegex(ValueError, "decision"):
            _evaluation(decision="PROMOTE")
        with self.assertRaisesRegex(ValueError, "schema"):
            _evaluation(schema_version="2.0")

    def test_evaluation_does_not_mutate_evidence(self) -> None:
        evidence = EvidenceRecord(
            evidence_id="EV-001",
            experiment_id="EXP-001",
            subject_kind="feature_sensor",
            subject_id="fixture_sensor",
            subject_version="1.0",
            hypothesis="Fixture hypothesis.",
            decision="HOLD",
            feature_artifact_uri="artifacts/features-001/data.bin",
            artifact_hash="sha256:fixture",
            created_at=CREATED_AT,
        )
        before = evidence.to_dict()

        evaluation = _evaluation(evidence_id=evidence.evidence_id)

        self.assertEqual(evaluation.evidence_id, "EV-001")
        self.assertEqual(evidence.to_dict(), before)


if __name__ == "__main__":
    unittest.main()
