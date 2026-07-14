# -*- coding: utf-8 -*-
"""诊断：武装 Lab 1 手毛正 vs M0-BASE live 账户负。

分解三层：成本、定仓、出场。不改策略参数。

用法::
  python -m research.run_pa_minimal_gap_diag --symbol rb
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from strategies.pa_minimal.backtest import run_minimal_backtest
from strategies.pa_minimal.symbol_config import resolve_minimal_profile


def main() -> None:
    parser = argparse.ArgumentParser(description="pa_minimal gap diagnosis")
    parser.add_argument("--symbol", default="rb")
    parser.add_argument("--output-dir", default=str(ROOT / "research" / "output"))
    args = parser.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    profile = resolve_minimal_profile(args.symbol, ROOT)
    print("=== 成本/定仓/出场缺口诊断 ===")
    print(
        f"品种 {args.symbol} | tick={profile['pricetick']} "
        f"size={profile['size']} slip={profile['slippage']} "
        f"risk_capital={profile.get('risk_capital')}"
    )

    bt = run_minimal_backtest(symbol=args.symbol, verbose=False)
    trips = bt["round_trips"]
    stats = bt["stats"]

    rows = []
    for t in trips:
        cost = t.gross_pnl - t.net_pnl
        rows.append(
            {
                "setup": t.setup,
                "exit_reason": t.exit_reason,
                "volume": t.volume,
                "gross_pnl": t.gross_pnl,
                "net_pnl": t.net_pnl,
                "cost": cost,
                "gross_1lot": t.gross_pnl / t.volume if t.volume else 0.0,
                "net_1lot": t.net_pnl / t.volume if t.volume else 0.0,
                "cost_1lot": cost / t.volume if t.volume else 0.0,
                "holding_minutes": t.holding_minutes,
            }
        )
    df = pd.DataFrame(rows)
    detail_path = out / f"exp_m0_gap_trips_{args.symbol.lower()}.csv"
    df.to_csv(detail_path, index=False, encoding="utf-8-sig")

    gross = float(df["gross_pnl"].sum())
    net = float(df["net_pnl"].sum())
    cost = float(df["cost"].sum())
    commission = float(stats.get("total_commission") or 0)
    slippage = float(stats.get("total_slippage") or 0)

    print("\n----- 1. 成本层 -----")
    print(f"价差毛利(gross): {gross:+,.0f}")
    print(f"手续费: {commission:,.0f}  滑点: {slippage:,.0f}  合计成本: {cost:,.0f}")
    print(f"账户净盈亏: {net:+,.0f}")
    print(f"成本/|毛利|: {cost / abs(gross):.1f}x" if abs(gross) > 1 else "")
    print(
        f"1 手折算: sum(gross/vol)={df['gross_1lot'].sum():+.0f}  "
        f"sum(net/vol)={df['net_1lot'].sum():+.0f}  "
        f"median(cost/vol)={df['cost_1lot'].median():.1f}"
    )

    print("\n----- 2. 定仓层 -----")
    print(
        f"手数 min/中位/max: {df.volume.min():.0f}/"
        f"{df.volume.median():.0f}/{df.volume.max():.0f}  "
        f"合计手数={df.volume.sum():.0f}"
    )
    at_cap = (df.volume >= 50).mean()
    print(f"顶满 max_position(50) 占比: {at_cap:.0%}")
    print("说明: 滑点公式 volume×size×slippage，手数↑则绝对成本近似线性放大。")

    print("\n----- 3. 出场层 -----")
    by_ex = (
        df.groupby("exit_reason")
        .agg(n=("net_pnl", "count"), net=("net_pnl", "sum"), gross=("gross_pnl", "sum"))
        .sort_values("net")
    )
    print(by_ex.to_string())

    arm_path = out / f"exp_m0_arm_detail_{args.symbol.lower()}.csv"
    if arm_path.exists():
        arm = pd.read_csv(arm_path)
        af = arm[(arm.rule == "A_CURRENT") & (arm.filled == True)].copy()  # noqa: E712
        med_c = float(df["cost_1lot"].median())
        af["net_after_cost"] = af["net_pnl_1lot"] - med_c
        print("\n----- 4. 对照武装 Lab A（固定止损/1R/120m，1 手）-----")
        print(f"成交笔数 Lab={len(af)}  live={len(df)}")
        print(f"Lab 毛盈亏合计: {af['net_pnl_1lot'].sum():+.0f}")
        print(f"扣中位 1 手成本({med_c:.1f}) 后: {af['net_after_cost'].sum():+.0f}")
        print(f"Lab 出场: {af['exit_tag'].value_counts().to_dict()}")
        print(f"live 1 手折算毛利: {df['gross_1lot'].sum():+.0f}（出场不同，集合也不完全相同）")

    summary = {
        "gross": gross,
        "net": net,
        "cost": cost,
        "commission": commission,
        "slippage": slippage,
        "n": len(df),
        "vol_sum": float(df.volume.sum()),
        "vol_median": float(df.volume.median()),
        "at_cap_pct": float(at_cap),
        "gross_1lot_sum": float(df["gross_1lot"].sum()),
        "net_1lot_sum": float(df["net_1lot"].sum()),
        "median_cost_1lot": float(df["cost_1lot"].median()),
    }
    sum_path = out / f"exp_m0_gap_summary_{args.symbol.lower()}.csv"
    pd.DataFrame([summary]).to_csv(sum_path, index=False, encoding="utf-8-sig")
    print(f"\n明细: {detail_path}")
    print(f"汇总: {sum_path}")


if __name__ == "__main__":
    main()
