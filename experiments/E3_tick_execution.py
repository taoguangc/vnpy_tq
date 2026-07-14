# -*- coding: utf-8
"""E3 — Tick 执行方式对照（验证用，不写策略）。

针对 E1 tick-native 筛出的子样本，用 tick 逐笔模拟不同入场执行。

执行方式（direction=-1 做空）::
  market_close / market_ask / stop_break_low / confirm_{bar_sec}s

用法::
  .venv\\Scripts\\python.exe experiments/E3_tick_execution.py \\
      --input experiments/output/tick_native_events_60s.csv --bar-sec 60
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.E1_failed_breakout import FWD_HORIZONS, MFE_WINDOW
from experiments.E1_pattern_delta_micro import _add_tick_micro_columns
from experiments.E1_tick_native_micro import _load_tick_cache_for_symbol, _resample_ticks_to_bars
from scripts.tq_tick_loader import _resample_ticks_to_1m

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
DEFAULT_EVENTS = OUTPUT_DIR / "tick_native_events.csv"
STOP_WAIT_SEC = 90


def _in_session(ts: pd.Timestamp) -> bool:
    m = ts.hour * 60 + ts.minute
    return 870 <= m < 900


def _stats(sub: pd.DataFrame, *, tick: float, cost: float) -> dict:
    if sub.empty:
        return {
            "n": 0,
            "fill_rate": np.nan,
            "avg_future_10": np.nan,
            "wr": np.nan,
            "avg_mfe": np.nan,
            "avg_mae": np.nan,
            "net_after_cost": np.nan,
            "net_at_2tick": np.nan,
        }
    f10 = sub["future_10"] / tick
    avg = float(f10.mean())
    return {
        "n": len(sub),
        "fill_rate": np.nan,
        "avg_future_10": avg,
        "wr": float((f10 > 0).mean()),
        "avg_mfe": float(sub["mfe"].mean() / tick),
        "avg_mae": float(sub["mae"].mean() / tick),
        "net_after_cost": avg - cost,
        "net_at_2tick": avg - 2.0,
    }


def _forward_from_entry(
    bars_1m: pd.DataFrame,
    entry_ts: pd.Timestamp,
    entry_price: float,
    direction: int,
) -> dict | None:
    b1 = bars_1m.sort_values("bar_end").reset_index(drop=True)
    ends = pd.to_datetime(b1["bar_end"]).tolist()
    idx = int(np.searchsorted(ends, entry_ts, side="right"))
    max_k = max(*FWD_HORIZONS, MFE_WINDOW)
    if idx + max_k > len(b1):
        return None

    closes = b1["close"].astype(float).to_numpy()
    highs = b1["high"].astype(float).to_numpy()
    lows = b1["low"].astype(float).to_numpy()

    out: dict = {"entry_time": entry_ts, "entry_price": entry_price}
    for k in FWD_HORIZONS:
        out[f"future_{k}"] = direction * (closes[idx + k - 1] - entry_price)
    mfe = mae = 0.0
    for j in range(MFE_WINDOW):
        bar_i = idx + j
        if direction > 0:
            mfe = max(mfe, highs[bar_i] - entry_price)
            mae = max(mae, entry_price - lows[bar_i])
        else:
            mfe = max(mfe, entry_price - lows[bar_i])
            mae = max(mae, highs[bar_i] - entry_price)
    out["mfe"] = mfe
    out["mae"] = mae
    return out


def _signal_bar(ticks: pd.DataFrame, signal_ts: pd.Timestamp, *, bar_sec: int) -> dict | None:
    bars = _resample_ticks_to_bars(ticks, bar_sec)
    if bars.empty:
        return None
    hit = bars[bars["bar_end"] == signal_ts]
    if hit.empty:
        bars = bars.sort_values("bar_end")
        idx = bars["bar_end"].searchsorted(signal_ts)
        if idx >= len(bars):
            return None
        row = bars.iloc[idx if bars.iloc[idx]["bar_end"] == signal_ts else max(0, idx - 1)]
    else:
        row = hit.iloc[0]
    w = ticks[
        (ticks["dt_cst"] > signal_ts - pd.Timedelta(seconds=bar_sec))
        & (ticks["dt_cst"] <= signal_ts)
    ]
    last = w.iloc[-1] if not w.empty else ticks[ticks["dt_cst"] <= signal_ts].iloc[-1]
    return {
        "open": float(row["open"]),
        "high": float(row["high"]),
        "low": float(row["low"]),
        "close": float(row["close"]),
        "ask": float(last["ask_price1"]) if float(last["ask_price1"]) > 0 else float(row["close"]),
        "next_end": signal_ts + pd.Timedelta(seconds=bar_sec),
    }


def _simulate_modes(
    ticks: pd.DataFrame,
    bars_1m: pd.DataFrame,
    *,
    signal_ts: pd.Timestamp,
    direction: int,
    bar_sec: int,
) -> list[dict]:
    sig = _signal_bar(ticks, signal_ts, bar_sec=bar_sec)
    if sig is None:
        return []

    confirm_mode = f"confirm_{bar_sec}s"
    base = {"signal_time": signal_ts, "direction": direction, "bar_sec": bar_sec}
    rows: list[dict] = []

    fwd = _forward_from_entry(bars_1m, signal_ts, sig["close"], direction)
    if fwd:
        rows.append({**base, "exec_mode": "market_close", **fwd})

    fwd = _forward_from_entry(bars_1m, signal_ts, sig["ask"], direction)
    if fwd:
        rows.append({**base, "exec_mode": "market_ask", **fwd})

    after = ticks[
        (ticks["dt_cst"] > signal_ts)
        & (ticks["dt_cst"] <= signal_ts + pd.Timedelta(seconds=STOP_WAIT_SEC))
    ]
    stop_px = sig["low"]
    filled = False
    for _, tk in after.iterrows():
        lp = float(tk["last_price"])
        if lp <= stop_px:
            fill = min(lp, stop_px)
            entry_ts = pd.Timestamp(tk["dt_cst"])
            fwd = _forward_from_entry(bars_1m, entry_ts, fill, direction)
            if fwd:
                rows.append({**base, "exec_mode": "stop_break_low", **fwd})
            filled = True
            break
    if not filled:
        rows.append({
            **base,
            "exec_mode": "stop_break_low",
            "entry_time": pd.NaT,
            "entry_price": np.nan,
            "future_10": np.nan,
            "mfe": np.nan,
            "mae": np.nan,
            "filled": False,
        })

    bars_sig = _resample_ticks_to_bars(ticks, bar_sec)
    nxt = bars_sig[bars_sig["bar_end"] == sig["next_end"]]
    if not nxt.empty and float(nxt.iloc[0]["close"]) < sig["close"]:
        entry_px = float(nxt.iloc[0]["close"])
        fwd = _forward_from_entry(bars_1m, sig["next_end"], entry_px, direction)
        if fwd:
            rows.append({**base, "exec_mode": confirm_mode, **fwd})
    else:
        rows.append({
            **base,
            "exec_mode": confirm_mode,
            "entry_time": pd.NaT,
            "entry_price": np.nan,
            "future_10": np.nan,
            "mfe": np.nan,
            "mae": np.nan,
            "filled": False,
        })

    return rows


def run_e3(
    *,
    symbol: str = "rb",
    events_path: Path = DEFAULT_EVENTS,
    event_type: str = "delta_div_short",
    bar_sec: int = 30,
    session_only: bool = True,
    tick: float = 1.0,
    cost_ticks: float = 3.0,
    verbose: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not events_path.exists():
        raise FileNotFoundError(f"缺少 {events_path}，请先跑 E1_tick_native_micro.py")

    raw = pd.read_csv(events_path)
    raw["datetime"] = pd.to_datetime(raw["datetime"])
    ev = raw[raw["event_type"] == event_type].copy()
    if session_only:
        ev = ev[ev["datetime"].apply(_in_session)]
    if ev.empty:
        raise ValueError("筛选后无事件")

    prefix, _, tick_cache = _load_tick_cache_for_symbol(symbol)

    all_rows: list[dict] = []
    for yymm, grp in ev.groupby("yymm"):
        yymm = str(yymm)
        if yymm not in tick_cache:
            continue
        seg = tick_cache[yymm].copy()
        seg = _add_tick_micro_columns(seg)
        bars_1m = _resample_ticks_to_1m(seg).rename(columns={"dt_cst": "bar_end"})

        for _, row in grp.iterrows():
            ts = pd.Timestamp(row["datetime"])
            if ts.tzinfo is None:
                ts = ts.tz_localize("Asia/Shanghai")
            t0 = ts - pd.Timedelta(minutes=5)
            t1 = ts + pd.Timedelta(minutes=MFE_WINDOW + 2)
            window = seg[(seg["dt_cst"] >= t0) & (seg["dt_cst"] <= t1)]
            if window.empty:
                continue
            all_rows.extend(
                _simulate_modes(
                    window,
                    bars_1m,
                    signal_ts=ts,
                    direction=int(row["direction"]),
                    bar_sec=bar_sec,
                )
            )

    detail = pd.DataFrame(all_rows)
    summary_rows: list[dict] = []
    n_signal = len(ev)
    for mode, sub in detail.groupby("exec_mode"):
        filled = sub[sub["future_10"].notna()]
        fill_rate = len(filled) / n_signal if n_signal else np.nan
        st = _stats(filled, tick=tick, cost=cost_ticks)
        st["exec_mode"] = mode
        st["fill_rate"] = fill_rate
        st["bar_sec"] = bar_sec
        st["symbol"] = symbol
        summary_rows.append(st)

    summary = pd.DataFrame(summary_rows).sort_values("avg_future_10", ascending=False)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = f"_{symbol.lower()}_{bar_sec}s"
    dp = OUTPUT_DIR / f"e3_execution_detail{suffix}.csv"
    sp = OUTPUT_DIR / f"e3_execution_summary{suffix}.csv"
    detail.to_csv(dp, index=False, encoding="utf-8-sig")
    summary.to_csv(sp, index=False, encoding="utf-8-sig")

    if verbose:
        _print_report(symbol, prefix, event_type, bar_sec, n_signal, summary, cost_ticks, dp, sp)

    return summary, detail


def _print_report(
    symbol: str,
    prefix: str,
    event_type: str,
    bar_sec: int,
    n_signal: int,
    summary: pd.DataFrame,
    cost: float,
    dp: Path,
    sp: Path,
) -> None:
    print("\n===== E3 Tick 执行对照（验证） =====")
    print(f"品种: {symbol} ({prefix}) | 子样本: {event_type} | bar={bar_sec}s | 14:30–15:00 | 信号: {n_signal}")
    print(f"成本: @3 tick / @2 tick（自 entry 计 future_10）")
    print("-" * 80)
    print(
        f"{'ExecMode':<18} {'Fill%':>6} {'N':>5} {'f10':>8} {'WR':>7} "
        f"{'MFE':>6} {'MAE':>6} {'net@3':>8} {'net@2':>8}"
    )
    for _, row in summary.iterrows():
        print(
            f"{row['exec_mode']:<18} {row['fill_rate']:6.1%} {int(row['n']):5d} "
            f"{row['avg_future_10']:+8.2f} {row['wr']:7.1%} "
            f"{row['avg_mfe']:6.2f} {row['avg_mae']:6.2f} "
            f"{row['net_after_cost']:+8.2f} {row['net_at_2tick']:+8.2f}"
        )
    base = summary[summary["exec_mode"] == "market_close"]
    if not base.empty:
        b = base.iloc[0]
        print(
            f"\nE1 基线 market_close: f10={b['avg_future_10']:+.2f} "
            f"net@3={b['net_after_cost']:+.2f} net@2={b['net_at_2tick']:+.2f}"
        )
    passed = summary[(summary["n"] >= 30) & (summary["net_at_2tick"] > 0)]
    print("\n【成本 gate】 net@2>0 且 n≥30:", "通过" if not passed.empty else "无")
    for _, row in passed.iterrows():
        print(f"  {row['exec_mode']}: net@2={row['net_at_2tick']:+.2f}")
    print(f"\n输出:\n  {dp}\n  {sp}")
    print("=" * 80)


def main() -> None:
    parser = argparse.ArgumentParser(description="E3 tick 执行对照")
    parser.add_argument("--symbol", default="rb")
    parser.add_argument("--input", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--event-type", default="delta_div_short")
    parser.add_argument("--bar-sec", type=int, default=30, choices=(15, 30, 60, 120))
    parser.add_argument("--tick", type=float, default=None, help="默认从 symbol profile 读取 pricetick")
    parser.add_argument("--cost-ticks", type=float, default=3.0)
    args = parser.parse_args()

    tick = args.tick
    if tick is None:
        from strategies.pa_cta.symbol_config import resolve_symbol_profile

        tick = float(resolve_symbol_profile(args.symbol, ROOT)["pricetick"])

    run_e3(
        symbol=args.symbol,
        events_path=args.input,
        event_type=args.event_type,
        bar_sec=args.bar_sec,
        tick=tick,
        cost_ticks=args.cost_ticks,
    )


if __name__ == "__main__":
    main()
