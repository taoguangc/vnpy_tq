"""Hash echo smoke for SIF_CID_008_V0_1."""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_SOURCE = "c6e47760e11290b171aec8d50c7f727606ed5df147ecb6eaa3b660fa62de9f99"
EXPECTED_PARAM = "06b64730fa61b0b1c9411feb332140d5a7b4911339c035ac30f0ede406db7a86"
PATHS = [
    "strategies/paaf/detectors/opp02_ema_pullback.py",
    "strategies/paaf/strat_trend_opp02_01.py",
]


class TestCid008IdentityHashes(unittest.TestCase):
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
            "ema_pullback_min_body_ratio": {"type": "float", "unit": "fraction", "value": 0.35},
            "ema_pullback_touch_atr": {"type": "float", "unit": "atr_multiple", "value": 1.0},
            "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
            "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
            "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
            "wick_max_fraction": {"type": "float", "unit": "fraction", "value": 0.45},
        }
        canon = json.dumps(params, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        self.assertEqual(hashlib.sha256(canon.encode("utf-8")).hexdigest(), EXPECTED_PARAM)

    def test_import(self) -> None:
        from strategies.paaf.strat_trend_opp02_01 import StratTrendOpp0201Strategy

        self.assertEqual(StratTrendOpp0201Strategy.strategy_id, "STRAT_TREND_OPP02_01")
        self.assertEqual(StratTrendOpp0201Strategy.strategy_version, "0.1.0")


if __name__ == "__main__":
    unittest.main()
