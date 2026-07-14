# -*- coding: utf-8
"""EXP-006 对照 — pa_cta OPP02 空侧 round_trips IS/OOS 切分。

与 Event 层 SHORT-only @30m 使用相同窗口：
  FULL     2023-01-01 ~ 2025-12-31
  IN-SAMPLE 2024-01-01 ~ 2025-06-30
  OOS-PRE  < 2024-01-01
  OOS-POST > 2025-06-30

用法::
  python -m research.run_opp02_is_oos --symbol rb
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
from strategies.pa_cta.symbol_config import resolve_symbol_profile

CST = ZoneInfo("Asia/Shanghai")
OPP02_SHORT = "OPP02_5M_EMA_PULLBACK_SHORT"

# Event 层 SHORT @30m 对照（2026-07-11 已跑，rb）
EVENT_SHORT_BENCHMARK = {
    "FULL": {"n": 103, "wr": 51.5, "net_ticks": 0.16, "gate": "PASS"},
    "IN-SAMPLE": {"n": 59, "wr": 57.6, "net_ticks": 7.00, "gate": "PASS"},
    "OOS-PRE": {"n": 33, "wr": 45.5, "net_ticks": -6.64, "gate": "FAIL"},
    "OOS-POST": {"n": 11, "wr": 36.4, "net_ticks": -16.18, "gate": "FAIL"},
}


def _ts(dt: datetime) -> pd.Timestamp:
    if dt.tzinfo is None:
        return pd.Timestamp(dt, tz=CST)
    return pd.Timestamp(dt).tz_convert(CST)


def _filter_opp02_short(round_trips: list[RoundTripTrade]) -> list[RoundTripTrade]:
    return [
        rt
        for rt in round_trips
        if (rt.setup or "") == OPP02_SHORT or (
            (rt.setup or "").startswith("OPP02_") and rt.direction == "空"
        )
    ]


def _avg_ticks_pnl(trips: list[RoundTripTrade], *, size: float, pricetick: float) -> float:
    if not trips:
        return float("nan")
    ticks: list[float] = []
    for rt in trips:
        vol = rt.volume if rt.volume else 1.0
        denom = size * pricetick * vol
        if denom <= 0:
            continue
        ticks.append(rt.net_pnl / denom)
    return float(sum(ticks) / len(ticks)) if ticks else float("nan")


def _cohort_metrics(
    trips: list[RoundTripTrade],
    *,
    size: float,
    pricetick: float,
) -> dict:
    if not trips:
        return {
            "n": 0,
            "wr": float("nan"),
            "pf": float("nan"),
            "net_pnl": 0.0,
            "avg_pnl": float("nan"),
            "avg_ticks": float("nan"),
            "gate_n30_profit": False,
        }
    summary = summarize_round_trips(trips)
    net = sum(t.net_pnl for t in trips)
    avg_ticks = _avg_ticks_pnl(trips, size=size, pricetick=pricetick)
    return {
        "n": len(trips),
        "wr": summary["win_rate"],
        "pf": summary["profit_factor"],
        "net_pnl": net,
        "avg_pnl": net / len(trips),
        "avg_ticks": avg_ticks,
        "gate_n30_profit": len(trips) >= 30 and net > 0,
    }


def _slice_cohorts(
    trips: list[RoundTripTrade],
    *,
    window_start: datetime,
    window_end: datetime,
    is_start: datetime,
    is_end: datetime,
) -> dict[str, list[RoundTripTrade]]:
    ws, we = _ts(window_start), _ts(window_end)
    is_s, is_e = _ts(is_start), _ts(is_end)

    full: list[RoundTripTrade] = []
    in_sample: list[RoundTripTrade] = []
    oos_pre: list[RoundTripTrade] = []
    oos_post: list[RoundTripTrade] = []

    for rt in trips:
        et = _ts(rt.entry_time)
        if et < ws or et > we:
            continue
        full.append(rt)
        if is_s <= et <= is_e:
            in_sample.append(rt)
        elif et < is_s:
            oos_pre.append(rt)
        elif et > is_e:
            oos_post.append(rt)

    return {
        "FULL": full,
        "IN-SAMPLE": in_sample,
        "OOS-PRE": oos_pre,
        "OOS-POST": oos_post,
    }


def run_opp02_is_oos(
    *,
    symbol: str = "rb",
    window_start: datetime,
    window_end: datetime,
    is_start: datetime,
    is_end: datetime,
    strategy_overrides: dict | None = None,
    label_suffix: str = "",
    verbose: bool = True,
) -> pd.DataFrame:
    profile = resolve_symbol_profile(symbol, ROOT)
    size = float(profile["size"])
    pricetick = float(profile["pricetick"])

    mode = "profile（AFF 开）" if not strategy_overrides else "counterfactual（AFF 关）"
    if verbose:
        print(f"\n===== EXP-006 对照 | pa_cta {OPP02_SHORT} | {symbol} | {mode} =====")
        print(f"回测窗口: {window_start.date()} ~ {window_end.date()}")
        print(f"IN-SAMPLE: {is_start.date()} ~ {is_end.date()}")
        print("运行 CbC 回测（含成本）…")

    bt = run_parquet_backtest(
        symbol=symbol,
        verbose=False,
        start=window_start,
        end=window_end,
        strategy_overrides=strategy_overrides,
    )
    shorts = _filter_opp02_short(bt["round_trips"])
    cohorts = _slice_cohorts(
        shorts,
        window_start=window_start,
        window_end=window_end,
        is_start=is_start,
        is_end=is_end,
    )

    rows: list[dict] = []
    for label in ("FULL", "IN-SAMPLE", "OOS-PRE", "OOS-POST"):
        m = _cohort_metrics(cohorts[label], size=size, pricetick=pricetick)
        ev = EVENT_SHORT_BENCHMARK.get(label, {})
        rows.append(
            {
                "cohort": label,
                "cta_n": m["n"],
                "cta_wr_pct": m["wr"],
                "cta_pf": m["pf"],
                "cta_net_pnl": m["net_pnl"],
                "cta_avg_pnl": m["avg_pnl"],
                "cta_avg_ticks": m["avg_ticks"],
                "cta_gate_n30_profit": m["gate_n30_profit"],
                "event_n": ev.get("n"),
                "event_wr_pct": ev.get("wr"),
                "event_net_ticks": ev.get("net_ticks"),
                "event_gate": ev.get("gate"),
            }
        )

    df = pd.DataFrame(rows)
    out_dir = ROOT / "research" / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"exp006_opp02_short_is_oos_{symbol}{label_suffix}.csv"
    df.to_csv(out_path, index=False, encoding="utf-8-sig")

    if verbose:
        _print_report(
            df,
            symbol=symbol,
            out_path=out_path,
            total_rt=len(bt["round_trips"]),
            mode=mode,
            aff_blocks=sum(
                1 for rt in bt["round_trips"] if (rt.setup or "").startswith("OPP02_")
            )
            if not strategy_overrides
            else None,
        )

    return df


def _print_report(
    df: pd.DataFrame,
    *,
    symbol: str,
    out_path: Path,
    total_rt: int,
    mode: str = "",
    aff_blocks: int | None = None,
) -> None:
    print(f"\n--- pa_cta OPP02 SHORT round_trips | {mode}（策略全量 {total_rt} RT）---")
    if aff_blocks is not None and df["cta_n"].sum() == 0:
        print(
            f"  注：OPP02 相关 RT 合计 {aff_blocks} 笔（含多），"
            "SHORT 为 0 — rb profile `opp02_aff_gate_enabled=True` 在低 alpha regime 拒空侧 OPP02。"
        )
    print(f"{'Cohort':<12} {'n':>4} {'WR':>7} {'PF':>6} {'net PnL':>10} {'avg tick':>9} {'Gate':>12}")
    print("-" * 68)
    for _, row in df.iterrows():
        wr = row["cta_wr_pct"]
        wr_s = f"{wr:.1f}%" if wr == wr else "—"
        pf = row["cta_pf"]
        pf_s = f"{pf:.2f}" if pf == pf else "—"
        ticks = row["cta_avg_ticks"]
        tick_s = f"{ticks:+.2f}" if ticks == ticks else "—"
        gate = "PASS" if row["cta_gate_n30_profit"] else "FAIL"
        print(
            f"{row['cohort']:<12} {int(row['cta_n']):>4} {wr_s:>7} {pf_s:>6} "
            f"{row['cta_net_pnl']:>+10.0f} {tick_s:>9} {gate:>12}"
        )

    print("\n--- Event SHORT @30m vs CTA OPP02 SHORT 对照 ---")
    print(
        f"{'Cohort':<12} {'Ev n':>5} {'Ev net@3':>9} {'Ev Gate':>8} "
        f"{'|':^3} {'CTA n':>5} {'CTA tick':>9} {'CTA Gate':>10}"
    )
    print("-" * 72)
    for _, row in df.iterrows():
        ev_net = row["event_net_ticks"]
        ev_s = f"{ev_net:+.2f}" if ev_net == ev_net else "—"
        ct = row["cta_avg_ticks"]
        ct_s = f"{ct:+.2f}" if ct == ct else "—"
        cg = "PASS" if row["cta_gate_n30_profit"] else "FAIL"
        print(
            f"{row['cohort']:<12} {int(row['event_n']):>5} {ev_s:>9} {row['event_gate']:>8} "
            f"{'|':^3} {int(row['cta_n']):>5} {ct_s:>9} {cg:>10}"
        )

    print("-" * 72)
    print(f"输出: {out_path}")
    print("=" * 72)


def main() -> None:
    parser = argparse.ArgumentParser(description="OPP02 SHORT IS/OOS vs Event layer")
    parser.add_argument("--symbol", default="rb")
    parser.add_argument("--start", default="2023-01-01")
    parser.add_argument("--end", default="2025-12-31")
    parser.add_argument("--is-start", default="2024-01-01")
    parser.add_argument("--is-end", default="2025-06-30")
    parser.add_argument(
        "--no-opp02-aff-gate",
        action="store_true",
        help="counterfactual：关闭 OPP02 AFF 门禁（非 production profile）",
    )
    args = parser.parse_args()

    overrides = None
    suffix = ""
    if args.no_opp02_aff_gate:
        overrides = {"opp02_aff_gate_enabled": False}
        suffix = "_no_aff"

    run_opp02_is_oos(
        symbol=args.symbol.lower(),
        window_start=datetime.strptime(args.start, "%Y-%m-%d"),
        window_end=datetime.strptime(args.end, "%Y-%m-%d"),
        is_start=datetime.strptime(args.is_start, "%Y-%m-%d"),
        is_end=datetime.strptime(args.is_end, "%Y-%m-%d"),
        strategy_overrides=overrides,
        label_suffix=suffix,
    )


if __name__ == "__main__":
    main()
