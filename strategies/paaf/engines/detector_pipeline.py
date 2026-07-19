"""Context → Detector → DetectionResult → Opportunity → Logger。"""

from __future__ import annotations

from typing import Any, Optional

from strategies.paaf.domain import (
    Context,
    DetectionResult,
    Direction,
    Opportunity,
    OpportunityDirection,
)
from strategies.paaf.engines.logger import OpportunityLogger
from strategies.paaf.registry import DetectorDescriptor, DetectorRegistry


class DetectorPipeline:
    """Detector Framework v0.2.4 的最小通用编排。"""

    def __init__(
        self,
        registry: DetectorRegistry,
        logger: Optional[OpportunityLogger] = None,
    ) -> None:
        self._registry = registry
        self._logger = logger

    def run(self, window: Any, context: Context) -> tuple[Opportunity, ...]:
        opportunities: list[Opportunity] = []
        for descriptor in self._registry.list(include_deprecated=False):
            if not self._context_satisfies(descriptor, context):
                continue

            detector = descriptor.create()
            result = detector.detect(window, context)
            if result is None:
                continue
            if not isinstance(result, DetectionResult):
                raise TypeError(
                    f"{descriptor.id}@{descriptor.version} "
                    "必须返回 DetectionResult | None"
                )
            self._validate_result(descriptor, result)

            opportunity = self._to_opportunity(
                descriptor,
                result,
                context,
            )
            opportunities.append(opportunity)
            if self._logger is not None:
                self._logger.write(opportunity)
        return tuple(opportunities)

    @staticmethod
    def _context_satisfies(
        descriptor: DetectorDescriptor,
        context: Context,
    ) -> bool:
        capability = descriptor.capability
        if (
            capability.market_states
            and context.market_state not in capability.market_states
        ):
            return False

        stable_fields = {"symbol", "datetime", "session", "market_state"}
        available = stable_fields | set(context.extras)
        return capability.requires.issubset(available)

    @staticmethod
    def _validate_result(
        descriptor: DetectorDescriptor,
        result: DetectionResult,
    ) -> None:
        if result.detector_id != descriptor.id:
            raise ValueError("DetectionResult.detector_id 与 Descriptor 不一致")
        if result.detector_version != descriptor.version:
            raise ValueError(
                "DetectionResult.detector_version 与 Descriptor 不一致"
            )
        if result.status is not descriptor.status:
            raise ValueError("DetectionResult.status 与 Descriptor 不一致")

    @staticmethod
    def _to_opportunity(
        descriptor: DetectorDescriptor,
        result: DetectionResult,
        context: Context,
    ) -> Opportunity:
        evidence_refs = tuple(
            dict.fromkeys((*descriptor.evidence_refs, *result.evidence_refs))
        )
        lineage = (
            f"DET:{descriptor.id}@{descriptor.version}",
            *(f"EXP:{ref}" for ref in evidence_refs),
        )
        direction = (
            OpportunityDirection.LONG
            if result.direction is Direction.LONG
            else OpportunityDirection.SHORT
        )
        return Opportunity(
            id=result.opportunity_id,
            version=descriptor.version,
            status=descriptor.status,
            direction=direction,
            market_state=context.market_state,
            detector_result=result,
            evidence_refs=evidence_refs,
            metadata={
                "symbol": context.symbol,
                "session": context.session.value,
            },
            lineage=lineage,
            created_at=result.created_at,
        )
