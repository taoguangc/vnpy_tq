# -*- coding: utf-8 -*-
"""共享 FakeBar / FakeAM / StopCap 策略桩，供 OPP / 楔形单测使用。"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from strategies.pa_cta.wedge import WedgeBar


@dataclass
class FakeBar:
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    datetime: datetime | None = None


class _Arr:
    """支持负索引的 OHLC 数组包装。"""

    def __init__(self, values: list[float]):
        self._v = list(values)

    def __getitem__(self, i: int) -> float:
        return self._v[i]

    def __len__(self) -> int:
        return len(self._v)


@dataclass
class FakeAM:
    open: list[float]
    high: list[float]
    low: list[float]
    close: list[float]
    size: int = 80

    def __post_init__(self) -> None:
        self.open = _Arr(self.open)  # type: ignore[assignment]
        self.high = _Arr(self.high)  # type: ignore[assignment]
        self.low = _Arr(self.low)  # type: ignore[assignment]
        self.close = _Arr(self.close)  # type: ignore[assignment]

    @property
    def count(self) -> int:
        return len(self.open)  # type: ignore[arg-type]


@dataclass
class StopCapStrategy:
    """最小策略桩：止损透传 + 常用门禁默认放行。"""

    always_in: str = "LONG"
    trend_phase: str = "EARLY"
    am_5min: Any = None
    am_15min: Any = None
    am_60min: Any = None
    ttr_rb_min_atr: float = 1.0
    wedge_flag_n_min: int = 3
    wedge_flag_alpha: float = 0.85
    wedge_flag_p3_max_age: int = 16
    wedge_flag_session_bound: bool = True
    wedge_flag_require_tl_break: bool = True
    _opp04_consumed: set = field(default_factory=set)
    _opp04_pending_key: Any = None
    _opp04_session_key: Any = None
    _opp04_bars_in_session: int = 0
    # OPP15
    wedge_setup_active: bool = False
    _wedge_direction: int = 0
    wedge_confirmed_p3_high: float = 0.0
    wedge_arm_time: Any = None
    wedge_arm_trigger_max_bars: int = 12
    wedge_trigger_line: float = 0.0
    wedge_current_alpha: float = 0.5
    wedge_b_prime_alpha: float = 0.7
    wedge_p3_body_floor: float = 0.0
    # OPP16
    two_bar_rev_context: str = "STRONG_BULL,STRONG_BEAR,BULL_CHANNEL,BEAR_CHANNEL"
    two_bar_rev_body_ratio: float = 0.5
    prev_bar_shape: str = "DOWN_TREND"
    opp16_strict_shape: bool = False
    # misc attrs
    extras: dict = field(default_factory=dict)

    def _cap_long_stop(self, raw_stop: float, close: float, atr: float) -> float:
        del close, atr
        return float(raw_stop)

    def _cap_short_stop(self, raw_stop: float, close: float, atr: float) -> float:
        del close, atr
        return float(raw_stop)

    def _pd_blocks_long_target(self, close: float, atr: float) -> bool:
        del close, atr
        return False

    def _pd_blocks_short_target(self, close: float, atr: float) -> bool:
        del close, atr
        return False

    def __getattr__(self, name: str) -> Any:
        if name in self.extras:
            return self.extras[name]
        raise AttributeError(name)


def make_bar(
    o: float,
    h: float,
    l: float,
    c: float,
    *,
    dt: datetime | None = None,
) -> FakeBar:
    return FakeBar(o, h, l, c, dt)


def mirror_ohlc(o: float, h: float, l: float, c: float) -> tuple[float, float, float, float]:
    """价格取负并交换高低 → 多空几何镜像。"""
    return -o, -l, -h, -c


def mirror_wedge_bar(b: WedgeBar) -> WedgeBar:
    return WedgeBar(
        open_price=-b.open_price,
        high_price=-b.low_price,
        low_price=-b.high_price,
        close_price=-b.close_price,
        index=b.index,
    )


def mirror_wedge_bars(bars: list[WedgeBar]) -> list[WedgeBar]:
    return [mirror_wedge_bar(b) for b in bars]


def wb(o: float, h: float, l: float, c: float, idx: int) -> WedgeBar:
    return WedgeBar(o, h, l, c, idx)
