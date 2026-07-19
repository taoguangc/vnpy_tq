"""ContextEngine：只发布 UNKNOWN / TREND / RANGE。"""

from __future__ import annotations

from typing import Any

from strategies.paaf.config import DEFAULT_CONFIG, PAAFConfig
from strategies.paaf.domain import Context, MarketState


class ContextEngine:
    """v0.1 接口：update(am) / get_context()。

    实现细节留给 Commit 002；当前始终返回 UNKNOWN，用于验证管线。
    """

    def __init__(self, config: PAAFConfig | None = None) -> None:
        self._config = config or DEFAULT_CONFIG
        self._context = Context(market_state=MarketState.UNKNOWN)

    def update(self, am: Any) -> Context:
        del am  # Commit 002 使用 ArrayManager 计算 TREND / RANGE
        self._context = Context(market_state=MarketState.UNKNOWN)
        return self._context

    def get_context(self) -> Context:
        return self._context
