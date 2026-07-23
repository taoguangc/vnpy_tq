"""Smoke: Opp16 Context Filter adapter subclasses MECH without mutating G5 hashes."""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_SOURCE = "6dee22fe6c1eaf5958defa3f94db614ece5991bdbc58abc93d281bbd7b1164b5"
PATHS = [
    "strategies/paaf/adapters/vnpy_adapter.py",
    "strategies/paaf/detectors/opp16_two_bar_reversal.py",
    "strategies/paaf/strat_rev_opp16_01.py",
    "strategies/paaf/strat_rev_opp16_01_v011.py",
]


class TestOpp16CtxFilterAdapter(unittest.TestCase):
    def test_g5_source_hash_unchanged(self) -> None:
        manifest = []
        for rel in sorted(PATHS):
            digest = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
            manifest.append({"path": rel, "sha256": digest})
        canon = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        self.assertEqual(hashlib.sha256(canon.encode()).hexdigest(), EXPECTED_SOURCE)

    def test_adapter_surface(self) -> None:
        from strategies.paaf.context_consumer.opp16_ctx_filter_v011 import Opp16CtxFilterV011
        from strategies.paaf.strat_rev_opp16_01_v011 import StratRevOpp1601StrategyV011

        self.assertTrue(issubclass(Opp16CtxFilterV011, StratRevOpp1601StrategyV011))
        self.assertEqual(Opp16CtxFilterV011.surface_id, "MECH")
        self.assertEqual(Opp16CtxFilterV011.filter_id, "F1_EXPANSION_ONLY")
        self.assertEqual(Opp16CtxFilterV011.freeze_id, "SIF_CID_003_V0_1_1")
        self.assertEqual(Opp16CtxFilterV011.experiment_id, "CTX_CID003_EXP001")


if __name__ == "__main__":
    unittest.main()
