# -*- coding: utf-8 -*-
"""OPP02 EMA 回撤 — 纯检测器（从 shadow_dry_scan._match_opp02 提取）。"""
from __future__ import annotations

from typing import Protocol

from strategies.pa_minimal.detectors.schema import PatternMatch


class _Opp02Context(Protocol):
    opp02_r2_gate_enabled: bool
    opp02_r2_min: float
    opp02_aff_gate_enabled: bool
    opp02_aff_alpha_min: float
    ema_pullback_touch_atr: float
    ema_pullback_min_body_ratio: float
    always_in: str
    _aff_alpha_strength: float

    def _trend_regime_blocks_continuation(self, min_r2: float) -> bool: ...
    def _pd_blocks_long_target(self, close: float, atr: float) -> bool: ...
    def _pd_blocks_short_target(self, close: float, atr: float) -> bool: ...
    def _cap_long_stop(self, raw_stop: float, close: float, atr: float) -> float: ...
    def _cap_short_stop(self, raw_stop: float, close: float, atr: float) -> float: ...


def match_opp02(
    strategy: _Opp02Context,
    bar,
    *,
    atr_5: float,
    tick: float,
    stop_buffer: float,
    bar_range: float,
    body: float,
    ema_20: float,
    is_oo: bool,
) -> list[PatternMatch]:
    if is_oo or bar_range <= tick or ema_20 <= 0 or atr_5 <= 0:
        return []
    if strategy.opp02_r2_gate_enabled and strategy._trend_regime_blocks_continuation(strategy.opp02_r2_min):
        return []
    if strategy.opp02_aff_gate_enabled and strategy._aff_alpha_strength < strategy.opp02_aff_alpha_min:
        return []
    touch_band = atr_5 * strategy.ema_pullback_touch_atr
    body_ratio = body / bar_range if bar_range > 0 else 0.0
    out: list[PatternMatch] = []
    if strategy.always_in == "LONG":
        touched = bar.low_price <= ema_20 + touch_band
        sig = (bar.close_price > bar.open_price
               and body_ratio >= strategy.ema_pullback_min_body_ratio
               and bar.high_price - max(bar.open_price, bar.close_price) < bar_range * 0.45)
        if touched and sig and not strategy._pd_blocks_long_target(bar.close_price, atr_5):
            out.append(PatternMatch(
                "OPP02_5M_EMA_PULLBACK_LONG", 1,
                bar.high_price + tick,
                strategy._cap_long_stop(bar.low_price - stop_buffer, bar.close_price, atr_5),
                "PENDING_CONFIRM",
            ))
    if strategy.always_in == "SHORT":
        touched = bar.high_price >= ema_20 - touch_band
        sig = (bar.close_price < bar.open_price
               and body_ratio >= strategy.ema_pullback_min_body_ratio
               and min(bar.open_price, bar.close_price) - bar.low_price < bar_range * 0.45)
        if touched and sig and not strategy._pd_blocks_short_target(bar.close_price, atr_5):
            out.append(PatternMatch(
                "OPP02_5M_EMA_PULLBACK_SHORT", -1,
                bar.low_price - tick,
                strategy._cap_short_stop(bar.high_price + stop_buffer, bar.close_price, atr_5),
                "PENDING_CONFIRM",
            ))
    return out
