"""Detector Catalog Registry（v0.2.3）。

核心存储只包含不可变 ``DetectorDescriptor``，不保存 Detector 实例。
v0.2 暂留实例注册与迭代兼容层，v0.3 删除。
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Optional

from strategies.paaf.base_detector import BaseDetector
from strategies.paaf.domain import (
    DetectorInfo,
    DetectorStatus,
    DetectorTag,
    Direction,
    MarketState,
)

DetectorKey = tuple[str, str]


def _normalize_tags(
    values: Iterable[DetectorTag | str],
) -> tuple[DetectorTag | str, ...]:
    normalized: list[DetectorTag | str] = []
    for value in values:
        if isinstance(value, DetectorTag):
            normalized.append(value)
        elif (
            isinstance(value, str)
            and value.startswith("custom:")
            and len(value) > 7
        ):
            normalized.append(value)
        else:
            raise ValueError("tag 必须是 DetectorTag 或 custom:<slug>")
    return tuple(normalized)


@dataclass(frozen=True)
class DetectorCapability:
    """Detector 声明的输入要求与输出能力。"""

    market_states: tuple[MarketState, ...] = ()
    directions: tuple[Direction, ...] = ()
    requires: frozenset[str] = field(default_factory=frozenset)
    produces: frozenset[DetectorTag | str] = field(default_factory=frozenset)
    timeframe: str = "5m"

    def __post_init__(self) -> None:
        if not self.timeframe.strip():
            raise ValueError("DetectorCapability.timeframe 不能为空")
        if Direction.NONE in self.directions:
            raise ValueError("DetectorCapability.directions 不能包含 NONE")
        if any(not item.strip() for item in self.requires):
            raise ValueError("DetectorCapability.requires 不能包含空值")
        object.__setattr__(self, "market_states", tuple(self.market_states))
        object.__setattr__(self, "directions", tuple(self.directions))
        object.__setattr__(self, "requires", frozenset(self.requires))
        object.__setattr__(
            self,
            "produces",
            frozenset(_normalize_tags(self.produces)),
        )


@dataclass(frozen=True)
class DetectorDescriptor:
    """Registry 中不可变的 Detector 目录项。"""

    id: str
    version: str
    status: DetectorStatus
    capability: DetectorCapability
    factory: Callable[[], BaseDetector] = field(repr=False, compare=False)
    evidence_refs: tuple[str, ...] = ()
    tags: tuple[DetectorTag | str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("DetectorDescriptor.id 不能为空")
        if not self.version.strip():
            raise ValueError("DetectorDescriptor.version 不能为空")
        if not callable(self.factory):
            raise TypeError("DetectorDescriptor.factory 必须可调用")

        evidence_refs = tuple(self.evidence_refs)
        if self.status is DetectorStatus.PRODUCTION and not evidence_refs:
            raise ValueError("PRODUCTION Descriptor 必须包含 evidence_refs")
        object.__setattr__(self, "evidence_refs", evidence_refs)
        object.__setattr__(self, "tags", _normalize_tags(self.tags))
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

    @property
    def deprecated(self) -> bool:
        return self.status is DetectorStatus.DEPRECATED

    def create(self) -> BaseDetector:
        """延迟实例化，并校验 factory 的返回类型。"""

        instance = self.factory()
        if not isinstance(instance, BaseDetector):
            raise TypeError("Detector factory 必须返回 BaseDetector")
        return instance


class DetectorRegistry:
    """Detector Descriptor Catalog；固定注册顺序，可按 Capability 查询。"""

    def __init__(self) -> None:
        self._descriptors: dict[DetectorKey, DetectorDescriptor] = {}

    def register(
        self,
        item: DetectorDescriptor | BaseDetector | type[BaseDetector],
    ) -> DetectorDescriptor | BaseDetector:
        """注册 Descriptor；v0.2 兼容旧 BaseDetector 注册。"""

        if isinstance(item, DetectorDescriptor):
            self._register_descriptor(item)
            return item

        descriptor, legacy_instance = self._adapt_legacy(item)
        self._register_descriptor(descriptor)
        return legacy_instance

    def _register_descriptor(self, descriptor: DetectorDescriptor) -> None:
        key = (descriptor.id, descriptor.version)
        if key in self._descriptors:
            raise ValueError(
                f"Detector Descriptor 已注册: {descriptor.id}@{descriptor.version}"
            )
        self._descriptors[key] = descriptor

    def unregister(
        self,
        detector_id: str,
        version: str,
    ) -> Optional[DetectorDescriptor]:
        return self._descriptors.pop((detector_id, version), None)

    def get(
        self,
        detector_id: str,
        version: str,
    ) -> Optional[DetectorDescriptor]:
        return self._descriptors.get((detector_id, version))

    def list(
        self,
        *,
        include_deprecated: bool = True,
    ) -> tuple[DetectorDescriptor, ...]:
        descriptors = tuple(self._descriptors.values())
        if include_deprecated:
            return descriptors
        return tuple(item for item in descriptors if not item.deprecated)

    def find(
        self,
        *,
        requires: Iterable[str] = (),
        produces: Iterable[DetectorTag | str] = (),
        tags: Iterable[DetectorTag | str] = (),
        status: Optional[DetectorStatus] = None,
        include_deprecated: bool = True,
    ) -> tuple[DetectorDescriptor, ...]:
        required_set = frozenset(requires)
        produced_set = frozenset(_normalize_tags(produces))
        tag_set = frozenset(_normalize_tags(tags))
        matches: list[DetectorDescriptor] = []
        for descriptor in self._descriptors.values():
            if not include_deprecated and descriptor.deprecated:
                continue
            if status is not None and descriptor.status is not status:
                continue
            if not required_set.issubset(descriptor.capability.requires):
                continue
            if not produced_set.issubset(descriptor.capability.produces):
                continue
            if not tag_set.issubset(descriptor.tags):
                continue
            matches.append(descriptor)
        return tuple(matches)

    def exists(self, detector_id: str, version: str) -> bool:
        return (detector_id, version) in self._descriptors

    def _adapt_legacy(
        self,
        item: BaseDetector | type[BaseDetector],
    ) -> tuple[DetectorDescriptor, BaseDetector]:
        if isinstance(item, type):
            if not issubclass(item, BaseDetector):
                raise TypeError("只能注册 DetectorDescriptor 或 BaseDetector")
            instance = item()
            factory: Callable[[], BaseDetector] = item
        elif isinstance(item, BaseDetector):
            instance = item
            factory = lambda instance=instance: instance
        else:
            raise TypeError("只能注册 DetectorDescriptor 或 BaseDetector")

        descriptor = DetectorDescriptor(
            id=instance.metadata.name,
            version=instance.metadata.version,
            status=DetectorStatus.EXPERIMENT,
            capability=DetectorCapability(
                timeframe=instance.metadata.timeframe,
            ),
            factory=factory,
            metadata=MappingProxyType(
                {
                    "legacy_adapter": True,
                    "evidence_level": instance.metadata.evidence_level,
                }
            ),
        )
        return descriptor, instance

    # v0.2 deprecated compatibility API; new code must use descriptor methods.
    def names(self) -> list[str]:
        return list(dict.fromkeys(item.id for item in self._descriptors.values()))

    def infos(self) -> list[DetectorInfo]:
        return [descriptor.create().info for descriptor in self._descriptors.values()]

    def all(self) -> list[BaseDetector]:
        return [descriptor.create() for descriptor in self._descriptors.values()]

    def __iter__(self) -> Iterator[BaseDetector]:
        return iter(self.all())

    def __len__(self) -> int:
        return len(self._descriptors)

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and any(
            descriptor.id == name for descriptor in self._descriptors.values()
        )


def build_registry(
    items: Iterable[
        DetectorDescriptor | BaseDetector | type[BaseDetector]
    ],
) -> DetectorRegistry:
    registry = DetectorRegistry()
    for item in items:
        registry.register(item)
    return registry
