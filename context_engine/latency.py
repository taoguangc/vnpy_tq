"""Latency probe — bar close → ContextState publish only."""

from __future__ import annotations

import time

import numpy as np
import pandas as pd

from context_engine.publisher import ContextStatePublisher, PublisherConfig


def measure_publish_latency_ms(
    df: pd.DataFrame,
    *,
    instrument: str,
    manifest_id: str | None = None,
    max_bars: int = 5000,
) -> dict:
    sample = df.iloc[: max(max_bars, 50)].copy()
    pub = ContextStatePublisher(
        PublisherConfig(instrument=instrument, manifest_id=manifest_id)
    )
    latencies: list[float] = []
    for row in sample.itertuples(index=False):
        t0 = time.perf_counter()
        pub.update_bar(
            timestamp=pd.Timestamp(row.dt_cst),
            high=float(row.high),
            low=float(row.low),
        )
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000.0)
    arr = np.asarray(latencies, dtype=float)
    return {
        "n_bars": int(arr.size),
        "p50_ms": float(np.percentile(arr, 50)),
        "p95_ms": float(np.percentile(arr, 95)),
        "p99_ms": float(np.percentile(arr, 99)),
        "max_ms": float(arr.max()),
        "threshold_p99_ms": 100.0,
        "pass_p99": bool(float(np.percentile(arr, 99)) < 100.0),
        "scope": "bar_close_to_ContextState_publish_only",
        "excluded": [
            "strategy_decision",
            "order_routing",
            "exchange_latency",
            "broker_feed",
        ],
    }
