"""Aggregate fail-closed live gate."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from strategies.paaf.lep.check_live_acl import AclEdge, check_call_edge
from strategies.paaf.lep.check_vmp_live import VmpLiveCheck, validate_vmp_live_checklist
from strategies.paaf.lep.constants import CONTRACT_ID, CXSD_CONTRACT_ID, LRC_CONTRACT_ID
from strategies.paaf.lep.validate_vbp_pack import VbpCheck, validate_vbp_pack


@dataclass(frozen=True)
class LiveGateResult:
    ok: bool
    reason: str
    lep_contract_id: str = CONTRACT_ID
    vbp: VbpCheck | None = None
    vmp: VmpLiveCheck | None = None
    acl_failures: tuple[AclEdge, ...] = field(default_factory=tuple)
    production_bindable: bool = False
    live_authorized: bool = False


def gate_live(
    *,
    vbp_pack: dict[str, Any] | None,
    vmp_checklist: dict[str, Any] | None,
    claimed_call_edges: list[tuple[str, str]] | None = None,
    cxsd_contract_id: str = CXSD_CONTRACT_ID,
    lrc_contract_id: str = LRC_CONTRACT_ID,
    claim_live: bool = True,
) -> LiveGateResult:
    """Fail closed for a live/sim readiness petition.

    Passing this gate does NOT grant Production Bindable or live auth.
    """
    if str(cxsd_contract_id or "").strip() != CXSD_CONTRACT_ID:
        return LiveGateResult(False, "cxsd_contract_id_mismatch")
    if str(lrc_contract_id or "").strip() != LRC_CONTRACT_ID:
        return LiveGateResult(False, "lrc_contract_id_mismatch")

    vbp = validate_vbp_pack(vbp_pack, require_filled=claim_live)
    if not vbp.ok:
        return LiveGateResult(False, f"vbp:{vbp.reason}", vbp=vbp)

    vmp = validate_vmp_live_checklist(vmp_checklist)
    if not vmp.ok:
        return LiveGateResult(False, f"vmp:{vmp.reason}", vbp=vbp, vmp=vmp)

    failures: list[AclEdge] = []
    for caller, callee in claimed_call_edges or ():
        edge = check_call_edge(caller, callee)
        if not edge.ok:
            failures.append(edge)
    if failures:
        return LiveGateResult(
            False,
            "acl_hard_deny",
            vbp=vbp,
            vmp=vmp,
            acl_failures=tuple(failures),
        )

    return LiveGateResult(
        True,
        "lep_preconditions_ok_not_go_live",
        vbp=vbp,
        vmp=vmp,
        production_bindable=False,
        live_authorized=False,
    )
