"""Evidence exporter for CXSD compliance bundles."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from strategies.paaf.cxsd.audit_schema import validate_audit_event
from strategies.paaf.cxsd.constants import CHARTER_ID, CONTRACT_ID, DESIGN_ID


def default_evidence_dir(root: Path, run_id: str = "CXSD_CID_002_IMPL_001") -> Path:
    return root / "research" / "output" / "evidence" / run_id


def export_compliance_bundle(
    out_dir: Path,
    *,
    audit_events: list[dict[str, Any]],
    violations: list[dict[str, Any]],
    self_checks: dict[str, Any],
    run_id: str = "CXSD_CID_002_IMPL_001",
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    audit_defects = [validate_audit_event(e) for e in audit_events]
    lineage_ok = all(len(d) == 0 for d in audit_defects) if audit_events else False
    no_violations = len(violations) == 0
    compliant = bool(self_checks.get("contract_cited")) and lineage_ok and no_violations

    meta = {
        "run_id": run_id,
        "status": "IMPLEMENTATION_SELF_CHECK",
        "contract_id": CONTRACT_ID,
        "design_id": DESIGN_ID,
        "charter_id": CHARTER_ID,
        "authorization": "Authorize CXSD Implementation",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "evaluation": {
            "contract_compliance": compliant,
            "auditability": lineage_ok,
            "failure_safety": bool(self_checks.get("failure_safety_pass")),
            "pnl_used": False,
        },
        "compliant_claim_allowed": compliant and bool(self_checks.get("failure_safety_pass")),
        "audit_event_count": len(audit_events),
        "violation_count": len(violations),
        "self_checks": self_checks,
        "alpha_claim": False,
        "production_bindable": False,
    }
    (out_dir / "run_metadata.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out_dir / "audit_events.json").write_text(
        json.dumps(audit_events, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out_dir / "violations.json").write_text(
        json.dumps(violations, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out_dir / "audit_defects.json").write_text(
        json.dumps(audit_defects, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return meta
