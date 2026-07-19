"""DetectionResult / PatternState domain contract tests（v0.2.1）。"""

from __future__ import annotations

import json
import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

from strategies.paaf import (
    DetectionResult,
    DetectorStatus,
    DetectorTag,
    Direction,
    PatternState,
)


def _result(**overrides: object) -> DetectionResult:
    values: dict[str, object] = {
        "detector_id": "OPP16",
        "detector_version": "1.0.0",
        "opportunity_id": "OPP16",
        "status": DetectorStatus.EXPERIMENT,
        "direction": Direction.LONG,
        "confidence": 0.82,
        "tags": (DetectorTag.REVERSAL, "custom:two_bar"),
        "entry": 3500.0,
        "stop": 3490.0,
        "target": 3520.0,
        "reason": "two-bar reversal candidate",
        "metadata": {
            "source": "unit-test",
            "nested": {"bars": [1, 2]},
        },
        "pattern_state": PatternState(
            name="armed",
            confidence=0.75,
            metadata={"phase": "confirm"},
        ),
        "evidence_refs": ("EXP-021",),
        "schema_version": "1.0",
        "created_at": datetime(2026, 7, 19, 6, 0, tzinfo=timezone.utc),
    }
    values.update(overrides)
    return DetectionResult(**values)  # type: ignore[arg-type]


class TestDetectionResultContract(unittest.TestCase):
    def test_result_and_pattern_state_are_immutable(self) -> None:
        result = _result()

        with self.assertRaises(FrozenInstanceError):
            result.confidence = 0.5  # type: ignore[misc]
        with self.assertRaises(TypeError):
            result.metadata["source"] = "changed"  # type: ignore[index]
        with self.assertRaises(TypeError):
            result.metadata["nested"]["bars"] = []  # type: ignore[index]
        with self.assertRaises(FrozenInstanceError):
            result.pattern_state.name = "changed"  # type: ignore[union-attr,misc]
        with self.assertRaises(TypeError):
            result.pattern_state.metadata["phase"] = "changed"  # type: ignore[union-attr,index]

    def test_json_serialization_round_trip_is_equal(self) -> None:
        original = _result()

        payload = original.to_dict()
        encoded = json.dumps(payload, ensure_ascii=False)
        restored = DetectionResult.from_dict(json.loads(encoded))

        self.assertEqual(restored, original)
        self.assertEqual(payload["status"], "EXPERIMENT")
        self.assertEqual(payload["direction"], "LONG")
        self.assertEqual(
            payload["tags"],
            ["REVERSAL", "custom:two_bar"],
        )
        self.assertEqual(
            payload["created_at"],
            "2026-07-19T06:00:00+00:00",
        )

    def test_pattern_state_round_trip_is_equal(self) -> None:
        original = PatternState(
            name="Compression",
            confidence=0.82,
            metadata={"window": 12, "flags": ["armed"]},
        )

        restored = PatternState.from_dict(original.to_dict())

        self.assertEqual(restored, original)
        self.assertIsInstance(restored.confidence, float)

    def test_schema_version_is_explicit_and_unknown_version_fails(self) -> None:
        payload = _result().to_dict()
        payload["schema_version"] = "1.1"

        with self.assertRaisesRegex(ValueError, "不支持 DetectionResult schema"):
            DetectionResult.from_dict(payload)

        del payload["schema_version"]
        with self.assertRaisesRegex(ValueError, "不支持 DetectionResult schema"):
            DetectionResult.from_dict(payload)

    def test_created_at_must_be_timezone_aware(self) -> None:
        with self.assertRaisesRegex(ValueError, "created_at 必须包含时区"):
            _result(created_at=datetime(2026, 7, 19, 6, 0))

    def test_confidence_is_float_in_closed_unit_interval(self) -> None:
        self.assertEqual(_result(confidence=1).confidence, 1.0)
        self.assertIsInstance(_result(confidence=1).confidence, float)

        for invalid in (-0.01, 1.01, 85):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(ValueError, r"必须在 \[0, 1\]"):
                    _result(confidence=invalid)

        with self.assertRaisesRegex(ValueError, r"必须在 \[0, 1\]"):
            PatternState(name="armed", confidence=1.1)

    def test_tags_are_standard_enum_or_custom_prefix(self) -> None:
        self.assertEqual(
            _result(tags=(DetectorTag.BREAKOUT, "custom:session_open")).tags,
            (DetectorTag.BREAKOUT, "custom:session_open"),
        )

        for invalid in ("Compression", "compress", "custom:"):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(ValueError, "DetectorTag"):
                    _result(tags=(invalid,))

    def test_production_requires_evidence_reference(self) -> None:
        with self.assertRaisesRegex(ValueError, "必须包含 evidence_refs"):
            _result(
                status=DetectorStatus.PRODUCTION,
                evidence_refs=(),
            )

        production = _result(
            status=DetectorStatus.PRODUCTION,
            evidence_refs=("EXP-021", "EXP-035"),
        )
        self.assertEqual(production.evidence_refs, ("EXP-021", "EXP-035"))

    def test_direction_none_means_no_detection(self) -> None:
        with self.assertRaisesRegex(ValueError, "无检测请返回 None"):
            _result(direction=Direction.NONE)

    def test_metadata_rejects_non_json_value(self) -> None:
        with self.assertRaisesRegex(TypeError, "JSON 兼容值"):
            _result(metadata={"bad": object()})


if __name__ == "__main__":
    unittest.main()
