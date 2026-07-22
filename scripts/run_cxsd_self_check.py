"""CXSD implementation self-check — compliance evidence only（no backtest）."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from strategies.paaf.cxsd import (
    CONTRACT_ID,
    build_audit_event,
    default_evidence_dir,
    detect_violations,
    export_compliance_bundle,
    failure_policy_blocks,
    may_emit_permission,
    may_read_context_state,
    resolve_permission,
    validate_intent,
)


def main() -> int:
    probe_hits = []
    for intent in ("buy", "modify_signal", "set_size"):
        for v in detect_violations(intent=intent):
            probe_hits.append({"code": v.code, "detail": v.detail, "kind": "intent_probe"})
    for v in detect_violations(
        context_state="invalid",
        permission="ALLOW",
        order_submitted=True,
    ):
        probe_hits.append({"code": v.code, "detail": v.detail, "kind": "fail_open_probe"})

    g_invalid = resolve_permission(
        consumer_id="CI_FILTER_ADAPTER",
        context_state="invalid",
        filter_would_allow=True,
    )
    g_block = resolve_permission(
        consumer_id="CI_FILTER_ADAPTER",
        context_state="compression",
        filter_would_allow=False,
    )
    g_allow = resolve_permission(
        consumer_id="CI_FILTER_ADAPTER",
        context_state="expansion",
        filter_would_allow=True,
    )

    checks = {
        "contract_cited": CONTRACT_ID == "CXSD-CID_002-v0.1",
        "get_state_ok": validate_intent("get_state").ok,
        "decide_ok": validate_intent("decide").ok,
        "buy_forbidden": not validate_intent("buy").ok,
        "detector_cannot_read": not may_read_context_state("CI_DETECTOR").ok,
        "filter_can_decide": may_emit_permission("CI_FILTER_ADAPTER").ok,
        "invalid_fail_closed": failure_policy_blocks("invalid"),
        "invalid_blocks_order": g_invalid.order_allowed is False,
        "compression_filter_block": g_block.permission == "BLOCK",
        "expansion_filter_allow": g_allow.permission == "ALLOW" and g_allow.order_allowed,
        "fail_open_probe_detected": any(x["kind"] == "fail_open_probe" for x in probe_hits),
        "forbidden_intent_probes": sum(1 for x in probe_hits if x["kind"] == "intent_probe"),
    }
    checks["failure_safety_pass"] = (
        checks["invalid_blocks_order"] and checks["fail_open_probe_detected"]
    )

    events = [
        build_audit_event(
            experiment_id="CXSD_CID_002_IMPL_001",
            surface_id="MECH",
            context_state="compression",
            permission=g_block.permission,
            event="PERMISSION_DENIAL",
            detector_binding="BROOKS_SCALP_FP@0.1.0",
            freeze_id="SIF_CID_002_V0_1_1",
        ),
        build_audit_event(
            experiment_id="CXSD_CID_002_IMPL_001",
            surface_id="MECH",
            context_state="expansion",
            permission=g_allow.permission,
            event="PERMISSION_ALLOW",
            detector_binding="BROOKS_SCALP_FP@0.1.0",
            freeze_id="SIF_CID_002_V0_1_1",
        ),
    ]

    meta = export_compliance_bundle(
        default_evidence_dir(ROOT),
        audit_events=events,
        violations=[],
        self_checks=checks,
    )
    print(
        {
            "contract_id": CONTRACT_ID,
            "compliant_claim_allowed": meta.get("compliant_claim_allowed"),
            "evaluation": meta.get("evaluation"),
        }
    )
    return 0 if meta.get("compliant_claim_allowed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
