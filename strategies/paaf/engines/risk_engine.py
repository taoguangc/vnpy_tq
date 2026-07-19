"""RiskEngine：第一版只提供 stop / target 接口。"""

from __future__ import annotations

from typing import Optional

from strategies.paaf.config import DEFAULT_CONFIG, PAAFConfig
from strategies.paaf.domain import Direction, Signal


class RiskEngine:
    """v0.1 骨架。Commit 002 再接入 ATR / 结构止损。"""

    def __init__(self, config: PAAFConfig | None = None) -> None:
        self._config = config or DEFAULT_CONFIG

    def stop(self, signal: Signal) -> Optional[float]:
        if signal.stop is not None:
            return signal.stop
        if signal.entry is None:
            return None
        buffer = self._config.tick_size
        if signal.direction is Direction.LONG:
            return signal.entry - buffer
        return signal.entry + buffer

    def target(self, signal: Signal) -> Optional[float]:
        return signal.target
