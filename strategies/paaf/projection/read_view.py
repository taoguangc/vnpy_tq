"""Read-only facade over Evidence stores for Projection consumers."""

from __future__ import annotations

from strategies.paaf.evidence.models import EvidenceRecord, ExperimentManifest

_WRITE_FORBIDDEN = (
    "Projection Contract: read-only; must not write back to Repository"
)


class EvidenceReadView:
    """Exposes load/list/exists only; all mutating entry points raise."""

    def __init__(self, store: object) -> None:
        self._store = store

    @classmethod
    def wrap(cls, source: object) -> "EvidenceReadView":
        if isinstance(source, EvidenceReadView):
            return source
        return cls(source)

    def list_experiment_ids(self) -> tuple[str, ...]:
        return self._store.list_experiment_ids()  # type: ignore[attr-defined]

    def list_evidence_ids(self, experiment_id: str) -> tuple[str, ...]:
        return self._store.list_evidence_ids(experiment_id)  # type: ignore[attr-defined]

    def load_manifest(self, experiment_id: str) -> ExperimentManifest:
        return self._store.load_manifest(experiment_id)  # type: ignore[attr-defined]

    def manifest_exists(self, experiment_id: str) -> bool:
        return self._store.manifest_exists(experiment_id)  # type: ignore[attr-defined]

    def load_evidence(
        self,
        experiment_id: str,
        evidence_id: str,
    ) -> EvidenceRecord:
        return self._store.load_evidence(experiment_id, evidence_id)  # type: ignore[attr-defined]

    def evidence_exists(self, experiment_id: str, evidence_id: str) -> bool:
        return self._store.evidence_exists(experiment_id, evidence_id)  # type: ignore[attr-defined]

    def save_manifest(self, *args: object, **kwargs: object) -> None:
        raise PermissionError(_WRITE_FORBIDDEN)

    def save_evidence(self, *args: object, **kwargs: object) -> None:
        raise PermissionError(_WRITE_FORBIDDEN)

    def update(self, *args: object, **kwargs: object) -> None:
        raise PermissionError(_WRITE_FORBIDDEN)

    def replace(self, *args: object, **kwargs: object) -> None:
        raise PermissionError(_WRITE_FORBIDDEN)

    def overwrite(self, *args: object, **kwargs: object) -> None:
        raise PermissionError(_WRITE_FORBIDDEN)

    def delete(self, *args: object, **kwargs: object) -> None:
        raise PermissionError(_WRITE_FORBIDDEN)
