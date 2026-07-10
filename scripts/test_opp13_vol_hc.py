# -*- coding: utf-8 -*-
"""hc OPP13 量能筛选 A/B 对照（一次性验证）。"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from strategies.pa_cta.backtest import run_parquet_backtest


def _run(label: str, overrides: dict) -> dict:
    r = run_parquet_backtest(symbol="hc", verbose=False, strategy_overrides=overrides)
    stats = r["stats"]
    rt = r["round_trips"]
    opp13 = [t for t in rt if (t.setup or "").startswith("OPP13_")]
    return {
        "label": label,
        "pnl": float(stats.get("total_net_pnl", 0)),
        "sharpe": float(stats.get("sharpe_ratio", 0)),
        "rt": len(rt),
        "pf": float(r["rt_summary"].get("profit_factor", 0)),
        "wr": float(r["rt_summary"].get("win_rate", 0)),
        "opp13_n": len(opp13),
        "opp13_net": sum(t.net_pnl for t in opp13),
    }


def main() -> None:
    cases = [
        ("baseline", {}),
        ("opp13_vol_on", {"opp13_vol_filter_enabled": True}),
        (
            "opp13_vol_strict",
            {
                "opp13_vol_filter_enabled": True,
                "opp13_min_volume_pct": 55.0,
                "opp13_climax_volume_pct": 70.0,
            },
        ),
    ]
    rows = [_run(lbl, ov) for lbl, ov in cases]
    print("| 版本 | 总PnL | Sharpe | RT | PF | WR | OPP13笔 | OPP13 PnL |")
    print("|------|-------|--------|-----|-----|-----|---------|-----------|")
    base = rows[0]["pnl"]
    for x in rows:
        d = x["pnl"] - base
        print(
            f"| {x['label']} | {x['pnl']:+,.0f} | {x['sharpe']:.2f} | {x['rt']} | "
            f"{x['pf']:.2f} | {x['wr']:.1f}% | {x['opp13_n']} | {x['opp13_net']:+,.0f} | "
            f"Δ{x['pnl'] - base:+,.0f}"
        )


if __name__ == "__main__":
    main()
