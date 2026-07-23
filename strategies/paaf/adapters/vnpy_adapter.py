"""vn.py → PAAF 边界适配。

本模块是唯一允许直接依赖 vn.py 的 PAAF 适配层。
Domain / Detector / ContextEngine 不得 import vn.py；需要 Bar 语义时经本层转换。

当前 Detector 仍接收只读行情窗口 ``am: Any``；本适配器提供只读辅助，
不改变 ``Market Data → Context → Detector → Risk → Execution → Logger`` 主链。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, Sequence

from vnpy.trader.object import BarData


@dataclass(frozen=True)
class PaafBar:
    """PAAF 侧只读 Bar；不携带 vn.py 类型。"""

    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0
    open_interest: float = 0.0
    datetime: Optional[datetime] = None
    symbol: str = ""


def bar_from_vnpy(bar: BarData) -> PaafBar:
    """将 vn.py ``BarData`` 转为 ``PaafBar``。"""

    return PaafBar(
        open=float(bar.open_price),
        high=float(bar.high_price),
        low=float(bar.low_price),
        close=float(bar.close_price),
        volume=float(bar.volume),
        open_interest=float(bar.open_interest),
        datetime=bar.datetime,
        symbol=str(bar.symbol or ""),
    )


def am_is_inited(am: Any) -> bool:
    """ArrayManager（或同协议对象）是否已可读取。"""

    if am is None:
        return False
    inited = getattr(am, "inited", None)
    if isinstance(inited, bool):
        return inited
    count = getattr(am, "count", None)
    if isinstance(count, int):
        return count > 0
    close = getattr(am, "close", None)
    return isinstance(close, Sequence) and len(close) > 0


def _array_window_len(am: Any) -> int:
    """固定缓冲长度（ArrayManager.size 窗口），兼容 list 与 numpy.ndarray。"""

    for name in ("close", "close_array"):
        series = getattr(am, name, None)
        if series is None:
            continue
        try:
            return int(len(series))
        except TypeError:
            continue
    return 0


def _series_len(am: Any) -> int:
    """可用 Bar 窗口长度。

    vn.py ``ArrayManager`` 的 ``count`` 可超过固定 ``size``；正下标只在
    ``0 .. len(close)-1`` 有效。长度取 ``min(count, array_len)``，避免
    ``bars_from_am`` 在 warmup 后读到越界默认 0.0（CID_003 zero-trade 根因）。

    注意：``numpy.ndarray`` 不是 ``typing.Sequence``，不可用 ``isinstance(..., Sequence)``。
    """

    array_len = _array_window_len(am)
    count = getattr(am, "count", None)
    if isinstance(count, int) and count >= 0:
        if array_len > 0:
            return min(count, array_len)
        return count
    return array_len


def last_bar(am: Any) -> Optional[PaafBar]:
    """从只读行情窗口取最近一根 Bar；窗口未就绪返回 None。"""

    if not am_is_inited(am):
        return None
    n = _series_len(am)
    if n <= 0:
        return None
    return _bar_at(am, -1)


def bars_from_am(am: Any, lookback: Optional[int] = None) -> list[PaafBar]:
    """从只读行情窗口提取最近 ``lookback`` 根 Bar（默认全部可用）。

    使用负下标（``-lookback .. -1``），与 ArrayManager 环形缓冲一致。
    ArrayManager 通常不保留逐 bar datetime；缺失时 ``PaafBar.datetime`` 为 None。
    """

    if not am_is_inited(am):
        return []
    n = _series_len(am)
    if n <= 0:
        return []
    if lookback is None or lookback > n:
        lookback = n
    if lookback <= 0:
        return []
    return [_bar_at(am, i) for i in range(-lookback, 0)]


def _bar_at(am: Any, index: int) -> PaafBar:
    def _get(name: str, default: float = 0.0) -> float:
        series = getattr(am, name, None)
        if series is None:
            return default
        try:
            return float(series[index])
        except (IndexError, TypeError, ValueError):
            return default

    symbol = str(getattr(am, "symbol", "") or "")
    return PaafBar(
        open=_get("open"),
        high=_get("high"),
        low=_get("low"),
        close=_get("close"),
        volume=_get("volume"),
        open_interest=_get("open_interest"),
        datetime=None,
        symbol=symbol,
    )
