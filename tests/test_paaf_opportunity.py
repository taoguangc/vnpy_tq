"""Opportunity domain contract tests（v0.2.2）。"""

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
    MarketState,
    Opportunity,
    OpportunityDirection,
)


def _detection(**overrides: object) -> DetectionResult:
    values: dict[str, object] = {
        "detector_id": "TwoBarReversalDetector",
        "detector_version": "1.0",
        "opportunity_id": "OPP16",
        "status": DetectorStatus.EXPERIMENT,
        "direction": Direction.LONG,
        "confidence": 0.82,
        "tags": (DetectorTag.REVERSAL,),
        "metadata": {"bars": 2},
        "evidence_refs": ("EXP-021",),
        "created_at": datetime(2026, 7, 19, 6, 0, tzinfo=timezone.utc),
    }
    values.update(overrides)
    return DetectionResult(**values)  # type: ignore[arg-type]


def _opportunity(**overrides: object) -> Opportunity:
    detection = overrides.pop("detector_result", _detection())
    values: dict[str, object] = {
        "id": "OPP16",
        "version": "1.0",
        "status": DetectorStatus.EXPERIMENT,
        "direction": OpportunityDirection.LONG,
        "market_state": MarketState.UNKNOWN,
        "detector_result": detection,
        "evidence_refs": ("EXP-021",),
        "metadata": {
            "source": "unit-test",
            "nested": {"bars": [1, 2]},
        },
        "lineage": (
            "DET:TwoBarReversalDetector@1.0",
            "EXP:EXP-021",
        ),
        "created_at": datetime(2026, 7, 19, 6, 1, tzinfo=timezone.utc),
        "schema_version": "1.0",
    }
    values.update(overrides)
    return Opportunity(**values)  # type: ignore[arg-type]


class TestOpportunityContract(unittest.TestCase):
    def test_is_immutable_and_keeps_detection_result_reference(self) -> None:
        detection = _detection()
        opportunity = _opportunity(detector_result=detection)

        self.assertIs(opportunity.detector_result, detection)
        with self.assertRaises(FrozenInstanceError):
            opportunity.status = DetectorStatus.PRODUCTION  # type: ignore[misc]

    def test_metadata_is_deeply_readonly(self) -> None:
        opportunity = _opportunity()

        with self.assertRaises(TypeError):
            opportunity.metadata["source"] = "changed"  # type: ignore[index]
        with self.assertRaises(TypeError):
            opportunity.metadata["nested"]["bars"] = []  # type: ignore[index]

    def test_json_serialization_round_trip_is_equal(self) -> None:
        original = _opportunity()

        payload = original.to_dict()
        encoded = json.dumps(payload, ensure_ascii=False)
        restored = Opportunity.from_dict(json.loads(encoded))

        self.assertEqual(restored, original)
        self.assertEqual(payload["id"], "OPP16")
        self.assertEqual(payload["direction"], "LONG")
        self.assertEqual(payload["market_state"], "UNKNOWN")
        self.assertEqual(
            payload["detector_result"]["detector_id"],
            "TwoBarReversalDetector",
        )
        self.assertEqual(
            payload["lineage"],
            ["DET:TwoBarReversalDetector@1.0", "EXP:EXP-021"],
        )

    def test_business_id_rejects_uuid_hash_and_free_text(self) -> None:
        for invalid in (
            "550e8400-e29b-41d4-a716-446655440000",
            "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3",
            "breakout",
            "OPP001",
        ):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(ValueError, "OPPXX"):
                    _opportunity(id=invalid)

        demo_detection = _detection(opportunity_id="DEMO_BREAKOUT")
        demo = _opportunity(
            id="DEMO_BREAKOUT",
            detector_result=demo_detection,
        )
        self.assertEqual(demo.id, "DEMO_BREAKOUT")

    def test_detection_result_opportunity_id_must_match(self) -> None:
        with self.assertRaisesRegex(ValueError, "opportunity_id"):
            _opportunity(detector_result=_detection(opportunity_id="OPP03"))

    def test_direction_alignment_for_long_and_short(self) -> None:
        with self.assertRaisesRegex(ValueError, "direction 不一致"):
            _opportunity(direction=OpportunityDirection.SHORT)

        both = _opportunity(direction=OpportunityDirection.BOTH)
        unknown = _opportunity(direction=OpportunityDirection.UNKNOWN)
        self.assertEqual(both.direction, OpportunityDirection.BOTH)
        self.assertEqual(unknown.direction, OpportunityDirection.UNKNOWN)

    def test_lineage_covers_detector_and_all_evidence(self) -> None:
        with self.assertRaisesRegex(ValueError, "直接来源"):
            _opportunity(lineage=("EXP:EXP-021",))

        with self.assertRaisesRegex(ValueError, "evidence 来源"):
            _opportunity(lineage=("DET:TwoBarReversalDetector@1.0",))

        with self.assertRaisesRegex(ValueError, "必须覆盖"):
            _opportunity(evidence_refs=(), lineage=(
                "DET:TwoBarReversalDetector@1.0",
            ))

    def test_production_requires_evidence(self) -> None:
        detection = _detection(evidence_refs=())
        with self.assertRaisesRegex(ValueError, "必须包含 evidence_refs"):
            _opportunity(
                status=DetectorStatus.PRODUCTION,
                detector_result=detection,
                evidence_refs=(),
                lineage=("DET:TwoBarReversalDetector@1.0",),
            )

    def test_schema_version_and_timezone_are_explicit(self) -> None:
        payload = _opportunity().to_dict()
        payload["schema_version"] = "1.1"
        with self.assertRaisesRegex(ValueError, "不支持 Opportunity schema"):
            Opportunity.from_dict(payload)

        with self.assertRaisesRegex(ValueError, "必须包含时区"):
            _opportunity(created_at=datetime(2026, 7, 19, 6, 1))

    def test_market_state_may_be_none(self) -> None:
        original = _opportunity(market_state=None)
        restored = Opportunity.from_dict(original.to_dict())

        self.assertIsNone(restored.market_state)
        self.assertEqual(restored, original)


if __name__ == "__main__":
    unittest.main()
