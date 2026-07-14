# -*- coding: utf-8
"""Phase 3 — Setup Quality Score（研究层 sizing 分档，非下单）。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd

FULL_THRESHOLD = 0.8
HALF_THRESHOLD = 0.6


def _clamp01(x: float) -> float:
    if x != x:
        return 0.0
    return float(max(0.0, min(1.0, x)))


def _col(row: pd.Series, name: str) -> float:
    if name in row.index and row[name] == row[name]:
        return float(row[name])
    feat = f"feat_{name}"
    if feat in row.index and row[feat] == row[feat]:
        return float(row[feat])
    return float("nan")


FeatureFn = Callable[[pd.Series], float]


@dataclass(frozen=True)
class QualityScoreProfile:
    setup: str
    components: tuple[tuple[str, float, FeatureFn], ...] = ()
    full_threshold: float = FULL_THRESHOLD
    half_threshold: float = HALF_THRESHOLD

    def score_row(self, row: pd.Series) -> tuple[float, dict[str, float]]:
        parts: dict[str, float] = {}
        total = 0.0
        weight_sum = 0.0
        for name, weight, fn in self.components:
            if weight <= 0:
                continue
            val = _clamp01(fn(row))
            parts[name] = val
            total += weight * val
            weight_sum += weight
        score = total / weight_sum if weight_sum > 0 else 0.0
        return score, parts

    def bucket(self, score: float) -> str:
        if score >= self.full_threshold:
            return "FULL"
        if score >= self.half_threshold:
            return "HALF"
        return "SKIP"


# --- feature normalizers (0~1) ---


def _feat_compression(row: pd.Series) -> float:
    return _col(row, "compression_score")


def _feat_er(row: pd.Series) -> float:
    er = _col(row, "er")
    return _clamp01(er / 0.5)


def _feat_env(row: pd.Series) -> float:
    return _col(row, "env_score")


def _feat_alpha(row: pd.Series) -> float:
    return _col(row, "alpha_strength")


def _feat_body(row: pd.Series) -> float:
    return _col(row, "body_ratio")


def _feat_narrow_range(row: pd.Series) -> float:
    w = _col(row, "prior_range_width_atr")
    if w != w:
        return 0.0
    return _clamp01(1.0 - w / 1.5)


def _feat_trend_leg(row: pd.Series) -> float:
    x = _col(row, "trend_leg_atr")
    if x != x:
        return 0.0
    return _clamp01(x / 2.0)


def _feat_shallow_pullback(row: pd.Series) -> float:
    d = _col(row, "pullback_depth_atr")
    if d != d:
        return 0.0
    return _clamp01(1.0 - d / 0.5)


def _feat_wick(row: pd.Series) -> float:
    return _clamp01(_col(row, "wick_ratio"))


def _feat_climax(row: pd.Series) -> float:
    direction = int(row.get("direction", 0))
    if direction < 0:
        raw = _col(row, "climax_up")
    else:
        raw = _col(row, "climax_down")
    if raw != raw:
        return 0.0
    return _clamp01(abs(raw) / 3.0)


def _feat_breakout_size(row: pd.Series) -> float:
    b = _col(row, "breakout_size")
    if b != b:
        return 0.0
    return _clamp01(b / 5.0)


def _feat_session(row: pd.Series) -> float:
    h = int(row.get("hour_cst", -1))
    if h in (9, 10, 13, 14):
        return 0.85
    if h in (11, 21, 22):
        return 0.55
    return 0.35


def _feat_expansion(row: pd.Series) -> float:
    comp = _feat_compression(row)
    atr_r = _col(row, "atr_ratio")
    if atr_r != atr_r:
        return 0.5
    return _clamp01(0.5 * (1.0 - comp) + 0.5 * min(1.0, atr_r / 1.2))


PROFILE_S1 = QualityScoreProfile(
    setup="compression_breakout",
    components=(
        ("compression", 0.35, _feat_compression),
        ("narrow_range", 0.25, _feat_narrow_range),
        ("trend_env", 0.20, _feat_er),
        ("body", 0.10, _feat_body),
        ("session", 0.10, _feat_session),
    ),
)

PROFILE_S2 = QualityScoreProfile(
    setup="first_pullback",
    components=(
        ("trend_leg", 0.35, _feat_trend_leg),
        ("env", 0.25, _feat_env),
        ("shallow_pullback", 0.20, _feat_shallow_pullback),
        ("alpha", 0.10, _feat_alpha),
        ("body", 0.10, _feat_body),
    ),
)

PROFILE_S3 = QualityScoreProfile(
    setup="failed_breakout",
    components=(
        ("climax", 0.35, _feat_climax),
        ("wick", 0.25, _feat_wick),
        ("compression", 0.15, _feat_compression),
        ("breakout", 0.15, _feat_breakout_size),
        ("session", 0.10, _feat_session),
    ),
)

PROFILES: dict[str, QualityScoreProfile] = {
    "compression_breakout": PROFILE_S1,
    "S1": PROFILE_S1,
    "first_pullback": PROFILE_S2,
    "S2": PROFILE_S2,
    "failed_breakout": PROFILE_S3,
    "S3": PROFILE_S3,
}


def get_quality_profile(setup: str) -> QualityScoreProfile:
    key = setup.strip()
    if key not in PROFILES:
        known = sorted({p.setup for p in PROFILES.values()})
        raise KeyError(f"no quality profile for {setup!r}; known setups: {known}")
    return PROFILES[key]


def score_events(events: pd.DataFrame, setup: str) -> pd.DataFrame:
    if events.empty:
        out = events.copy()
        out["quality_score"] = pd.Series(dtype=float)
        out["size_bucket"] = pd.Series(dtype=str)
        return out

    profile = get_quality_profile(setup)
    scores: list[float] = []
    buckets: list[str] = []
    comp_cols: dict[str, list[float]] = {}

    for _, row in events.iterrows():
        score, parts = profile.score_row(row)
        scores.append(score)
        buckets.append(profile.bucket(score))
        for k, v in parts.items():
            comp_cols.setdefault(f"q_{k}", []).append(v)

    out = events.copy()
    out["quality_score"] = scores
    out["size_bucket"] = buckets
    for col, vals in comp_cols.items():
        out[col] = vals
    return out


def quality_segments(events: pd.DataFrame):
    if events.empty or "quality_score" not in events.columns:
        return
    yield "Q_FULL", events[events["size_bucket"] == "FULL"]
    yield "Q_HALF", events[events["size_bucket"] == "HALF"]
    yield "Q_SKIP", events[events["size_bucket"] == "SKIP"]
    try:
        for q, sub in events.groupby(
            pd.qcut(events["quality_score"], 5, duplicates="drop"), observed=True
        ):
            yield f"Score Q{q}", sub
    except ValueError:
        pass
