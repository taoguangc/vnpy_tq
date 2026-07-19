"""PAAF 领域模型（Domain）。

只放通用语言对象。禁止放入指标定义、仓位、订单或 vn.py / numpy / pandas / talib 依赖。
允许：dataclass、Enum、typing、标准库类型。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

# Documented extras keys (values are research/diagnostic; not MarketState).
EXTRAS_TREND_BIAS = "trend_bias"
EXTRAS_STATE_CONFIDENCE = "state_confidence"
EXTRAS_COMPRESSION_SCORE = "compression_score"


class Direction(str, Enum):
    """交易方向。无信号用 ``None``，不要构造 Direction.NONE 的 Signal。"""

    LONG = "LONG"
    SHORT = "SHORT"
    NONE = "NONE"


class MarketState(str, Enum):
    """一级市场状态（v0.1.1 基线）。不编码方向、强度或实验性信息。"""

    UNKNOWN = "UNKNOWN"
    TREND = "TREND"
    RANGE = "RANGE"


class Session(str, Enum):
    """交易时段抽象。稳定领域模型，非实验对象。"""

    DAY = "DAY"
    NIGHT = "NIGHT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Context:
    """ContextEngine 发布的只读市场上下文（Semantic Layer）。

    符合 ``docs/specs/CONTEXT_ENGINE_SPEC.md`` v1.0.0。
    ``extras`` 在构造后为只读 MappingProxyType。
    """

    symbol: str = ""
    datetime: Optional[datetime] = None
    session: Session = Session.UNKNOWN
    market_state: MarketState = MarketState.UNKNOWN
    extras: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.extras, MappingProxyType):
            object.__setattr__(self, "extras", MappingProxyType(dict(self.extras)))


@dataclass(frozen=True)
class DetectorInfo:
    """Detector 身份信息，供 Registry / Logger / Dashboard 使用。"""

    name: str
    version: str
    description: str = ""
    author: str = "PAAF"
    status: str = "Candidate"


@dataclass(frozen=True)
class Signal:
    """Detector 输出。

    ``confidence`` 预留给 Opportunity Score；v0.1 固定为 1.0。
    """

    detector: str
    direction: Direction
    confidence: float = 1.0
    entry: Optional[float] = None
    stop: Optional[float] = None
    target: Optional[float] = None
    reason: str = ""
    extras: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.direction is Direction.NONE:
            raise ValueError("无信号请返回 None，不能构造 Direction.NONE Signal")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("Signal.confidence 必须在 [0, 1]")
        if not isinstance(self.extras, MappingProxyType):
            object.__setattr__(self, "extras", MappingProxyType(dict(self.extras)))


@dataclass(frozen=True)
class TradeRecord:
    """冻结的交易记录；可直接 ``asdict`` 写出 CSV。"""

    run_id: str
    experiment_id: str
    version: str
    symbol: str
    detector: str
    context: str
    direction: str
    entry: float
    exit: float
    stop: float
    target: Optional[float]
    bars: int
    mfe: float
    mae: float
    pnl: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


TRADE_RECORD_FIELDS: tuple[str, ...] = tuple(TradeRecord.__dataclass_fields__)


def make_experiment_id(
    symbol: str,
    version: str,
    trading_date: Optional[date] = None,
) -> str:
    """生成 ``YYYYMMDD_symbol_vX.Y.Z`` 形式的实验 ID。"""

    symbol_key = symbol.strip().lower()
    version_key = version.strip()
    if not symbol_key:
        raise ValueError("symbol 不能为空")
    if not version_key:
        raise ValueError("version 不能为空")
    if not version_key.startswith("v"):
        version_key = f"v{version_key}"
    day = trading_date or date.today()
    return f"{day:%Y%m%d}_{symbol_key}_{version_key}"
