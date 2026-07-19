"""Feature Sensor Framework Phase 3.0 contract tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path

from strategies.paaf.domain import DetectionResult, Opportunity
from strategies.paaf.sensors import (
    DEMO_CONSTANT_DESCRIPTOR,
    BaseFeatureSensor,
    DemoConstantSensor,
    FeatureResult,
    SensorCapability,
    SensorDescriptor,
    SensorRegistry,
    SensorStatus,
    write_feature_artifact,
)


TIMESTAMP = datetime(2026, 7, 19, 10, 0, tzinfo=timezone.utc)


def _result(**overrides: object) -> FeatureResult:
    values: dict[str, object] = {
        "sensor_id": "fixture_sensor",
        "sensor_version": "1.0",
        "symbol": "rb888",
        "timeframe": "1m",
        "timestamp": TIMESTAMP,
        "values": {"fixture_value": 0.5},
        "diagnostics": {"warmup_state": "ready"},
    }
    values.update(overrides)
    return FeatureResult(**values)  # type: ignore[arg-type]


def _descriptor(**overrides: object) -> SensorDescriptor:
    values: dict[str, object] = {
        "sensor_id": "fixture_sensor",
        "sensor_version": "1.0",
        "status": SensorStatus.EXPERIMENT,
        "capability": SensorCapability(
            requires=("window",),
            produces=("fixture_value",),
            timeframe="1m",
        ),
        "factory": DemoConstantSensor,
        "output_schema": ("fixture_value",),
        "parameter_schema": ("fixture_value",),
    }
    values.update(overrides)
    return SensorDescriptor(**values)  # type: ignore[arg-type]


class TestFeatureResult(unittest.TestCase):
    def test_is_immutable_and_mappings_are_defensively_readonly(self) -> None:
        source_values = {"fixture_value": 0.5}
        result = _result(values=source_values)
        source_values["fixture_value"] = 9.0

        self.assertEqual(result.values["fixture_value"], 0.5)
        with self.assertRaises(FrozenInstanceError):
            result.symbol = "hc888"  # type: ignore[misc]
        with self.assertRaises(TypeError):
            result.values["fixture_value"] = 1.0  # type: ignore[index]
        with self.assertRaises(TypeError):
            result.diagnostics["warmup_state"] = "partial"  # type: ignore[index]

    def test_json_round_trip_preserves_identity(self) -> None:
        original = _result()
        payload = json.loads(json.dumps(original.to_dict()))
        restored = FeatureResult.from_dict(payload)

        self.assertEqual(restored, original)
        self.assertEqual(payload["sensor_version"], "1.0")
        self.assertEqual(payload["timestamp"], TIMESTAMP.isoformat())

    def test_has_no_direction_status_or_experiment_fields(self) -> None:
        fields = FeatureResult.__dataclass_fields__
        self.assertNotIn("direction", fields)
        self.assertNotIn("status", fields)
        self.assertNotIn("experiment_id", fields)
        self.assertNotIn("evidence_id", fields)

    def test_forbidden_business_keys_are_rejected(self) -> None:
        for key in (
            "direction",
            "action",
            "weight",
            "experiment_id",
            "pipeline_status",
        ):
            with self.subTest(key=key):
                with self.assertRaisesRegex(ValueError, "禁止"):
                    _result(values={key: 1.0})

    def test_schema_timestamp_and_value_types_are_validated(self) -> None:
        with self.assertRaisesRegex(ValueError, "时区"):
            _result(timestamp=datetime(2026, 7, 19, 10, 0))
        with self.assertRaisesRegex(ValueError, "schema"):
            _result(schema_version="2.0")
        with self.assertRaisesRegex(TypeError, "int 或 float"):
            _result(values={"fixture_value": True})
        with self.assertRaisesRegex(ValueError, "有限"):
            _result(values={"fixture_value": float("nan")})


class TestSensorContracts(unittest.TestCase):
    def test_sensor_status_is_independent_and_complete(self) -> None:
        self.assertEqual(
            {item.value for item in SensorStatus},
            {
                "EXPERIMENT",
                "VALIDATED",
                "CANDIDATE",
                "PRODUCTION",
                "DEPRECATED",
            },
        )

    def test_capability_has_no_directions(self) -> None:
        capability = SensorCapability(produces=("fixture_value",))
        self.assertFalse(hasattr(capability, "directions"))
        with self.assertRaisesRegex(ValueError, "emit_mode"):
            SensorCapability(emit_mode="conditional")

    def test_production_descriptor_requires_evidence(self) -> None:
        with self.assertRaisesRegex(ValueError, "evidence_refs"):
            _descriptor(status=SensorStatus.PRODUCTION)

        production = _descriptor(
            status=SensorStatus.PRODUCTION,
            evidence_refs=("EV-001",),
        )
        self.assertEqual(production.evidence_refs, ("EV-001",))

    def test_descriptor_factory_must_return_base_sensor(self) -> None:
        descriptor = _descriptor(factory=lambda: object())
        with self.assertRaisesRegex(TypeError, "BaseFeatureSensor"):
            descriptor.create()


class TestSensorRegistryAndDemo(unittest.TestCase):
    def test_registry_uses_id_version_key_and_supports_versions(self) -> None:
        registry = SensorRegistry()
        first = registry.register(_descriptor())
        second = registry.register(
            _descriptor(sensor_version="2.0")
        )

        self.assertIs(registry.get("fixture_sensor", "1.0"), first)
        self.assertIs(registry.get("fixture_sensor", "2.0"), second)
        self.assertTrue(registry.exists("fixture_sensor", "2.0"))
        self.assertEqual(len(registry.list()), 2)

    def test_registry_rejects_duplicate_and_non_descriptor(self) -> None:
        registry = SensorRegistry()
        registry.register(_descriptor())
        with self.assertRaisesRegex(ValueError, "已注册"):
            registry.register(_descriptor())
        with self.assertRaisesRegex(TypeError, "SensorDescriptor"):
            registry.register(DemoConstantSensor())  # type: ignore[arg-type]

    def test_registry_find_and_create_are_sensor_only(self) -> None:
        registry = SensorRegistry()
        registry.register(DEMO_CONSTANT_DESCRIPTOR)

        matches = registry.find(
            status=SensorStatus.EXPERIMENT,
            produces=("fixture_value",),
        )
        self.assertEqual(matches, (DEMO_CONSTANT_DESCRIPTOR,))
        self.assertIsInstance(
            registry.create("demo_constant", "1.0"),
            BaseFeatureSensor,
        )
        with self.assertRaises(KeyError):
            registry.create("missing", "1.0")

    def test_demo_always_emits_deterministically_with_warmup_diagnostic(
        self,
    ) -> None:
        sensor = DemoConstantSensor()
        kwargs = {
            "symbol": "rb888",
            "timeframe": "1m",
            "timestamp": TIMESTAMP,
            "window": {},
            "parameters": {"fixture_value": 0.75},
        }
        first = sensor.observe(**kwargs)
        second = sensor.observe(**kwargs)

        self.assertEqual(first, second)
        self.assertEqual(first.values["fixture_value"], 0.75)
        self.assertEqual(first.diagnostics["warmup_state"], "partial")
        self.assertNotIsInstance(first, DetectionResult)
        self.assertNotIsInstance(first, Opportunity)

        ready = sensor.observe(**{**kwargs, "window": {"bars": (1, 2)}})
        self.assertEqual(ready.diagnostics["warmup_state"], "ready")


class TestFeatureArtifact(unittest.TestCase):
    def test_jsonl_artifact_hash_is_stable_and_content_is_replayable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results = (_result(), _result(timestamp=TIMESTAMP.replace(minute=1)))
            left_path = root / "left" / "features.jsonl"
            right_path = root / "right" / "features.jsonl"

            left = write_feature_artifact(
                left_path,
                results,
                artifact_id="features-left",
                uri="artifacts/features-left/features.jsonl",
            )
            right = write_feature_artifact(
                right_path,
                results,
                artifact_id="features-right",
                uri="artifacts/features-right/features.jsonl",
            )

            self.assertEqual(left.content_hash, right.content_hash)
            restored = tuple(
                FeatureResult.from_dict(json.loads(line))
                for line in left_path.read_text(encoding="utf-8").splitlines()
            )
            self.assertEqual(restored, results)

    def test_artifact_is_create_once_and_requires_results(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "features.jsonl"
            with self.assertRaisesRegex(ValueError, "至少"):
                write_feature_artifact(
                    path,
                    (),
                    artifact_id="empty",
                    uri="artifacts/empty/features.jsonl",
                )

            write_feature_artifact(
                path,
                (_result(),),
                artifact_id="features-001",
                uri="artifacts/features-001/features.jsonl",
            )
            with self.assertRaises(FileExistsError):
                write_feature_artifact(
                    path,
                    (_result(),),
                    artifact_id="features-001",
                    uri="artifacts/features-001/features.jsonl",
                )


if __name__ == "__main__":
    unittest.main()
