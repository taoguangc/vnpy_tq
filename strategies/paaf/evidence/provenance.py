"""Provenance helpers: fingerprints and observation-key assembly."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

from strategies.paaf.evidence.hashing import hash_canonical_json
from strategies.paaf.evidence.models import EvidenceRecord, ExperimentManifest


def fingerprint_parameters(
    parameters: Mapping[str, str | int | float | bool],
) -> str:
    """Fingerprint a flat parameter set; key order does not matter."""

    if not isinstance(parameters, Mapping):
        raise TypeError("parameters 必须是 Mapping")
    for key, value in parameters.items():
        if not isinstance(key, str):
            raise TypeError("parameters 的键必须是 str")
        if isinstance(value, bool):
            continue
        if isinstance(value, (str, int, float)):
            continue
        raise TypeError("parameters 的值只允许 str、int、float、bool")
    return hash_canonical_json(dict(parameters))


def fingerprint_manifest(manifest: ExperimentManifest) -> str:
    """Fingerprint experiment identity + sealed artifact refs.

    Uses canonical JSON. Does not include runtime clocks (Manifest has none).
    ``artifact_refs`` are sorted by ``artifact_id`` so insertion order is stable.
    """

    payload: dict[str, Any] = {
        "experiment_id": manifest.experiment_id,
        "sensor_id": manifest.sensor_id,
        "sensor_version": manifest.sensor_version,
        "parameters": dict(manifest.parameters),
        "parameter_fingerprint": manifest.parameter_fingerprint,
        "code_revision": manifest.code_revision,
        "data_fingerprint": manifest.data_fingerprint,
        "environment_fingerprint": manifest.environment_fingerprint,
        "schema_version": manifest.schema_version,
        "artifact_refs": [
            ref.to_dict()
            for ref in sorted(
                manifest.artifact_refs,
                key=lambda item: item.artifact_id,
            )
        ],
    }
    return hash_canonical_json(payload)


def verify_parameter_fingerprint(manifest: ExperimentManifest) -> None:
    """Raise if ``parameter_fingerprint`` does not match ``parameters``."""

    expected = fingerprint_parameters(manifest.parameters)
    if manifest.parameter_fingerprint != expected:
        raise ValueError(
            "parameter_fingerprint 与 parameters 不一致"
        )


def fingerprint_evidence_body(record: EvidenceRecord) -> str:
    """Fingerprint EvidenceRecord without ``created_at`` (audit clock only)."""

    payload = record.to_dict()
    payload.pop("created_at", None)
    return hash_canonical_json(payload)


def build_observation_key(
    *,
    sensor_id: str,
    sensor_version: str,
    parameter_fingerprint: str,
    symbol: str,
    timeframe: str,
    timestamp: datetime,
) -> str:
    """Build Observation Key string for audit (not stored on FeatureResult)."""

    if timestamp.tzinfo is None:
        raise ValueError("timestamp 必须包含时区")
    parts = (
        sensor_id.strip(),
        sensor_version.strip(),
        parameter_fingerprint.strip(),
        symbol.strip(),
        timeframe.strip(),
        timestamp.isoformat(),
    )
    if any(not part for part in parts):
        raise ValueError("Observation Key 字段不能为空")
    return "|".join(parts)
