"""PAAFStrategy：只编排，不识别形态。

Commit 001 提供可单测的编排骨架。
Commit 002 再接入 vn.py ``CtaTemplate`` 与真实回测。
"""

from __future__ import annotations

from typing import Any, Optional

from strategies.paaf.base_detector import BaseDetector
from strategies.paaf.config import DEFAULT_CONFIG, PAAFConfig
from strategies.paaf.domain import Context, Signal, make_experiment_id
from strategies.paaf.engines import (
    ContextEngine,
    ExecutionEngine,
    RiskEngine,
    SignalEngine,
    TradeLogger,
)
from strategies.paaf.registry import DetectorRegistry


class PaafStrategy:
    """Context → Registry/SignalEngine → Risk → Execution → Logger。"""

    def __init__(
        self,
        *,
        symbol: str = "rb",
        config: Optional[PAAFConfig] = None,
        registry: Optional[DetectorRegistry] = None,
        log_path: Optional[str] = None,
    ) -> None:
        self.symbol = symbol
        self.config = config or DEFAULT_CONFIG
        self.registry = registry or DetectorRegistry()
        self.context_engine = ContextEngine(self.config)
        self.signal_engine = SignalEngine(self.registry)
        self.risk_engine = RiskEngine(self.config)
        self.execution_engine = ExecutionEngine()
        self.logger = TradeLogger(
            log_path
            or f"research/output/paaf_{make_experiment_id(symbol, self.config.framework_version)}.csv"
        )
        self.run_id = make_experiment_id(symbol, self.config.framework_version)
        self.experiment_id = self.run_id

    def register(self, detector: BaseDetector | type[BaseDetector]) -> BaseDetector:
        return self.registry.register(detector)

    def on_bar_window(self, am: Any) -> list[Signal]:
        """用只读行情窗口跑完一轮检测。"""

        context: Context = self.context_engine.update(am)
        signals = self.signal_engine.scan(am, context)
        for signal in signals:
            _ = self.risk_engine.stop(signal)
            _ = self.risk_engine.target(signal)
        return signals
