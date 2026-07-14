# -*- coding: utf-8
"""Tick 原生微观结构 Event Study（脱离 1m PA 形态）。

在可配置 tick 聚合窗口上检测订单流事件，用 1m close 计算 future_5/10/20。
不写策略、不模拟下单。

滚动窗口按 **固定 60 分钟** 历史缩放（非固定 bar 根数）；冷却 **2 分钟**。

事件（bar 收盘触发）::
  delta_div_long / delta_div_short / spread_div_* / exhaustion_* / exhaust_spread_*

用法::
  .venv\\Scripts\\python.exe experiments/E1_tick_native_micro.py --symbol rb
  .venv\\Scripts\\python.exe experiments/E1_tick_native_micro.py --bar-sec 60
  .venv\\Scripts\\python.exe experiments/E1_tick_native_micro.py --ladder
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.E1_failed_breakout import FWD_HORIZONS, MFE_WINDOW
from experiments.E1_pattern_delta_micro import _add_tick_micro_columns
from scripts.tq_tick_loader import (
    _load_tick_cache,
    _resample_ticks_to_1m,
    _slice_segment,
)
from tools.dominant_windows import build_segments_from_map
from tools.tq_paths import symbol_dir, tick_dir

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
LADDER_BAR_SECS = (15, 30, 60, 120)
LOOKBACK_MINUTES = 60
COOLDOWN_MINUTES = 2
COST_TICKS = 3.0
COST_TICKS_ALT = 2.0
PRICE_MIN_TICKS = 2.0
DELTA_FLOOR = 40.0


@dataclass(frozen=True)
class BarConfig:
    bar_sec: int
    roll_win: int
    cooldown_bars: int
    freq: str


def _bar_config(bar_sec: int) -> BarConfig:
    if bar_sec not in LADDER_BAR_SECS and bar_sec not in (15, 30, 60, 120):
        raise ValueError(f"bar_sec 须为 15/30/60/120，收到 {bar_sec}")
    roll_win = max(20, LOOKBACK_MINUTES * 60 // bar_sec)
    cooldown_bars = max(1, COOLDOWN_MINUTES * 60 // bar_sec)
    freq = f"{bar_sec}s" if bar_sec < 60 else ("1min" if bar_sec == 60 else "2min")
    return BarConfig(bar_sec=bar_sec, roll_win=roll_win, cooldown_bars=cooldown_bars, freq=freq)


def _resample_ticks_to_bars(df: pd.DataFrame, bar_sec: int) -> pd.DataFrame:
    cfg = _bar_config(bar_sec)
    if df.empty:
        return pd.DataFrame()
    work = df.sort_values("dt_cst").set_index("dt_cst")
    price = work["last_price"].astype(float)
    ohlc = price.resample(cfg.freq).ohlc().dropna(subset=["open"])
    delta = work["tick_delta"].resample(cfg.freq).sum()
    spread = work["spread1"].resample(cfg.freq).max()
    vol = work["tick_vol"].resample(cfg.freq).sum()
    imb = work["imbalance1"].resample(cfg.freq).last()
    out = ohlc.join(delta.rename("delta_bar")).join(spread.rename("spread_max"))
    out = out.join(vol.rename("volume_bar")).join(imb.rename("imbalance1"))
    out = out[out["volume_bar"] > 0].reset_index().rename(columns={"dt_cst": "bar_end"})
    out["price_chg"] = out["close"] - out["open"]
    out["price_range"] = out["high"] - out["low"]
    out["abs_delta"] = out["delta_bar"].abs()
    return out


def _resample_ticks_to_30s(df: pd.DataFrame) -> pd.DataFrame:
    """E3 等旧引用兼容。"""
    return _resample_ticks_to_bars(df, 30)


def _rolling_prior_quantile(s: pd.Series, q: float, win: int) -> pd.Series:
    return s.shift(1).rolling(win, min_periods=max(20, win // 4)).quantile(q)


def _prepare_features(bars: pd.DataFrame, cfg: BarConfig) -> pd.DataFrame:
    win = cfg.roll_win
    out = bars.copy()
    out["spread_p75"] = _rolling_prior_quantile(out["spread_max"], 0.75, win)
    out["abs_delta_p75"] = _rolling_prior_quantile(out["abs_delta"], 0.75, win)
    out["range_p25"] = _rolling_prior_quantile(out["price_range"], 0.25, win)
    out["abs_delta_p50"] = _rolling_prior_quantile(out["abs_delta"], 0.50, win)
    out["delta_thresh"] = np.maximum(out["abs_delta_p50"].fillna(DELTA_FLOOR), DELTA_FLOOR)
    out["spread_wide"] = out["spread_max"] >= out["spread_p75"]
    return out


def _detect_raw_events(bars: pd.DataFrame, *, tick: float) -> pd.DataFrame:
    price_min = PRICE_MIN_TICKS * tick
    rows: list[dict] = []

    for _, row in bars.iterrows():
        if pd.isna(row["delta_thresh"]) or pd.isna(row["spread_p75"]):
            continue
        dt = row["delta_thresh"]
        pc = float(row["price_chg"])
        d = float(row["delta_bar"])
        base = {
            "datetime": row["bar_end"],
            "entry_price": float(row["close"]),
            "delta_bar": d,
            "price_chg": pc,
            "price_range": float(row["price_range"]),
            "spread_max": float(row["spread_max"]),
            "spread_wide": bool(row["spread_wide"]),
            "imbalance1": float(row["imbalance1"]),
            "absorption": float(row["abs_delta"]) / max(float(row["price_range"]), tick),
        }

        div_long = pc <= -price_min and d >= dt
        div_short = pc >= price_min and d <= -dt
        exh_long = (
            float(row["abs_delta"]) >= float(row["abs_delta_p75"])
            and float(row["price_range"]) <= float(row["range_p25"])
            and d < 0
        )
        exh_short = (
            float(row["abs_delta"]) >= float(row["abs_delta_p75"])
            and float(row["price_range"]) <= float(row["range_p25"])
            and d > 0
        )

        if div_long:
            rows.append({**base, "event_type": "delta_div_long", "direction": 1})
            if row["spread_wide"]:
                rows.append({**base, "event_type": "spread_div_long", "direction": 1})
        if div_short:
            rows.append({**base, "event_type": "delta_div_short", "direction": -1})
            if row["spread_wide"]:
                rows.append({**base, "event_type": "spread_div_short", "direction": -1})
        if exh_long:
            rows.append({**base, "event_type": "exhaustion_long", "direction": 1})
            if row["spread_wide"]:
                rows.append({**base, "event_type": "exhaust_spread_long", "direction": 1})
        if exh_short:
            rows.append({**base, "event_type": "exhaustion_short", "direction": -1})
            if row["spread_wide"]:
                rows.append({**base, "event_type": "exhaust_spread_short", "direction": -1})

    return pd.DataFrame(rows)


def _apply_cooldown(events: pd.DataFrame, cfg: BarConfig) -> pd.DataFrame:
    if events.empty:
        return events
    events = events.sort_values(["event_type", "datetime"])
    keep: list[int] = []
    last_ts: dict[str, pd.Timestamp] = {}
    gap = pd.Timedelta(seconds=cfg.bar_sec * cfg.cooldown_bars)
    for idx, row in events.iterrows():
        et = row["event_type"]
        ts = pd.Timestamp(row["datetime"])
        if et in last_ts and ts - last_ts[et] < gap:
            continue
        keep.append(idx)
        last_ts[et] = ts
    return events.loc[keep].sort_values("datetime").reset_index(drop=True)


def _attach_forward(bars_1m: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    if events.empty or bars_1m.empty:
        return events

    b1 = bars_1m.sort_values("bar_end").reset_index(drop=True)
    ends = b1["bar_end"].tolist()
    closes = b1["close"].astype(float).to_numpy()
    highs = b1["high"].astype(float).to_numpy()
    lows = b1["low"].astype(float).to_numpy()
    max_k = max(*FWD_HORIZONS, MFE_WINDOW)

    out_rows: list[dict] = []
    for _, ev in events.iterrows():
        ts = pd.Timestamp(ev["datetime"])
        idx = int(np.searchsorted(ends, ts, side="right"))
        if idx + max_k >= len(b1):
            continue
        direction = int(ev["direction"])
        entry = float(ev["entry_price"])
        row = ev.to_dict()
        for k in FWD_HORIZONS:
            row[f"future_{k}"] = direction * (closes[idx + k - 1] - entry)
        mfe = mae = 0.0
        for j in range(MFE_WINDOW):
            bar_i = idx + j
            if direction > 0:
                mfe = max(mfe, highs[bar_i] - entry)
                mae = max(mae, entry - lows[bar_i])
            else:
                mfe = max(mfe, entry - lows[bar_i])
                mae = max(mae, highs[bar_i] - entry)
        row["mfe"] = mfe
        row["mae"] = mae
        out_rows.append(row)

    return pd.DataFrame(out_rows)


def _scan_segment(
    seg_tick: pd.DataFrame,
    *,
    yymm: str,
    tick: float,
    cfg: BarConfig,
) -> pd.DataFrame:
    seg_tick = _add_tick_micro_columns(seg_tick)
    bars = _resample_ticks_to_bars(seg_tick, cfg.bar_sec)
    min_len = cfg.roll_win + cfg.cooldown_bars + max(*FWD_HORIZONS, MFE_WINDOW) + 5
    if len(bars) < min_len:
        return pd.DataFrame()

    bars = _prepare_features(bars, cfg)
    bars_1m = _resample_ticks_to_1m(seg_tick)
    if bars_1m.empty:
        return pd.DataFrame()
    bars_1m = bars_1m.rename(columns={"dt_cst": "bar_end"})

    raw = _detect_raw_events(bars, tick=tick)
    if raw.empty:
        return pd.DataFrame()
    cooled = _apply_cooldown(raw, cfg)
    events = _attach_forward(bars_1m, cooled)
    if not events.empty:
        events["yymm"] = yymm
        events["bar_sec"] = cfg.bar_sec
    return events


def _stats(sub: pd.DataFrame, *, tick: float, cost: float = COST_TICKS) -> dict:
    if sub.empty:
        return {
            "n": 0,
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
        "avg_future_10": avg,
        "wr": float((f10 > 0).mean()),
        "avg_mfe": float(sub["mfe"].mean() / tick),
        "avg_mae": float(sub["mae"].mean() / tick),
        "net_after_cost": avg - cost,
        "net_at_2tick": avg - COST_TICKS_ALT,
    }


def _assign_session(dt: pd.Series) -> pd.Series:
    ts = pd.to_datetime(dt)

    def _label(m: int) -> str:
        if 540 <= m < 630:
            return "morning_0900_1030"
        if 630 <= m < 690:
            return "morning_1030_1130"
        if 810 <= m < 870:
            return "afternoon_1330_1430"
        if 870 <= m < 900:
            return "afternoon_1430_1500"
        if 1260 <= m < 1380:
            return "night_2100_2300"
        return "other"

    return ts.apply(lambda x: _label(x.hour * 60 + x.minute))


def _build_summary(events: pd.DataFrame, *, tick: float, bar_sec: int) -> pd.DataFrame:
    rows = []
    for et, sub in events.groupby("event_type"):
        rows.append({"bar_sec": bar_sec, "segment": et, **_stats(sub, tick=tick)})
    for et, sub in events.groupby("event_type"):
        sub = sub.copy()
        sub["session"] = _assign_session(sub["datetime"])
        for sess, g in sub.groupby("session"):
            if len(g) < 20:
                continue
            rows.append({"bar_sec": bar_sec, "segment": f"{et}|{sess}", **_stats(g, tick=tick)})
    return pd.DataFrame(rows).sort_values("avg_future_10", ascending=False)


def _load_tick_cache_for_symbol(symbol: str):
    from strategies.pa_cta.symbol_config import resolve_symbol_profile, resolve_tq_cbc_paths

    profile = resolve_symbol_profile(symbol, ROOT)
    _, prefix = resolve_tq_cbc_paths(profile)
    data_dir = symbol_dir(prefix)
    tick_root = tick_dir(prefix)
    rollover_map = pd.read_parquet(data_dir / "rollover_map.parquet")
    segments = build_segments_from_map(rollover_map)
    tick_cache = _load_tick_cache(tick_root, prefix)
    return prefix, segments, tick_cache


def run_study(
    *,
    symbol: str = "rb",
    bar_sec: int = 30,
    start: datetime | None = None,
    end: datetime | None = None,
    tick: float = 1.0,
    verbose: bool = True,
    save_outputs: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    cfg = _bar_config(bar_sec)
    prefix, segments, tick_cache = _load_tick_cache_for_symbol(symbol)

    start_ts = pd.Timestamp(start, tz="Asia/Shanghai") if start else None
    end_ts = pd.Timestamp(end, tz="Asia/Shanghai") if end else None

    if verbose:
        print(
            f"\n--- bar_sec={bar_sec}s | roll_win={cfg.roll_win} | cooldown={cfg.cooldown_bars} bars ---",
            flush=True,
        )

    chunks: list[pd.DataFrame] = []
    for seg in segments:
        yymm = seg["yymm"]
        if yymm not in tick_cache:
            continue
        seg_tick = _slice_segment(tick_cache[yymm], seg)
        if start_ts is not None:
            seg_tick = seg_tick[seg_tick["dt_cst"] >= start_ts]
        if end_ts is not None:
            seg_tick = seg_tick[seg_tick["dt_cst"] <= end_ts]
        if seg_tick.empty:
            continue
        if verbose:
            print(f"  scan {yymm} ticks={len(seg_tick):,} ...", flush=True)
        part = _scan_segment(seg_tick, yymm=yymm, tick=tick, cfg=cfg)
        if not part.empty:
            chunks.append(part)

    events = pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()
    summary = _build_summary(events, tick=tick, bar_sec=bar_sec) if not events.empty else pd.DataFrame()

    if save_outputs:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        suffix = f"_{bar_sec}s"
        ep = OUTPUT_DIR / f"tick_native_events{suffix}.csv"
        sp = OUTPUT_DIR / f"tick_native_summary{suffix}.csv"
        events.to_csv(ep, index=False, encoding="utf-8-sig")
        summary.to_csv(sp, index=False, encoding="utf-8-sig")
        if bar_sec == 30:
            events.to_csv(OUTPUT_DIR / "tick_native_events.csv", index=False, encoding="utf-8-sig")
            summary.to_csv(OUTPUT_DIR / "tick_native_summary.csv", index=False, encoding="utf-8-sig")
        if verbose:
            _print_report(symbol, prefix, bar_sec, events, summary, ep, sp)

    return events, summary


def run_ladder(
    *,
    symbol: str = "rb",
    start: datetime | None = None,
    end: datetime | None = None,
    tick: float = 1.0,
    bar_secs: tuple[int, ...] = LADDER_BAR_SECS,
) -> pd.DataFrame:
    summaries: list[pd.DataFrame] = []
    for sec in bar_secs:
        _, summary = run_study(
            symbol=symbol,
            bar_sec=sec,
            start=start,
            end=end,
            tick=tick,
            verbose=True,
            save_outputs=True,
        )
        if not summary.empty:
            summaries.append(summary)

    if not summaries:
        return pd.DataFrame()

    combined = pd.concat(summaries, ignore_index=True)
    focus_segments = (
        "delta_div_short",
        "delta_div_short|afternoon_1430_1500",
        "delta_div_short|morning_0900_1030",
        "delta_div_long",
    )
    ladder = combined[combined["segment"].isin(focus_segments)].copy()
    ladder = ladder.sort_values(["segment", "bar_sec"])

    lp = OUTPUT_DIR / "tick_native_ladder_summary.csv"
    ladder.to_csv(lp, index=False, encoding="utf-8-sig")
    _print_ladder(symbol, ladder, lp)
    return ladder


def _print_report(
    symbol: str,
    prefix: str,
    bar_sec: int,
    events: pd.DataFrame,
    summary: pd.DataFrame,
    ep: Path,
    sp: Path,
) -> None:
    print("\n===== Tick 原生微观 Event Study =====")
    print(f"品种: {symbol} ({prefix}) | bar={bar_sec}s | 事件: {len(events):,} | 成本: {COST_TICKS:.0f} tick")
    print("-" * 68)
    if summary.empty:
        print("无事件")
    else:
        base = summary[~summary["segment"].str.contains("|", regex=False)]
        print(f"{'EventType':<26} {'N':>7} {'f10':>8} {'WR':>7} {'MFE':>6} {'MAE':>6} {'net3':>7} {'net2':>7}")
        for _, row in base.sort_values("avg_future_10", ascending=False).iterrows():
            print(
                f"{row['segment']:<26} {int(row['n']):7d} {row['avg_future_10']:+8.2f} "
                f"{row['wr']:7.1%} {row['avg_mfe']:6.2f} {row['avg_mae']:6.2f} "
                f"{row['net_after_cost']:+7.2f} {row['net_at_2tick']:+7.2f}"
            )
    print(f"\n输出:\n  {ep}\n  {sp}")
    print("=" * 68)


def _print_ladder(symbol: str, ladder: pd.DataFrame, lp: Path) -> None:
    print("\n" + "=" * 78)
    print(f"===== Ladder 周期对照 | {symbol} | delta_div | 滚动={LOOKBACK_MINUTES}min =====")
    print("=" * 78)
    for seg in ladder["segment"].unique():
        block = ladder[ladder["segment"] == seg].sort_values("bar_sec")
        print(f"\n【{seg}】")
        print(f"{'bar':>5} {'N':>6} {'f10':>8} {'WR':>7} {'MFE':>6} {'MAE':>6} {'net@3':>8} {'net@2':>8}")
        for _, row in block.iterrows():
            print(
                f"{int(row['bar_sec']):5d} {int(row['n']):6d} {row['avg_future_10']:+8.2f} "
                f"{row['wr']:7.1%} {row['avg_mfe']:6.2f} {row['avg_mae']:6.2f} "
                f"{row['net_after_cost']:+8.2f} {row['net_at_2tick']:+8.2f}"
            )
    best = ladder[ladder["segment"] == "delta_div_short"].sort_values("avg_future_10", ascending=False)
    if not best.empty:
        b = best.iloc[0]
        print(f"\n全样本 f10 最优: bar={int(b['bar_sec'])}s f10={b['avg_future_10']:+.2f} net@2={b['net_at_2tick']:+.2f}")
    close = ladder[ladder["segment"] == "delta_div_short|afternoon_1430_1500"].sort_values(
        "avg_future_10", ascending=False
    )
    if not close.empty:
        c = close.iloc[0]
        print(
            f"收盘段最优: bar={int(c['bar_sec'])}s f10={c['avg_future_10']:+.2f} "
            f"net@2={c['net_at_2tick']:+.2f} n={int(c['n'])}"
        )
    passed = ladder[(ladder["n"] >= 30) & (ladder["net_at_2tick"] > 0)]
    print("\n【成本 gate】 net@2>0 且 n≥30:", "通过" if not passed.empty else "无")
    for _, row in passed.iterrows():
        print(f"  bar={int(row['bar_sec'])}s {row['segment']} net@2={row['net_at_2tick']:+.2f}")
    print(f"\n输出: {lp}")
    print("=" * 78)


def main() -> None:
    parser = argparse.ArgumentParser(description="Tick 原生微观 Event Study")
    parser.add_argument("--symbol", default="rb")
    parser.add_argument("--bar-sec", type=int, default=30, choices=(15, 30, 60, 120))
    parser.add_argument("--ladder", action="store_true", help="批量跑 15/30/60/120s")
    parser.add_argument("--start", default="2025-01-01")
    parser.add_argument("--end", default="2026-06-30")
    parser.add_argument("--tick", type=float, default=1.0)
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d")
    end = datetime.strptime(args.end, "%Y-%m-%d")

    if args.ladder:
        print(f"Ladder {args.symbol} {args.start} ~ {args.end} | bars={LADDER_BAR_SECS}")
        run_ladder(symbol=args.symbol, start=start, end=end, tick=args.tick)
    else:
        print(f"Tick-native study {args.symbol} bar={args.bar_sec}s {args.start} ~ {args.end}")
        run_study(symbol=args.symbol, bar_sec=args.bar_sec, start=start, end=end, tick=args.tick)


if __name__ == "__main__":
    main()
