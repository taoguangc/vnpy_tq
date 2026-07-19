"""Filesystem persistence boundary for Evidence Engine Phase 0."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from strategies.paaf.evidence.hashing import canonical_json_dumps
from strategies.paaf.evidence.models import EvidenceRecord, ExperimentManifest


DEFAULT_EVIDENCE_ROOT = Path("research/output/evidence")
_INVALID_PATH_CHARS = frozenset('<>:"/\\|?*')


def _validate_path_segment(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} 不能为空")
    if value != value.strip():
        raise ValueError(f"{field_name} 不能包含首尾空白")
    if value in {".", ".."} or any(char in value for char in _INVALID_PATH_CHARS):
        raise ValueError(f"{field_name} 包含非法路径字符")
    if "\x00" in value:
        raise ValueError(f"{field_name} 包含非法路径字符")
    return value


def _load_json(path: Path) -> Mapping[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise TypeError(f"{path} 的根对象必须是 JSON object")
    return payload


def _write_new_json(path: Path, payload: Mapping[str, Any]) -> None:
    serialized = f"{canonical_json_dumps(payload)}\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as file:
        file.write(serialized)


class EvidenceRepository:
    """Append-only filesystem repository for manifests and evidence records."""

    def __init__(self, root_path: Path = DEFAULT_EVIDENCE_ROOT) -> None:
        self.root_path = Path(root_path)

    def _experiment_dir(self, experiment_id: str) -> Path:
        safe_id = _validate_path_segment(experiment_id, "experiment_id")
        return self.root_path / safe_id

    def _manifest_path(self, experiment_id: str) -> Path:
        return self._experiment_dir(experiment_id) / "manifest.json"

    def _evidence_path(self, experiment_id: str, evidence_id: str) -> Path:
        safe_evidence_id = _validate_path_segment(evidence_id, "evidence_id")
        return (
            self._experiment_dir(experiment_id)
            / "evidence"
            / f"{safe_evidence_id}.json"
        )

    def save_manifest(self, manifest: ExperimentManifest) -> None:
        """Persist once; an existing experiment manifest is never overwritten."""

        _write_new_json(
            self._manifest_path(manifest.experiment_id),
            manifest.to_dict(),
        )

    def load_manifest(self, experiment_id: str) -> ExperimentManifest:
        """Load a manifest or raise ``FileNotFoundError``."""

        return ExperimentManifest.from_dict(
            _load_json(self._manifest_path(experiment_id))
        )

    def manifest_exists(self, experiment_id: str) -> bool:
        return self._manifest_path(experiment_id).is_file()

    def save_evidence(self, evidence: EvidenceRecord) -> None:
        """Persist once under its experiment; manifest must already exist."""

        if not self.manifest_exists(evidence.experiment_id):
            raise FileNotFoundError(
                self._manifest_path(evidence.experiment_id)
            )
        _write_new_json(
            self._evidence_path(
                evidence.experiment_id,
                evidence.evidence_id,
            ),
            evidence.to_dict(),
        )

    def load_evidence(
        self,
        experiment_id: str,
        evidence_id: str,
    ) -> EvidenceRecord:
        """Load an evidence record or raise ``FileNotFoundError``."""

        return EvidenceRecord.from_dict(
            _load_json(self._evidence_path(experiment_id, evidence_id))
        )

    def evidence_exists(self, experiment_id: str, evidence_id: str) -> bool:
        return self._evidence_path(experiment_id, evidence_id).is_file()
