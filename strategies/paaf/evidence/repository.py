"""Filesystem persistence boundary for Evidence Engine Phase 0/2.1.

Complies with ``docs/specs/APPEND_ONLY_STORAGE_SPEC.md`` (Decision 018):
create-only writes, immutable records, read paths never mutate.
``save_*`` names are retained; semantics are create-once (not update).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Mapping

from strategies.paaf.evidence.hashing import canonical_json_dumps
from strategies.paaf.evidence.models import EvidenceRecord, ExperimentManifest
from strategies.paaf.evidence.storage_protocol import ForbiddenStorageOperations

if TYPE_CHECKING:
    from strategies.paaf.evaluation.models import (
        EvaluationResult,
        MetricDefinition,
        OutcomeDefinition,
    )


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
    """Create-only write; never overwrite an existing path."""

    serialized = f"{canonical_json_dumps(payload)}\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as file:
            file.write(serialized)
    except FileExistsError as exc:
        raise FileExistsError(
            "Storage Contract create-only: "
            f"record already exists: {path}"
        ) from exc


class EvidenceRepository(ForbiddenStorageOperations):
    """Append-only filesystem repository for manifests, evidence, and evaluations."""

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

    def _outcome_definition_path(
        self,
        experiment_id: str,
        outcome_id: str,
    ) -> Path:
        safe_outcome_id = _validate_path_segment(outcome_id, "outcome_id")
        return (
            self._experiment_dir(experiment_id)
            / "definitions"
            / "outcomes"
            / f"{safe_outcome_id}.json"
        )

    def _metric_definition_path(
        self,
        experiment_id: str,
        metric_id: str,
    ) -> Path:
        safe_metric_id = _validate_path_segment(metric_id, "metric_id")
        return (
            self._experiment_dir(experiment_id)
            / "definitions"
            / "metrics"
            / f"{safe_metric_id}.json"
        )

    def _evaluation_path(
        self,
        experiment_id: str,
        evaluation_id: str,
    ) -> Path:
        safe_evaluation_id = _validate_path_segment(
            evaluation_id,
            "evaluation_id",
        )
        return (
            self._experiment_dir(experiment_id)
            / "evaluation"
            / f"{safe_evaluation_id}.json"
        )

    def _require_manifest(self, experiment_id: str) -> None:
        if not self.manifest_exists(experiment_id):
            raise FileNotFoundError(self._manifest_path(experiment_id))

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

        self._require_manifest(evidence.experiment_id)
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

    def list_evidence_ids(self, experiment_id: str) -> tuple[str, ...]:
        """List evidence IDs for one experiment (sorted); empty if none."""

        _validate_path_segment(experiment_id, "experiment_id")
        evidence_dir = self._experiment_dir(experiment_id) / "evidence"
        if not evidence_dir.is_dir():
            return ()
        return tuple(
            sorted(path.stem for path in evidence_dir.glob("*.json"))
        )

    def save_outcome_definition(
        self,
        experiment_id: str,
        definition: OutcomeDefinition,
    ) -> None:
        self._require_manifest(experiment_id)
        _write_new_json(
            self._outcome_definition_path(experiment_id, definition.outcome_id),
            definition.to_dict(),
        )

    def load_outcome_definition(
        self,
        experiment_id: str,
        outcome_id: str,
    ) -> OutcomeDefinition:
        from strategies.paaf.evaluation.models import OutcomeDefinition

        return OutcomeDefinition.from_dict(
            _load_json(
                self._outcome_definition_path(experiment_id, outcome_id)
            )
        )

    def outcome_definition_exists(
        self,
        experiment_id: str,
        outcome_id: str,
    ) -> bool:
        return self._outcome_definition_path(
            experiment_id,
            outcome_id,
        ).is_file()

    def save_metric_definition(
        self,
        experiment_id: str,
        definition: MetricDefinition,
    ) -> None:
        self._require_manifest(experiment_id)
        _write_new_json(
            self._metric_definition_path(experiment_id, definition.metric_id),
            definition.to_dict(),
        )

    def load_metric_definition(
        self,
        experiment_id: str,
        metric_id: str,
    ) -> MetricDefinition:
        from strategies.paaf.evaluation.models import MetricDefinition

        return MetricDefinition.from_dict(
            _load_json(self._metric_definition_path(experiment_id, metric_id))
        )

    def metric_definition_exists(
        self,
        experiment_id: str,
        metric_id: str,
    ) -> bool:
        return self._metric_definition_path(
            experiment_id,
            metric_id,
        ).is_file()

    def save_evaluation(self, evaluation: EvaluationResult) -> None:
        """Persist evaluation once; referenced definitions must already exist."""

        self._require_manifest(evaluation.experiment_id)
        self._validate_evaluation_definitions(evaluation)
        self._validate_evaluation_evidence_link(evaluation)
        _write_new_json(
            self._evaluation_path(
                evaluation.experiment_id,
                evaluation.evaluation_id,
            ),
            evaluation.to_dict(),
        )

    def load_evaluation(
        self,
        experiment_id: str,
        evaluation_id: str,
    ) -> EvaluationResult:
        from strategies.paaf.evaluation.models import EvaluationResult

        return EvaluationResult.from_dict(
            _load_json(self._evaluation_path(experiment_id, evaluation_id))
        )

    def evaluation_exists(
        self,
        experiment_id: str,
        evaluation_id: str,
    ) -> bool:
        return self._evaluation_path(experiment_id, evaluation_id).is_file()

    def _validate_evaluation_definitions(
        self,
        evaluation: EvaluationResult,
    ) -> None:
        for outcome_id in evaluation.outcome_refs:
            if not self.outcome_definition_exists(
                evaluation.experiment_id,
                outcome_id,
            ):
                raise FileNotFoundError(
                    self._outcome_definition_path(
                        evaluation.experiment_id,
                        outcome_id,
                    )
                )
        for metric_id in evaluation.metric_refs:
            if not self.metric_definition_exists(
                evaluation.experiment_id,
                metric_id,
            ):
                raise FileNotFoundError(
                    self._metric_definition_path(
                        evaluation.experiment_id,
                        metric_id,
                    )
                )

    def _validate_evaluation_evidence_link(
        self,
        evaluation: EvaluationResult,
    ) -> None:
        claimed = self._find_evidence_claiming_evaluation(
            evaluation.experiment_id,
            evaluation.evaluation_id,
        )
        if claimed is not None:
            if (
                evaluation.evidence_id is not None
                and claimed.evidence_id != evaluation.evidence_id
            ):
                raise ValueError("Evidence 与 Evaluation 的 evidence_id 不一致")
            if evaluation.evidence_id is None:
                raise ValueError("Evidence 与 Evaluation 的 evidence_id 不一致")

        if evaluation.evidence_id is None:
            return
        if not self.evidence_exists(
            evaluation.experiment_id,
            evaluation.evidence_id,
        ):
            return

        evidence = self.load_evidence(
            evaluation.experiment_id,
            evaluation.evidence_id,
        )
        if evidence.evidence_id != evaluation.evidence_id:
            raise ValueError("Evidence 与 Evaluation 的 evidence_id 不一致")
        if evidence.experiment_id != evaluation.experiment_id:
            raise ValueError("Evidence 与 Evaluation 的 experiment_id 不一致")

        linked = evidence.metadata.get("evaluation_id")
        if linked and linked != evaluation.evaluation_id:
            raise ValueError("Evidence 已链接到其它 EvaluationResult")

    def _find_evidence_claiming_evaluation(
        self,
        experiment_id: str,
        evaluation_id: str,
    ) -> EvidenceRecord | None:
        evidence_dir = self._experiment_dir(experiment_id) / "evidence"
        if not evidence_dir.is_dir():
            return None
        for path in sorted(evidence_dir.glob("*.json")):
            evidence = EvidenceRecord.from_dict(_load_json(path))
            if evidence.metadata.get("evaluation_id") == evaluation_id:
                return evidence
        return None
