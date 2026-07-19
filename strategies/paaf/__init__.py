"""PAAF Framework v0.2.1

开发顺序：Domain → Interface → Engine → Strategy → Detector
Spec-Driven：先改 docs/specs，再改实现。
"""

from strategies.paaf.base_detector import BaseDetector
from strategies.paaf.config import DEFAULT_CONFIG, PAAFConfig
from strategies.paaf.domain import (
    EXTRAS_COMPRESSION_SCORE,
    EXTRAS_STATE_CONFIDENCE,
    EXTRAS_TREND_BIAS,
    TRADE_RECORD_FIELDS,
    Context,
    DetectionResult,
    DetectorInfo,
    DetectorStatus,
    DetectorTag,
    Direction,
    MarketState,
    PatternState,
    Session,
    Signal,
    TradeRecord,
    make_experiment_id,
)
from strategies.paaf.engines import (
    ContextEngine,
    ExecutionEngine,
    RiskEngine,
    SignalEngine,
    TradeLogger,
)
from strategies.paaf.metadata import DetectorMetadata
from strategies.paaf.paaf_strategy import PaafStrategy
from strategies.paaf.registry import DetectorRegistry, build_registry

__all__ = [
    "DEFAULT_CONFIG",
    "EXTRAS_COMPRESSION_SCORE",
    "EXTRAS_STATE_CONFIDENCE",
    "EXTRAS_TREND_BIAS",
    "TRADE_RECORD_FIELDS",
    "BaseDetector",
    "Context",
    "ContextEngine",
    "DetectionResult",
    "DetectorInfo",
    "DetectorMetadata",
    "DetectorRegistry",
    "DetectorStatus",
    "DetectorTag",
    "Direction",
    "ExecutionEngine",
    "MarketState",
    "PAAFConfig",
    "PaafStrategy",
    "PatternState",
    "RiskEngine",
    "Session",
    "Signal",
    "SignalEngine",
    "TradeLogger",
    "TradeRecord",
    "build_registry",
    "make_experiment_id",
]

__version__ = "0.2.1"
