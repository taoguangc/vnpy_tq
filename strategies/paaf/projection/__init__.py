"""Projection Layer — read-only views over Evidence Repository (Decision 018)."""

from strategies.paaf.projection.builder import ProjectionBuilder
from strategies.paaf.projection.models import (
    PORTFOLIO_BUCKETS,
    PortfolioBucketSummary,
    PortfolioEvidenceRef,
    PortfolioProjection,
)
from strategies.paaf.projection.read_view import EvidenceReadView

__all__ = [
    "PORTFOLIO_BUCKETS",
    "EvidenceReadView",
    "PortfolioBucketSummary",
    "PortfolioEvidenceRef",
    "PortfolioProjection",
    "ProjectionBuilder",
]
