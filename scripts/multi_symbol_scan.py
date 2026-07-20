# -*- coding: utf-8
"""EXP-021 — lean 多品种扫描（通用 rb profile，无品种特化禁单）。

向无 SYMBOL_PROFILES 的品种注入 rb lean 模板 + TQ_SYMBOL_PARAM_OVERRIDES。
输出 PROFIT / MARGINAL / LOSS 分档，写入 backtests/multi_symbol_scan.json。

用法::
  python scripts/multi_symbol_scan.py
  python scripts/multi_symbol_scan.py --symbols rb,hc,al,zn
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from strategies.pa_cta.backtest import run_parquet_backtest
from strategies.pa_cta.symbol_config import TQ_SYMBOL_ENGINE, cross_symbol_list

WINDOW_START = datetime(2021, 7, 1)
WINDOW_END = datetime(2026, 6, 30)

DEFAULT_SYMBOLS = tuple(cross_symbol_list())


def _has_data(symbol: str) -> bool:
    key = symbol.lower()
    if key not in TQ_SYMBOL_ENGINE:
        return False
    eng = TQ_SYMBOL_ENGINE[key]
    data_dir = ROOT / "data" / "tq" / eng["folder"]
    return (data_dir / "rollover_map.parquet").is_file()


def _tier(pnl: float, sharpe: float | None, n: int) -> str:
    if n == 0:
        return "NO_TRADES"
    sh = sharpe if sharpe is not None else float("-inf")
    if pnl > 3000 and sh > 0.8:
        return "PROFIT"
    if pnl > 0:
        return "MARGINAL"
    return "LOSS"


def scan_symbol(symbol: str) -> dict:
    bt = run_parquet_backtest(
        symbol=symbol,
        verbose=False,
        start=WINDOW_START,
        end=WINDOW_END,
    )
    stats = bt["stats"]
    rt = bt["rt_summary"] or {}
    pnl = float(stats.get("total_net_pnl") or 0.0)
    sharpe = stats.get("sharpe_ratio")
    n = int(rt.get("total") or stats.get("total_trade_count") or 0)
    wr = rt.get("win_rate")
    pf = rt.get("profit_factor")
    return {
        "symbol": symbol.lower(),
        "tier": _tier(pnl, sharpe, n),
        "total_net_pnl": pnl,
        "sharpe_ratio": sharpe,
        "round_trips": n,
        "win_rate": wr,
        "profit_factor": pf,
        "max_ddpercent": stats.get("max_ddpercent"),
        "annual_return": stats.get("annual_return"),
    }


def _json_safe(obj):
    """Convert numpy/scalar types for json.dumps."""
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    if hasattr(obj, "item"):
        return obj.item()
    return obj


def main() -> None:
    parser = argparse.ArgumentParser(description="EXP-021 lean multi-symbol scan")
    parser.add_argument(
        "--symbols",
        default=",".join(DEFAULT_SYMBOLS),
        help="逗号分隔品种列表",
    )
    args = parser.parse_args()
    symbols = [s.strip().lower() for s in args.symbols.split(",") if s.strip()]

    print("=== EXP-021 lean 多品种扫描 ===")
    print(f"窗口: {WINDOW_START.date()} ~ {WINDOW_END.date()} | 含成本 | 通用 rb profile\n")

    results: list[dict] = []
    for sym in symbols:
        if not _has_data(sym):
            print(f"  SKIP {sym}: 无 rollover_map")
            continue
        print(f"  扫描 {sym}…", flush=True)
        try:
            row = scan_symbol(sym)
            results.append(row)
            print(
                f"    → {row['tier']:>10} PnL={row['total_net_pnl']:+,.0f} "
                f"Sharpe={row['sharpe_ratio']} n={row['round_trips']}"
            )
        except Exception as exc:
            print(f"    → ERROR: {exc}")

    results.sort(key=lambda r: r.get("total_net_pnl") or 0, reverse=True)

    print("\n| 档位 | 品种 | 净盈亏 | Sharpe | 笔数 | WR | PF |")
    print("|------|------|--------|--------|------|-----|-----|")
    for row in results:
        wr = row.get("win_rate")
        pf = row.get("profit_factor")
        wr_s = f"{wr:.1f}%" if wr is not None else "—"
        pf_s = f"{pf:.2f}" if pf is not None else "—"
        sh = row.get("sharpe_ratio")
        sh_s = f"{sh:.2f}" if sh is not None else "—"
        print(
            f"| {row['tier']} | {row['symbol']} | {row['total_net_pnl']:+,.0f} | "
            f"{sh_s} | {row['round_trips']} | {wr_s} | {pf_s} |"
        )

    by_tier: dict[str, list[str]] = {"PROFIT": [], "MARGINAL": [], "LOSS": [], "NO_TRADES": []}
    for row in results:
        by_tier.setdefault(row["tier"], []).append(row["symbol"])

    print("\n分档汇总:")
    for tier in ("PROFIT", "MARGINAL", "LOSS", "NO_TRADES"):
        syms = by_tier.get(tier, [])
        if syms:
            print(f"  {tier}: {', '.join(syms)}")

    out_dir = ROOT / "backtests"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "multi_symbol_scan.json"
    payload = _json_safe({
        "window": {"start": str(WINDOW_START.date()), "end": str(WINDOW_END.date())},
        "profile": "lean_rb_generic",
        "results": results,
        "tiers": by_tier,
    })
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n输出: {out_path}")


if __name__ == "__main__":
    main()
