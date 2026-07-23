"""Hash echo smoke for SIF_CID_007_V0_1."""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_SOURCE = "f7cbcb3f9b556af5478d7f88fa9d7f51627887250273b4bd4c153e38e43d90d6"
EXPECTED_PARAM = "3f9793feda3d0ca20ba238197acbf120a469a486620b0f23a002dcceb5762a05"
PATHS = [
    "strategies/paaf/detectors/opp19_opening_drive_breakout.py",
    "strategies/paaf/strat_sess_opp19_01.py",
]


class TestCid007IdentityHashes(unittest.TestCase):
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
            "opening_drive_bars": {"type": "int", "unit": "bars", "value": 6},
            "opening_drive_min_body": {"type": "float", "unit": "fraction", "value": 0.5},
            "opening_drive_range_atr_min": {"type": "float", "unit": "atr_multiple", "value": 0.2},
            "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
            "strong_bar_atr_mult": {"type": "float", "unit": "atr_multiple", "value": 1.0},
            "strong_bar_body_ratio": {"type": "float", "unit": "fraction", "value": 0.6},
        }
        canon = json.dumps(params, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        self.assertEqual(hashlib.sha256(canon.encode("utf-8")).hexdigest(), EXPECTED_PARAM)

    def test_import(self) -> None:
        from strategies.paaf.strat_sess_opp19_01 import StratSessOpp1901Strategy

        self.assertEqual(StratSessOpp1901Strategy.strategy_id, "STRAT_SESS_OPP19_01")
        self.assertEqual(StratSessOpp1901Strategy.strategy_version, "0.1.0")


if __name__ == "__main__":
    unittest.main()
