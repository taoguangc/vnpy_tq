"""CXSD audit lineage field tests."""
from __future__ import annotations

import unittest

from strategies.paaf.cxsd import (
    CONTRACT_ID,
    audit_lineage_complete,
    build_audit_event,
    validate_audit_event,
)


class TestAuditFields(unittest.TestCase):
    def test_complete_audit_passes(self) -> None:
        event = build_audit_event(
            experiment_id="CXSD_SELF_CHECK",
            surface_id="MECH",
            context_state="compression",
            permission="BLOCK",
            event="PERMISSION_DENIAL",
            detector_binding="BROOKS_SCALP_FP@0.1.0",
            freeze_id="SIF_CID_002_V0_1_1",
            signal_reason="demo",
        )
        self.assertEqual(validate_audit_event(event), [])
        self.assertTrue(audit_lineage_complete(event))
        self.assertEqual(event["cxsd_version"], CONTRACT_ID)

    def test_missing_field_fails(self) -> None:
        event = build_audit_event(
            experiment_id="CXSD_SELF_CHECK",
            surface_id="MECH",
            context_state="expansion",
            permission="ALLOW",
            event="PERMISSION_ALLOW",
            detector_binding="BROOKS_SCALP_FP@0.1.0",
            freeze_id="SIF_CID_002_V0_1_1",
        )
        del event["freeze_id"]
        defects = validate_audit_event(event)
        self.assertIn("missing:freeze_id", defects)


if __name__ == "__main__":
    unittest.main()
