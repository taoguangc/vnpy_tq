# -*- coding: utf-8 -*-
"""OPP15 Wedge。"""
from __future__ import annotations

from datetime import time

from vnpy_ctastrategy import ArrayManager

from strategies.pa_cta.wedge import WedgeBar, scan_latest_bearish_wedge, scan_latest_bullish_wedge


class Opp15Mixin:
    def _reset_wedge_setup(self) -> None:
        self.wedge_setup_active = False
        self.wedge_confirmed_p3_high = 0.0
        self.wedge_trigger_line = 0.0
        self.wedge_arm_time = None
        self.wedge_current_alpha = 0.0
        self.wedge_p3_body_floor = 0.0
        self._wedge_direction = 0

    @staticmethod
    def _array_manager_to_wedge_bars(am: ArrayManager) -> list[WedgeBar]:
        n = min(am.count, am.size)
        return [WedgeBar(
            open_price=float(am.open[-(n - i)]), high_price=float(am.high[-(n - i)]),
            low_price=float(am.low[-(n - i)]), close_price=float(am.close[-(n - i)]), index=i,
        ) for i in range(n)]

    def _update_mtf_wedge_exhaustion_zone(self, atr_15: float) -> None:
        if atr_15 <= 0 or self.am_15min.count < 7:
            self.mtf_wedge_exhaustion_zone = False
            self.mtf_bull_wedge_exhaustion_zone = False
            return
        tick = self.get_pricetick()
        bars = self._array_manager_to_wedge_bars(self.am_15min)
        verdict_bear = scan_latest_bearish_wedge(
            bars, atr_15, tick_size=tick, n_min=self.wedge_n_min_15m,
            alpha_threshold=self.wedge_mtf_alpha_threshold)
        self.mtf_wedge_exhaustion_zone = verdict_bear.get("status") == "wedge_valid:hh3"
        verdict_bull = scan_latest_bullish_wedge(
            bars, atr_15, tick_size=tick, n_min=self.wedge_n_min_15m,
            alpha_threshold=self.wedge_mtf_alpha_threshold)
        self.mtf_bull_wedge_exhaustion_zone = verdict_bull.get("status") == "wedge_valid:ll3"

    def _p3_body_from_idx(self, p3_idx: int, *, side: int = 0) -> float:
        n = min(self.am_5min.count, self.am_5min.size)
        neg = n - p3_idx
        if neg < 1 or neg > n:
            return self.wedge_confirmed_p3_high
        o = float(self.am_5min.open[-neg])
        c = float(self.am_5min.close[-neg])
        if o <= 0 or c <= 0:
            return self.wedge_confirmed_p3_high
        if side > 0:
            return max(o, c)
        if side < 0:
            return min(o, c)
        return min(o, c)

    def _process_wedge_trigger_phase(self, bar, atr_5, tick, *, is_strong_bar) -> bool:
        if not self.wedge_setup_active or self._wedge_direction == 0:
            return False
        d = self._wedge_direction
        # HH3 (bearish short)
        if d == -1:
            p3_price = self.wedge_confirmed_p3_high
            if bar.high_price > p3_price + tick:
                self._reset_wedge_setup()
                return False
            bars_since = (int((bar.datetime - self.wedge_arm_time).total_seconds() / 300)
                          if self.wedge_arm_time else 0)
            if bars_since > self.wedge_arm_trigger_max_bars:
                self._reset_wedge_setup()
                return False
            if self.am_5min.count >= 2:
                self.wedge_trigger_line = min(
                    float(self.am_5min.low[-1]), float(self.am_5min.low[-2]))
            p3_stop = p3_price + tick
            trigger = bar.low_price - tick
            # Path A: 强趋势棒反向突破
            if (is_strong_bar and bar.close_price < bar.open_price
                    and self.wedge_trigger_line > 0
                    and bar.close_price < self.wedge_trigger_line
                    and not self._pd_blocks_short_target(bar.close_price, atr_5)):
                self._arm_fast_track(
                    direction=-1, opportunity="OPP15_5M_WEDGE_REVERSAL",
                    trigger=trigger,
                    stop=self._cap_short_stop(p3_stop, bar.close_price, atr_5),
                    invalid_line=p3_price)
                self._reset_wedge_setup()
                return True
            # Path B': alpha 衰减 + 跌破 p3 body floor
            if (self.wedge_current_alpha < self.wedge_b_prime_alpha
                    and bar.close_price < bar.open_price
                    and self.wedge_p3_body_floor > 0
                    and bar.close_price < self.wedge_p3_body_floor
                    and bars_since <= self.wedge_arm_trigger_max_bars
                    and not self._pd_blocks_short_target(bar.close_price, atr_5)):
                opp15 = "OPP15_5M_WEDGE_B_PRIME"
                if self._setup_disabled(opp15):
                    self._reset_wedge_setup()
                    return False
                entry_price = bar.close_price - tick
                if self._try_opp15_direct_entry(
                        bar=bar,
                        direction=-1,
                        opportunity=opp15,
                        entry_price=entry_price,
                        stop=p3_stop,
                        invalid_line=p3_price,
                        atr_5=atr_5,
                ):
                    self._reset_wedge_setup()
                    return True
            return False
        # LL3 (bullish long)
        p3_price = self.wedge_confirmed_p3_high
        if bar.low_price < p3_price - tick:
            self._reset_wedge_setup()
            return False
        bars_since = (int((bar.datetime - self.wedge_arm_time).total_seconds() / 300)
                      if self.wedge_arm_time else 0)
        if bars_since > self.wedge_arm_trigger_max_bars:
            self._reset_wedge_setup()
            return False
        if self.am_5min.count >= 2:
            self.wedge_trigger_line = max(
                float(self.am_5min.high[-1]), float(self.am_5min.high[-2]))
        p3_stop = p3_price - tick
        trigger = bar.high_price + tick
        # Path B' (long)
        if (self.wedge_current_alpha < self.wedge_b_prime_alpha
                and bar.close_price > bar.open_price
                and self.wedge_p3_body_floor > 0
                and bar.close_price > self.wedge_p3_body_floor
                and bars_since <= self.wedge_arm_trigger_max_bars
                and not self._pd_blocks_long_target(bar.close_price, atr_5)):
            opp15 = "OPP15_5M_WEDGE_B_PRIME_LONG"
            if self._setup_disabled(opp15):
                self._reset_wedge_setup()
                return False
            entry_price = bar.close_price + tick
            if self._try_opp15_direct_entry(
                    bar=bar,
                    direction=1,
                    opportunity=opp15,
                    entry_price=entry_price,
                    stop=p3_stop,
                    invalid_line=p3_price,
                    atr_5=atr_5,
            ):
                self._reset_wedge_setup()
                return True
        return False

    def _try_arm_wedge_setup(self, bar, atr_5, tick) -> None:
        if self.wedge_setup_active or self.machine_state != "IDLE":
            return
        if self._setup_disabled("OPP15_"):
            return
        if self.late_phase_gate_enabled and self.trend_phase == "LATE":
            return
        if bar.datetime.time() < time(self.wedge_session_start_hour, self.wedge_session_start_minute):
            return
        if atr_5 < self.ttr_rb_min_atr:
            return
        bars = self._array_manager_to_wedge_bars(self.am_5min)
        # HH3 (bearish wedge → short)
        if self.market_context in ("WIDE_RANGE", "TIGHT_RANGE"):
            if not self.wedge_require_mtf or self.mtf_wedge_exhaustion_zone:
                verdict = scan_latest_bearish_wedge(
                    bars, atr_5, tick_size=tick, n_min=self.wedge_n_min_5m,
                    alpha_threshold=self.wedge_alpha_threshold)
                if verdict.get("status") == "wedge_valid:hh3":
                    p3_idx = int(verdict["p3_idx"])
                    if len(bars) - 1 >= p3_idx + 2:
                        p3_high = float(verdict.get("p3_high", 0.0))
                        if p3_high > 0:
                            self.wedge_setup_active = True
                            self._wedge_direction = -1
                            self.wedge_confirmed_p3_high = p3_high
                            self.wedge_arm_time = bar.datetime
                            self.wedge_current_alpha = float(verdict.get("alpha", 0.0))
                            self.wedge_p3_body_floor = self._p3_body_from_idx(p3_idx)
                            if self.am_5min.count >= 2:
                                self.wedge_trigger_line = min(
                                    float(self.am_5min.low[-1]), float(self.am_5min.low[-2]))
                            return
        # LL3 (bullish wedge → long)
        if self.market_context in ("BULL_CHANNEL", "WIDE_RANGE"):
            if not (self.market_context == "WIDE_RANGE" and not self.mtf_bull_wedge_exhaustion_zone):
                if self.always_in in ("LONG", "NONE"):
                    verdict = scan_latest_bullish_wedge(
                        bars, atr_5, tick_size=tick, n_min=self.wedge_n_min_5m,
                        alpha_threshold=self.wedge_alpha_threshold)
                    if verdict.get("status") == "wedge_valid:ll3":
                        p3_idx = int(verdict["p3_idx"])
                        if len(bars) - 1 >= p3_idx + 2:
                            p3_low = float(verdict.get("p3_low", 0.0))
                            if p3_low > 0:
                                self.wedge_setup_active = True
                                self._wedge_direction = 1
                                self.wedge_confirmed_p3_high = p3_low
                                self.wedge_arm_time = bar.datetime
                                self.wedge_current_alpha = float(verdict.get("alpha", 0.0))
                                self.wedge_p3_body_floor = self._p3_body_from_idx(p3_idx, side=1)
                                if self.am_5min.count >= 2:
                                    self.wedge_trigger_line = max(
                                        float(self.am_5min.high[-1]), float(self.am_5min.high[-2]))
                                return
