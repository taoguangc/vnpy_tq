"""PAAF Commit 001 地基测试。"""

from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path
from typing import Any, Optional

from strategies.paaf import (
    DEFAULT_CONFIG,
    TRADE_RECORD_FIELDS,
    BaseDetector,
    Context,
    DetectorMetadata,
    DetectorRegistry,
    Direction,
    MarketState,
    PaafStrategy,
    Signal,
    TradeLogger,
    TradeRecord,
    make_experiment_id,
)
from strategies.paaf.engines import ContextEngine, RiskEngine, SignalEngine


class _FakeAM:
    def __init__(self, close: float = 100.0) -> None:
        self.close = [close]


class _StubOpp16(BaseDetector):
    metadata = DetectorMetadata(
        name="OPP16",
        version="0.1.0",
        description="Two Bar Reversal stub",
        status="Candidate",
        category="Reversal",
    )

    def detect(self, am: Any, context: Context) -> Optional[Signal]:
        del context
        close = float(am.close[-1])
        return self.make_signal(
            Direction.LONG,
            entry=close,
            stop=close - 1.0,
            reason="stub",
        )


class TestPaafCommit001(unittest.TestCase):
    def test_domain_purity(self) -> None:
        self.assertEqual(
            {state.value for state in MarketState},
            {"UNKNOWN", "TREND", "RANGE"},
        )
        self.assertEqual(
            set(DEFAULT_CONFIG.__dataclass_fields__) - {"framework_version"},
            {"ema_period", "atr_period", "adx_period", "risk_per_trade", "tick_size"},
        )
        ctx = Context()
        self.assertFalse(hasattr(ctx, "ema"))
        self.assertFalse(hasattr(ctx, "atr"))

    def test_signal_confidence(self) -> None:
        signal = Signal(detector="OPP16", direction=Direction.LONG)
        self.assertEqual(signal.confidence, 1.0)
        with self.assertRaises(ValueError):
            Signal(detector="OPP16", direction=Direction.NONE)

    def test_experiment_id_and_trade_record(self) -> None:
        self.assertEqual(
            make_experiment_id("RB", "0.1.0", date(2026, 7, 19)),
            "20260719_rb_v0.1.0",
        )
        self.assertIn("experiment_id", TRADE_RECORD_FIELDS)
        record = TradeRecord(
            run_id="run-1",
            experiment_id="20260719_rb_v0.1.0",
            version="0.1.0",
            symbol="rb",
            detector="OPP16",
            context="RANGE",
            direction="LONG",
            entry=1.0,
            exit=2.0,
            stop=0.5,
            target=None,
            bars=2,
            mfe=1.5,
            mae=-0.2,
            pnl=1.0,
            reason="test",
        )
        self.assertEqual(record.to_dict()["detector"], "OPP16")

    def test_registry_plugin(self) -> None:
        registry = DetectorRegistry()
        registry.register(_StubOpp16)
        self.assertIn("OPP16", registry)
        self.assertEqual(registry.infos()[0].name, "OPP16")

        engine = SignalEngine(registry)
        signals = engine.scan(_FakeAM(101.0), Context(market_state=MarketState.RANGE))
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].entry, 101.0)

    def test_context_and_risk_interfaces(self) -> None:
        ctx_engine = ContextEngine()
        context = ctx_engine.update(_FakeAM())
        self.assertEqual(context.market_state, MarketState.UNKNOWN)
        self.assertEqual(ctx_engine.get_context().market_state, MarketState.UNKNOWN)

        signal = Signal(
            detector="OPP16",
            direction=Direction.LONG,
            entry=100.0,
            stop=None,
        )
        risk = RiskEngine()
        self.assertEqual(risk.stop(signal), 99.0)
        self.assertIsNone(risk.target(signal))

    def test_strategy_orchestration_and_logger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trades.csv"
            strategy = PaafStrategy(symbol="rb", log_path=str(path))
            strategy.register(_StubOpp16())
            signals = strategy.on_bar_window(_FakeAM(200.0))
            self.assertEqual(len(signals), 1)

            logger = TradeLogger(path)
            logger.write(
                TradeRecord(
                    run_id=strategy.run_id,
                    experiment_id=strategy.experiment_id,
                    version="0.1.0",
                    symbol="rb",
                    detector="OPP16",
                    context="UNKNOWN",
                    direction="LONG",
                    entry=200.0,
                    exit=201.0,
                    stop=199.0,
                    target=None,
                    bars=1,
                    mfe=1.0,
                    mae=0.0,
                    pnl=1.0,
                    reason="stub",
                )
            )
            text = path.read_text(encoding="utf-8")
            self.assertIn("experiment_id", text)
            self.assertIn("OPP16", text)

    def test_detector_requires_metadata_name(self) -> None:
        with self.assertRaises(TypeError):

            class Bad(BaseDetector):  # noqa: F841
                metadata = DetectorMetadata(name="", version="0.1.0")

                def detect(self, am: Any, context: Context) -> Optional[Signal]:
                    return None


if __name__ == "__main__":
    unittest.main()
