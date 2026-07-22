"""Interface validator — allowed API intents only."""
from __future__ import annotations

from dataclasses import dataclass

from strategies.paaf.cxsd.constants import ALLOWED_INTENTS, FORBIDDEN_INTENTS


@dataclass(frozen=True)
class IntentCheck:
    intent: str
    ok: bool
    reason: str


def normalize_intent(intent: str) -> str:
    return str(intent or "").strip()


def validate_intent(intent: str) -> IntentCheck:
    """Return whether ``intent`` is an allowed CXSD v0.1 API intent."""
    name = normalize_intent(intent)
    if not name:
        return IntentCheck(intent=name, ok=False, reason="empty_intent")
    if name in FORBIDDEN_INTENTS:
        return IntentCheck(intent=name, ok=False, reason="forbidden_intent")
    if name in ALLOWED_INTENTS:
        return IntentCheck(intent=name, ok=True, reason="allowed")
    return IntentCheck(intent=name, ok=False, reason="unknown_intent")


def assert_intent_allowed(intent: str) -> None:
    check = validate_intent(intent)
    if not check.ok:
        raise PermissionError(f"CXSD intent rejected: {check.intent} ({check.reason})")
