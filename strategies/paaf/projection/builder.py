"""Projection Builder entry (Portfolio + Validation consumers)."""

from __future__ import annotations

from datetime import datetime

from strategies.paaf.projection.models import PortfolioProjection
from strategies.paaf.projection.portfolio import build_portfolio_projection
from strategies.paaf.projection.read_view import EvidenceReadView
from strategies.paaf.projection.validation import (
    build_promotion_readiness,
    build_validation_comparison,
    find_evidence,
)
from strategies.paaf.projection.validation_models import (
    EvidenceSnapshot,
    PromotionReadinessView,
    ValidationComparisonView,
)


class ProjectionBuilder:
    """Read-only Projection orchestration; no Repository write path."""

    def __init__(self, source: EvidenceReadView | object) -> None:
        self._view = EvidenceReadView.wrap(source)

    @property
    def view(self) -> EvidenceReadView:
        return self._view

    def build_portfolio(
        self,
        *,
        built_at: datetime | None = None,
    ) -> PortfolioProjection:
        return build_portfolio_projection(self._view, built_at=built_at)

    def build_validation_comparison(
        self,
        *,
        experiment_ids: tuple[str, ...] | None = None,
        built_at: datetime | None = None,
    ) -> ValidationComparisonView:
        return build_validation_comparison(
            self._view,
            experiment_ids=experiment_ids,
            built_at=built_at,
        )

    def find_evidence(
        self,
        *,
        experiment_id: str | None = None,
        symbol: str | None = None,
        evidence_type: str | None = None,
        classification: str | None = None,
        status: str | None = None,
    ) -> tuple[EvidenceSnapshot, ...]:
        return find_evidence(
            self._view,
            experiment_id=experiment_id,
            symbol=symbol,
            evidence_type=evidence_type,
            classification=classification,
            status=status,
        )

    def build_promotion_readiness(
        self,
        *,
        experiment_id: str,
        evidence_id: str,
    ) -> PromotionReadinessView:
        return build_promotion_readiness(
            self._view,
            experiment_id=experiment_id,
            evidence_id=evidence_id,
        )
