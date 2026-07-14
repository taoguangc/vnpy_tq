# -*- coding: utf-8
"""Event Research Framework — Phase 1."""
from research.event_engine.quality_score import (
    FULL_THRESHOLD,
    HALF_THRESHOLD,
    QualityScoreProfile,
    get_quality_profile,
    score_events,
)
from research.event_engine.runner import EventStudyRunner, run_event_study
from research.event_engine.schema import EventRecord, FWD_HORIZONS

__all__ = [
    "EventRecord",
    "EventStudyRunner",
    "FWD_HORIZONS",
    "FULL_THRESHOLD",
    "HALF_THRESHOLD",
    "QualityScoreProfile",
    "get_quality_profile",
    "run_event_study",
    "score_events",
]
