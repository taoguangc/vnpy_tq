"""Contract tests for Feature roll-neighborhood annotation helpers."""

from __future__ import annotations

import unittest

from strategies.paaf.data_audit import (
    DEFAULT_ROLL_WINDOW,
    aggregate_roll_neighborhood,
    contract_roll_neighborhood_mask,
    roll_change_indices,
    roll_neighborhood_mask,
)


class TestRollAnnotation(unittest.TestCase):
    def test_default_window_is_policy_value(self) -> None:
        self.assertEqual(DEFAULT_ROLL_WINDOW, 60)

    def test_contract_changes_define_inclusive_neighborhoods(self) -> None:
        contract_ids = ("2401", "2401", "2405", "2405", "2410")

        self.assertEqual(roll_change_indices(contract_ids), (2, 4))
        mask = contract_roll_neighborhood_mask(contract_ids, window=1)
        self.assertEqual(mask.tolist(), [False, True, True, True, True])

    def test_neighborhood_is_clipped_at_series_boundaries(self) -> None:
        mask = roll_neighborhood_mask(4, roll_indices=(1,), window=2)

        self.assertEqual(mask.tolist(), [True, True, True, True])

    def test_composite_bar_uses_any_constituent_one_minute_flag(self) -> None:
        self.assertTrue(
            aggregate_roll_neighborhood((False, False, True, False))
        )
        self.assertFalse(
            aggregate_roll_neighborhood((False, False, False))
        )

    def test_invalid_inputs_fail_explicitly(self) -> None:
        with self.assertRaisesRegex(ValueError, "length"):
            roll_neighborhood_mask(-1, (), window=60)
        with self.assertRaisesRegex(ValueError, "window"):
            roll_neighborhood_mask(3, (), window=-1)
        with self.assertRaisesRegex(ValueError, "roll_index"):
            roll_neighborhood_mask(3, (3,), window=1)
        with self.assertRaisesRegex(ValueError, "不得为空"):
            aggregate_roll_neighborhood(())
        with self.assertRaisesRegex(TypeError, "bool"):
            aggregate_roll_neighborhood((False, 1))  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
