# -*- coding: utf-8
"""形态 + Tick 微观结构 Event Study（Delta / 1档盘口）。

在 E1 价格行为事件上附加 tick 级特征，检验微观结构能否分层 edge。
不写策略、不模拟下单。

形态（--pattern）::
  failed_breakout   E1 假突破（上/下）
  breakout_success  成功突破（收盘站上/跌破，且非假突破）
  all               两者

Tick 特征（信号 1m bar 收盘时刻）::
  delta_1m          信号分钟内 Tick Delta 合计
  delta_30s         收盘前 30s Delta
  delta_60s         收盘前 60s Delta
  imbalance1        末 tick 买卖一量失衡 (bid-ask)/(bid+ask)
  spread1_ticks     末 tick 买卖价差 / tick
  absorption        |delta_1m| / 信号 bar range（越大=成交多但走得少）

Delta 分类（Lee-Ready 简化，与 smc_orderflow_vwap 一致）::

  价涨 → +volume；价跌 → -volume；不变则按买卖一价推断

输出::
  experiments/output/pattern_delta_events.csv
  experiments/output/pattern_delta_summary.csv
  experiments/output/delta_strata_summary.csv

用法::
  .venv\\Scripts\\python.exe experiments/E1_pattern_delta_micro.py --symbol rb
  .venv\\Scripts\\python.exe experiments/E1_pattern_delta_micro.py --symbol ma \\
      --start 2025-01-01 --end 2026-06-30
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

from experiments.E1_failed_breakout import FWD_HORIZONS, MFE_WINDOW
from scripts.tq_tick_loader import (
    _load_tick_cache,
    _resample_ticks_to_1m,
    _slice_segment,
)
from tools.dominant_windows import build_segments_from_map
from tools.tq_paths import symbol_dir, tick_dir

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
LOOKBACK = 20
COST_TICKS = 3.0


def _add_tick_micro_columns(df: pd.DataFrame) -> pd.DataFrame:
    """向量化 Tick Delta + 1档失衡（按 smc_orderflow 规则）。"""
    out = df.sort_values("dt_cst").reset_index(drop=True)
    lp = out["last_price"].astype(float).to_numpy()
    vol_raw = out["volume"].astype(float).diff().fillna(out["volume"]).clip(lower=0).to_numpy()
    bid = out["bid_price1"].astype(float).to_numpy()
    ask = out["ask_price1"].astype(float).to_numpy()
    bidv = out["bid_volume1"].astype(float).to_numpy()
    askv = out["ask_volume1"].astype(float).to_numpy()

    n = len(out)
    delta = np.zeros(n, dtype=np.float64)
    for i in range(1, n):
        v = vol_raw[i]
        if v <= 0:
            continue
        if lp[i] > lp[i - 1]:
            delta[i] = v
        elif lp[i] < lp[i - 1]:
            delta[i] = -v
        elif ask[i] > 0 and lp[i] >= ask[i]:
            delta[i] = v
        elif bid[i] > 0 and lp[i] <= bid[i]:
            delta[i] = -v

    out["tick_vol"] = vol_raw
    out["tick_delta"] = delta
    denom = np.maximum(bidv + askv, 0.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        imb = np.where(denom > 0, (bidv - askv) / denom, 0.0)
    out["imbalance1"] = np.nan_to_num(imb, nan=0.0)
    out["spread1"] = ask - bid
    return out


def _prepare_1m(feat: pd.DataFrame) -> pd.DataFrame:
    h = feat["high"].astype(float)
    lo = feat["low"].astype(float)
    o = feat["open"].astype(float)
    c = feat["close"].astype(float)
    out = feat.copy()
    out["prev_20_high"] = h.shift(1).rolling(LOOKBACK, min_periods=LOOKBACK).max()
    out["prev_20_low"] = lo.shift(1).rolling(LOOKBACK, min_periods=LOOKBACK).min()
    out["body"] = (c - o).abs()
    rng = (h - lo).clip(lower=1e-9)
    out["range"] = rng
    out["body_ratio"] = out["body"] / rng
    out["upper_wick"] = h - np.maximum(o, c)
    out["lower_wick"] = np.minimum(o, c) - lo
    return out


def _failed_breakout_up(row: pd.Series) -> bool:
    ph = row["prev_20_high"]
    if pd.isna(ph):
        return False
    return (
        row["high"] > ph
        and row["close"] < ph
        and row["upper_wick"] > row["body"]
    )


def _failed_breakdown_down(row: pd.Series) -> bool:
    pl = row["prev_20_low"]
    if pd.isna(pl):
        return False
    return (
        row["low"] < pl
        and row["close"] > pl
        and row["lower_wick"] > row["body"]
    )


def _breakout_success_up(row: pd.Series) -> bool:
    ph = row["prev_20_high"]
    if pd.isna(ph):
        return False
    return row["high"] > ph and row["close"] > ph and not _failed_breakout_up(row)


def _breakout_success_down(row: pd.Series) -> bool:
    pl = row["prev_20_low"]
    if pd.isna(pl):
        return False
    return row["low"] < pl and row["close"] < pl and not _failed_breakdown_down(row)


def _classify_bar(row: pd.Series, pattern: str) -> list[tuple[str, int]]:
    out: list[tuple[str, int]] = []
    if pattern in ("failed_breakout", "all"):
        if _failed_breakout_up(row):
            out.append(("failed_breakout_up", -1))
        if _failed_breakdown_down(row):
            out.append(("failed_breakdown_down", 1))
    if pattern in ("breakout_success", "all"):
        if _breakout_success_up(row):
            out.append(("breakout_success_up", 1))
        if _breakout_success_down(row):
            out.append(("breakout_success_down", -1))
    return out


def _micro_at_bar(ticks: pd.DataFrame, bar_end: pd.Timestamp, *, bar_range: float) -> dict:
    """信号 1m bar 收盘时刻的 tick 微观特征。"""
    if ticks.empty:
        return {
            "delta_1m": 0.0,
            "delta_30s": 0.0,
            "delta_60s": 0.0,
            "imbalance1": 0.0,
            "spread1_ticks": 0.0,
            "absorption": 0.0,
        }

    bar_start = bar_end - pd.Timedelta(minutes=1)
    w60 = ticks[(ticks["dt_cst"] > bar_end - pd.Timedelta(seconds=60)) & (ticks["dt_cst"] <= bar_end)]
    w30 = ticks[(ticks["dt_cst"] > bar_end - pd.Timedelta(seconds=30)) & (ticks["dt_cst"] <= bar_end)]
    w1m = ticks[(ticks["dt_cst"] > bar_start) & (ticks["dt_cst"] <= bar_end)]

    last = ticks.iloc[-1]
    delta_1m = float(w1m["tick_delta"].sum()) if not w1m.empty else 0.0
    absorption = abs(delta_1m) / max(bar_range, 1e-9)

    return {
        "delta_1m": delta_1m,
        "delta_30s": float(w30["tick_delta"].sum()) if not w30.empty else 0.0,
        "delta_60s": float(w60["tick_delta"].sum()) if not w60.empty else 0.0,
        "imbalance1": float(last["imbalance1"]),
        "spread1_ticks": float(last["spread1"]),
        "absorption": absorption,
    }


def _forward_from_bars(bars: pd.DataFrame, i: int, direction: int) -> dict:
    close0 = float(bars.iloc[i]["close"])
    one_r = float(bars.iloc[i]["range"])
    fwd = {}
    for k in FWD_HORIZONS:
        fwd[f"future_{k}"] = direction * (float(bars.iloc[i + k]["close"]) - close0)
    mfe = mae = 0.0
    for j in range(1, MFE_WINDOW + 1):
        bar = bars.iloc[i + j]
        if direction > 0:
            mfe = max(mfe, float(bar["high"]) - close0)
            mae = max(mae, close0 - float(bar["low"]))
        else:
            mfe = max(mfe, close0 - float(bar["low"]))
            mae = max(mae, float(bar["high"]) - close0)
    return {
        **fwd,
        "mfe": mfe,
        "mae": mae,
        "one_r": one_r,
        "mfe_gt_1r": int(mfe > one_r),
    }


def _scan_symbol(
    prefix: str,
    *,
    pattern: str,
    start: pd.Timestamp | None,
    end: pd.Timestamp | None,
    tick_size: float,
) -> pd.DataFrame:
    data_dir = symbol_dir(prefix)
    tick_root = tick_dir(prefix)
    rollover_map = pd.read_parquet(data_dir / "rollover_map.parquet")
    segments = build_segments_from_map(rollover_map)
    tick_cache = _load_tick_cache(tick_root, prefix)

    rows: list[dict] = []
    max_k = max(*FWD_HORIZONS, MFE_WINDOW)

    for seg in segments:
        yymm = seg["yymm"]
        if yymm not in tick_cache:
            continue
        seg_tick = _slice_segment(tick_cache[yymm], seg)
        if seg_tick.empty:
            continue
        seg_tick = _add_tick_micro_columns(seg_tick)
        bars = _resample_ticks_to_1m(seg_tick)
        if bars.empty:
            continue
        bars = bars.rename(columns={"dt_cst": "bar_end"})
        bars = _prepare_1m(bars)

        if start is not None:
            bars = bars[bars["bar_end"] >= start]
        if end is not None:
            bars = bars[bars["bar_end"] <= end]
        if len(bars) < LOOKBACK + max_k + 5:
            continue

        ticks = seg_tick
        if start is not None:
            ticks = ticks[ticks["dt_cst"] >= start - pd.Timedelta(minutes=5)]
        if end is not None:
            ticks = ticks[ticks["dt_cst"] <= end + pd.Timedelta(minutes=MFE_WINDOW + 1)]

        bar_ends = bars["bar_end"].tolist()
        for i in range(LOOKBACK, len(bars) - max_k):
            row = bars.iloc[i]
            bar_end = pd.Timestamp(row["bar_end"])
            for pname, direction in _classify_bar(row, pattern):
                micro = _micro_at_bar(
                    ticks[(ticks["dt_cst"] <= bar_end) & (ticks["dt_cst"] > bar_end - pd.Timedelta(minutes=2))],
                    bar_end,
                    bar_range=float(row["range"]),
                )
                fwd = _forward_from_bars(bars, i, direction)
                aligned_delta = direction * micro["delta_30s"]
                rows.append(
                    {
                        "datetime": bar_end,
                        "yymm": yymm,
                        "pattern": pname,
                        "direction": direction,
                        "delta_1m": micro["delta_1m"],
                        "delta_30s": micro["delta_30s"],
                        "delta_60s": micro["delta_60s"],
                        "aligned_delta_30s": aligned_delta,
                        "imbalance1": micro["imbalance1"],
                        "spread1_ticks": micro["spread1_ticks"] / tick_size,
                        "absorption": micro["absorption"],
                        **fwd,
                    }
                )

    return pd.DataFrame(rows)


def _stats(sub: pd.DataFrame, *, tick: float) -> dict:
    if sub.empty:
        return {"n": 0, "avg_future_10": np.nan, "wr": np.nan, "avg_mfe": np.nan, "avg_mae": np.nan}
    f10 = sub["future_10"] / tick
    return {
        "n": len(sub),
        "avg_future_10": float(f10.mean()),
        "wr": float((f10 > 0).mean()),
        "avg_mfe": float(sub["mfe"].mean() / tick),
        "avg_mae": float(sub["mae"].mean() / tick),
        "net_after_cost": float(f10.mean()) - COST_TICKS,
    }


def _build_summaries(events: pd.DataFrame, *, tick: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    pat_rows = []
    for pname, sub in events.groupby("pattern"):
        pat_rows.append({"segment": pname, **_stats(sub, tick=tick)})
    pattern_summary = pd.DataFrame(pat_rows)

    strata_rows = []
    for pname, sub in events.groupby("pattern"):
        strata_rows.append({"segment": f"{pname}|ALL", **_stats(sub, tick=tick)})
        if len(sub) >= 20:
            med = sub["aligned_delta_30s"].median()
            strata_rows.append(
                {"segment": f"{pname}|delta30_aligned>0", **_stats(sub[sub["aligned_delta_30s"] > 0], tick=tick)}
            )
            strata_rows.append(
                {"segment": f"{pname}|delta30_aligned<=0", **_stats(sub[sub["aligned_delta_30s"] <= med], tick=tick)}
            )
            strata_rows.append(
                {"segment": f"{pname}|delta30_aligned>{med}", **_stats(sub[sub["aligned_delta_30s"] > med], tick=tick)}
            )
        if len(sub) >= 20:
            strata_rows.append(
                {"segment": f"{pname}|imbalance_bid_heavy", **_stats(sub[sub["imbalance1"] > 0.1], tick=tick)}
            )
            strata_rows.append(
                {"segment": f"{pname}|imbalance_ask_heavy", **_stats(sub[sub["imbalance1"] < -0.1], tick=tick)}
            )
        if len(sub) >= 20:
            hi_abs = sub["absorption"].quantile(0.75)
            strata_rows.append(
                {"segment": f"{pname}|high_absorption", **_stats(sub[sub["absorption"] >= hi_abs], tick=tick)}
            )

    strata_summary = pd.DataFrame(strata_rows)
    return pattern_summary, strata_summary


def run_study(
    *,
    symbol: str = "rb",
    pattern: str = "all",
    start: datetime | None = None,
    end: datetime | None = None,
    tick: float = 1.0,
    verbose: bool = True,
) -> pd.DataFrame:
    from strategies.pa_cta.symbol_config import resolve_symbol_profile, resolve_tq_cbc_paths

    profile = resolve_symbol_profile(symbol, ROOT)
    _, prefix = resolve_tq_cbc_paths(profile)

    start_ts = pd.Timestamp(start, tz="Asia/Shanghai") if start else None
    end_ts = pd.Timestamp(end, tz="Asia/Shanghai") if end else None

    events = _scan_symbol(prefix, pattern=pattern, start=start_ts, end=end_ts, tick_size=tick)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    ep = OUTPUT_DIR / "pattern_delta_events.csv"
    events.to_csv(ep, index=False, encoding="utf-8-sig")

    pattern_summary, strata_summary = _build_summaries(events, tick=tick)
    sp = OUTPUT_DIR / "pattern_delta_summary.csv"
    tp = OUTPUT_DIR / "delta_strata_summary.csv"
    pattern_summary.to_csv(sp, index=False, encoding="utf-8-sig")
    strata_summary.to_csv(tp, index=False, encoding="utf-8-sig")

    if verbose:
        _print_report(symbol, prefix, events, pattern_summary, strata_summary, ep, sp, tp)

    return events


def _print_report(
    symbol: str,
    prefix: str,
    events: pd.DataFrame,
    pattern_summary: pd.DataFrame,
    strata_summary: pd.DataFrame,
    ep: Path,
    sp: Path,
    tp: Path,
) -> None:
    print("\n===== 形态 + Delta/盘口 Event Study =====")
    print(f"品种: {symbol} ({prefix}) | 事件: {len(events):,}")
    print("-" * 62)
    print(f"{'Pattern':<22} {'N':>6} {'f10':>8} {'WR':>7} {'MFE':>6} {'MAE':>6} {'net':>7}")
    for _, row in pattern_summary.iterrows():
        print(
            f"{row['segment']:<22} {int(row['n']):6d} {row['avg_future_10']:+8.2f} "
            f"{row['wr']:7.1%} {row['avg_mfe']:6.2f} {row['avg_mae']:6.2f} {row['net_after_cost']:+7.2f}"
        )
    print("\n【Delta/盘口分层 — 每 pattern 子集 f10 最优 3 项】")
    if not strata_summary.empty:
        top = strata_summary.sort_values("avg_future_10", ascending=False).head(12)
        for _, row in top.iterrows():
            print(
                f"  {row['segment']:<40} n={int(row['n']):4d} "
                f"f10={row['avg_future_10']:+.2f} WR={row['wr']:.1%} net={row['net_after_cost']:+.2f}"
            )
    print(f"\n输出:\n  {ep}\n  {sp}\n  {tp}")
    print("=" * 62)
    if events.empty:
        print("无事件：检查 tick 目录是否有合并后的 *_tick.parquet（非 _part_）")
    else:
        print("注: aligned_delta_30s = direction × delta_30s（与 fade/顺势方向同号为正）")


def main() -> None:
    parser = argparse.ArgumentParser(description="形态 + Delta/盘口 Event Study")
    parser.add_argument("--symbol", default="rb")
    parser.add_argument(
        "--pattern",
        choices=("failed_breakout", "breakout_success", "all"),
        default="all",
    )
    parser.add_argument("--start", default="2025-01-01")
    parser.add_argument("--end", default="2026-06-30")
    parser.add_argument("--tick", type=float, default=1.0)
    args = parser.parse_args()

    run_study(
        symbol=args.symbol,
        pattern=args.pattern,
        start=datetime.strptime(args.start, "%Y-%m-%d"),
        end=datetime.strptime(args.end, "%Y-%m-%d"),
        tick=args.tick,
    )


if __name__ == "__main__":
    main()
