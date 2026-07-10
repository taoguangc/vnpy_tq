# -*- coding: utf-8 -*-
"""品种自适应：流动性分档 → Router / OPP19 / 定仓（可扩展至 hc 类低流动性同步品种）。"""
from __future__ import annotations

import math

# 1m 成交量中位数（2023-05~2026-05 回测窗统计；新品种可补表或脚本自动写入）
SYMBOL_VOL_BASELINE_1M: dict[str, float] = {
    "rb": 2861.0,
    "hc": 936.0,
    "ma": 1756.0,
    "ta": 1849.0,
}

# 参照流动性（黑色系锚点 rb）
DEFAULT_LIQUIDITY_REF_1M = 2861.0
DEFAULT_LIQUIDITY_LOW_RATIO = 0.45


def liquidity_ratio(vol_baseline: float, ref: float = DEFAULT_LIQUIDITY_REF_1M) -> float:
    if ref <= 0:
        return 1.0
    return vol_baseline / ref


def liquidity_tier(ratio: float, low_threshold: float = DEFAULT_LIQUIDITY_LOW_RATIO) -> str:
    if ratio < low_threshold:
        return "LOW"
    if ratio < 0.75:
        return "MID"
    return "HIGH"


def static_liquidity_risk_mult(
    ratio: float,
    *,
    floor: float = 0.55,
    ceil: float = 1.0,
) -> float:
    """sqrt 缩放：低流动性品种降仓，高流动性不放大超过 1。"""
    if ratio <= 0:
        return floor
    return max(floor, min(ceil, math.sqrt(ratio)))


def runtime_liquidity_risk_mult(
    recent_vol: float,
    vol_baseline: float,
    *,
    floor: float = 0.50,
    ceil: float = 1.0,
) -> float:
    """15m 滚动成交量相对品种基线的动态乘子。"""
    if vol_baseline <= 0 or recent_vol <= 0:
        return 1.0
    ratio = recent_vol / vol_baseline
    return max(floor, min(ceil, math.sqrt(ratio)))


def parse_prefix_list(raw: str) -> tuple[str, ...]:
    if not raw:
        return ()
    return tuple(p.strip() for p in raw.split(",") if p.strip())


def apply_symbol_adaptive(profile: dict) -> dict:
    """按 symbol_vol_baseline_1m 注入自适应策略参数（resolve 时调用）。"""
    if not profile.get("symbol_adaptive_enabled", True):
        return profile

    key = str(profile.get("symbol", "")).lower()
    ref = float(profile.get("symbol_liquidity_ref_1m", DEFAULT_LIQUIDITY_REF_1M))
    low_thr = float(profile.get("symbol_liquidity_low_ratio", DEFAULT_LIQUIDITY_LOW_RATIO))
    floor = float(profile.get("symbol_liquidity_risk_floor", 0.55))

    vol_base = profile.get("symbol_vol_baseline_1m")
    if vol_base is None and key in SYMBOL_VOL_BASELINE_1M:
        vol_base = SYMBOL_VOL_BASELINE_1M[key]
        profile["symbol_vol_baseline_1m"] = vol_base

    if vol_base is None:
        return profile

    ratio = liquidity_ratio(float(vol_base), ref)
    tier = liquidity_tier(ratio, low_thr)
    profile["symbol_liquidity_tier"] = tier
    profile["symbol_liquidity_ratio"] = round(ratio, 4)
    # 仅 LOW 档降仓；HIGH/MID 保持 1.0，避免 ma 等同步品种被误缩
    if tier == "LOW":
        profile["symbol_liquidity_risk_mult"] = round(
            static_liquidity_risk_mult(ratio, floor=floor), 4
        )
    else:
        profile["symbol_liquidity_risk_mult"] = 1.0
    return profile
