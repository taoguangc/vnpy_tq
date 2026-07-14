# -*- coding: utf-8
"""BrooksFade E2 — Context Filter Study（Trading Range × Failed Breakout）。

E1 结论: 裸 Failed Breakout 无 Alpha。
E2 假设: 失败突破仅在 Trading Range 环境中有效；Trend 中为假信号。

市场状态（信号 bar，无未来数据）
--------------------------------
State RANGE（同时满足）:
  - ADX14 < 20
  - abs(ema_slope) < 0.5
    ema_slope = (EMA20[t] - EMA20[t-20]) / ATR20

State TREND（满足其一）:
  - ADX14 > 25
  - abs(ema_slope) > 1.0

其余 → MID（不参与 Table 1 主对比，仍写入 events CSV）

事件定义: 与 E1 完全相同（禁止修改）。

输出::
  experiments/output/failed_breakout_context_events.csv
  experiments/output/state_summary.csv
  experiments/output/direction_summary.csv

用法::
  .venv\\Scripts\\python.exe experiments/E2_failed_breakout_context.py
  .venv\\Scripts\\python.exe experiments/E2_failed_breakout_context.py \\
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

from experiments.E1_failed_breakout import (
    _detect_events,
    _prepare_features,
    load_bars,
)

OUTPUT_DIR = Path(__file__).resolve().parent / "output"

EMA_SLOPE_LAG = 20
RANGE_ADX_MAX = 20.0
RANGE_SLOPE_MAX = 0.5
TREND_ADX_MIN = 25.0
TREND_SLOPE_MIN = 1.0

# E2 通过标准（Range 子样本）
E2_MIN_N = 300
E2_MIN_FUTURE10 = 1.0
E2_MIN_P_MFE_1R = 0.55


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
    return dx.rolling(period, min_periods=period).mean()


def _add_regime_columns(feat: pd.DataFrame) -> pd.DataFrame:
    out = feat.copy()
    out["adx14"] = _calc_adx(out)
    out["ema_slope"] = (out["ema20"] - out["ema20"].shift(EMA_SLOPE_LAG)) / out["atr20"]
    abs_slope = out["ema_slope"].abs()

    is_range = (out["adx14"] < RANGE_ADX_MAX) & (abs_slope < RANGE_SLOPE_MAX)
    is_trend = (out["adx14"] > TREND_ADX_MIN) | (abs_slope > TREND_SLOPE_MIN)

    out["market_state"] = np.where(
        is_range,
        "range",
        np.where(is_trend, "trend", "mid"),
    )
    return out


def _attach_context(feat: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    dt_map = feat.set_index(pd.to_datetime(feat["dt_cst"], utc=True))[
        ["market_state", "adx14", "ema_slope"]
    ]
    rows: list[dict] = []
    for _, ev in events.iterrows():
        ts = pd.Timestamp(ev["datetime"])
        if ts.tzinfo is None:
            ts = ts.tz_localize("Asia/Shanghai")
        key = ts.tz_convert("UTC")
        if key not in dt_map.index:
            continue
        ctx = dt_map.loc[key]
        rec = {
            "datetime": ev["datetime"],
            "direction": int(ev["direction"]),
            "market_state": ctx["market_state"],
            "adx": float(ctx["adx14"]) if not pd.isna(ctx["adx14"]) else np.nan,
            "ema_slope": float(ctx["ema_slope"]) if not pd.isna(ctx["ema_slope"]) else np.nan,
            "future_5": float(ev["future_5"]),
            "future_10": float(ev["future_10"]),
            "future_20": float(ev["future_20"]),
            "mfe": float(ev["mfe"]),
            "mae": float(ev["mae"]),
            "one_r": float(ev["one_r"]),
            "mfe_gt_1r": int(ev["mfe_gt_1r"]),
        }
        rows.append(rec)
    return pd.DataFrame(rows)


def _segment_stats(sub: pd.DataFrame, *, tick: float) -> dict:
    if sub.empty:
        return {"n": 0, "avg_future_10": np.nan, "wr": np.nan, "p_mfe_gt_1r": np.nan}
    f10 = sub["future_10"] / tick
    return {
        "n": len(sub),
        "avg_future_10": float(f10.mean()),
        "wr": float((f10 > 0).mean()),
        "p_mfe_gt_1r": float(sub["mfe_gt_1r"].mean()),
    }


def _build_state_summary(events: pd.DataFrame, *, tick: float) -> pd.DataFrame:
    rows = []
    for state in ("range", "trend", "mid"):
        sub = events[events["market_state"] == state]
        s = _segment_stats(sub, tick=tick)
        s["state"] = state
        rows.append(s)
    df = pd.DataFrame(rows)[["state", "n", "avg_future_10", "wr", "p_mfe_gt_1r"]]
    return df


def _build_direction_summary(events: pd.DataFrame, *, tick: float) -> pd.DataFrame:
    """Table 2: State × Long fade / Short fade → avg future_10 (ticks)."""
    rows = []
    for state in ("range", "trend"):
        sub = events[events["market_state"] == state]
        long_fade = sub[sub["direction"] == 1]
        short_fade = sub[sub["direction"] == -1]
        rows.append(
            {
                "state": state,
                "long_fade_n": len(long_fade),
                "long_fade_future10": _segment_stats(long_fade, tick=tick)["avg_future_10"],
                "short_fade_n": len(short_fade),
                "short_fade_future10": _segment_stats(short_fade, tick=tick)["avg_future_10"],
            }
        )
    return pd.DataFrame(rows)


def _e2_verdict(range_row: pd.Series) -> tuple[bool, str]:
    if int(range_row["n"]) < E2_MIN_N:
        return False, f"Range N={int(range_row['n'])}<{E2_MIN_N}"
    f10 = float(range_row["avg_future_10"])
    p1r = float(range_row["p_mfe_gt_1r"])
    if f10 > E2_MIN_FUTURE10:
        return True, f"Range future_10={f10:+.2f}t > {E2_MIN_FUTURE10}t"
    if p1r > E2_MIN_P_MFE_1R:
        return True, f"Range P(MFE>1R)={p1r:.1%} > {E2_MIN_P_MFE_1R:.0%}"
    if f10 < 0:
        return False, f"Range future_10={f10:+.2f}t < 0 → RB Fade 主线可结束"
    return False, f"Range future_10={f10:+.2f}t 未达 {E2_MIN_FUTURE10}t 且 P(MFE>1R)={p1r:.1%}"


def run_e2(
    *,
    input_path: Path | None = None,
    symbol: str = "rb",
    start: datetime | None = None,
    end: datetime | None = None,
    tick: float = 1.0,
    verbose: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    bars, source = load_bars(input_path=input_path, symbol=symbol)
    if start is not None:
        bars = bars[bars["dt_cst"] >= pd.Timestamp(start, tz="Asia/Shanghai")]
    if end is not None:
        bars = bars[bars["dt_cst"] <= pd.Timestamp(end, tz="Asia/Shanghai")]
    bars = bars.sort_values("dt_cst").reset_index(drop=True)

    feat = _add_regime_columns(_prepare_features(bars))
    events_raw = _detect_events(feat)
    events = _attach_context(feat, events_raw)

    # ticks 列便于 CSV 阅读
    for col in ("future_5", "future_10", "future_20", "mfe", "mae", "one_r"):
        events[f"{col}_ticks"] = events[col] / tick

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    events_path = OUTPUT_DIR / "failed_breakout_context_events.csv"
    state_path = OUTPUT_DIR / "state_summary.csv"
    direction_path = OUTPUT_DIR / "direction_summary.csv"

    export_cols = [
        "datetime",
        "direction",
        "market_state",
        "adx",
        "ema_slope",
        "future_5_ticks",
        "future_10_ticks",
        "future_20_ticks",
        "mfe_ticks",
        "mae_ticks",
    ]
    events[export_cols].rename(
        columns={
            "future_5_ticks": "future_5",
            "future_10_ticks": "future_10",
            "future_20_ticks": "future_20",
            "mfe_ticks": "mfe",
            "mae_ticks": "mae",
        }
    ).to_csv(events_path, index=False, encoding="utf-8-sig")

    state_summary = _build_state_summary(events, tick=tick)
    direction_summary = _build_direction_summary(events, tick=tick)
    state_summary.to_csv(state_path, index=False, encoding="utf-8-sig")
    direction_summary.to_csv(direction_path, index=False, encoding="utf-8-sig")

    if verbose:
        _print_report(
            source=source,
            n_bars=len(bars),
            events=events,
            state_summary=state_summary,
            direction_summary=direction_summary,
            events_path=events_path,
            state_path=state_path,
            direction_path=direction_path,
        )

    return events, state_summary, direction_summary


def _print_report(
    *,
    source: str,
    n_bars: int,
    events: pd.DataFrame,
    state_summary: pd.DataFrame,
    direction_summary: pd.DataFrame,
    events_path: Path,
    state_path: Path,
    direction_path: Path,
) -> None:
    print("\n===== BrooksFade E2 | Context Filter Study =====")
    print(f"数据源: {source} | bars: {n_bars:,} | 事件: {len(events):,}")
    print(
        f"RANGE: ADX<{RANGE_ADX_MAX} & |ema_slope(20)|<{RANGE_SLOPE_MAX} | "
        f"TREND: ADX>{TREND_ADX_MIN} | |ema_slope|>{TREND_SLOPE_MIN}"
    )
    print("-" * 60)
    print("【Table 1 — State Performance】")
    print(f"{'State':<8} {'N':>6} {'Avg f10':>10} {'WR':>8} {'P(MFE>1R)':>10}")
    print("-" * 60)
    for _, row in state_summary.iterrows():
        print(
            f"{row['state']:<8} {int(row['n']):6d} "
            f"{row['avg_future_10']:+10.2f} {row['wr']:8.1%} {row['p_mfe_gt_1r']:10.1%}"
        )

    print("\n【Table 2 — Direction × State (avg future_10 ticks)】")
    print(f"{'State':<8} {'Long fade':>12} {'(n)':>6} {'Short fade':>12} {'(n)':>6}")
    print("-" * 60)
    for _, row in direction_summary.iterrows():
        lf = row["long_fade_future10"]
        sf = row["short_fade_future10"]
        lf_s = f"{lf:+.2f}" if not pd.isna(lf) else "N/A"
        sf_s = f"{sf:+.2f}" if not pd.isna(sf) else "N/A"
        print(
            f"{row['state']:<8} {lf_s:>12} {int(row['long_fade_n']):6d} "
            f"{sf_s:>12} {int(row['short_fade_n']):6d}"
        )

    print("-" * 60)
    range_row = state_summary[state_summary["state"] == "range"].iloc[0]
    trend_row = state_summary[state_summary["state"] == "trend"].iloc[0]
    passed, reason = _e2_verdict(range_row)
    spread = float(range_row["avg_future_10"]) - float(trend_row["avg_future_10"])
    print(f"Range − Trend future_10: {spread:+.2f} ticks")
    print(f"E2 门禁: {'**通过**' if passed else '**未通过**'} — {reason}")

    if float(range_row["avg_future_10"]) < 0:
        print("结论: Range 子样本 future_10 < 0 → **RB 裸 Fade 主线建议结束**")
    elif passed:
        print("结论: 可进入 E3 Execution Study（仍不写完整策略）")
    else:
        print("结论: Context 分层未达策略门槛，需更强 Range 定义或换形态（Pullback Failure / H2）")

    print(f"\n输出:\n  {events_path}\n  {state_path}\n  {direction_path}")
    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(description="BrooksFade E2 Context Filter Study")
    parser.add_argument("--input", type=Path, default=None, help="Parquet 1m 路径（默认 TQ CbC）")
    parser.add_argument("--symbol", default="rb")
    parser.add_argument("--start", default="2025-01-01")
    parser.add_argument("--end", default="2026-06-30")
    parser.add_argument("--tick", type=float, default=1.0)
    args = parser.parse_args()

    run_e2(
        input_path=args.input,
        symbol=args.symbol,
        start=datetime.strptime(args.start, "%Y-%m-%d"),
        end=datetime.strptime(args.end, "%Y-%m-%d"),
        tick=args.tick,
    )


if __name__ == "__main__":
    main()
