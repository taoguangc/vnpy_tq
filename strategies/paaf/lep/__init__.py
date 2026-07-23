"""LEP-CID_002-v0.1 — Live Enforcement Package（research · fail-closed）.

≠ go-live auth · ≠ Production Bindable · ≠ Alpha.
"""
from __future__ import annotations

from strategies.paaf.lep.check_live_acl import AclEdge, check_call_edge, denied_edges
from strategies.paaf.lep.check_vmp_live import VmpLiveCheck, validate_vmp_live_checklist
from strategies.paaf.lep.constants import (
    BACKTEST_FILL_BINDING,
    CONTRACT_ID,
    CXSD_CONTRACT_ID,
    LRC_CONTRACT_ID,
    VBP_PROTOCOL_ID,
    VMP_LIVE_CHECKLIST_ID,
)
from strategies.paaf.lep.gate_live import LiveGateResult, gate_live
from strategies.paaf.lep.validate_vbp_pack import VbpCheck, validate_vbp_pack

__all__ = [
    "CONTRACT_ID",
    "CXSD_CONTRACT_ID",
    "LRC_CONTRACT_ID",
    "VBP_PROTOCOL_ID",
    "VMP_LIVE_CHECKLIST_ID",
    "BACKTEST_FILL_BINDING",
    "AclEdge",
    "LiveGateResult",
    "VbpCheck",
    "VmpLiveCheck",
    "check_call_edge",
    "denied_edges",
    "gate_live",
    "validate_vbp_pack",
    "validate_vmp_live_checklist",
]
