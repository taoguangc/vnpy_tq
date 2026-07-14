# -*- coding: utf-8
"""EXP-029 — Phase-4 setup 软收缩：估计 risk_mult，对比硬禁菜单。

用法::
  python -m research.run_setup_shrinkage --symbols rb,hc,au,ma
  python -m research.run_setup_shrinkage --symbol hc --compare-menu
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.backtest_trade_analysis import RoundTripTrade, summarize_round_trips
from strategies.pa_cta.backtest import run_parquet_backtest
from strategies.pa_cta.setup_shrinkage import (
    ShrinkageConfig,
    aggregate_observations,
    compute_class_pools,
    compute_global_pool,
    overrides_from_results,
    shrink_setup_table,
)
from strategies.pa_cta.symbol_config import SYMBOL_PROFILES, cross_symbol_list, resolve_symbol_profile

IS_END = datetime(2025, 5, 16)
OOS_START = datetime(2025, 5, 17)


def _trips_to_records(trips: list[RoundTripTrade]) -> list[dict]:
    out: list[dict] = []
    for rt in trips:
        init_r = float(rt.mae_ticks) if rt.exit_reason == "STOP_LOSS" and rt.mae_ticks > 0 else float(rt.mfe_ticks or 0) * 0.5
        if init_r <= 0 and rt.net_pnl != 0:
            init_r = abs(rt.net_pnl)
        r_mult = rt.net_pnl / init_r if init_r > 0 else 0.0
        out.append({
            "setup": rt.setup or "UNKNOWN",
            "net_pnl": rt.net_pnl,
            "r_multiple": r_mult,
            "initial_r_yuan": init_r,
            "entry_time": rt.entry_time,
        })
    return out


def _split_is_oos(records: list[dict]) -> tuple[list[dict], list[dict]]:
    is_rows, oos_rows = [], []
    oos_naive = OOS_START.replace(tzinfo=None)
    for r in records:
        et = r.get("entry_time")
        if et is None:
            is_rows.append(r)
            continue
        if getattr(et, "tzinfo", None) is not None:
            et_cmp = et.replace(tzinfo=None)
        else:
            et_cmp = et
        if et_cmp >= oos_naive:
            oos_rows.append(r)
        else:
            is_rows.append(r)
    return is_rows, oos_rows


def _run_symbol(symbol: str, *, overrides: dict | None = None) -> dict:
    bt = run_parquet_backtest(symbol=symbol, verbose=False, strategy_overrides=overrides)
    trips = bt["round_trips"]
    stats = bt["stats"]
    rt_sum = summarize_round_trips(trips)
    return {
        "symbol": symbol,
        "stats": stats,
        "rt_summary": rt_sum,
        "trips": trips,
        "records": _trips_to_records(trips),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="EXP-029 setup shrinkage lab")
    parser.add_argument("--symbols", default=",".join(cross_symbol_list()))
    parser.add_argument("--symbol", default=None, help="单品种 + --compare-menu")
    parser.add_argument("--compare-menu", action="store_true", help="对比 disabled_setups vs 软收缩")
    parser.add_argument("--output-dir", default=str(ROOT / "research" / "output"))
    args = parser.parse_args()

    symbols = [s.strip().lower() for s in args.symbols.split(",") if s.strip()]
    if args.symbol:
        sym0 = args.symbol.lower()
        if sym0 not in symbols:
            symbols = [sym0]
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    all_is: list[dict] = []
    all_oos: list[dict] = []
    per_symbol: dict[str, dict] = {}
    compare_rows: list[dict] = []

    print("=== EXP-029 Phase-4 Setup Shrinkage ===")
    print(f"品种: {', '.join(symbols)} | IS ≤ {IS_END.date()} | OOS ≥ {OOS_START.date()}\n")

    for sym in symbols:
        run = _run_symbol(sym)
        is_rows, oos_rows = _split_is_oos(run["records"])
        all_is.extend(is_rows)
        all_oos.extend(oos_rows)
        per_symbol[sym] = run
        print(f"--- {sym} baseline ---")
        print(f"  RT={run['rt_summary']['total']:.0f}  PnL={run['stats'].get('total_net_pnl', 0):+,.0f}  "
              f"PF={run['rt_summary'].get('profit_factor', 0):.2f}")

    is_obs = aggregate_observations(all_is)
    oos_obs = aggregate_observations(all_oos)
    cls_pools = compute_class_pools(is_obs)
    g_pool = compute_global_pool(is_obs)

    cfg = ShrinkageConfig()
    table = shrink_setup_table(
        is_obs, class_pools=cls_pools, global_pool=g_pool, oos_local=oos_obs, cfg=cfg,
    )

    rows = []
    for setup, res in sorted(table.items(), key=lambda x: (x[1].setup_class, x[0])):
        rows.append({
            "setup": setup,
            "class": res.setup_class,
            "n_is": res.n_local,
            "n_class": res.n_class,
            "mean_r_is": round(res.mean_r_local, 3),
            "shrunk_r": round(res.shrunk_r, 3),
            "risk_mult": res.risk_mult,
            "action": res.action,
            "disable_candidate": res.disable_candidate,
        })

    df = pd.DataFrame(rows)
    csv_path = out_dir / "exp029_shrinkage_table.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    overrides_str = overrides_from_results(table, aggregate_class=True)
    print(f"\n--- 分层收缩 risk_mult（类级）---")
    print(f"global_mean_r={g_pool[0]:.3f} (n={g_pool[1]})")
    print(f"profile overrides: setup_shrinkage_overrides=\"{overrides_str}\"")
    print(f"\n禁用候选（须 OOS 负期望 + n≥{cfg.min_n_disable}，默认仍不禁）:")
    disable_rows = [r for r in rows if r["disable_candidate"]]
    if disable_rows:
        for r in disable_rows:
            print(f"  {r['setup']}  shrunk_r={r['shrunk_r']}  action={r['action']}")
    else:
        print("  （无）")

    half_rows = [r for r in rows if r["action"] == "UNKNOWN_HALF"]
    print(f"\n样本不足 → 0.5 风险: {len(half_rows)} 个 setup")

    # 对照默认仅 hc（授权范围）；--symbol 可指定其他
    if args.compare_menu:
        if args.symbol:
            compare_list = [args.symbol.lower()]
        else:
            compare_list = [s for s in symbols if s == "hc"]
        for sym in compare_list:
            profile = resolve_symbol_profile(sym, ROOT)
            disabled = profile.get("disabled_setups", "")
            if not disabled:
                print(f"\n{sym} 无 disabled_setups，跳过菜单对照")
                continue
            # profile 已含硬禁时，基线 ≡ 硬禁；显式再跑一遍确认
            menu_run = _run_symbol(sym, overrides={"disabled_setups": disabled})
            shrink_run = _run_symbol(sym, overrides={
                "setup_shrinkage_enabled": True,
                "setup_shrinkage_overrides": overrides_str,
                "disabled_setups": "",
            })
            base = per_symbol[sym]
            print(f"\n--- {sym} 硬禁 vs 软收缩（同全窗，待验证假设）---")
            print("| 版本 | RT | PnL | PF | Sharpe |")
            print("|------|-----|------|-----|--------|")
            for label, run in [("基线(含菜单)", base), ("硬禁菜单", menu_run), ("软收缩(无硬禁)", shrink_run)]:
                rs = run["rt_summary"]
                sh = run["stats"].get("sharpe_ratio")
                sh_s = f"{sh:.2f}" if sh is not None else "—"
                print(f"| {label} | {rs['total']:.0f} | {run['stats'].get('total_net_pnl', 0):+,.0f} | "
                      f"{rs.get('profit_factor', 0):.2f} | {sh_s} |")
                compare_rows.append({
                    "symbol": sym,
                    "version": label,
                    "rt": rs["total"],
                    "pnl": run["stats"].get("total_net_pnl", 0),
                    "pf": rs.get("profit_factor", 0),
                    "sharpe": sh,
                    "disabled": disabled if "硬禁" in label or "菜单" in label else "",
                    "overrides": overrides_str if "软收缩" in label else "",
                })

    if compare_rows:
        cmp_path = out_dir / "exp029_hc_menu_vs_shrink.csv"
        pd.DataFrame(compare_rows).to_csv(cmp_path, index=False, encoding="utf-8-sig")
        print(f"\n对照输出: {cmp_path.name}")

    print(f"\n输出: {csv_path.name}")


if __name__ == "__main__":
    main()
