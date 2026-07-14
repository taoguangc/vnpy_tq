# -*- coding: utf-8
"""P2 — delta_div_short × Compression 条件 Alpha（Last Chance）。

子样本：收盘段 14:30–15:00 | rb | bar=60s
条件：AFF compression / atr_ratio / ER 分层

Gate：n≥30 且 net@2>0 @ h=10；失败 → DEAD_FACTOR

用法::
  .venv\\Scripts\\python.exe experiments/P2_conditional_alpha.py --symbol rb
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

from experiments.E1_tick_native_micro import run_study
from experiments.E4_expectancy_curve import (
    EXPECTANCY_HORIZONS,
    _attach_horizons,
    _curve_stats,
    _enrich_horizons,
    _in_close_session,
)
from strategies.pa_cta.aff_gate import compute_aff_snapshot
from strategies.pa_cta.symbol_config import resolve_symbol_profile, resolve_tq_cbc_paths

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
BAR_SEC = 60
EVENT_TYPE = "delta_div_short"
MIN_N = 30
ATR_WINDOW = 14


def _load_1m_ohlc(symbol: str, start: datetime, end: datetime) -> pd.DataFrame:
    from scripts.tq_rollover_data import load_stitched_raw_bars
    from vnpy.trader.constant import Exchange

    profile = resolve_symbol_profile(symbol, ROOT)
    _, prefix = resolve_tq_cbc_paths(profile)
    exchange = profile.get("exchange", Exchange.SHFE)
    bars = load_stitched_raw_bars(prefix, exchange, start=start, end=end)
    if not bars:
        return pd.DataFrame()
    rows = [
        {
            "dt": b.datetime,
            "open": float(b.open_price),
            "high": float(b.high_price),
            "low": float(b.low_price),
            "close": float(b.close_price),
        }
        for b in bars
    ]
    df = pd.DataFrame(rows).sort_values("dt")
    if df["dt"].dt.tz is None:
        df["dt"] = df["dt"].dt.tz_localize("Asia/Shanghai")
    else:
        df["dt"] = df["dt"].dt.tz_convert("Asia/Shanghai")
    return df.set_index("dt")


def _resample_ohlc(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    o = df["open"].resample(rule).first()
    h = df["high"].resample(rule).max()
    lo = df["low"].resample(rule).min()
    c = df["close"].resample(rule).last()
    out = pd.DataFrame({"open": o, "high": h, "low": lo, "close": c}).dropna(subset=["close"])
    return out


def _atr_sma(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int) -> float:
    n = len(close)
    if n < period:
        return 0.0
    tr = np.empty(n, dtype=np.float64)
    tr[0] = high[0] - low[0]
    if n > 1:
        hl = high[1:] - low[1:]
        hc = np.abs(high[1:] - close[:-1])
        lc = np.abs(low[1:] - close[:-1])
        tr[1:] = np.maximum(hl, np.maximum(hc, lc))
    kernel = np.ones(period, dtype=np.float64) / period
    atr_tail = np.convolve(tr, kernel, mode="valid")
    return float(atr_tail[-1]) if len(atr_tail) else 0.0


def _attach_regime(events: pd.DataFrame, bars_5m: pd.DataFrame, bars_15m: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        return events

    rows: list[dict] = []
    idx5 = bars_5m.index
    idx15 = bars_15m.index

    for _, ev in events.iterrows():
        ts = pd.Timestamp(ev["datetime"])
        if ts.tzinfo is None:
            ts = ts.tz_localize("Asia/Shanghai")
        else:
            ts = ts.tz_convert("Asia/Shanghai")

        b15 = bars_15m.loc[:ts]
        b5 = bars_5m.loc[:ts]
        if len(b15) < 30 or len(b5) < ATR_WINDOW + 5:
            continue

        snap = compute_aff_snapshot(
            b15["close"].to_numpy(),
            b15["high"].to_numpy(),
            b15["low"].to_numpy(),
            b15["open"].to_numpy(),
        )
        atr_5 = _atr_sma(
            b5["high"].to_numpy(), b5["low"].to_numpy(), b5["close"].to_numpy(), ATR_WINDOW
        )
        atr_15 = _atr_sma(
            b15["high"].to_numpy(), b15["low"].to_numpy(), b15["close"].to_numpy(), ATR_WINDOW
        )
        atr_ratio = round(atr_5 / atr_15, 3) if atr_15 > 0 and atr_5 > 0 else 0.0

        row = ev.to_dict()
        row["compression_score"] = snap.compression_score
        row["alpha_strength"] = snap.alpha_strength
        row["env_score"] = snap.env_score
        row["er"] = snap.er
        row["atr_ratio"] = atr_ratio
        rows.append(row)

    return pd.DataFrame(rows)


def _strata_defs() -> list[tuple[str, str]]:
    return [
        ("ALL_close", "baseline"),
        ("COMP_ge_0.6", "compression_score >= 0.6"),
        ("COMP_eq_1.0", "compression_score >= 0.99"),
        ("COMP06_ATRlo", "compression_score >= 0.6 and atr_ratio < 0.70"),
        ("COMP06_ERlo", "compression_score >= 0.6 and er < 0.25"),
        ("ALPHA_lt_0.25", "alpha_strength < 0.25"),
    ]


def _pick_stratum(df: pd.DataFrame, name: str) -> pd.DataFrame:
    if name == "ALL_close":
        return df
    if name == "COMP_ge_0.6":
        return df[df["compression_score"] >= 0.6]
    if name == "COMP_eq_1.0":
        return df[df["compression_score"] >= 0.99]
    if name == "COMP06_ATRlo":
        return df[(df["compression_score"] >= 0.6) & (df["atr_ratio"] < 0.70)]
    if name == "COMP06_ERlo":
        return df[(df["compression_score"] >= 0.6) & (df["er"] < 0.25)]
    if name == "ALPHA_lt_0.25":
        return df[df["alpha_strength"] < 0.25]
    return pd.DataFrame()


def run_p2(
    *,
    symbol: str = "rb",
    start: datetime,
    end: datetime,
    verbose: bool = True,
) -> pd.DataFrame:
    profile = resolve_symbol_profile(symbol, ROOT)
    tick = float(profile["pricetick"])

    if verbose:
        print(f"P2 Conditional Alpha | {symbol} | {start.date()} ~ {end.date()}", flush=True)
        print("  [1/4] E1 events ...", flush=True)

    events, _ = run_study(
        symbol=symbol,
        bar_sec=BAR_SEC,
        start=start,
        end=end,
        tick=tick,
        verbose=False,
        save_outputs=False,
    )
    if events.empty:
        raise ValueError("无 tick-native 事件")

    ev = events[events["event_type"] == EVENT_TYPE].copy()
    ev["datetime"] = pd.to_datetime(ev["datetime"])
    ev = ev[ev["datetime"].apply(_in_close_session)]

    if verbose:
        print(f"       收盘 {EVENT_TYPE}: {len(ev)}", flush=True)
        print("  [2/4] 1m/5m/15m + AFF context ...", flush=True)

    ohlc_1m = _load_1m_ohlc(symbol, start, end)
    if ohlc_1m.empty:
        raise ValueError("无 1m OHLC")
    bars_5m = _resample_ohlc(ohlc_1m, "5min")
    bars_15m = _resample_ohlc(ohlc_1m, "15min")

    enriched_ctx = _attach_regime(ev, bars_5m, bars_15m)
    if verbose:
        print(f"       带 context 事件: {len(enriched_ctx)}", flush=True)
        print("  [3/4] forward horizons ...", flush=True)

    from experiments.E1_tick_native_micro import _load_tick_cache_for_symbol

    _, _, tick_cache = _load_tick_cache_for_symbol(symbol)
    enriched = _enrich_horizons(enriched_ctx, tick_cache)
    if enriched.empty:
        raise ValueError("forward 标注后无事件")

    summary_rows: list[dict] = []
    for seg_name, _desc in _strata_defs():
        sub = _pick_stratum(enriched, seg_name)
        for h in EXPECTANCY_HORIZONS:
            st = _curve_stats(sub, tick=tick, horizon=h)
            summary_rows.append(
                {
                    "symbol": symbol,
                    "segment": seg_name,
                    "horizon": h,
                    "pricetick": tick,
                    **st,
                }
            )

    summary = pd.DataFrame(summary_rows)
    h10 = summary[summary["horizon"] == 10].copy()
    passed = h10[(h10["n"] >= MIN_N) & (h10["net_at_2tick"] > 0)]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUTPUT_DIR / f"p2_conditional_alpha_{symbol}.csv"
    summary.to_csv(out, index=False, encoding="utf-8-sig")
    enriched.to_csv(
        OUTPUT_DIR / f"p2_conditional_events_{symbol}.csv",
        index=False,
        encoding="utf-8-sig",
    )

    if verbose:
        print("  [4/4] Gate")
        print("\n===== P2 Conditional Alpha | h=10 =====")
        print(f"{'Segment':<16} {'N':>6} {'E[t]':>8} {'WR':>7} {'net@3':>8} {'net@2':>8}")
        for _, row in h10.sort_values("avg_future_ticks", ascending=False).iterrows():
            flag = " *" if row["n"] >= MIN_N and row["net_at_2tick"] > 0 else ""
            print(
                f"{row['segment']:<16} {int(row['n']):6d} "
                f"{row['avg_future_ticks']:+8.2f} {row['wr']:7.1%} "
                f"{row['net_at_3tick']:+8.2f} {row['net_at_2tick']:+8.2f}{flag}"
            )
        best = h10.sort_values("avg_future_ticks", ascending=False).iloc[0]
        print(
            f"\n峰值分层: {best['segment']} E[t]={best['avg_future_ticks']:+.2f} "
            f"net@2={best['net_at_2tick']:+.2f} n={int(best['n'])}"
        )
        if passed.empty:
            print("\n【Gate】 net@2>0 且 n≥30: **无**")
            print("【Verdict】 DEAD_FACTOR — 归档 delta_div_short，停止后续研究")
        else:
            print("\n【Gate】 通过:")
            for _, row in passed.iterrows():
                print(f"  {row['segment']} net@2={row['net_at_2tick']:+.2f} n={int(row['n'])}")
            print("【Verdict】 条件 Alpha 待扩展验证（非 DEAD）")
        print(f"\n输出: {out}")
        print("=" * 60)

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="P2 conditional alpha")
    parser.add_argument("--symbol", default="rb")
    parser.add_argument("--start", default="2025-01-01")
    parser.add_argument("--end", default="2026-06-30")
    args = parser.parse_args()
    run_p2(
        symbol=args.symbol.lower(),
        start=datetime.strptime(args.start, "%Y-%m-%d"),
        end=datetime.strptime(args.end, "%Y-%m-%d"),
    )


if __name__ == "__main__":
    main()
