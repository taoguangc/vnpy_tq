"""Immutable Evidence Engine contracts for PAAF v0.3 Phase 0."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Any, Mapping


SCHEMA_VERSION = "1.0"
EVIDENCE_DECISIONS = frozenset({"KEEP", "REVERT", "HOLD"})
SUBJECT_KINDS = frozenset({"feature_sensor", "opportunity", "detector"})

ParameterValue = str | int | float | bool
ObservationValue = float | str
WindowValue = int | str


def _require_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} 不能为空")


def _require_schema(value: str, model_name: str) -> None:
    if value != SCHEMA_VERSION:
        raise ValueError(f"不支持 {model_name} schema: {value}")


def _freeze_typed_mapping(
    value: Mapping[str, Any],
    *,
    field_name: str,
    allowed_types: tuple[type, ...],
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{field_name} 必须是 Mapping")

    copied: dict[str, Any] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise TypeError(f"{field_name} 的键必须是 str")
        if not isinstance(item, allowed_types):
            allowed = ", ".join(item_type.__name__ for item_type in allowed_types)
            raise TypeError(f"{field_name} 的值只允许 {allowed}")
        copied[key] = item
    return MappingProxyType(copied)


def _thaw_mapping(value: Mapping[str, Any]) -> dict[str, Any]:
    return dict(value)


def _freeze_float_mapping(
    value: Mapping[str, Any],
    *,
    field_name: str,
) -> Mapping[str, float]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{field_name} 必须是 Mapping")

    copied: dict[str, float] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise TypeError(f"{field_name} 的键必须是 str")
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise TypeError(f"{field_name} 的值只允许 int 或 float")
        copied[key] = float(item)
    return MappingProxyType(copied)


@dataclass(frozen=True)
class ArtifactReference:
    """Reference to immutable artifact content; never loads the artifact."""

    artifact_id: str
    uri: str
    content_hash: str
    artifact_type: str
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        _require_text(self.artifact_id, "artifact_id")
        _require_text(self.uri, "uri")
        _require_text(self.content_hash, "content_hash")
        _require_text(self.artifact_type, "artifact_type")
        _require_schema(self.schema_version, "ArtifactReference")

    def to_dict(self) -> dict[str, str]:
        return {
            "artifact_id": self.artifact_id,
            "uri": self.uri,
            "content_hash": self.content_hash,
            "artifact_type": self.artifact_type,
            "schema_version": self.schema_version,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ArtifactReference":
        return cls(
            artifact_id=str(data["artifact_id"]),
            uri=str(data["uri"]),
            content_hash=str(data["content_hash"]),
            artifact_type=str(data["artifact_type"]),
            schema_version=str(data.get("schema_version", "")),
        )


@dataclass(frozen=True)
class ExperimentManifest:
    """Reproducibility identity for one experiment."""

    experiment_id: str
    sensor_id: str
    sensor_version: str
    parameters: Mapping[str, ParameterValue]
    parameter_fingerprint: str
    code_revision: str
    data_fingerprint: str
    environment_fingerprint: str
    artifact_refs: tuple[ArtifactReference, ...] = ()
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        for field_name in (
            "experiment_id",
            "sensor_id",
            "sensor_version",
            "parameter_fingerprint",
            "code_revision",
            "data_fingerprint",
            "environment_fingerprint",
        ):
            _require_text(getattr(self, field_name), field_name)
        _require_schema(self.schema_version, "ExperimentManifest")

        parameters = _freeze_typed_mapping(
            self.parameters,
            field_name="parameters",
            allowed_types=(str, int, float, bool),
        )
        artifact_refs = tuple(self.artifact_refs)
        if any(not isinstance(ref, ArtifactReference) for ref in artifact_refs):
            raise TypeError("artifact_refs 只允许 ArtifactReference")

        object.__setattr__(self, "parameters", parameters)
        object.__setattr__(self, "artifact_refs", artifact_refs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "sensor_id": self.sensor_id,
            "sensor_version": self.sensor_version,
            "parameters": _thaw_mapping(self.parameters),
            "parameter_fingerprint": self.parameter_fingerprint,
            "code_revision": self.code_revision,
            "data_fingerprint": self.data_fingerprint,
            "environment_fingerprint": self.environment_fingerprint,
            "artifact_refs": [ref.to_dict() for ref in self.artifact_refs],
            "schema_version": self.schema_version,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ExperimentManifest":
        raw_refs = data.get("artifact_refs", ())
        if not isinstance(raw_refs, (list, tuple)):
            raise TypeError("artifact_refs 必须是 list 或 tuple")
        return cls(
            experiment_id=str(data["experiment_id"]),
            sensor_id=str(data["sensor_id"]),
            sensor_version=str(data["sensor_version"]),
            parameters=data.get("parameters", {}),
            parameter_fingerprint=str(data["parameter_fingerprint"]),
            code_revision=str(data["code_revision"]),
            data_fingerprint=str(data["data_fingerprint"]),
            environment_fingerprint=str(data["environment_fingerprint"]),
            artifact_refs=tuple(
                ArtifactReference.from_dict(ref)
                for ref in raw_refs
            ),
            schema_version=str(data.get("schema_version", "")),
        )


@dataclass(frozen=True)
class EvidenceRecord:
    """Auditable conclusion referencing persisted experiment artifacts."""

    evidence_id: str
    experiment_id: str
    subject_kind: str
    subject_id: str
    subject_version: str
    hypothesis: str
    decision: str
    feature_artifact_uri: str
    artifact_hash: str
    created_at: datetime
    observation: Mapping[str, ObservationValue] = field(default_factory=dict)
    outcome: Mapping[str, ObservationValue] = field(default_factory=dict)
    window: Mapping[str, WindowValue] = field(default_factory=dict)
    metrics: Mapping[str, float] = field(default_factory=dict)
    data_protocol_version: str = ""
    metadata: Mapping[str, str] = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        for field_name in (
            "evidence_id",
            "experiment_id",
            "subject_id",
            "subject_version",
            "hypothesis",
            "feature_artifact_uri",
            "artifact_hash",
        ):
            _require_text(getattr(self, field_name), field_name)
        if self.subject_kind not in SUBJECT_KINDS:
            raise ValueError(
                "subject_kind 必须是 feature_sensor、opportunity 或 detector"
            )
        if self.decision not in EVIDENCE_DECISIONS:
            raise ValueError("decision 必须是 KEEP、REVERT 或 HOLD")
        if self.created_at.tzinfo is None:
            raise ValueError("created_at 必须包含时区")
        _require_schema(self.schema_version, "EvidenceRecord")

        object.__setattr__(
            self,
            "observation",
            _freeze_typed_mapping(
                self.observation,
                field_name="observation",
                allowed_types=(float, str),
            ),
        )
        object.__setattr__(
            self,
            "outcome",
            _freeze_typed_mapping(
                self.outcome,
                field_name="outcome",
                allowed_types=(float, str),
            ),
        )
        object.__setattr__(
            self,
            "window",
            _freeze_typed_mapping(
                self.window,
                field_name="window",
                allowed_types=(int, str),
            ),
        )
        object.__setattr__(
            self,
            "metrics",
            _freeze_float_mapping(
                self.metrics,
                field_name="metrics",
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            _freeze_typed_mapping(
                self.metadata,
                field_name="metadata",
                allowed_types=(str,),
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "experiment_id": self.experiment_id,
            "subject_kind": self.subject_kind,
            "subject_id": self.subject_id,
            "subject_version": self.subject_version,
            "hypothesis": self.hypothesis,
            "decision": self.decision,
            "feature_artifact_uri": self.feature_artifact_uri,
            "artifact_hash": self.artifact_hash,
            "created_at": self.created_at.isoformat(),
            "observation": _thaw_mapping(self.observation),
            "outcome": _thaw_mapping(self.outcome),
            "window": _thaw_mapping(self.window),
            "metrics": _thaw_mapping(self.metrics),
            "data_protocol_version": self.data_protocol_version,
            "metadata": _thaw_mapping(self.metadata),
            "schema_version": self.schema_version,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "EvidenceRecord":
        return cls(
            evidence_id=str(data["evidence_id"]),
            experiment_id=str(data["experiment_id"]),
            subject_kind=str(data["subject_kind"]),
            subject_id=str(data["subject_id"]),
            subject_version=str(data["subject_version"]),
            hypothesis=str(data["hypothesis"]),
            decision=str(data["decision"]),
            feature_artifact_uri=str(data["feature_artifact_uri"]),
            artifact_hash=str(data["artifact_hash"]),
            created_at=datetime.fromisoformat(str(data["created_at"])),
            observation=data.get("observation", {}),
            outcome=data.get("outcome", {}),
            window=data.get("window", {}),
            metrics=data.get("metrics", {}),
            data_protocol_version=str(data.get("data_protocol_version", "")),
            metadata=data.get("metadata", {}),
            schema_version=str(data.get("schema_version", "")),
        )
