"""Minimal Detector：仅用于验证 Detector Pipeline，不代表 Alpha。"""

from __future__ import annotations

from typing import Any, Optional

from strategies.paaf.adapters import last_bar
from strategies.paaf.base_detector import BaseDetector
from strategies.paaf.domain import (
    Context,
    DetectionResult,
    DetectorStatus,
    DetectorTag,
    Direction,
    PatternState,
)
from strategies.paaf.metadata import DetectorMetadata
from strategies.paaf.registry import DetectorCapability, DetectorDescriptor


class DemoMinimalDetector(BaseDetector):
    """已完成 Bar ``close > open`` 时产出 DEMO DetectionResult。"""

    metadata = DetectorMetadata(
        name="DEMO_MINIMAL",
        version="1.0.0",
        description="Pipeline verification only; no Alpha claim",
        status="Candidate",
        category="Demo",
        timeframe="1m",
        evidence_level="E0",
    )

    def detect(
        self,
        am: Any,
        context: Context,
    ) -> Optional[DetectionResult]:
        bar = last_bar(am)
        if bar is None or bar.close <= bar.open:
            return None

        return DetectionResult(
            detector_id=self.metadata.name,
            detector_version=self.metadata.version,
            opportunity_id="DEMO_MINIMAL",
            status=DetectorStatus.EXPERIMENT,
            direction=Direction.LONG,
            confidence=1.0,
            tags=(DetectorTag.DEMO,),
            entry=bar.close,
            reason="pipeline verification: close > open",
            metadata={
                "market_state": context.market_state.value,
                "session": context.session.value,
            },
            pattern_state=PatternState(
                name="bullish_bar",
                confidence=1.0,
            ),
        )


DEMO_MINIMAL_DESCRIPTOR = DetectorDescriptor(
    id="DEMO_MINIMAL",
    version="1.0.0",
    status=DetectorStatus.EXPERIMENT,
    capability=DetectorCapability(
        directions=(Direction.LONG,),
        requires=frozenset({"session"}),
        produces=frozenset({DetectorTag.DEMO}),
        timeframe="1m",
    ),
    factory=DemoMinimalDetector,
    tags=(DetectorTag.DEMO,),
    metadata={
        "purpose": "pipeline_verification",
        "alpha_claim": False,
    },
)
