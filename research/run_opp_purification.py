# -*- coding: utf-8
"""EXP-009F — hc OPP Purification（关拖累 setup 对照）。

用法::
  python -m research.run_opp_purification --symbol hc
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.backtest_trade_analysis import RoundTripTrade, summarize_round_trips
from strategies.pa_cta.backtest import run_parquet_backtest

# 009E′ 静态候选：OPP13 + OPP15；可选加 OPP19 空
HC_VARIANTS: list[tuple[str, str]] = [
    ("基线", ""),
    ("关 OPP13+OPP15", "OPP13_,OPP15_"),
    ("关 OPP13+OPP15+OPP19空", "OPP13_,OPP15_,OPP19_5M_OD_REV_SHORT"),
]


@dataclass
class VariantResult:
    label: str
    disabled: str
    stats: dict
    round_trips: list[RoundTripTrade]
    rt_summary: dict


def _setup_net(trips: list[RoundTripTrade]) -> dict[str, float]:
    acc: dict[str, float] = defaultdict(float)
    for rt in trips:
        acc[rt.setup or "UNKNOWN"] += rt.net_pnl
    return dict(acc)


def main() -> None:
    parser = argparse.ArgumentParser(description="EXP-009F OPP Purification")
    parser.add_argument("--symbol", default="hc")
    args = parser.parse_args()

    print(f"=== EXP-009F OPP Purification | {args.symbol} ===")
    print("窗口: 2023-05-17 ~ 2026-05-16 | 含成本 | disabled_setups 前缀硬禁\n")

    results: list[VariantResult] = []
    for label, disabled in HC_VARIANTS:
        overrides = {"disabled_setups": disabled} if disabled else {}
        bt = run_parquet_backtest(
            symbol=args.symbol,
            verbose=False,
            strategy_overrides=overrides or None,
        )
        results.append(
            VariantResult(
                label=label,
                disabled=disabled or "(none)",
                stats=bt["stats"],
                round_trips=bt["round_trips"],
                rt_summary=bt["rt_summary"],
            )
        )

    print("| 版本 | disabled | 总净盈亏 | Sharpe | 笔数 | WR | PF | maxDD% | ΔPnL |")
    print("|------|----------|----------|--------|------|-----|-----|--------|------|")
    base_pnl = results[0].stats.get("total_net_pnl", 0.0)
    for v in results:
        s = v.stats
        rs = v.rt_summary
        pnl = s.get("total_net_pnl", 0.0)
        print(
            f"| {v.label} | `{v.disabled}` | {pnl:+,.0f} | "
            f"{s.get('sharpe_ratio', 0):.2f} | {int(rs.get('total', 0))} | "
            f"{rs.get('win_rate', 0):.1f}% | {rs.get('profit_factor', 0):.2f} | "
            f"{s.get('max_ddpercent', 0):.2f}% | {pnl - base_pnl:+,.0f} |"
        )

    print("\n--- 各版本剩余 setup 净盈亏 ---")
    for v in results:
        nets = _setup_net(v.round_trips)
        print(f"\n[{v.label}]")
        for setup, net in sorted(nets.items(), key=lambda x: x[1], reverse=True):
            n = sum(1 for t in v.round_trips if (t.setup or "") == setup)
            print(f"  {setup:<42s} {n:>3}笔  {net:>+10.0f}")

    best = max(results, key=lambda v: v.stats.get("total_net_pnl", 0.0))
    print(f"\n样本内最优: {best.label} ({best.stats.get('total_net_pnl', 0):+,.0f})")
    print("注意: 静态加总不可代替本表；跨品种须另跑（EXP-012x 先例）。")


if __name__ == "__main__":
    main()
