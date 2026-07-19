"""SignalEngine：遍历 Registry，收集 Signal。"""

from __future__ import annotations

from typing import Any

from strategies.paaf.domain import Context, Signal
from strategies.paaf.registry import DetectorRegistry


class SignalEngine:
    """Strategy 只调用本引擎，不逐个 import Detector。"""

    def __init__(self, registry: DetectorRegistry) -> None:
        self._registry = registry

    def scan(self, am: Any, context: Context) -> list[Signal]:
        signals: list[Signal] = []
        for detector in self._registry:
            signal = detector.detect(am, context)
            if signal is not None:
                signals.append(signal)
        return signals
