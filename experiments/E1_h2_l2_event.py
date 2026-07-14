# -*- coding: utf-8
"""Brooks H2/L2 Event Study E1 — 二次入场形态统计（纯事件，无交易模拟）。

研究假设: RB 1m 上 H2/L2 Second Entry 存在可量化方向性 edge。

H2（多头）状态机
----------------
  趋势 → PB1 → Rally → PB2 → 突破 signal_high = high[t-1]+tick

趋势（多头）:
  - EMA20[t] > EMA20[t-10]
  - close > EMA20
  - higher_high & higher_low（近 10 根结构）

回调:
  - low < EMA20 或连续 2 根阴线

L2: 对称（空头趋势 + 两次反弹 + 跌破前低）

输出::
  experiments/output/h2_l2_events.csv
  experiments/output/h2_l2_summary.csv
  experiments/output/h2_l2_direction.csv

用法::
  .venv\\Scripts\\python.exe experiments/E1_h2_l2_event.py --symbol rb \\
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
FWD_HORIZONS_LIST = list(FWD_HORIZONS)
EMA_TREND_LAG = 10
STRUCT_LOOKBACK = 10
H2_READY_MAX_BARS = 5

# E1 通过门槛
MIN_N = 300
MIN_FUTURE10 = 1.0
MIN_MFE_MAE_RATIO = 1.3
COST_TICKS = 3.0


class LongState(IntEnum):
    IDLE = 0
    TREND = 1
    PB1 = 2
    RALLY = 3
    PB2 = 4
    H2_READY = 5


class ShortState(IntEnum):
    IDLE = 0
    TREND = 1
    PB1 = 2
    RALLY = 3
    PB2 = 4
    L2_READY = 5


@dataclass
class LegTracker:
    bars: int = 0
    depth_atr: float = 0.0

    def reset(self) -> None:
        self.bars = 0
        self.depth_atr = 0.0

    def update_long_pb(self, ema: float, low: float, atr: float) -> None:
        self.bars += 1
        if atr > 0:
            self.depth_atr = max(self.depth_atr, (ema - low) / atr)

    def update_short_pb(self, ema: float, high: float, atr: float) -> None:
        self.bars += 1
        if atr > 0:
            self.depth_atr = max(self.depth_atr, (high - ema) / atr)


@dataclass
class LongFsm:
    state: LongState = LongState.IDLE
    pb1: LegTracker = field(default_factory=LegTracker)
    pb2: LegTracker = field(default_factory=LegTracker)
    ready_bars: int = 0
    below_ema_bars: int = 0

    def reset(self) -> None:
        self.state = LongState.IDLE
        self.pb1.reset()
        self.pb2.reset()
        self.ready_bars = 0
        self.below_ema_bars = 0


@dataclass
class ShortFsm:
    state: ShortState = ShortState.IDLE
    pb1: LegTracker = field(default_factory=LegTracker)
    pb2: LegTracker = field(default_factory=LegTracker)
    ready_bars: int = 0
    above_ema_bars: int = 0

    def reset(self) -> None:
        self.state = ShortState.IDLE
        self.pb1.reset()
        self.pb2.reset()
        self.ready_bars = 0
        self.above_ema_bars = 0


def _prepare(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy().reset_index(drop=True)
    c = out["close"].astype(float)
    h = out["high"].astype(float)
    lo = out["low"].astype(float)
    o = out["open"].astype(float)

    prev_c = c.shift(1)
    tr = pd.concat([(h - lo), (h - prev_c).abs(), (lo - prev_c).abs()], axis=1).max(axis=1)
    out["atr20"] = tr.rolling(20, min_periods=20).mean()
    out["ema20"] = c.ewm(span=20, adjust=False).mean()
    out["ema_slope10"] = (out["ema20"] - out["ema20"].shift(EMA_TREND_LAG)) / out["atr20"]
    out["bear_bar"] = (c < o).astype(int)
    out["bull_bar"] = (c > o).astype(int)
    out["bear2"] = (out["bear_bar"] + out["bear_bar"].shift(1).fillna(0)) >= 2
    out["bull2"] = (out["bull_bar"] + out["bull_bar"].shift(1).fillna(0)) >= 2
    out["range"] = h - lo
    return out


def _bull_structure(feat: pd.DataFrame, i: int, n: int = STRUCT_LOOKBACK) -> bool:
    window = feat.iloc[i - n + 1 : i + 1]
    highs = window["high"].astype(float).values
    lows = window["low"].astype(float).values
    if len(highs) < 2:
        return False
    hh = sum(1 for j in range(1, len(highs)) if highs[j] > highs[j - 1])
    hl = sum(1 for j in range(1, len(lows)) if lows[j] > lows[j - 1])
    return hh >= 6 and hl >= 6


def _bear_structure(feat: pd.DataFrame, i: int, n: int = STRUCT_LOOKBACK) -> bool:
    window = feat.iloc[i - n + 1 : i + 1]
    highs = window["high"].astype(float).values
    lows = window["low"].astype(float).values
    if len(highs) < 2:
        return False
    lh = sum(1 for j in range(1, len(highs)) if highs[j] < highs[j - 1])
    ll = sum(1 for j in range(1, len(lows)) if lows[j] < lows[j - 1])
    return lh >= 6 and ll >= 6


def _bull_trend(row: pd.Series, feat: pd.DataFrame, i: int) -> bool:
    if pd.isna(row["ema20"]) or pd.isna(row["atr20"]):
        return False
    if i < EMA_TREND_LAG + STRUCT_LOOKBACK:
        return False
    ema_now = float(row["ema20"])
    ema_prev = float(feat.iloc[i - EMA_TREND_LAG]["ema20"])
    if ema_now <= ema_prev:
        return False
    if float(row["close"]) <= ema_now:
        return False
    return _bull_structure(feat, i)


def _bear_trend(row: pd.Series, feat: pd.DataFrame, i: int) -> bool:
    if pd.isna(row["ema20"]) or pd.isna(row["atr20"]):
        return False
    if i < EMA_TREND_LAG + STRUCT_LOOKBACK:
        return False
    ema_now = float(row["ema20"])
    ema_prev = float(feat.iloc[i - EMA_TREND_LAG]["ema20"])
    if ema_now >= ema_prev:
        return False
    if float(row["close"]) >= ema_now:
        return False
    return _bear_structure(feat, i)


def _seq_bull_valid(row: pd.Series, feat: pd.DataFrame, i: int) -> bool:
    """序列进行中：只要求 EMA 仍向上 + close 在 EMA 上方（不要求每根 hh/hl）。"""
    if i < EMA_TREND_LAG:
        return False
    ema_now = float(row["ema20"])
    ema_prev = float(feat.iloc[i - EMA_TREND_LAG]["ema20"])
    return float(row["close"]) > ema_now and ema_now > ema_prev


def _seq_bear_valid(row: pd.Series, feat: pd.DataFrame, i: int) -> bool:
    if i < EMA_TREND_LAG:
        return False
    ema_now = float(row["ema20"])
    ema_prev = float(feat.iloc[i - EMA_TREND_LAG]["ema20"])
    return float(row["close"]) < ema_now and ema_now < ema_prev


def _long_invalidate(lf: LongFsm, row: pd.Series) -> bool:
    if float(row["close"]) < float(row["ema20"]):
        lf.below_ema_bars += 1
    else:
        lf.below_ema_bars = 0
    return lf.below_ema_bars >= 3


def _short_invalidate(sf: ShortFsm, row: pd.Series) -> bool:
    if float(row["close"]) > float(row["ema20"]):
        sf.above_ema_bars += 1
    else:
        sf.above_ema_bars = 0
    return sf.above_ema_bars >= 3


def _long_pullback(row: pd.Series) -> bool:
    return float(row["low"]) < float(row["ema20"]) or bool(row["bear2"])


def _short_pullback(row: pd.Series) -> bool:
    return float(row["high"]) > float(row["ema20"]) or bool(row["bull2"])


def _long_pb_end(row: pd.Series) -> bool:
    return float(row["close"]) >= float(row["ema20"])


def _short_pb_end(row: pd.Series) -> bool:
    return float(row["close"]) <= float(row["ema20"])


def _forward_stats(df: pd.DataFrame, i: int, direction: int) -> dict:
    close0 = float(df.iloc[i]["close"])
    row = df.iloc[i]
    one_r = float(row["range"])
    fwd = {}
    for k in FWD_HORIZONS_LIST:
        close_k = float(df.iloc[i + k]["close"])
        fwd[f"future_{k}"] = direction * (close_k - close0)

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

    stop_risk = one_r + 1.0  # signal bar range + 1 tick 近似 1R
    return {
        **fwd,
        "mfe": mfe,
        "mae": mae,
        "one_r": one_r,
        "mfe_gt_1r": int(mfe > stop_risk),
    }


def _detect_h2_l2(feat: pd.DataFrame, *, tick: float) -> pd.DataFrame:
    rows: list[dict] = []
    n = len(feat)
    max_k = max(*FWD_HORIZONS_LIST, MFE_WINDOW)
    lf = LongFsm()
    sf = ShortFsm()

    for i in range(STRUCT_LOOKBACK + EMA_TREND_LAG, n - max_k):
        row = feat.iloc[i]
        prev = feat.iloc[i - 1]
        ema = float(row["ema20"])
        atr = float(row["atr20"])
        low = float(row["low"])
        high = float(row["high"])

        # ---- Long FSM (H2) ----
        in_sequence = lf.state != LongState.IDLE
        if in_sequence:
            if _long_invalidate(lf, row) or not _seq_bull_valid(row, feat, i):
                lf.reset()
            else:
                if lf.state == LongState.TREND:
                    if _long_pullback(row):
                        lf.state = LongState.PB1
                        lf.pb1.reset()
                        lf.pb1.update_long_pb(ema, low, atr)
                elif lf.state == LongState.PB1:
                    lf.pb1.update_long_pb(ema, low, atr)
                    if _long_pb_end(row):
                        lf.state = LongState.RALLY
                elif lf.state == LongState.RALLY:
                    if _long_pullback(row):
                        lf.state = LongState.PB2
                        lf.pb2.reset()
                        lf.pb2.update_long_pb(ema, low, atr)
                elif lf.state == LongState.PB2:
                    lf.pb2.update_long_pb(ema, low, atr)
                    if _long_pb_end(row):
                        lf.state = LongState.H2_READY
                        lf.ready_bars = 0
                elif lf.state == LongState.H2_READY:
                    lf.ready_bars += 1
                    if high > float(prev["high"]) + tick:
                        stats = _forward_stats(feat, i, direction=1)
                        rows.append(
                            {
                                "datetime": row["dt_cst"],
                                "setup": "H2",
                                "direction": 1,
                                "trend_strength": float(row["ema_slope10"]),
                                "ema_slope": float(row["ema_slope10"]),
                                "pullback1_bars": lf.pb1.bars,
                                "pullback2_bars": lf.pb2.bars,
                                "pullback1_depth": lf.pb1.depth_atr,
                                "pullback2_depth": lf.pb2.depth_atr,
                                "signal_bar_range": float(row["range"]),
                                **stats,
                            }
                        )
                        lf.reset()
                        lf.state = LongState.TREND
                    elif lf.ready_bars > H2_READY_MAX_BARS:
                        lf.state = LongState.TREND
                        lf.pb2.reset()
                    elif _long_pullback(row):
                        lf.state = LongState.PB2
                        lf.pb2.reset()
                        lf.pb2.update_long_pb(ema, low, atr)
        elif _bull_trend(row, feat, i):
            lf.state = LongState.TREND

        # ---- Short FSM (L2) ----
        in_seq_s = sf.state != ShortState.IDLE
        if in_seq_s:
            if _short_invalidate(sf, row) or not _seq_bear_valid(row, feat, i):
                sf.reset()
            else:
                if sf.state == ShortState.TREND:
                    if _short_pullback(row):
                        sf.state = ShortState.PB1
                        sf.pb1.reset()
                        sf.pb1.update_short_pb(ema, high, atr)
                elif sf.state == ShortState.PB1:
                    sf.pb1.update_short_pb(ema, high, atr)
                    if _short_pb_end(row):
                        sf.state = ShortState.RALLY
                elif sf.state == ShortState.RALLY:
                    if _short_pullback(row):
                        sf.state = ShortState.PB2
                        sf.pb2.reset()
                        sf.pb2.update_short_pb(ema, high, atr)
                elif sf.state == ShortState.PB2:
                    sf.pb2.update_short_pb(ema, high, atr)
                    if _short_pb_end(row):
                        sf.state = ShortState.L2_READY
                        sf.ready_bars = 0
                elif sf.state == ShortState.L2_READY:
                    sf.ready_bars += 1
                    if low < float(prev["low"]) - tick:
                        stats = _forward_stats(feat, i, direction=-1)
                        rows.append(
                            {
                                "datetime": row["dt_cst"],
                                "setup": "L2",
                                "direction": -1,
                                "trend_strength": float(row["ema_slope10"]),
                                "ema_slope": float(row["ema_slope10"]),
                                "pullback1_bars": sf.pb1.bars,
                                "pullback2_bars": sf.pb2.bars,
                                "pullback1_depth": sf.pb1.depth_atr,
                                "pullback2_depth": sf.pb2.depth_atr,
                                "signal_bar_range": float(row["range"]),
                                **stats,
                            }
                        )
                        sf.reset()
                        sf.state = ShortState.TREND
                    elif sf.ready_bars > H2_READY_MAX_BARS:
                        sf.state = ShortState.TREND
                        sf.pb2.reset()
                    elif _short_pullback(row):
                        sf.state = ShortState.PB2
                        sf.pb2.reset()
                        sf.pb2.update_short_pb(ema, high, atr)
        elif _bear_trend(row, feat, i):
            sf.state = ShortState.TREND

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
    ratio = avg_mfe / avg_mae if avg_mae > 0 else np.nan
    return {
        "n": len(events),
        "avg_future_10": avg_f10,
        "wr": float((f10 > 0).mean()),
        "avg_mfe": avg_mfe,
        "avg_mae": avg_mae,
        "mfe_mae_ratio": ratio,
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
        return True, f"future_10={f10:+.2f}t, net={s['net_after_cost']:+.2f}t"
    if not np.isnan(ratio) and ratio > MIN_MFE_MAE_RATIO and s["net_after_cost"] > 0:
        return True, f"MFE/MAE={ratio:.2f}>{MIN_MFE_MAE_RATIO}, net={s['net_after_cost']:+.2f}t"
    if f10 <= 0:
        return False, f"future_10={f10:+.2f}t≤0"
    return False, f"future_10={f10:+.2f}t 未达 {MIN_FUTURE10}t 或 net≤0"


def run_h2_l2_e1(
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
    events = _detect_h2_l2(feat, tick=tick)

    if events.empty:
        events = pd.DataFrame(
            columns=[
                "datetime", "setup", "direction", "trend_strength", "ema_slope",
                "pullback1_bars", "pullback2_bars", "pullback1_depth", "pullback2_depth",
                "signal_bar_range", "future_5", "future_10", "future_20",
                "mfe", "mae", "one_r", "mfe_gt_1r",
            ]
        )

    for col in ("future_5", "future_10", "future_20", "mfe", "mae", "signal_bar_range", "one_r"):
        if col in events.columns:
            events[f"{col}_ticks"] = events[col] / tick

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    events_path = OUTPUT_DIR / "h2_l2_events.csv"
    events.to_csv(events_path, index=False, encoding="utf-8-sig")

    all_stats = _segment_stats(events, tick=tick)
    h2_stats = _segment_stats(events[events["setup"] == "H2"], tick=tick)
    l2_stats = _segment_stats(events[events["setup"] == "L2"], tick=tick)

    summary = pd.DataFrame(
        [
            {"segment": "ALL", **all_stats},
            {"segment": "H2_LONG", **h2_stats},
            {"segment": "L2_SHORT", **l2_stats},
        ]
    )
    summary_path = OUTPUT_DIR / "h2_l2_summary.csv"
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")

    direction = pd.DataFrame(
        [
            {
                "setup": "H2",
                "direction": "long",
                **h2_stats,
            },
            {
                "setup": "L2",
                "direction": "short",
                **l2_stats,
            },
        ]
    )
    direction_path = OUTPUT_DIR / "h2_l2_direction.csv"
    direction.to_csv(direction_path, index=False, encoding="utf-8-sig")

    if verbose:
        _print_report(source, len(bars), events, summary, direction, events_path, summary_path, direction_path)

    return events, summary, direction


def _print_report(
    source: str,
    n_bars: int,
    events: pd.DataFrame,
    summary: pd.DataFrame,
    direction: pd.DataFrame,
    events_path: Path,
    summary_path: Path,
    direction_path: Path,
) -> None:
    print("\n===== Brooks H2/L2 Event Study E1 =====")
    print(f"数据源: {source} | bars: {n_bars:,} | 事件: {len(events):,}")
    print(f"成本假设: {COST_TICKS:.0f} tick 往返 | 门槛: N>{MIN_N}, f10>{MIN_FUTURE10}t 或 MFE/MAE>{MIN_MFE_MAE_RATIO}")
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
    all_row = summary[summary["segment"] == "ALL"].iloc[0]
    passed, reason = _pass_verdict(all_row.to_dict())
    print(f"E1 门禁: {'**通过**' if passed else '**未通过**'} — {reason}")
    if not passed and int(all_row["n"]) > 0:
        print("建议: RB 1m 裸 H2/L2 无足够 edge → 转 MA/TA 或加强 Execution/Context 后再研究")
    elif passed:
        print("建议: 可进入 Round 2 过滤（趋势强度/回调深度/时段）或 E3 Execution Study")
    print(f"\n输出:\n  {events_path}\n  {summary_path}\n  {direction_path}")
    print("=" * 65)


def main() -> None:
    parser = argparse.ArgumentParser(description="Brooks H2/L2 Event Study E1")
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--symbol", default="rb")
    parser.add_argument("--start", default="2025-01-01")
    parser.add_argument("--end", default="2026-06-30")
    parser.add_argument("--tick", type=float, default=1.0)
    args = parser.parse_args()

    run_h2_l2_e1(
        input_path=args.input,
        symbol=args.symbol,
        start=datetime.strptime(args.start, "%Y-%m-%d"),
        end=datetime.strptime(args.end, "%Y-%m-%d"),
        tick=args.tick,
    )


if __name__ == "__main__":
    main()
