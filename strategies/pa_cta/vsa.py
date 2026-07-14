# -*- coding: utf-8 -*-
"""VSA 量价滤网与价格持续性豁免。"""
from __future__ import annotations

from collections import deque

import numpy as np
from vnpy_ctastrategy import BarData


class VsaFilterMixin:
    """5m VSA 开仓熔断 + 价格持续性豁免。

    量能分位默认用「同时段历史相对量」：只与过去若干交易日
    同一 (hour, minute) 的 5m 棒比较，避免夜盘/开盘/午前混窗误判。
    """

    def _print_vsa_funnel(self) -> None:
        if not getattr(self, "vsa_enabled", False):
            return
        mode = (
            "同时段相对量"
            if getattr(self, "vsa_session_relative_enabled", True)
            else f"近{int(self.vsa_volume_window)}根混窗"
        )
        lines = [
            "=" * 44,
            "VSA 开仓熔断",
            "=" * 44,
            f"  量能口径:           {mode}",
            f"  拦截次数:           {self.vsa_block_count:>6}",
            f"  持续性豁免:         {self.vsa_persistence_exempt_count:>6}",
            "=" * 44,
        ]
        self.write_log("\n" + "\n".join(lines))

    def _ensure_vsa_slot_hist(self) -> deque:
        hist = getattr(self, "_vsa_slot_hist", None)
        if hist is None:
            # ~20 交易日 × ~100 根 5m；留余量给跨夜品种
            hist = deque(maxlen=4000)
            self._vsa_slot_hist = hist
        return hist

    def _record_vsa_slot_volume(self, bar: BarData) -> None:
        """在信号逻辑之后写入，保证当前棒不进入自身分位样本。"""
        if not getattr(self, "vsa_enabled", False):
            return
        vol = float(bar.volume)
        if vol <= 0:
            return
        dt = bar.datetime
        self._ensure_vsa_slot_hist().append((int(dt.hour), int(dt.minute), vol))

    def _rolling_volume_percentile(self, vol: float) -> float:
        """近 N 根 5m 混窗分位（旧口径 / 同时段样本不足时回退）。"""
        n = min(int(self.vsa_volume_window), self.am_5min.count)
        if n < 20:
            return 50.0
        vol_slice = self.am_5min.volume_array[-n:]
        valid = vol_slice[vol_slice > 0]
        if len(valid) < 20:
            return 50.0
        sorted_valid = np.sort(valid)
        return float(np.searchsorted(sorted_valid, vol) / len(sorted_valid) * 100.0)

    def _session_relative_volume_pct(self, vol: float, bar: BarData) -> float:
        """同一 (hour, minute) 历史相对量分位；样本不足回退混窗。"""
        hist = getattr(self, "_vsa_slot_hist", None)
        if not hist:
            return self._rolling_volume_percentile(vol)
        hour, minute = int(bar.datetime.hour), int(bar.datetime.minute)
        lookback = max(int(getattr(self, "vsa_session_lookback_days", 15)), 1)
        min_n = max(int(getattr(self, "vsa_session_min_samples", 8)), 3)
        same: list[float] = []
        for h, m, v in reversed(hist):
            if h == hour and m == minute and v > 0:
                same.append(float(v))
                if len(same) >= lookback:
                    break
        if len(same) < min_n:
            return self._rolling_volume_percentile(vol)
        sorted_same = np.sort(np.asarray(same, dtype=float))
        return float(np.searchsorted(sorted_same, vol) / len(sorted_same) * 100.0)

    def _volume_percentile(self, vol: float, bar: BarData | None = None) -> float:
        """信号棒成交量分位 (0-100)。默认同时段相对量。"""
        if (
            getattr(self, "vsa_session_relative_enabled", True)
            and bar is not None
        ):
            return self._session_relative_volume_pct(vol, bar)
        return self._rolling_volume_percentile(vol)

    def _is_price_persistence_exempt(self, direction: int) -> bool:
        """v0.9.66 萌芽期豁免：相对索引净位移 + 允许 1 根异色 + 浅回踩。"""
        if not self.vsa_persistence_enabled or not self.am_5min.inited:
            return False

        n = int(self.vsa_persistence_bars)
        if n < 2 or self.am_5min.count < n:
            return False

        tick = self.get_pricetick()
        atr_5 = float(self.am_5min.atr(self.atr_window))
        if atr_5 <= 0:
            return False

        c_end = float(self.am_5min.close[-1])
        o_start = float(self.am_5min.open[-n])
        net_displacement = abs(c_end - o_start)
        min_disp = max(
            int(self.vsa_persistence_displacement_ticks) * tick,
            float(self.vsa_persistence_displacement_atr) * atr_5,
        )
        if net_displacement < min_disp:
            return False

        closes = self.am_5min.close_array[-n:]
        opens = self.am_5min.open_array[-n:]
        tol = max(0, int(self.vsa_persistence_opposite_tolerance))

        if direction > 0:
            if not (c_end > o_start and closes[-1] > opens[-1]):
                return False
            bull = sum(1 for c, o in zip(closes, opens) if c > o)
            if bull < n - tol:
                return False
            mid_early = (
                float(self.am_5min.high[-n]) + float(self.am_5min.low[-n])
            ) / 2.0
            if float(np.min(self.am_5min.low_array[-2:])) < mid_early:
                return False
            for i in range(1, n):
                if float(self.am_5min.low[-n + i]) < float(self.am_5min.low[-n + i - 1]) - tick:
                    return False
        elif direction < 0:
            if not (c_end < o_start and closes[-1] < opens[-1]):
                return False
            bear = sum(1 for c, o in zip(closes, opens) if c < o)
            if bear < n - tol:
                return False
            mid_early = (
                float(self.am_5min.high[-n]) + float(self.am_5min.low[-n])
            ) / 2.0
            if float(np.max(self.am_5min.high_array[-2:])) > mid_early:
                return False
            for i in range(1, n):
                if float(self.am_5min.high[-n + i]) > float(self.am_5min.high[-n + i - 1]) + tick:
                    return False
        else:
            return False

        return True

    def _vsa_blocks_entry(
        self, direction: int, bar: BarData | None = None
    ) -> bool:
        """VSA 量价滤网：无量空涨/出货(多)、无量空跌/止跌量(空) → 熔断开仓。"""
        if not self.vsa_enabled or not self.am_5min.inited:
            return False
        if bar is not None:
            o, h, l, c = (
                bar.open_price,
                bar.high_price,
                bar.low_price,
                bar.close_price,
            )
            vol = float(bar.volume)
        else:
            o = float(self.am_5min.open[-1])
            h = float(self.am_5min.high[-1])
            l = float(self.am_5min.low[-1])
            c = float(self.am_5min.close[-1])
            vol = float(self.am_5min.volume[-1])
        atr_5 = float(self.am_5min.atr(self.atr_window))
        if atr_5 <= 0 or vol <= 0:
            return False
        spread = h - l
        if spread <= 0:
            return False
        vol_pct = self._volume_percentile(vol, bar=bar)
        close_pos = (c - l) / spread
        is_bull = c > o
        is_bear = c < o
        min_spread = self.vsa_spread_atr_mult * atr_5
        body_ratio = abs(c - o) / spread
        blocked = False
        if direction > 0:
            if (
                is_bull
                and vol_pct <= self.vsa_low_volume_pct
                and spread >= min_spread
            ):
                blocked = True
            elif vol_pct >= self.vsa_high_volume_pct and is_bull:
                if close_pos <= self.vsa_weak_close_ratio:
                    blocked = True
                elif body_ratio <= 0.25:
                    blocked = True
        elif direction < 0:
            if (
                is_bear
                and vol_pct <= self.vsa_low_volume_pct
                and spread >= min_spread
            ):
                blocked = True
            elif vol_pct >= self.vsa_high_volume_pct and is_bear:
                if close_pos >= self.vsa_stopping_close_ratio:
                    blocked = True
                elif body_ratio <= 0.25:
                    blocked = True
        if blocked:
            if self._is_price_persistence_exempt(direction):
                self._vsa_persistence_exempt_count += 1
                self.vsa_persistence_exempt_count = self._vsa_persistence_exempt_count
                return False
            self._vsa_block_count += 1
            self.vsa_block_count = self._vsa_block_count
        return blocked

    def _opp13_volume_allows_entry(self, bar: BarData, direction: int) -> bool:
        """OPP13 日边界：信号棒量能分位下限；高潮量须配合拒绝收盘（Brooks 边界测试须有参与）。"""
        if not getattr(self, "opp13_vol_filter_enabled", False):
            return True
        vol = float(bar.volume)
        if vol <= 0:
            return False
        vol_pct = self._volume_percentile(vol, bar=bar)
        if vol_pct < float(getattr(self, "opp13_min_volume_pct", 45.0)):
            return False
        climax_pct = float(getattr(self, "opp13_climax_volume_pct", 65.0))
        if vol_pct >= climax_pct:
            spread = bar.high_price - bar.low_price
            if spread <= 0:
                return False
            close_pos = (bar.close_price - bar.low_price) / spread
            if direction < 0:
                if close_pos > float(getattr(self, "opp13_short_max_close_pos", 0.50)):
                    return False
            elif direction > 0:
                if close_pos < float(getattr(self, "opp13_long_min_close_pos", 0.50)):
                    return False
        return True
