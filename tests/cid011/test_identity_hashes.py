"""Hash echo smoke for SIF_CID_011_V0_1."""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_SOURCE = "731c908d810d6c5f61400ceaeb06beb37a8436bc2f8503261ba2fecd86060593"
EXPECTED_PARAM = "2f8f2170dc94cfa63ac9e99bfd365d239be4c4186672c5db54143ae0d21b8f71"
PATHS = [
    "strategies/paaf/detectors/opp19_opening_drive_reversal.py",
    "strategies/paaf/strat_sess_opp19_rev_01.py",
]


class TestCid011IdentityHashes(unittest.TestCase):
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
            "max_bar1_range_atr": {"type": "float", "unit": "atr_multiple", "value": 2.5},
            "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
            "min_bar1_range_atr": {"type": "float", "unit": "atr_multiple", "value": 0.3},
            "morning_cutoff_minute": {"type": "int", "unit": "minute", "value": 25},
            "night_cutoff_minute": {"type": "int", "unit": "minute", "value": 25},
            "opening_rev_body_ratio": {"type": "float", "unit": "fraction", "value": 0.45},
            "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
        }
        canon = json.dumps(params, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        self.assertEqual(hashlib.sha256(canon.encode("utf-8")).hexdigest(), EXPECTED_PARAM)

    def test_import(self) -> None:
        from strategies.paaf.strat_sess_opp19_rev_01 import StratSessOpp19Rev01Strategy

        self.assertEqual(StratSessOpp19Rev01Strategy.strategy_id, "STRAT_SESS_OPP19_REV_01")
        self.assertEqual(StratSessOpp19Rev01Strategy.strategy_version, "0.1.0")


if __name__ == "__main__":
    unittest.main()
