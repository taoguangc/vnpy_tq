"""Hash echo smoke for SIF_CID_010_V0_1."""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_SOURCE = "d20147d23918edac9d94cdea5572155dacc8375218b62c0aa4a822eac303d1de"
EXPECTED_PARAM = "1f95584dfc3a17c18ad41210a53e53fbe050988850d656f881686d80e7c11405"
PATHS = [
    "strategies/paaf/detectors/opp13_day_boundary_touch.py",
    "strategies/paaf/strat_rev_opp13_01.py",
]


class TestCid010IdentityHashes(unittest.TestCase):
    def test_source_hash(self) -> None:
        manifest = []
        for rel in sorted(PATHS):
            digest = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
            manifest.append({"path": rel, "sha256": digest})
        canon = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        self.assertEqual(hashlib.sha256(canon.encode()).hexdigest(), EXPECTED_SOURCE)

    def test_parameter_hash(self) -> None:
        params = {
            "boundary_reversal_close_ratio": {"type": "float", "unit": "fraction", "value": 0.3},
            "boundary_reversal_shadow_ratio": {"type": "float", "unit": "fraction", "value": 0.45},
            "day_boundary_tolerance": {"type": "float", "unit": "ticks", "value": 5.0},
            "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
            "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
            "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
        }
        canon = json.dumps(params, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        self.assertEqual(hashlib.sha256(canon.encode("utf-8")).hexdigest(), EXPECTED_PARAM)

    def test_import(self) -> None:
        from strategies.paaf.strat_rev_opp13_01 import StratRevOpp1301Strategy

        self.assertEqual(StratRevOpp1301Strategy.strategy_id, "STRAT_REV_OPP13_01")
        self.assertEqual(StratRevOpp1301Strategy.strategy_version, "0.1.0")


if __name__ == "__main__":
    unittest.main()
