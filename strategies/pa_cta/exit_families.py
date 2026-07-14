# -*- coding: utf-8 -*-
"""Phase-3 出场族：趋势延续 vs 反转/区间（单表路由，禁止 per-setup 出场分叉）。"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ExitFamily(str, Enum):
    """出场族（与 AFF 入场 Lane TREND/REVERSAL 不同层）。"""

    CONTINUATION = "CONTINUATION"  # 趋势延续族
    REVERSAL = "REVERSAL"  # 反转/区间族


@dataclass(frozen=True)
class ExitFamilyConfig:
    """一族出场参数；v3 启用时替代 Fast/Slow 混用。"""

    breakeven_atr_mult: float
    enable_fast_lane_trail: bool
    enable_mm_half: bool
    enable_mm_runner: bool
    enable_profit_protect: bool
    enable_chandelier_trail: bool
    chandelier_active_atr_mult: float
    time_stop_minutes: int | None
    partial_at_1r_fraction: float  # 0=不在 1R 分批；0.5=平半仓


CONTINUATION_CONFIG = ExitFamilyConfig(
    breakeven_atr_mult=2.5,
    enable_fast_lane_trail=False,
    enable_mm_half=True,
    enable_mm_runner=True,
    enable_profit_protect=False,
    enable_chandelier_trail=True,
    chandelier_active_atr_mult=1.5,
    time_stop_minutes=None,
    partial_at_1r_fraction=0.5,
)

REVERSAL_CONFIG = ExitFamilyConfig(
    breakeven_atr_mult=1.0,
    enable_fast_lane_trail=False,
    enable_mm_half=True,
    enable_mm_runner=False,
    enable_profit_protect=True,
    enable_chandelier_trail=False,
    chandelier_active_atr_mult=99.0,
    time_stop_minutes=90,
    partial_at_1r_fraction=0.67,
)

_CONTINUATION_PREFIXES = ("OPP02_EMA_", "OPP08_")
_REVERSAL_PREFIXES = ("OPP12_", "OPP13_", "OPP15_", "OPP16_")


def resolve_exit_family(setup: str) -> ExitFamily:
    """按 setup 名路由出场族；OPP19 按 breakout/reversal 子类型拆分。"""
    name = setup or ""
    upper = name.upper()
    if "OD_BREAKOUT" in upper:
        return ExitFamily.CONTINUATION
    if "OD_REV" in upper:
        return ExitFamily.REVERSAL
    for prefix in _CONTINUATION_PREFIXES:
        if name.startswith(prefix):
            return ExitFamily.CONTINUATION
    for prefix in _REVERSAL_PREFIXES:
        if name.startswith(prefix):
            return ExitFamily.REVERSAL
    return ExitFamily.REVERSAL


def get_exit_family_config(family: ExitFamily) -> ExitFamilyConfig:
    if family == ExitFamily.CONTINUATION:
        return CONTINUATION_CONFIG
    return REVERSAL_CONFIG


def family_for_setup(setup: str) -> tuple[ExitFamily, ExitFamilyConfig]:
    fam = resolve_exit_family(setup)
    return fam, get_exit_family_config(fam)
