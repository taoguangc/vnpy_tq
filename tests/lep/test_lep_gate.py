"""Unit tests for LEP-CID_002-v0.1."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from strategies.paaf.lep import (
    BACKTEST_FILL_BINDING,
    CONTRACT_ID,
    check_call_edge,
    gate_live,
    validate_vbp_pack,
    validate_vmp_live_checklist,
)

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = ROOT / "docs" / "research" / "VBP_CID_002_venue_pack_TEMPLATE.json"


def _filled_pack() -> dict:
    return {
        "protocol_id": "VBP-CID_002-v0.1",
        "kind": "FILLED",
        "filled": True,
        "lrc_contract_id": "LRC-CID_002-v0.1",
        "ei_artifact_set_id": "DID_CID_002_V0_2_ARTIFACT_SET",
        "venue_id": "EXAMPLE_VENUE",
        "broker_legal_name": "Example Broker Co",
        "account_class": "SIM",
        "order_types": ["LIMIT"],
        "session_calendar_ref": "exchange_calendar:SHFE",
        "fee_schedule_source": "broker_fee_table_v1",
        "slippage_policy_source": "venue_slippage_note_v1",
        "failover_policy": "halt_new_entries",
        "disconnect_policy": "flatten_on_disconnect_timeout",
        "fill_binding_id": "VENUE_SIM_FILLS_V1",
        "declared_by": "test",
        "declared_at": "2026-07-23T00:00:00Z",
        "evidence_paths": [],
    }


def _vmp_ok() -> dict:
    return {
        "checklist_id": "VMP_LIVE_CID_002_V0_1",
        "session_calendar_ref": "exchange_calendar:SHFE",
        "restart_policy": "cold_reload_pins",
        "drift_detection": "hash_and_clock_check",
        "failover_policy": "halt_new_entries",
        "disconnect_policy": "flatten_on_disconnect_timeout",
        "identity_pin_ref": "DID_CID_002_V0_2_ARTIFACT_SET",
        "lrc_contract_id": "LRC-CID_002-v0.1",
        "vbp_pack_ref": "docs/research/example_filled.json",
        "cxsd_contract_id": "CXSD-CID_002-v0.1",
        "declared_by": "test",
        "declared_at": "2026-07-23T00:00:00Z",
    }


class TestVbp(unittest.TestCase):
    def test_template_ok_when_not_required_filled(self) -> None:
        pack = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
        check = validate_vbp_pack(pack, require_filled=False)
        self.assertTrue(check.ok)
        self.assertEqual(check.kind, "TEMPLATE")

    def test_template_fails_when_live_claimed(self) -> None:
        pack = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
        check = validate_vbp_pack(pack, require_filled=True)
        self.assertFalse(check.ok)
        self.assertEqual(check.reason, "live_requires_filled_pack")

    def test_filled_rejects_backtest_binding(self) -> None:
        pack = _filled_pack()
        pack["fill_binding_id"] = BACKTEST_FILL_BINDING
        check = validate_vbp_pack(pack, require_filled=True)
        self.assertFalse(check.ok)
        self.assertIn("backtest", check.reason)


class TestAcl(unittest.TestCase):
    def test_detector_cannot_buy(self) -> None:
        edge = check_call_edge("P_DETECTOR", "Engine.buy_sell")
        self.assertFalse(edge.ok)

    def test_filter_cannot_submit_entry(self) -> None:
        edge = check_call_edge("P_CTX_FILTER", "Orch.submit_entry")
        self.assertFalse(edge.ok)


class TestVmp(unittest.TestCase):
    def test_incomplete_fails(self) -> None:
        check = validate_vmp_live_checklist({"checklist_id": "VMP_LIVE_CID_002_V0_1"})
        self.assertFalse(check.ok)
        self.assertTrue(check.missing)

    def test_complete_ok(self) -> None:
        check = validate_vmp_live_checklist(_vmp_ok())
        self.assertTrue(check.ok)


class TestGate(unittest.TestCase):
    def test_fail_closed_on_template(self) -> None:
        pack = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
        result = gate_live(vbp_pack=pack, vmp_checklist=_vmp_ok(), claim_live=True)
        self.assertFalse(result.ok)
        self.assertFalse(result.production_bindable)
        self.assertFalse(result.live_authorized)

    def test_pass_preconditions_still_not_go_live(self) -> None:
        result = gate_live(
            vbp_pack=_filled_pack(),
            vmp_checklist=_vmp_ok(),
            claimed_call_edges=[("P_ORCH_MECH", "Detector.detect")],
            claim_live=True,
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.lep_contract_id, CONTRACT_ID)
        self.assertFalse(result.production_bindable)
        self.assertFalse(result.live_authorized)

    def test_acl_deny_blocks_gate(self) -> None:
        result = gate_live(
            vbp_pack=_filled_pack(),
            vmp_checklist=_vmp_ok(),
            claimed_call_edges=[("P_DETECTOR", "Engine.buy_sell")],
            claim_live=True,
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.reason, "acl_hard_deny")


if __name__ == "__main__":
    unittest.main()
