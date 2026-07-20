"""Append-only storage protocol (Decision 018 / Storage Spec).

Defines the replaceable interface surface. Implementations may use any backend.
Public method names such as ``save_*`` remain create-only semantics.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from strategies.paaf.evidence.models import EvidenceRecord, ExperimentManifest

_FORBIDDEN_MESSAGE = (
    "Append-only Storage Contract forbids mutating operations; "
    "create a new record with provenance instead"
)


class ForbiddenStorageOperations:
    """Mixin: explicit reject of update/replace/overwrite/delete."""

    def update(self, *args: object, **kwargs: object) -> None:
        raise PermissionError(_FORBIDDEN_MESSAGE)

    def replace(self, *args: object, **kwargs: object) -> None:
        raise PermissionError(_FORBIDDEN_MESSAGE)

    def overwrite(self, *args: object, **kwargs: object) -> None:
        raise PermissionError(_FORBIDDEN_MESSAGE)

    def delete(self, *args: object, **kwargs: object) -> None:
        raise PermissionError(_FORBIDDEN_MESSAGE)


@runtime_checkable
class AppendOnlyEvidenceStore(Protocol):
    """Minimal create-only evidence store; backends must be interchangeable."""

    def save_manifest(self, manifest: ExperimentManifest) -> None:
        """Create-once; existing ID must fail."""

    def load_manifest(self, experiment_id: str) -> ExperimentManifest:
        """Read-only load."""

    def manifest_exists(self, experiment_id: str) -> bool:
        """Read-only existence check."""

    def save_evidence(self, evidence: EvidenceRecord) -> None:
        """Create-once under an existing experiment."""

    def load_evidence(
        self,
        experiment_id: str,
        evidence_id: str,
    ) -> EvidenceRecord:
        """Read-only load."""

    def evidence_exists(self, experiment_id: str, evidence_id: str) -> bool:
        """Read-only existence check."""

    def list_evidence_ids(self, experiment_id: str) -> tuple[str, ...]:
        """List evidence IDs for one experiment; empty if none."""

    def list_experiment_ids(self) -> tuple[str, ...]:
        """List experiment IDs that have a persisted manifest; empty if none."""
