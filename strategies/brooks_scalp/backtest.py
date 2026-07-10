"""Brooks Scalp v0.1 Parquet/CbC 回测入口。

用法:
    .venv\\Scripts\\python.exe -m strategies.brooks_scalp.backtest
    .venv\\Scripts\\python.exe strategies/brooks_scalp/backtest.py --symbol ma
    .venv\\Scripts\\python.exe strategies/brooks_scalp/backtest.py --symbol ma \\
        --start 2024-01-01 --end 2026-06-30
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from strategies.brooks_scalp.rollover_strategy import BrooksScalpV01RolloverStrategy
from strategies.pa_cta.backtest import run_tq_cbc_backtest


def _print_scalp_diagnostics(result: dict, *, pricetick: float) -> None:
    from scripts.backtest_trade_analysis import summarize_round_trips

    round_trips = result.get("round_trips") or []
    rt_summary = summarize_round_trips(round_trips)
    stats = result.get("stats") or {}

    print("\n===== Brooks Scalp v0.1 诊断 =====")
    print(f"Trades: {int(stats.get('total_trade_count') or 0)}")
    if rt_summary:
        wr = rt_summary.get("win_rate")
        pf = rt_summary.get("profit_factor")
        if wr is not None:
            print(f"WR: {wr:.2f}%")
        if pf is not None:
            print(f"PF: {pf:.2f}")
    sharpe = stats.get("sharpe_ratio")
    if sharpe is not None:
        print(f"Sharpe: {sharpe:.2f}")

    trade_log = result.get("trade_log") or []
    if trade_log:
        mfe_vals = [float(t.get("mfe_ticks", 0) or 0) for t in trade_log]
        mae_vals = [float(t.get("mae_ticks", 0) or 0) for t in trade_log]
        print(
            f"MFE (ticks): avg={sum(mfe_vals)/len(mfe_vals):.1f} "
            f"med={sorted(mfe_vals)[len(mfe_vals)//2]:.1f}"
        )
        print(
            f"MAE (ticks): avg={sum(mae_vals)/len(mae_vals):.1f} "
            f"med={sorted(mae_vals)[len(mae_vals)//2]:.1f}"
        )

        monthly: dict[str, float] = defaultdict(float)
        hourly: dict[int, float] = defaultdict(float)
        for rt in round_trips:
            key = rt.exit_time.strftime("%Y-%m")
            monthly[key] += rt.net_pnl
            hourly[rt.exit_time.hour] += rt.net_pnl

        print("\n----- 每月净盈亏 -----")
        for month in sorted(monthly):
            print(f"  {month}: {monthly[month:+,.0f}")
        print("\n----- 每小时净盈亏（按 exit 小时 CST）-----")
        for hour in sorted(hourly):
            print(f"  {hour:02d}:00  {hourly[hour]:+,.0f}")
    print("=" * 40)


def run_parquet_backtest(
    *,
    symbol: str = "ma",
    zero_cost: bool = False,
    start: datetime | None = None,
    end: datetime | None = None,
    slippage_override: float | None = None,
    verbose: bool = True,
) -> dict:
    """MA888 / 品种键 ma → TQ CbC data/tq/MA/。"""
    start = start or datetime(2024, 1, 1)
    end = end or datetime(2026, 6, 30)

    result = run_tq_cbc_backtest(
        symbol=symbol,
        zero_cost=zero_cost,
        start=start,
        end=end,
        slippage_override=slippage_override,
        strategy_class=BrooksScalpV01RolloverStrategy,
        strategy_label="Brooks Scalp v0.1",
        base_strategy_class=BrooksScalpV01RolloverStrategy,
        rollover_strategy_class=BrooksScalpV01RolloverStrategy,
        verbose=verbose,
    )

    if verbose:
        from strategies.pa_cta.symbol_config import resolve_symbol_profile

        profile = resolve_symbol_profile(symbol, _ROOT)
        _print_scalp_diagnostics(
            result,
            pricetick=float(profile.get("pricetick") or 1.0),
        )

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Brooks Scalp v0.1 CbC 回测")
    parser.add_argument(
        "--symbol",
        default="ma",
        help="品种键，ma=MA888(CZCE 甲醇 CbC)",
    )
    parser.add_argument("--start", default="2024-01-01")
    parser.add_argument("--end", default="2026-06-30")
    parser.add_argument("--zero-cost", action="store_true")
    parser.add_argument("--slippage", type=float, default=None)
    args = parser.parse_args()

    run_parquet_backtest(
        symbol=args.symbol,
        zero_cost=args.zero_cost,
        start=datetime.strptime(args.start, "%Y-%m-%d"),
        end=datetime.strptime(args.end, "%Y-%m-%d"),
        slippage_override=args.slippage,
    )
