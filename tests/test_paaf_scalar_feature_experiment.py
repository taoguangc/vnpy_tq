"""Tests for preregistered scalar Feature experiment gates."""

from __future__ import annotations

import unittest

import pandas as pd

from scripts.paaf_scalar_feature_experiment import (
    _frame_values,
    classify_association,
)


class TestScalarFeatureEvidenceGate(unittest.TestCase):
    def test_open_interest_prefers_close_and_falls_back_to_open(self) -> None:
        frame = pd.DataFrame({
            "open_oi": [100.0, 101.0, 102.0],
            "close_oi": [110.0, None, 112.0],
        })

        values = _frame_values(frame, "open_interest")

        self.assertEqual(values.tolist(), [110.0, 101.0, 112.0])

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
