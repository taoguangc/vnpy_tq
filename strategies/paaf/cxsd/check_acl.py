"""ACL checker — Consumer Identity read / decide rights."""
from __future__ import annotations

from dataclasses import dataclass

from strategies.paaf.cxsd.constants import (
    CONSUMERS_FORBIDDEN_READ,
    CONSUMERS_MAY_DECIDE,
    CONSUMERS_MAY_READ,
    SURFACE_IDS,
)


@dataclass(frozen=True)
class AclCheck:
    consumer_id: str
    action: str
    ok: bool
    reason: str


def may_read_context_state(consumer_id: str) -> AclCheck:
    cid = str(consumer_id or "").strip()
    if cid in CONSUMERS_MAY_READ:
        return AclCheck(cid, "read", True, "listed_reader")
    if cid in CONSUMERS_FORBIDDEN_READ:
        return AclCheck(cid, "read", False, "forbidden_reader")
    return AclCheck(cid, "read", False, "unknown_consumer")


def may_emit_permission(consumer_id: str) -> AclCheck:
    """Only Filter adapter may emit ALLOW/BLOCK on trading path."""
    cid = str(consumer_id or "").strip()
    if cid in CONSUMERS_MAY_DECIDE:
        return AclCheck(cid, "decide", True, "filter_adapter")
    if cid == "CI_MONITOR":
        return AclCheck(cid, "decide", False, "monitor_may_not_decide_trading")
    return AclCheck(cid, "decide", False, "not_decision_principal")


def may_cite_surface(surface_id: str) -> AclCheck:
    sid = str(surface_id or "").strip().upper()
    if sid in SURFACE_IDS:
        return AclCheck(sid, "surface", True, "cc_surface")
    return AclCheck(sid, "surface", False, "invalid_surface")
