# -*- coding: utf-8
"""EXP-009 — Trade Management Lab（pa_cta round_trips 同一 Entry cohort）。

对比 ACTUAL / FIXED_1R / FIXED_2R / TIME_120 / ATR_TRAIL / STOP_EOD。

用法::
  python -m research.run_tm_lab --symbol rb
  python -m research.run_tm_lab --symbol rb --start 2024-01-01 --end 2025-06-30
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.event_engine.bars import load_bars
from research.trade_management_lab import (
    ExitRule,
    build_cohort_from_backtest,
    format_summary_table,
    run_management_lab,
    summarize_by_setup,
)
from scripts.backtest_trade_analysis import summarize_round_trips
from strategies.pa_cta.backtest import run_parquet_backtest
from strategies.pa_cta.symbol_config import resolve_symbol_profile


def _parse_date(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d")


def main() -> None:
    parser = argparse.ArgumentParser(description="EXP-009 Trade Management Lab")
    parser.add_argument("--symbol", default="rb")
    parser.add_argument("--start", default=None, help="YYYY-MM-DD（默认 profile 全窗）")
    parser.add_argument("--end", default=None, help="YYYY-MM-DD")
    parser.add_argument("--zero-cost", action="store_true")
    parser.add_argument("--output-dir", default=str(ROOT / "research" / "output"))
    parser.add_argument(
        "--v3",
        action="store_true",
        help="EXP-028 Phase-3：加入 FAMILY_CONTINUATION / FAMILY_REVERSAL / FAMILY_ASSIGNED",
    )
    args = parser.parse_args()

    start = _parse_date(args.start) if args.start else None
    end = _parse_date(args.end) if args.end else None

    profile = resolve_symbol_profile(args.symbol, ROOT)
    symbol = profile["symbol"]
    contract_size = float(profile["size"])
    rate = 0.0 if args.zero_cost else 0.00003
    slippage = 0 if args.zero_cost else float(profile["slippage"])

    print(f"=== EXP-009 Trade Management Lab | {symbol} ===")
    bt = run_parquet_backtest(
        symbol=args.symbol,
        zero_cost=args.zero_cost,
        verbose=False,
        start=start,
        end=end,
    )
    round_trips = bt["round_trips"]
    trade_log = bt.get("trade_log") or []
    stats = bt["stats"]

    rt_sum = summarize_round_trips(round_trips)
    print(f"\n--- pa_cta ACTUAL 回测 ---")
    print(f"区间: {start or '2023-05-17'} ~ {end or '2026-05-16'}")
    print(f"完整交易: {int(rt_sum['total'])} 笔 | WR {rt_sum['win_rate']:.1f}% | PF {rt_sum['profit_factor']:.2f}")
    print(f"总净盈亏: {stats.get('total_net_pnl', 0):,.0f} | Sharpe {stats.get('sharpe_ratio', 0):.2f}")

    bars, source = load_bars(symbol=args.symbol, start=start, end=end)
    print(f"1m 数据: {source} ({len(bars):,} bars)")

    cohort = build_cohort_from_backtest(
        round_trips, trade_log, bars_1m=bars, contract_size=contract_size,
    )
    print(f"可重放 cohort: {len(cohort)} / {len(trade_log)} 笔（需 initial R）")

    if args.v3:
        from strategies.pa_cta.exit_families import resolve_exit_family

        cont_n = sum(1 for t in cohort if resolve_exit_family(t.setup).value == "CONTINUATION")
        rev_n = len(cohort) - cont_n
        print(f"Phase-3 族分布: CONTINUATION={cont_n} REVERSAL={rev_n}")

    rules = None
    if args.v3:
        rules = [
            ExitRule.ACTUAL,
            ExitRule.FAMILY_ASSIGNED,
            ExitRule.FAMILY_CONTINUATION,
            ExitRule.FAMILY_REVERSAL,
            ExitRule.STOP_EOD,
        ]

    if not cohort:
        print("ERROR: cohort 为空，请确认回测有成交且 _entry_snapshot 含 initial_stop。")
        sys.exit(1)

    sim_results, summaries = run_management_lab(
        cohort,
        bars,
        contract_size=contract_size,
        rate=rate,
        slippage=slippage,
        rules=rules,
    )

    print("\n--- 出场规则对照（同一 Entry cohort）---")
    print(format_summary_table(summaries))

    actual = next(s for s in summaries if s.rule == ExitRule.ACTUAL)
    fixed_1r = next(s for s in summaries if s.rule == ExitRule.FIXED_1R)
    print(f"\n--- Entry vs Management 分解（待验证假设检验）---")
    print(f"Entry 代理 (FIXED_1R): PF={fixed_1r.profit_factor:.2f} net={fixed_1r.net_pnl:+,.0f}")
    print(f"Production (ACTUAL):   PF={actual.profit_factor:.2f} net={actual.net_pnl:+,.0f}")
    if fixed_1r.profit_factor > 0:
        lift = actual.profit_factor / fixed_1r.profit_factor
        print(f"Management PF / Entry PF = {lift:.2f}（>1 表示管理层增值）")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    sym_tag = args.symbol.lower()
    win_tag = ""
    if start and end:
        win_tag = f"_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}"
    exp_tag = "exp028" if args.v3 else "exp009"
    summary_path = out_dir / f"{exp_tag}_tm_lab_{sym_tag}{win_tag}_summary.csv"
    setup_path = out_dir / f"{exp_tag}_tm_lab_{sym_tag}{win_tag}_by_setup.csv"

    import pandas as pd

    pd.DataFrame([
        {
            "rule": s.rule.value,
            "n": s.n,
            "skipped": s.skipped,
            "win_rate": s.win_rate,
            "profit_factor": s.profit_factor,
            "net_pnl": s.net_pnl,
            "avg_r": s.avg_r,
            "avg_holding_min": s.avg_holding_min,
            "vs_actual_delta": s.vs_actual_delta,
        }
        for s in summaries
    ]).to_csv(summary_path, index=False, encoding="utf-8-sig")

    summarize_by_setup(sim_results).to_csv(setup_path, index=False, encoding="utf-8-sig")
    print(f"\n输出: {summary_path.name} | {setup_path.name}")


if __name__ == "__main__":
    main()
