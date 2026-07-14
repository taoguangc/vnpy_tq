# -*- coding: utf-8
"""EXP-025 — GENERIC_BASE 上 ag/au/ma：IS 归因选菜单 → OOS 验证。

协议（Program 4.0）：
  1. profile_mode=generic_base（无 AFF / 无禁单 / 无 Router）
  2. 菜单仅由 IS 窗 setup 归因决定（禁止用 FULL/OOS 选禁单）
  3. Base vs Menu 对照同一完整回测窗，按 entry_time 切 IS/OOS
  4. 不复用 EXP-022 禁单列表

Gate（与 EXP-023 相同，OOS 全满足才 KEEP-OOS）：
  ΔPnL>0；PF_menu≥PF_base；n 保留≥50%；IS/OOS 同向；非单笔驱动。

用法::
  python -m research.run_exp025_menu_oos
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.backtest_trade_analysis import RoundTripTrade, summarize_round_trips
from strategies.pa_cta.backtest import run_parquet_backtest

CST = ZoneInfo("Asia/Shanghai")

WINDOW_START = datetime(2023, 5, 17)
WINDOW_END = datetime(2026, 5, 16)
IS_START = datetime(2023, 5, 17)
IS_END = datetime(2024, 12, 31, 23, 59, 59)
OOS_START = datetime(2025, 1, 1)
OOS_END = datetime(2026, 5, 16, 23, 59, 59)

DEFAULT_SYMBOLS = ("ag", "au", "ma")
MIN_SETUP_N = 3
MIN_SETUP_LOSS = -2000.0


def _ts(dt: datetime) -> pd.Timestamp:
    if dt.tzinfo is None:
        return pd.Timestamp(dt, tz=CST)
    return pd.Timestamp(dt).tz_convert(CST)


def _slice(
    trips: list[RoundTripTrade],
    *,
    start: datetime,
    end: datetime,
) -> list[RoundTripTrade]:
    s, e = _ts(start), _ts(end)
    return [rt for rt in trips if s <= _ts(rt.entry_time) <= e]


def _metrics(trips: list[RoundTripTrade]) -> dict:
    if not trips:
        return {
            "n": 0,
            "wr": float("nan"),
            "pf": float("nan"),
            "net_pnl": 0.0,
            "max_abs_trade": 0.0,
            "pnl_wo_max": 0.0,
        }
    summary = summarize_round_trips(trips)
    nets = [t.net_pnl for t in trips]
    net = sum(nets)
    abs_idx = max(range(len(nets)), key=lambda i: abs(nets[i]))
    return {
        "n": len(trips),
        "wr": summary.get("win_rate"),
        "pf": summary.get("profit_factor"),
        "net_pnl": net,
        "max_abs_trade": abs(nets[abs_idx]),
        "pnl_wo_max": net - nets[abs_idx],
    }


def _setup_stats(trips: list[RoundTripTrade]) -> dict[str, tuple[float, int]]:
    acc: dict[str, float] = defaultdict(float)
    cnt: dict[str, int] = defaultdict(int)
    for rt in trips:
        key = rt.setup or "UNKNOWN"
        acc[key] += rt.net_pnl
        cnt[key] += 1
    return {k: (acc[k], cnt[k]) for k in acc}


def _prefix_candidates(setup_stats: dict[str, tuple[float, int]]) -> list[str]:
    by_prefix: dict[str, tuple[float, int]] = defaultdict(lambda: (0.0, 0))
    for setup, (net, n) in setup_stats.items():
        if setup == "UNKNOWN":
            continue
        parts = setup.split("_")
        prefix = f"{parts[0]}_" if parts and parts[0].startswith("OPP") else setup
        p_net, p_n = by_prefix[prefix]
        by_prefix[prefix] = (p_net + net, p_n + n)

    out: list[str] = []
    for prefix, (net, n) in sorted(by_prefix.items(), key=lambda x: x[1][0]):
        if n >= MIN_SETUP_N and net <= MIN_SETUP_LOSS:
            out.append(prefix if prefix.endswith("_") else prefix + "_")
    return out


def _run(symbol: str, disabled: str) -> dict:
    return run_parquet_backtest(
        symbol=symbol,
        verbose=False,
        start=WINDOW_START,
        end=WINDOW_END,
        strategy_overrides={"disabled_setups": disabled},
        profile_mode="generic_base",
    )


def _pf_ok(menu_pf: float, base_pf: float) -> bool:
    if menu_pf != menu_pf:
        return False
    if base_pf != base_pf:
        return True
    return menu_pf >= base_pf - 1e-9


def _verdict(
    *,
    is_delta: float,
    oos_delta: float,
    oos_base: dict,
    oos_menu: dict,
) -> str:
    n_base = oos_base["n"]
    n_menu = oos_menu["n"]
    n_ok = n_menu >= max(3, int(0.5 * n_base)) if n_base > 0 else n_menu >= 3
    pf_ok = _pf_ok(oos_menu["pf"], oos_base["pf"])
    same_dir = (is_delta > 0 and oos_delta > 0) or (is_delta < 0 and oos_delta < 0)
    extreme_ok = (oos_menu["pnl_wo_max"] - oos_base["net_pnl"]) > 0 or oos_delta <= 0

    if oos_delta <= 0:
        return "REVERT"
    if not n_ok or not pf_ok or not same_dir or not extreme_ok:
        return "HOLD"
    return "KEEP-OOS"


def process_symbol(symbol: str) -> dict:
    sym = symbol.lower()
    print(f"\n===== EXP-025 | {sym} | generic_base =====", flush=True)
    print("  Base 回测…", flush=True)
    base_bt = _run(sym, "")
    base_trips = base_bt["round_trips"]
    is_trips = _slice(base_trips, start=IS_START, end=IS_END)

    print("--- IS setup×PnL（仅用于选菜单）---")
    is_stats = _setup_stats(is_trips)
    for setup, (net, n) in sorted(is_stats.items(), key=lambda x: x[1][0]):
        print(f"  {setup:<42} n={n:>3} net={net:>+10,.0f}")

    candidates = _prefix_candidates(is_stats)
    if not candidates:
        print("  IS 无净亏前缀候选 → SKIP")
        return {
            "symbol": sym,
            "menu": "",
            "is_delta": 0.0,
            "oos_delta": 0.0,
            "oos_base_n": _metrics(_slice(base_trips, start=OOS_START, end=OOS_END))["n"],
            "oos_menu_n": 0,
            "verdict": "SKIP",
        }

    menu = ",".join(dict.fromkeys(candidates))
    print(f"  IS 候选菜单: `{menu}`", flush=True)
    print("  Menu 回测…", flush=True)
    menu_bt = _run(sym, menu)

    base_is = _metrics(is_trips)
    base_oos = _metrics(_slice(base_trips, start=OOS_START, end=OOS_END))
    menu_is = _metrics(_slice(menu_bt["round_trips"], start=IS_START, end=IS_END))
    menu_oos = _metrics(_slice(menu_bt["round_trips"], start=OOS_START, end=OOS_END))

    is_delta = menu_is["net_pnl"] - base_is["net_pnl"]
    oos_delta = menu_oos["net_pnl"] - base_oos["net_pnl"]
    verdict = _verdict(
        is_delta=is_delta,
        oos_delta=oos_delta,
        oos_base=base_oos,
        oos_menu=menu_oos,
    )

    print("| Cohort | Base n | Base PnL | PF | Menu n | Menu PnL | PF | ΔPnL |")
    print("|--------|--------|----------|-----|--------|----------|-----|------|")
    for label, b, m in (
        ("IN-SAMPLE", base_is, menu_is),
        ("OUT-OF-SAMPLE", base_oos, menu_oos),
    ):
        bpf = f"{b['pf']:.2f}" if b["pf"] == b["pf"] else "—"
        mpf = f"{m['pf']:.2f}" if m["pf"] == m["pf"] else "—"
        d = m["net_pnl"] - b["net_pnl"]
        print(
            f"| {label} | {b['n']} | {b['net_pnl']:+,.0f} | {bpf} | "
            f"{m['n']} | {m['net_pnl']:+,.0f} | {mpf} | {d:+,.0f} |"
        )
    print(f"结论: {verdict}（IS Δ={is_delta:+,.0f} | OOS Δ={oos_delta:+,.0f}）")

    return {
        "symbol": sym,
        "menu": menu,
        "is_delta": is_delta,
        "oos_delta": oos_delta,
        "oos_base_n": base_oos["n"],
        "oos_menu_n": menu_oos["n"],
        "oos_base_pnl": base_oos["net_pnl"],
        "oos_menu_pnl": menu_oos["net_pnl"],
        "oos_base_pf": base_oos["pf"],
        "oos_menu_pf": menu_oos["pf"],
        "verdict": verdict,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="EXP-025 generic_base menu IS/OOS")
    parser.add_argument("--symbols", default=",".join(DEFAULT_SYMBOLS))
    args = parser.parse_args()
    symbols = [s.strip().lower() for s in args.symbols.split(",") if s.strip()]

    print("=== EXP-025 GENERIC_BASE 菜单 IS 选择 → OOS 验证 ===")
    print(f"窗: {WINDOW_START.date()} ~ {WINDOW_END.date()}")
    print(f"IS:  {IS_START.date()} ~ {IS_END.date()}（归因选菜单）")
    print(f"OOS: {OOS_START.date()} ~ {OOS_END.date()}（定 KEEP）")
    print("单变量: disabled_setups | generic_base | 含成本\n")

    rows = [process_symbol(s) for s in symbols]
    out_dir = ROOT / "research" / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "exp025_menu_is_oos_summary.csv"
    pd.DataFrame(rows).to_csv(out_path, index=False, encoding="utf-8-sig")

    print("\n===== 汇总 =====")
    print("| 品种 | 菜单(IS选) | IS Δ | OOS Δ | OOS n(B→M) | 决策 |")
    print("|------|------------|------|-------|------------|------|")
    for r in rows:
        menu = r["menu"] or "(none)"
        print(
            f"| {r['symbol']} | `{menu}` | {r['is_delta']:+,.0f} | "
            f"{r['oos_delta']:+,.0f} | {int(r['oos_base_n'])}→{int(r['oos_menu_n'])} | "
            f"**{r['verdict']}** |"
        )
    print(f"\n输出: {out_path}")
    print("规则: 仅 KEEP-OOS 才可写 SYMBOL_PROFILES；本脚本不自动写 profile。")


if __name__ == "__main__":
    main()
