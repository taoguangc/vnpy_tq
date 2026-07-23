"""Live ACL hard-deny matrix（from ACL_CID_002_V0_1）."""
from __future__ import annotations

from dataclasses import dataclass

# callee keys used by LEP
_DETECT = "Detector.detect"
_ENTRY = "Orch.submit_entry"
_RISK = "Risk.sizing_kill"
_ENGINE = "Engine.buy_sell"
_CTX = "Ctx.publish_tag"

# Hard DENY edges only（ALLOW/N/A omitted）
_DENIED: frozenset[tuple[str, str]] = frozenset(
    {
        ("P_ORCH_MECH", _RISK),
        ("P_ORCH_MECH", _CTX),
        ("P_ORCH_RISK", _CTX),
        ("P_CTX_FILTER", _DETECT),
        ("P_CTX_FILTER", _ENTRY),
        ("P_CTX_FILTER", _RISK),
        ("P_CTX_FILTER", _ENGINE),
        ("P_CTX_ENGINE", _DETECT),
        ("P_CTX_ENGINE", _ENTRY),
        ("P_CTX_ENGINE", _RISK),
        ("P_CTX_ENGINE", _ENGINE),
        ("P_DETECTOR", _ENTRY),
        ("P_DETECTOR", _RISK),
        ("P_DETECTOR", _ENGINE),
        ("P_DETECTOR", _CTX),
        ("P_ENGINE", _DETECT),
        ("P_ENGINE", _ENTRY),
        ("P_ENGINE", _RISK),
        ("P_ENGINE", _CTX),
    }
)


@dataclass(frozen=True)
class AclEdge:
    caller: str
    callee: str
    ok: bool
    reason: str


def check_call_edge(caller: str, callee: str) -> AclEdge:
    c = str(caller or "").strip()
    a = str(callee or "").strip()
    if (c, a) in _DENIED:
        return AclEdge(c, a, False, "acl_hard_deny")
    return AclEdge(c, a, True, "not_hard_deny")


def denied_edges() -> list[tuple[str, str]]:
    return sorted(_DENIED)
