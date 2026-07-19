"""ATR ratio experiment Sensor; produces observations, never trade decisions."""

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


ATR_SENSOR_ID = "atr_compression"
ATR_SENSOR_VERSION = "1.0"
ATR_OUTPUT_KEY = "atr_ratio"
DEFAULT_ATR_PERIOD = 14
DEFAULT_BASELINE_WINDOW = 100


def _positive_int(
    parameters: Mapping[str, ParameterValue],
    name: str,
    default: int,
) -> int:
    value = parameters.get(name, default)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} 必须是正整数")
    return value


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


class ATRCompressionSensor(BaseFeatureSensor):
    """Observe ATR relative to its rolling mean for the frozen rb/1m experiment."""

    sensor_id = ATR_SENSOR_ID
    sensor_version = ATR_SENSOR_VERSION

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
            raise ValueError("ATR Compression v1 实验仅允许 rb")
        if timeframe != "1m":
            raise ValueError("ATR Compression v1 实验仅允许 1m")

        parameter_values = parameters or {}
        atr_period = _positive_int(
            parameter_values,
            "atr_period",
            DEFAULT_ATR_PERIOD,
        )
        baseline_window = _positive_int(
            parameter_values,
            "baseline_window",
            DEFAULT_BASELINE_WINDOW,
        )
        rollover_flag = window.get("rollover_flag", False)
        if not isinstance(rollover_flag, bool):
            raise TypeError("window['rollover_flag'] 必须是 bool")

        high = _price_series(window, "high")
        low = _price_series(window, "low")
        close = _price_series(window, "close")
        if len({len(high), len(low), len(close)}) != 1:
            raise ValueError("high、low、close 序列长度必须一致")

        diagnostics = {
            "atr_period": str(atr_period),
            "baseline_window": str(baseline_window),
            "rollover_flag": str(rollover_flag).lower(),
        }
        required_bars = atr_period + baseline_window
        if len(close) < required_bars:
            diagnostics["warmup_state"] = "insufficient"
            return self._result(
                symbol,
                timeframe,
                timestamp,
                None,
                diagnostics,
            )

        true_ranges: list[float] = []
        for index, (bar_high, bar_low) in enumerate(zip(high, low)):
            if bar_high < bar_low:
                raise ValueError("high 不得小于 low")
            if index == 0:
                true_range = bar_high - bar_low
            else:
                previous_close = close[index - 1]
                true_range = max(
                    bar_high - bar_low,
                    abs(bar_high - previous_close),
                    abs(bar_low - previous_close),
                )
            true_ranges.append(true_range)

        atr_values = [
            math.fsum(true_ranges[end - atr_period:end]) / atr_period
            for end in range(atr_period, len(true_ranges) + 1)
        ]
        current_atr = atr_values[-1]
        baseline_atr = (
            math.fsum(atr_values[-baseline_window:]) / baseline_window
        )
        if baseline_atr == 0.0:
            diagnostics["warmup_state"] = "ready"
            diagnostics["calculation_status"] = "zero_baseline"
            return self._result(
                symbol,
                timeframe,
                timestamp,
                None,
                diagnostics,
            )

        diagnostics["warmup_state"] = "ready"
        diagnostics["calculation_status"] = "ok"
        return self._result(
            symbol,
            timeframe,
            timestamp,
            current_atr / baseline_atr,
            diagnostics,
        )

    def _result(
        self,
        symbol: str,
        timeframe: str,
        timestamp: datetime,
        atr_ratio: float | None,
        diagnostics: Mapping[str, str],
    ) -> FeatureResult:
        return FeatureResult(
            sensor_id=self.sensor_id,
            sensor_version=self.sensor_version,
            symbol=symbol,
            timeframe=timeframe,
            timestamp=timestamp,
            values={ATR_OUTPUT_KEY: atr_ratio},
            diagnostics=diagnostics,
        )


ATR_COMPRESSION_DESCRIPTOR = SensorDescriptor(
    sensor_id=ATR_SENSOR_ID,
    sensor_version=ATR_SENSOR_VERSION,
    status=SensorStatus.EXPERIMENT,
    capability=SensorCapability(
        requires=("high", "low", "close"),
        produces=(ATR_OUTPUT_KEY,),
        timeframe="1m",
        emit_mode="always",
    ),
    factory=ATRCompressionSensor,
    output_schema=(ATR_OUTPUT_KEY,),
    parameter_schema=("atr_period", "baseline_window"),
)
