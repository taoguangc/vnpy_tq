# -*- coding: utf-8 -*-
"""Dual Core / VSA 旧硬门禁 vs 新软调节+同时段量 对照（pa_minimal）。

LEGACY: dual_core_soft_enabled=False + vsa_session_relative_enabled=False
NEW:    默认（soft Dual Core + 同时段 VSA）

用法::
  python -m research.run_pa_minimal_gate_soft --symbol rb
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from strategies.pa_minimal.backtest import run_minimal_backtest

LEGACY_OVERRIDES = {
    "dual_core_soft_enabled": False,
    "vsa_session_relative_enabled": False,
}
NEW_OVERRIDES = {
    "dual_core_soft_enabled": True,
    "vsa_session_relative_enabled": True,
}


def _summarize(label: str, bt: dict) -> dict:
    stats = bt["stats"]
    trips = bt["round_trips"]
    funnel = bt.get("candidate_funnel") or {}
    diag = bt.get("funnel_diag") or {}
    blocks = funnel.get("blocks") or {}
    net = float(stats.get("total_net_pnl") or sum(t.net_pnl for t in trips))
    sharpe = float(stats.get("sharpe_ratio") or 0)
    mdd = float(stats.get("max_ddpercent") or 0)
    wr = float(stats.get("win_rate") or 0)
    opp08 = [t for t in trips if (t.setup or "").startswith("OPP08_")]
    opp16 = [t for t in trips if (t.setup or "").startswith("OPP16_")]
    row = {
        "version": label,
        "net": net,
        "sharpe": sharpe,
        "mdd_pct": mdd,
        "wr": wr,
        "n_rt": len(trips),
        "candidates": funnel.get("candidates"),
        "gate_pass": funnel.get("gate_pass"),
        "armed": funnel.get("armed"),
        "dual_core_blocks": int(blocks.get("dual_core", 0) or 0),
        "vsa_blocks": int(blocks.get("vsa", 0) or 0),
        "dual_core_hard": int(diag.get("dual_core_block_count", 0) or 0),
        "vsa_hard": int(diag.get("vsa_block_count", 0) or 0),
        "dual_core_soft_reduce": int(
            diag.get("dual_core_soft_reduce_count", 0) or 0
        ),
        "opp08_n": len(opp08),
        "opp08_pnl": sum(t.net_pnl for t in opp08),
        "opp16_n": len(opp16),
        "opp16_pnl": sum(t.net_pnl for t in opp16),
    }
    print(f"===== {label} =====")
    print(
        f"net={row['net']:+,.0f} sharpe={row['sharpe']:.2f} "
        f"mdd={row['mdd_pct']:.1f}% n={row['n_rt']} wr={row['wr']:.1f}%"
    )
    print(
        f"cand={row['candidates']} pass={row['gate_pass']} armed={row['armed']} "
        f"blocks dual_core={row['dual_core_blocks']} vsa={row['vsa_blocks']}"
    )
    print(
        f"engine: dc_hard={row['dual_core_hard']} vsa={row['vsa_hard']} "
        f"dc_soft_reduce={row['dual_core_soft_reduce']}"
    )
    for k in sorted({(t.setup or "")[:32] for t in trips}):
        sub = [t for t in trips if (t.setup or "").startswith(k)]
        p = sum(t.net_pnl for t in sub)
        print(f"  {k}: n={len(sub)} pnl={p:+,.0f}")
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description="pa_minimal gate soft vs legacy")
    parser.add_argument("--symbol", default="rb")
    parser.add_argument("--output-dir", default=str(ROOT / "research" / "output"))
    args = parser.parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== pa_minimal {args.symbol} | LEGACY vs NEW (Dual Core + VSA) ===\n")

    bt_legacy = run_minimal_backtest(
        symbol=args.symbol,
        verbose=False,
        strategy_overrides=LEGACY_OVERRIDES,
    )
    r0 = _summarize("LEGACY (hard DC + 混窗 VSA)", bt_legacy)

    bt_new = run_minimal_backtest(
        symbol=args.symbol,
        verbose=False,
        strategy_overrides=NEW_OVERRIDES,
    )
    r1 = _summarize("NEW (soft DC + 同时段 VSA)", bt_new)

    delta_net = r1["net"] - r0["net"]
    delta_n = r1["n_rt"] - r0["n_rt"]
    print("\n===== DELTA NEW - LEGACY =====")
    print(f"delta_net={delta_net:+,.0f} delta_n={delta_n}")
    print(
        f"Δdual_core_blocks={r1['dual_core_blocks'] - r0['dual_core_blocks']} "
        f"Δvsa_blocks={r1['vsa_blocks'] - r0['vsa_blocks']}"
    )

    df = pd.DataFrame([r0, r1])
    path = out_dir / f"exp_gate_soft_{args.symbol.lower()}.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"\n输出: {path}")


if __name__ == "__main__":
    main()
