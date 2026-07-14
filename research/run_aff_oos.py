# -*- coding: utf-8
"""EXP-020 — rb Setup AFF 日历 IS/OOS 开 vs 关（全策略 PnL）。

窗口（Program 3.0）:
  IS  2023-05-17 ~ 2024-12-31
  OOS 2025-01-01 ~ 2026-05-16

用法::
  python -m research.run_aff_oos --symbol rb
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

CST = ZoneInfo("Asia/Shanghai")

WINDOW_START = datetime(2023, 5, 17)
WINDOW_END = datetime(2026, 5, 16)
IS_START = datetime(2023, 5, 17)
IS_END = datetime(2024, 12, 31, 23, 59, 59)
OOS_START = datetime(2025, 1, 1)
OOS_END = datetime(2026, 5, 16, 23, 59, 59)

AFF_OFF_OVERRIDES = {
    "opp02_aff_gate_enabled": False,
    "opp19_breakout_aff_gate_enabled": False,
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


def _metrics(trips: list[RoundTripTrade], stats: dict) -> dict:
    if not trips:
        return {
            "n": 0,
            "wr": float("nan"),
            "pf": float("nan"),
            "net_pnl": 0.0,
            "sharpe": stats.get("sharpe_ratio"),
        }
    summary = summarize_round_trips(trips)
    net = sum(t.net_pnl for t in trips)
    return {
        "n": len(trips),
        "wr": summary.get("win_rate"),
        "pf": summary.get("profit_factor"),
        "net_pnl": net,
        "sharpe": stats.get("sharpe_ratio"),
    }


def run_variant(
    *,
    symbol: str,
    label: str,
    strategy_overrides: dict | None,
) -> dict:
    bt = run_parquet_backtest(
        symbol=symbol,
        verbose=False,
        start=WINDOW_START,
        end=WINDOW_END,
        strategy_overrides=strategy_overrides,
    )
    trips = bt["round_trips"]
    stats = bt["stats"]
    is_trips = _slice_cohort(trips, start=IS_START, end=IS_END)
    oos_trips = _slice_cohort(trips, start=OOS_START, end=OOS_END)
    return {
        "label": label,
        "full": _metrics(trips, stats),
        "is": _metrics(is_trips, stats),
        "oos": _metrics(oos_trips, stats),
        "stats": stats,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="EXP-020 Setup AFF IS/OOS")
    parser.add_argument("--symbol", default="rb")
    args = parser.parse_args()
    symbol = args.symbol.lower()

    print(f"=== EXP-020 Setup AFF IS/OOS | {symbol} ===")
    print(f"回测窗: {WINDOW_START.date()} ~ {WINDOW_END.date()}")
    print(f"IS:  {IS_START.date()} ~ {IS_END.date()}")
    print(f"OOS: {OOS_START.date()} ~ {OOS_END.date()}")
    print("含成本 | production profile vs AFF 关（OPP02/19 突破）\n")

    aff_on = run_variant(symbol=symbol, label="AFF 开", strategy_overrides=None)
    aff_off = run_variant(
        symbol=symbol, label="AFF 关", strategy_overrides=AFF_OFF_OVERRIDES
    )

    rows = []
    for cohort_key, cohort_label in (("is", "IN-SAMPLE"), ("oos", "OUT-OF-SAMPLE")):
        on_m = aff_on[cohort_key]
        off_m = aff_off[cohort_key]
        delta = on_m["net_pnl"] - off_m["net_pnl"]
        gate = (
            cohort_key == "oos"
            and on_m["net_pnl"] >= off_m["net_pnl"]
            and on_m["n"] >= max(5, int(off_m["n"] * 0.5))
        )
        rows.append(
            {
                "cohort": cohort_label,
                "aff_on_n": on_m["n"],
                "aff_on_pnl": on_m["net_pnl"],
                "aff_on_pf": on_m["pf"],
                "aff_on_wr": on_m["wr"],
                "aff_off_n": off_m["n"],
                "aff_off_pnl": off_m["net_pnl"],
                "aff_off_pf": off_m["pf"],
                "aff_off_wr": off_m["wr"],
                "delta_pnl": delta,
                "oos_gate_pass": gate if cohort_key == "oos" else None,
            }
        )

    df = pd.DataFrame(rows)
    out_dir = ROOT / "research" / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"exp020_aff_is_oos_{symbol}.csv"
    df.to_csv(out_path, index=False, encoding="utf-8-sig")

    print("| Cohort | AFF开 n | AFF开 PnL | PF | AFF关 n | AFF关 PnL | PF | ΔPnL | Gate |")
    print("|--------|---------|-----------|-----|---------|-----------|-----|------|------|")
    for _, row in df.iterrows():
        on_pf = row["aff_on_pf"]
        off_pf = row["aff_off_pf"]
        on_pf_s = f"{on_pf:.2f}" if on_pf == on_pf else "—"
        off_pf_s = f"{off_pf:.2f}" if off_pf == off_pf else "—"
        gate_s = (
            "PASS" if row["oos_gate_pass"] else ("FAIL" if row["cohort"] == "OUT-OF-SAMPLE" else "—")
        )
        print(
            f"| {row['cohort']} | {int(row['aff_on_n'])} | {row['aff_on_pnl']:+,.0f} | "
            f"{on_pf_s} | {int(row['aff_off_n'])} | {row['aff_off_pnl']:+,.0f} | "
            f"{off_pf_s} | {row['delta_pnl']:+,.0f} | {gate_s} |"
        )

    oos_row = df[df["cohort"] == "OUT-OF-SAMPLE"].iloc[0]
    verdict = "KEEP（regime alpha）" if oos_row["oos_gate_pass"] else "HOLD（rb 样本内）"
    print(f"\n结论: {verdict}")
    print(f"输出: {out_path}")


if __name__ == "__main__":
    main()
