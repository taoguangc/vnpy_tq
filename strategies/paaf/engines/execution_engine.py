"""ExecutionEngine：为 vn.py / CTP / IB 适配预留边界。"""

from __future__ import annotations

from strategies.paaf.domain import Signal


class ExecutionEngine:
    """Commit 001 仅保留接口；不直接依赖具体网关。"""

    def submit(self, signal: Signal) -> None:
        del signal
        raise NotImplementedError("ExecutionEngine.submit 将在 Commit 002 接入 vn.py")
