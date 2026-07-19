"""Descriptor-only SensorRegistry; isolated from DetectorRegistry."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Optional

from strategies.paaf.sensors.base import BaseFeatureSensor
from strategies.paaf.sensors.models import (
    SensorDescriptor,
    SensorKey,
    SensorStatus,
)


class SensorRegistry:
    """Feature Sensor catalog keyed by ``(sensor_id, sensor_version)``."""

    def __init__(self) -> None:
        self._descriptors: dict[SensorKey, SensorDescriptor] = {}

    def register(self, descriptor: SensorDescriptor) -> SensorDescriptor:
        if not isinstance(descriptor, SensorDescriptor):
            raise TypeError("SensorRegistry 只允许 SensorDescriptor")
        key = (descriptor.sensor_id, descriptor.sensor_version)
        if key in self._descriptors:
            raise ValueError(
                "SensorDescriptor 已注册: "
                f"{descriptor.sensor_id}@{descriptor.sensor_version}"
            )
        self._descriptors[key] = descriptor
        return descriptor

    def unregister(
        self,
        sensor_id: str,
        sensor_version: str,
    ) -> Optional[SensorDescriptor]:
        return self._descriptors.pop((sensor_id, sensor_version), None)

    def get(
        self,
        sensor_id: str,
        sensor_version: str,
    ) -> Optional[SensorDescriptor]:
        return self._descriptors.get((sensor_id, sensor_version))

    def list(
        self,
        *,
        include_deprecated: bool = True,
    ) -> tuple[SensorDescriptor, ...]:
        descriptors = tuple(self._descriptors.values())
        if include_deprecated:
            return descriptors
        return tuple(item for item in descriptors if not item.deprecated)

    def find(
        self,
        *,
        requires: Iterable[str] = (),
        produces: Iterable[str] = (),
        status: Optional[SensorStatus] = None,
        include_deprecated: bool = True,
    ) -> tuple[SensorDescriptor, ...]:
        required_set = frozenset(requires)
        produced_set = frozenset(produces)
        matches: list[SensorDescriptor] = []
        for descriptor in self._descriptors.values():
            if not include_deprecated and descriptor.deprecated:
                continue
            if status is not None and descriptor.status is not status:
                continue
            if not required_set.issubset(descriptor.capability.requires):
                continue
            if not produced_set.issubset(descriptor.capability.produces):
                continue
            matches.append(descriptor)
        return tuple(matches)

    def exists(self, sensor_id: str, sensor_version: str) -> bool:
        return (sensor_id, sensor_version) in self._descriptors

    def create(
        self,
        sensor_id: str,
        sensor_version: str,
    ) -> BaseFeatureSensor:
        descriptor = self.get(sensor_id, sensor_version)
        if descriptor is None:
            raise KeyError(f"Sensor 未注册: {sensor_id}@{sensor_version}")
        return descriptor.create()


def build_sensor_registry(
    descriptors: Iterable[SensorDescriptor],
) -> SensorRegistry:
    registry = SensorRegistry()
    for descriptor in descriptors:
        registry.register(descriptor)
    return registry
