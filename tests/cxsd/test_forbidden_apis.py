"""CXSD forbidden API intent tests."""
from __future__ import annotations

import unittest

from strategies.paaf.cxsd import detect_violations, validate_intent


class TestForbiddenApis(unittest.TestCase):
    def test_get_state_and_decide_allowed(self) -> None:
        self.assertTrue(validate_intent("get_state").ok)
        self.assertTrue(validate_intent("decide").ok)

    def test_forbidden_intents_rejected(self) -> None:
        for name in (
            "modify_signal",
            "modify_position",
            "generate_order",
            "set_size",
            "buy",
            "score_alpha",
        ):
            check = validate_intent(name)
            self.assertFalse(check.ok)
            hits = detect_violations(intent=name)
            self.assertTrue(any(v.code == "F_FORBIDDEN_INTENT" for v in hits))


if __name__ == "__main__":
    unittest.main()
