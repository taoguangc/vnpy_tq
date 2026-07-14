# -*- coding: utf-8
"""EXP-023 — 分品种 Setup 菜单日历 IS/OOS（Base vs Menu）。

协议（Program 4.0）：
  IS  2023-05-17 ~ 2024-12-31  （选择窗，仅报告）
  OOS 2025-01-01 ~ 2026-05-16  （验证窗，定 KEEP）
  单变量：仅 disabled_setups 开/关；AFF/ATR/仓位/出场不变。

Gate（OOS 同时满足才 KEEP-OOS）：
  1. ΔPnL > 0
  2. PF_menu ≥ PF_base（或 base PF 为 nan 且 menu PF 有限）
  3. n_menu ≥ max(3, 0.5 * n_base)
  4. IS 与 OOS 的 ΔPnL 同向
  5. OOS 改善不全由单笔贡献（单笔 |net| < |ΔPnL| 或 ΔPnL 去掉最大一笔后仍 >0）

用法::
  python -m research.run_menu_oos
  python -m research.run_menu_oos --symbols hc,rb,au,ma,j
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.backtest_trade_analysis import RoundTripTrade, summarize_round_trips
from strategies.pa_cta.backtest import run_parquet_backtest
from strategies.pa_cta.symbol_config import SYMBOL_PROFILES

CST = ZoneInfo("Asia/Shanghai")

WINDOW_START = datetime(2023, 5, 17)
WINDOW_END = datetime(2026, 5, 16)
IS_START = datetime(2023, 5, 17)
IS_END = datetime(2024, 12, 31, 23, 59, 59)
OOS_START = datetime(2025, 1, 1)
OOS_END = datetime(2026, 5, 16, 23, 59, 59)

DEFAULT_SYMBOLS = ("hc", "rb", "au", "ma", "j")

# Program 3.0 / EXP-022 写入的候选菜单（显式列出，避免误读 profile 漂移）
CANDIDATE_MENUS: dict[str, str] = {
    "hc": "OPP13_,OPP15_,OPP19_5M_OD_REV_SHORT",
    "rb": "OPP12_",
    "au": "OPP15_,OPP12_,OPP13_",
    "ma": "OPP15_,OPP13_",
    "j": "OPP15_",
}


def _ts(dt: datetime) -> pd.Timestamp:
    if dt.tzinfo is None:
        return pd.Timestamp(dt, tz=CST)
    return pd.Timestamp(dt).tz_convert(CST)


def _slice_cohort(
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
    # 去掉对总 PnL 贡献最大的那一笔（按绝对值）
    abs_idx = max(range(len(nets)), key=lambda i: abs(nets[i]))
    pnl_wo_max = net - nets[abs_idx]
    return {
        "n": len(trips),
        "wr": summary.get("win_rate"),
        "pf": summary.get("profit_factor"),
        "net_pnl": net,
        "max_abs_trade": abs(nets[abs_idx]),
        "pnl_wo_max": pnl_wo_max,
    }


def _run_bt(symbol: str, disabled: str) -> dict:
    overrides = {"disabled_setups": disabled}
    bt = run_parquet_backtest(
        symbol=symbol,
        verbose=False,
        start=WINDOW_START,
        end=WINDOW_END,
        strategy_overrides=overrides,
    )
    trips = bt["round_trips"]
    return {
        "full": _metrics(trips),
        "is": _metrics(_slice_cohort(trips, start=IS_START, end=IS_END)),
        "oos": _metrics(_slice_cohort(trips, start=OOS_START, end=OOS_END)),
        "stats": bt["stats"],
    }


def _pf_ok(menu_pf: float, base_pf: float) -> bool:
    if menu_pf != menu_pf:  # nan
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
    # 去掉最大一笔后 OOS menu 仍优于 base（近似：menu_wo_max - base_net > 0）
    extreme_ok = (oos_menu["pnl_wo_max"] - oos_base["net_pnl"]) > 0 or oos_delta <= 0

    if oos_delta <= 0:
        return "REVERT"
    if not n_ok or not pf_ok:
        return "HOLD"
    if not same_dir:
        return "HOLD"
    if not extreme_ok:
        return "HOLD"
    return "KEEP-OOS"


def process_symbol(symbol: str) -> dict:
    sym = symbol.lower()
    menu = CANDIDATE_MENUS.get(sym) or SYMBOL_PROFILES.get(sym, {}).get("disabled_setups", "")
    if not menu:
        raise ValueError(f"{sym}: 无候选菜单")

    print(f"\n===== EXP-023 | {sym} | menu=`{menu}` =====", flush=True)
    print("  跑 Base（禁单空）…", flush=True)
    base = _run_bt(sym, "")
    print("  跑 Menu…", flush=True)
    menu_r = _run_bt(sym, menu)

    rows = []
    for cohort, key in (("IN-SAMPLE", "is"), ("OUT-OF-SAMPLE", "oos"), ("FULL", "full")):
        b, m = base[key], menu_r[key]
        delta = m["net_pnl"] - b["net_pnl"]
        rows.append(
            {
                "symbol": sym,
                "menu": menu,
                "cohort": cohort,
                "base_n": b["n"],
                "base_pnl": b["net_pnl"],
                "base_pf": b["pf"],
                "menu_n": m["n"],
                "menu_pnl": m["net_pnl"],
                "menu_pf": m["pf"],
                "delta_pnl": delta,
            }
        )

    is_delta = menu_r["is"]["net_pnl"] - base["is"]["net_pnl"]
    oos_delta = menu_r["oos"]["net_pnl"] - base["oos"]["net_pnl"]
    verdict = _verdict(
        is_delta=is_delta,
        oos_delta=oos_delta,
        oos_base=base["oos"],
        oos_menu=menu_r["oos"],
    )

    print(
        f"| {sym} | Cohort | Base n | Base PnL | PF | Menu n | Menu PnL | PF | ΔPnL |"
    )
    print("|------|--------|--------|----------|-----|--------|----------|-----|------|")
    for r in rows:
        if r["cohort"] == "FULL":
            continue
        bpf = r["base_pf"]
        mpf = r["menu_pf"]
        bpf_s = f"{bpf:.2f}" if bpf == bpf else "—"
        mpf_s = f"{mpf:.2f}" if mpf == mpf else "—"
        print(
            f"| {sym} | {r['cohort']} | {int(r['base_n'])} | {r['base_pnl']:+,.0f} | "
            f"{bpf_s} | {int(r['menu_n'])} | {r['menu_pnl']:+,.0f} | "
            f"{mpf_s} | {r['delta_pnl']:+,.0f} |"
        )
    print(f"结论: {verdict}（IS Δ={is_delta:+,.0f} | OOS Δ={oos_delta:+,.0f}）")

    return {
        "symbol": sym,
        "menu": menu,
        "is_delta": is_delta,
        "oos_delta": oos_delta,
        "oos_base_n": base["oos"]["n"],
        "oos_menu_n": menu_r["oos"]["n"],
        "oos_base_pnl": base["oos"]["net_pnl"],
        "oos_menu_pnl": menu_r["oos"]["net_pnl"],
        "oos_base_pf": base["oos"]["pf"],
        "oos_menu_pf": menu_r["oos"]["pf"],
        "verdict": verdict,
        "detail_rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="EXP-023 menu IS/OOS")
    parser.add_argument(
        "--symbols",
        default=",".join(DEFAULT_SYMBOLS),
        help="逗号分隔品种",
    )
    args = parser.parse_args()
    symbols = [s.strip().lower() for s in args.symbols.split(",") if s.strip()]

    print("=== EXP-023 Setup 菜单日历 IS/OOS ===")
    print(f"窗: {WINDOW_START.date()} ~ {WINDOW_END.date()}")
    print(f"IS:  {IS_START.date()} ~ {IS_END.date()}")
    print(f"OOS: {OOS_START.date()} ~ {OOS_END.date()}")
    print("单变量: disabled_setups | AFF/其余参数不变 | 含成本\n")

    summaries: list[dict] = []
    all_rows: list[dict] = []
    for sym in symbols:
        result = process_symbol(sym)
        summaries.append({k: v for k, v in result.items() if k != "detail_rows"})
        all_rows.extend(result["detail_rows"])

    out_dir = ROOT / "research" / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    detail_path = out_dir / "exp023_menu_is_oos_detail.csv"
    summary_path = out_dir / "exp023_menu_is_oos_summary.csv"
    pd.DataFrame(all_rows).to_csv(detail_path, index=False, encoding="utf-8-sig")
    pd.DataFrame(summaries).to_csv(summary_path, index=False, encoding="utf-8-sig")

    print("\n===== 汇总 =====")
    print("| 品种 | 菜单 | IS Δ | OOS Δ | OOS n(B→M) | 决策 |")
    print("|------|------|------|-------|------------|------|")
    for s in summaries:
        print(
            f"| {s['symbol']} | `{s['menu']}` | {s['is_delta']:+,.0f} | "
            f"{s['oos_delta']:+,.0f} | {int(s['oos_base_n'])}→{int(s['oos_menu_n'])} | "
            f"**{s['verdict']}** |"
        )
    print(f"\n输出: {summary_path}")
    print(f"明细: {detail_path}")


if __name__ == "__main__":
    main()
