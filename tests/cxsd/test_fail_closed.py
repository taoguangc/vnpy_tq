"""CXSD fail-closed trading path tests."""
from __future__ import annotations

import unittest

from strategies.paaf.cxsd import detect_violations, failure_policy_blocks, resolve_permission


class TestFailClosed(unittest.TestCase):
    def test_invalid_state_blocks_orders(self) -> None:
        self.assertTrue(failure_policy_blocks("invalid"))
        gate = resolve_permission(
            consumer_id="CI_FILTER_ADAPTER",
            context_state="invalid",
            filter_would_allow=True,
        )
        self.assertEqual(gate.permission, "BLOCK")
        self.assertFalse(gate.order_allowed)

    def test_order_under_block_is_violation(self) -> None:
        hits = detect_violations(
            context_state="expansion",
            permission="BLOCK",
            order_submitted=True,
        )
        self.assertTrue(any(v.code == "F_FAIL_OPEN" for v in hits))

    def test_monitor_must_not_submit(self) -> None:
        gate = resolve_permission(
            consumer_id="CI_MONITOR",
            context_state="expansion",
            filter_would_allow=True,
            monitor_only=True,
        )
        self.assertEqual(gate.permission, "MONITOR")
        self.assertFalse(gate.order_allowed)
        hits = detect_violations(
            context_state="expansion",
            permission="MONITOR",
            order_submitted=True,
        )
        self.assertTrue(any(v.code == "F_MONITOR_TRADE" for v in hits))

    def test_detector_cannot_decide(self) -> None:
        gate = resolve_permission(
            consumer_id="CI_DETECTOR",
            context_state="expansion",
            filter_would_allow=True,
        )
        self.assertFalse(gate.order_allowed)


if __name__ == "__main__":
    unittest.main()
