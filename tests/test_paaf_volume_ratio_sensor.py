"""Volume Ratio EXP001 Sensor contract tests."""

from __future__ import annotations

from datetime import datetime, timezone
import unittest

from strategies.paaf.sensors import (
    VOLUME_OUTPUT_KEY,
    VOLUME_RATIO_DESCRIPTOR,
    SensorStatus,
    VolumeRatioSensor,
)


TIMESTAMP = datetime(2026, 7, 19, 10, 0, tzinfo=timezone.utc)


class TestVolumeRatioSensor(unittest.TestCase):
    def setUp(self) -> None:
        self.sensor = VolumeRatioSensor()

    def test_descriptor_is_experiment_observation_only(self) -> None:
        descriptor = VOLUME_RATIO_DESCRIPTOR

        self.assertEqual(descriptor.sensor_id, "volume_ratio")
        self.assertEqual(descriptor.sensor_version, "1.0")
        self.assertIs(descriptor.status, SensorStatus.EXPERIMENT)
        self.assertEqual(descriptor.capability.requires, ("volume",))
        self.assertEqual(descriptor.output_schema, ("volume_ratio",))

    def test_ratio_uses_current_in_inclusive_baseline(self) -> None:
        result = self.sensor.observe(
            symbol="rb888",
            timeframe="1m",
            timestamp=TIMESTAMP,
            window={
                "volume": (10.0, 20.0, 30.0),
                "roll_neighborhood": False,
            },
            parameters={"baseline_window": 3},
        )

        self.assertAlmostEqual(result.values[VOLUME_OUTPUT_KEY], 1.5)
        self.assertEqual(result.diagnostics["calculation_status"], "ok")
        self.assertEqual(result.diagnostics["roll_neighborhood"], "false")

    def test_warmup_emits_null_and_roll_annotation(self) -> None:
        result = self.sensor.observe(
            symbol="rb888",
            timeframe="1m",
            timestamp=TIMESTAMP,
            window={
                "volume": (10.0,),
                "roll_neighborhood": True,
            },
            parameters={"baseline_window": 2},
        )

        self.assertIsNone(result.values[VOLUME_OUTPUT_KEY])
        self.assertEqual(result.diagnostics["warmup_state"], "insufficient")
        self.assertEqual(result.diagnostics["roll_neighborhood"], "true")

    def test_zero_baseline_emits_null(self) -> None:
        result = self.sensor.observe(
            symbol="rb888",
            timeframe="1m",
            timestamp=TIMESTAMP,
            window={"volume": (0.0, 0.0)},
            parameters={"baseline_window": 2},
        )

        self.assertIsNone(result.values[VOLUME_OUTPUT_KEY])
        self.assertEqual(
            result.diagnostics["calculation_status"],
            "zero_baseline",
        )

    def test_invalid_inputs_fail_explicitly(self) -> None:
        with self.assertRaisesRegex(ValueError, "仅允许 rb"):
            self.sensor.observe(
                symbol="hc888",
                timeframe="1m",
                timestamp=TIMESTAMP,
                window={"volume": ()},
            )
        with self.assertRaisesRegex(ValueError, "有限非负"):
            self.sensor.observe(
                symbol="rb888",
                timeframe="1m",
                timestamp=TIMESTAMP,
                window={"volume": (-1.0,)},
            )
        with self.assertRaisesRegex(TypeError, "roll_neighborhood"):
            self.sensor.observe(
                symbol="rb888",
                timeframe="1m",
                timestamp=TIMESTAMP,
                window={"volume": (), "roll_neighborhood": "false"},
            )


if __name__ == "__main__":
    unittest.main()
