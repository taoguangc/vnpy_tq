"""Detector Registry：插件式发现与启停。"""

from __future__ import annotations

from typing import Iterable, Iterator, Optional, Type

from strategies.paaf.base_detector import BaseDetector
from strategies.paaf.domain import DetectorInfo


class DetectorRegistry:
    """Strategy 不硬编码 Detector 列表；统一通过 Registry 注册。"""

    def __init__(self) -> None:
        self._detectors: dict[str, BaseDetector] = {}

    def register(
        self,
        detector: BaseDetector | Type[BaseDetector],
    ) -> BaseDetector:
        instance = detector() if isinstance(detector, type) else detector
        if not isinstance(instance, BaseDetector):
            raise TypeError("只能注册 BaseDetector 或其子类")
        name = instance.metadata.name
        if name in self._detectors:
            raise ValueError(f"Detector 已注册: {name}")
        self._detectors[name] = instance
        return instance

    def unregister(self, name: str) -> None:
        self._detectors.pop(name, None)

    def get(self, name: str) -> Optional[BaseDetector]:
        return self._detectors.get(name)

    def names(self) -> list[str]:
        return list(self._detectors.keys())

    def infos(self) -> list[DetectorInfo]:
        return [detector.info for detector in self._detectors.values()]

    def all(self) -> list[BaseDetector]:
        return list(self._detectors.values())

    def __iter__(self) -> Iterator[BaseDetector]:
        return iter(self._detectors.values())

    def __len__(self) -> int:
        return len(self._detectors)

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and name in self._detectors


def build_registry(detectors: Iterable[BaseDetector | Type[BaseDetector]]) -> DetectorRegistry:
    registry = DetectorRegistry()
    for detector in detectors:
        registry.register(detector)
    return registry
