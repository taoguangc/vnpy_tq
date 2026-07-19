"""Tests for preregistered scalar Feature experiment gates."""

from __future__ import annotations

import unittest

from scripts.paaf_scalar_feature_experiment import classify_association


class TestScalarFeatureEvidenceGate(unittest.TestCase):
    def test_detects_only_material_stable_association(self) -> None:
        self.assertEqual(
            classify_association(
                rho_ex_roll=0.12,
                ci95_low_ex_roll=0.08,
                ci95_high_ex_roll=0.16,
                rho_full=0.10,
            ),
            "association_detected",
        )

    def test_rejects_small_crossing_or_roll_unstable_effects(self) -> None:
        cases = (
            {
                "rho_ex_roll": 0.09,
                "ci95_low_ex_roll": 0.05,
                "ci95_high_ex_roll": 0.13,
                "rho_full": 0.09,
            },
            {
                "rho_ex_roll": 0.12,
                "ci95_low_ex_roll": -0.01,
                "ci95_high_ex_roll": 0.20,
                "rho_full": 0.12,
            },
            {
                "rho_ex_roll": 0.12,
                "ci95_low_ex_roll": 0.08,
                "ci95_high_ex_roll": 0.16,
                "rho_full": -0.10,
            },
            {
                "rho_ex_roll": 0.12,
                "ci95_low_ex_roll": 0.08,
                "ci95_high_ex_roll": 0.16,
                "rho_full": 0.01,
            },
        )
        for case in cases:
            with self.subTest(case=case):
                self.assertEqual(
                    classify_association(**case),
                    "inconclusive",
                )


if __name__ == "__main__":
    unittest.main()
