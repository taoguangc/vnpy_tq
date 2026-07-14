# -*- coding: utf-8
"""EXP-009D — hc EOD_FLAT（14:55 日内强平）单变量消融。

用法::
  python -m research.run_eod_flat_ablation --symbol hc
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


@dataclass
class VariantResult:
    label: str
    stats: dict
    round_trips: list[RoundTripTrade]
    rt_summary: dict


def _exit_reason_table(trips: list[RoundTripTrade]) -> dict[str, dict]:
    by: dict[str, list[float]] = defaultdict(list)
    for rt in trips:
        by[rt.exit_reason or "UNKNOWN"].append(rt.net_pnl)
    out = {}
    for reason, pnls in sorted(by.items()):
        out[reason] = {"n": len(pnls), "net": sum(pnls)}
    return out


def _setup_net(trips: list[RoundTripTrade], prefix: str = "") -> dict[str, float]:
    acc: dict[str, float] = defaultdict(float)
    for rt in trips:
        setup = rt.setup or "UNKNOWN"
        if prefix and not setup.startswith(prefix):
            continue
        acc[setup] += rt.net_pnl
    return dict(acc)


def _run_variant(symbol: str, *, eod_flat_enabled: bool) -> VariantResult:
    label = "基线（EOD 强平 开）" if eod_flat_enabled else "消融（EOD 强平 关）"
    bt = run_parquet_backtest(
        symbol=symbol,
        verbose=False,
        strategy_overrides={"eod_flat_enabled": eod_flat_enabled},
    )
    return VariantResult(
        label=label,
        stats=bt["stats"],
        round_trips=bt["round_trips"],
        rt_summary=bt["rt_summary"],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="EXP-009D EOD_FLAT 消融")
    parser.add_argument("--symbol", default="hc")
    args = parser.parse_args()

    print(f"=== EXP-009D EOD_FLAT 消融 | {args.symbol} ===")
    print("窗口: 2023-05-17 ~ 2026-05-16 | 含成本 | 单变量: eod_flat_enabled\n")

    baseline = _run_variant(args.symbol, eod_flat_enabled=True)
    ablated = _run_variant(args.symbol, eod_flat_enabled=False)

    rows = [baseline, ablated]
    print("| 版本 | 总净盈亏 | Sharpe | 笔数 | WR | PF | maxDD% |")
    print("|------|----------|--------|------|-----|-----|--------|")
    for v in rows:
        s = v.stats
        rs = v.rt_summary
        print(
            f"| {v.label} | {s.get('total_net_pnl', 0):+,.0f} | "
            f"{s.get('sharpe_ratio', 0):.2f} | {int(rs.get('total', 0))} | "
            f"{rs.get('win_rate', 0):.1f}% | {rs.get('profit_factor', 0):.2f} | "
            f"{s.get('max_ddpercent', 0):.2f}% |"
        )

    d_pnl = ablated.stats.get("total_net_pnl", 0) - baseline.stats.get("total_net_pnl", 0)
    print(f"\nΔNet（关 − 开）: {d_pnl:+,.0f}")

    print("\n--- exit_reason 对照（基线 vs 消融）---")
    base_ex = _exit_reason_table(baseline.round_trips)
    abl_ex = _exit_reason_table(ablated.round_trips)
    reasons = sorted(set(base_ex) | set(abl_ex))
    print("| exit_reason | 基线 n/net | 消融 n/net |")
    print("|-------------|------------|------------|")
    for r in reasons:
        b = base_ex.get(r, {"n": 0, "net": 0.0})
        a = abl_ex.get(r, {"n": 0, "net": 0.0})
        print(f"| {r} | {b['n']} / {b['net']:+,.0f} | {a['n']} / {a['net']:+,.0f} |")

    print("\n--- 主要 setup 净盈亏 Δ（关 − 开）---")
    base_setups = _setup_net(baseline.round_trips)
    abl_setups = _setup_net(ablated.round_trips)
    deltas = []
    for k in sorted(set(base_setups) | set(abl_setups)):
        d = abl_setups.get(k, 0.0) - base_setups.get(k, 0.0)
        deltas.append((k, base_setups.get(k, 0.0), abl_setups.get(k, 0.0), d))
    deltas.sort(key=lambda x: abs(x[3]), reverse=True)
    for k, b, a, d in deltas[:10]:
        print(f"  {k:<42s} 基线 {b:+,.0f}  消融 {a:+,.0f}  Δ {d:+,.0f}")

    b_hold = baseline.rt_summary.get("avg_holding_hours", 0.0)
    a_hold = ablated.rt_summary.get("avg_holding_hours", 0.0)
    print(f"\n平均持有: 基线 {b_hold:.1f}h | 消融 {a_hold:.1f}h")

    if d_pnl > 5000:
        verdict = "关 EOD 强平 **显著改善** hc"
    elif d_pnl > 0:
        verdict = "关 EOD 强平 **略改善** hc（样本内需权衡 DD）"
    elif d_pnl < -5000:
        verdict = "关 EOD 强平 **显著劣化** hc — 保留 EOD"
    elif d_pnl < 0:
        verdict = "关 EOD 强平 **略劣化** hc — 保留 EOD"
    else:
        verdict = "无明显差异"
    print(f"\n结论: {verdict}")


if __name__ == "__main__":
    main()
