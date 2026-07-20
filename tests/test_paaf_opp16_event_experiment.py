"""OPP16 event-study evidence gate tests."""

from __future__ import annotations

import unittest

from scripts.paaf_opp16_event_experiment import classify_opp16_association


class TestOpp16EvidenceGate(unittest.TestCase):
    def test_detects_only_when_all_gates_pass(self) -> None:
        self.assertEqual(
            classify_opp16_association(
                mean_ex_roll=0.001,
                ci95_low_ex_roll=0.0002,
                mean_full=0.0009,
                sample_n_ex_roll=120,
            ),
            "association_detected",
        )

    def test_rejects_small_crossing_or_unstable(self) -> None:
        cases = (
            {
                "mean_ex_roll": 0.001,
                "ci95_low_ex_roll": -0.0001,
                "mean_full": 0.001,
                "sample_n_ex_roll": 120,
            },
            {
                "mean_ex_roll": 0.001,
                "ci95_low_ex_roll": 0.0002,
                "mean_full": -0.001,
                "sample_n_ex_roll": 120,
            },
            {
                "mean_ex_roll": 0.001,
                "ci95_low_ex_roll": 0.0002,
                "mean_full": 0.002,
                "sample_n_ex_roll": 120,
            },
            {
                "mean_ex_roll": 0.001,
                "ci95_low_ex_roll": 0.0002,
                "mean_full": 0.001,
                "sample_n_ex_roll": 50,
            },
        )
        for case in cases:
            with self.subTest(case=case):
                self.assertEqual(
                    classify_opp16_association(**case),
                    "inconclusive",
                )


if __name__ == "__main__":
    unittest.main()
