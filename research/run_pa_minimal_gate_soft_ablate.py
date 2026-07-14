# -*- coding: utf-8 -*-
"""OPP16 soft 乘数单变量消融（rb，VSA 固定混窗）。

对照基线 LEGACY（hard DC）见 EXP-GATE-SOFT-BT：−58,992 / 43 RT。

用法::
  python -m research.run_pa_minimal_gate_soft_ablate --symbol rb
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

# VSA 固定混窗，只消融 Dual Core soft / OPP16 参数
_SOFT_BASE = {
    "dual_core_soft_enabled": True,
    "vsa_session_relative_enabled": False,
}

VARIANTS: list[tuple[str, dict]] = [
    (
        "V0_SOFT_ORIG",
        _SOFT_BASE.copy(),
    ),
    (
        "V1_OPP16_OFF",
        {
            **_SOFT_BASE,
            "dual_core_opp16_soft_enabled": False,
        },
    ),
    (
        "V2_OPP16_LITE",
        {
            **_SOFT_BASE,
            "dual_core_opp16_wrong_side_size_mult": 0.65,
            "dual_core_opp16_wrong_side_target_mult": 0.75,
            "dual_core_opp16_shallow_size_mult": 0.85,
            "dual_core_opp16_shallow_target_mult": 0.90,
            "dual_core_opp16_favor_size_floor": 0.92,
            "dual_core_opp16_favor_target_floor": 0.95,
            "dual_core_opp16_favor_skip_extra": True,
            "dual_core_opp16_soft_min_size_mult": 0.75,
            "dual_core_opp16_soft_min_target_mult": 0.65,
        },
    ),
]

LEGACY_NET = -58_992.0
LEGACY_RT = 43


def _row(label: str, bt: dict) -> dict:
    stats = bt["stats"]
    trips = bt["round_trips"]
    funnel = bt.get("candidate_funnel") or {}
    diag = bt.get("funnel_diag") or {}
    blocks = funnel.get("blocks") or {}
    net = float(stats.get("total_net_pnl") or sum(t.net_pnl for t in trips))
    opp16 = [t for t in trips if (t.setup or "").startswith("OPP16_")]
    opp16_long = [t for t in opp16 if t.direction == "多"]
    return {
        "variant": label,
        "net": net,
        "delta_vs_legacy": net - LEGACY_NET,
        "sharpe": float(stats.get("sharpe_ratio") or 0),
        "mdd_pct": float(stats.get("max_ddpercent") or 0),
        "n_rt": len(trips),
        "gate_pass": funnel.get("gate_pass"),
        "dual_core_blocks": int(blocks.get("dual_core", 0) or 0),
        "vsa_blocks": int(blocks.get("vsa", 0) or 0),
        "soft_reduce": int(diag.get("dual_core_soft_reduce_count", 0) or 0),
        "opp16_n": len(opp16),
        "opp16_pnl": sum(t.net_pnl for t in opp16),
        "opp16_long_n": len(opp16_long),
        "opp16_long_pnl": sum(t.net_pnl for t in opp16_long),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="OPP16 soft ablation")
    parser.add_argument("--symbol", default="rb")
    parser.add_argument("--output-dir", default=str(ROOT / "research" / "output"))
    args = parser.parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(
        f"=== {args.symbol} OPP16 soft 消融 "
        f"(LEGACY 参照 {LEGACY_NET:+,.0f} / {LEGACY_RT} RT) ===\n"
    )

    rows: list[dict] = []
    for label, overrides in VARIANTS:
        print(f"--- {label} ---", flush=True)
        bt = run_minimal_backtest(
            symbol=args.symbol,
            verbose=False,
            strategy_overrides=overrides,
        )
        r = _row(label, bt)
        rows.append(r)
        print(
            f"  net={r['net']:+,.0f} Δlegacy={r['delta_vs_legacy']:+,.0f} "
            f"sharpe={r['sharpe']:.2f} n={r['n_rt']} "
            f"soft_reduce={r['soft_reduce']} "
            f"OPP16={r['opp16_pnl']:+,.0f} (n={r['opp16_n']}, "
            f"多={r['opp16_long_pnl']:+,.0f}/n={r['opp16_long_n']})",
            flush=True,
        )

    df = pd.DataFrame(rows)
    path = out_dir / f"exp_gate_soft_ablate_{args.symbol.lower()}.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")

    best = df.loc[df["net"].idxmax()]
    print("\n===== 汇总 =====")
    print(
        f"{'变体':<14} {'净盈亏':>10} {'ΔLEGACY':>10} {'RT':>4} "
        f"{'soft减':>6} {'OPP16':>10} {'OPP16多':>10}"
    )
    for _, r in df.iterrows():
        print(
            f"{r['variant']:<14} {r['net']:>+10,.0f} {r['delta_vs_legacy']:>+10,.0f} "
            f"{int(r['n_rt']):>4} {int(r['soft_reduce']):>6} "
            f"{r['opp16_pnl']:>+10,.0f} {r['opp16_long_pnl']:>+10,.0f}"
        )
    print(
        f"\n最优（本批）: {best['variant']} net={best['net']:+,.0f} "
        f"(Δlegacy {best['delta_vs_legacy']:+,.0f})"
    )
    print(f"输出: {path}")


if __name__ == "__main__":
    main()
