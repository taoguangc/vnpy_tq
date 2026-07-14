# -*- coding: utf-8 -*-
"""pa_minimal 第二阶段：跨品种诊断（CROSS_SYMBOL_UNIVERSE）。"""
from __future__ import annotations

from typing import Any

import pandas as pd

from research.pa_minimal_baseline import OOS_PROMOTE_N, COST_RATE
from strategies.pa_cta.symbol_config import cross_symbol_list
from strategies.pa_minimal.backtest import run_minimal_backtest
from strategies.pa_minimal.symbol_config import resolve_minimal_profile


def diagnose_symbol(symbol: str, root) -> dict[str, Any]:
    """阶段 A：只读候选诊断（1 次回测）。"""
    profile = resolve_minimal_profile(symbol, root)
    bt = run_minimal_backtest(symbol=symbol, verbose=False)
    records = bt.get("candidate_records") or []
    funnel = bt.get("candidate_funnel") or {}
    trips = bt["round_trips"]
    stats = bt["stats"]
    gate = [r for r in records if r.get("gate_pass")]
    by_setup: dict[str, int] = {}
    for r in gate:
        by_setup[r["setup"]] = by_setup.get(r["setup"], 0) + 1
    gross = sum(t.gross_pnl for t in trips)
    net = sum(t.net_pnl for t in trips)
    cost = gross - net
    n = len(trips)
    avg_1r_proxy = 0.0
    if trips:
        # 用平均 |毛利|/手数 粗估；成本覆盖用中位 1 手成本
        vols = [t.volume for t in trips]
        cost_1lot = [((t.gross_pnl - t.net_pnl) / t.volume) for t in trips if t.volume]
        med_cost = float(pd.Series(cost_1lot).median()) if cost_1lot else 0.0
        avg_1r_proxy = med_cost
    else:
        med_cost = 0.0
    eligible = n >= OOS_PROMOTE_N and net > -abs(cost) * 0.5  # 粗滤：不全是成本吞噬
    return {
        "symbol": symbol.lower(),
        "candidates": funnel.get("candidates", len(records)),
        "gate_pass": len(gate),
        "armed": funnel.get("armed", 0),
        "by_setup": by_setup,
        "n_rt": n,
        "gross": gross,
        "net": net,
        "cost": cost,
        "sharpe": float(stats.get("sharpe_ratio") or 0.0),
        "median_cost_1lot": med_cost,
        "slippage": float(profile["slippage"]),
        "size": float(profile["size"]),
        "phase_b_eligible": bool(n >= 15 and net / max(n, 1) > -5000),  # 候选期望不明显为负
        "rate": COST_RATE,
    }


def run_cross_symbol_phase_a(symbols: list[str] | None = None, root=None) -> pd.DataFrame:
    symbols = symbols or cross_symbol_list()
    rows = []
    for sym in symbols:
        d = diagnose_symbol(sym, root)
        by = d.pop("by_setup")
        d["opp08_gate"] = sum(v for k, v in by.items() if k.startswith("OPP08"))
        d["opp16_gate"] = sum(v for k, v in by.items() if k.startswith("OPP16"))
        rows.append(d)
    return pd.DataFrame(rows)
