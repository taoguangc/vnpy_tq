# -*- coding: utf-8 -*-
"""EXP-M0-ARM — pa_minimal 固定候选武装对照（离线重放）。

1 次 M0-BASE 回测导出过门候选 → 在同一 cohort 上重放 A/B/C 武装。

用法::
  python -m research.run_pa_minimal_arm_lab --symbol rb
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.arm_lab import run_arm_lab
from scripts.tq_rollover_data import load_stitched_raw_bars
from strategies.pa_minimal.backtest import run_minimal_backtest
from strategies.pa_minimal.symbol_config import resolve_minimal_profile


def main() -> None:
    parser = argparse.ArgumentParser(description="pa_minimal arm lab")
    parser.add_argument("--symbol", default="rb")
    parser.add_argument("--retest-window", type=int, default=30)
    parser.add_argument("--output-dir", default=str(ROOT / "research" / "output"))
    args = parser.parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=== pa_minimal 武装 Lab（固定 signal cohort）===")
    print(f"品种: {args.symbol}")
    print("A=CURRENT  B=NEXT_CLOSE  C=RETEST/RECLAIM")
    print(f"回踩窗口: {args.retest_window} 分钟 | 出场冻结: 止损 / 1R / 120m\n")

    print("----- 导出 M0-BASE 候选 -----")
    bt = run_minimal_backtest(symbol=args.symbol, verbose=False)
    records = bt.get("candidate_records") or []
    funnel = bt.get("candidate_funnel") or {}
    gate_pass = [r for r in records if r.get("gate_pass")]
    print(
        f"candidates={funnel.get('candidates')} "
        f"gate_pass={len(gate_pass)} armed={funnel.get('armed')}"
    )
    if not gate_pass:
        print("无过门候选，退出")
        return

    cand_path = out_dir / f"exp_m0_arm_cohort_{args.symbol.lower()}.csv"
    pd.DataFrame(gate_pass).to_csv(cand_path, index=False, encoding="utf-8-sig")
    print(f"cohort: {cand_path}")

    profile = resolve_minimal_profile(args.symbol, ROOT)
    bars = load_stitched_raw_bars(
        profile["file_stem"],
        profile["exchange"],
        symbol=args.symbol,
        start=datetime(2023, 5, 17),
        end=datetime(2026, 5, 16),
    )
    print(f"1m bars: {len(bars):,}")

    print("\n----- 离线重放 A/B/C -----")
    sims, summary = run_arm_lab(
        gate_pass,
        bars,
        tick=float(profile["pricetick"]),
        contract_size=float(profile["size"]),
        retest_window=args.retest_window,
    )
    detail_path = out_dir / f"exp_m0_arm_detail_{args.symbol.lower()}.csv"
    sum_path = out_dir / f"exp_m0_arm_summary_{args.symbol.lower()}.csv"
    pd.DataFrame([s.__dict__ for s in sims]).to_csv(
        detail_path, index=False, encoding="utf-8-sig"
    )
    summary.to_csv(sum_path, index=False, encoding="utf-8-sig")

    print("\n===== 并列汇总（1 手毛额，止损/1R/120m）=====")
    cols = [
        "rule",
        "group",
        "n_candidates",
        "n_filled",
        "fill_rate",
        "avg_slip_ticks",
        "hit_1r_rate",
        "hit_2r_rate",
        "avg_mfe_r",
        "avg_mae_r",
        "avg_r",
        "sum_pnl_1lot",
        "pf",
        "miss",
    ]
    show = summary[cols].copy()
    for c in ("fill_rate", "hit_1r_rate", "hit_2r_rate"):
        show[c] = show[c].map(lambda x: f"{x:.1%}" if x == x else "n/a")
    for c in ("avg_slip_ticks", "avg_mfe_r", "avg_mae_r", "avg_r", "pf"):
        show[c] = show[c].map(lambda x: f"{x:.2f}" if x == x else "n/a")
    show["sum_pnl_1lot"] = show["sum_pnl_1lot"].map(lambda x: f"{x:+.0f}")
    print(show.to_string(index=False))
    print(f"\n明细: {detail_path}")
    print(f"汇总: {sum_path}")


if __name__ == "__main__":
    main()
