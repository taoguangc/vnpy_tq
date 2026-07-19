"""Filesystem EvidenceRepository contract tests."""

from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

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
        sensor_id="atr_compression",
        sensor_version="1.0",
        parameters={"atr_window": 14},
        parameter_fingerprint="sha256:params",
        code_revision="git:abc",
        data_fingerprint="sha256:data",
        environment_fingerprint="sha256:env",
        artifact_refs=(
            ArtifactReference(
                artifact_id="features-001",
                uri="artifacts/features-001/features.parquet",
                content_hash="sha256:artifact",
                artifact_type="feature_results",
            ),
        ),
    )


def _evidence(
    experiment_id: str = "EXP-001",
    evidence_id: str = "EV-001",
) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=evidence_id,
        experiment_id=experiment_id,
        subject_kind="feature_sensor",
        subject_id="atr_compression",
        subject_version="1.0",
        hypothesis="Compression precedes volatility expansion.",
        decision="HOLD",
        feature_artifact_uri="artifacts/features-001/features.parquet",
        artifact_hash="sha256:artifact",
        created_at=CREATED_AT,
    )


class TestEvidenceRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.repository = EvidenceRepository(self.root)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_manifest_round_trip_and_exists(self) -> None:
        manifest = _manifest()

        self.assertFalse(self.repository.manifest_exists(manifest.experiment_id))
        self.repository.save_manifest(manifest)

        self.assertTrue(self.repository.manifest_exists(manifest.experiment_id))
        self.assertEqual(
            self.repository.load_manifest(manifest.experiment_id),
            manifest,
        )
        self.assertTrue((self.root / "EXP-001" / "manifest.json").is_file())

    def test_evidence_round_trip_and_multiple_records(self) -> None:
        self.repository.save_manifest(_manifest())
        first = _evidence(evidence_id="EV-001")
        second = _evidence(evidence_id="EV-002")

        self.repository.save_evidence(first)
        self.repository.save_evidence(second)

        self.assertEqual(
            self.repository.load_evidence("EXP-001", "EV-001"),
            first,
        )
        self.assertEqual(
            self.repository.load_evidence("EXP-001", "EV-002"),
            second,
        )
        self.assertTrue(self.repository.evidence_exists("EXP-001", "EV-001"))

    def test_existing_records_cannot_be_overwritten(self) -> None:
        manifest = _manifest()
        self.repository.save_manifest(manifest)
        with self.assertRaises(FileExistsError):
            self.repository.save_manifest(manifest)

        evidence = _evidence()
        self.repository.save_evidence(evidence)
        with self.assertRaises(FileExistsError):
            self.repository.save_evidence(evidence)

    def test_missing_records_raise_file_not_found(self) -> None:
        with self.assertRaises(FileNotFoundError):
            self.repository.load_manifest("EXP-MISSING")
        with self.assertRaises(FileNotFoundError):
            self.repository.load_evidence("EXP-MISSING", "EV-MISSING")

    def test_evidence_requires_existing_manifest(self) -> None:
        with self.assertRaises(FileNotFoundError):
            self.repository.save_evidence(_evidence())
        self.assertFalse(self.repository.evidence_exists("EXP-001", "EV-001"))

    def test_experiments_are_path_isolated(self) -> None:
        manifest_a = _manifest("EXP-A")
        manifest_b = _manifest("EXP-B")
        self.repository.save_manifest(manifest_a)
        self.repository.save_manifest(manifest_b)
        self.repository.save_evidence(_evidence("EXP-A", "EV-SAME"))
        self.repository.save_evidence(_evidence("EXP-B", "EV-SAME"))

        loaded_a = self.repository.load_evidence("EXP-A", "EV-SAME")
        loaded_b = self.repository.load_evidence("EXP-B", "EV-SAME")
        self.assertEqual(loaded_a.experiment_id, "EXP-A")
        self.assertEqual(loaded_b.experiment_id, "EXP-B")

    def test_path_traversal_ids_are_rejected(self) -> None:
        for invalid in ("..", "../escape", r"..\\escape", "C:escape"):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(ValueError, "路径"):
                    self.repository.manifest_exists(invalid)

        self.repository.save_manifest(_manifest())
        with self.assertRaisesRegex(ValueError, "路径"):
            self.repository.evidence_exists("EXP-001", "../EV")

    def test_repository_does_not_copy_artifact_content(self) -> None:
        self.repository.save_manifest(_manifest())

        self.assertFalse((self.root / "EXP-001" / "artifacts").exists())


if __name__ == "__main__":
    unittest.main()
