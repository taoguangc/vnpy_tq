"""Export LEP compliance evidence bundles（research · not go-live）."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from strategies.paaf.lep.constants import CONTRACT_ID, CXSD_CONTRACT_ID, LRC_CONTRACT_ID
from strategies.paaf.lep.gate_live import LiveGateResult, gate_live


def default_evidence_dir(root: Path, run_id: str = "LEP_CID_002_BUNDLE_001") -> Path:
    return root / "research" / "output" / "evidence" / run_id


def export_lep_bundle(
    out_dir: Path,
    *,
    gate: LiveGateResult,
    vbp_pack: dict[str, Any] | None,
    vmp_checklist: dict[str, Any] | None,
    claimed_call_edges: list[tuple[str, str]] | None = None,
    run_id: str = "LEP_CID_002_BUNDLE_001",
    note: str = "",
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "run_id": run_id,
        "status": "LEP_COMPLIANCE_BUNDLE",
        "lep_contract_id": CONTRACT_ID,
        "lrc_contract_id": LRC_CONTRACT_ID,
        "cxsd_contract_id": CXSD_CONTRACT_ID,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "gate_ok": gate.ok,
        "gate_reason": gate.reason,
        "production_bindable": False,
        "live_authorized": False,
        "claimed_call_edges": [
            {"caller": c, "callee": a} for c, a in (claimed_call_edges or [])
        ],
        "vbp_kind": None if gate.vbp is None else gate.vbp.kind,
        "vbp_reason": None if gate.vbp is None else gate.vbp.reason,
        "vmp_reason": None if gate.vmp is None else gate.vmp.reason,
        "acl_failure_count": len(gate.acl_failures),
        "note": note,
        "alpha_claim": False,
    }
    (out_dir / "run_metadata.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out_dir / "vbp_pack.json").write_text(
        json.dumps(vbp_pack or {}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out_dir / "vmp_checklist.json").write_text(
        json.dumps(vmp_checklist or {}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out_dir / "gate_result.json").write_text(
        json.dumps(
            {
                "ok": gate.ok,
                "reason": gate.reason,
                "lep_contract_id": gate.lep_contract_id,
                "production_bindable": gate.production_bindable,
                "live_authorized": gate.live_authorized,
                "acl_failures": [
                    {"caller": e.caller, "callee": e.callee, "reason": e.reason}
                    for e in gate.acl_failures
                ],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return meta


def build_and_export(
    out_dir: Path,
    *,
    vbp_pack: dict[str, Any] | None,
    vmp_checklist: dict[str, Any] | None,
    claimed_call_edges: list[tuple[str, str]] | None = None,
    claim_live: bool = True,
    run_id: str = "LEP_CID_002_BUNDLE_001",
    note: str = "",
) -> dict[str, Any]:
    gate = gate_live(
        vbp_pack=vbp_pack,
        vmp_checklist=vmp_checklist,
        claimed_call_edges=claimed_call_edges,
        claim_live=claim_live,
    )
    return export_lep_bundle(
        out_dir,
        gate=gate,
        vbp_pack=vbp_pack,
        vmp_checklist=vmp_checklist,
        claimed_call_edges=claimed_call_edges,
        run_id=run_id,
        note=note,
    )
