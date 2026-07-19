"""Detector Pipeline Verification contract tests（v0.2.4）。"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from strategies.paaf import (
    BaseDetector,
    Context,
    DetectionResult,
    DetectorCapability,
    DetectorDescriptor,
    DetectorMetadata,
    DetectorPipeline,
    DetectorRegistry,
    DetectorStatus,
    Direction,
    MarketState,
    Opportunity,
    OpportunityLogger,
    Session,
)
from strategies.paaf.detectors import (
    DEMO_MINIMAL_DESCRIPTOR,
    DemoMinimalDetector,
)


class _FakeAM:
    def __init__(self, open_price: float, close_price: float) -> None:
        self.open = [open_price]
        self.high = [max(open_price, close_price)]
        self.low = [min(open_price, close_price)]
        self.close = [close_price]
        self.volume = [1.0]
        self.open_interest = [0.0]
        self.count = 1
        self.inited = True


class _BoolDetector(BaseDetector):
    metadata = DetectorMetadata(name="DEMO_BOOL", version="1.0.0")

    def detect(self, am: Any, context: Context) -> Any:
        del am, context
        return True


class _MismatchDetector(BaseDetector):
    metadata = DetectorMetadata(name="DEMO_MISMATCH", version="1.0.0")

    def detect(self, am: Any, context: Context) -> DetectionResult:
        del am, context
        return DetectionResult(
            detector_id="OTHER_DETECTOR",
            detector_version="1.0.0",
            opportunity_id="DEMO_MISMATCH",
            status=DetectorStatus.EXPERIMENT,
            direction=Direction.LONG,
        )


def _descriptor(
    detector_id: str,
    factory: type[BaseDetector],
) -> DetectorDescriptor:
    return DetectorDescriptor(
        id=detector_id,
        version="1.0.0",
        status=DetectorStatus.EXPERIMENT,
        capability=DetectorCapability(
            directions=(Direction.LONG,),
            requires=frozenset({"session"}),
            timeframe="1m",
        ),
        factory=factory,
    )


class TestDetectorPipelineVerification(unittest.TestCase):
    def test_full_seven_step_pipeline_and_logger(self) -> None:
        registry = DetectorRegistry()
        registered = registry.register(DEMO_MINIMAL_DESCRIPTOR)
        self.assertIs(registered, DEMO_MINIMAL_DESCRIPTOR)

        detector = DEMO_MINIMAL_DESCRIPTOR.create()
        self.assertIsInstance(detector, DemoMinimalDetector)

        context = Context(
            symbol="rb",
            session=Session.DAY,
            market_state=MarketState.UNKNOWN,
        )
        before = context

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "opportunities.jsonl"
            logger = OpportunityLogger(path)
            pipeline = DetectorPipeline(registry, logger)

            opportunities = pipeline.run(_FakeAM(100.0, 101.0), context)

            self.assertEqual(len(opportunities), 1)
            opportunity = opportunities[0]
            self.assertIsInstance(opportunity, Opportunity)
            self.assertIsInstance(
                opportunity.detector_result,
                DetectionResult,
            )
            self.assertEqual(opportunity.id, "DEMO_MINIMAL")
            self.assertEqual(
                opportunity.detector_result.detector_id,
                "DEMO_MINIMAL",
            )
            self.assertEqual(
                opportunity.detector_result.metadata["market_state"],
                "UNKNOWN",
            )
            self.assertEqual(opportunity.metadata["symbol"], "rb")
            self.assertEqual(
                opportunity.lineage,
                ("DET:DEMO_MINIMAL@1.0.0",),
            )
            self.assertIs(context, before)
            self.assertEqual(context.market_state, MarketState.UNKNOWN)

            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            restored = Opportunity.from_dict(json.loads(lines[0]))
            self.assertEqual(restored, opportunity)

    def test_non_bullish_bar_produces_nothing_and_logs_nothing(self) -> None:
        registry = DetectorRegistry()
        registry.register(DEMO_MINIMAL_DESCRIPTOR)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "opportunities.jsonl"
            pipeline = DetectorPipeline(registry, OpportunityLogger(path))

            equal = pipeline.run(_FakeAM(100.0, 100.0), Context())
            bearish = pipeline.run(_FakeAM(101.0, 100.0), Context())

            self.assertEqual(equal, ())
            self.assertEqual(bearish, ())
            self.assertFalse(path.exists())

    def test_demo_is_experiment_and_never_opp(self) -> None:
        self.assertEqual(
            DEMO_MINIMAL_DESCRIPTOR.status,
            DetectorStatus.EXPERIMENT,
        )
        self.assertTrue(DEMO_MINIMAL_DESCRIPTOR.id.startswith("DEMO_"))
        self.assertFalse(DEMO_MINIMAL_DESCRIPTOR.id.startswith("OPP"))
        self.assertEqual(DEMO_MINIMAL_DESCRIPTOR.evidence_refs, ())

    def test_pipeline_rejects_bool_result(self) -> None:
        registry = DetectorRegistry()
        registry.register(_descriptor("DEMO_BOOL", _BoolDetector))

        with self.assertRaisesRegex(TypeError, "DetectionResult"):
            DetectorPipeline(registry).run(_FakeAM(1.0, 2.0), Context())

    def test_pipeline_rejects_descriptor_result_mismatch(self) -> None:
        registry = DetectorRegistry()
        registry.register(
            _descriptor("DEMO_MISMATCH", _MismatchDetector)
        )

        with self.assertRaisesRegex(ValueError, "detector_id"):
            DetectorPipeline(registry).run(_FakeAM(1.0, 2.0), Context())

    def test_capability_market_state_gate_skips_detector(self) -> None:
        descriptor = DetectorDescriptor(
            id="DEMO_MINIMAL",
            version="1.0.0",
            status=DetectorStatus.EXPERIMENT,
            capability=DetectorCapability(
                market_states=(MarketState.TREND,),
                directions=(Direction.LONG,),
                requires=frozenset({"session"}),
                timeframe="1m",
            ),
            factory=DemoMinimalDetector,
        )
        registry = DetectorRegistry()
        registry.register(descriptor)

        opportunities = DetectorPipeline(registry).run(
            _FakeAM(1.0, 2.0),
            Context(market_state=MarketState.UNKNOWN),
        )

        self.assertEqual(opportunities, ())


if __name__ == "__main__":
    unittest.main()
