"""CXSD-CID_002-v0.1 conformance constants."""
from __future__ import annotations

CONTRACT_ID = "CXSD-CID_002-v0.1"
DESIGN_ID = "CXSD_CID_002_V0_1"
CHARTER_ID = "CXSDIC_CID_002_V0_1"

PERMISSIONS = frozenset({"ALLOW", "BLOCK", "MONITOR"})

ALLOWED_INTENTS = frozenset({"get_state", "decide"})

FORBIDDEN_INTENTS = frozenset(
    {
        "modify_signal",
        "modify_position",
        "generate_order",
        "set_size",
        "set_lots",
        "predict_return",
        "score_alpha",
        "buy",
        "sell",
        "cancel",
        "cover",
    }
)

# Design §2.1 Consumer Identity
CONSUMERS_MAY_READ = frozenset(
    {
        "CI_FILTER_ADAPTER",
        "CI_MONITOR",
        "CI_HARNESS",
    }
)

CONSUMERS_MAY_DECIDE = frozenset(
    {
        "CI_FILTER_ADAPTER",
    }
)

CONSUMERS_FORBIDDEN_READ = frozenset(
    {
        "CI_ORCH_MECH",
        "CI_ORCH_RISK",
        "CI_DETECTOR",
        "CI_ENGINE",
    }
)

# Failure Policy — Context conditions that force BLOCK on trading path
FAIL_CLOSED_STATES = frozenset(
    {
        "invalid",
        "missing",
        "degraded",
        "unsupported",
        "",
    }
)

# Audit required fields（Design §2.6）
AUDIT_REQUIRED_FIELDS = (
    "experiment_id",
    "surface_id",
    "cxsd_version",
    "context_version",
    "context_engine_id",
    "context_state",
    "permission",
    "detector_binding",
    "freeze_id",
    "event",
)

SURFACE_IDS = frozenset({"MECH", "RISK"})
