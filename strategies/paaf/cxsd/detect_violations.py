"""Violation detector — forbidden actions + fail-open trading path."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from strategies.paaf.cxsd.constants import FAIL_CLOSED_STATES, FORBIDDEN_INTENTS
from strategies.paaf.cxsd.validate_interface import normalize_intent


@dataclass(frozen=True)
class Violation:
    code: str
    detail: str


def detect_forbidden_intent(intent: str) -> Violation | None:
    name = normalize_intent(intent)
    if name in FORBIDDEN_INTENTS:
        return Violation("F_FORBIDDEN_INTENT", name)
    return None


def detect_fail_open_trade(
    *,
    context_state: str,
    permission: str,
    order_submitted: bool,
) -> Violation | None:
    """Trading path must fail closed on bad Context / BLOCK / MONITOR."""
    if not order_submitted:
        return None
    state = str(context_state or "").strip().lower()
    perm = str(permission or "").strip().upper()
    if state in FAIL_CLOSED_STATES or state not in {"expansion", "compression"}:
        return Violation("F_FAIL_OPEN", f"order_under_state={state}")
    if perm == "BLOCK":
        return Violation("F_FAIL_OPEN", "order_under_BLOCK")
    if perm == "MONITOR":
        return Violation("F_MONITOR_TRADE", "MONITOR_must_not_submit")
    return None


def detect_context_wrote_signal(flags: dict[str, Any]) -> Violation | None:
    if flags.get("context_generated_detection_result"):
        return Violation("F1_SIGNAL", "context_generated_detection_result")
    if flags.get("context_called_buy_sell"):
        return Violation("F2_ORDER", "context_called_buy_sell")
    if flags.get("context_modified_levels"):
        return Violation("F3_LEVELS", "context_modified_entry_stop_target")
    if flags.get("context_modified_size"):
        return Violation("F4_SIZE", "context_modified_sizing")
    if flags.get("context_alpha_score"):
        return Violation("F5_ALPHA", "context_invented_alpha_score")
    if flags.get("mutated_g5_bytes"):
        return Violation("F6_G5", "mutated_g5_binding_bytes")
    if flags.get("reopened_rc001_b"):
        return Violation("F7_RC001B", "reopened_or_reused_closed_id")
    if flags.get("collapsed_pnl_claim"):
        return Violation("F8_COLLAPSE", "unlabeled_merged_pnl_claim")
    return None


def detect_violations(
    *,
    intent: str | None = None,
    context_state: str = "",
    permission: str = "",
    order_submitted: bool = False,
    flags: dict[str, Any] | None = None,
) -> list[Violation]:
    found: list[Violation] = []
    if intent is not None:
        v = detect_forbidden_intent(intent)
        if v:
            found.append(v)
    v2 = detect_fail_open_trade(
        context_state=context_state,
        permission=permission,
        order_submitted=order_submitted,
    )
    if v2:
        found.append(v2)
    v3 = detect_context_wrote_signal(flags or {})
    if v3:
        found.append(v3)
    return found
