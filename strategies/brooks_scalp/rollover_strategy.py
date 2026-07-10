"""Brooks Scalp v0.1 换月适配：平移止损/目标/挂单价。"""
from __future__ import annotations

from scripts.tq_rollover_data import RolloverEvent
from strategies.brooks_scalp.brooks_scalp_v01 import BrooksScalpV01


class BrooksScalpV01RolloverStrategy(BrooksScalpV01):
    """TQ CbC 换月时同步平移 v0.1 价格刻度。"""

    def on_rollover_adjust(self, event: RolloverEvent) -> None:
        shift = event.price_shift
        if abs(shift) < 1e-9:
            return
        for attr in (
            "entry_price",
            "stop_price",
            "target_price",
            "pullback_low",
            "pullback_high",
            "_entry_fill",
        ):
            val = getattr(self, attr, 0.0)
            if val > 0:
                setattr(self, attr, val + shift)
