"""休市间隙感知 BarGenerator：跨交易段前强制收盘未完成合成 K。"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from vnpy.trader.constant import Interval
from vnpy.trader.object import BarData
from vnpy.trader.utility import BarGenerator

CST = ZoneInfo("Asia/Shanghai")
GAP_MINUTES = 5


def _bar_cst(bar: BarData) -> datetime:
    dt = bar.datetime
    if dt.tzinfo is None:
        return dt.replace(tzinfo=CST)
    return dt.astimezone(CST)


class SessionAwareBarGenerator:
    """1m 序列出现 >GAP_MINUTES 空档时，先 flush 未完成的 window/hour bar。"""

    def __init__(self, inner: BarGenerator) -> None:
        self._inner = inner
        self._last_dt: datetime | None = None

    def update_bar(self, bar: BarData) -> None:
        dt = _bar_cst(bar)
        if self._last_dt is not None:
            gap_sec = (dt - self._last_dt).total_seconds()
            if gap_sec > GAP_MINUTES * 60:
                self._flush()
        self._inner.update_bar(bar)
        self._last_dt = dt

    def _flush(self) -> None:
        bg = self._inner
        if bg.interval == Interval.HOUR and bg.hour_bar is not None:
            bg.on_hour_bar(bg.hour_bar)
            bg.hour_bar = None
            return
        if bg.window_bar is not None and bg.on_window_bar is not None:
            bg.on_window_bar(bg.window_bar)
            bg.window_bar = None
