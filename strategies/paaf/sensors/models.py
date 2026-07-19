"""Immutable Feature Sensor contracts for PAAF Phase 3.0."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import math
import re
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from strategies.paaf.sensors.base import BaseFeatureSensor


SCHEMA_VERSION = "2.0"
SUPPORTED_SCHEMA_VERSIONS = frozenset({"1.0", SCHEMA_VERSION})
EMIT_MODES = frozenset({"always", "sparse"})
FORBIDDEN_FEATURE_KEYS = frozenset({
    "action",
    "buy",
    "dataset_hash",
    "decision",
    "direction",
    "dispatch_id",
    "evidence_metric",
    "experiment_id",
    "git_hash",
    "long",
    "parameter_set",
    "pipeline_status",
    "position_size",
    "run_id",
    "sell",
    "sharpe",
    "short",
    "side",
    "signal",
    "weight",
})

SensorKey = tuple[str, str]


def _require_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} 不能为空")


def _require_keys(
    keys: Iterable[str],
    field_name: str,
) -> tuple[str, ...]:
    normalized = tuple(keys)
    for key in normalized:
        _require_text(key, field_name)
        if not re.fullmatch(r"[a-z][a-z0-9_]*", key):
            raise ValueError(f"{field_name} 必须使用 snake_case")
        if key.lower() in FORBIDDEN_FEATURE_KEYS:
            raise ValueError(f"{field_name} 禁止业务语义键: {key}")
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{field_name} 不允许重复")
    return normalized


class SensorStatus(str, Enum):
    """Sensor governance lifecycle; never belongs to FeatureResult."""

    EXPERIMENT = "EXPERIMENT"
    VALIDATED = "VALIDATED"
    CANDIDATE = "CANDIDATE"
    PRODUCTION = "PRODUCTION"
    DEPRECATED = "DEPRECATED"


@dataclass(frozen=True)
class FeatureResult:
    """One deterministic market observation produced by a Feature Sensor."""

    sensor_id: str
    sensor_version: str
    symbol: str
    timeframe: str
    timestamp: datetime
    values: Mapping[str, float | None]
    diagnostics: Mapping[str, str] = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        for field_name in (
            "sensor_id",
            "sensor_version",
            "symbol",
            "timeframe",
        ):
            _require_text(getattr(self, field_name), field_name)
        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp 必须包含时区")
        if self.schema_version not in SUPPORTED_SCHEMA_VERSIONS:
            raise ValueError(
                f"不支持 FeatureResult schema: {self.schema_version}"
            )

        value_keys = _require_keys(self.values.keys(), "values")
        frozen_values: dict[str, float | None] = {}
        for key in value_keys:
            value = self.values[key]
            if value is None:
                if self.schema_version == "1.0":
                    raise TypeError("FeatureResult schema 1.0 不允许 null value")
                frozen_values[key] = None
                continue
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError("values 的值只允许 int、float 或 None")
            normalized = float(value)
            if not math.isfinite(normalized):
                raise ValueError("values 的数值必须有限")
            frozen_values[key] = normalized

        diagnostic_keys = _require_keys(
            self.diagnostics.keys(),
            "diagnostics",
        )
        frozen_diagnostics: dict[str, str] = {}
        for key in diagnostic_keys:
            value = self.diagnostics[key]
            if not isinstance(value, str):
                raise TypeError("diagnostics 的值只允许 str")
            frozen_diagnostics[key] = value

        object.__setattr__(
            self,
            "values",
            MappingProxyType(frozen_values),
        )
        object.__setattr__(
            self,
            "diagnostics",
            MappingProxyType(frozen_diagnostics),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "sensor_id": self.sensor_id,
            "sensor_version": self.sensor_version,
            "schema_version": self.schema_version,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "timestamp": self.timestamp.isoformat(),
            "values": dict(self.values),
            "diagnostics": dict(self.diagnostics),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "FeatureResult":
        return cls(
            sensor_id=str(data["sensor_id"]),
            sensor_version=str(data["sensor_version"]),
            symbol=str(data["symbol"]),
            timeframe=str(data["timeframe"]),
            timestamp=datetime.fromisoformat(str(data["timestamp"])),
            values=data.get("values", {}),
            diagnostics=data.get("diagnostics", {}),
            schema_version=str(data.get("schema_version", "")),
        )


@dataclass(frozen=True)
class SensorCapability:
    """Sensor input requirements and output feature keys (no directions)."""

    requires: tuple[str, ...] = ()
    produces: tuple[str, ...] = ()
    timeframe: str = "1m"
    emit_mode: str = "always"

    def __post_init__(self) -> None:
        _require_text(self.timeframe, "SensorCapability.timeframe")
        if self.emit_mode not in EMIT_MODES:
            raise ValueError("emit_mode 必须是 always 或 sparse")
        object.__setattr__(
            self,
            "requires",
            _require_keys(self.requires, "requires"),
        )
        object.__setattr__(
            self,
            "produces",
            _require_keys(self.produces, "produces"),
        )


@dataclass(frozen=True)
class SensorDescriptor:
    """Immutable SensorRegistry catalog entry."""

    sensor_id: str
    sensor_version: str
    status: SensorStatus
    capability: SensorCapability
    factory: Callable[[], BaseFeatureSensor] = field(
        repr=False,
        compare=False,
    )
    output_schema: tuple[str, ...] = ()
    parameter_schema: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_text(self.sensor_id, "sensor_id")
        _require_text(self.sensor_version, "sensor_version")
        if not callable(self.factory):
            raise TypeError("SensorDescriptor.factory 必须可调用")

        output_schema = _require_keys(
            self.output_schema,
            "output_schema",
        )
        parameter_schema = _require_keys(
            self.parameter_schema,
            "parameter_schema",
        )
        evidence_refs = tuple(self.evidence_refs)
        for ref in evidence_refs:
            _require_text(ref, "evidence_refs")
        if self.status is SensorStatus.PRODUCTION and not evidence_refs:
            raise ValueError("PRODUCTION SensorDescriptor 必须包含 evidence_refs")
        if output_schema and set(output_schema) != set(
            self.capability.produces
        ):
            raise ValueError(
                "output_schema 必须与 capability.produces 一致"
            )

        object.__setattr__(self, "output_schema", output_schema)
        object.__setattr__(self, "parameter_schema", parameter_schema)
        object.__setattr__(self, "evidence_refs", evidence_refs)

    @property
    def deprecated(self) -> bool:
        return self.status is SensorStatus.DEPRECATED

    def create(self) -> BaseFeatureSensor:
        from strategies.paaf.sensors.base import BaseFeatureSensor

        instance = self.factory()
        if not isinstance(instance, BaseFeatureSensor):
            raise TypeError("Sensor factory 必须返回 BaseFeatureSensor")
        return instance
