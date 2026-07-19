"""Open-interest change experiment Sensor; observations only."""

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


OI_SENSOR_ID = "oi_change"
OI_SENSOR_VERSION = "1.0"
OI_OUTPUT_KEY = "oi_rel_change"


def _oi_series(window: Mapping[str, Any]) -> tuple[float, ...]:
    raw = window.get("open_interest", ())
    if (
        isinstance(raw, (str, bytes, Mapping))
        or not isinstance(raw, Iterable)
    ):
        raise TypeError("window['open_interest'] 必须是数值序列")

    values: list[float] = []
    for item in raw:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise TypeError("window['open_interest'] 必须是数值序列")
        value = float(item)
        if not math.isfinite(value) or value < 0:
            raise ValueError("window['open_interest'] 必须包含有限非负数值")
        values.append(value)
    return tuple(values)


class OIChangeSensor(BaseFeatureSensor):
    """Observe one-bar relative open-interest change."""

    sensor_id = OI_SENSOR_ID
    sensor_version = OI_SENSOR_VERSION

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
        del context, parameters
        if not symbol.lower().startswith("rb"):
            raise ValueError("OI Change v1 实验仅允许 rb")
        if timeframe != "1m":
            raise ValueError("OI Change v1 实验仅允许 1m")

        roll_neighborhood = window.get("roll_neighborhood", False)
        if not isinstance(roll_neighborhood, bool):
            raise TypeError("window['roll_neighborhood'] 必须是 bool")
        values = _oi_series(window)
        diagnostics = {
            "roll_neighborhood": str(roll_neighborhood).lower(),
        }
        if len(values) < 2:
            diagnostics["warmup_state"] = "insufficient"
            return self._result(
                symbol,
                timeframe,
                timestamp,
                None,
                diagnostics,
            )

        diagnostics["warmup_state"] = "ready"
        previous = values[-2]
        if previous <= 0:
            diagnostics["calculation_status"] = "nonpositive_prev_oi"
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
            (values[-1] - previous) / previous,
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
            values={OI_OUTPUT_KEY: value},
            diagnostics=diagnostics,
        )


OI_CHANGE_DESCRIPTOR = SensorDescriptor(
    sensor_id=OI_SENSOR_ID,
    sensor_version=OI_SENSOR_VERSION,
    status=SensorStatus.EXPERIMENT,
    capability=SensorCapability(
        requires=("open_interest",),
        produces=(OI_OUTPUT_KEY,),
        timeframe="1m",
        emit_mode="always",
    ),
    factory=OIChangeSensor,
    output_schema=(OI_OUTPUT_KEY,),
    parameter_schema=(),
)
