"""Runtime audit schema — Design §2.6 lineage fields."""
from __future__ import annotations

from typing import Any

from strategies.paaf.cxsd.constants import (
    AUDIT_REQUIRED_FIELDS,
    CONTRACT_ID,
    PERMISSIONS,
    SURFACE_IDS,
)


def build_audit_event(
    *,
    experiment_id: str,
    surface_id: str,
    context_state: str,
    permission: str,
    event: str,
    detector_binding: str,
    freeze_id: str,
    context_version: str = "A1-CTX-PS-v1.0.0",
    context_engine_id: str = "paaf.context_published_state",
    cxsd_version: str = CONTRACT_ID,
    signal_reason: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "experiment_id": experiment_id,
        "surface_id": str(surface_id).upper(),
        "cxsd_version": cxsd_version,
        "context_version": context_version,
        "context_engine_id": context_engine_id,
        "context_state": context_state,
        "permission": str(permission).upper(),
        "detector_binding": detector_binding,
        "freeze_id": freeze_id,
        "event": event,
    }
    if signal_reason is not None:
        row["signal_reason"] = signal_reason
    if extra:
        row.update(extra)
    return row


def validate_audit_event(event: dict[str, Any]) -> list[str]:
    """Return list of defect codes；empty means schema-ok."""
    defects: list[str] = []
    for field in AUDIT_REQUIRED_FIELDS:
        if field not in event or event[field] in (None, ""):
            defects.append(f"missing:{field}")
    perm = str(event.get("permission", "")).upper()
    if perm and perm not in PERMISSIONS:
        defects.append("invalid_permission")
    surface = str(event.get("surface_id", "")).upper()
    if surface and surface not in SURFACE_IDS:
        defects.append("invalid_surface")
    if str(event.get("cxsd_version", "")) != CONTRACT_ID:
        defects.append("cxsd_version_mismatch")
    return defects


def audit_lineage_complete(event: dict[str, Any]) -> bool:
    return not validate_audit_event(event)
