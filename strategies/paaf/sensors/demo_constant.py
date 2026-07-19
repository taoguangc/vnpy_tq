"""Non-alpha fixture Sensor proving the Phase 3.0 execution contract."""

from __future__ import annotations

from datetime import datetime
import math
from typing import Any, Mapping

from strategies.paaf.sensors.base import BaseFeatureSensor, ParameterValue
from strategies.paaf.sensors.models import (
    FeatureResult,
    SensorCapability,
    SensorDescriptor,
    SensorStatus,
)


DEMO_SENSOR_ID = "demo_constant"
DEMO_SENSOR_VERSION = "1.0"
DEMO_OUTPUT_KEY = "fixture_value"


class DemoConstantSensor(BaseFeatureSensor):
    """Always emits a caller-controlled constant; not a research hypothesis."""

    sensor_id = DEMO_SENSOR_ID
    sensor_version = DEMO_SENSOR_VERSION

    def observe(
        self,
        *,
        symbol: str,
        timeframe: str,
        timestamp: datetime,
        window: Mapping[str, Any],
        context: Any | None = None,
        parameters: Mapping[str, ParameterValue] | None = None,
    ) -> FeatureResult:
        del context
        parameter_values = parameters or {}
        raw_value = parameter_values.get("fixture_value", 1.0)
        if isinstance(raw_value, bool) or not isinstance(
            raw_value,
            (int, float),
        ):
            raise TypeError("fixture_value 必须是 int 或 float")
        value = float(raw_value)
        if not math.isfinite(value):
            raise ValueError("fixture_value 必须是有限数值")

        warmup_state = "ready" if window else "partial"
        return FeatureResult(
            sensor_id=self.sensor_id,
            sensor_version=self.sensor_version,
            symbol=symbol,
            timeframe=timeframe,
            timestamp=timestamp,
            values={DEMO_OUTPUT_KEY: value},
            diagnostics={"warmup_state": warmup_state},
        )


DEMO_CONSTANT_DESCRIPTOR = SensorDescriptor(
    sensor_id=DEMO_SENSOR_ID,
    sensor_version=DEMO_SENSOR_VERSION,
    status=SensorStatus.EXPERIMENT,
    capability=SensorCapability(
        requires=("window",),
        produces=(DEMO_OUTPUT_KEY,),
        timeframe="1m",
        emit_mode="always",
    ),
    factory=DemoConstantSensor,
    output_schema=(DEMO_OUTPUT_KEY,),
    parameter_schema=("fixture_value",),
)
