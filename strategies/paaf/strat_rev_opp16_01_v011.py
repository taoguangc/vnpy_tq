"""STRAT_REV_OPP16_01@0.1.1 — adapter window repair lineage.

Repair from @0.1.0（immutable binding file）. Morphology still OPP16@1.0.0.
Runtime fix lives in ``strategies/paaf/adapters/vnpy_adapter.py``
（``_series_len`` / ``bars_from_am``）；this module stamps the repair version
for identity / evidence lineage.

≠ Alpha · ≠ parameter change · ≠ rewrite of Closed EXP001.
"""

from __future__ import annotations

from strategies.paaf.strat_rev_opp16_01 import StratRevOpp1601Strategy


class StratRevOpp1601StrategyV011(StratRevOpp1601Strategy):
    """v0.1.1 orchestrator: identical parameters · repair version stamp."""

    strategy_version = "0.1.1"

    def on_init(self) -> None:
        self.write_log(
            f"{self.strategy_id}@{self.strategy_version} initialized "
            f"(CID_003 repair lineage from 0.1.0; detector=OPP16@1.0.0; "
            f"adapter_window_fix=YES; signal=5m; risk=1m)"
        )
        self.load_bar(30)
