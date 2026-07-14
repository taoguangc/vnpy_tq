# -*- coding: utf-8 -*-
"""EXP-M0 / M1 — pa_minimal 消融驱动（单变量，配额内）。

用法::
  python -m research.run_pa_minimal_ablation --symbol rb
  # 默认跑 M0-BASE + M0-NULL + M1-01(dual_core OFF)，共 3 次回测
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.backtest_trade_analysis import summarize_round_trips
from strategies.pa_minimal.backtest import run_minimal_backtest
from strategies.pa_minimal.symbol_config import MINIMAL_NULL_OVERRIDES


def _filter_setups(trips: list, prefixes: tuple[str, ...]) -> list:
    return [t for t in trips if (t.setup or "").startswith(prefixes)]


def _row(label: str, bt: dict) -> dict:
    stats = bt["stats"]
    trips = bt["round_trips"]
    rt = summarize_round_trips(trips) or {}
    t08 = _filter_setups(trips, ("OPP08_",))
    t16 = _filter_setups(trips, ("OPP16_",))
    other = [t for t in trips if not (t.setup or "").startswith(("OPP08_", "OPP16_"))]
    funnel = bt.get("candidate_funnel") or {}
    end_bal = stats.get("end_balance")
    bankrupt = end_bal is not None and float(end_bal) <= 0
    pnl = stats.get("total_net_pnl")
    if bankrupt:
        pnl = sum(t.net_pnl for t in trips)
    return {
        "label": label,
        "pnl": pnl,
        "bankrupt": bankrupt,
        "sharpe": stats.get("sharpe_ratio"),
        "mdd_pct": stats.get("max_ddpercent"),
        "rt": rt.get("total", 0),
        "wr": rt.get("win_rate"),
        "pf": rt.get("profit_factor"),
        "opp08_n": len(t08),
        "opp08_pnl": sum(t.net_pnl for t in t08),
        "opp16_n": len(t16),
        "opp16_pnl": sum(t.net_pnl for t in t16),
        "other_n": len(other),
        "candidates": funnel.get("candidates", 0),
        "gate_pass": funnel.get("gate_pass", 0),
        "armed": funnel.get("armed", 0),
        "blocks": str(funnel.get("blocks", {})),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="pa_minimal M0/M1 ablation")
    parser.add_argument("--symbol", default="rb")
    parser.add_argument("--output-dir", default=str(ROOT / "research" / "output"))
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== pa_minimal ablation | {args.symbol} | 最多 3 次回测 ===\n")

    runs = [
        ("M0-BASE", None),
        ("M0-NULL", MINIMAL_NULL_OVERRIDES),
        ("M1-01-no-dual-core", {"dual_core_enabled": False}),
    ]

    rows = []
    for label, overrides in runs:
        print(f"\n----- {label} -----")
        bt = run_minimal_backtest(
            symbol=args.symbol,
            verbose=True,
            strategy_overrides=overrides,
        )
        row = _row(label, bt)
        rows.append(row)
        print(
            f"摘要: PnL={row['pnl']:+,.0f} RT={row['rt']} "
            f"OPP08={row['opp08_n']}/{row['opp08_pnl']:+.0f} "
            f"OPP16={row['opp16_n']}/{row['opp16_pnl']:+.0f} "
            f"other={row['other_n']} cand={row['candidates']}"
        )

    df = pd.DataFrame(rows)
    path = out_dir / f"exp_m0_minimal_{args.symbol.lower()}.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"\n===== 并列汇总 =====")
    print(df.to_string(index=False))
    print(f"\n输出: {path}")


if __name__ == "__main__":
    main()
