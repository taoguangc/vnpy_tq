# -*- coding: utf-8 -*-
"""pa_minimal：以 OPP08 + OPP16 为默认的极简 Alpha 探索策略。

实现策略：薄子类 + 独立 5m 路由；检测器在 strategies.pa_minimal.detectors
（含 OPP02/08/12/13/15/16/17/19）。默认仅开 08+16，其余按开关启用。
执行/门禁/出场复用 pa_cta。
"""
from __future__ import annotations

import numpy as np

from vnpy.trader.object import BarData

from strategies.pa_cta.bar_patterns import (
    BarMetrics,
    classify_bar_shape,
    is_bear_reversal as bp_is_bear_reversal,
    is_boundary_bear_reversal,
    is_boundary_bull_reversal,
    is_bull_reversal as bp_is_bull_reversal,
    is_outside_outside,
    is_strong_bar as bp_is_strong_bar,
)
from strategies.pa_cta.shadow_dry_scan import (
    _match_opp08 as dry_match_opp08,
    _match_opp16 as dry_match_opp16,
)
from strategies.pa_cta.strategy import BrooksPaCtaStrategy
from strategies.pa_minimal.candidate_ledger import CandidateLedger, SignalCandidate
from strategies.pa_minimal.detectors import (
    match_opp02,
    match_opp08,
    match_opp12,
    match_opp13_boundary,
    match_opp13_double_top,
    match_opp15_trigger,
    match_opp16,
    match_opp17,
    match_opp19,
)

def _match_key(setup: str, direction: int, trigger: float, stop: float) -> tuple:
    return (setup, direction, round(float(trigger), 4), round(float(stop), 4))


class PaMinimal0816Strategy(BrooksPaCtaStrategy):
    """OPP08 + OPP16 默认开启；其余 OPP 经 detectors 按开关可启用。"""

    author = "Tao"
    version = "0.2_MINIMAL_MULTI"

    ema_pullback_enabled = False
    climax_rev_enabled = False
    opening_drive_enabled = False
    opening_rev_enabled = False
    two_bar_rev_enabled = True
    overshoot_fail_enabled = False   # OPP12
    day_boundary_enabled = False     # OPP13
    wedge_enabled = False            # OPP15
    # False=宽松（实体阈值即可）；True=实体阈值 AND 前棒形态匹配
    opp16_strict_shape = False

    candidate_ledger_enabled = True
    # True=全 OPP 只记账不武装，持仓/抢占不截断候选（稳定 Alpha shadow）
    alpha_shadow_mode = False
    # brooks | r2_chop | vwap_tri
    context_mode = "brooks"
    # R²+CHOP 三态阈值（仅 context_mode=r2_chop）
    alt_r2_trend_min = 0.55
    alt_chop_trend_max = 61.8
    alt_chop_range_min = 61.8
    # 与 dry-scan 同 bar 对照（研究用）
    dryscan_compare_enabled = False

    parameters = list(BrooksPaCtaStrategy.parameters) + [
        "candidate_ledger_enabled",
        "alpha_shadow_mode",
        "context_mode",
        "alt_r2_trend_min",
        "alt_chop_trend_max",
        "alt_chop_range_min",
        "dryscan_compare_enabled",
        "opp16_strict_shape",
        "overshoot_fail_enabled",
        "day_boundary_enabled",
        "wedge_enabled",
    ]

    def on_init(self) -> None:
        self.write_log("pa_minimal OPP08+OPP16 初始化...")
        self.load_bar(10)

    def on_start(self) -> None:
        super().on_start()
        self._candidate_ledger = CandidateLedger(
            self.vt_symbol.split(".")[0] if self.vt_symbol else "unknown"
        )
        # 默认保证 OPP16 开；其余开关以类属性 / setting 注入为准，不在此硬关
        if not hasattr(self, "two_bar_rev_enabled") or self.two_bar_rev_enabled is None:
            self.two_bar_rev_enabled = True
        self.disabled_setups = getattr(self, "disabled_setups", "") or ""
        self._dryscan_compare = {
            "bars_checked": 0,
            "bars_with_signal": 0,
            "exact_match_bars": 0,
            "mismatch_bars": 0,
            "minimal_only": 0,
            "dry_only": 0,
            "mismatch_samples": [],
        }

    def _resolve_effective_context(self, bar: BarData) -> str:
        mode = (self.context_mode or "brooks").strip().lower()
        if mode == "r2_chop":
            return self._context_from_r2_chop()
        if mode == "vwap_tri":
            return self._context_from_vwap_tri()
        return self.market_context

    def _context_from_r2_chop(self) -> str:
        r2 = float(getattr(self, "_trend_r2", 0.0))
        chop = float(getattr(self, "_trend_chop", 100.0))
        if r2 >= float(self.alt_r2_trend_min) and chop <= float(self.alt_chop_trend_max):
            slope = self._recent_close_slope()
            if slope > 0:
                return "STRONG_BULL"
            if slope < 0:
                return "STRONG_BEAR"
            return "TRADING_RANGE"
        if chop >= float(self.alt_chop_range_min):
            return "WIDE_RANGE"
        return "TRADING_RANGE"

    def _recent_close_slope(self) -> float:
        period = max(int(self.trend_gate_r2_period), 3)
        if not self.am_15min.inited or self.am_15min.count < period:
            return 0.0
        y = np.asarray(self.am_15min.close_array[-period:], dtype=np.float64)
        if not np.all(np.isfinite(y)):
            return 0.0
        x = np.arange(period, dtype=np.float64)
        slope = float(np.polyfit(x, y, 1)[0])
        return slope

    def _context_from_vwap_tri(self) -> str:
        regime = self.vwap_regime or "UNINIT"
        if regime == "TREND_UP":
            return "STRONG_BULL"
        if regime == "TREND_DOWN":
            return "STRONG_BEAR"
        if regime == "CHOP":
            return "WIDE_RANGE"
        return "TRADING_RANGE"

    def on_5min_bar(self, bar: BarData) -> None:
        """5m 路由：默认 OPP08/16；其余 OPP 经 detectors + 开关。"""
        self._current_5min_bar = bar
        self.am_5min.update_bar(bar)
        self.bg_15.update_bar(bar)
        if not self.am_5min.inited:
            self._record_vsa_slot_volume(bar)
            return

        atr_5 = float(self.am_5min.atr(self.atr_window))
        atr_15 = float(self.am_15min.atr(self.atr_window)) if self.am_15min.inited else 0.0
        atr_ratio = round(atr_5 / atr_15, 3) if atr_15 > 0 and atr_5 > 0 else 0.0
        self._current_atr_ratio = atr_ratio
        allow_new_entry = self.atr_regime_min <= atr_ratio <= self.atr_regime_max

        bar_m = BarMetrics.from_bar(bar)
        self.prev_bar_shape = classify_bar_shape(
            bar_m,
            BarMetrics.from_bar(self._prev_5min_bar) if self._prev_5min_bar else None,
            self._pattern_th,
        )
        self._prev_5min_bar = bar
        self._update_pd_levels(bar)

        ema_20 = float(self.am_5min.ema(self.ema_window))
        tick = self.get_pricetick()
        stop_buffer = self._stop_buffer(atr_5, tick)

        if self.market_context != self.last_context:
            self.h_counter = 0
            self.l_counter = 0
            self.last_context = self.market_context

        if self.pos != 0:
            self._update_position_risk(bar, atr_5, stop_buffer)

        bar_range = bar_m.bar_range or tick
        th = self._pattern_th
        body = bar_m.body
        upper_shadow = bar_m.upper_shadow
        lower_shadow = bar_m.lower_shadow
        is_strong_bar = bp_is_strong_bar(bar_m, bar_range, atr_5, th)
        is_bull_reversal = bp_is_bull_reversal(bar_m, bar_range, th)
        is_bear_reversal = bp_is_bear_reversal(bar_m, bar_range, th)
        is_boundary_bull = is_boundary_bull_reversal(bar_m, bar_range, th)
        is_boundary_bear = is_boundary_bear_reversal(bar_m, bar_range, th)
        prev_high = float(self.am_5min.high[-2])
        recent_5bar_low = float(np.min(self.am_5min.low_array[-6:-1]))
        is_oo = (
            is_outside_outside(
                tuple(float(self.am_5min.high[-i]) for i in (1, 2, 3)),
                tuple(float(self.am_5min.low[-i]) for i in (1, 2, 3)),
            )
            if self.am_5min.count >= 5
            else False
        )
        is_long_climax = (bar.close_price - ema_20) > (self.long_climax_atr_mult * atr_5)
        is_short_climax = (ema_20 - bar.close_price) > (self.long_climax_atr_mult * atr_5)
        boundary_tol = self.day_boundary_tolerance * tick
        day_high_touch_tol = self.day_high_second_test_ticks * tick
        lh_max_drop = self.day_high_lh_max_ticks * tick

        shadow = bool(getattr(self, "alpha_shadow_mode", False))

        if self.pos == 0 and self.machine_state != "IDLE":
            if self._execute_state_machine(bar, atr_5, tick, is_strong_bar):
                if not shadow:
                    self._record_vsa_slot_volume(bar)
                    return

        effective_context = self._resolve_effective_context(bar)
        env_block = ""

        if not self.entry_window_open:
            env_block = "entry_window"
            if not shadow:
                self._reset_machine()
                self._record_vsa_slot_volume(bar)
                return
        if atr_5 < self._min_atr_for_context(effective_context):
            env_block = env_block or "atr_context"
            if not shadow:
                self._reset_machine()
                self._record_vsa_slot_volume(bar)
                return
        if self.pos != 0:
            env_block = env_block or "in_position"
            if not shadow:
                self._record_vsa_slot_volume(bar)
                return
        if not allow_new_entry:
            env_block = env_block or "atr_regime"
            if not shadow:
                self._reset_machine()
                self._record_vsa_slot_volume(bar)
                return
        if self.daily_trade_count >= self.max_daily_trades:
            env_block = env_block or "max_daily_trades"
            if not shadow:
                self._record_vsa_slot_volume(bar)
                return

        # OPP15：先武装楔形 setup（检测器只读触发）
        if self.wedge_enabled and not self.wedge_setup_active and self.machine_state == "IDLE" and not is_oo:
            self._try_arm_wedge_setup(bar, atr_5, tick)

        # OPP19：状态机推进 + 可能直接武装（有副作用）
        if self.opening_drive_enabled and self.machine_state == "IDLE":
            if self._process_opening_drive(
                    bar, effective_context, atr_5, tick, stop_buffer, bar_range,
                    body, is_strong_bar, is_oo):
                if not shadow:
                    self._record_vsa_slot_volume(bar)
                    return

        # OPP13：日高双顶状态推进（FIRST_TEST）；命中则武装并返回
        if self.day_boundary_enabled and effective_context == "WIDE_RANGE":
            if self._try_day_high_double_top(
                    bar, atr_5, tick, bar_range, upper_shadow, is_boundary_bear,
                    effective_context, day_high_touch_tol, lh_max_drop):
                if not shadow:
                    self._record_vsa_slot_volume(bar)
                    return

        matches = self._collect_detector_matches(
            bar,
            effective_context=effective_context,
            atr_5=atr_5,
            tick=tick,
            stop_buffer=stop_buffer,
            ema_20=ema_20,
            prev_high=prev_high,
            recent_5bar_low=recent_5bar_low,
            is_strong_bar=is_strong_bar,
            is_oo=is_oo,
            is_long_climax=is_long_climax,
            is_short_climax=is_short_climax,
            bar_range=bar_range,
            body=body,
            upper_shadow=upper_shadow,
            lower_shadow=lower_shadow,
            is_bull_reversal=is_bull_reversal,
            is_bear_reversal=is_bear_reversal,
            is_boundary_bull=is_boundary_bull,
            is_boundary_bear=is_boundary_bear,
            boundary_tol=boundary_tol,
            day_high_touch_tol=day_high_touch_tol,
            lh_max_drop=lh_max_drop,
        )

        detect_kwargs = dict(
            atr_5=atr_5,
            tick=tick,
            stop_buffer=stop_buffer,
            ema_20=ema_20,
            prev_high=prev_high,
            recent_5bar_low=recent_5bar_low,
            is_strong_bar=is_strong_bar,
            is_oo=is_oo,
            is_long_climax=is_long_climax,
            is_short_climax=is_short_climax,
            bar_range=bar_range,
        )
        if self.dryscan_compare_enabled:
            self._compare_with_dryscan(bar, effective_context, detect_kwargs, matches)

        session = self._candidate_session_label(bar)
        bar_winner = ""
        for m in matches:
            snap = self._shadow_gate_counters_snapshot()
            first_block = self._diagnose_first_block(m.setup, m.direction, bar)
            self._shadow_gate_counters_restore(snap)
            if env_block and not first_block:
                first_block = env_block
            gate_ok = first_block == ""
            if gate_ok:
                if getattr(m, "is_direct", False):
                    # DIRECT 路径门禁子集在 _try_opp15_direct_entry 内再验
                    pass
                else:
                    gate_ok = self._production_gates_pass(
                        direction=m.direction,
                        opportunity=m.setup,
                        bar=bar,
                        include_opp13_volume=bool(
                            getattr(m, "include_opp13_volume", False)
                        ),
                    )
                    if not gate_ok:
                        first_block = "production_gates"

            entry_px = float(m.trigger)
            if hasattr(self, "_shadow_entry_price"):
                entry_px = float(self._shadow_entry_price(bar, int(m.direction), tick))

            if self.candidate_ledger_enabled and hasattr(self, "_candidate_ledger"):
                snap = self.context_layer_snapshot()
                preempted = bar_winner if (bar_winner and not shadow) else ""
                disposition = "GATE_BLOCKED" if not gate_ok else "CANDIDATE"
                if preempted:
                    disposition = "PREEMPTED"
                if env_block and not gate_ok:
                    disposition = "ENV_BLOCKED"
                self._candidate_ledger.add(
                    SignalCandidate(
                        time=bar.datetime,
                        setup=m.setup,
                        direction=m.direction,
                        trigger=m.trigger,
                        stop=m.stop,
                        arm_mode=m.arm_mode,
                        market_context=effective_context,
                        always_in=self.always_in,
                        aff_alpha=float(getattr(self, "_aff_alpha_strength", 0.0)),
                        ctx_trend_quality=float(snap.trend_quality),
                        ctx_vol_abnormality=float(snap.vol_abnormality),
                        ctx_opp08_fit=float(snap.opp08_fit),
                        ctx_opp16_fit=float(snap.opp16_fit),
                        fast_trend_r2=float(snap.fast.trend_r2),
                        slow_trend_r2=float(snap.slow.trend_r2),
                        slow_er=float(snap.slow.er),
                        gate_pass=gate_ok and not env_block,
                        first_block=first_block or env_block,
                        armed=False,
                        disposition=disposition,
                        symbol=self._candidate_ledger.symbol,
                        entry_price=entry_px,
                        structural_stop=float(m.stop),
                        vwap_regime=str(getattr(self, "vwap_regime", "")),
                        session=session,
                        env_block=env_block,
                        preempted_by=preempted,
                        gate_before=gate_ok,
                    )
                )

            if shadow:
                continue
            if not gate_ok or env_block:
                continue

            if getattr(m, "is_direct", False):
                armed = self._try_opp15_direct_entry(
                    bar=bar,
                    direction=m.direction,
                    opportunity=m.setup,
                    entry_price=float(m.trigger),
                    stop=float(m.stop),
                    invalid_line=float(m.stop),
                    atr_5=atr_5,
                )
            else:
                armed = self._try_production_arm(
                    direction=m.direction,
                    opportunity=m.setup,
                    trigger=m.trigger,
                    stop=m.stop,
                    arm_mode=m.arm_mode,
                    include_opp13_volume=bool(
                        getattr(m, "include_opp13_volume", False)
                    ),
                )
            if armed and self.candidate_ledger_enabled and hasattr(self, "_candidate_ledger"):
                if self._candidate_ledger.records:
                    self._candidate_ledger.records[-1].armed = True
                    self._candidate_ledger.records[-1].disposition = "ARMED"
            if armed:
                bar_winner = m.setup
                self._record_vsa_slot_volume(bar)
                return

        self._record_vsa_slot_volume(bar)

    def _candidate_session_label(self, bar: BarData) -> str:
        t = bar.datetime.time()
        h, m = t.hour, t.minute
        if h == 9 and m < 30:
            return "OPEN_AM"
        if (h == 9 and m >= 30) or h == 10 or (h == 11 and m <= 30):
            return "DAY_AM"
        if h == 13 or (h == 14) or (h == 15 and m == 0):
            return "DAY_PM"
        if h >= 21 or h < 3:
            return "NIGHT"
        return "OTHER"

    def _try_production_arm(
        self,
        *,
        direction: int,
        opportunity: str,
        trigger: float,
        stop: float,
        invalid_line: float = 0.0,
        arm_mode: str = "FAST_TRACK",
        include_opp13_volume: bool = False,
    ) -> bool:
        if getattr(self, "alpha_shadow_mode", False):
            return False
        return super()._try_production_arm(
            direction=direction,
            opportunity=opportunity,
            trigger=trigger,
            stop=stop,
            invalid_line=invalid_line,
            arm_mode=arm_mode,
            include_opp13_volume=include_opp13_volume,
        )

    def _try_opp15_direct_entry(
        self,
        *,
        bar: BarData,
        direction: int,
        opportunity: str,
        entry_price: float,
        stop: float,
        invalid_line: float,
        atr_5: float,
    ) -> bool:
        if getattr(self, "alpha_shadow_mode", False):
            return False
        return super()._try_opp15_direct_entry(
            bar=bar,
            direction=direction,
            opportunity=opportunity,
            entry_price=entry_price,
            stop=stop,
            invalid_line=invalid_line,
            atr_5=atr_5,
        )

    def _collect_detector_matches(
        self,
        bar: BarData,
        *,
        effective_context: str,
        atr_5: float,
        tick: float,
        stop_buffer: float,
        ema_20: float,
        prev_high: float,
        recent_5bar_low: float,
        is_strong_bar: bool,
        is_oo: bool,
        is_long_climax: bool,
        is_short_climax: bool,
        bar_range: float,
        body: float,
        upper_shadow: float,
        lower_shadow: float,
        is_bull_reversal: bool,
        is_bear_reversal: bool,
        is_boundary_bull: bool,
        is_boundary_bear: bool,
        boundary_tol: float,
        day_high_touch_tol: float,
        lh_max_drop: float,
    ) -> list:
        """按 production 近似顺序收集 detectors 命中（只读）。"""
        matches: list = []
        if self.wedge_enabled:
            matches.extend(
                match_opp15_trigger(
                    self, bar, atr_5=atr_5, tick=tick, is_strong_bar=is_strong_bar,
                )
            )
        matches.extend(
            match_opp08(
                self,
                bar,
                effective_context,
                atr_5=atr_5,
                tick=tick,
                stop_buffer=stop_buffer,
                ema_20=ema_20,
                prev_high=prev_high,
                recent_5bar_low=recent_5bar_low,
                is_strong_bar=is_strong_bar,
                is_oo=is_oo,
                is_long_climax=is_long_climax,
                is_short_climax=is_short_climax,
                bar_range=bar_range,
            )
        )
        if (
            self.overshoot_fail_enabled
            and effective_context in ("BULL_CHANNEL", "BEAR_CHANNEL")
        ):
            matches.extend(
                match_opp12(
                    self,
                    bar,
                    atr_5=atr_5,
                    tick=tick,
                    ema_20=ema_20,
                    is_bull_reversal=is_bull_reversal,
                    is_bear_reversal=is_bear_reversal,
                    is_oo=is_oo,
                )
            )
        if self.day_boundary_enabled and effective_context == "WIDE_RANGE":
            matches.extend(
                match_opp13_boundary(
                    self,
                    bar,
                    atr_5=atr_5,
                    tick=tick,
                    bar_range=bar_range,
                    upper_shadow=upper_shadow,
                    lower_shadow=lower_shadow,
                    is_boundary_bull=is_boundary_bull,
                    is_boundary_bear=is_boundary_bear,
                    boundary_tol=boundary_tol,
                    is_oo=is_oo,
                )
            )
            matches.extend(
                match_opp13_double_top(
                    self,
                    bar,
                    atr_5=atr_5,
                    tick=tick,
                    bar_range=bar_range,
                    is_boundary_bear=is_boundary_bear,
                    effective_context=effective_context,
                    day_high_touch_tol=day_high_touch_tol,
                    lh_max_drop=lh_max_drop,
                )
            )
        if self.two_bar_rev_enabled and self.am_5min.count >= 2:
            if self.am_5min.count >= 3:
                prev_prev = type("B", (), {
                    "open_price": float(self.am_5min.open[-3]),
                    "high_price": float(self.am_5min.high[-3]),
                    "low_price": float(self.am_5min.low[-3]),
                    "close_price": float(self.am_5min.close[-3]),
                })()
                self._opp16_prev_shape = classify_bar_shape(
                    BarMetrics.from_bar(type("B", (), {
                        "open_price": float(self.am_5min.open[-2]),
                        "high_price": float(self.am_5min.high[-2]),
                        "low_price": float(self.am_5min.low[-2]),
                        "close_price": float(self.am_5min.close[-2]),
                    })()),
                    BarMetrics.from_bar(prev_prev),
                    self._pattern_th,
                )
            else:
                self._opp16_prev_shape = ""
            matches.extend(
                match_opp16(
                    self,
                    bar,
                    effective_context,
                    atr_5=atr_5,
                    tick=tick,
                    stop_buffer=stop_buffer,
                    bar_range=bar_range,
                )
            )
        if self.ema_pullback_enabled:
            matches.extend(
                match_opp02(
                    self,
                    bar,
                    atr_5=atr_5,
                    tick=tick,
                    stop_buffer=stop_buffer,
                    bar_range=bar_range,
                    body=body,
                    ema_20=ema_20,
                    is_oo=is_oo,
                )
            )
        if self.climax_rev_enabled:
            matches.extend(
                match_opp17(
                    self,
                    bar,
                    effective_context,
                    atr_5=atr_5,
                    tick=tick,
                    stop_buffer=stop_buffer,
                    bar_range=bar_range,
                    is_oo=is_oo,
                )
            )
        if self.opening_drive_enabled:
            # 状态已由 _process_opening_drive 推进；此处仅作账本/对照候选
            matches.extend(
                match_opp19(
                    self,
                    bar,
                    effective_context,
                    atr_5=atr_5,
                    tick=tick,
                    stop_buffer=stop_buffer,
                    bar_range=bar_range,
                    body=body,
                    is_strong_bar=is_strong_bar,
                    is_oo=is_oo,
                )
            )
        return matches

    def _compare_with_dryscan(
        self,
        bar: BarData,
        ctx: str,
        detect_kwargs: dict,
        minimal_matches: list,
    ) -> None:
        stats = self._dryscan_compare
        stats["bars_checked"] += 1
        dry = list(
            dry_match_opp08(
                self,
                bar,
                ctx,
                detect_kwargs["atr_5"],
                detect_kwargs["tick"],
                detect_kwargs["stop_buffer"],
                detect_kwargs["ema_20"],
                detect_kwargs["prev_high"],
                detect_kwargs["recent_5bar_low"],
                detect_kwargs["is_strong_bar"],
                detect_kwargs["is_oo"],
                detect_kwargs["is_long_climax"],
                detect_kwargs["is_short_climax"],
                detect_kwargs["bar_range"],
            )
        )
        if self.two_bar_rev_enabled:
            dry.extend(
                dry_match_opp16(
                    self,
                    bar,
                    ctx,
                    detect_kwargs["atr_5"],
                    detect_kwargs["tick"],
                    detect_kwargs["stop_buffer"],
                    detect_kwargs["bar_range"],
                )
            )
        min_keys = {
            _match_key(m.setup, m.direction, m.trigger, m.stop) for m in minimal_matches
        }
        dry_keys = {
            _match_key(m.setup, m.direction, m.trigger, m.stop) for m in dry
        }
        if min_keys or dry_keys:
            stats["bars_with_signal"] += 1
        if min_keys == dry_keys:
            if min_keys:
                stats["exact_match_bars"] += 1
            return
        stats["mismatch_bars"] += 1
        only_min = min_keys - dry_keys
        only_dry = dry_keys - min_keys
        stats["minimal_only"] += len(only_min)
        stats["dry_only"] += len(only_dry)
        if len(stats["mismatch_samples"]) < 20:
            stats["mismatch_samples"].append(
                {
                    "time": str(bar.datetime),
                    "ctx": ctx,
                    "minimal": sorted(min_keys),
                    "dry": sorted(dry_keys),
                }
            )

    def _diagnose_first_block(self, opportunity: str, direction: int, bar: BarData) -> str:
        if self._setup_disabled(opportunity):
            return "disabled"
        if self._aff_archetype_blocks_entry(opportunity):
            return "aff_archetype"
        if self._late_phase_blocks_entry(direction, self.market_context, opportunity):
            return "late_phase"
        if self._context_layer_blocks_entry(direction, opportunity):
            return "context_layer"
        if self._aff_blocks_entry():
            return "aff_filter"
        lane = self._setup_entry_lane(opportunity)
        if not self._dual_core_allows_entry(direction, lane):
            return "dual_core"
        if self._vsa_blocks_entry(direction, bar=bar):
            return "vsa"
        if not self._opp_tf_arm_gate(direction, opportunity):
            return "tf_arm"
        return ""

    def get_candidate_ledger(self) -> CandidateLedger | None:
        return getattr(self, "_candidate_ledger", None)

    def get_dryscan_compare(self) -> dict | None:
        return getattr(self, "_dryscan_compare", None)
