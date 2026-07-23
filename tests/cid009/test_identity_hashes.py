"""Hash echo smoke for SIF_CID_009_V0_1."""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_SOURCE = "1b0f5858d8d22371906085cdf974b8378e60d6bdb8c3924a509bfce62e9cb8a1"
EXPECTED_PARAM = "960b1ae8abdf5011f6d7977bf99c4bae7a8f8264721afca0488e687b539af9f6"
PATHS = [
    "strategies/paaf/detectors/opp15_wedge_path_a.py",
    "strategies/paaf/morphology/wedge.py",
    "strategies/paaf/strat_rev_opp15_01.py",
]


class TestCid009IdentityHashes(unittest.TestCase):
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
            "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
            "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
            "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
            "strong_bar_atr_mult": {"type": "float", "unit": "atr_multiple", "value": 1.0},
            "strong_bar_body_ratio": {"type": "float", "unit": "fraction", "value": 0.6},
            "wedge_alpha_threshold": {"type": "float", "unit": "fraction", "value": 0.85},
            "wedge_arm_trigger_max_bars": {"type": "int", "unit": "bars", "value": 4},
            "wedge_n_min": {"type": "int", "unit": "bars", "value": 3},
        }
        canon = json.dumps(params, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        self.assertEqual(hashlib.sha256(canon.encode("utf-8")).hexdigest(), EXPECTED_PARAM)

    def test_import(self) -> None:
        from strategies.paaf.strat_rev_opp15_01 import StratRevOpp1501Strategy

        self.assertEqual(StratRevOpp1501Strategy.strategy_id, "STRAT_REV_OPP15_01")
        self.assertEqual(StratRevOpp1501Strategy.strategy_version, "0.1.0")


if __name__ == "__main__":
    unittest.main()
