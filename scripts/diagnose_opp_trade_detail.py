# -*- coding: utf-8 -*-
"""hc/rb OPP 逐笔细分解：汇总、exit_reason 透视、品种对照。"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.backtest_trade_analysis import RoundTripTrade, summarize_round_trips
from strategies.pa_cta.backtest import run_parquet_backtest
from strategies.pa_cta.symbol_config import resolve_symbol_profile


@dataclass
class SymbolResult:
    symbol: str
    profile: dict
    stats: dict
    round_trips: list[RoundTripTrade]
    rt_summary: dict


def _capture_pct(net_pnl: float, mfe_ticks: float) -> str:
    if mfe_ticks and mfe_ticks > 0:
        return f"{net_pnl / mfe_ticks * 100:.0f}%"
    return "—"


def _fmt_dt(dt) -> str:
    if dt is None:
        return "—"
    return dt.strftime("%Y-%m-%d %H:%M")


def _setup_stats(round_trips: list[RoundTripTrade]) -> dict[str, dict]:
    by_setup: dict[str, list[RoundTripTrade]] = defaultdict(list)
    for rt in round_trips:
        key = rt.setup or "(unknown)"
        by_setup[key].append(rt)
    out: dict[str, dict] = {}
    total_net = sum(t.net_pnl for t in round_trips)
    for setup, items in by_setup.items():
        wins = sum(1 for t in items if t.net_pnl > 0)
        net = sum(t.net_pnl for t in items)
        out[setup] = {
            "n": len(items),
            "wins": wins,
            "wr": wins / len(items) * 100.0 if items else 0.0,
            "net_pnl": net,
            "pct_total": net / total_net * 100.0 if total_net else 0.0,
            "avg_holding": sum(t.holding_minutes for t in items) / len(items),
            "items": items,
        }
    return out


def _print_config(profile: dict, symbol: str) -> None:
    print(f"\n--- {symbol} 配置摘要 ---")
    tier = profile.get("symbol_liquidity_tier", "—")
    vol = profile.get("symbol_vol_baseline_1m", "—")
    risk_mult = profile.get("symbol_liquidity_risk_mult", 1.0)
    print(f"  symbol_liquidity_tier: {tier}")
    print(f"  symbol_vol_baseline_1m: {vol}")
    print(f"  symbol_liquidity_risk_mult: {risk_mult}")
    print(
        "  Setup AFF: "
        f"opp02={profile.get('opp02_aff_gate_enabled', False)} | "
        f"opp19_breakout={profile.get('opp19_breakout_aff_gate_enabled', False)}"
    )
    print(
        "  Router: "
        f"enabled={profile.get('aff_archetype_router_enabled', False)} | "
        f"adaptive={profile.get('aff_archetype_adaptive_enabled', False)} | "
        f"minimal={profile.get('aff_archetype_minimal_enabled', False)}"
    )
    print(f"  symbol_adaptive_enabled: {profile.get('symbol_adaptive_enabled', False)}")


def _print_symbol_overview(results: list[SymbolResult]) -> None:
    print("\n" + "=" * 72)
    print("A. 品种总览")
    print("=" * 72)
    headers = ["指标"] + [r.symbol for r in results]
    col_w = 14
    print(f"{headers[0]:<22}" + "".join(f"{h:>{col_w}}" for h in headers[1:]))
    print("-" * (22 + col_w * len(results)))

    def row(label: str, values: list[str]) -> None:
        print(f"{label:<22}" + "".join(f"{v:>{col_w}}" for v in values))

    row(
        "总PnL",
        [f"{r.stats.get('total_net_pnl', 0):+,.0f}" for r in results],
    )
    row(
        "Round-trip",
        [f"{int(r.rt_summary.get('total', 0))}" for r in results],
    )
    row(
        "PF",
        [f"{r.rt_summary.get('profit_factor', 0):.2f}" for r in results],
    )
    row(
        "Sharpe",
        [f"{r.stats.get('sharpe_ratio', 0):.2f}" for r in results],
    )
    row(
        "胜率",
        [f"{r.rt_summary.get('win_rate', 0):.1f}%" for r in results],
    )

    for r in results:
        by = _setup_stats(r.round_trips)
        r._profit_setups = sum(1 for s in by.values() if s["net_pnl"] > 0)
        r._loss_setups = sum(1 for s in by.values() if s["net_pnl"] < 0)

    row(
        "盈利 OPP 数",
        [f"{getattr(r, '_profit_setups', 0)}" for r in results],
    )
    row(
        "亏损 OPP 数",
        [f"{getattr(r, '_loss_setups', 0)}" for r in results],
    )


def _print_opp_summary(result: SymbolResult) -> None:
    by = _setup_stats(result.round_trips)
    total_net = sum(t.net_pnl for t in result.round_trips)
    print(f"\n--- {result.symbol} OPP 汇总 (总PnL {total_net:+,.0f}) ---")
    print(
        f"{'setup':<42} {'n':>3} {'WR':>6} {'net_pnl':>10} {'占总额':>7} {'均持仓min':>9}"
    )
    print("-" * 82)
    for setup, s in sorted(by.items(), key=lambda x: x[1]["net_pnl"], reverse=True):
        print(
            f"{setup:<42} {s['n']:>3} {s['wr']:>5.1f}% "
            f"{s['net_pnl']:>+10.0f} {s['pct_total']:>6.1f}% {s['avg_holding']:>9.0f}"
        )


def _print_trade_detail(
    results: list[SymbolResult],
    *,
    prefix: str | None,
    show_all: bool,
) -> None:
    print("\n" + "=" * 72)
    title = "B. OPP 逐笔明细" if show_all else f"B. {prefix or 'OPP'} 逐笔明细"
    print(title)
    print("=" * 72)
    print(
        f"{'#':>3} {'品种':<4} {'setup':<38} {'向':>2} "
        f"{'入场':<16} {'出场':<16} {'net':>8} {'exit_reason':<22} "
        f"{'MFE':>7} {'MAE':>7} {'cap':>5} {'context':<14} {'AI':<6} {'min':>5}"
    )
    print("-" * 160)
    idx = 0
    for result in results:
        trips = result.round_trips
        if prefix and not show_all:
            trips = [t for t in trips if (t.setup or "").startswith(prefix)]
        trips = sorted(trips, key=lambda t: (t.setup, t.entry_time))
        for rt in trips:
            idx += 1
            print(
                f"{idx:>3} {result.symbol:<4} {(rt.setup or '?'):<38} {rt.direction:>2} "
                f"{_fmt_dt(rt.entry_time):<16} {_fmt_dt(rt.exit_time):<16} "
                f"{rt.net_pnl:>+8.0f} {(rt.exit_reason or '?'):<22} "
                f"{rt.mfe_ticks:>7.0f} {rt.mae_ticks:>7.0f} "
                f"{_capture_pct(rt.net_pnl, rt.mfe_ticks):>5} "
                f"{(rt.market_context or '?'):<14} {(rt.always_in or '?'):<6} "
                f"{rt.holding_minutes:>5.0f}"
            )
    if idx == 0:
        print("(无匹配交易)")


def _print_exit_reason_pivot(results: list[SymbolResult], prefix: str | None) -> None:
    print("\n" + "=" * 72)
    print("出场原因透视 (setup × exit_reason)")
    print("=" * 72)
    for result in results:
        trips = result.round_trips
        if prefix:
            trips = [t for t in trips if (t.setup or "").startswith(prefix)]
        pivot: dict[tuple[str, str], list[RoundTripTrade]] = defaultdict(list)
        for rt in trips:
            pivot[(rt.setup or "?", rt.exit_reason or "?")].append(rt)
        print(f"\n--- {result.symbol} ---")
        print(f"{'setup':<38} {'exit_reason':<22} {'n':>3} {'net_pnl':>10}")
        print("-" * 78)
        for (setup, reason), items in sorted(
            pivot.items(),
            key=lambda x: sum(t.net_pnl for t in x[1]),
            reverse=True,
        ):
            net = sum(t.net_pnl for t in items)
            print(f"{setup:<38} {reason:<22} {len(items):>3} {net:>+10.0f}")


def _print_compare(results: list[SymbolResult]) -> None:
    if len(results) < 2:
        return
    print("\n" + "=" * 72)
    print("C. hc vs rb 对照 (同 setup)")
    print("=" * 72)
    by_sym: dict[str, dict[str, dict]] = {}
    for r in results:
        by_sym[r.symbol] = _setup_stats(r.round_trips)

    all_setups = set()
    for stats in by_sym.values():
        all_setups.update(stats.keys())

    print(
        f"{'setup':<42} "
        + "".join(f"{sym+' n':>8}{sym+' net':>10}{sym+' WR':>8}" for sym in by_sym)
    )
    print("-" * (42 + 26 * len(by_sym)))

    only_one: list[tuple[str, str]] = []
    for setup in sorted(all_setups, key=lambda s: max(
        by_sym[sym].get(s, {"net_pnl": 0})["net_pnl"] for sym in by_sym
    ), reverse=True):
        present = [sym for sym in by_sym if setup in by_sym[sym]]
        if len(present) == 1:
            only_one.append((setup, present[0]))
        cols = []
        for sym in by_sym:
            if setup in by_sym[sym]:
                s = by_sym[sym][setup]
                cols.extend([f"{s['n']:>8}", f"{s['net_pnl']:>+10.0f}", f"{s['wr']:>7.1f}%"])
            else:
                cols.extend(["—".rjust(8), "—".rjust(10), "—".rjust(8)])
        print(f"{setup:<42}" + "".join(cols))

    if only_one:
        print("\n仅单品种出现的 setup:")
        for setup, sym in only_one:
            s = by_sym[sym][setup]
            print(f"  [{sym}] {setup}: {s['n']} 笔, net {s['net_pnl']:+.0f}")

    # OPP08 LONG/SHORT 分项
    print("\n--- OPP08 子 setup 分项 ---")
    for prefix in ("OPP08_5M_STRONG_BREAKOUT_LONG", "OPP08_5M_STRONG_BREAKOUT_SHORT"):
        cols = []
        for sym in by_sym:
            sub = {k: v for k, v in by_sym[sym].items() if k.startswith(prefix)}
            if sub:
                n = sum(v["n"] for v in sub.values())
                net = sum(v["net_pnl"] for v in sub.values())
                cols.append(f"{sym}: {n}笔/{net:+.0f}")
            else:
                cols.append(f"{sym}: 0笔")
        print(f"  {prefix}: {' | '.join(cols)}")


def _print_conclusion(results: list[SymbolResult]) -> None:
    if len(results) < 2:
        return
    by_sym = {r.symbol: _setup_stats(r.round_trips) for r in results}
    print("\n" + "=" * 72)
    print("D. 可验证结论（基于本轮回测）")
    print("=" * 72)

    def opp_net(sym: str, prefix: str) -> tuple[int, float]:
        stats = by_sym[sym]
        items = [(k, v) for k, v in stats.items() if k.startswith(prefix)]
        n = sum(v["n"] for _, v in items)
        net = sum(v["net_pnl"] for _, v in items)
        return n, net

    for sym in by_sym:
        n08, net08 = opp_net(sym, "OPP08_")
        print(f"  {sym} OPP08: {n08} 笔, net {net08:+.0f}")

    hc08 = opp_net("hc", "OPP08_") if "hc" in by_sym else (0, 0.0)
    rb08 = opp_net("rb", "OPP08_") if "rb" in by_sym else (0, 0.0)
    if hc08[0] > 0 and rb08[0] == 0:
        print("  hc 有 OPP08 成交而 rb 无（或笔数更少）——与 EXP-016 Router 误杀 hc OPP08 的假设一致（本 run 为 baseline）。")
    elif hc08[1] > 0 and rb08[1] <= 0:
        print("  hc OPP08 净贡献为正，rb 同 setup 未贡献或更少。")

    # 最大拖累 setup
    for sym in ("hc", "rb"):
        if sym not in by_sym:
            continue
        worst = min(by_sym[sym].items(), key=lambda x: x[1]["net_pnl"], default=None)
        best = max(by_sym[sym].items(), key=lambda x: x[1]["net_pnl"], default=None)
        if worst:
            print(
                f"  {sym} 最大拖累: {worst[0]} ({worst[1]['n']}笔, {worst[1]['net_pnl']:+.0f})"
            )
        if best:
            print(
                f"  {sym} 最大贡献: {best[0]} ({best[1]['n']}笔, {best[1]['net_pnl']:+.0f})"
            )


def run_backtests(symbols: list[str]) -> list[SymbolResult]:
    out: list[SymbolResult] = []
    for sym in symbols:
        profile = resolve_symbol_profile(sym, _ROOT)
        _print_config(profile, sym)
        bt = run_parquet_backtest(symbol=sym, verbose=False)
        out.append(
            SymbolResult(
                symbol=sym,
                profile=profile,
                stats=bt["stats"],
                round_trips=bt["round_trips"],
                rt_summary=bt["rt_summary"],
            )
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="hc/rb OPP 逐笔细分解与对照")
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=["hc", "rb"],
        help="品种列表，默认 hc rb",
    )
    parser.add_argument(
        "--prefix",
        default="OPP08_",
        help="逐笔/exit 透视过滤前缀，默认 OPP08_",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="输出全部 OPP 逐笔（忽略 prefix 过滤）",
    )
    args = parser.parse_args()

    symbols = [s.lower() for s in args.symbols]
    prefix = None if args.all else args.prefix

    print("=" * 72)
    print(f"OPP 逐笔诊断 | symbols={','.join(symbols)} | "
          f"{'全部 OPP' if args.all else f'prefix={prefix}'}")
    print("=" * 72)

    results = run_backtests(symbols)
    _print_symbol_overview(results)
    for r in results:
        _print_opp_summary(r)
    _print_trade_detail(results, prefix=prefix, show_all=args.all)
    _print_exit_reason_pivot(results, prefix if not args.all else None)
    _print_compare(results)
    _print_conclusion(results)


if __name__ == "__main__":
    main()
