"""Hash echo smoke for SIF_CID_003_V0_2_0（@0.2.0 positioning lineage）."""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_SOURCE = "0e796e226b5906f22bdc4ce622f522788985a05525d2f65ae05e40fb2c474012"
EXPECTED_PARAM = "fce3f995d1421ada2152e591362700ed2a24d93c7ff3259394261f254cd7aa22"
PATHS = [
    "strategies/paaf/adapters/vnpy_adapter.py",
    "strategies/paaf/detectors/opp16_two_bar_reversal.py",
    "strategies/paaf/strat_rev_opp16_01.py",
    "strategies/paaf/strat_rev_opp16_01_v011.py",
    "strategies/paaf/strat_rev_opp16_01_v020.py",
]


class TestCid003IdentityHashesV020(unittest.TestCase):
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
            "capital_floor_ratio": {"type": "float", "unit": "fraction_of_capital", "value": 0.5},
            "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
            "hard_max_lots": {"type": "int", "unit": "contracts", "value": 1},
            "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
            "risk_per_trade": {"type": "float", "unit": "fraction_of_equity", "value": 0.005},
            "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
            "sizing_mode": {"type": "str", "unit": "enum", "value": "RISK_FRACTION_OF_CAPITAL"},
        }
        canon = json.dumps(params, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        self.assertEqual(hashlib.sha256(canon.encode("utf-8")).hexdigest(), EXPECTED_PARAM)

    def test_import_version(self) -> None:
        from strategies.paaf.strat_rev_opp16_01_v020 import StratRevOpp1601StrategyV020

        self.assertEqual(StratRevOpp1601StrategyV020.strategy_version, "0.2.0")
        self.assertEqual(StratRevOpp1601StrategyV020.strategy_id, "STRAT_REV_OPP16_01")


if __name__ == "__main__":
    unittest.main()
