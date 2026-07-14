# -*- coding: utf-8
"""EXP-007B — pa_cta OPP08 vs Event BP @5m IS/OOS 对照。

窗口（与 EXP-006B 一致）::
  FULL      2023-01-01 ~ 2025-12-31
  IN-SAMPLE 2024-01-01 ~ 2025-06-30
  OOS-PRE   < 2024-01-01
  OOS-POST  > 2025-06-30

Event 层：breakout_pullback @ **5m**（007A 相对最优 TF）

用法::
  python -m research.run_opp08_is_oos --symbol rb
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.event_engine.bars import load_bars, resample_minutes
from research.event_engine.detectors import get_detector
from research.event_engine.forwards import attach_forwards
from research.event_engine.schema import DEFAULT_COST_TICKS, records_to_dataframe
from scripts.backtest_trade_analysis import RoundTripTrade, summarize_round_trips
from strategies.pa_cta.backtest import run_parquet_backtest
from strategies.pa_cta.symbol_config import resolve_symbol_profile

CST = ZoneInfo("Asia/Shanghai")
EVENT_TF_MIN = 5
COHORT_LABELS = ("FULL", "IN-SAMPLE", "OOS-PRE", "OOS-POST")


def _ts(dt: datetime) -> pd.Timestamp:
    if dt.tzinfo is None:
        return pd.Timestamp(dt, tz=CST)
    return pd.Timestamp(dt).tz_convert(CST)


def _filter_opp08(
    round_trips: list[RoundTripTrade],
    *,
    side: str | None = None,
) -> list[RoundTripTrade]:
    trips = [rt for rt in round_trips if (rt.setup or "").startswith("OPP08_")]
    if side == "short":
        return [rt for rt in trips if rt.direction == "空" or "SHORT" in (rt.setup or "")]
    if side == "long":
        return [rt for rt in trips if rt.direction == "多" or "LONG" in (rt.setup or "")]
    return trips


def _slice_by_entry_time(
    items: list,
    *,
    time_fn,
    window_start: datetime,
    window_end: datetime,
    is_start: datetime,
    is_end: datetime,
) -> dict[str, list]:
    ws, we = _ts(window_start), _ts(window_end)
    is_s, is_e = _ts(is_start), _ts(is_end)
    out = {k: [] for k in COHORT_LABELS}
    for item in items:
        et = _ts(time_fn(item))
        if et < ws or et > we:
            continue
        out["FULL"].append(item)
        if is_s <= et <= is_e:
            out["IN-SAMPLE"].append(item)
        elif et < is_s:
            out["OOS-PRE"].append(item)
        elif et > is_e:
            out["OOS-POST"].append(item)
    return out


def _avg_ticks_pnl(trips: list[RoundTripTrade], *, size: float, pricetick: float) -> float:
    if not trips:
        return float("nan")
    vals: list[float] = []
    for rt in trips:
        vol = rt.volume if rt.volume else 1.0
        denom = size * pricetick * vol
        if denom > 0:
            vals.append(rt.net_pnl / denom)
    return float(sum(vals) / len(vals)) if vals else float("nan")


def _cta_metrics(trips: list[RoundTripTrade], *, size: float, pricetick: float) -> dict:
    if not trips:
        return {
            "n": 0,
            "wr": np.nan,
            "pf": np.nan,
            "net_pnl": 0.0,
            "avg_ticks": np.nan,
            "gate": False,
        }
    summary = summarize_round_trips(trips)
    net = sum(t.net_pnl for t in trips)
    return {
        "n": len(trips),
        "wr": summary["win_rate"],
        "pf": summary["profit_factor"],
        "net_pnl": net,
        "avg_ticks": _avg_ticks_pnl(trips, size=size, pricetick=pricetick),
        "gate": len(trips) >= 30 and net > 0,
    }


def _event_metrics(events: pd.DataFrame, *, tick: float, cost_ticks: float) -> dict:
    if events.empty:
        return {"n": 0, "wr": np.nan, "net_ticks": np.nan, "gate": False}
    f10 = events["future_10"] / tick
    net3 = float(f10.mean()) - cost_ticks
    return {
        "n": len(events),
        "wr": float((f10 > 0).mean()) * 100.0,
        "net_ticks": net3,
        "gate": len(events) >= 30 and net3 > 0,
    }


def _build_event_bp(
    *,
    symbol: str,
    window_start: datetime,
    window_end: datetime,
    tick: float,
) -> pd.DataFrame:
    spec = get_detector("breakout_pullback")
    bars_1m, _ = load_bars(symbol=symbol, start=window_start, end=window_end)
    bars = resample_minutes(bars_1m, EVENT_TF_MIN)
    work = spec.prepare(bars) if spec.prepare is not None else bars
    records = spec.detect(work, symbol=symbol, tick=tick)
    for rec in records:
        rec.bar_interval = f"{EVENT_TF_MIN}m"
    records = attach_forwards(records, bars)
    return records_to_dataframe(records)


def run_opp08_is_oos(
    *,
    symbol: str = "rb",
    window_start: datetime,
    window_end: datetime,
    is_start: datetime,
    is_end: datetime,
    tick: float = 1.0,
    cost_ticks: float = DEFAULT_COST_TICKS,
    verbose: bool = True,
) -> pd.DataFrame:
    profile = resolve_symbol_profile(symbol, ROOT)
    size = float(profile["size"])
    pricetick = float(profile["pricetick"])

    if verbose:
        print(f"\n===== EXP-007B | OPP08 vs Event BP @{EVENT_TF_MIN}m | {symbol} =====")
        print(f"回测窗口: {window_start.date()} ~ {window_end.date()}")
        print(f"IN-SAMPLE: {is_start.date()} ~ {is_end.date()}")
        print("加载 Event BP @5m …")

    events_all = _build_event_bp(
        symbol=symbol,
        window_start=window_start,
        window_end=window_end,
        tick=tick,
    )
    ev_long = events_all[events_all["direction"] == 1] if not events_all.empty else events_all
    ev_short = events_all[events_all["direction"] == -1] if not events_all.empty else events_all

    def _df_cohorts(base: pd.DataFrame) -> dict[str, pd.DataFrame]:
        if base.empty:
            return {k: base.copy() for k in COHORT_LABELS}
        sliced = _slice_by_entry_time(
            base.to_dict("records"),
            time_fn=lambda r: r["datetime"],
            window_start=window_start,
            window_end=window_end,
            is_start=is_start,
            is_end=is_end,
        )
        return {k: pd.DataFrame(v) if v else base.iloc[0:0].copy() for k, v in sliced.items()}

    ev_cohorts = {
        "ALL": _df_cohorts(events_all),
        "LONG": _df_cohorts(ev_long),
        "SHORT": _df_cohorts(ev_short),
    }

    if verbose:
        print("运行 pa_cta CbC 回测（含成本）…")

    bt = run_parquet_backtest(
        symbol=symbol,
        verbose=False,
        start=window_start,
        end=window_end,
    )
    cta_cohorts = {
        "ALL": _slice_by_entry_time(
            _filter_opp08(bt["round_trips"]),
            time_fn=lambda rt: rt.entry_time,
            window_start=window_start,
            window_end=window_end,
            is_start=is_start,
            is_end=is_end,
        ),
        "LONG": _slice_by_entry_time(
            _filter_opp08(bt["round_trips"], side="long"),
            time_fn=lambda rt: rt.entry_time,
            window_start=window_start,
            window_end=window_end,
            is_start=is_start,
            is_end=is_end,
        ),
        "SHORT": _slice_by_entry_time(
            _filter_opp08(bt["round_trips"], side="short"),
            time_fn=lambda rt: rt.entry_time,
            window_start=window_start,
            window_end=window_end,
            is_start=is_start,
            is_end=is_end,
        ),
    }

    rows: list[dict] = []
    for side in ("ALL", "LONG", "SHORT"):
        for label in COHORT_LABELS:
            em = _event_metrics(ev_cohorts[side][label], tick=tick, cost_ticks=cost_ticks)
            cm = _cta_metrics(cta_cohorts[side][label], size=size, pricetick=pricetick)
            rows.append(
                {
                    "side": side,
                    "cohort": label,
                    "event_n": em["n"],
                    "event_wr_pct": em["wr"],
                    "event_net_ticks": em["net_ticks"],
                    "event_gate": em["gate"],
                    "cta_n": cm["n"],
                    "cta_wr_pct": cm["wr"],
                    "cta_pf": cm["pf"],
                    "cta_net_pnl": cm["net_pnl"],
                    "cta_avg_ticks": cm["avg_ticks"],
                    "cta_gate": cm["gate"],
                }
            )

    df = pd.DataFrame(rows)
    out_dir = ROOT / "research" / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"exp007b_opp08_vs_bp5m_{symbol}.csv"
    df.to_csv(out_path, index=False, encoding="utf-8-sig")

    if verbose:
        _print_report(df, out_path=out_path, total_rt=len(bt["round_trips"]))

    return df


def _print_report(df: pd.DataFrame, *, out_path: Path, total_rt: int) -> None:
    print(f"\n--- pa_cta OPP08 round_trips（策略全量 {total_rt} RT）---")
    print(f"{'Side':<6} {'Cohort':<12} {'n':>4} {'WR':>7} {'PF':>6} {'net PnL':>10} {'avg tick':>9} {'Gate':>6}")
    print("-" * 72)
    cta = df[df["side"] == "ALL"]
    for _, row in cta.iterrows():
        wr = row["cta_wr_pct"]
        wr_s = f"{wr:.1f}%" if wr == wr else "—"
        pf = row["cta_pf"]
        pf_s = f"{pf:.2f}" if pf == pf else "—"
        ticks = row["cta_avg_ticks"]
        tick_s = f"{ticks:+.2f}" if ticks == ticks else "—"
        g = "PASS" if row["cta_gate"] else "FAIL"
        print(
            f"{'ALL':<6} {row['cohort']:<12} {int(row['cta_n']):>4} {wr_s:>7} {pf_s:>6} "
            f"{row['cta_net_pnl']:>+10.0f} {tick_s:>9} {g:>6}"
        )

    print("\n--- Event BP @5m ---")
    print(f"{'Side':<6} {'Cohort':<12} {'n':>4} {'WR':>7} {'net@3':>8} {'Gate':>6}")
    print("-" * 52)
    for side in ("ALL", "LONG", "SHORT"):
        sub = df[df["side"] == side]
        for _, row in sub.iterrows():
            wr = row["event_wr_pct"]
            wr_s = f"{wr:.1f}%" if wr == wr else "—"
            net3 = row["event_net_ticks"]
            net_s = f"{net3:+.2f}" if net3 == net3 else "—"
            g = "PASS" if row["event_gate"] else "FAIL"
            print(
                f"{side:<6} {row['cohort']:<12} {int(row['event_n']):>4} {wr_s:>7} "
                f"{net_s:>8} {g:>6}"
            )

    print("\n--- 对照（ALL）---")
    print(f"{'Cohort':<12} {'Ev n':>5} {'Ev net@3':>9} {'Ev':>5} | {'CTA n':>5} {'CTA tick':>9} {'CTA':>5}")
    print("-" * 62)
    for _, row in cta.iterrows():
        en = row["event_net_ticks"]
        en_s = f"{en:+.2f}" if en == en else "—"
        ct = row["cta_avg_ticks"]
        ct_s = f"{ct:+.2f}" if ct == ct else "—"
        print(
            f"{row['cohort']:<12} {int(row['event_n']):>5} {en_s:>9} "
            f"{'P' if row['event_gate'] else 'F':>5} | "
            f"{int(row['cta_n']):>5} {ct_s:>9} {'P' if row['cta_gate'] else 'F':>5}"
        )

    print("-" * 62)
    print(f"输出: {out_path}")
    print("=" * 72)


def main() -> None:
    parser = argparse.ArgumentParser(description="EXP-007B OPP08 vs Event BP IS/OOS")
    parser.add_argument("--symbol", default="rb")
    parser.add_argument("--start", default="2023-01-01")
    parser.add_argument("--end", default="2025-12-31")
    parser.add_argument("--is-start", default="2024-01-01")
    parser.add_argument("--is-end", default="2025-06-30")
    parser.add_argument("--tick", type=float, default=1.0)
    parser.add_argument("--cost-ticks", type=float, default=3.0)
    args = parser.parse_args()

    run_opp08_is_oos(
        symbol=args.symbol.lower(),
        window_start=datetime.strptime(args.start, "%Y-%m-%d"),
        window_end=datetime.strptime(args.end, "%Y-%m-%d"),
        is_start=datetime.strptime(args.is_start, "%Y-%m-%d"),
        is_end=datetime.strptime(args.is_end, "%Y-%m-%d"),
        tick=args.tick,
        cost_ticks=args.cost_ticks,
    )


if __name__ == "__main__":
    main()
