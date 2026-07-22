"""Evidence writers with C-LINEAGE fields."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _lineage(
    *,
    manifest_id: str,
    runtime_hash: str,
    dataset_fingerprint: dict[str, Any],
    schema_version: str,
) -> dict[str, Any]:
    return {
        "manifest_id": manifest_id,
        "runtime_hash": runtime_hash,
        "dataset_fingerprint": dataset_fingerprint,
        "schema_version": schema_version,
        "execution_timestamp": datetime.now(timezone.utc).isoformat(),
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def attach_lineage(payload: dict[str, Any], lineage: dict[str, Any]) -> dict[str, Any]:
    out = dict(payload)
    out["lineage"] = lineage
    return out


def make_lineage(
    *,
    manifest_id: str,
    runtime_hash: str,
    dataset_fingerprint: dict[str, Any],
    schema_version: str,
) -> dict[str, Any]:
    return _lineage(
        manifest_id=manifest_id,
        runtime_hash=runtime_hash,
        dataset_fingerprint=dataset_fingerprint,
        schema_version=schema_version,
    )
