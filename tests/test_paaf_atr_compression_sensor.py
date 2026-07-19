"""ATR Compression Phase 3.1 Feature Sensor contract tests."""

from __future__ import annotations

from datetime import datetime, timezone
import unittest

from strategies.paaf.sensors import (
    ATR_COMPRESSION_DESCRIPTOR,
    ATR_OUTPUT_KEY,
    ATRCompressionSensor,
    SensorStatus,
)


TIMESTAMP = datetime(2026, 7, 19, 10, 0, tzinfo=timezone.utc)
FORBIDDEN_KEYS = {
    "action",
    "breakout_probability",
    "compression_score",
    "direction",
    "signal",
    "weight",
}


def _window(
    widths: tuple[float, ...],
    *,
    rollover_flag: bool = False,
) -> dict[str, object]:
    return {
        "high": tuple(100.0 + width / 2 for width in widths),
        "low": tuple(100.0 - width / 2 for width in widths),
        "close": (100.0,) * len(widths),
        "rollover_flag": rollover_flag,
    }


class TestATRCompressionSensor(unittest.TestCase):
    def setUp(self) -> None:
        self.sensor = ATRCompressionSensor()

    def test_descriptor_is_experiment_rb_1m_contract(self) -> None:
        descriptor = ATR_COMPRESSION_DESCRIPTOR

        self.assertEqual(descriptor.sensor_id, "atr_compression")
        self.assertEqual(descriptor.sensor_version, "1.0")
        self.assertIs(descriptor.status, SensorStatus.EXPERIMENT)
        self.assertEqual(descriptor.capability.timeframe, "1m")
        self.assertEqual(descriptor.capability.emit_mode, "always")
        self.assertEqual(descriptor.output_schema, ("atr_ratio",))
        self.assertNotIn("compression_score", descriptor.output_schema)

        with self.assertRaisesRegex(ValueError, "仅允许 rb"):
            self.sensor.observe(
                symbol="hc888",
                timeframe="1m",
                timestamp=TIMESTAMP,
                window={},
            )
        with self.assertRaisesRegex(ValueError, "仅允许 1m"):
            self.sensor.observe(
                symbol="rb888",
                timeframe="5m",
                timestamp=TIMESTAMP,
                window={},
            )

    def test_atr_ratio_is_deterministic_and_matches_definition(self) -> None:
        kwargs = {
            "symbol": "rb888",
            "timeframe": "1m",
            "timestamp": TIMESTAMP,
            "window": _window((2.0, 2.0, 2.0, 2.0, 4.0)),
            "parameters": {"atr_period": 2, "baseline_window": 3},
        }

        first = self.sensor.observe(**kwargs)
        second = self.sensor.observe(**kwargs)

        self.assertEqual(first, second)
        self.assertAlmostEqual(first.values[ATR_OUTPUT_KEY], 9 / 7)
        self.assertEqual(first.diagnostics["warmup_state"], "ready")
        self.assertEqual(first.diagnostics["calculation_status"], "ok")

    def test_warmup_always_emits_null_and_rollover_fact(self) -> None:
        result = self.sensor.observe(
            symbol="rb888",
            timeframe="1m",
            timestamp=TIMESTAMP,
            window=_window((2.0,), rollover_flag=True),
        )

        self.assertIsNone(result.values[ATR_OUTPUT_KEY])
        self.assertEqual(result.schema_version, "2.0")
        self.assertEqual(result.diagnostics["warmup_state"], "insufficient")
        self.assertEqual(result.diagnostics["rollover_flag"], "true")
        with self.assertRaises(TypeError):
            result.values[ATR_OUTPUT_KEY] = 1.0  # type: ignore[index]

    def test_result_has_only_feature_observation_fields(self) -> None:
        result = self.sensor.observe(
            symbol="rb888",
            timeframe="1m",
            timestamp=TIMESTAMP,
            window=_window((2.0,) * 114),
        )
        payload = result.to_dict()
        all_output_keys = set(payload["values"]) | set(payload["diagnostics"])

        self.assertEqual(set(payload["values"]), {"atr_ratio"})
        self.assertTrue(FORBIDDEN_KEYS.isdisjoint(all_output_keys))

    def test_zero_baseline_returns_null_not_nan(self) -> None:
        result = self.sensor.observe(
            symbol="rb888",
            timeframe="1m",
            timestamp=TIMESTAMP,
            window=_window((0.0,) * 114),
        )

        self.assertIsNone(result.values[ATR_OUTPUT_KEY])
        self.assertEqual(
            result.diagnostics["calculation_status"],
            "zero_baseline",
        )


if __name__ == "__main__":
    unittest.main()
