"""Detector 抽象接口。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from strategies.paaf.domain import Context, DetectorInfo, Direction, Signal
from strategies.paaf.metadata import DetectorMetadata


class BaseDetector(ABC):
    """纯检测接口：输入行情窗口与 Context，输出 Signal 或 None。

    禁止访问持仓、下单、修改 Strategy。
    ``am`` 是只读行情窗口（例如 vn.py ArrayManager），Domain 不依赖 vn.py。
    """

    metadata: DetectorMetadata = DetectorMetadata(
        name="",
        version="0.1.0",
    )

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if cls is BaseDetector:
            return
        meta = getattr(cls, "metadata", None)
        if not isinstance(meta, DetectorMetadata) or not meta.name:
            raise TypeError(f"{cls.__name__} 必须定义 metadata.name")

    @abstractmethod
    def detect(self, am: Any, context: Context) -> Optional[Signal]:
        """识别形态。无信号返回 None。"""

    @property
    def info(self) -> DetectorInfo:
        return self.metadata.to_info()

    def make_signal(
        self,
        direction: Direction,
        *,
        confidence: float = 1.0,
        entry: Optional[float] = None,
        stop: Optional[float] = None,
        target: Optional[float] = None,
        reason: str = "",
    ) -> Signal:
        return Signal(
            detector=self.metadata.name,
            direction=direction,
            confidence=confidence,
            entry=entry,
            stop=stop,
            target=target,
            reason=reason,
        )
