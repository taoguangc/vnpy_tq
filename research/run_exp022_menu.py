# -*- coding: utf-8
"""EXP-022 — PROFIT 品种 setup 归因 + Purification 对照。

读取 EXP-021 扫描结果或 --symbols，对 PROFIT/MARGINAL 品种：
  1. 基线回测 + setup×PnL 归因
  2. 自动候选：净亏 setup 前缀（n≥3 且 net<-2000）
  3. 1 次 Purification 对照（基线 vs disabled_setups）
  4. 通过则输出可写入 SYMBOL_PROFILES 的 disabled_setups 建议

用法::
  python -m research.run_exp022_menu
  python -m research.run_exp022_menu --symbols hc,al
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.backtest_trade_analysis import RoundTripTrade
from strategies.pa_cta.backtest import run_parquet_backtest
from strategies.pa_cta.symbol_config import SYMBOL_PROFILES

SCAN_JSON = ROOT / "backtests" / "multi_symbol_scan.json"
MIN_SETUP_N = 3
MIN_SETUP_LOSS = -2000.0
PURIFY_DELTA_MIN = 0.0


def _setup_net(trips: list[RoundTripTrade]) -> dict[str, float]:
    acc: dict[str, float] = defaultdict(float)
    cnt: dict[str, int] = defaultdict(int)
    for rt in trips:
        key = rt.setup or "UNKNOWN"
        acc[key] += rt.net_pnl
        cnt[key] += 1
    return {k: (acc[k], cnt[k]) for k in acc}


def _prefix_candidates(setup_stats: dict[str, tuple[float, int]]) -> list[str]:
    """按 OPP 前缀聚合，找净亏族。"""
    by_prefix: dict[str, tuple[float, int]] = defaultdict(lambda: (0.0, 0))
    for setup, (net, n) in setup_stats.items():
        if setup == "UNKNOWN":
            continue
        parts = setup.split("_")
        prefix = parts[0] + "_" if parts else setup
        if len(parts) >= 2 and parts[0].startswith("OPP"):
            prefix = f"{parts[0]}_"
        p_net, p_n = by_prefix[prefix]
        by_prefix[prefix] = (p_net + net, p_n + n)

    candidates: list[str] = []
    for prefix, (net, n) in sorted(by_prefix.items(), key=lambda x: x[1][0]):
        if n >= MIN_SETUP_N and net <= MIN_SETUP_LOSS:
            candidates.append(prefix.rstrip("_") + "_")
    return candidates


def _run_purify(symbol: str, disabled: str) -> dict:
    overrides = {"disabled_setups": disabled} if disabled else {}
    bt = run_parquet_backtest(symbol=symbol, verbose=False, strategy_overrides=overrides or None)
    stats = bt["stats"]
    rt = bt["rt_summary"] or {}
    return {
        "disabled": disabled or "(none)",
        "total_net_pnl": stats.get("total_net_pnl", 0.0),
        "sharpe_ratio": stats.get("sharpe_ratio"),
        "round_trips": rt.get("total", 0),
        "profit_factor": rt.get("profit_factor"),
    }


def _load_profit_symbols() -> list[str]:
    if not SCAN_JSON.is_file():
        return []
    data = json.loads(SCAN_JSON.read_text(encoding="utf-8"))
    tiers = data.get("tiers", {})
    out: list[str] = []
    for tier in ("PROFIT", "MARGINAL"):
        out.extend(tiers.get(tier, []))
    # hc 已有固化菜单，跳过自动 Purify
    return [s for s in out if s.lower() != "hc" and s.lower() not in {k.lower() for k in SYMBOL_PROFILES if SYMBOL_PROFILES[k].get("disabled_setups")}]


def process_symbol(symbol: str) -> dict | None:
    sym = symbol.lower()
    print(f"\n===== EXP-022 | {sym} =====")

    base_bt = run_parquet_backtest(symbol=sym, verbose=False)
    trips = base_bt["round_trips"]
    setup_stats = _setup_net(trips)
    base_pnl = base_bt["stats"].get("total_net_pnl", 0.0)

    print("--- setup×PnL 归因（ACTUAL，含成本）---")
    for setup, (net, n) in sorted(setup_stats.items(), key=lambda x: x[1][0]):
        print(f"  {setup:<42} n={n:>3} net={net:>+10,.0f}")

    candidates = _prefix_candidates(setup_stats)
    if not candidates:
        print("  无净亏 setup 前缀候选（n≥3 & net<-2k）→ SKIP Purify")
        return None

    disabled = ",".join(dict.fromkeys(candidates))
    print(f"\n候选 disabled_setups: `{disabled}`")

    base_r = _run_purify(sym, "")
    pur_r = _run_purify(sym, disabled)
    delta = pur_r["total_net_pnl"] - base_r["total_net_pnl"]

    print("| 版本 | disabled | 净盈亏 | Sharpe | 笔数 | PF | ΔPnL |")
    print("|------|----------|--------|--------|------|-----|------|")
    for label, r in (("基线", base_r), ("Purify", pur_r)):
        pf = r["profit_factor"]
        pf_s = f"{pf:.2f}" if pf is not None else "—"
        sh = r["sharpe_ratio"]
        sh_s = f"{sh:.2f}" if sh is not None else "—"
        d = delta if label == "Purify" else "—"
        print(
            f"| {label} | `{r['disabled']}` | {r['total_net_pnl']:+,.0f} | "
            f"{sh_s} | {r['round_trips']} | {pf_s} | {d if d == '—' else f'{d:+,.0f}'} |"
        )

    passed = delta > PURIFY_DELTA_MIN
    verdict = "KEEP（写 profile）" if passed else "REVERT/HOLD"
    print(f"结论: {verdict}（ΔPnL={delta:+,.0f}）")
    if passed:
        print(f"  建议 `{sym}` profile: disabled_setups=\"{disabled}\"")

    return {
        "symbol": sym,
        "base_pnl": base_pnl,
        "disabled_setups": disabled,
        "purify_pnl": pur_r["total_net_pnl"],
        "delta_pnl": delta,
        "verdict": verdict,
        "write_profile": passed,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="EXP-022 per-symbol setup menu")
    parser.add_argument("--symbols", default="", help="逗号分隔；空则从 scan JSON PROFIT/MARGINAL 读取")
    args = parser.parse_args()

    if args.symbols.strip():
        symbols = [s.strip().lower() for s in args.symbols.split(",") if s.strip()]
    else:
        symbols = _load_profit_symbols()
        if not symbols:
            print("无 PROFIT/MARGINAL 品种或未找到 backtests/multi_symbol_scan.json")
            sys.exit(1)

    print("=== EXP-022 分品种 Setup 菜单 ===")
    print(f"品种: {', '.join(symbols)}")

    summaries: list[dict] = []
    for sym in symbols:
        row = process_symbol(sym)
        if row:
            summaries.append(row)

    out_dir = ROOT / "research" / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    if summaries:
        import pandas as pd

        df = pd.DataFrame(summaries)
        out_path = out_dir / "exp022_menu_summary.csv"
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"\n汇总输出: {out_path}")


if __name__ == "__main__":
    main()
