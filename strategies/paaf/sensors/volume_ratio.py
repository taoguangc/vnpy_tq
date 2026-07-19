"""Relative-volume experiment Sensor; observations only, never trading."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime
import math
from typing import Any

from strategies.paaf.sensors.base import BaseFeatureSensor, ParameterValue
from strategies.paaf.sensors.models import (
    FeatureResult,
    SensorCapability,
    SensorDescriptor,
    SensorStatus,
)


VOLUME_SENSOR_ID = "volume_ratio"
VOLUME_SENSOR_VERSION = "1.0"
VOLUME_OUTPUT_KEY = "volume_ratio"
DEFAULT_VOLUME_BASELINE_WINDOW = 100


def _volume_series(window: Mapping[str, Any]) -> tuple[float, ...]:
    raw = window.get("volume", ())
    if (
        isinstance(raw, (str, bytes, Mapping))
        or not isinstance(raw, Iterable)
    ):
        raise TypeError("window['volume'] 必须是数值序列")

    values: list[float] = []
    for item in raw:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise TypeError("window['volume'] 必须是数值序列")
        value = float(item)
        if not math.isfinite(value) or value < 0:
            raise ValueError("window['volume'] 必须包含有限非负数值")
        values.append(value)
    return tuple(values)


class VolumeRatioSensor(BaseFeatureSensor):
    """Observe current volume relative to its inclusive rolling mean."""

    sensor_id = VOLUME_SENSOR_ID
    sensor_version = VOLUME_SENSOR_VERSION

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
        if not symbol.lower().startswith("rb"):
            raise ValueError("Volume Ratio v1 实验仅允许 rb")
        if timeframe != "1m":
            raise ValueError("Volume Ratio v1 实验仅允许 1m")

        parameter_values = parameters or {}
        baseline_window = parameter_values.get(
            "baseline_window",
            DEFAULT_VOLUME_BASELINE_WINDOW,
        )
        if (
            isinstance(baseline_window, bool)
            or not isinstance(baseline_window, int)
            or baseline_window <= 0
        ):
            raise ValueError("baseline_window 必须是正整数")

        roll_neighborhood = window.get("roll_neighborhood", False)
        if not isinstance(roll_neighborhood, bool):
            raise TypeError("window['roll_neighborhood'] 必须是 bool")

        volumes = _volume_series(window)
        diagnostics = {
            "baseline_window": str(baseline_window),
            "roll_neighborhood": str(roll_neighborhood).lower(),
        }
        if len(volumes) < baseline_window:
            diagnostics["warmup_state"] = "insufficient"
            return self._result(
                symbol,
                timeframe,
                timestamp,
                None,
                diagnostics,
            )

        diagnostics["warmup_state"] = "ready"
        baseline = math.fsum(volumes[-baseline_window:]) / baseline_window
        if baseline == 0.0:
            diagnostics["calculation_status"] = "zero_baseline"
            return self._result(
                symbol,
                timeframe,
                timestamp,
                None,
                diagnostics,
            )

        diagnostics["calculation_status"] = "ok"
        return self._result(
            symbol,
            timeframe,
            timestamp,
            volumes[-1] / baseline,
            diagnostics,
        )

    def _result(
        self,
        symbol: str,
        timeframe: str,
        timestamp: datetime,
        value: float | None,
        diagnostics: Mapping[str, str],
    ) -> FeatureResult:
        return FeatureResult(
            sensor_id=self.sensor_id,
            sensor_version=self.sensor_version,
            symbol=symbol,
            timeframe=timeframe,
            timestamp=timestamp,
            values={VOLUME_OUTPUT_KEY: value},
            diagnostics=diagnostics,
        )


VOLUME_RATIO_DESCRIPTOR = SensorDescriptor(
    sensor_id=VOLUME_SENSOR_ID,
    sensor_version=VOLUME_SENSOR_VERSION,
    status=SensorStatus.EXPERIMENT,
    capability=SensorCapability(
        requires=("volume",),
        produces=(VOLUME_OUTPUT_KEY,),
        timeframe="1m",
        emit_mode="always",
    ),
    factory=VolumeRatioSensor,
    output_schema=(VOLUME_OUTPUT_KEY,),
    parameter_schema=("baseline_window",),
)
