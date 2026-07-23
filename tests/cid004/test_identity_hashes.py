"""Hash echo smoke for SIF_CID_004_V0_1."""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_SOURCE = "2efd2112a7ffd6eae70ac2761c0ba3559a07a3e0f6ef7f13ae4e35caba42de4d"
EXPECTED_PARAM = "b6c767a8bf8afde7e5bba56a2777a036ab21f06b7b807ec630d9bd6edb9e1418"
PATHS = [
    "strategies/paaf/detectors/opp12_overshoot_fail.py",
    "strategies/paaf/strat_rev_opp12_01.py",
]


class TestCid004IdentityHashes(unittest.TestCase):
    def test_source_hash(self) -> None:
        manifest = []
        for rel in sorted(PATHS):
            digest = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
            manifest.append({"path": rel, "sha256": digest})
        canon = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        self.assertEqual(hashlib.sha256(canon.encode()).hexdigest(), EXPECTED_SOURCE)

    def test_parameter_hash(self) -> None:
        params = {
            "atr_period": {"type": "int", "unit": "bars", "value": 14},
            "ema_period": {"type": "int", "unit": "bars", "value": 20},
            "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
            "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
            "overshoot_atr_mult": {"type": "float", "unit": "atr_multiple", "value": 1.2},
            "overshoot_max_atr_mult": {"type": "float", "unit": "atr_multiple", "value": 2.5},
            "reversal_close_quarter": {"type": "float", "unit": "fraction", "value": 0.25},
            "reversal_min_body_ratio": {"type": "float", "unit": "fraction", "value": 0.15},
            "reversal_shadow_min_ratio": {"type": "float", "unit": "fraction", "value": 0.4},
            "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
        }
        canon = json.dumps(params, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        self.assertEqual(hashlib.sha256(canon.encode("utf-8")).hexdigest(), EXPECTED_PARAM)

    def test_import(self) -> None:
        from strategies.paaf.strat_rev_opp12_01 import StratRevOpp1201Strategy

        self.assertEqual(StratRevOpp1201Strategy.strategy_id, "STRAT_REV_OPP12_01")
        self.assertEqual(StratRevOpp1201Strategy.strategy_version, "0.1.0")


if __name__ == "__main__":
    unittest.main()
