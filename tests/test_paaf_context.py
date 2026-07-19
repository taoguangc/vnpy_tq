"""Context Engine：单元测试与 Contract Test（Spec v1.0.0）。"""

from __future__ import annotations

import ast
import unittest
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from strategies.paaf import (
    EXTRAS_TREND_BIAS,
    BaseDetector,
    Context,
    ContextEngine,
    DetectorMetadata,
    Direction,
    MarketState,
    Session,
    Signal,
)

class _FakeAM:
    def __init__(self, close: float = 100.0) -> None:
        self.close = [close]


class _ReadOnlyDetector(BaseDetector):
    metadata = DetectorMetadata(name="CTX_RO", version="0.1.0")

    def __init__(self) -> None:
        self.last_state: MarketState | None = None

    def detect(self, am: Any, context: Context) -> Optional[Signal]:
        del am
        self.last_state = context.market_state
        _ = context.session
        _ = context.extras.get(EXTRAS_TREND_BIAS)
        return None


class _MutatingDetector(BaseDetector):
    """故意尝试写 Context；契约要求失败。"""

    metadata = DetectorMetadata(name="CTX_MUT", version="0.1.0")

    def detect(self, am: Any, context: Context) -> Optional[Signal]:
        del am
        try:
            context.market_state = MarketState.TREND  # type: ignore[misc]
        except Exception:
            return None
        return self.make_signal(Direction.LONG, reason="mutated")


class TestContextDomain(unittest.TestCase):
    def test_session_and_market_state_enums(self) -> None:
        self.assertEqual(
            {s.value for s in Session},
            {"DAY", "NIGHT", "UNKNOWN"},
        )
        self.assertEqual(
            {s.value for s in MarketState},
            {"UNKNOWN", "TREND", "RANGE"},
        )

    def test_context_fields_and_frozen(self) -> None:
        ctx = Context(
            symbol="rb",
            datetime=datetime(2026, 7, 19, 9, 1),
            session=Session.DAY,
            market_state=MarketState.UNKNOWN,
            extras={EXTRAS_TREND_BIAS: "NONE"},
        )
        self.assertEqual(ctx.symbol, "rb")
        self.assertEqual(ctx.session, Session.DAY)
        with self.assertRaises(Exception):
            ctx.market_state = MarketState.TREND  # type: ignore[misc]
        with self.assertRaises(TypeError):
            ctx.extras[EXTRAS_TREND_BIAS] = "UP"  # type: ignore[index]

    def test_domain_source_has_no_heavy_imports(self) -> None:
        path = (
            Path(__file__).resolve().parents[1]
            / "strategies"
            / "paaf"
            / "domain.py"
        )
        tree = ast.parse(path.read_text(encoding="utf-8"))
        forbidden = {"vnpy", "numpy", "pandas", "talib", "vnpy_ctastrategy"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".", 1)[0]
                    self.assertNotIn(root, forbidden)
            elif isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".", 1)[0]
                self.assertNotIn(root, forbidden)


class TestContextEngineLifecycle(unittest.TestCase):
    def test_update_publish_readonly_always_unknown(self) -> None:
        engine = ContextEngine(symbol="rb")
        first = engine.get_context()
        self.assertEqual(first.market_state, MarketState.UNKNOWN)

        published = engine.update(
            _FakeAM(),
            symbol="rb",
            datetime=datetime(2026, 7, 19, 21, 0),
            session=Session.NIGHT,
        )
        self.assertIs(published, engine.get_context())
        self.assertEqual(published.market_state, MarketState.UNKNOWN)
        self.assertEqual(published.session, Session.NIGHT)
        self.assertEqual(published.symbol, "rb")
        self.assertIsNot(published, first)

        again = engine.update(_FakeAM(), symbol="rb", session=Session.DAY)
        self.assertIsNot(again, published)
        self.assertEqual(again.market_state, MarketState.UNKNOWN)

    def test_reset_keeps_symbol(self) -> None:
        engine = ContextEngine(symbol="ag")
        engine.update(_FakeAM(), symbol="ag", session=Session.DAY)
        reset = engine.reset()
        self.assertEqual(reset.symbol, "ag")
        self.assertEqual(reset.market_state, MarketState.UNKNOWN)
        self.assertEqual(reset.session, Session.UNKNOWN)

    def test_state_transition_observability_via_publish(self) -> None:
        """v0.1.1 无算法；用 publish 注入验证转换可观测（桩）。"""

        engine = ContextEngine(symbol="rb")
        paths = [
            MarketState.TREND,
            MarketState.RANGE,
            MarketState.TREND,
            MarketState.UNKNOWN,
            MarketState.RANGE,
            MarketState.UNKNOWN,
        ]
        for state in paths:
            ctx = engine.publish(
                Context(symbol="rb", market_state=state, session=Session.DAY)
            )
            self.assertEqual(engine.get_context().market_state, state)
            self.assertEqual(ctx.market_state, state)


class TestContextContracts(unittest.TestCase):
    def test_detector_may_read_published_context(self) -> None:
        engine = ContextEngine(symbol="rb")
        ctx = engine.update(_FakeAM(), symbol="rb", session=Session.DAY)
        detector = _ReadOnlyDetector()
        signal = detector.detect(_FakeAM(), ctx)
        self.assertIsNone(signal)
        self.assertEqual(detector.last_state, MarketState.UNKNOWN)

    def test_detector_cannot_mutate_published_context(self) -> None:
        engine = ContextEngine(symbol="rb")
        ctx = engine.update(_FakeAM(), symbol="rb")
        before = ctx.market_state
        detector = _MutatingDetector()
        signal = detector.detect(_FakeAM(), ctx)
        self.assertIsNone(signal)
        self.assertEqual(ctx.market_state, before)
        self.assertEqual(engine.get_context().market_state, MarketState.UNKNOWN)

    def test_freeze_rejects_non_context(self) -> None:
        engine = ContextEngine(symbol="rb")
        with self.assertRaises(TypeError):
            engine.freeze(object())  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
