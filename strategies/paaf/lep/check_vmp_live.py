"""Validate VMP live-ops checklist completeness."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from strategies.paaf.lep.constants import (
    CXSD_CONTRACT_ID,
    LRC_CONTRACT_ID,
    VMP_LIVE_CHECKLIST_ID,
    VMP_LIVE_REQUIRED_FIELDS,
)


@dataclass(frozen=True)
class VmpLiveCheck:
    ok: bool
    reason: str
    missing: tuple[str, ...]


def validate_vmp_live_checklist(checklist: dict[str, Any] | None) -> VmpLiveCheck:
    if not isinstance(checklist, dict):
        return VmpLiveCheck(False, "checklist_missing", tuple(VMP_LIVE_REQUIRED_FIELDS))

    checklist_id = str(checklist.get("checklist_id") or "").strip()
    if checklist_id and checklist_id != VMP_LIVE_CHECKLIST_ID:
        return VmpLiveCheck(False, "checklist_id_mismatch", ())

    missing = []
    for field in VMP_LIVE_REQUIRED_FIELDS:
        value = checklist.get(field)
        if value is None or value == "" or value == []:
            missing.append(field)
    if missing:
        return VmpLiveCheck(False, "incomplete_checklist", tuple(missing))

    if str(checklist.get("lrc_contract_id") or "").strip() != LRC_CONTRACT_ID:
        return VmpLiveCheck(False, "lrc_contract_id_mismatch", ())
    if str(checklist.get("cxsd_contract_id") or "").strip() != CXSD_CONTRACT_ID:
        return VmpLiveCheck(False, "cxsd_contract_id_mismatch", ())

    return VmpLiveCheck(True, "checklist_ok", ())
