"""In-memory AppendOnlyEvidenceStore for replaceability contract tests."""

from __future__ import annotations

from strategies.paaf.evidence.models import EvidenceRecord, ExperimentManifest
from strategies.paaf.evidence.storage_protocol import ForbiddenStorageOperations


class MemoryEvidenceRepository(ForbiddenStorageOperations):
    """Create-only dict backend; Domain objects unchanged vs filesystem store."""

    def __init__(self) -> None:
        self._manifests: dict[str, ExperimentManifest] = {}
        self._evidence: dict[tuple[str, str], EvidenceRecord] = {}

    def save_manifest(self, manifest: ExperimentManifest) -> None:
        if manifest.experiment_id in self._manifests:
            raise FileExistsError(
                "Storage Contract create-only: "
                f"manifest already exists: {manifest.experiment_id}"
            )
        self._manifests[manifest.experiment_id] = manifest

    def load_manifest(self, experiment_id: str) -> ExperimentManifest:
        try:
            return self._manifests[experiment_id]
        except KeyError as exc:
            raise FileNotFoundError(experiment_id) from exc

    def manifest_exists(self, experiment_id: str) -> bool:
        return experiment_id in self._manifests

    def save_evidence(self, evidence: EvidenceRecord) -> None:
        if evidence.experiment_id not in self._manifests:
            raise FileNotFoundError(evidence.experiment_id)
        key = (evidence.experiment_id, evidence.evidence_id)
        if key in self._evidence:
            raise FileExistsError(
                "Storage Contract create-only: "
                f"evidence already exists: {evidence.evidence_id}"
            )
        self._evidence[key] = evidence

    def load_evidence(
        self,
        experiment_id: str,
        evidence_id: str,
    ) -> EvidenceRecord:
        try:
            return self._evidence[(experiment_id, evidence_id)]
        except KeyError as exc:
            raise FileNotFoundError(
                f"{experiment_id}/{evidence_id}"
            ) from exc

    def evidence_exists(self, experiment_id: str, evidence_id: str) -> bool:
        return (experiment_id, evidence_id) in self._evidence

    def list_evidence_ids(self, experiment_id: str) -> tuple[str, ...]:
        ids = [
            evidence_id
            for exp_id, evidence_id in self._evidence
            if exp_id == experiment_id
        ]
        return tuple(sorted(ids))

    def list_experiment_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._manifests))
