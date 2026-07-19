"""Tests for DATA EXP002 multi-symbol roll evidence gates."""

from __future__ import annotations

import unittest

from scripts.paaf_data_multi_symbol_roll_exp002 import (
    _is_material,
    classify_multi,
)


class TestDataExp002Gates(unittest.TestCase):
    def test_material_requires_roll_and_ratio_gate(self) -> None:
        self.assertTrue(_is_material(1.6, 1.0, 2))
        self.assertTrue(_is_material(1.0, 1.25, 1))
        self.assertFalse(_is_material(1.4, 1.1, 3))
        self.assertFalse(_is_material(2.0, 2.0, 0))

    def test_majority_classification(self) -> None:
        self.assertEqual(classify_multi(0, 4), "roll_effect_immaterial_multi")
        self.assertEqual(
            classify_multi(2, 4),
            "roll_effect_material_annotate_multi",
        )
        self.assertEqual(classify_multi(1, 4), "inconclusive")


if __name__ == "__main__":
    unittest.main()
