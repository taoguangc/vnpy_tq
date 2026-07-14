# -*- coding: utf-8
"""EXP-024 — 干净 GENERIC_BASE 多品种扫描。

与 EXP-021 区别：
  - profile_mode=generic_base（不读 SYMBOL_PROFILES / 无 AFF / 无禁单 / 无 Router）
  - 仅合约规格 + TQ_SYMBOL_PARAM_OVERRIDES 机械尺度
  - 增加 BLOWUP 档（资金归零或 PnL=0 且过频）

用法::
  python -m research.run_generic_base_scan
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

WINDOW_START = datetime(2023, 5, 17)
WINDOW_END = datetime(2026, 5, 16)

DEFAULT_SYMBOLS = tuple(cross_symbol_list())


def _has_data(symbol: str) -> bool:
    key = symbol.lower()
    if key not in TQ_SYMBOL_ENGINE:
        return False
    eng = TQ_SYMBOL_ENGINE[key]
    data_dir = ROOT / "data" / "tq" / eng["folder"]
    return (data_dir / "rollover_map.parquet").is_file()


def _tier(
    pnl: float,
    sharpe: float | None,
    n: int,
    *,
    end_balance: float | None,
    blowup: bool,
) -> str:
    if blowup:
        return "BLOWUP"
    if n == 0:
        return "NO_TRADES"
    sh = sharpe if sharpe is not None else float("-inf")
    if pnl > 3000 and sh > 0.8:
        return "PROFIT"
    if pnl > 0:
        return "MARGINAL"
    return "LOSS"


def _is_blowup(stats: dict, pnl: float, n: int) -> bool:
    end_bal = stats.get("end_balance")
    if end_bal is not None and float(end_bal) <= 0:
        return True
    # vnpy 统计失败时常返回 sharpe=0 且 pnl=0 但笔数很多
    if n >= 80 and abs(pnl) < 1.0 and (stats.get("sharpe_ratio") or 0) == 0:
        return True
    mdd = stats.get("max_ddpercent")
    if mdd is not None and float(mdd) <= -99.0 and n > 20:
        return True
    return False


def scan_symbol(symbol: str) -> dict:
    bt = run_parquet_backtest(
        symbol=symbol,
        verbose=False,
        start=WINDOW_START,
        end=WINDOW_END,
        profile_mode="generic_base",
    )
    stats = bt["stats"]
    rt = bt["rt_summary"] or {}
    pnl = float(stats.get("total_net_pnl") or 0.0)
    sharpe = stats.get("sharpe_ratio")
    n = int(rt.get("total") or stats.get("total_trade_count") or 0)
    end_balance = stats.get("end_balance")
    blowup = _is_blowup(stats, pnl, n)
    return {
        "symbol": symbol.lower(),
        "tier": _tier(pnl, sharpe, n, end_balance=end_balance, blowup=blowup),
        "total_net_pnl": pnl,
        "end_balance": end_balance,
        "sharpe_ratio": sharpe,
        "round_trips": n,
        "win_rate": rt.get("win_rate"),
        "profit_factor": rt.get("profit_factor"),
        "max_ddpercent": stats.get("max_ddpercent"),
        "annual_return": stats.get("annual_return"),
    }


def _json_safe(obj):
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    if hasattr(obj, "item"):
        return obj.item()
    return obj


def main() -> None:
    parser = argparse.ArgumentParser(description="EXP-024 generic base scan")
    parser.add_argument("--symbols", default=",".join(DEFAULT_SYMBOLS))
    args = parser.parse_args()
    symbols = [s.strip().lower() for s in args.symbols.split(",") if s.strip()]

    print("=== EXP-024 GENERIC_BASE 多品种扫描 ===")
    print(f"窗口: {WINDOW_START.date()} ~ {WINDOW_END.date()} | 含成本")
    print("profile: 无 SYMBOL_PROFILES / 无 AFF / 无禁单 / 无 Router\n")

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
                f"end={row['end_balance']} n={row['round_trips']}"
            )
        except Exception as exc:
            print(f"    → ERROR: {exc}")

    results.sort(key=lambda r: r.get("total_net_pnl") or 0, reverse=True)

    print("\n| 档位 | 品种 | 净盈亏 | Sharpe | 笔数 | end_bal |")
    print("|------|------|--------|--------|------|---------|")
    for row in results:
        sh = row.get("sharpe_ratio")
        sh_s = f"{sh:.2f}" if sh is not None else "—"
        eb = row.get("end_balance")
        eb_s = f"{eb:,.0f}" if eb is not None else "—"
        print(
            f"| {row['tier']} | {row['symbol']} | {row['total_net_pnl']:+,.0f} | "
            f"{sh_s} | {row['round_trips']} | {eb_s} |"
        )

    by_tier: dict[str, list[str]] = {
        "PROFIT": [], "MARGINAL": [], "LOSS": [], "BLOWUP": [], "NO_TRADES": [],
    }
    for row in results:
        by_tier.setdefault(row["tier"], []).append(row["symbol"])

    print("\n分档汇总:")
    for tier in ("PROFIT", "MARGINAL", "LOSS", "BLOWUP", "NO_TRADES"):
        syms = by_tier.get(tier, [])
        if syms:
            print(f"  {tier}: {', '.join(syms)}")

    out_dir = ROOT / "backtests"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "generic_base_scan.json"
    payload = _json_safe({
        "window": {"start": str(WINDOW_START.date()), "end": str(WINDOW_END.date())},
        "profile": "generic_base",
        "results": results,
        "tiers": by_tier,
    })
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n输出: {out_path}")


if __name__ == "__main__":
    main()
