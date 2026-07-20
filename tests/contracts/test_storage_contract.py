"""Storage Contract compliance tests (Decision 018).

Validates Append-only Storage Spec against replaceable backends.
Does not bind Domain semantics to a concrete filesystem layout.
"""

from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from strategies.paaf.evidence.memory_repository import MemoryEvidenceRepository
from strategies.paaf.evidence.models import (
    ArtifactReference,
    EvidenceRecord,
    ExperimentManifest,
)
from strategies.paaf.evidence.repository import EvidenceRepository
from strategies.paaf.evidence.storage_protocol import AppendOnlyEvidenceStore

CREATED_AT = datetime(2026, 7, 19, 10, 0, tzinfo=timezone.utc)
CREATED_AT_B = datetime(2026, 7, 19, 11, 0, tzinfo=timezone.utc)


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
    *,
    decision: str = "HOLD",
    metadata: dict[str, str] | None = None,
    created_at: datetime = CREATED_AT,
) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=evidence_id,
        experiment_id=experiment_id,
        subject_kind="feature_sensor",
        subject_id="atr_compression",
        subject_version="1.0",
        hypothesis="Compression precedes volatility expansion.",
        decision=decision,
        feature_artifact_uri="artifacts/features-001/features.parquet",
        artifact_hash="sha256:artifact",
        created_at=created_at,
        metadata=metadata or {},
    )


class StorageContractAssertions:
    """Shared DoD assertions over any AppendOnlyEvidenceStore (not a test case)."""

    store: AppendOnlyEvidenceStore

    def test_protocol_runtime_checkable(self) -> None:
        self.assertIsInstance(self.store, AppendOnlyEvidenceStore)

    def test_create_only_manifest_and_evidence(self) -> None:
        manifest = _manifest()
        self.assertFalse(self.store.manifest_exists(manifest.experiment_id))
        self.store.save_manifest(manifest)
        self.assertTrue(self.store.manifest_exists(manifest.experiment_id))
        with self.assertRaises(FileExistsError):
            self.store.save_manifest(manifest)

        evidence = _evidence()
        self.store.save_evidence(evidence)
        self.assertTrue(
            self.store.evidence_exists(evidence.experiment_id, evidence.evidence_id)
        )
        with self.assertRaises(FileExistsError):
            self.store.save_evidence(evidence)

    def test_immutable_record_round_trip(self) -> None:
        self.store.save_manifest(_manifest())
        original = _evidence()
        self.store.save_evidence(original)
        loaded = self.store.load_evidence("EXP-001", "EV-001")
        self.assertEqual(loaded, original)
        self.assertEqual(
            self.store.load_manifest("EXP-001"),
            _manifest(),
        )

    def test_forbidden_operations_explicitly_rejected(self) -> None:
        for name in ("update", "replace", "overwrite", "delete"):
            with self.subTest(op=name):
                method = getattr(self.store, name)
                with self.assertRaises(PermissionError):
                    method()

    def test_list_evidence_ids_append_only(self) -> None:
        self.store.save_manifest(_manifest())
        self.assertEqual(self.store.list_evidence_ids("EXP-001"), ())
        self.store.save_evidence(_evidence(evidence_id="EV-002"))
        self.store.save_evidence(_evidence(evidence_id="EV-001"))
        self.assertEqual(
            self.store.list_evidence_ids("EXP-001"),
            ("EV-001", "EV-002"),
        )

    def test_provenance_parent_creates_new_record_without_mutating_parent(
        self,
    ) -> None:
        self.store.save_manifest(_manifest())
        parent = _evidence(evidence_id="EV-A", decision="HOLD")
        self.store.save_evidence(parent)

        child = _evidence(
            evidence_id="EV-B",
            decision="REVERT",
            metadata={"parent": "EV-A"},
            created_at=CREATED_AT_B,
        )
        self.store.save_evidence(child)

        loaded_parent = self.store.load_evidence("EXP-001", "EV-A")
        loaded_child = self.store.load_evidence("EXP-001", "EV-B")
        self.assertEqual(loaded_parent, parent)
        self.assertEqual(loaded_child.metadata.get("parent"), "EV-A")
        self.assertEqual(loaded_child.decision, "REVERT")
        with self.assertRaises(FileExistsError):
            self.store.save_evidence(parent)


class TestFilesystemStorageContract(StorageContractAssertions, unittest.TestCase):
    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.store = EvidenceRepository(Path(self._temp.name))

    def tearDown(self) -> None:
        self._temp.cleanup()


class TestMemoryStorageContract(StorageContractAssertions, unittest.TestCase):
    def setUp(self) -> None:
        self.store = MemoryEvidenceRepository()


class TestReplaceabilityAcrossBackends(unittest.TestCase):
    """Same Domain objects work against filesystem and memory stores."""

    def test_domain_record_survives_backend_swap(self) -> None:
        manifest = _manifest("EXP-SWAP")
        evidence = _evidence("EXP-SWAP", "EV-SWAP")

        def exercise(factory: Callable[[], AppendOnlyEvidenceStore]) -> None:
            store = factory()
            store.save_manifest(manifest)
            store.save_evidence(evidence)
            self.assertEqual(store.load_manifest("EXP-SWAP"), manifest)
            self.assertEqual(
                store.load_evidence("EXP-SWAP", "EV-SWAP"),
                evidence,
            )
            self.assertEqual(
                store.list_evidence_ids("EXP-SWAP"),
                ("EV-SWAP",),
            )

        with tempfile.TemporaryDirectory() as tmp:
            exercise(lambda: EvidenceRepository(Path(tmp)))
        exercise(MemoryEvidenceRepository)


if __name__ == "__main__":
    unittest.main()
