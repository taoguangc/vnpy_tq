"""Evidence Engine Phase 0 immutable model contract tests."""

from __future__ import annotations

import json
import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

from strategies.paaf.evidence import (
    ArtifactReference,
    EvidenceRecord,
    ExperimentManifest,
)


CREATED_AT = datetime(2026, 7, 19, 10, 0, tzinfo=timezone.utc)


def _artifact(**overrides: object) -> ArtifactReference:
    values: dict[str, object] = {
        "artifact_id": "features-001",
        "uri": "artifacts/features-001/feature_results.parquet",
        "content_hash": "sha256:abc123",
        "artifact_type": "feature_results",
    }
    values.update(overrides)
    return ArtifactReference(**values)  # type: ignore[arg-type]


def _manifest(**overrides: object) -> ExperimentManifest:
    values: dict[str, object] = {
        "experiment_id": "EXP-20260719-001",
        "sensor_id": "atr_compression",
        "sensor_version": "1.0",
        "parameters": {
            "atr_window": 14,
            "baseline_window": 100,
            "normalize": True,
            "profile": "baseline",
        },
        "parameter_fingerprint": "sha256:params",
        "code_revision": "git:abc123",
        "data_fingerprint": "sha256:data",
        "environment_fingerprint": "sha256:env",
        "artifact_refs": (_artifact(),),
    }
    values.update(overrides)
    return ExperimentManifest(**values)  # type: ignore[arg-type]


def _evidence(**overrides: object) -> EvidenceRecord:
    values: dict[str, object] = {
        "evidence_id": "EV-20260719-001",
        "experiment_id": "EXP-20260719-001",
        "subject_kind": "feature_sensor",
        "subject_id": "atr_compression",
        "subject_version": "1.0",
        "hypothesis": "Compression precedes volatility expansion.",
        "decision": "HOLD",
        "feature_artifact_uri": (
            "artifacts/features-001/feature_results.parquet"
        ),
        "artifact_hash": "sha256:abc123",
        "created_at": CREATED_AT,
        "observation": {"atr_ratio": 0.72, "bucket": "low"},
        "outcome": {"realized_volatility": 0.18},
        "window": {"bars_forward": 30, "bar": "1m"},
        "metrics": {"sample_n": 120.0},
        "data_protocol_version": "tq-cbc-1m-v1",
        "metadata": {"author": "unit-test"},
    }
    values.update(overrides)
    return EvidenceRecord(**values)  # type: ignore[arg-type]


class TestArtifactReference(unittest.TestCase):
    def test_is_immutable_and_round_trips_json(self) -> None:
        original = _artifact()

        with self.assertRaises(FrozenInstanceError):
            original.uri = "changed"  # type: ignore[misc]

        payload = json.loads(json.dumps(original.to_dict()))
        self.assertEqual(ArtifactReference.from_dict(payload), original)

    def test_required_fields_and_schema_are_validated(self) -> None:
        with self.assertRaisesRegex(ValueError, "artifact_id"):
            _artifact(artifact_id="")
        with self.assertRaisesRegex(ValueError, "schema"):
            _artifact(schema_version="2.0")


class TestExperimentManifest(unittest.TestCase):
    def test_parameters_and_artifact_refs_are_immutable(self) -> None:
        source_parameters = {"atr_window": 14}
        manifest = _manifest(parameters=source_parameters)
        source_parameters["atr_window"] = 99

        self.assertEqual(manifest.parameters["atr_window"], 14)
        with self.assertRaises(TypeError):
            manifest.parameters["atr_window"] = 20  # type: ignore[index]
        with self.assertRaises(FrozenInstanceError):
            manifest.sensor_version = "2.0"  # type: ignore[misc]

    def test_round_trips_json(self) -> None:
        original = _manifest()
        payload = json.loads(json.dumps(original.to_dict()))

        self.assertEqual(ExperimentManifest.from_dict(payload), original)
        self.assertEqual(payload["artifact_refs"][0]["artifact_id"], "features-001")

    def test_parameters_are_flat_scalars_only(self) -> None:
        with self.assertRaisesRegex(TypeError, "parameters"):
            _manifest(parameters={"nested": {"window": 14}})
        with self.assertRaisesRegex(TypeError, "parameters"):
            _manifest(parameters={"windows": [14, 100]})

    def test_required_fields_and_schema_are_validated(self) -> None:
        with self.assertRaisesRegex(ValueError, "experiment_id"):
            _manifest(experiment_id=" ")
        with self.assertRaisesRegex(ValueError, "schema"):
            _manifest(schema_version="2.0")
        with self.assertRaisesRegex(TypeError, "ArtifactReference"):
            _manifest(artifact_refs=("artifact-id",))


class TestEvidenceRecord(unittest.TestCase):
    def test_is_immutable_and_mappings_are_readonly(self) -> None:
        evidence = _evidence()

        with self.assertRaises(FrozenInstanceError):
            evidence.decision = "KEEP"  # type: ignore[misc]
        with self.assertRaises(TypeError):
            evidence.metrics["sample_n"] = 121.0  # type: ignore[index]
        with self.assertRaises(TypeError):
            evidence.metadata["author"] = "changed"  # type: ignore[index]

    def test_round_trips_json_with_caller_timestamp(self) -> None:
        original = _evidence()
        payload = json.loads(json.dumps(original.to_dict()))
        restored = EvidenceRecord.from_dict(payload)

        self.assertEqual(restored, original)
        self.assertEqual(restored.created_at, CREATED_AT)

    def test_decision_subject_kind_and_timezone_are_validated(self) -> None:
        with self.assertRaisesRegex(ValueError, "decision"):
            _evidence(decision="PROMOTE")
        with self.assertRaisesRegex(ValueError, "subject_kind"):
            _evidence(subject_kind="strategy")
        with self.assertRaisesRegex(ValueError, "时区"):
            _evidence(created_at=datetime(2026, 7, 19, 10, 0))

    def test_required_fields_and_schema_are_validated(self) -> None:
        with self.assertRaisesRegex(ValueError, "evidence_id"):
            _evidence(evidence_id="")
        with self.assertRaisesRegex(ValueError, "feature_artifact_uri"):
            _evidence(feature_artifact_uri="")
        with self.assertRaisesRegex(ValueError, "schema"):
            _evidence(schema_version="2.0")

    def test_mapping_value_types_are_restricted(self) -> None:
        evidence = _evidence(metrics={"sample_n": 120})
        self.assertEqual(evidence.metrics["sample_n"], 120.0)
        with self.assertRaisesRegex(TypeError, "metrics"):
            _evidence(metrics={"valid": True})
        with self.assertRaisesRegex(TypeError, "metadata"):
            _evidence(metadata={"nested": "ok", "bad": 1})


if __name__ == "__main__":
    unittest.main()
