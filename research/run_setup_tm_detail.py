# -*- coding: utf-8
"""EXP-009E — 多品种 setup 级 TM 细读（ACTUAL exit_reason × TM STOP_EOD/1R）。

用法::
  python -m research.run_setup_tm_detail --symbol hc
  python -m research.run_setup_tm_detail --all
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from strategies.pa_cta.backtest import run_parquet_backtest

DEFAULT_SYMBOLS = ("rb", "hc", "MA")
DELTA_THRESHOLD = 3000.0


def _group_by_setup(trips) -> dict[str, list]:
    by: dict[str, list] = defaultdict(list)
    for t in trips:
        by[t.setup or "UNKNOWN"].append(t)
    return by


def _load_tm_pivot(symbol: str) -> pd.DataFrame | None:
    sym_tag = symbol.lower()
    csv = ROOT / "research" / "output" / f"exp009_tm_lab_{sym_tag}_by_setup.csv"
    if not csv.is_file():
        return None
    df = pd.read_csv(csv)
    piv = df.pivot_table(index="setup", columns="rule", values="net_pnl", aggfunc="first")
    piv["d_STOP_EOD"] = piv["STOP_EOD"] - piv["ACTUAL"]
    piv["d_1R"] = piv["FIXED_1R"] - piv["ACTUAL"]
    return piv


def _print_actual_table(by: dict[str, list]) -> None:
    print("--- A. ACTUAL setup × exit_reason 笔数 ---")
    print(
        f"{'setup':<40} {'n':>3} {'WR':>5} {'net':>9} "
        f"{'PP':>3} {'EOD':>3} {'CHAN':>4} {'STOP':>4} {'BE':>3}"
    )
    for setup, items in sorted(by.items(), key=lambda x: sum(t.net_pnl for t in x[1])):
        n = len(items)
        wr = sum(1 for t in items if t.net_pnl > 0) / n * 100
        net = sum(t.net_pnl for t in items)
        er: dict[str, int] = defaultdict(int)
        for t in items:
            er[t.exit_reason or "?"] += 1
        print(
            f"{setup:<40} {n:>3} {wr:>4.0f}% {net:>+9.0f} "
            f"{er.get('PROFIT_PROTECT_1440', 0):>3} {er.get('EOD_FLAT', 0):>3} "
            f"{er.get('CHANDELIER_STOP', 0):>4} {er.get('STOP_LOSS', 0):>4} "
            f"{er.get('BREAKEVEN', 0):>3}"
        )


def _print_exit_net(by: dict[str, list]) -> None:
    print("\n--- B. ACTUAL setup × exit_reason 净盈亏 ---")
    for setup, items in sorted(by.items(), key=lambda x: sum(t.net_pnl for t in x[1])):
        er_net: dict[str, float] = defaultdict(float)
        er_n: dict[str, int] = defaultdict(int)
        for t in items:
            key = t.exit_reason or "?"
            er_net[key] += t.net_pnl
            er_n[key] += 1
        parts = [f"{k}:{er_n[k]}={er_net[k]:+.0f}" for k in sorted(er_net)]
        print(f"{setup}: " + " | ".join(parts))


def _print_tm_table(piv: pd.DataFrame) -> None:
    print("\n--- C. TM Lab：ACTUAL vs STOP_EOD / FIXED_1R（Δ = 机械 − ACTUAL）---")
    print(
        f"{'setup':<40} {'ACTUAL':>9} {'STOP_EOD':>9} {'d_SE':>9} "
        f"{'FIXED_1R':>9} {'d_1R':>9}"
    )
    for setup in piv.sort_values("d_STOP_EOD").index:
        r = piv.loc[setup]
        print(
            f"{setup:<40} {r['ACTUAL']:>+9.0f} {r['STOP_EOD']:>+9.0f} "
            f"{r['d_STOP_EOD']:>+9.0f} {r['FIXED_1R']:>+9.0f} {r['d_1R']:>+9.0f}"
        )


def _print_mgmt_class(piv: pd.DataFrame) -> None:
    print("\n--- D. 管理效应分类（相对 STOP_EOD）---")
    hurt = piv[piv["d_STOP_EOD"] > DELTA_THRESHOLD].sort_values("d_STOP_EOD", ascending=False)
    help_ = piv[piv["d_STOP_EOD"] < -DELTA_THRESHOLD].sort_values("d_STOP_EOD")
    flat = piv[(piv["d_STOP_EOD"].abs() <= DELTA_THRESHOLD)]
    print("生产栈相对 STOP_EOD 减损（STOP_EOD 更好）:")
    for setup, r in hurt.iterrows():
        print(
            f"  {setup}: ACTUAL {r['ACTUAL']:+.0f} → STOP_EOD {r['STOP_EOD']:+.0f} "
            f"(Δ{r['d_STOP_EOD']:+.0f})"
        )
    print("生产栈相对 STOP_EOD 增值（ACTUAL 更好）:")
    for setup, r in help_.iterrows():
        print(
            f"  {setup}: ACTUAL {r['ACTUAL']:+.0f} → STOP_EOD {r['STOP_EOD']:+.0f} "
            f"(Δ{r['d_STOP_EOD']:+.0f})"
        )
    print("近似中性 (|Δ|≤3k):")
    for setup, r in flat.iterrows():
        print(f"  {setup}: Δ{r['d_STOP_EOD']:+.0f}")


def _build_detail_rows(symbol: str, by: dict[str, list], piv: pd.DataFrame | None) -> list[dict]:
    rows = []
    for setup, items in by.items():
        net = sum(t.net_pnl for t in items)
        er_net = defaultdict(float)
        er_n = defaultdict(int)
        for t in items:
            er_net[t.exit_reason or "?"] += t.net_pnl
            er_n[t.exit_reason or "?"] += 1
        row = {
            "symbol": symbol.lower(),
            "setup": setup,
            "n": len(items),
            "actual_net": net,
            "wr": sum(1 for t in items if t.net_pnl > 0) / len(items) * 100,
        }
        for k in ("PROFIT_PROTECT_1440", "EOD_FLAT", "CHANDELIER_STOP", "STOP_LOSS", "BREAKEVEN"):
            row[f"{k}_n"] = er_n.get(k, 0)
            row[f"{k}_net"] = er_net.get(k, 0.0)
        if piv is not None and setup in piv.index:
            row["tm_stop_eod"] = float(piv.loc[setup, "STOP_EOD"])
            row["tm_d_stop_eod"] = float(piv.loc[setup, "d_STOP_EOD"])
            row["tm_fixed_1r"] = float(piv.loc[setup, "FIXED_1R"])
        rows.append(row)
    return rows


def analyze_symbol(symbol: str, *, verbose: bool = True) -> list[dict]:
    if verbose:
        print(f"\n{'=' * 72}")
        print(f"=== {symbol.lower()} setup 级 TM 细读 ===")
        print("窗口: 2023-05-17 ~ 2026-05-16 | 含成本")
        stats_line = ""
    bt = run_parquet_backtest(symbol=symbol, verbose=False)
    trips = bt["round_trips"]
    by = _group_by_setup(trips)
    piv = _load_tm_pivot(symbol)

    if verbose:
        s = bt["stats"]
        rs = bt["rt_summary"]
        print(
            f"总净盈亏: {s.get('total_net_pnl', 0):+,.0f} | "
            f"n={int(rs.get('total', 0))} | PF={rs.get('profit_factor', 0):.2f}"
        )
        if piv is None:
            print(f"WARN: 未找到 exp009_tm_lab_{symbol.lower()}_by_setup.csv，跳过 TM 对照")
        _print_actual_table(by)
        _print_exit_net(by)
        if piv is not None:
            _print_tm_table(piv)
            _print_mgmt_class(piv)

    sym_tag = symbol.lower()
    out = ROOT / "research" / "output" / f"exp009e_{sym_tag}_setup_tm_detail.csv"
    rows = _build_detail_rows(symbol, by, piv)
    pd.DataFrame(rows).sort_values("actual_net").to_csv(out, index=False, encoding="utf-8-sig")
    if verbose:
        print(f"\n输出: {out.name}")
    return rows


def _print_cross_summary(all_rows: list[dict]) -> None:
    df = pd.DataFrame(all_rows)
    if df.empty:
        return
    print(f"\n{'=' * 72}")
    print("=== 跨品种 setup 汇总（ACTUAL net Top/Bottom）===")
    for sym in sorted(df["symbol"].unique()):
        sub = df[df["symbol"] == sym].sort_values("actual_net")
        total = sub["actual_net"].sum()
        print(f"\n[{sym}] 合计 {total:+,.0f} | {len(sub)} setup")
        print("  拖累 Top3:")
        for _, r in sub.head(3).iterrows():
            d = r.get("tm_d_stop_eod", float("nan"))
            d_txt = f" TMΔ{d:+.0f}" if pd.notna(d) else ""
            print(f"    {r['setup']}: {r['actual_net']:+.0f} (n={int(r['n'])}){d_txt}")
        print("  盈利 Top3:")
        for _, r in sub.tail(3).iloc[::-1].iterrows():
            d = r.get("tm_d_stop_eod", float("nan"))
            d_txt = f" TMΔ{d:+.0f}" if pd.notna(d) else ""
            print(f"    {r['setup']}: {r['actual_net']:+.0f} (n={int(r['n'])}){d_txt}")


def main() -> None:
    parser = argparse.ArgumentParser(description="EXP-009E 多品种 setup TM 细读")
    parser.add_argument("--symbol", default=None, help="单品种 rb / hc / MA")
    parser.add_argument("--all", action="store_true", help="rb + hc + MA")
    args = parser.parse_args()

    if args.all:
        symbols = list(DEFAULT_SYMBOLS)
    elif args.symbol:
        symbols = [args.symbol]
    else:
        symbols = ["hc"]

    print("=== EXP-009E setup 级 TM 细读 ===")
    print("窗口: 2023-05-17 ~ 2026-05-16 | 含成本")

    all_rows: list[dict] = []
    for sym in symbols:
        all_rows.extend(analyze_symbol(sym, verbose=len(symbols) == 1 or args.all))

    combined = ROOT / "research" / "output" / "exp009e_setup_tm_detail_all.csv"
    pd.DataFrame(all_rows).sort_values(["symbol", "actual_net"]).to_csv(
        combined, index=False, encoding="utf-8-sig",
    )
    if len(symbols) > 1:
        _print_cross_summary(all_rows)
        print(f"\n合并输出: {combined.name}")


if __name__ == "__main__":
    main()
