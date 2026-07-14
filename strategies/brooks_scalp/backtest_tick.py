"""Brooks Scalp v0.1 — TQ tick parquet → 1m → CbC 回测。

策略逻辑仍在 on_bar（由 tick 重采样 1m K 驱动，非逐 tick on_tick）。

用法:
    .venv\\Scripts\\python.exe -m strategies.brooks_scalp.backtest_tick
    .venv\\Scripts\\python.exe strategies/brooks_scalp/backtest_tick.py --symbol rb \\
        --start 2025-01-01 --end 2026-06-30
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.tq_tick_loader import load_stitched_tick_bars
from strategies.brooks_scalp.backtest import _print_scalp_diagnostics
from strategies.brooks_scalp.rollover_strategy import BrooksScalpV01RolloverStrategy
from strategies.pa_cta.backtest import run_tq_cbc_backtest
from strategies.pa_cta.symbol_config import resolve_symbol_profile


def run_tick_backtest(
    *,
    symbol: str = "rb",
    zero_cost: bool = False,
    start: datetime | None = None,
    end: datetime | None = None,
    slippage_override: float | None = None,
    verbose: bool = True,
) -> dict:
    start = start or datetime(2025, 1, 1)
    end = end or datetime(2026, 6, 30)

    result = run_tq_cbc_backtest(
        symbol=symbol,
        zero_cost=zero_cost,
        start=start,
        end=end,
        slippage_override=slippage_override,
        strategy_class=BrooksScalpV01RolloverStrategy,
        strategy_label="Brooks Scalp v0.1 | tick→1m",
        base_strategy_class=BrooksScalpV01RolloverStrategy,
        rollover_strategy_class=BrooksScalpV01RolloverStrategy,
        bars_loader=load_stitched_tick_bars,
        verbose=verbose,
    )

    if verbose:
        profile = resolve_symbol_profile(symbol, _ROOT)
        _print_scalp_diagnostics(
            result,
            pricetick=float(profile.get("pricetick") or 1.0),
        )

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Brooks Scalp tick→1m CbC 回测")
    parser.add_argument("--symbol", default="rb", help="品种键，如 rb / ma")
    parser.add_argument("--start", default="2025-01-01")
    parser.add_argument("--end", default="2026-06-30")
    parser.add_argument("--zero-cost", action="store_true")
    parser.add_argument("--slippage", type=float, default=None)
    args = parser.parse_args()

    run_tick_backtest(
        symbol=args.symbol,
        zero_cost=args.zero_cost,
        start=datetime.strptime(args.start, "%Y-%m-%d"),
        end=datetime.strptime(args.end, "%Y-%m-%d"),
        slippage_override=args.slippage,
    )
