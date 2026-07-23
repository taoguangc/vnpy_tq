"""Hash echo smoke for SIF_CID_003_V0_1_1（@0.1.1 repair lineage）."""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_SOURCE = "6dee22fe6c1eaf5958defa3f94db614ece5991bdbc58abc93d281bbd7b1164b5"
EXPECTED_PARAM = "76b124f47414af2da2e0cdfdc6afcd5025d2cca8ae3a5583ba667cc7e1e31c57"
PATHS = [
    "strategies/paaf/adapters/vnpy_adapter.py",
    "strategies/paaf/detectors/opp16_two_bar_reversal.py",
    "strategies/paaf/strat_rev_opp16_01.py",
    "strategies/paaf/strat_rev_opp16_01_v011.py",
]


class TestCid003IdentityHashesV011(unittest.TestCase):
    def test_source_hash(self) -> None:
        manifest = []
        for rel in sorted(PATHS):
            digest = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
            manifest.append({"path": rel, "sha256": digest})
        canon = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        self.assertEqual(hashlib.sha256(canon.encode()).hexdigest(), EXPECTED_SOURCE)

    def test_parameter_hash(self) -> None:
        params = {
            "body_ratio": {"type": "float", "unit": "fraction", "value": 0.5},
            "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
            "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
            "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
        }
        canon = json.dumps(params, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        self.assertEqual(hashlib.sha256(canon.encode("utf-8")).hexdigest(), EXPECTED_PARAM)

    def test_import_version(self) -> None:
        from strategies.paaf.strat_rev_opp16_01 import StratRevOpp1601Strategy
        from strategies.paaf.strat_rev_opp16_01_v011 import StratRevOpp1601StrategyV011

        self.assertEqual(StratRevOpp1601Strategy.strategy_version, "0.1.0")
        self.assertEqual(StratRevOpp1601StrategyV011.strategy_version, "0.1.1")
        self.assertEqual(StratRevOpp1601StrategyV011.strategy_id, "STRAT_REV_OPP16_01")


if __name__ == "__main__":
    unittest.main()
