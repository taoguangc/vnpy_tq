"""Hash echo smoke for SIF_CID_006_V0_1."""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_SOURCE = "0a6023e581b8547d42c10a30f05324f0c841d131cbbd748ade4ad7476fd66f14"
EXPECTED_PARAM = "5c48a70f7666d033d340799e4fdf19972aeadfc15c98b068f85521ab32d0163e"
PATHS = [
    "strategies/paaf/detectors/opp08_strong_breakout.py",
    "strategies/paaf/strat_trend_opp08_01.py",
]


class TestCid006IdentityHashes(unittest.TestCase):
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
            "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
            "strong_bar_atr_mult": {"type": "float", "unit": "atr_multiple", "value": 1.0},
            "strong_bar_body_ratio": {"type": "float", "unit": "fraction", "value": 0.6},
        }
        canon = json.dumps(params, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        self.assertEqual(hashlib.sha256(canon.encode("utf-8")).hexdigest(), EXPECTED_PARAM)

    def test_import(self) -> None:
        from strategies.paaf.strat_trend_opp08_01 import StratTrendOpp0801Strategy

        self.assertEqual(StratTrendOpp0801Strategy.strategy_id, "STRAT_TREND_OPP08_01")
        self.assertEqual(StratTrendOpp0801Strategy.strategy_version, "0.1.0")


if __name__ == "__main__":
    unittest.main()
