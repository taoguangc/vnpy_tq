"""Smoke: Opp16 Context×RISK adapter subclasses V020 without mutating G5 hashes."""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_SOURCE = "0e796e226b5906f22bdc4ce622f522788985a05525d2f65ae05e40fb2c474012"
PATHS = [
    "strategies/paaf/adapters/vnpy_adapter.py",
    "strategies/paaf/detectors/opp16_two_bar_reversal.py",
    "strategies/paaf/strat_rev_opp16_01.py",
    "strategies/paaf/strat_rev_opp16_01_v011.py",
    "strategies/paaf/strat_rev_opp16_01_v020.py",
]


class TestOpp16CtxFilterV020(unittest.TestCase):
    def test_g5_source_hash_unchanged(self) -> None:
        manifest = []
        for rel in sorted(PATHS):
            digest = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
            manifest.append({"path": rel, "sha256": digest})
        canon = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        self.assertEqual(hashlib.sha256(canon.encode()).hexdigest(), EXPECTED_SOURCE)

    def test_adapter_surface(self) -> None:
        from strategies.paaf.context_consumer.opp16_ctx_filter_v020 import Opp16CtxFilterV020
        from strategies.paaf.strat_rev_opp16_01_v020 import StratRevOpp1601StrategyV020

        self.assertTrue(issubclass(Opp16CtxFilterV020, StratRevOpp1601StrategyV020))
        self.assertEqual(Opp16CtxFilterV020.surface_id, "RISK")
        self.assertEqual(Opp16CtxFilterV020.filter_id, "F1_EXPANSION_ONLY")
        self.assertEqual(Opp16CtxFilterV020.freeze_id, "SIF_CID_003_V0_2_0")
        self.assertEqual(Opp16CtxFilterV020.experiment_id, "CTX_CID003_EXP004")


if __name__ == "__main__":
    unittest.main()
