"""PAAF 最小配置。指标周期属于配置，不属于 Domain。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PAAFConfig:
    """第一版只保留五类参数。"""

    ema_period: int = 20
    atr_period: int = 14
    adx_period: int = 14
    risk_per_trade: float = 0.01
    tick_size: float = 1.0
    framework_version: str = "0.2.3"

    def __post_init__(self) -> None:
        if min(self.ema_period, self.atr_period, self.adx_period) <= 0:
            raise ValueError("指标周期必须大于 0")
        if not 0.0 < self.risk_per_trade <= 1.0:
            raise ValueError("risk_per_trade 必须在 (0, 1]")
        if self.tick_size <= 0.0:
            raise ValueError("tick_size 必须大于 0")


DEFAULT_CONFIG = PAAFConfig()
