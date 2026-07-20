"""Close-location experiment Sensor; observations only, never trading."""

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


CLOSE_SENSOR_ID = "close_location"
CLOSE_SENSOR_VERSION = "1.0"
CLOSE_OUTPUT_KEY = "close_location"


def _price_series(window: Mapping[str, Any], name: str) -> tuple[float, ...]:
    raw = window.get(name, ())
    if (
        isinstance(raw, (str, bytes, Mapping))
        or not isinstance(raw, Iterable)
    ):
        raise TypeError(f"window[{name!r}] 必须是数值序列")

    values: list[float] = []
    for item in raw:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise TypeError(f"window[{name!r}] 必须是数值序列")
        value = float(item)
        if not math.isfinite(value):
            raise ValueError(f"window[{name!r}] 必须包含有限数值")
        values.append(value)
    return tuple(values)


class CloseLocationSensor(BaseFeatureSensor):
    """Observe close location inside the current bar range."""

    sensor_id = CLOSE_SENSOR_ID
    sensor_version = CLOSE_SENSOR_VERSION

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
            raise ValueError("Close Location v1 实验仅允许 rb")
        if timeframe != "1m":
            raise ValueError("Close Location v1 实验仅允许 1m")

        roll_neighborhood = window.get("roll_neighborhood", False)
        if not isinstance(roll_neighborhood, bool):
            raise TypeError("window['roll_neighborhood'] 必须是 bool")

        high = _price_series(window, "high")
        low = _price_series(window, "low")
        close = _price_series(window, "close")
        diagnostics = {
            "roll_neighborhood": str(roll_neighborhood).lower(),
        }
        if not high or not low or not close:
            diagnostics["warmup_state"] = "insufficient"
            return self._result(
                symbol,
                timeframe,
                timestamp,
                None,
                diagnostics,
            )
        if len({len(high), len(low), len(close)}) != 1:
            raise ValueError("high、low、close 序列长度必须一致")

        bar_high = high[-1]
        bar_low = low[-1]
        bar_close = close[-1]
        if bar_high < bar_low:
            raise ValueError("high 不得小于 low")

        diagnostics["warmup_state"] = "ready"
        span = bar_high - bar_low
        if span == 0.0:
            diagnostics["calculation_status"] = "zero_range"
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
            (bar_close - bar_low) / span,
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
            values={CLOSE_OUTPUT_KEY: value},
            diagnostics=diagnostics,
        )


CLOSE_LOCATION_DESCRIPTOR = SensorDescriptor(
    sensor_id=CLOSE_SENSOR_ID,
    sensor_version=CLOSE_SENSOR_VERSION,
    status=SensorStatus.EXPERIMENT,
    capability=SensorCapability(
        requires=("high", "low", "close"),
        produces=(CLOSE_OUTPUT_KEY,),
        timeframe="1m",
        emit_mode="always",
    ),
    factory=CloseLocationSensor,
    output_schema=(CLOSE_OUTPUT_KEY,),
    parameter_schema=(),
)
