"""Contract tests for Method A roll audit helpers."""

from __future__ import annotations

from datetime import datetime, timezone
import unittest

import numpy as np

from strategies.paaf.data_audit.roll_audit import (
    compute_roll_gaps,
    neighborhood_mask,
    summarize_roll_audit,
)
from strategies.paaf.evidence.models import SUBJECT_KINDS, EvidenceRecord


class TestRollAudit(unittest.TestCase):
    def test_compute_roll_gaps_on_yymm_change(self) -> None:
        closes = [100.0, 101.0, 110.0, 111.0]
        yymms = ["2401", "2401", "2405", "2405"]
        timestamps = [
            datetime(2024, 3, 1, i, tzinfo=timezone.utc) for i in range(4)
        ]
        gaps = compute_roll_gaps(closes, yymms, timestamps)
        self.assertEqual(len(gaps), 1)
        self.assertEqual(gaps[0].roll_index, 2)
        self.assertEqual(gaps[0].from_yymm, "2401")
        self.assertEqual(gaps[0].to_yymm, "2405")
        self.assertAlmostEqual(gaps[0].gap_abs, 9.0)
        self.assertAlmostEqual(gaps[0].gap_rel, 9.0 / 101.0)

    def test_neighborhood_mask_window(self) -> None:
        mask = neighborhood_mask(10, roll_indices=(5,), window=2)
        self.assertEqual(
            mask.tolist(),
            [False, False, False, True, True, True, True, True, False, False],
        )

    def test_summary_vol_ratio_detects_roll_shock(self) -> None:
        # Mild noise away from the roll, one large jump at roll.
        rng = np.random.default_rng(0)
        base = 100.0 + rng.normal(0.0, 0.05, size=40)
        closes = base.tolist()
        closes[20] = closes[19] + 8.0
        for index in range(21, 40):
            closes[index] = closes[20] + rng.normal(0.0, 0.05)
        yymms = ["2401"] * 20 + ["2405"] * 20
        timestamps = [
            datetime(2024, 1, 1, 0, i % 60, tzinfo=timezone.utc)
            for i in range(len(closes))
        ]
        gaps = compute_roll_gaps(closes, yymms, timestamps)
        summary = summarize_roll_audit(
            closes=closes,
            gaps=gaps,
            window=3,
            atr_ratios=[1.0] * len(closes),
        )
        self.assertEqual(summary.roll_count, 1)
        self.assertGreater(summary.gap_abs_mean, 1.0)
        self.assertGreater(summary.vol_ratio, 1.0)
        self.assertAlmostEqual(summary.atr_ratio_neighborhood_mean, 1.0)
        self.assertAlmostEqual(summary.atr_ratio_non_roll_mean, 1.0)

    def test_dataset_subject_kind_is_allowed(self) -> None:
        self.assertIn("dataset", SUBJECT_KINDS)
        evidence = EvidenceRecord(
            evidence_id="EV-DATA-TEST",
            experiment_id="DATA-TEST",
            subject_kind="dataset",
            subject_id="rb_cbc_unadjusted",
            subject_version="1.0",
            hypothesis="fixture",
            decision="HOLD",
            feature_artifact_uri="artifacts/x/data.json",
            artifact_hash="sha256:abc",
            created_at=datetime(2026, 7, 19, tzinfo=timezone.utc),
        )
        self.assertEqual(evidence.subject_kind, "dataset")


if __name__ == "__main__":
    unittest.main()
