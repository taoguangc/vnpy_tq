"""CXSD wire-up into Context Filter adapter（no G5 mutate）."""
from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from strategies.paaf.brooks_scalp_paaf_strategy_v011 import BrooksScalpPaafStrategyV011
from strategies.paaf.context_consumer.brooks_scalp_ctx_filter_v011 import (
    BrooksScalpCtxFilterV011,
)
from strategies.paaf.cxsd import CONTRACT_ID, audit_lineage_complete


class _DummyFilter(BrooksScalpCtxFilterV011):
    """Bypass CtaTemplate __init__ for unit tests."""

    def __init__(self) -> None:
        self._permission_denials = []
        self._cxsd_audit_events = []
        self._last_context_state = "invalid"
        self._last_cxsd_permission = "BLOCK"
        self.am = object()
        self.filter_id = BrooksScalpCtxFilterV011.filter_id
        self.context_version = BrooksScalpCtxFilterV011.context_version
        self.cxsd_version = BrooksScalpCtxFilterV011.cxsd_version
        self.consumer_id = BrooksScalpCtxFilterV011.consumer_id
        self.surface_id = BrooksScalpCtxFilterV011.surface_id
        self.freeze_id = BrooksScalpCtxFilterV011.freeze_id
        self.detector_binding = BrooksScalpCtxFilterV011.detector_binding
        self.experiment_id = BrooksScalpCtxFilterV011.experiment_id
        self._submitted = False


class TestCxsdAdapterWire(unittest.TestCase):
    def test_compression_blocks_with_cxsd_audit(self) -> None:
        filt = _DummyFilter()
        result = SimpleNamespace(
            reason="TEST",
            direction=SimpleNamespace(value="LONG"),
            entry=1.0,
        )
        with (
            patch(
                "strategies.paaf.context_consumer.brooks_scalp_ctx_filter_v011.publish_a1_context_state",
                return_value="compression",
            ),
            patch.object(
                BrooksScalpPaafStrategyV011,
                "_submit_stop_entry",
                lambda self, result: setattr(filt, "_submitted", True),
            ),
        ):
            BrooksScalpCtxFilterV011._submit_stop_entry(filt, result)
        self.assertFalse(filt._submitted)
        self.assertEqual(filt._last_cxsd_permission, "BLOCK")
        self.assertEqual(len(filt._cxsd_audit_events), 1)
        self.assertTrue(audit_lineage_complete(filt._cxsd_audit_events[0]))
        self.assertEqual(filt._cxsd_audit_events[0]["cxsd_version"], CONTRACT_ID)
        self.assertEqual(len(filt._permission_denials), 1)

    def test_expansion_allows_submit(self) -> None:
        filt = _DummyFilter()
        result = SimpleNamespace(
            reason="TEST",
            direction=SimpleNamespace(value="LONG"),
            entry=1.0,
        )
        with (
            patch(
                "strategies.paaf.context_consumer.brooks_scalp_ctx_filter_v011.publish_a1_context_state",
                return_value="expansion",
            ),
            patch.object(
                BrooksScalpPaafStrategyV011,
                "_submit_stop_entry",
                lambda self, result: setattr(filt, "_submitted", True),
            ),
        ):
            BrooksScalpCtxFilterV011._submit_stop_entry(filt, result)
        self.assertTrue(filt._submitted)
        self.assertEqual(filt._last_cxsd_permission, "ALLOW")
        self.assertTrue(audit_lineage_complete(filt._cxsd_audit_events[0]))
        self.assertEqual(len(filt._permission_denials), 0)

    def test_invalid_fail_closed(self) -> None:
        filt = _DummyFilter()
        result = SimpleNamespace(reason="TEST", direction=SimpleNamespace(value="LONG"), entry=1.0)
        with (
            patch(
                "strategies.paaf.context_consumer.brooks_scalp_ctx_filter_v011.publish_a1_context_state",
                return_value="invalid",
            ),
            patch.object(
                BrooksScalpPaafStrategyV011,
                "_submit_stop_entry",
                lambda self, result: setattr(filt, "_submitted", True),
            ),
        ):
            BrooksScalpCtxFilterV011._submit_stop_entry(filt, result)
        self.assertFalse(filt._submitted)
        self.assertEqual(filt._last_cxsd_permission, "BLOCK")


if __name__ == "__main__":
    unittest.main()
