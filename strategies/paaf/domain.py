"""PAAF 领域模型（Domain）。

只放通用语言对象。禁止放入指标定义、仓位、订单或 vn.py / numpy / pandas / talib 依赖。
允许：dataclass、Enum、typing、标准库类型。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
import re
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


class DetectorTag(str, Enum):
    """Detector 标准分类标签；仅用于分类、检索与统计。"""

    COMPRESSION = "COMPRESSION"
    TREND = "TREND"
    BREAKOUT = "BREAKOUT"
    REVERSAL = "REVERSAL"
    PULLBACK = "PULLBACK"
    LIQUIDITY = "LIQUIDITY"
    DEMO = "DEMO"


class DetectorStatus(str, Enum):
    """Detector 的证据可见工程状态。"""

    EXPERIMENT = "EXPERIMENT"
    VALIDATED = "VALIDATED"
    PRODUCTION = "PRODUCTION"
    DEPRECATED = "DEPRECATED"


class OpportunityDirection(str, Enum):
    """Opportunity 描述方向；与交易层 Direction 分离。"""

    LONG = "LONG"
    SHORT = "SHORT"
    BOTH = "BOTH"
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


def _freeze_json_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
    """复制并深度冻结 JSON 兼容 Mapping。"""

    return MappingProxyType(
        {str(key): _freeze_json_value(item) for key, item in value.items()}
    )


def _freeze_json_value(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise TypeError("metadata 的键必须是 str")
        return _freeze_json_mapping(value)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json_value(item) for item in value)
    raise TypeError(f"metadata 只允许 JSON 兼容值，收到 {type(value).__name__}")


def _thaw_json_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw_json_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json_value(item) for item in value]
    return value


@dataclass(frozen=True)
class PatternState:
    """显式、可序列化的跨 bar 形态状态。"""

    name: str
    confidence: float = 1.0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("PatternState.name 不能为空")
        confidence = float(self.confidence)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("PatternState.confidence 必须在 [0, 1]")
        object.__setattr__(self, "confidence", confidence)
        object.__setattr__(self, "metadata", _freeze_json_mapping(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "confidence": self.confidence,
            "metadata": _thaw_json_value(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PatternState":
        return cls(
            name=str(data["name"]),
            confidence=float(data.get("confidence", 1.0)),
            metadata=data.get("metadata", {}),
        )


@dataclass(frozen=True)
class DetectionResult:
    """Detector 发布的唯一结构化结果（schema 1.0）。

    这是检测证据，不是交易指令。无检测时 Detector 返回 ``None``。
    """

    detector_id: str
    detector_version: str
    opportunity_id: str
    status: DetectorStatus
    direction: Direction
    confidence: float = 1.0
    tags: tuple[DetectorTag | str, ...] = ()
    entry: Optional[float] = None
    stop: Optional[float] = None
    target: Optional[float] = None
    reason: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)
    pattern_state: Optional[PatternState] = None
    evidence_refs: tuple[str, ...] = ()
    schema_version: str = "1.0"
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        if not self.detector_id.strip():
            raise ValueError("detector_id 不能为空")
        if not self.detector_version.strip():
            raise ValueError("detector_version 不能为空")
        if not self.opportunity_id.strip():
            raise ValueError("opportunity_id 不能为空")
        if self.direction is Direction.NONE:
            raise ValueError("无检测请返回 None，不能使用 Direction.NONE")

        confidence = float(self.confidence)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("DetectionResult.confidence 必须在 [0, 1]")
        object.__setattr__(self, "confidence", confidence)

        normalized_tags: list[DetectorTag | str] = []
        for tag in self.tags:
            if isinstance(tag, DetectorTag):
                normalized_tags.append(tag)
            elif isinstance(tag, str) and tag.startswith("custom:") and len(tag) > 7:
                normalized_tags.append(tag)
            else:
                raise ValueError(
                    "tags 必须是 DetectorTag 或 custom:<slug> 字符串"
                )
        object.__setattr__(self, "tags", tuple(normalized_tags))
        object.__setattr__(self, "metadata", _freeze_json_mapping(self.metadata))
        object.__setattr__(self, "evidence_refs", tuple(self.evidence_refs))

        if self.schema_version != "1.0":
            raise ValueError(f"不支持 DetectionResult schema: {self.schema_version}")
        if self.created_at.tzinfo is None:
            raise ValueError("created_at 必须包含时区")
        if self.status is DetectorStatus.PRODUCTION and not self.evidence_refs:
            raise ValueError("PRODUCTION DetectionResult 必须包含 evidence_refs")

    def to_dict(self) -> dict[str, Any]:
        """转换为 JSON 友好的 schema 1.0 字典。"""

        return {
            "detector_id": self.detector_id,
            "detector_version": self.detector_version,
            "opportunity_id": self.opportunity_id,
            "status": self.status.value,
            "direction": self.direction.value,
            "confidence": self.confidence,
            "tags": [
                tag.value if isinstance(tag, DetectorTag) else tag
                for tag in self.tags
            ],
            "entry": self.entry,
            "stop": self.stop,
            "target": self.target,
            "reason": self.reason,
            "metadata": _thaw_json_value(self.metadata),
            "pattern_state": (
                self.pattern_state.to_dict() if self.pattern_state else None
            ),
            "evidence_refs": list(self.evidence_refs),
            "schema_version": self.schema_version,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "DetectionResult":
        """从 schema 1.0 字典恢复；未知版本明确失败。"""

        schema_version = str(data.get("schema_version", ""))
        if schema_version != "1.0":
            raise ValueError(f"不支持 DetectionResult schema: {schema_version}")

        tags: list[DetectorTag | str] = []
        for raw_tag in data.get("tags", ()):
            tag = str(raw_tag)
            try:
                tags.append(DetectorTag(tag))
            except ValueError:
                tags.append(tag)

        raw_pattern = data.get("pattern_state")
        return cls(
            detector_id=str(data["detector_id"]),
            detector_version=str(data["detector_version"]),
            opportunity_id=str(data["opportunity_id"]),
            status=DetectorStatus(str(data["status"])),
            direction=Direction(str(data["direction"])),
            confidence=float(data.get("confidence", 1.0)),
            tags=tuple(tags),
            entry=data.get("entry"),
            stop=data.get("stop"),
            target=data.get("target"),
            reason=str(data.get("reason", "")),
            metadata=data.get("metadata", {}),
            pattern_state=(
                PatternState.from_dict(raw_pattern)
                if isinstance(raw_pattern, Mapping)
                else None
            ),
            evidence_refs=tuple(data.get("evidence_refs", ())),
            schema_version=schema_version,
            created_at=datetime.fromisoformat(str(data["created_at"])),
        )


@dataclass(frozen=True)
class Opportunity:
    """可审计、不可变的交易机会描述（schema 1.0）。

    Opportunity 引用 DetectionResult，但不是订单或立即交易指令。
    """

    id: str
    version: str
    status: DetectorStatus
    direction: OpportunityDirection
    market_state: Optional[MarketState]
    detector_result: DetectionResult
    evidence_refs: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)
    lineage: tuple[str, ...] = ()
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    schema_version: str = "1.0"

    def __post_init__(self) -> None:
        if not re.fullmatch(r"(?:OPP\d{2}|DEMO_[A-Z0-9_]+)", self.id):
            raise ValueError("Opportunity.id 必须是 OPPXX 或 DEMO_<SLUG>")
        if not self.version.strip():
            raise ValueError("Opportunity.version 不能为空")
        if self.detector_result.opportunity_id != self.id:
            raise ValueError(
                "detector_result.opportunity_id 必须等于 Opportunity.id"
            )

        if self.direction is OpportunityDirection.LONG:
            if self.detector_result.direction is not Direction.LONG:
                raise ValueError("LONG Opportunity 与 DetectionResult.direction 不一致")
        elif self.direction is OpportunityDirection.SHORT:
            if self.detector_result.direction is not Direction.SHORT:
                raise ValueError("SHORT Opportunity 与 DetectionResult.direction 不一致")

        evidence_refs = tuple(self.evidence_refs)
        lineage = tuple(self.lineage)
        detector_lineage = (
            f"DET:{self.detector_result.detector_id}"
            f"@{self.detector_result.detector_version}"
        )
        if detector_lineage not in lineage:
            raise ValueError(f"lineage 缺少直接来源 {detector_lineage}")
        missing_evidence = [
            ref for ref in evidence_refs if f"EXP:{ref}" not in lineage
        ]
        if missing_evidence:
            raise ValueError(
                f"lineage 缺少 evidence 来源: {', '.join(missing_evidence)}"
            )
        if not set(self.detector_result.evidence_refs).issubset(evidence_refs):
            raise ValueError(
                "Opportunity.evidence_refs 必须覆盖 DetectionResult.evidence_refs"
            )
        if self.status is DetectorStatus.PRODUCTION and not evidence_refs:
            raise ValueError("PRODUCTION Opportunity 必须包含 evidence_refs")

        if self.schema_version != "1.0":
            raise ValueError(f"不支持 Opportunity schema: {self.schema_version}")
        if self.created_at.tzinfo is None:
            raise ValueError("Opportunity.created_at 必须包含时区")

        object.__setattr__(self, "evidence_refs", evidence_refs)
        object.__setattr__(self, "metadata", _freeze_json_mapping(self.metadata))
        object.__setattr__(self, "lineage", lineage)

    def to_dict(self) -> dict[str, Any]:
        """转换为 JSON 友好的 schema 1.0 字典。"""

        return {
            "id": self.id,
            "version": self.version,
            "status": self.status.value,
            "direction": self.direction.value,
            "market_state": (
                self.market_state.value if self.market_state else None
            ),
            "detector_result": self.detector_result.to_dict(),
            "evidence_refs": list(self.evidence_refs),
            "metadata": _thaw_json_value(self.metadata),
            "lineage": list(self.lineage),
            "created_at": self.created_at.isoformat(),
            "schema_version": self.schema_version,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Opportunity":
        """从 schema 1.0 字典恢复；未知版本明确失败。"""

        schema_version = str(data.get("schema_version", ""))
        if schema_version != "1.0":
            raise ValueError(f"不支持 Opportunity schema: {schema_version}")

        raw_market_state = data.get("market_state")
        raw_detection = data.get("detector_result")
        if not isinstance(raw_detection, Mapping):
            raise TypeError("detector_result 必须是 Mapping")
        return cls(
            id=str(data["id"]),
            version=str(data["version"]),
            status=DetectorStatus(str(data["status"])),
            direction=OpportunityDirection(str(data["direction"])),
            market_state=(
                MarketState(str(raw_market_state))
                if raw_market_state is not None
                else None
            ),
            detector_result=DetectionResult.from_dict(raw_detection),
            evidence_refs=tuple(data.get("evidence_refs", ())),
            metadata=data.get("metadata", {}),
            lineage=tuple(data.get("lineage", ())),
            created_at=datetime.fromisoformat(str(data["created_at"])),
            schema_version=schema_version,
        )


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
    """Deprecated v0.2：遗留 Detector 输出，v0.3 删除。

    新 Detector 必须返回 ``DetectionResult | None``；Signal 仅供迁移期旧路径。
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
