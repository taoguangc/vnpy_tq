"""OI Change EXP001 Sensor contract tests."""

from __future__ import annotations

from datetime import datetime, timezone
import unittest

from strategies.paaf.sensors import (
    OI_CHANGE_DESCRIPTOR,
    OI_OUTPUT_KEY,
    OIChangeSensor,
    SensorStatus,
)


TIMESTAMP = datetime(2026, 7, 19, 10, 0, tzinfo=timezone.utc)


class TestOIChangeSensor(unittest.TestCase):
    def setUp(self) -> None:
        self.sensor = OIChangeSensor()

    def test_descriptor_is_experiment_observation_only(self) -> None:
        descriptor = OI_CHANGE_DESCRIPTOR

        self.assertEqual(descriptor.sensor_id, "oi_change")
        self.assertEqual(descriptor.sensor_version, "1.0")
        self.assertIs(descriptor.status, SensorStatus.EXPERIMENT)
        self.assertEqual(descriptor.capability.requires, ("open_interest",))
        self.assertEqual(descriptor.output_schema, ("oi_rel_change",))

    def test_relative_change_matches_frozen_definition(self) -> None:
        result = self.sensor.observe(
            symbol="rb888",
            timeframe="1m",
            timestamp=TIMESTAMP,
            window={
                "open_interest": (100.0, 105.0),
                "roll_neighborhood": False,
            },
        )

        self.assertAlmostEqual(result.values[OI_OUTPUT_KEY], 0.05)
        self.assertEqual(result.diagnostics["calculation_status"], "ok")

    def test_warmup_and_zero_previous_emit_null(self) -> None:
        warmup = self.sensor.observe(
            symbol="rb888",
            timeframe="1m",
            timestamp=TIMESTAMP,
            window={"open_interest": (100.0,), "roll_neighborhood": True},
        )
        zero_previous = self.sensor.observe(
            symbol="rb888",
            timeframe="1m",
            timestamp=TIMESTAMP,
            window={"open_interest": (0.0, 5.0)},
        )

        self.assertIsNone(warmup.values[OI_OUTPUT_KEY])
        self.assertEqual(warmup.diagnostics["roll_neighborhood"], "true")
        self.assertIsNone(zero_previous.values[OI_OUTPUT_KEY])
        self.assertEqual(
            zero_previous.diagnostics["calculation_status"],
            "nonpositive_prev_oi",
        )

    def test_invalid_inputs_fail_explicitly(self) -> None:
        with self.assertRaisesRegex(ValueError, "仅允许 rb"):
            self.sensor.observe(
                symbol="hc888",
                timeframe="1m",
                timestamp=TIMESTAMP,
                window={"open_interest": ()},
            )
        with self.assertRaisesRegex(ValueError, "有限非负"):
            self.sensor.observe(
                symbol="rb888",
                timeframe="1m",
                timestamp=TIMESTAMP,
                window={"open_interest": (-1.0,)},
            )
        with self.assertRaisesRegex(TypeError, "roll_neighborhood"):
            self.sensor.observe(
                symbol="rb888",
                timeframe="1m",
                timestamp=TIMESTAMP,
                window={
                    "open_interest": (),
                    "roll_neighborhood": "false",
                },
            )


if __name__ == "__main__":
    unittest.main()
