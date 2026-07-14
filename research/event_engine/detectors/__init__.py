# -*- coding: utf-8
"""Event detector 注册表。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterator

import pandas as pd

from research.event_engine.detectors import (
    breakout_pullback,
    compression_breakout,
    failed_breakout,
    first_pullback,
)
from research.event_engine.schema import EventRecord


@dataclass(frozen=True)
class DetectorSpec:
    name: str
    detect: Callable[..., list[EventRecord]]
    prepare: Callable[[pd.DataFrame], pd.DataFrame] | None = None
    segment: Callable[[pd.DataFrame], Iterator[tuple[str, pd.DataFrame]]] | None = None
    aliases: tuple[str, ...] = ()


DETECTORS: dict[str, DetectorSpec] = {}


def _register(spec: DetectorSpec) -> None:
    DETECTORS[spec.name] = spec
    for alias in spec.aliases:
        DETECTORS[alias] = spec


_register(
    DetectorSpec(
        name="failed_breakout",
        aliases=("S3", "S3_failed_breakout"),
        detect=failed_breakout.detect_events,
        prepare=failed_breakout.prepare_features,
        segment=failed_breakout.segment_events,
    )
)

_register(
    DetectorSpec(
        name="compression_breakout",
        aliases=("S1", "S1_compression_breakout"),
        detect=compression_breakout.detect_events,
        prepare=compression_breakout.prepare_features,
        segment=compression_breakout.segment_events,
    )
)

_register(
    DetectorSpec(
        name="first_pullback",
        aliases=("S2", "S2_first_pullback"),
        detect=first_pullback.detect_events,
        prepare=first_pullback.prepare_features,
        segment=first_pullback.segment_events,
    )
)

_register(
    DetectorSpec(
        name="breakout_pullback",
        aliases=("BP", "BP_breakout_pullback"),
        detect=breakout_pullback.detect_events,
        prepare=breakout_pullback.prepare_features,
        segment=breakout_pullback.segment_events,
    )
)


def get_detector(name: str) -> DetectorSpec:
    key = name.strip()
    if key not in DETECTORS:
        known = sorted({s.name for s in DETECTORS.values()})
        raise KeyError(f"unknown setup detector: {name!r}; known: {known}")
    return DETECTORS[key]
