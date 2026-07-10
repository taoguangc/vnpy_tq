# -*- coding: utf-8 -*-
"""Brooks 楔形三推（HH3）无状态探测器 — 策略与漏斗审计共用。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import numpy as np

WedgeStatus = Literal[
    "no_structure",
    "wedge_invalid:tr_order",
    "wedge_invalid:move_floor",
    "wedge_invalid:alpha",
    "wedge_valid:hh3",
    "wedge_valid:ll3",
]

TroughTier = Literal[
    "empty",
    "swing_2bar",
    "swing_1bar",
    "body_floor",
    "body_floor:narrow_v",
]


@dataclass(frozen=True, slots=True)
class WedgeBar:
    """OHLC 切片；index 为序列内下标（0=最旧）。"""

    open_price: float
    high_price: float
    low_price: float
    close_price: float
    index: int


def is_2bar_fractal_high(bars: list[WedgeBar], idx: int) -> bool:
    if idx < 2 or idx >= len(bars) - 2:
        return False
    h = [bars[i].high_price for i in range(idx - 2, idx + 3)]
    return h[2] >= h[0] and h[2] >= h[1] and h[2] > h[3] and h[2] > h[4]


def is_2bar_swing_low(bars: list[WedgeBar], idx: int) -> bool:
    if idx < 2 or idx >= len(bars) - 2:
        return False
    lows = [bars[i].low_price for i in range(idx - 2, idx + 3)]
    return (
        lows[2] <= lows[0]
        and lows[2] <= lows[1]
        and lows[2] < lows[3]
        and lows[2] < lows[4]
    )


def is_1bar_swing_low(bars: list[WedgeBar], idx: int) -> bool:
    if idx < 1 or idx >= len(bars) - 1:
        return False
    cur = bars[idx].low_price
    return cur <= bars[idx - 1].low_price and cur < bars[idx + 1].low_price


# ─── LL3 (Bullish Wedge) mirror detectors ────────────────────────────────

def is_2bar_fractal_low(bars: list[WedgeBar], idx: int) -> bool:
    """2-bar fractal low: LLHLH — idx is the lowest of 5 bars. Mirror of is_2bar_fractal_high."""
    if idx < 2 or idx >= len(bars) - 2:
        return False
    l = [bars[i].low_price for i in range(idx - 2, idx + 3)]
    return l[2] <= l[0] and l[2] <= l[1] and l[2] < l[3] and l[2] < l[4]


def is_2bar_fractal_high_for_ll3(bars: list[WedgeBar], idx: int) -> bool:
    """2-bar swing high (same as is_2bar_fractal_high, used for peak anchor in LL3)."""
    return is_2bar_fractal_high(bars, idx)


def is_1bar_swing_high(bars: list[WedgeBar], idx: int) -> bool:
    """1-bar swing high. Mirror of is_1bar_swing_low."""
    if idx < 1 or idx >= len(bars) - 1:
        return False
    cur = bars[idx].high_price
    return cur >= bars[idx - 1].high_price and cur > bars[idx + 1].high_price


def anchor_peak(bars: list[WedgeBar], i: int, j: int) -> tuple[float, TroughTier]:
    """开放区间 (i, j) 内的反弹高点 Pk_k。Mirror of anchor_trough."""
    if j <= i + 1:
        return float("nan"), "empty"

    segment = bars[i + 1 : j]
    if not segment:
        return float("nan"), "empty"

    swings_2bar = [
        b.high_price for b in segment if is_2bar_fractal_high_for_ll3(bars, b.index)
    ]
    if swings_2bar:
        return max(swings_2bar), "swing_2bar"

    swings_1bar = [
        b.high_price for b in segment if is_1bar_swing_high(bars, b.index)
    ]
    if swings_1bar:
        return max(swings_1bar), "swing_1bar"

    body_highs = [max(b.open_price, b.close_price) for b in segment]
    tier: TroughTier = "body_floor"
    if len(segment) == 2:
        tier = "body_floor:narrow_v"
    return max(body_highs), tier


def _evaluate_ll3_triple(
    bars: list[WedgeBar],
    p1: WedgeBar,
    p2: WedgeBar,
    p3: WedgeBar,
    *,
    atr_5: float,
    tick_size: float,
    n_min: int,
    alpha_threshold: float,
) -> dict[str, Any]:
    """LL3 审计：P1 > P2 > P3（低点逐步降低），反弹峰 Pk1 > Pk2（衰竭）。"""
    if not (p3.low_price < p2.low_price < p1.low_price):
        return {"status": "no_structure"}

    if p2.index - p1.index < n_min or p3.index - p2.index < n_min:
        return {"status": "no_structure"}

    pk1_val, pk1_tier = anchor_peak(bars, p1.index, p2.index)
    pk2_val, pk2_tier = anchor_peak(bars, p2.index, p3.index)
    if np.isnan(pk1_val) or np.isnan(pk2_val):
        return {"status": "no_structure"}

    pk_floor = max(2 * tick_size, 0.15 * atr_5)
    if (pk1_val - pk2_val) < pk_floor:
        return {
            "status": "wedge_invalid:tr_order",
            "p1_idx": p1.index,
            "p2_idx": p2.index,
            "p3_idx": p3.index,
            "p3_low": p3.low_price,
            "pk1_tier": pk1_tier,
            "pk2_tier": pk2_tier,
        }

    move1 = p1.low_price - p2.low_price
    move2 = p2.low_price - p3.low_price
    move1_floor = max(3 * tick_size, 0.25 * atr_5)
    move2_floor = max(2 * tick_size, 0.15 * atr_5)
    if move1 < move1_floor or move2 < move2_floor:
        return {
            "status": "wedge_invalid:move_floor",
            "p1_idx": p1.index,
            "p2_idx": p2.index,
            "p3_idx": p3.index,
            "p3_low": p3.low_price,
            "pk1_tier": pk1_tier,
            "pk2_tier": pk2_tier,
        }

    alpha = move2 / move1 if move1 > 0 else float("inf")
    if alpha >= alpha_threshold:
        return {
            "status": "wedge_invalid:alpha",
            "p1_idx": p1.index,
            "p2_idx": p2.index,
            "p3_idx": p3.index,
            "p3_low": p3.low_price,
            "pk1_tier": pk1_tier,
            "pk2_tier": pk2_tier,
            "alpha": alpha,
        }

    return {
        "status": "wedge_valid:ll3",
        "p1_idx": p1.index,
        "p2_idx": p2.index,
        "p3_idx": p3.index,
        "p3_low": p3.low_price,
        "pk1_tier": pk1_tier,
        "pk2_tier": pk2_tier,
        "alpha": alpha,
    }


def scan_latest_bullish_wedge(
    bars: list[WedgeBar],
    atr_5: float,
    *,
    tick_size: float = 1.0,
    n_min: int = 3,
    alpha_threshold: float = 0.85,
) -> dict[str, Any]:
    """从最近向过去检索第一组通过审计的 LL3 楔形（牛市衰竭三推）。"""
    results: dict[str, Any] = {"status": "no_structure"}
    if len(bars) < 7 or atr_5 <= 0:
        return results

    p_candidates = [
        bars[idx]
        for idx in range(2, len(bars) - 2)
        if is_2bar_fractal_low(bars, idx)
    ]
    if len(p_candidates) < 3:
        return results

    last_fail: dict[str, Any] | None = None
    for idx3 in range(len(p_candidates) - 1, 1, -1):
        p3 = p_candidates[idx3]
        for idx2 in range(idx3 - 1, 0, -1):
            p2 = p_candidates[idx2]
            if p3.index - p2.index < n_min:
                continue
            for idx1 in range(idx2 - 1, -1, -1):
                p1 = p_candidates[idx1]
                if p2.index - p1.index < n_min:
                    continue

                verdict = _evaluate_ll3_triple(
                    bars,
                    p1,
                    p2,
                    p3,
                    atr_5=atr_5,
                    tick_size=tick_size,
                    n_min=n_min,
                    alpha_threshold=alpha_threshold,
                )
                if verdict["status"] == "wedge_valid:ll3":
                    return verdict
                if verdict["status"] != "no_structure":
                    last_fail = verdict

    return last_fail if last_fail is not None else results


def anchor_trough(bars: list[WedgeBar], i: int, j: int) -> tuple[float, TroughTier]:
    """开放区间 (i, j) 内的回撤低点 Tr_k。"""
    if j <= i + 1:
        return float("nan"), "empty"

    segment = bars[i + 1 : j]
    if not segment:
        return float("nan"), "empty"

    swings_2bar = [
        b.low_price for b in segment if is_2bar_swing_low(bars, b.index)
    ]
    if swings_2bar:
        return min(swings_2bar), "swing_2bar"

    swings_1bar = [
        b.low_price for b in segment if is_1bar_swing_low(bars, b.index)
    ]
    if swings_1bar:
        return min(swings_1bar), "swing_1bar"

    body_lows = [min(b.open_price, b.close_price) for b in segment]
    tier: TroughTier = "body_floor"
    if len(segment) == 2:
        tier = "body_floor:narrow_v"
    return min(body_lows), tier


def _evaluate_hh3_triple(
    bars: list[WedgeBar],
    p1: WedgeBar,
    p2: WedgeBar,
    p3: WedgeBar,
    *,
    atr_5: float,
    tick_size: float,
    n_min: int,
    alpha_threshold: float,
) -> dict[str, Any]:
    if not (p3.high_price > p2.high_price > p1.high_price):
        return {"status": "no_structure"}

    if p2.index - p1.index < n_min or p3.index - p2.index < n_min:
        return {"status": "no_structure"}

    tr1_val, tr1_tier = anchor_trough(bars, p1.index, p2.index)
    tr2_val, tr2_tier = anchor_trough(bars, p2.index, p3.index)
    if np.isnan(tr1_val) or np.isnan(tr2_val):
        return {"status": "no_structure"}

    tr_floor = max(2 * tick_size, 0.15 * atr_5)
    if (tr2_val - tr1_val) < tr_floor:
        return {
            "status": "wedge_invalid:tr_order",
            "p1_idx": p1.index,
            "p2_idx": p2.index,
            "p3_idx": p3.index,
            "p3_high": p3.high_price,
            "tr1_tier": tr1_tier,
            "tr2_tier": tr2_tier,
        }

    move1 = p2.high_price - p1.high_price
    move2 = p3.high_price - p2.high_price
    move1_floor = max(3 * tick_size, 0.25 * atr_5)
    move2_floor = max(2 * tick_size, 0.15 * atr_5)
    if move1 < move1_floor or move2 < move2_floor:
        return {
            "status": "wedge_invalid:move_floor",
            "p1_idx": p1.index,
            "p2_idx": p2.index,
            "p3_idx": p3.index,
            "p3_high": p3.high_price,
            "tr1_tier": tr1_tier,
            "tr2_tier": tr2_tier,
        }

    alpha = move2 / move1 if move1 > 0 else float("inf")
    if alpha >= alpha_threshold:
        return {
            "status": "wedge_invalid:alpha",
            "p1_idx": p1.index,
            "p2_idx": p2.index,
            "p3_idx": p3.index,
            "p3_high": p3.high_price,
            "tr1_tier": tr1_tier,
            "tr2_tier": tr2_tier,
            "alpha": alpha,
        }

    return {
        "status": "wedge_valid:hh3",
        "p1_idx": p1.index,
        "p2_idx": p2.index,
        "p3_idx": p3.index,
        "p3_high": p3.high_price,
        "tr1_tier": tr1_tier,
        "tr2_tier": tr2_tier,
        "alpha": alpha,
    }


def scan_latest_bearish_wedge(
    bars: list[WedgeBar],
    atr_5: float,
    *,
    tick_size: float = 1.0,
    n_min: int = 3,
    alpha_threshold: float = 0.85,
) -> dict[str, Any]:
    """从最近向过去检索第一组通过审计的 HH3 楔形。"""
    results: dict[str, Any] = {"status": "no_structure"}
    if len(bars) < 7 or atr_5 <= 0:
        return results

    p_candidates = [
        bars[idx]
        for idx in range(2, len(bars) - 2)
        if is_2bar_fractal_high(bars, idx)
    ]
    if len(p_candidates) < 3:
        return results

    last_fail: dict[str, Any] | None = None
    for idx3 in range(len(p_candidates) - 1, 1, -1):
        p3 = p_candidates[idx3]
        for idx2 in range(idx3 - 1, 0, -1):
            p2 = p_candidates[idx2]
            if p3.index - p2.index < n_min:
                continue
            for idx1 in range(idx2 - 1, -1, -1):
                p1 = p_candidates[idx1]
                if p2.index - p1.index < n_min:
                    continue

                verdict = _evaluate_hh3_triple(
                    bars,
                    p1,
                    p2,
                    p3,
                    atr_5=atr_5,
                    tick_size=tick_size,
                    n_min=n_min,
                    alpha_threshold=alpha_threshold,
                )
                if verdict["status"] == "wedge_valid:hh3":
                    return verdict
                if verdict["status"] != "no_structure":
                    last_fail = verdict

    return last_fail if last_fail is not None else results


def audit_wedge_funnel(
    bars: list[WedgeBar],
    atr_5: float,
    *,
    tick_size: float = 1.0,
    n_min: int = 3,
    alpha_threshold: float = 0.85,
) -> dict[str, int]:
    """统计全日三推候选与 Tr 锚定 tier 分布。"""
    counts: dict[str, int] = {
        "triple_scanned": 0,
        "wedge_valid:hh3": 0,
        "wedge_invalid:tr_order": 0,
        "wedge_invalid:move_floor": 0,
        "wedge_invalid:alpha": 0,
        "tr_tier:swing_2bar": 0,
        "tr_tier:swing_1bar": 0,
        "tr_tier:body_floor": 0,
        "tr_tier:body_floor:narrow_v": 0,
    }
    if len(bars) < 7 or atr_5 <= 0:
        return counts

    p_candidates = [
        bars[idx]
        for idx in range(2, len(bars) - 2)
        if is_2bar_fractal_high(bars, idx)
    ]
    if len(p_candidates) < 3:
        return counts

    seen_valid: set[tuple[int, int, int]] = set()
    for idx3 in range(len(p_candidates) - 1, 1, -1):
        p3 = p_candidates[idx3]
        for idx2 in range(idx3 - 1, 0, -1):
            p2 = p_candidates[idx2]
            if p3.index - p2.index < n_min:
                continue
            for idx1 in range(idx2 - 1, -1, -1):
                p1 = p_candidates[idx1]
                if p2.index - p1.index < n_min:
                    continue

                counts["triple_scanned"] += 1
                verdict = _evaluate_hh3_triple(
                    bars,
                    p1,
                    p2,
                    p3,
                    atr_5=atr_5,
                    tick_size=tick_size,
                    n_min=n_min,
                    alpha_threshold=alpha_threshold,
                )
                status = verdict.get("status", "no_structure")
                for tier_key in ("tr1_tier", "tr2_tier"):
                    tier = verdict.get(tier_key)
                    if tier in (
                        "swing_2bar",
                        "swing_1bar",
                        "body_floor",
                        "body_floor:narrow_v",
                    ):
                        counts[f"tr_tier:{tier}"] += 1

                if status == "wedge_valid:hh3":
                    key = (p1.index, p2.index, p3.index)
                    if key not in seen_valid:
                        seen_valid.add(key)
                        counts["wedge_valid:hh3"] += 1
                elif status.startswith("wedge_invalid:"):
                    counts[status] += 1

    return counts
