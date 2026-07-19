"""Generic immutable Evaluation contracts for PAAF Phase 2."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import math
from types import MappingProxyType
from typing import Any, Mapping

from strategies.paaf.evidence.models import EVIDENCE_DECISIONS


SCHEMA_VERSION = "1.0"
FORBIDDEN_TRADING_KEYS = frozenset({
    "action",
    "buy",
    "direction",
    "sell",
    "side",
    "weight",
})

OutcomeValue = float | str
WindowValue = int | str


def _require_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} 不能为空")


def _require_schema(value: str, model_name: str) -> None:
    if value != SCHEMA_VERSION:
        raise ValueError(f"不支持 {model_name} schema: {value}")


def _freeze_mapping(
    value: Mapping[str, Any],
    *,
    field_name: str,
    allowed_types: tuple[type, ...],
    forbid_trading_keys: bool = False,
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{field_name} 必须是 Mapping")

    copied: dict[str, Any] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise TypeError(f"{field_name} 的键必须是 str")
        if forbid_trading_keys and key.lower() in FORBIDDEN_TRADING_KEYS:
            raise ValueError(f"{field_name} 禁止交易语义键: {key}")
        if isinstance(item, bool) and bool not in allowed_types:
            raise TypeError(f"{field_name} 不允许 bool 值")
        if not isinstance(item, allowed_types):
            allowed = ", ".join(kind.__name__ for kind in allowed_types)
            raise TypeError(f"{field_name} 的值只允许 {allowed}")
        if isinstance(item, float) and not math.isfinite(item):
            raise ValueError(f"{field_name} 的数值必须有限")
        copied[key] = item
    return MappingProxyType(copied)


def _require_sample_n(value: float | int) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("sample_n 必须是 int 或 float")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized < 0:
        raise ValueError("sample_n 必须是有限非负数")
    return normalized


def _require_finite_value(value: float | int, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} 必须是 int 或 float")
    normalized = float(value)
    if not math.isfinite(normalized):
        raise ValueError(f"{field_name} 必须是有限数值")
    return normalized


def _require_unique_refs(refs: tuple[str, ...], field_name: str) -> None:
    for ref in refs:
        _require_text(ref, field_name)
    if len(refs) != len(set(refs)):
        raise ValueError(f"{field_name} 不允许重复")


@dataclass(frozen=True)
class OutcomeDefinition:
    """Pre-registered definition of what an experiment measures."""

    outcome_id: str
    name: str
    window: Mapping[str, WindowValue]
    unit: str = ""
    description: str = ""
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        _require_text(self.outcome_id, "outcome_id")
        _require_text(self.name, "name")
        _require_schema(self.schema_version, "OutcomeDefinition")
        object.__setattr__(
            self,
            "window",
            _freeze_mapping(
                self.window,
                field_name="window",
                allowed_types=(int, str),
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome_id": self.outcome_id,
            "name": self.name,
            "window": dict(self.window),
            "unit": self.unit,
            "description": self.description,
            "schema_version": self.schema_version,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "OutcomeDefinition":
        return cls(
            outcome_id=str(data["outcome_id"]),
            name=str(data["name"]),
            window=data.get("window", {}),
            unit=str(data.get("unit", "")),
            description=str(data.get("description", "")),
            schema_version=str(data.get("schema_version", "")),
        )


@dataclass(frozen=True)
class OutcomeRecord:
    """Caller-supplied aggregate values for one OutcomeDefinition."""

    definition_id: str
    values: Mapping[str, OutcomeValue]
    sample_n: float
    artifact_refs: tuple[str, ...] = ()
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        _require_text(self.definition_id, "definition_id")
        _require_schema(self.schema_version, "OutcomeRecord")
        object.__setattr__(
            self,
            "values",
            _freeze_mapping(
                self.values,
                field_name="values",
                allowed_types=(float, str),
                forbid_trading_keys=True,
            ),
        )
        object.__setattr__(self, "sample_n", _require_sample_n(self.sample_n))
        refs = tuple(self.artifact_refs)
        _require_unique_refs(refs, "artifact_refs")
        object.__setattr__(self, "artifact_refs", refs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "definition_id": self.definition_id,
            "values": dict(self.values),
            "sample_n": self.sample_n,
            "artifact_refs": list(self.artifact_refs),
            "schema_version": self.schema_version,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "OutcomeRecord":
        return cls(
            definition_id=str(data["definition_id"]),
            values=data.get("values", {}),
            sample_n=float(data["sample_n"]),
            artifact_refs=tuple(data.get("artifact_refs", ())),
            schema_version=str(data.get("schema_version", "")),
        )


@dataclass(frozen=True)
class MetricDefinition:
    """Pre-registered metric identity; formula_id is not executable code."""

    metric_id: str
    name: str
    formula_id: str
    higher_is_better: bool | None = None
    description: str = ""
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        _require_text(self.metric_id, "metric_id")
        _require_text(self.name, "name")
        _require_text(self.formula_id, "formula_id")
        if self.higher_is_better is not None and not isinstance(
            self.higher_is_better,
            bool,
        ):
            raise TypeError("higher_is_better 必须是 bool 或 None")
        _require_schema(self.schema_version, "MetricDefinition")

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "name": self.name,
            "formula_id": self.formula_id,
            "higher_is_better": self.higher_is_better,
            "description": self.description,
            "schema_version": self.schema_version,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "MetricDefinition":
        return cls(
            metric_id=str(data["metric_id"]),
            name=str(data["name"]),
            formula_id=str(data["formula_id"]),
            higher_is_better=data.get("higher_is_better"),
            description=str(data.get("description", "")),
            schema_version=str(data.get("schema_version", "")),
        )


@dataclass(frozen=True)
class MetricRecord:
    """Caller-supplied scalar result for one MetricDefinition."""

    metric_id: str
    value: float
    sample_n: float
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        _require_text(self.metric_id, "metric_id")
        _require_schema(self.schema_version, "MetricRecord")
        object.__setattr__(
            self,
            "value",
            _require_finite_value(self.value, "value"),
        )
        object.__setattr__(self, "sample_n", _require_sample_n(self.sample_n))

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "value": self.value,
            "sample_n": self.sample_n,
            "schema_version": self.schema_version,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "MetricRecord":
        return cls(
            metric_id=str(data["metric_id"]),
            value=float(data["value"]),
            sample_n=float(data["sample_n"]),
            schema_version=str(data.get("schema_version", "")),
        )


@dataclass(frozen=True)
class EvaluationResult:
    """Immutable aggregation of pre-registered outcomes and metrics."""

    evaluation_id: str
    experiment_id: str
    evidence_id: str | None
    hypothesis: str
    decision: str
    outcome_refs: tuple[str, ...]
    metric_refs: tuple[str, ...]
    outcomes: tuple[OutcomeRecord, ...]
    metrics: tuple[MetricRecord, ...]
    created_at: datetime
    notes: str = ""
    metadata: Mapping[str, str] = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        for field_name in ("evaluation_id", "experiment_id", "hypothesis"):
            _require_text(getattr(self, field_name), field_name)
        if self.evidence_id is not None:
            _require_text(self.evidence_id, "evidence_id")
        if self.decision not in EVIDENCE_DECISIONS:
            raise ValueError("decision 必须是 KEEP、REVERT 或 HOLD")
        if self.decision == "KEEP" and self.evidence_id is None:
            raise ValueError("KEEP EvaluationResult 必须引用 evidence_id")
        if self.created_at.tzinfo is None:
            raise ValueError("created_at 必须包含时区")
        _require_schema(self.schema_version, "EvaluationResult")

        outcome_refs = tuple(self.outcome_refs)
        metric_refs = tuple(self.metric_refs)
        outcomes = tuple(self.outcomes)
        metrics = tuple(self.metrics)
        _require_unique_refs(outcome_refs, "outcome_refs")
        _require_unique_refs(metric_refs, "metric_refs")
        if any(not isinstance(record, OutcomeRecord) for record in outcomes):
            raise TypeError("outcomes 只允许 OutcomeRecord")
        if any(not isinstance(record, MetricRecord) for record in metrics):
            raise TypeError("metrics 只允许 MetricRecord")

        outcome_ids = tuple(record.definition_id for record in outcomes)
        metric_ids = tuple(record.metric_id for record in metrics)
        if set(outcome_ids) != set(outcome_refs):
            raise ValueError("OutcomeRecord 必须与 outcome_refs 完全对应")
        if set(metric_ids) != set(metric_refs):
            raise ValueError("MetricRecord 必须与 metric_refs 完全对应")
        if len(outcome_ids) != len(set(outcome_ids)):
            raise ValueError("outcomes 不允许重复 definition_id")
        if len(metric_ids) != len(set(metric_ids)):
            raise ValueError("metrics 不允许重复 metric_id")

        object.__setattr__(self, "outcome_refs", outcome_refs)
        object.__setattr__(self, "metric_refs", metric_refs)
        object.__setattr__(self, "outcomes", outcomes)
        object.__setattr__(self, "metrics", metrics)
        object.__setattr__(
            self,
            "metadata",
            _freeze_mapping(
                self.metadata,
                field_name="metadata",
                allowed_types=(str,),
                forbid_trading_keys=True,
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evaluation_id": self.evaluation_id,
            "experiment_id": self.experiment_id,
            "evidence_id": self.evidence_id,
            "hypothesis": self.hypothesis,
            "decision": self.decision,
            "outcome_refs": list(self.outcome_refs),
            "metric_refs": list(self.metric_refs),
            "outcomes": [record.to_dict() for record in self.outcomes],
            "metrics": [record.to_dict() for record in self.metrics],
            "created_at": self.created_at.isoformat(),
            "notes": self.notes,
            "metadata": dict(self.metadata),
            "schema_version": self.schema_version,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "EvaluationResult":
        raw_outcomes = data.get("outcomes", ())
        raw_metrics = data.get("metrics", ())
        if not isinstance(raw_outcomes, (list, tuple)):
            raise TypeError("outcomes 必须是 list 或 tuple")
        if not isinstance(raw_metrics, (list, tuple)):
            raise TypeError("metrics 必须是 list 或 tuple")
        raw_evidence_id = data.get("evidence_id")
        return cls(
            evaluation_id=str(data["evaluation_id"]),
            experiment_id=str(data["experiment_id"]),
            evidence_id=(
                str(raw_evidence_id)
                if raw_evidence_id is not None
                else None
            ),
            hypothesis=str(data["hypothesis"]),
            decision=str(data["decision"]),
            outcome_refs=tuple(data.get("outcome_refs", ())),
            metric_refs=tuple(data.get("metric_refs", ())),
            outcomes=tuple(
                OutcomeRecord.from_dict(record)
                for record in raw_outcomes
            ),
            metrics=tuple(
                MetricRecord.from_dict(record)
                for record in raw_metrics
            ),
            created_at=datetime.fromisoformat(str(data["created_at"])),
            notes=str(data.get("notes", "")),
            metadata=data.get("metadata", {}),
            schema_version=str(data.get("schema_version", "")),
        )
