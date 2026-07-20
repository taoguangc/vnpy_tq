"""Close Location EXP001 Sensor contract tests."""

from __future__ import annotations

from datetime import datetime, timezone
import unittest

from strategies.paaf.sensors import (
    CLOSE_LOCATION_DESCRIPTOR,
    CLOSE_OUTPUT_KEY,
    CloseLocationSensor,
    SensorStatus,
)


TIMESTAMP = datetime(2026, 7, 19, 10, 0, tzinfo=timezone.utc)


class TestCloseLocationSensor(unittest.TestCase):
    def setUp(self) -> None:
        self.sensor = CloseLocationSensor()

    def test_descriptor_is_experiment_observation_only(self) -> None:
        descriptor = CLOSE_LOCATION_DESCRIPTOR

        self.assertEqual(descriptor.sensor_id, "close_location")
        self.assertEqual(descriptor.sensor_version, "1.0")
        self.assertIs(descriptor.status, SensorStatus.EXPERIMENT)
        self.assertEqual(
            descriptor.capability.requires,
            ("high", "low", "close"),
        )
        self.assertEqual(descriptor.output_schema, ("close_location",))

    def test_location_matches_frozen_definition(self) -> None:
        result = self.sensor.observe(
            symbol="rb888",
            timeframe="1m",
            timestamp=TIMESTAMP,
            window={
                "high": (110.0,),
                "low": (100.0,),
                "close": (107.0,),
                "roll_neighborhood": False,
            },
        )

        self.assertAlmostEqual(result.values[CLOSE_OUTPUT_KEY], 0.7)
        self.assertEqual(result.diagnostics["calculation_status"], "ok")

    def test_zero_range_and_roll_annotation(self) -> None:
        zero_range = self.sensor.observe(
            symbol="rb888",
            timeframe="1m",
            timestamp=TIMESTAMP,
            window={
                "high": (100.0,),
                "low": (100.0,),
                "close": (100.0,),
                "roll_neighborhood": True,
            },
        )

        self.assertIsNone(zero_range.values[CLOSE_OUTPUT_KEY])
        self.assertEqual(
            zero_range.diagnostics["calculation_status"],
            "zero_range",
        )
        self.assertEqual(
            zero_range.diagnostics["roll_neighborhood"],
            "true",
        )

    def test_invalid_inputs_fail_explicitly(self) -> None:
        with self.assertRaisesRegex(ValueError, "仅允许 rb"):
            self.sensor.observe(
                symbol="hc888",
                timeframe="1m",
                timestamp=TIMESTAMP,
                window={},
            )
        with self.assertRaisesRegex(ValueError, "high 不得小于 low"):
            self.sensor.observe(
                symbol="rb888",
                timeframe="1m",
                timestamp=TIMESTAMP,
                window={
                    "high": (99.0,),
                    "low": (100.0,),
                    "close": (99.5,),
                },
            )
        with self.assertRaisesRegex(TypeError, "roll_neighborhood"):
            self.sensor.observe(
                symbol="rb888",
                timeframe="1m",
                timestamp=TIMESTAMP,
                window={
                    "high": (101.0,),
                    "low": (100.0,),
                    "close": (100.5,),
                    "roll_neighborhood": "false",
                },
            )


if __name__ == "__main__":
    unittest.main()
