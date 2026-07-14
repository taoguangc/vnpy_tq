# -*- coding: utf-8
"""EXP-009C — hc PROFIT_PROTECT_1440 单变量消融（14:40 前低/前高抬止损）。

用法::
  python -m research.run_profit_protect_ablation --symbol hc
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


def _run_variant(symbol: str, *, profit_protect_enabled: bool) -> VariantResult:
    label = "基线（PROFIT_PROTECT 开）" if profit_protect_enabled else "消融（PROFIT_PROTECT 关）"
    bt = run_parquet_backtest(
        symbol=symbol,
        verbose=False,
        strategy_overrides={"profit_protect_enabled": profit_protect_enabled},
    )
    return VariantResult(
        label=label,
        stats=bt["stats"],
        round_trips=bt["round_trips"],
        rt_summary=bt["rt_summary"],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="EXP-009C PROFIT_PROTECT 消融")
    parser.add_argument("--symbol", default="hc")
    args = parser.parse_args()

    print(f"=== EXP-009C PROFIT_PROTECT 消融 | {args.symbol} ===")
    print("窗口: 2023-05-17 ~ 2026-05-16 | 含成本 | 单变量: profit_protect_enabled\n")

    baseline = _run_variant(args.symbol, profit_protect_enabled=True)
    ablated = _run_variant(args.symbol, profit_protect_enabled=False)

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

    print("\n--- OPP19 族 setup 净盈亏 ---")
    for prefix in ("OPP19_",):
        print(f"\n[{prefix}*]")
        base_setups = _setup_net(baseline.round_trips, prefix)
        abl_setups = _setup_net(ablated.round_trips, prefix)
        keys = sorted(set(base_setups) | set(abl_setups))
        for k in keys:
            b = base_setups.get(k, 0.0)
            a = abl_setups.get(k, 0.0)
            print(f"  {k:<42s} 基线 {b:+,.0f}  消融 {a:+,.0f}  Δ {a - b:+,.0f}")

    opp19_short_base = [t for t in baseline.round_trips if (t.setup or "").startswith("OPP19_") and t.direction == "空"]
    opp19_short_abl = [t for t in ablated.round_trips if (t.setup or "").startswith("OPP19_") and t.direction == "空"]
    if opp19_short_base or opp19_short_abl:
        sb = summarize_round_trips(opp19_short_base)
        sa = summarize_round_trips(opp19_short_abl)
        print("\n--- OPP19 SHORT 汇总 ---")
        print(
            f"基线: n={int(sb['total'])} net={sum(t.net_pnl for t in opp19_short_base):+,.0f} "
            f"PF={sb['profit_factor']:.2f}"
        )
        print(
            f"消融: n={int(sa['total'])} net={sum(t.net_pnl for t in opp19_short_abl):+,.0f} "
            f"PF={sa['profit_factor']:.2f}"
        )

    if d_pnl > 0:
        verdict = "关 PROFIT_PROTECT **改善** hc（与 TM Lab STOP_EOD 方向一致）"
    elif d_pnl < 0:
        verdict = "关 PROFIT_PROTECT **劣化** hc — 保留 production 栈"
    else:
        verdict = "无明显差异"
    print(f"\n结论: {verdict}")


if __name__ == "__main__":
    main()
