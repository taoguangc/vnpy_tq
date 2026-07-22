"""Failure-safe permission gate（CXSD Articles 2 + 5）."""
from __future__ import annotations

from dataclasses import dataclass

from strategies.paaf.cxsd.check_acl import may_emit_permission, may_read_context_state
from strategies.paaf.cxsd.constants import FAIL_CLOSED_STATES, PERMISSIONS
from strategies.paaf.cxsd.validate_interface import validate_intent


@dataclass(frozen=True)
class GateResult:
    permission: str
    ok: bool
    reason: str
    order_allowed: bool


def normalize_context_state(state: str | None) -> str:
    return str(state or "").strip().lower()


def failure_policy_blocks(context_state: str) -> bool:
    state = normalize_context_state(context_state)
    if state in FAIL_CLOSED_STATES:
        return True
    # unknown tags → BLOCK（Art 2.4 / Design §2.5）
    if state not in {"expansion", "compression"}:
        return True
    return False


def resolve_permission(
    *,
    consumer_id: str,
    context_state: str,
    filter_would_allow: bool,
    monitor_only: bool = False,
) -> GateResult:
    """Resolve ALLOW/BLOCK/MONITOR with fail-closed trading path.

    ``filter_would_allow`` is supplied by the strategy Filter rule（e.g. F1）.
    CXSD does not invent Alpha scores；it only applies safety policy.
    """
    read = may_read_context_state(consumer_id)
    if monitor_only:
        if not read.ok:
            return GateResult("BLOCK", False, f"monitor_read_denied:{read.reason}", False)
        return GateResult("MONITOR", True, "monitor_only", False)

    decide = may_emit_permission(consumer_id)
    if not decide.ok:
        return GateResult("BLOCK", False, f"decide_denied:{decide.reason}", False)

    if failure_policy_blocks(context_state):
        return GateResult(
            "BLOCK",
            True,
            f"fail_closed:{normalize_context_state(context_state)}",
            False,
        )

    if filter_would_allow:
        return GateResult("ALLOW", True, "filter_allow", True)
    return GateResult("BLOCK", True, "filter_block", False)


def sanitize_permission(permission: str) -> str:
    p = str(permission or "").strip().upper()
    if p not in PERMISSIONS:
        return "BLOCK"
    return p


def check_get_state_intent() -> bool:
    return validate_intent("get_state").ok


def check_decide_intent() -> bool:
    return validate_intent("decide").ok
