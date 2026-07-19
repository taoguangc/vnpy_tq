"""Feature Sensor execution contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Mapping

from strategies.paaf.sensors.models import FeatureResult


ParameterValue = str | int | float | bool


class BaseFeatureSensor(ABC):
    """Read-only observation interface; never emits trading semantics."""

    sensor_id: str = ""
    sensor_version: str = ""

    @abstractmethod
    def observe(
        self,
        *,
        symbol: str,
        timeframe: str,
        timestamp: datetime,
        window: Mapping[str, Any],
        context: Any | None = None,
        parameters: Mapping[str, ParameterValue] | None = None,
    ) -> FeatureResult | None:
        """Produce one FeatureResult or None for sparse emit mode."""
