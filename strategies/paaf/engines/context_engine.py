"""ContextEngine：发布不可变 Context（Semantic Layer）。

v0.1.1：只实现生命周期与契约，不做 Market State 算法。
``market_state`` 始终为 ``UNKNOWN``（Context Framework，非 Market State Framework）。

规范：``docs/specs/CONTEXT_ENGINE_SPEC.md`` v1.0.0 / Decision 009。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from strategies.paaf.config import DEFAULT_CONFIG, PAAFConfig
from strategies.paaf.domain import Context, MarketState, Session


class ContextEngine:
    """One Symbol → One ContextEngine。不保证线程安全。"""

    def __init__(
        self,
        config: PAAFConfig | None = None,
        *,
        symbol: str = "",
    ) -> None:
        self._config = config or DEFAULT_CONFIG
        self._symbol = symbol
        self._context = Context(
            symbol=symbol,
            session=Session.UNKNOWN,
            market_state=MarketState.UNKNOWN,
        )

    def update(
        self,
        window: Any,
        *,
        symbol: Optional[str] = None,
        datetime: Optional[datetime] = None,
        session: Session = Session.UNKNOWN,
    ) -> Context:
        """每根信号 Bar：构造并发布新的 frozen Context。

        ``window`` 在 v0.1.1 不参与状态判定（无 Market State 算法）。
        """

        del window  # Framework only; no TREND/RANGE/COMPRESSION classification yet
        if symbol is not None:
            self._symbol = symbol
        ctx = Context(
            symbol=self._symbol,
            datetime=datetime,
            session=session,
            market_state=MarketState.UNKNOWN,
            extras={},
        )
        return self.publish(self.freeze(ctx))

    def freeze(self, context: Context) -> Context:
        """发布前冻结步骤。Domain ``Context`` 已是 frozen；此处做类型校验。"""

        if not isinstance(context, Context):
            raise TypeError("freeze 只接受 domain.Context")
        return context

    def publish(self, context: Context) -> Context:
        """将 Context 设为当前发布实例；此后下游只读。"""

        frozen = self.freeze(context)
        self._context = frozen
        return self._context

    def get_context(self) -> Context:
        """返回最近一次发布的 Context。"""

        return self._context

    def reset(self) -> Context:
        """回到 market_state=UNKNOWN；保留当前 symbol。"""

        return self.publish(
            Context(
                symbol=self._symbol,
                session=Session.UNKNOWN,
                market_state=MarketState.UNKNOWN,
            )
        )
