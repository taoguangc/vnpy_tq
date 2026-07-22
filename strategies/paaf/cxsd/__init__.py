"""CXSD-CID_002-v0.1 conformance toolkit（research · not Alpha）."""
from __future__ import annotations

from strategies.paaf.cxsd.audit_schema import (
    audit_lineage_complete,
    build_audit_event,
    validate_audit_event,
)
from strategies.paaf.cxsd.check_acl import (
    may_cite_surface,
    may_emit_permission,
    may_read_context_state,
)
from strategies.paaf.cxsd.constants import CONTRACT_ID, DESIGN_ID
from strategies.paaf.cxsd.detect_violations import Violation, detect_violations
from strategies.paaf.cxsd.export_evidence import (
    default_evidence_dir,
    export_compliance_bundle,
)
from strategies.paaf.cxsd.gate import GateResult, failure_policy_blocks, resolve_permission
from strategies.paaf.cxsd.validate_interface import IntentCheck, validate_intent

__all__ = [
    "CONTRACT_ID",
    "DESIGN_ID",
    "GateResult",
    "IntentCheck",
    "Violation",
    "audit_lineage_complete",
    "build_audit_event",
    "default_evidence_dir",
    "detect_violations",
    "export_compliance_bundle",
    "failure_policy_blocks",
    "may_cite_surface",
    "may_emit_permission",
    "may_read_context_state",
    "resolve_permission",
    "validate_audit_event",
    "validate_intent",
]
