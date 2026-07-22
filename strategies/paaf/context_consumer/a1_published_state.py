"""A1 ContextState descriptive tag publisher（research consumer）.

Implements CAP_CTX_A1 Fill v0.2 primary rule only:
  invalid | compression | expansion

Not a MarketState Spec upgrade. Not trade signal generation.
"""
from __future__ import annotations

from typing import Any


CONTEXT_VERSION = "A1-CTX-PS-v1.0.0"
SCHEMA_VERSION = "ContextState.v1"
ENGINE_ID = "paaf.context_published_state"
SMA_PERIOD = 20


def publish_a1_context_state(window: Any, *, sma_period: int = SMA_PERIOD) -> str:
    """Return primary ``context_state`` tag for the latest closed bar.

    Rule（A1 Fill v0.2）:
      if warmup fail or non-finite: invalid
      else if range_ratio < 1: compression
      else: expansion
    where range_ratio = (high-low) / SMA(range, sma_period) on bars ≤ t.
    """
    try:
        count = int(getattr(window, "count", 0) or 0)
        high = getattr(window, "high", None)
        low = getattr(window, "low", None)
        if high is None or low is None or count < int(sma_period):
            return "invalid"
        # Use last sma_period closed ranges including t
        h = [float(high[i]) for i in range(-sma_period, 0)]
        l = [float(low[i]) for i in range(-sma_period, 0)]
        ranges = [hi - lo for hi, lo in zip(h, l)]
        cur = ranges[-1]
        sma = sum(ranges) / float(sma_period)
        if not (cur == cur) or not (sma == sma) or sma <= 0:  # NaN check
            return "invalid"
        ratio = cur / sma
        if ratio < 1.0:
            return "compression"
        return "expansion"
    except (TypeError, ValueError, IndexError, ZeroDivisionError):
        return "invalid"
