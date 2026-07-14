# -*- coding: utf-8 -*-
"""OPP12 超伸失败 — 纯检测器（从 shadow_dry_scan._match_opp12 提取）。"""
from __future__ import annotations

from typing import Protocol

from strategies.pa_minimal.detectors.schema import PatternMatch


class _Opp12Context(Protocol):
    overshoot_atr_mult: float
    overshoot_max_atr_mult: float

    def _pd_blocks_long_target(self, close: float, atr: float) -> bool: ...
    def _pd_blocks_short_target(self, close: float, atr: float) -> bool: ...
    def _cap_long_stop(self, raw_stop: float, close: float, atr: float) -> float: ...
    def _cap_short_stop(self, raw_stop: float, close: float, atr: float) -> float: ...


def match_opp12(
    strategy: _Opp12Context,
    bar,
    *,
    atr_5: float,
    tick: float,
    ema_20: float,
    is_bull_reversal: bool,
    is_bear_reversal: bool,
    is_oo: bool,
) -> list[PatternMatch]:
    if is_oo:
        return []
    out: list[PatternMatch] = []
    overshoot_depth = ema_20 - bar.close_price
    if (atr_5 * strategy.overshoot_atr_mult <= overshoot_depth
            <= atr_5 * strategy.overshoot_max_atr_mult
            and is_bull_reversal and bar.close_price > bar.open_price
            and not strategy._pd_blocks_long_target(bar.close_price, atr_5)):
        out.append(PatternMatch(
            "OPP12_5M_OVERSHOOT_FAIL_LONG", 1,
            bar.high_price,
            strategy._cap_long_stop(bar.low_price - tick, bar.close_price, atr_5),
            "PENDING_CONFIRM",
        ))
    if (bar.close_price > ema_20 + atr_5 * strategy.overshoot_atr_mult
            and is_bear_reversal
            and not strategy._pd_blocks_short_target(bar.close_price, atr_5)):
        out.append(PatternMatch(
            "OPP12_5M_OVERSHOOT_FAIL_SHORT", -1,
            bar.low_price,
            strategy._cap_short_stop(bar.high_price + tick, bar.close_price, atr_5),
            "PENDING_CONFIRM",
        ))
    return out
