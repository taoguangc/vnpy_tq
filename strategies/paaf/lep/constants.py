"""LEP constants — pin contract IDs."""
from __future__ import annotations

CONTRACT_ID = "LEP-CID_002-v0.1"
VBP_PROTOCOL_ID = "VBP-CID_002-v0.1"
LRC_CONTRACT_ID = "LRC-CID_002-v0.1"
CXSD_CONTRACT_ID = "CXSD-CID_002-v0.1"
VMP_LIVE_CHECKLIST_ID = "VMP_LIVE_CID_002_V0_1"
BACKTEST_FILL_BINDING = "VNPY_CTA_BACKTEST_ENGINE_DEFAULTS_AT_EXP_REGISTRATION"

VMP_LIVE_REQUIRED_FIELDS = (
    "session_calendar_ref",
    "restart_policy",
    "drift_detection",
    "failover_policy",
    "disconnect_policy",
    "identity_pin_ref",
    "lrc_contract_id",
    "vbp_pack_ref",
    "cxsd_contract_id",
    "declared_by",
    "declared_at",
)

VBP_FILLED_REQUIRED_FIELDS = (
    "venue_id",
    "broker_legal_name",
    "account_class",
    "order_types",
    "session_calendar_ref",
    "fee_schedule_source",
    "slippage_policy_source",
    "failover_policy",
    "disconnect_policy",
    "fill_binding_id",
    "ei_artifact_set_id",
    "lrc_contract_id",
    "declared_by",
    "declared_at",
)
