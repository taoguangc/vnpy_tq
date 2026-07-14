# -*- coding: utf-8
"""E4 — delta_div 子样本 full-horizon expectancy curve（1m bars）。

验证「薄 edge 是否随持有期放大」；不写策略。

Horizons: 5, 10, 20, 30, 60, 120（1m close vs entry_price）

用法::
  .venv\\Scripts\\python.exe experiments/E4_expectancy_curve.py
  .venv\\Scripts\\python.exe experiments/E4_expectancy_curve.py --symbol ta --bar-sec 30
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.E1_tick_native_micro import (
    _load_tick_cache_for_symbol,
    run_study,
)
from experiments.E1_pattern_delta_micro import _add_tick_micro_columns
from scripts.tq_tick_loader import _resample_ticks_to_1m

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
EXPECTANCY_HORIZONS = (5, 10, 20, 30, 60, 120)
COST_TICKS = 3.0
COST_TICKS_ALT = 2.0

# 各品种 ladder 收盘段最优 bar_sec
DEFAULT_SPECIES = {
    "rb": 60,
    "ma": 60,
    "ta": 30,
}


def _in_close_session(ts: pd.Timestamp) -> bool:
    m = ts.hour * 60 + ts.minute
    return 870 <= m < 900


def _attach_horizons(
    bars_1m: pd.DataFrame,
    events: pd.DataFrame,
    horizons: tuple[int, ...],
) -> pd.DataFrame:
    if events.empty or bars_1m.empty:
        return pd.DataFrame()

    b1 = bars_1m.sort_values("bar_end").reset_index(drop=True)
    ends = pd.to_datetime(b1["bar_end"]).tolist()
    closes = b1["close"].astype(float).to_numpy()
    max_k = max(horizons)

    rows: list[dict] = []
    for _, ev in events.iterrows():
        ts = pd.Timestamp(ev["datetime"])
        if ts.tzinfo is None:
            ts = ts.tz_localize("Asia/Shanghai")
        idx = int(np.searchsorted(ends, ts, side="right"))
        if idx + max_k > len(b1):
            continue
        direction = int(ev["direction"])
        entry = float(ev["entry_price"])
        row = ev.to_dict()
        for k in horizons:
            row[f"future_{k}"] = direction * (closes[idx + k - 1] - entry)
        rows.append(row)
    return pd.DataFrame(rows)


def _enrich_horizons(events: pd.DataFrame, tick_cache: dict[str, pd.DataFrame]) -> pd.DataFrame:
    chunks: list[pd.DataFrame] = []
    for yymm, grp in events.groupby("yymm"):
        yymm = str(yymm)
        if yymm not in tick_cache:
            continue
        seg = _add_tick_micro_columns(tick_cache[yymm].copy())
        bars_1m = _resample_ticks_to_1m(seg)
        if bars_1m.empty:
            continue
        bars_1m = bars_1m.rename(columns={"dt_cst": "bar_end"})
        part = _attach_horizons(bars_1m, grp, EXPECTANCY_HORIZONS)
        if not part.empty:
            chunks.append(part)
    return pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()


def _curve_stats(sub: pd.DataFrame, *, tick: float, horizon: int) -> dict:
    col = f"future_{horizon}"
    if sub.empty or col not in sub.columns:
        return {
            "horizon": horizon,
            "n": 0,
            "avg_future_ticks": np.nan,
            "wr": np.nan,
            "net_at_3tick": np.nan,
            "net_at_2tick": np.nan,
        }
    ft = sub[col] / tick
    avg = float(ft.mean())
    return {
        "horizon": horizon,
        "n": len(sub),
        "avg_future_ticks": avg,
        "wr": float((ft > 0).mean()),
        "net_at_3tick": avg - COST_TICKS,
        "net_at_2tick": avg - COST_TICKS_ALT,
    }


def run_species_curve(
    *,
    symbol: str,
    bar_sec: int,
    start: datetime,
    end: datetime,
    event_type: str = "delta_div_short",
    session_close_only: bool = True,
    verbose: bool = True,
) -> pd.DataFrame:
    from strategies.pa_cta.symbol_config import resolve_symbol_profile

    profile = resolve_symbol_profile(symbol, ROOT)
    tick = float(profile["pricetick"])
    _, _, tick_cache = _load_tick_cache_for_symbol(symbol)

    if verbose:
        print(
            f"\n--- {symbol} bar={bar_sec}s pricetick={tick} "
            f"{start.date()} ~ {end.date()} ---",
            flush=True,
        )

    events, _ = run_study(
        symbol=symbol,
        bar_sec=bar_sec,
        start=start,
        end=end,
        tick=tick,
        verbose=verbose,
        save_outputs=False,
    )
    if events.empty:
        return pd.DataFrame()

    ev = events[events["event_type"] == event_type].copy()
    if session_close_only:
        ev["datetime"] = pd.to_datetime(ev["datetime"])
        ev = ev[ev["datetime"].apply(_in_close_session)]
    if ev.empty:
        if verbose:
            print(f"  {symbol}: 筛选后无 {event_type} 事件", flush=True)
        return pd.DataFrame()

    enriched = _enrich_horizons(ev, tick_cache)
    if enriched.empty:
        return pd.DataFrame()

    rows = [
        {
            "symbol": symbol,
            "bar_sec": bar_sec,
            "event_type": event_type,
            "segment": "close_1430_1500" if session_close_only else "all",
            "pricetick": tick,
            **_curve_stats(enriched, tick=tick, horizon=h),
        }
        for h in EXPECTANCY_HORIZONS
    ]
    curve = pd.DataFrame(rows)
    if verbose:
        _print_curve(curve)
    return curve


def _print_curve(curve: pd.DataFrame) -> None:
    if curve.empty:
        return
    sym = curve.iloc[0]["symbol"]
    bar = int(curve.iloc[0]["bar_sec"])
    n0 = int(curve.iloc[0]["n"])
    print(f"\n===== Expectancy Curve | {sym} | bar={bar}s | close | n={n0} =====")
    print(f"{'h(1m)':>6} {'N':>6} {'E[t]':>8} {'WR':>7} {'net@3':>8} {'net@2':>8}")
    for _, row in curve.iterrows():
        print(
            f"{int(row['horizon']):6d} {int(row['n']):6d} "
            f"{row['avg_future_ticks']:+8.2f} {row['wr']:7.1%} "
            f"{row['net_at_3tick']:+8.2f} {row['net_at_2tick']:+8.2f}"
        )
    best = curve.sort_values("avg_future_ticks", ascending=False).iloc[0]
    gate = curve[(curve["n"] >= 30) & (curve["net_at_2tick"] > 0)]
    print(
        f"\n峰值 horizon={int(best['horizon'])} E[t]={best['avg_future_ticks']:+.2f} "
        f"net@2={best['net_at_2tick']:+.2f}"
    )
    print("【gate】 net@2>0:", "通过" if not gate.empty else "无")
    if not gate.empty:
        for _, row in gate.iterrows():
            print(f"  h={int(row['horizon'])} net@2={row['net_at_2tick']:+.2f}")


def run_all_species(
    *,
    species: dict[str, int] | None = None,
    start: datetime,
    end: datetime,
    verbose: bool = True,
) -> pd.DataFrame:
    cfg = species or DEFAULT_SPECIES
    curves: list[pd.DataFrame] = []
    for sym, bar_sec in cfg.items():
        part = run_species_curve(
            symbol=sym,
            bar_sec=bar_sec,
            start=start,
            end=end,
            verbose=verbose,
        )
        if not part.empty:
            curves.append(part)
    if not curves:
        return pd.DataFrame()

    combined = pd.concat(curves, ignore_index=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUTPUT_DIR / "expectancy_curve_summary.csv"
    combined.to_csv(out, index=False, encoding="utf-8-sig")
    for sym in combined["symbol"].unique():
        sub = combined[combined["symbol"] == sym]
        sub.to_csv(
            OUTPUT_DIR / f"expectancy_curve_{sym.lower()}.csv",
            index=False,
            encoding="utf-8-sig",
        )

    if verbose:
        print("\n" + "=" * 72)
        print("三品种峰值对照（收盘段 delta_div_short）")
        print(f"{'sym':>4} {'bar':>4} {'peak_h':>7} {'E_peak':>8} {'net@2':>8} {'gate':>6}")
        for sym in combined["symbol"].unique():
            sub = combined[combined["symbol"] == sym].sort_values(
                "avg_future_ticks", ascending=False
            )
            b = sub.iloc[0]
            passed = sub[(sub["n"] >= 30) & (sub["net_at_2tick"] > 0)]
            gate = "Y" if not passed.empty else "N"
            print(
                f"{sym:>4} {int(b['bar_sec']):4d} {int(b['horizon']):7d} "
                f"{b['avg_future_ticks']:+8.2f} {b['net_at_2tick']:+8.2f} {gate:>6}"
            )
        print(f"\n输出: {out}")
        print("=" * 72)
    return combined


def main() -> None:
    parser = argparse.ArgumentParser(description="E4 full-horizon expectancy curve")
    parser.add_argument("--symbol", help="单品种；省略则跑 rb/ma/ta")
    parser.add_argument("--bar-sec", type=int, choices=(15, 30, 60, 120))
    parser.add_argument("--start", default="2025-01-01")
    parser.add_argument("--end", default="2026-06-30")
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d")
    end = datetime.strptime(args.end, "%Y-%m-%d")

    if args.symbol:
        bar = args.bar_sec or DEFAULT_SPECIES.get(args.symbol.lower(), 30)
        run_species_curve(symbol=args.symbol.lower(), bar_sec=bar, start=start, end=end)
    else:
        run_all_species(start=start, end=end)


if __name__ == "__main__":
    main()
