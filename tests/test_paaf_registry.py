"""Detector Descriptor Catalog Registry contract tests（v0.2.3）。"""

from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError
from typing import Any

from strategies.paaf import (
    BaseDetector,
    Context,
    DetectorCapability,
    DetectorDescriptor,
    DetectorMetadata,
    DetectorRegistry,
    DetectorStatus,
    DetectorTag,
    Direction,
    MarketState,
)


class _CatalogDetector(BaseDetector):
    metadata = DetectorMetadata(
        name="OPP03",
        version="1.0",
        timeframe="5m",
    )

    def detect(self, am: Any, context: Context) -> None:
        del am, context
        return None


def _descriptor(
    *,
    detector_id: str = "OPP03",
    version: str = "1.0",
    status: DetectorStatus = DetectorStatus.EXPERIMENT,
    requires: frozenset[str] = frozenset({"trend_bias"}),
    produces: frozenset[DetectorTag | str] = frozenset(
        {DetectorTag.PULLBACK}
    ),
    tags: tuple[DetectorTag | str, ...] = (DetectorTag.PULLBACK,),
    factory: Any = _CatalogDetector,
    evidence_refs: tuple[str, ...] = (),
) -> DetectorDescriptor:
    return DetectorDescriptor(
        id=detector_id,
        version=version,
        status=status,
        capability=DetectorCapability(
            market_states=(MarketState.TREND,),
            directions=(Direction.LONG, Direction.SHORT),
            requires=requires,
            produces=produces,
            timeframe="5m",
        ),
        factory=factory,
        evidence_refs=evidence_refs,
        tags=tags,
        metadata={"owner": "unit-test"},
    )


class TestDetectorRegistryContract(unittest.TestCase):
    def test_duplicate_composite_key_is_rejected(self) -> None:
        registry = DetectorRegistry()
        descriptor = _descriptor()
        registry.register(descriptor)

        with self.assertRaisesRegex(ValueError, "OPP03@1.0"):
            registry.register(_descriptor())

    def test_different_versions_coexist(self) -> None:
        registry = DetectorRegistry()
        first = _descriptor(version="1.0")
        second = _descriptor(version="2.0")

        registry.register(first)
        registry.register(second)

        self.assertTrue(registry.exists("OPP03", "1.0"))
        self.assertTrue(registry.exists("OPP03", "2.0"))
        self.assertIs(registry.get("OPP03", "1.0"), first)
        self.assertIs(registry.get("OPP03", "2.0"), second)
        self.assertEqual(registry.list(), (first, second))

    def test_capability_query_uses_subset_semantics(self) -> None:
        registry = DetectorRegistry()
        pullback = _descriptor()
        breakout = _descriptor(
            detector_id="OPP04",
            requires=frozenset({"session", "trend_bias"}),
            produces=frozenset({DetectorTag.BREAKOUT, "custom:opening"}),
            tags=(DetectorTag.BREAKOUT, "custom:opening"),
        )
        registry.register(pullback)
        registry.register(breakout)

        self.assertEqual(
            registry.find(requires={"session"}),
            (breakout,),
        )
        self.assertEqual(
            registry.find(requires={"trend_bias"}),
            (pullback, breakout),
        )
        self.assertEqual(
            registry.find(produces={DetectorTag.BREAKOUT}),
            (breakout,),
        )
        self.assertEqual(
            registry.find(tags={"custom:opening"}),
            (breakout,),
        )

    def test_descriptor_and_capability_are_immutable(self) -> None:
        descriptor = _descriptor()

        with self.assertRaises(FrozenInstanceError):
            descriptor.status = DetectorStatus.PRODUCTION  # type: ignore[misc]
        with self.assertRaises(FrozenInstanceError):
            descriptor.capability.timeframe = "15m"  # type: ignore[misc]
        with self.assertRaises(TypeError):
            descriptor.metadata["owner"] = "changed"  # type: ignore[index]

    def test_deprecated_is_visible_by_default_and_filterable(self) -> None:
        registry = DetectorRegistry()
        active = _descriptor()
        deprecated = _descriptor(
            version="0.9",
            status=DetectorStatus.DEPRECATED,
        )
        registry.register(active)
        registry.register(deprecated)

        self.assertTrue(deprecated.deprecated)
        self.assertEqual(registry.list(), (active, deprecated))
        self.assertEqual(
            registry.list(include_deprecated=False),
            (active,),
        )
        self.assertEqual(
            registry.find(status=DetectorStatus.DEPRECATED),
            (deprecated,),
        )
        self.assertEqual(
            registry.find(include_deprecated=False),
            (active,),
        )

    def test_factory_is_lazy_and_return_type_is_validated(self) -> None:
        descriptor = _descriptor()
        first = descriptor.create()
        second = descriptor.create()

        self.assertIsInstance(first, _CatalogDetector)
        self.assertIsNot(first, second)

        invalid = _descriptor(factory=lambda: object())
        with self.assertRaisesRegex(TypeError, "必须返回 BaseDetector"):
            invalid.create()

        with self.assertRaisesRegex(TypeError, "factory 必须可调用"):
            _descriptor(factory=object())

    def test_unregister_and_exists_use_exact_version(self) -> None:
        registry = DetectorRegistry()
        first = _descriptor(version="1.0")
        second = _descriptor(version="2.0")
        registry.register(first)
        registry.register(second)

        removed = registry.unregister("OPP03", "1.0")

        self.assertIs(removed, first)
        self.assertFalse(registry.exists("OPP03", "1.0"))
        self.assertTrue(registry.exists("OPP03", "2.0"))
        self.assertIsNone(registry.unregister("OPP03", "missing"))

    def test_production_descriptor_requires_evidence(self) -> None:
        with self.assertRaisesRegex(ValueError, "必须包含 evidence_refs"):
            _descriptor(status=DetectorStatus.PRODUCTION)

        descriptor = _descriptor(
            status=DetectorStatus.PRODUCTION,
            evidence_refs=("EXP-021",),
        )
        self.assertEqual(descriptor.evidence_refs, ("EXP-021",))

    def test_registry_stores_descriptor_not_instance(self) -> None:
        registry = DetectorRegistry()
        descriptor = _descriptor()

        registered = registry.register(descriptor)

        self.assertIs(registered, descriptor)
        self.assertIs(registry.list()[0], descriptor)
        self.assertIsInstance(registry.list()[0], DetectorDescriptor)


if __name__ == "__main__":
    unittest.main()
