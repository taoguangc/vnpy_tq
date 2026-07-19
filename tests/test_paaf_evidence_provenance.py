"""Evidence provenance / hashing contract tests."""

from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from strategies.paaf.evidence.hashing import (
    canonical_json_dumps,
    hash_bytes,
    hash_canonical_json,
    hash_file,
)
from strategies.paaf.evidence.models import (
    ArtifactReference,
    EvidenceRecord,
    ExperimentManifest,
)
from strategies.paaf.evidence.provenance import (
    build_observation_key,
    fingerprint_evidence_body,
    fingerprint_manifest,
    fingerprint_parameters,
    verify_parameter_fingerprint,
)


CREATED_AT = datetime(2026, 7, 19, 10, 0, tzinfo=timezone.utc)


class TestHashing(unittest.TestCase):
    def test_same_bytes_yield_same_hash(self) -> None:
        content = b"feature-row-1\n"
        self.assertEqual(hash_bytes(content), hash_bytes(content))
        self.assertTrue(hash_bytes(content).startswith("sha256:"))

    def test_modified_bytes_change_hash(self) -> None:
        self.assertNotEqual(hash_bytes(b"abc"), hash_bytes(b"abd"))

    def test_hash_file_matches_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "artifact.bin"
            payload = b"immutable-artifact"
            path.write_bytes(payload)
            self.assertEqual(hash_file(path), hash_bytes(payload))

    def test_canonical_json_ignores_key_order(self) -> None:
        left = {"b": 2, "a": 1}
        right = {"a": 1, "b": 2}
        self.assertEqual(canonical_json_dumps(left), canonical_json_dumps(right))
        self.assertEqual(hash_canonical_json(left), hash_canonical_json(right))


class TestProvenance(unittest.TestCase):
    def test_parameter_fingerprint_is_order_independent(self) -> None:
        left = fingerprint_parameters(
            {"baseline_window": 100, "atr_window": 14, "normalize": True}
        )
        right = fingerprint_parameters(
            {"atr_window": 14, "normalize": True, "baseline_window": 100}
        )
        self.assertEqual(left, right)

    def test_parameter_fingerprint_changes_when_value_changes(self) -> None:
        base = fingerprint_parameters({"atr_window": 14})
        changed = fingerprint_parameters({"atr_window": 20})
        self.assertNotEqual(base, changed)

    def test_verify_parameter_fingerprint(self) -> None:
        parameters = {"atr_window": 14, "baseline_window": 100}
        manifest = ExperimentManifest(
            experiment_id="EXP-001",
            sensor_id="atr_compression",
            sensor_version="1.0",
            parameters=parameters,
            parameter_fingerprint=fingerprint_parameters(parameters),
            code_revision="git:abc",
            data_fingerprint="sha256:data",
            environment_fingerprint="sha256:env",
        )
        verify_parameter_fingerprint(manifest)

        broken = ExperimentManifest(
            experiment_id="EXP-001",
            sensor_id="atr_compression",
            sensor_version="1.0",
            parameters=parameters,
            parameter_fingerprint="sha256:wrong",
            code_revision="git:abc",
            data_fingerprint="sha256:data",
            environment_fingerprint="sha256:env",
        )
        with self.assertRaisesRegex(ValueError, "parameter_fingerprint"):
            verify_parameter_fingerprint(broken)

    def test_manifest_fingerprint_stable_for_ref_order(self) -> None:
        ref_a = ArtifactReference(
            artifact_id="a-features",
            uri="artifacts/a-features/data.bin",
            content_hash="sha256:a",
            artifact_type="feature_results",
        )
        ref_b = ArtifactReference(
            artifact_id="b-outcomes",
            uri="artifacts/b-outcomes/data.bin",
            content_hash="sha256:b",
            artifact_type="outcomes",
        )
        parameters = {"atr_window": 14}
        common = {
            "experiment_id": "EXP-001",
            "sensor_id": "atr_compression",
            "sensor_version": "1.0",
            "parameters": parameters,
            "parameter_fingerprint": fingerprint_parameters(parameters),
            "code_revision": "git:abc",
            "data_fingerprint": "sha256:data",
            "environment_fingerprint": "sha256:env",
        }
        left = ExperimentManifest(**common, artifact_refs=(ref_a, ref_b))
        right = ExperimentManifest(**common, artifact_refs=(ref_b, ref_a))
        self.assertEqual(fingerprint_manifest(left), fingerprint_manifest(right))

    def test_evidence_body_fingerprint_excludes_created_at(self) -> None:
        base = EvidenceRecord(
            evidence_id="EV-001",
            experiment_id="EXP-001",
            subject_kind="feature_sensor",
            subject_id="atr_compression",
            subject_version="1.0",
            hypothesis="Compression precedes expansion.",
            decision="HOLD",
            feature_artifact_uri="artifacts/a/data.bin",
            artifact_hash="sha256:a",
            created_at=CREATED_AT,
            metrics={"sample_n": 10.0},
        )
        later = EvidenceRecord(
            evidence_id="EV-001",
            experiment_id="EXP-001",
            subject_kind="feature_sensor",
            subject_id="atr_compression",
            subject_version="1.0",
            hypothesis="Compression precedes expansion.",
            decision="HOLD",
            feature_artifact_uri="artifacts/a/data.bin",
            artifact_hash="sha256:a",
            created_at=datetime(2026, 7, 20, 10, 0, tzinfo=timezone.utc),
            metrics={"sample_n": 10.0},
        )
        self.assertEqual(
            fingerprint_evidence_body(base),
            fingerprint_evidence_body(later),
        )

    def test_observation_key_requires_timezone(self) -> None:
        key = build_observation_key(
            sensor_id="atr_compression",
            sensor_version="1.0",
            parameter_fingerprint="sha256:params",
            symbol="rb888",
            timeframe="1m",
            timestamp=CREATED_AT,
        )
        self.assertIn("atr_compression", key)
        self.assertIn("rb888", key)

        with self.assertRaisesRegex(ValueError, "时区"):
            build_observation_key(
                sensor_id="atr_compression",
                sensor_version="1.0",
                parameter_fingerprint="sha256:params",
                symbol="rb888",
                timeframe="1m",
                timestamp=datetime(2026, 7, 19, 10, 0),
            )


if __name__ == "__main__":
    unittest.main()
