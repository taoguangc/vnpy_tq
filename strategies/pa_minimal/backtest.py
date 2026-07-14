# -*- coding: utf-8 -*-
"""pa_minimal CbC 回测入口。"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from strategies.pa_cta.backtest import run_tq_cbc_backtest, print_backtest_report
from strategies.pa_minimal.rollover_strategy import PaMinimal0816RolloverStrategy
from strategies.pa_minimal.strategy import PaMinimal0816Strategy
from strategies.pa_minimal.symbol_config import (
    MINIMAL_NULL_OVERRIDES,
    build_minimal_setting,
    resolve_minimal_profile,
)


def run_minimal_backtest(
    symbol: str = "rb",
    *,
    zero_cost: bool = False,
    verbose: bool = True,
    start: datetime | None = None,
    end: datetime | None = None,
    strategy_overrides: dict | None = None,
) -> dict:
    root = _ROOT
    profile = resolve_minimal_profile(symbol, root)

    def _resolver(sym: str, r: Path, **_: object) -> dict:
        return resolve_minimal_profile(sym, r)

    def _build(prof: dict, capital: float = 200_000.0, max_position: int = 50) -> dict:
        return build_minimal_setting(prof, capital=capital)

    result = run_tq_cbc_backtest(
        symbol=symbol,
        zero_cost=zero_cost,
        verbose=verbose,
        start=start,
        end=end,
        strategy_overrides=strategy_overrides,
        strategy_class=PaMinimal0816RolloverStrategy,
        profile_resolver=_resolver,
        build_setting=_build,
        strategy_label="pa_minimal OPP08+OPP16",
        base_strategy_class=PaMinimal0816Strategy,
        rollover_strategy_class=PaMinimal0816RolloverStrategy,
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="pa_minimal OPP08+OPP16 backtest")
    parser.add_argument("--symbol", default="rb")
    parser.add_argument("--zero-cost", action="store_true")
    parser.add_argument("--null-bg", action="store_true", help="M0-NULL：背景门禁全关")
    parser.add_argument("--no-dual-core", action="store_true", help="M1-01：关 Dual Core")
    args = parser.parse_args()

    overrides: dict = {}
    if args.null_bg:
        overrides.update(MINIMAL_NULL_OVERRIDES)
    if args.no_dual_core:
        overrides["dual_core_enabled"] = False

    bt = run_minimal_backtest(
        symbol=args.symbol,
        zero_cost=args.zero_cost,
        strategy_overrides=overrides or None,
    )
    funnel = bt.get("candidate_funnel") or {}
    if funnel:
        print("\n===== Candidate Ledger 漏斗 =====")
        print(f"candidates: {funnel.get('candidates')}")
        print(f"gate_pass:  {funnel.get('gate_pass')}")
        print(f"armed:      {funnel.get('armed')}")
        print(f"by_setup:   {funnel.get('by_setup')}")
        print(f"blocks:     {funnel.get('blocks')}")


if __name__ == "__main__":
    main()
