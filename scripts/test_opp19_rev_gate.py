# -*- coding: utf-8 -*-
"""OPP19 OD_REV 门禁 A/B（rb + hc）。"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from strategies.pa_cta.backtest import run_parquet_backtest

GATE = {"opp19_rev_gate_enabled": True}


def _opp19_stats(round_trips):
    opp19 = [t for t in round_trips if (t.setup or "").startswith("OPP19_")]
    by_setup: dict[str, list] = {}
    for t in opp19:
        by_setup.setdefault(t.setup or "?", []).append(t)
    return opp19, by_setup


def run_symbol(symbol: str, label: str, overrides: dict) -> None:
    r = run_parquet_backtest(symbol=symbol, verbose=False, strategy_overrides=overrides)
    stats = r["stats"]
    opp19, by_setup = _opp19_stats(r["round_trips"])
    net19 = sum(t.net_pnl for t in opp19)
    print(
        f"{symbol} {label}: PnL {stats.get('total_net_pnl', 0):+,.0f} | "
        f"Sharpe {stats.get('sharpe_ratio', 0):.2f} | RT {len(r['round_trips'])} | "
        f"OPP19 {len(opp19)}笔 {net19:+,.0f}"
    )
    for setup, items in sorted(by_setup.items()):
        n = len(items)
        net = sum(t.net_pnl for t in items)
        wr = sum(1 for t in items if t.net_pnl > 0) / n * 100 if n else 0
        print(f"  {setup}: {n}笔 {net:+,.0f} WR{wr:.0f}%")


def main() -> None:
    cases = [
        ("rb", "pending+time窗", {}),
        ("hc", "pending+time窗", {}),
        ("hc", "禁用OPP19", {"disabled_setups": "OPP19_"}),
    ]
    for sym, label, ov in cases:
        print(f"\n=== {sym} {label} ===")
        run_symbol(sym, label, ov)


if __name__ == "__main__":
    main()
