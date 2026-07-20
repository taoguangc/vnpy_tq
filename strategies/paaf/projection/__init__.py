"""Projection Layer — read-only views over Evidence Repository (Decision 018)."""

from strategies.paaf.projection.builder import ProjectionBuilder
from strategies.paaf.projection.models import (
    PORTFOLIO_BUCKETS,
    PortfolioBucketSummary,
    PortfolioEvidenceRef,
    PortfolioProjection,
)
from strategies.paaf.projection.read_view import EvidenceReadView
from strategies.paaf.projection.validation_models import (
    EvidenceSnapshot,
    PromotionReadinessView,
    ValidationComparisonView,
)

__all__ = [
    "PORTFOLIO_BUCKETS",
    "EvidenceReadView",
    "EvidenceSnapshot",
    "PortfolioBucketSummary",
    "PortfolioEvidenceRef",
    "PortfolioProjection",
    "ProjectionBuilder",
    "PromotionReadinessView",
    "ValidationComparisonView",
]
