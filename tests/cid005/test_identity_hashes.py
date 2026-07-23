"""Hash echo smoke for SIF_CID_005_V0_1."""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_SOURCE = "9d85cf960f30715524f7224bdf3dd9750ce4fd1ad86a79d9122789c75e5cb576"
EXPECTED_PARAM = "40ef1e1d594294e89e9872f08c5ac5d057dc36156081784e030c072fd19b0816"
PATHS = [
    "strategies/paaf/detectors/opp17_climax_reversal.py",
    "strategies/paaf/strat_rev_opp17_01.py",
]


class TestCid005IdentityHashes(unittest.TestCase):
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
            "climax_range_atr": {"type": "float", "unit": "atr_multiple", "value": 2.5},
            "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
            "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
            "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
        }
        canon = json.dumps(params, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        self.assertEqual(hashlib.sha256(canon.encode("utf-8")).hexdigest(), EXPECTED_PARAM)

    def test_import(self) -> None:
        from strategies.paaf.strat_rev_opp17_01 import StratRevOpp1701Strategy

        self.assertEqual(StratRevOpp1701Strategy.strategy_id, "STRAT_REV_OPP17_01")
        self.assertEqual(StratRevOpp1701Strategy.strategy_version, "0.1.0")


if __name__ == "__main__":
    unittest.main()
