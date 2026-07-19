"""Controlled Experiment → Manifest → Evidence workflow for PAAF Phase 1."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Mapping

from strategies.paaf.evidence.models import (
    SUBJECT_KINDS,
    ArtifactReference,
    EvidenceRecord,
    ExperimentManifest,
    ObservationValue,
    ParameterValue,
    WindowValue,
)
from strategies.paaf.evidence.provenance import (
    fingerprint_parameters,
    verify_parameter_fingerprint,
)
from strategies.paaf.evidence.repository import EvidenceRepository


def _require_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} 不能为空")


def _freeze_parameters(
    parameters: Mapping[str, ParameterValue],
) -> Mapping[str, ParameterValue]:
    fingerprint_parameters(parameters)
    return MappingProxyType(dict(parameters))


def _freeze_labels(labels: Mapping[str, str]) -> Mapping[str, str]:
    if not isinstance(labels, Mapping):
        raise TypeError("labels 必须是 Mapping")
    copied: dict[str, str] = {}
    for key, value in labels.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise TypeError("labels 的键和值必须是 str")
        copied[key] = value
    return MappingProxyType(copied)


@dataclass(frozen=True)
class ExperimentContext:
    """Declared experiment inputs; contains no Feature values or conclusions."""

    experiment_id: str
    sensor_id: str
    sensor_version: str
    parameters: Mapping[str, ParameterValue]
    hypothesis: str
    code_revision: str
    data_fingerprint: str
    environment_fingerprint: str
    subject_kind: str = "feature_sensor"
    data_protocol_version: str = ""

    def __post_init__(self) -> None:
        for field_name in (
            "experiment_id",
            "sensor_id",
            "sensor_version",
            "hypothesis",
            "code_revision",
            "data_fingerprint",
            "environment_fingerprint",
        ):
            _require_text(getattr(self, field_name), field_name)
        if self.subject_kind not in SUBJECT_KINDS:
            raise ValueError(
                "subject_kind 必须是 feature_sensor、opportunity 或 detector"
            )
        object.__setattr__(
            self,
            "parameters",
            _freeze_parameters(self.parameters),
        )


@dataclass(frozen=True)
class RunContext:
    """Caller-owned execution identity and audit clock."""

    experiment_id: str
    created_at: datetime
    run_id: str | None = None
    labels: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_text(self.experiment_id, "experiment_id")
        if self.created_at.tzinfo is None:
            raise ValueError("created_at 必须包含时区")
        if self.run_id is not None:
            _require_text(self.run_id, "run_id")
        object.__setattr__(self, "labels", _freeze_labels(self.labels))


def register_artifact_reference(
    *,
    artifact_id: str,
    uri: str,
    content_hash: str,
    artifact_type: str,
) -> ArtifactReference:
    """Construct a caller-owned reference; does not read or copy artifact data."""

    return ArtifactReference(
        artifact_id=artifact_id,
        uri=uri,
        content_hash=content_hash,
        artifact_type=artifact_type,
    )


class ExperimentWorkflow:
    """Minimal orchestration over provenance models and EvidenceRepository."""

    def __init__(self, repository: EvidenceRepository) -> None:
        self.repository = repository

    def build_manifest(
        self,
        context: ExperimentContext,
        artifact_refs: tuple[ArtifactReference, ...] = (),
    ) -> ExperimentManifest:
        return ExperimentManifest(
            experiment_id=context.experiment_id,
            sensor_id=context.sensor_id,
            sensor_version=context.sensor_version,
            parameters=context.parameters,
            parameter_fingerprint=fingerprint_parameters(context.parameters),
            code_revision=context.code_revision,
            data_fingerprint=context.data_fingerprint,
            environment_fingerprint=context.environment_fingerprint,
            artifact_refs=artifact_refs,
        )

    def persist_manifest(self, manifest: ExperimentManifest) -> None:
        verify_parameter_fingerprint(manifest)
        self.repository.save_manifest(manifest)

    def build_evidence(
        self,
        context: ExperimentContext,
        *,
        run_context: RunContext,
        evidence_id: str,
        decision: str,
        feature_artifact_uri: str,
        artifact_hash: str,
        observation: Mapping[str, ObservationValue] | None = None,
        outcome: Mapping[str, ObservationValue] | None = None,
        window: Mapping[str, WindowValue] | None = None,
        metrics: Mapping[str, float] | None = None,
        metadata: Mapping[str, str] | None = None,
    ) -> EvidenceRecord:
        manifest = self._load_matching_manifest(context)
        if run_context.experiment_id != context.experiment_id:
            raise ValueError(
                "RunContext.experiment_id 必须等于 ExperimentContext.experiment_id"
            )
        if not any(
            ref.uri == feature_artifact_uri
            and ref.content_hash == artifact_hash
            for ref in manifest.artifact_refs
        ):
            raise ValueError("Evidence artifact 未在 Manifest.artifact_refs 中登记")

        return EvidenceRecord(
            evidence_id=evidence_id,
            experiment_id=context.experiment_id,
            subject_kind=context.subject_kind,
            subject_id=context.sensor_id,
            subject_version=context.sensor_version,
            hypothesis=context.hypothesis,
            decision=decision,
            feature_artifact_uri=feature_artifact_uri,
            artifact_hash=artifact_hash,
            created_at=run_context.created_at,
            observation=observation or {},
            outcome=outcome or {},
            window=window or {},
            metrics=metrics or {},
            data_protocol_version=context.data_protocol_version,
            metadata=metadata or {},
        )

    def persist_evidence(self, evidence: EvidenceRecord) -> None:
        manifest = self.repository.load_manifest(evidence.experiment_id)
        verify_parameter_fingerprint(manifest)
        self._verify_replay_links(manifest, evidence)
        self.repository.save_evidence(evidence)

    def replay(
        self,
        experiment_id: str,
        evidence_id: str,
    ) -> tuple[ExperimentManifest, EvidenceRecord]:
        manifest = self.repository.load_manifest(experiment_id)
        evidence = self.repository.load_evidence(experiment_id, evidence_id)
        verify_parameter_fingerprint(manifest)
        self._verify_replay_links(manifest, evidence)
        return manifest, evidence

    def _load_matching_manifest(
        self,
        context: ExperimentContext,
    ) -> ExperimentManifest:
        manifest = self.repository.load_manifest(context.experiment_id)
        verify_parameter_fingerprint(manifest)
        if (
            manifest.sensor_id != context.sensor_id
            or manifest.sensor_version != context.sensor_version
            or dict(manifest.parameters) != dict(context.parameters)
            or manifest.code_revision != context.code_revision
            or manifest.data_fingerprint != context.data_fingerprint
            or manifest.environment_fingerprint
            != context.environment_fingerprint
        ):
            raise ValueError("ExperimentContext 与已持久化 Manifest 不一致")
        return manifest

    @staticmethod
    def _verify_replay_links(
        manifest: ExperimentManifest,
        evidence: EvidenceRecord,
    ) -> None:
        if evidence.experiment_id != manifest.experiment_id:
            raise ValueError("Evidence.experiment_id 与 Manifest 不一致")
        if (
            evidence.subject_id != manifest.sensor_id
            or evidence.subject_version != manifest.sensor_version
        ):
            raise ValueError("Evidence subject 与 Manifest sensor 不一致")
        if not any(
            ref.uri == evidence.feature_artifact_uri
            and ref.content_hash == evidence.artifact_hash
            for ref in manifest.artifact_refs
        ):
            raise ValueError("Evidence artifact 与 Manifest.artifact_refs 不一致")
