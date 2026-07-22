"""STRAT_TREND_BROOKS_SCALP_02@0.1.1 — rollover price-scale repair.

Repair lineage from 0.1.0（immutable）. Morphology still BROOKS_SCALP_FP@0.1.0.
Only adds on_rollover_adjust for CbC contract switch price continuity.
"""
from __future__ import annotations

from scripts.tq_rollover_data import RolloverEvent
from strategies.paaf.brooks_scalp_paaf_strategy import BrooksScalpPaafStrategy


class BrooksScalpPaafStrategyV011(BrooksScalpPaafStrategy):
    """v0.1.1 orchestrator: identical to v0.1.0 + rollover price shift."""

    strategy_version = "0.1.1"

    def on_init(self) -> None:
        self.write_log(
            f"{self.strategy_id}@{self.strategy_version} initialized "
            f"(repair lineage from 0.1.0; detector=BROOKS_SCALP_FP@0.1.0; "
            f"on_rollover_adjust=YES)"
        )
        self.load_bar(30)

    def on_rollover_adjust(self, event: RolloverEvent) -> None:
        shift = float(event.price_shift)
        if abs(shift) < 1e-9:
            return
        for attr in (
            "entry_price",
            "stop_price",
            "target_price",
            "_entry_fill",
        ):
            val = float(getattr(self, attr, 0.0) or 0.0)
            if val > 0:
                setattr(self, attr, val + shift)
        self.write_log(
            f"on_rollover_adjust shift={shift:.4f} "
            f"{event.from_yymm}->{event.to_yymm} "
            f"stop={self.stop_price} target={self.target_price}"
        )
