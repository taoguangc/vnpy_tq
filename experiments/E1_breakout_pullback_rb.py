# -*- coding: utf-8
"""Brooks RB E1 — Breakout Pullback Continuation（顺势，非 Fade）。

研究假设: RB 1m 上「突破 → 回踩持稳 → 续攻」存在可量化方向 edge。

与 BrooksFade 区别
------------------
  - Fade: 突破失败 → 反向
  - 本实验: 突破成功（收盘站上）→ 回踩不破 → 顺势续攻

事件定义（多头 BP Long）
-----------------------
1. 突破: high > prev_high(20) 且 close > prev_high（成功突破）
2. 回踩: 突破后 1~15 根内 low 回落，但 close 始终 >= breakout_level - 1*tick
3. 触发: 回踩结束后 high > high[t-1] + tick

空头 BP Short: 对称。

输出::
  experiments/output/bp_continuation_events.csv
  experiments/output/bp_continuation_summary.csv
  experiments/output/bp_continuation_direction.csv

用法::
  .venv\\Scripts\\python.exe experiments/E1_breakout_pullback_rb.py --symbol rb \\
      --start 2025-01-01 --end 2026-06-30
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.E1_failed_breakout import FWD_HORIZONS, MFE_WINDOW, load_bars

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
LOOKBACK = 20
PULLBACK_MAX_BARS = 15
READY_MAX_BARS = 5
MIN_N = 300
MIN_FUTURE10 = 1.0
MIN_MFE_MAE_RATIO = 1.3
COST_TICKS = 3.0


class LongState(IntEnum):
    IDLE = 0
    WATCH = 1
    PULLBACK = 2
    READY = 3


class ShortState(IntEnum):
    IDLE = 0
    WATCH = 1
    PULLBACK = 2
    READY = 3


@dataclass
class LongLeg:
    breakout_level: float = 0.0
    bars_since_bo: int = 0
    pb_bars: int = 0
    pb_depth_atr: float = 0.0
    bo_size: float = 0.0

    def reset(self) -> None:
        self.breakout_level = 0.0
        self.bars_since_bo = 0
        self.pb_bars = 0
        self.pb_depth_atr = 0.0
        self.bo_size = 0.0


@dataclass
class LongFsm:
    state: LongState = LongState.IDLE
    leg: LongLeg = field(default_factory=LongLeg)

    def reset(self) -> None:
        self.state = LongState.IDLE
        self.leg.reset()


@dataclass
class ShortLeg:
    breakout_level: float = 0.0
    bars_since_bo: int = 0
    pb_bars: int = 0
    pb_depth_atr: float = 0.0
    bo_size: float = 0.0

    def reset(self) -> None:
        self.breakout_level = 0.0
        self.bars_since_bo = 0
        self.pb_bars = 0
        self.pb_depth_atr = 0.0
        self.bo_size = 0.0


@dataclass
class ShortFsm:
    state: ShortState = ShortState.IDLE
    leg: ShortLeg = field(default_factory=ShortLeg)
    ready_bars: int = 0

    def reset(self) -> None:
        self.state = ShortState.IDLE
        self.leg.reset()
        self.ready_bars = 0


def _prepare(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy().reset_index(drop=True)
    h = out["high"].astype(float)
    lo = out["low"].astype(float)
    c = out["close"].astype(float)
    prev_c = c.shift(1)
    tr = pd.concat([(h - lo), (h - prev_c).abs(), (lo - prev_c).abs()], axis=1).max(axis=1)
    out["atr20"] = tr.rolling(20, min_periods=20).mean()
    out["ema20"] = c.ewm(span=20, adjust=False).mean()
    out["ema_slope10"] = (out["ema20"] - out["ema20"].shift(10)) / out["atr20"]
    out["prev_20_high"] = h.shift(1).rolling(LOOKBACK, min_periods=LOOKBACK).max()
    out["prev_20_low"] = lo.shift(1).rolling(LOOKBACK, min_periods=LOOKBACK).min()
    out["range"] = h - lo
    return out


def _forward_stats(df: pd.DataFrame, i: int, direction: int) -> dict:
    close0 = float(df.iloc[i]["close"])
    one_r = float(df.iloc[i]["range"])
    fwd = {}
    for k in FWD_HORIZONS:
        fwd[f"future_{k}"] = direction * (float(df.iloc[i + k]["close"]) - close0)
    mfe = 0.0
    mae = 0.0
    for j in range(1, MFE_WINDOW + 1):
        bar = df.iloc[i + j]
        if direction > 0:
            mfe = max(mfe, float(bar["high"]) - close0)
            mae = max(mae, close0 - float(bar["low"]))
        else:
            mfe = max(mfe, close0 - float(bar["low"]))
            mae = max(mae, float(bar["high"]) - close0)
    stop_risk = one_r + 1.0
    return {**fwd, "mfe": mfe, "mae": mae, "one_r": one_r, "mfe_gt_1r": int(mfe > stop_risk)}


def _detect_events(feat: pd.DataFrame, *, tick: float) -> pd.DataFrame:
    rows: list[dict] = []
    n = len(feat)
    max_k = max(*FWD_HORIZONS, MFE_WINDOW)
    lf = LongFsm()
    sf = ShortFsm()
    sf.ready_bars = 0
    lf_ready = 0

    for i in range(LOOKBACK, n - max_k):
        row = feat.iloc[i]
        prev = feat.iloc[i - 1]
        if pd.isna(row["prev_20_high"]) or pd.isna(row["atr20"]):
            continue

        high = float(row["high"])
        low = float(row["low"])
        close = float(row["close"])
        open_ = float(row["open"])
        atr = float(row["atr20"])
        prev_high = float(row["prev_20_high"])
        prev_low = float(row["prev_20_low"])

        # ---- Long BP ----
        if lf.state == LongState.IDLE:
            if high > prev_high and close > prev_high:
                lf.state = LongState.WATCH
                lf.leg.breakout_level = prev_high
                lf.leg.bo_size = high - prev_high
                lf.leg.bars_since_bo = 0
                lf.leg.pb_bars = 0
                lf.leg.pb_depth_atr = 0.0
        elif lf.state == LongState.WATCH:
            lf.leg.bars_since_bo += 1
            if close < lf.leg.breakout_level - tick:
                lf.reset()
            elif low < close and (close < open_ or low < float(row["ema20"])):
                lf.state = LongState.PULLBACK
                lf.leg.pb_bars = 1
                if atr > 0:
                    lf.leg.pb_depth_atr = max(0.0, (lf.leg.breakout_level - low) / atr)
            elif lf.leg.bars_since_bo > PULLBACK_MAX_BARS:
                lf.reset()
        elif lf.state == LongState.PULLBACK:
            lf.leg.bars_since_bo += 1
            lf.leg.pb_bars += 1
            if atr > 0:
                lf.leg.pb_depth_atr = max(lf.leg.pb_depth_atr, (lf.leg.breakout_level - low) / atr)
            if close < lf.leg.breakout_level - tick:
                lf.reset()
            elif close >= open_ or close >= float(row["ema20"]):
                lf.state = LongState.READY
                lf_ready = 0
            elif lf.leg.bars_since_bo > PULLBACK_MAX_BARS:
                lf.reset()
        elif lf.state == LongState.READY:
            lf.leg.bars_since_bo += 1
            lf_ready += 1
            if high > float(prev["high"]) + tick:
                stats = _forward_stats(feat, i, direction=1)
                rows.append(
                    {
                        "datetime": row["dt_cst"],
                        "setup": "BP_LONG",
                        "direction": 1,
                        "breakout_size": lf.leg.bo_size,
                        "pullback_bars": lf.leg.pb_bars,
                        "pullback_depth_atr": lf.leg.pb_depth_atr,
                        "ema_slope": float(row["ema_slope10"]),
                        "signal_bar_range": float(row["range"]),
                        **stats,
                    }
                )
                lf.reset()
            elif lf_ready > READY_MAX_BARS or lf.leg.bars_since_bo > PULLBACK_MAX_BARS + READY_MAX_BARS:
                lf.reset()
            elif close < lf.leg.breakout_level - tick:
                lf.reset()

        # ---- Short BP ----
        if sf.state == ShortState.IDLE:
            if low < prev_low and close < prev_low:
                sf.state = ShortState.WATCH
                sf.leg.breakout_level = prev_low
                sf.leg.bo_size = prev_low - low
                sf.leg.bars_since_bo = 0
                sf.leg.pb_bars = 0
                sf.leg.pb_depth_atr = 0.0
        elif sf.state == ShortState.WATCH:
            sf.leg.bars_since_bo += 1
            if close > sf.leg.breakout_level + tick:
                sf.reset()
            elif high > close and (close > open_ or high > float(row["ema20"])):
                sf.state = ShortState.PULLBACK
                sf.leg.pb_bars = 1
                if atr > 0:
                    sf.leg.pb_depth_atr = max(0.0, (high - sf.leg.breakout_level) / atr)
            elif sf.leg.bars_since_bo > PULLBACK_MAX_BARS:
                sf.reset()
        elif sf.state == ShortState.PULLBACK:
            sf.leg.bars_since_bo += 1
            sf.leg.pb_bars += 1
            if atr > 0:
                sf.leg.pb_depth_atr = max(sf.leg.pb_depth_atr, (high - sf.leg.breakout_level) / atr)
            if close > sf.leg.breakout_level + tick:
                sf.reset()
            elif close <= open_ or close <= float(row["ema20"]):
                sf.state = ShortState.READY
                sf.ready_bars = 0
            elif sf.leg.bars_since_bo > PULLBACK_MAX_BARS:
                sf.reset()
        elif sf.state == ShortState.READY:
            sf.leg.bars_since_bo += 1
            sf.ready_bars += 1
            if low < float(prev["low"]) - tick:
                stats = _forward_stats(feat, i, direction=-1)
                rows.append(
                    {
                        "datetime": row["dt_cst"],
                        "setup": "BP_SHORT",
                        "direction": -1,
                        "breakout_size": sf.leg.bo_size,
                        "pullback_bars": sf.leg.pb_bars,
                        "pullback_depth_atr": sf.leg.pb_depth_atr,
                        "ema_slope": float(row["ema_slope10"]),
                        "signal_bar_range": float(row["range"]),
                        **stats,
                    }
                )
                sf.reset()
            elif sf.ready_bars > READY_MAX_BARS or sf.leg.bars_since_bo > PULLBACK_MAX_BARS + READY_MAX_BARS:
                sf.reset()
            elif close > sf.leg.breakout_level + tick:
                sf.reset()

    return pd.DataFrame(rows)


def _segment_stats(events: pd.DataFrame, *, tick: float) -> dict:
    if events.empty:
        return {
            "n": 0,
            "avg_future_10": np.nan,
            "wr": np.nan,
            "avg_mfe": np.nan,
            "avg_mae": np.nan,
            "mfe_mae_ratio": np.nan,
            "p_mfe_gt_1r": np.nan,
            "net_after_cost": np.nan,
        }
    f10 = events["future_10"] / tick
    mfe = events["mfe"] / tick
    mae = events["mae"] / tick
    avg_f10 = float(f10.mean())
    avg_mfe = float(mfe.mean())
    avg_mae = float(mae.mean())
    return {
        "n": len(events),
        "avg_future_10": avg_f10,
        "wr": float((f10 > 0).mean()),
        "avg_mfe": avg_mfe,
        "avg_mae": avg_mae,
        "mfe_mae_ratio": avg_mfe / avg_mae if avg_mae > 0 else np.nan,
        "p_mfe_gt_1r": float(events["mfe_gt_1r"].mean()),
        "net_after_cost": avg_f10 - COST_TICKS,
    }


def _pass_verdict(s: dict) -> tuple[bool, str]:
    if s["n"] < MIN_N:
        return False, f"N={s['n']}<{MIN_N}"
    f10 = s["avg_future_10"]
    ratio = s["mfe_mae_ratio"]
    if np.isnan(f10):
        return False, "无样本"
    if f10 > MIN_FUTURE10 and s["net_after_cost"] > 0:
        return True, f"future_10={f10:+.2f}t net={s['net_after_cost']:+.2f}t"
    if not np.isnan(ratio) and ratio > MIN_MFE_MAE_RATIO and s["net_after_cost"] > 0:
        return True, f"MFE/MAE={ratio:.2f} net={s['net_after_cost']:+.2f}t"
    return False, f"future_10={f10:+.2f}t net={s['net_after_cost']:+.2f}t"


def run_bp_e1(
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

    feat = _prepare(bars)
    events = _detect_events(feat, tick=tick)

    if events.empty:
        events = pd.DataFrame(
            columns=[
                "datetime", "setup", "direction", "breakout_size", "pullback_bars",
                "pullback_depth_atr", "ema_slope", "signal_bar_range",
                "future_5", "future_10", "future_20", "mfe", "mae", "one_r", "mfe_gt_1r",
            ]
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ep = OUTPUT_DIR / "bp_continuation_events.csv"
    events.to_csv(ep, index=False, encoding="utf-8-sig")

    all_s = _segment_stats(events, tick=tick)
    long_s = _segment_stats(events[events["setup"] == "BP_LONG"], tick=tick)
    short_s = _segment_stats(events[events["setup"] == "BP_SHORT"], tick=tick)

    summary = pd.DataFrame(
        [
            {"segment": "ALL", **all_s},
            {"segment": "BP_LONG", **long_s},
            {"segment": "BP_SHORT", **short_s},
        ]
    )
    sp = OUTPUT_DIR / "bp_continuation_summary.csv"
    summary.to_csv(sp, index=False, encoding="utf-8-sig")

    direction = pd.DataFrame(
        [
            {"setup": "BP_LONG", "direction": "long", **long_s},
            {"setup": "BP_SHORT", "direction": "short", **short_s},
        ]
    )
    dp = OUTPUT_DIR / "bp_continuation_direction.csv"
    direction.to_csv(dp, index=False, encoding="utf-8-sig")

    if verbose:
        _print_report(source, len(bars), events, summary, ep, sp, dp)

    return events, summary, direction


def _print_report(
    source: str,
    n_bars: int,
    events: pd.DataFrame,
    summary: pd.DataFrame,
    ep: Path,
    sp: Path,
    dp: Path,
) -> None:
    print("\n===== RB Breakout Pullback Continuation E1 =====")
    print(f"数据源: {source} | bars: {n_bars:,} | 事件: {len(events):,}")
    print(f"定义: 突破成功(close 站上) → 回踩持稳 → 突破前K高/低触发 | 成本={COST_TICKS}t")
    print("-" * 65)
    print(f"{'Segment':<12} {'N':>6} {'f10':>8} {'WR':>7} {'MFE':>6} {'MAE':>6} {'M/A':>6} {'P1R':>6} {'net':>7}")
    print("-" * 65)
    for _, row in summary.iterrows():
        print(
            f"{row['segment']:<12} {int(row['n']):6d} {row['avg_future_10']:+8.2f} "
            f"{row['wr']:7.1%} {row['avg_mfe']:6.2f} {row['avg_mae']:6.2f} "
            f"{row['mfe_mae_ratio']:6.2f} {row['p_mfe_gt_1r']:6.1%} {row['net_after_cost']:+7.2f}"
        )
    print("-" * 65)
    passed, reason = _pass_verdict(summary[summary["segment"] == "ALL"].iloc[0].to_dict())
    print(f"E1 门禁: {'**通过**' if passed else '**未通过**'} — {reason}")
    print(f"\n输出:\n  {ep}\n  {sp}\n  {dp}")
    print("=" * 65)


def main() -> None:
    parser = argparse.ArgumentParser(description="RB Breakout Pullback Continuation E1")
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--symbol", default="rb")
    parser.add_argument("--start", default="2025-01-01")
    parser.add_argument("--end", default="2026-06-30")
    parser.add_argument("--tick", type=float, default=1.0)
    args = parser.parse_args()

    run_bp_e1(
        input_path=args.input,
        symbol=args.symbol,
        start=datetime.strptime(args.start, "%Y-%m-%d"),
        end=datetime.strptime(args.end, "%Y-%m-%d"),
        tick=args.tick,
    )


if __name__ == "__main__":
    main()
