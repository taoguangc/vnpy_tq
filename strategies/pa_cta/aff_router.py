# -*- coding: utf-8 -*-
"""AFF Archetype Router：15m compression / env / alpha → 允许 OPP 族（v0/v1/v2）。"""
from __future__ import annotations

# ── v0（EXP-013 初版）：按前缀列表，TREND/REVERSAL 混在同一表 ──
ARCHETYPE_ALLOWED_V0: dict[str, tuple[str, ...]] = {
    "LOW_ALPHA": ("OPP12_", "OPP13_", "OPP15_", "OPP16_", "OPP17_"),
    "COMPRESSION": ("OPP13_", "OPP15_", "OPP16_"),
    "EXPANSION": ("OPP02_", "OPP08_", "OPP19_", "OPP16_"),
    "EXHAUSTION": ("OPP12_", "OPP13_", "OPP17_"),
}

# ── v1（lane 矩阵）：TREND 仅在 EXPANSION/NEUTRAL；REVERSAL 按档前缀 ──
TREND_ALLOWED_ARCHETYPES = frozenset({"EXPANSION", "NEUTRAL"})

# None = 该档不限制 REVERSAL 前缀
REVERSAL_PREFIXES_V1: dict[str, tuple[str, ...] | None] = {
    "LOW_ALPHA": ("OPP12_", "OPP13_", "OPP15_", "OPP16_", "OPP17_"),
    "COMPRESSION": ("OPP13_", "OPP15_", "OPP16_"),
    "EXPANSION": ("OPP13_", "OPP15_", "OPP16_"),
    "EXHAUSTION": ("OPP12_", "OPP13_", "OPP17_"),
    "NEUTRAL": None,
}

# v2：EXPANSION 下禁止 OPP16 多（顺势扩张期二棒反转易假）
REVERSAL_EXPANSION_BLOCK_PREFIXES = ("OPP16_5M_TWO_BAR_REV_LONG",)

RANGE_CONTEXTS = frozenset({"TRADING_RANGE", "TIGHT_RANGE"})
# 策略已在该 context 内路由出 TREND setup → AFF 仅 LOW_ALPHA 硬拒
TREND_CONTEXT_BYPASS = frozenset({
    "STRONG_BULL", "STRONG_BEAR", "BULL_CHANNEL", "BEAR_CHANNEL",
})


def entry_direction_from_opportunity(opportunity: str) -> int:
    """1=多, -1=空, 0=未知。"""
    name = opportunity or ""
    if name.endswith("_LONG") or "_LONG" in name:
        return 1
    if name.endswith("_SHORT") or "_SHORT" in name:
        return -1
    return 0


def always_in_aligns(direction: int, always_in: str) -> bool:
    if direction == 0 or always_in == "NONE":
        return False
    if direction > 0 and always_in == "LONG":
        return True
    if direction < 0 and always_in == "SHORT":
        return True
    return False


def classify_aff_archetype(
    *,
    alpha: float,
    compression: float,
    env: float,
    alpha_low: float = 0.25,
    compression_min: float = 0.6,
    expansion_env_min: float = 0.75,
    exhaustion_env_max: float = 0.25,
) -> str:
    """分档优先级：LOW_ALPHA → COMPRESSION → EXPANSION → EXHAUSTION → NEUTRAL。"""
    if alpha < alpha_low:
        return "LOW_ALPHA"
    if compression >= compression_min:
        return "COMPRESSION"
    if env >= expansion_env_min and compression < 0.3:
        return "EXPANSION"
    if env <= exhaustion_env_max and compression < 0.3:
        return "EXHAUSTION"
    return "NEUTRAL"


def setup_allowed_v0(opportunity: str, archetype: str) -> bool:
    if not opportunity:
        return True
    if archetype == "NEUTRAL":
        return True
    prefixes = ARCHETYPE_ALLOWED_V0.get(archetype)
    if not prefixes:
        return True
    return any(opportunity.startswith(p) for p in prefixes)


def setup_allowed_v1(opportunity: str, archetype: str, lane: str) -> bool:
    if not opportunity:
        return True
    if archetype == "NEUTRAL":
        return True
    if lane == "TREND":
        return archetype in TREND_ALLOWED_ARCHETYPES
    prefixes = REVERSAL_PREFIXES_V1.get(archetype)
    if prefixes is None:
        return True
    return any(opportunity.startswith(p) for p in prefixes)


def setup_allowed_v2(
    opportunity: str,
    archetype: str,
    lane: str,
    *,
    always_in: str = "NONE",
    market_context: str = "TRADING_RANGE",
    trend_bypass_prefixes: tuple[str, ...] = ("OPP08_",),
) -> bool:
    """v2：v1 基础上 + always_in 顺势放行 TREND；收紧 EXPANSION 下 OPP16 多。"""
    if not opportunity:
        return True
    if archetype == "NEUTRAL":
        return True

    direction = entry_direction_from_opportunity(opportunity)
    aligned = always_in_aligns(direction, always_in)

    # context 已路由的突破：指定 TREND 前缀不受 LOW_ALPHA 误杀（默认 OPP08_）
    if lane == "TREND" and market_context in TREND_CONTEXT_BYPASS:
        bypass_prefixes = trend_bypass_prefixes or ("OPP08_",)
        if any(opportunity.startswith(p) for p in bypass_prefixes):
            return True
        return archetype != "LOW_ALPHA"

    # LOW_ALPHA：仅保留反转族；TREND 全关（等同 Setup AFF）
    if archetype == "LOW_ALPHA":
        if lane == "TREND":
            return False
        return setup_allowed_v1(opportunity, archetype, lane)

    if lane == "TREND":
        if archetype in TREND_ALLOWED_ARCHETYPES:
            return True
        # COMPRESSION/EXHAUSTION：always_in 与入场同向时放行顺势突破
        if aligned and archetype in ("COMPRESSION", "EXHAUSTION"):
            return True
        # 区间环境不放行逆势 TREND
        if market_context in RANGE_CONTEXTS:
            return False
        return aligned

    # REVERSAL：趋势 context 下 OPP16 多易假反转
    if lane == "REVERSAL" and opportunity.startswith("OPP16_5M_TWO_BAR_REV_LONG"):
        if market_context in TREND_CONTEXT_BYPASS and archetype in (
            "EXPANSION", "LOW_ALPHA", "EXHAUSTION",
        ):
            return False
    if archetype == "EXPANSION":
        if any(opportunity.startswith(p) for p in REVERSAL_EXPANSION_BLOCK_PREFIXES):
            return False
    return setup_allowed_v1(opportunity, archetype, lane)


def setup_allowed_minimal(opportunity: str, archetype: str, lane: str) -> bool:
    """仅 LOW_ALPHA 硬拒 TREND lane（等同 Setup AFF 趋势族；反转全放行）。"""
    if not opportunity:
        return True
    if archetype == "NEUTRAL":
        return True
    if archetype == "LOW_ALPHA" and lane == "TREND":
        return False
    return True


def setup_allowed_for_archetype(
    opportunity: str,
    archetype: str,
    *,
    lane: str = "REVERSAL",
    use_lane_matrix: bool = True,
    adaptive_enabled: bool = False,
    minimal_enabled: bool = False,
    always_in: str = "NONE",
    market_context: str = "TRADING_RANGE",
    trend_bypass_prefixes: tuple[str, ...] = ("OPP08_",),
) -> bool:
    if minimal_enabled:
        return setup_allowed_minimal(opportunity, archetype, lane)
    if adaptive_enabled:
        return setup_allowed_v2(
            opportunity,
            archetype,
            lane,
            always_in=always_in,
            market_context=market_context,
            trend_bypass_prefixes=trend_bypass_prefixes,
        )
    if use_lane_matrix:
        return setup_allowed_v1(opportunity, archetype, lane)
    return setup_allowed_v0(opportunity, archetype)
