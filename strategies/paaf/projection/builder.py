"""Projection Builder entry (Portfolio is the first consumer)."""

from __future__ import annotations

from datetime import datetime

from strategies.paaf.projection.models import PortfolioProjection
from strategies.paaf.projection.portfolio import build_portfolio_projection
from strategies.paaf.projection.read_view import EvidenceReadView


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
