# -*- coding: utf-8
"""BrooksFade E2 — Context Filter Study（Trading Range × Failed Breakout）。

前置: E1 全样本无 Alpha → 检验假突破是否仅在特定市场状态下可交易。

研究问题
--------
Q1  Range 状态下 Failed Breakout 是否有正向 future_10？
Q2  Trend 状态下是否应**禁止** Fade（future_10 为负）？
Q3  Range 子样本是否通过 E1 成本门禁（future_10 > cost_ticks, MFE > MAE）？

市场状态（信号 bar 当时，不含未来数据）
------------------------------------
ADX14:
  - RANGE:  ADX < 20
  - TREND:  ADX > 25
  - MID:    20 <= ADX <= 25

EMA20 slope（辅助，atr 归一化 5-bar 斜率）:
  - FLAT:   |slope| < 0.15
  - STEEP:  |slope| > 0.35
  - MID:    其余

事件定义: 与 E1 相同（复用 E1_failed_breakout）。

输出::
  experiments/output/E2_context_events.csv
  experiments/output/E2_context_summary.csv

用法::
  .venv\\Scripts\\python.exe experiments/E2_context_fade.py
  .venv\\Scripts\\python.exe experiments/E2_context_fade.py --start 2025-01-01 --end 2026-06-30
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

from experiments.E1_failed_breakout import (
    FWD_HORIZONS,
    MFE_WINDOW,
    _detect_events,
    _prepare_features,
    _verdict_row,
    load_bars,
)

OUTPUT_DIR = Path(__file__).resolve().parent / "output"

ADX_RANGE = 20.0
ADX_TREND = 25.0
EMA_FLAT = 0.15
EMA_STEEP = 0.35


def _calc_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
    h = df["high"].astype(float)
    lo = df["low"].astype(float)
    c = df["close"].astype(float)

    up = h.diff()
    down = -lo.diff()
    plus_dm = np.where((up > down) & (up > 0), up, 0.0)
    minus_dm = np.where((down > up) & (down > 0), down, 0.0)

    prev_c = c.shift(1)
    tr = pd.concat([(h - lo), (h - prev_c).abs(), (lo - prev_c).abs()], axis=1).max(axis=1)
    atr = tr.rolling(period, min_periods=period).mean()

    plus_di = 100 * pd.Series(plus_dm, index=df.index).rolling(period, min_periods=period).mean() / atr
    minus_di = 100 * pd.Series(minus_dm, index=df.index).rolling(period, min_periods=period).mean() / atr
    dx = (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan) * 100
    adx = dx.rolling(period, min_periods=period).mean()
    return adx


def _attach_regime(feat: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    """将 ADX / EMA slope 映射到每个事件（按 datetime 对齐 feat 行）。"""
    feat = feat.copy()
    feat["adx14"] = _calc_adx(feat)
    feat["ema_slope5"] = (feat["ema20"] - feat["ema20"].shift(5)) / feat["atr20"]

    dt_to_idx = {pd.Timestamp(row["dt_cst"]): i for i, row in feat.iterrows()}
    rows: list[dict] = []
    for _, ev in events.iterrows():
        ts = pd.Timestamp(ev["datetime"])
        idx = dt_to_idx.get(ts)
        if idx is None:
            continue
        row = feat.loc[idx]
        adx = float(row["adx14"]) if not pd.isna(row["adx14"]) else np.nan
        slope = float(row["ema_slope5"]) if not pd.isna(row["ema_slope5"]) else np.nan

        if pd.isna(adx):
            adx_regime = "NA"
        elif adx < ADX_RANGE:
            adx_regime = "RANGE"
        elif adx > ADX_TREND:
            adx_regime = "TREND"
        else:
            adx_regime = "MID"

        if pd.isna(slope):
            ema_regime = "NA"
        elif abs(slope) < EMA_FLAT:
            ema_regime = "FLAT"
        elif abs(slope) > EMA_STEEP:
            ema_regime = "STEEP"
        else:
            ema_regime = "MID"

        rec = ev.to_dict()
        rec["adx14"] = adx
        rec["ema_slope5"] = slope
        rec["adx_regime"] = adx_regime
        rec["ema_regime"] = ema_regime
        rows.append(rec)

    return pd.DataFrame(rows)


def _build_summaries(events: pd.DataFrame, *, tick: float, cost_ticks: float) -> pd.DataFrame:
    rows: list[dict] = []

    def add(label: str, sub: pd.DataFrame) -> None:
        rows.append(_verdict_row(sub, tick=tick, cost_ticks=cost_ticks, label=label))

    add("E2_ALL", events)

    for regime in ("RANGE", "MID", "TREND", "NA"):
        add(f"ADX_{regime}", events[events["adx_regime"] == regime])

    for regime in ("FLAT", "MID", "STEEP", "NA"):
        add(f"EMA_{regime}", events[events["ema_regime"] == regime])

    # 交叉：ADX Range × 方向
    for direction, dlabel in [(-1, "SHORT"), (1, "LONG")]:
        sub_dir = events[events["direction"] == direction]
        add(f"{dlabel}_ALL", sub_dir)
        add(
            f"{dlabel}_ADX_RANGE",
            sub_dir[sub_dir["adx_regime"] == "RANGE"],
        )
        add(
            f"{dlabel}_ADX_TREND",
            sub_dir[sub_dir["adx_regime"] == "TREND"],
        )

    # Brooks 组合：Range + Flat EMA（双震荡确认）
    combo = events[(events["adx_regime"] == "RANGE") & (events["ema_regime"] == "FLAT")]
    add("COMBO_RANGE_FLAT", combo)

    combo2 = events[events["adx_regime"] == "RANGE"]
    add("COMBO_ADX_RANGE_ONLY", combo2)

    trend_combo = events[events["adx_regime"] == "TREND"]
    add("COMBO_ADX_TREND_ONLY", trend_combo)

    return pd.DataFrame(rows)


def run_e2(
    *,
    input_path: Path | None = None,
    symbol: str = "rb",
    start: datetime | None = None,
    end: datetime | None = None,
    tick: float = 1.0,
    cost_ticks: float = 3.0,
    verbose: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    bars, source = load_bars(input_path=input_path, symbol=symbol)
    if start is not None:
        bars = bars[bars["dt_cst"] >= pd.Timestamp(start, tz="Asia/Shanghai")]
    if end is not None:
        bars = bars[bars["dt_cst"] <= pd.Timestamp(end, tz="Asia/Shanghai")]
    bars = bars.sort_values("dt_cst").reset_index(drop=True)

    feat = _prepare_features(bars)
    events_raw = _detect_events(feat)
    events = _attach_regime(feat, events_raw)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    events_path = OUTPUT_DIR / "E2_context_events.csv"
    events.to_csv(events_path, index=False, encoding="utf-8-sig")

    summary = _build_summaries(events, tick=tick, cost_ticks=cost_ticks)
    summary_path = OUTPUT_DIR / "E2_context_summary.csv"
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")

    if verbose:
        _print_report(source=source, n_bars=len(bars), events=events, summary=summary, cost_ticks=cost_ticks)

    return events, summary


def _print_report(
    *,
    source: str,
    n_bars: int,
    events: pd.DataFrame,
    summary: pd.DataFrame,
    cost_ticks: float,
) -> None:
    print("\n===== BrooksFade E2 | Context Filter Study =====")
    print(f"数据源: {source} | bars: {n_bars:,} | 事件: {len(events):,}")
    print(f"ADX 阈值: RANGE<{ADX_RANGE} | TREND>{ADX_TREND}")
    print(f"EMA slope: FLAT<{EMA_FLAT} | STEEP>{EMA_STEEP} (5bar/ATR)")
    print("-" * 60)

    key_segments = [
        "E2_ALL",
        "ADX_RANGE",
        "ADX_TREND",
        "ADX_MID",
        "SHORT_ADX_RANGE",
        "SHORT_ADX_TREND",
        "COMBO_ADX_RANGE_ONLY",
        "COMBO_ADX_TREND_ONLY",
        "COMBO_RANGE_FLAT",
    ]
    print(f"{'Segment':<22} {'n':>5} {'f10':>7} {'MFE':>6} {'MAE':>6} {'P1R':>6} {'net':>7} {'PASS':>5}")
    print("-" * 60)
    for seg in key_segments:
        row = summary[summary["segment"] == seg]
        if row.empty:
            continue
        r = row.iloc[0]
        passed = bool(r["pass_q1"] and r["pass_q2"] and r["pass_cost"])
        print(
            f"{seg:<22} {int(r['n']):5d} {r['avg_future_10']:+7.2f} "
            f"{r['avg_mfe']:6.2f} {r['avg_mae']:6.2f} {r['p_mfe_gt_1r']:6.1%} "
            f"{r['net_after_cost_10']:+7.2f} {'Y' if passed else 'N'}"
        )

    print("-" * 60)
    range_row = summary[summary["segment"] == "ADX_RANGE"]
    trend_row = summary[summary["segment"] == "ADX_TREND"]
    if not range_row.empty and not trend_row.empty:
        rf = float(range_row.iloc[0]["avg_future_10"])
        tf = float(trend_row.iloc[0]["avg_future_10"])
        spread = rf - tf
        print(f"Range vs Trend future_10 差: {spread:+.2f} ticks")
        if rf > 0 and tf < 0:
            print("假设方向一致: Range 正 / Trend 负 → **支持 Context 假说**（待样本外）")
        elif rf > tf:
            print("Range 优于 Trend，但未形成正负分列 → **部分支持，不足以进策略**")
        else:
            print("Context 分层未改善 edge → **E2 假说未证实**")

    out_dir = OUTPUT_DIR
    print(f"\n输出: {out_dir / 'E2_context_events.csv'}")
    print(f"      {out_dir / 'E2_context_summary.csv'}")
    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(description="BrooksFade E2 Context Filter Study")
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--symbol", default="rb")
    parser.add_argument("--start", default="2025-01-01")
    parser.add_argument("--end", default="2026-06-30")
    parser.add_argument("--tick", type=float, default=1.0)
    parser.add_argument("--cost-ticks", type=float, default=3.0)
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d") if args.start else None
    end = datetime.strptime(args.end, "%Y-%m-%d") if args.end else None

    run_e2(
        input_path=args.input,
        symbol=args.symbol,
        start=start,
        end=end,
        tick=args.tick,
        cost_ticks=args.cost_ticks,
    )


if __name__ == "__main__":
    main()
