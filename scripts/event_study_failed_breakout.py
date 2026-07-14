# -*- coding: utf-8
"""Failed Breakout 事件研究（BrooksFade v0.1 前置）。

机械定义（用户规范）：
  Step1 突破: high > rolling_high(20)（不含当前 bar）
  Step2 假突破 K（向上失败 → 做空方向）:
    - high > prev_high + 2*tick
    - close < prev_high
    - upper_wick > body * 1.5
    - body_ratio < 0.4
  可选 Climax: (close - ema20) / atr20 > climax_threshold

入场模拟（信号 bar 之后）：
  - Market: 信号 K 收盘价做空
  - Stop:  signal_low - tick，下一根起最多 stop_window 根内触发

出场（入场后 max_hold bars）：
  - 止损: signal_high + tick
  - 止盈: 1R（risk = stop - entry）
  - 同 bar 止损优先

用法:
  .venv\\Scripts\\python.exe scripts/event_study_failed_breakout.py --symbol rb
  .venv\\Scripts\\python.exe scripts/event_study_failed_breakout.py --symbol rb --data tick
  .venv\\Scripts\\python.exe scripts/event_study_failed_breakout.py --symbol ma --compare
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

from strategies.pa_cta.symbol_config import resolve_symbol_profile, resolve_tq_cbc_paths


@dataclass
class EventOutcome:
    entry_type: str
    filled: bool
    entry_price: float
    exit_reason: str
    exit_price: float
    mfe_ticks: float
    mae_ticks: float
    bars_held: int
    hit_1r: bool
    hit_stop: bool


def _load_bars_df(
    symbol: str,
    *,
    data: str,
    start: datetime,
    end: datetime,
) -> pd.DataFrame:
    profile = resolve_symbol_profile(symbol, ROOT)
    _, file_stem = resolve_tq_cbc_paths(profile)
    start_ts = pd.Timestamp(start, tz="Asia/Shanghai")
    end_ts = pd.Timestamp(end, tz="Asia/Shanghai")

    if data == "tick":
        from scripts.tq_tick_loader import build_stitched_tick_1m_frame

        df = build_stitched_tick_1m_frame(file_stem)
        label = "tick→1m"
    else:
        from scripts.tq_rollover_data import build_stitched_raw_frame

        df = build_stitched_raw_frame(file_stem)
        label = "分月 1m"

    df = df[(df["dt_cst"] >= start_ts) & (df["dt_cst"] <= end_ts)].copy()
    if df.empty:
        raise RuntimeError(f"{symbol} 在 {start.date()}~{end.date()} 无数据")
    df = df.sort_values("dt_cst").reset_index(drop=True)
    df.attrs["data_label"] = label
    return df


def _calc_indicators(df: pd.DataFrame, *, lookback: int, ema_period: int, atr_period: int) -> pd.DataFrame:
    out = df.copy()
    o = out["open"].astype(float)
    h = out["high"].astype(float)
    lo = out["low"].astype(float)
    c = out["close"].astype(float)

    prev_high = h.shift(1).rolling(lookback, min_periods=lookback).max()
    prev_low = lo.shift(1).rolling(lookback, min_periods=lookback).min()

    body = (c - o).abs()
    rng = (h - lo).clip(lower=1e-9)
    upper_wick = h - np.maximum(o, c)
    lower_wick = np.minimum(o, c) - lo
    body_ratio = body / rng

    prev_c = c.shift(1)
    tr = pd.concat(
        [(h - lo), (h - prev_c).abs(), (lo - prev_c).abs()],
        axis=1,
    ).max(axis=1)
    atr = tr.rolling(atr_period, min_periods=atr_period).mean()
    ema = c.ewm(span=ema_period, adjust=False).mean()

    out["prev_high"] = prev_high
    out["prev_low"] = prev_low
    out["body"] = body
    out["upper_wick"] = upper_wick
    out["lower_wick"] = lower_wick
    out["body_ratio"] = body_ratio
    out["atr20"] = atr
    out["ema20"] = ema
    out["climax_up"] = (c - ema) / atr
    out["climax_down"] = (ema - c) / atr
    return out


def _detect_failed_breakout_up(
    row: pd.Series,
    *,
    tick: float,
    wick_body_mult: float,
    max_body_ratio: float,
    breakout_ticks: float,
) -> bool:
    if pd.isna(row["prev_high"]) or pd.isna(row["atr20"]):
        return False
    prev_high = float(row["prev_high"])
    if row["high"] <= prev_high + breakout_ticks * tick:
        return False
    if row["close"] >= prev_high:
        return False
    if row["body_ratio"] >= max_body_ratio:
        return False
    if row["body"] <= 0:
        return row["upper_wick"] > 0
    if row["upper_wick"] <= row["body"] * wick_body_mult:
        return False
    return True


def _detect_failed_breakdown_down(
    row: pd.Series,
    *,
    tick: float,
    wick_body_mult: float,
    max_body_ratio: float,
    breakout_ticks: float,
) -> bool:
    if pd.isna(row["prev_low"]) or pd.isna(row["atr20"]):
        return False
    prev_low = float(row["prev_low"])
    if row["low"] >= prev_low - breakout_ticks * tick:
        return False
    if row["close"] <= prev_low:
        return False
    if row["body_ratio"] >= max_body_ratio:
        return False
    if row["body"] <= 0:
        return row["lower_wick"] > 0
    if row["lower_wick"] <= row["body"] * wick_body_mult:
        return False
    return True


def _simulate_short(
    df: pd.DataFrame,
    i: int,
    *,
    tick: float,
    entry_type: str,
    stop_window: int,
    max_hold: int,
) -> EventOutcome:
    row = df.iloc[i]
    signal_high = float(row["high"])
    signal_low = float(row["low"])
    stop_price = signal_high + tick
    stop_entry = signal_low - tick
    risk = stop_price - stop_entry
    target = stop_entry - risk

    if risk <= tick:
        return EventOutcome(entry_type, False, 0.0, "SKIP", 0.0, 0.0, 0.0, 0, False, False)

    entry_price = 0.0
    entry_bar = -1

    if entry_type == "market":
        entry_price = float(row["close"])
        entry_bar = i
    else:
        for j in range(1, stop_window + 1):
            if i + j >= len(df):
                break
            bar = df.iloc[i + j]
            if bar["low"] <= stop_entry:
                entry_price = min(float(bar["open"]), stop_entry)
                entry_bar = i + j
                break
        if entry_bar < 0:
            return EventOutcome(entry_type, False, 0.0, "NO_FILL", 0.0, 0.0, 0.0, 0, False, False)

    mfe = 0.0
    mae = 0.0
    exit_reason = "TIME"
    exit_price = float(df.iloc[min(entry_bar + max_hold, len(df) - 1)]["close"])
    hit_1r = False
    hit_stop = False
    bars_held = 0

    for j in range(1, max_hold + 1):
        if entry_bar + j >= len(df):
            break
        bar = df.iloc[entry_bar + j]
        bars_held = j
        bar_high = float(bar["high"])
        bar_low = float(bar["low"])
        bar_open = float(bar["open"])

        mfe = max(mfe, entry_price - bar_low)
        mae = max(mae, bar_high - entry_price)

        stop_hit = bar_high >= stop_price
        target_hit = bar_low <= target
        if stop_hit and target_hit:
            exit_reason = "STOP"
            exit_price = max(bar_open, stop_price)
            hit_stop = True
            break
        if stop_hit:
            exit_reason = "STOP"
            exit_price = max(bar_open, stop_price)
            hit_stop = True
            break
        if target_hit:
            exit_reason = "TARGET"
            exit_price = min(bar_open, target)
            hit_1r = True
            break
        exit_price = float(bar["close"])

    return EventOutcome(
        entry_type=entry_type,
        filled=True,
        entry_price=entry_price,
        exit_reason=exit_reason,
        exit_price=exit_price,
        mfe_ticks=mfe / tick,
        mae_ticks=mae / tick,
        bars_held=bars_held,
        hit_1r=hit_1r,
        hit_stop=hit_stop,
    )


def _simulate_long(
    df: pd.DataFrame,
    i: int,
    *,
    tick: float,
    entry_type: str,
    stop_window: int,
    max_hold: int,
) -> EventOutcome:
    row = df.iloc[i]
    signal_high = float(row["high"])
    signal_low = float(row["low"])
    stop_price = signal_low - tick
    stop_entry = signal_high + tick
    risk = stop_entry - stop_price
    target = stop_entry + risk

    if risk <= tick:
        return EventOutcome(entry_type, False, 0.0, "SKIP", 0.0, 0.0, 0.0, 0, False, False)

    entry_price = 0.0
    entry_bar = -1

    if entry_type == "market":
        entry_price = float(row["close"])
        entry_bar = i
    else:
        for j in range(1, stop_window + 1):
            if i + j >= len(df):
                break
            bar = df.iloc[i + j]
            if bar["high"] >= stop_entry:
                entry_price = max(float(bar["open"]), stop_entry)
                entry_bar = i + j
                break
        if entry_bar < 0:
            return EventOutcome(entry_type, False, 0.0, "NO_FILL", 0.0, 0.0, 0.0, 0, False, False)

    mfe = 0.0
    mae = 0.0
    exit_reason = "TIME"
    exit_price = float(df.iloc[min(entry_bar + max_hold, len(df) - 1)]["close"])
    hit_1r = False
    hit_stop = False
    bars_held = 0

    for j in range(1, max_hold + 1):
        if entry_bar + j >= len(df):
            break
        bar = df.iloc[entry_bar + j]
        bars_held = j
        bar_high = float(bar["high"])
        bar_low = float(bar["low"])
        bar_open = float(bar["open"])

        mfe = max(mfe, bar_high - entry_price)
        mae = max(mae, entry_price - bar_low)

        stop_hit = bar_low <= stop_price
        target_hit = bar_high >= target
        if stop_hit and target_hit:
            exit_reason = "STOP"
            exit_price = min(bar_open, stop_price)
            hit_stop = True
            break
        if stop_hit:
            exit_reason = "STOP"
            exit_price = min(bar_open, stop_price)
            hit_stop = True
            break
        if target_hit:
            exit_reason = "TARGET"
            exit_price = max(bar_open, target)
            hit_1r = True
            break
        exit_price = float(bar["close"])

    return EventOutcome(
        entry_type=entry_type,
        filled=True,
        entry_price=entry_price,
        exit_reason=exit_reason,
        exit_price=exit_price,
        mfe_ticks=mfe / tick,
        mae_ticks=mae / tick,
        bars_held=bars_held,
        hit_1r=hit_1r,
        hit_stop=hit_stop,
    )


def _forward_excursion(
    df: pd.DataFrame,
    i: int,
    *,
    direction: str,
    tick: float,
    max_hold: int,
) -> tuple[float, float]:
    """信号 bar 收盘后 max_hold 根内的 MFE/MAE（ticks），不含入场滑点假设。"""
    if i + 1 >= len(df):
        return 0.0, 0.0
    ref = float(df.iloc[i]["close"])
    mfe = 0.0
    mae = 0.0
    end = min(i + max_hold, len(df) - 1)
    for j in range(i + 1, end + 1):
        bar = df.iloc[j]
        if direction == "short":
            mfe = max(mfe, ref - float(bar["low"]))
            mae = max(mae, float(bar["high"]) - ref)
        else:
            mfe = max(mfe, float(bar["high"]) - ref)
            mae = max(mae, ref - float(bar["low"]))
    return mfe / tick, mae / tick


def _summarize_outcomes(outcomes: list[EventOutcome], tick: float) -> dict:
    filled = [o for o in outcomes if o.filled]
    if not filled:
        return {"n": 0}
    pnls = [(o.entry_price - o.exit_price) / tick for o in filled]  # short PnL in ticks
    return {
        "n": len(filled),
        "fill_rate": len(filled) / len(outcomes) if outcomes else 0.0,
        "target_rate": sum(o.hit_1r for o in filled) / len(filled),
        "stop_rate": sum(o.hit_stop for o in filled) / len(filled),
        "time_rate": sum(o.exit_reason == "TIME" for o in filled) / len(filled),
        "avg_mfe": float(np.mean([o.mfe_ticks for o in filled])),
        "med_mfe": float(np.median([o.mfe_ticks for o in filled])),
        "avg_mae": float(np.mean([o.mae_ticks for o in filled])),
        "med_mae": float(np.median([o.mae_ticks for o in filled])),
        "avg_pnl_ticks": float(np.mean(pnls)),
        "med_pnl_ticks": float(np.median(pnls)),
        "wr": sum(p > 0 for p in pnls) / len(pnls),
    }


def _summarize_outcomes_long(outcomes: list[EventOutcome], tick: float) -> dict:
    filled = [o for o in outcomes if o.filled]
    if not filled:
        return {"n": 0}
    pnls = [(o.exit_price - o.entry_price) / tick for o in filled]
    return {
        "n": len(filled),
        "fill_rate": len(filled) / len(outcomes) if outcomes else 0.0,
        "target_rate": sum(o.hit_1r for o in filled) / len(filled),
        "stop_rate": sum(o.hit_stop for o in filled) / len(filled),
        "time_rate": sum(o.exit_reason == "TIME" for o in filled) / len(filled),
        "avg_mfe": float(np.mean([o.mfe_ticks for o in filled])),
        "med_mfe": float(np.median([o.mfe_ticks for o in filled])),
        "avg_mae": float(np.mean([o.mae_ticks for o in filled])),
        "med_mae": float(np.median([o.mae_ticks for o in filled])),
        "avg_pnl_ticks": float(np.mean(pnls)),
        "med_pnl_ticks": float(np.median(pnls)),
        "wr": sum(p > 0 for p in pnls) / len(pnls),
    }


def run_event_study(
    symbol: str,
    *,
    data: str = "1m",
    start: datetime | None = None,
    end: datetime | None = None,
    lookback: int = 20,
    climax_threshold: float = 2.0,
    stop_window: int = 1,
    max_hold: int = 10,
    verbose: bool = True,
) -> dict:
    start = start or datetime(2025, 1, 1)
    end = end or datetime(2026, 6, 30)
    profile = resolve_symbol_profile(symbol, ROOT)
    tick = float(profile["pricetick"])

    df = _load_bars_df(symbol, data=data, start=start, end=end)
    df = _calc_indicators(df, lookback=lookback, ema_period=20, atr_period=20)

    n_bars = len(df)
    trading_days = df["dt_cst"].dt.date.nunique()

    breakout_up = (df["high"] > df["prev_high"]).sum()
    breakout_down = (df["low"] < df["prev_low"]).sum()

    failed_up_idx: list[int] = []
    failed_down_idx: list[int] = []
    for i in range(len(df)):
        row = df.iloc[i]
        if _detect_failed_breakout_up(
            row, tick=tick, wick_body_mult=1.5, max_body_ratio=0.4, breakout_ticks=2.0
        ):
            failed_up_idx.append(i)
        if _detect_failed_breakdown_down(
            row, tick=tick, wick_body_mult=1.5, max_body_ratio=0.4, breakout_ticks=2.0
        ):
            failed_down_idx.append(i)

    climax_up_idx = [
        i for i in failed_up_idx if float(df.iloc[i]["climax_up"]) > climax_threshold
    ]
    climax_down_idx = [
        i for i in failed_down_idx if float(df.iloc[i]["climax_down"]) > climax_threshold
    ]

    # 信号 bar 后纯 forward MFE/MAE（close 基准）
    up_mfe = [_forward_excursion(df, i, direction="short", tick=tick, max_hold=max_hold) for i in failed_up_idx]
    up_climax_mfe = [_forward_excursion(df, i, direction="short", tick=tick, max_hold=max_hold) for i in climax_up_idx]

    stop_out_up = [
        _simulate_short(df, i, tick=tick, entry_type="stop", stop_window=stop_window, max_hold=max_hold)
        for i in failed_up_idx
    ]
    mkt_out_up = [
        _simulate_short(df, i, tick=tick, entry_type="market", stop_window=stop_window, max_hold=max_hold)
        for i in failed_up_idx
    ]
    stop_out_climax = [
        _simulate_short(df, i, tick=tick, entry_type="stop", stop_window=stop_window, max_hold=max_hold)
        for i in climax_up_idx
    ]
    mkt_out_climax = [
        _simulate_short(df, i, tick=tick, entry_type="market", stop_window=stop_window, max_hold=max_hold)
        for i in climax_up_idx
    ]

    result = {
        "symbol": symbol,
        "data_label": df.attrs.get("data_label", data),
        "start": start.date().isoformat(),
        "end": end.date().isoformat(),
        "n_bars": n_bars,
        "trading_days": trading_days,
        "breakout_up": int(breakout_up),
        "breakout_down": int(breakout_down),
        "failed_up": len(failed_up_idx),
        "failed_down": len(failed_down_idx),
        "climax_up": len(climax_up_idx),
        "climax_down": len(climax_down_idx),
        "failed_up_per_day": len(failed_up_idx) / trading_days if trading_days else 0.0,
        "climax_up_per_day": len(climax_up_idx) / trading_days if trading_days else 0.0,
        "forward_mfe_up": up_mfe,
        "forward_mfe_climax_up": up_climax_mfe,
        "stop_all_up": _summarize_outcomes(stop_out_up, tick),
        "market_all_up": _summarize_outcomes(mkt_out_up, tick),
        "stop_climax_up": _summarize_outcomes(stop_out_climax, tick),
        "market_climax_up": _summarize_outcomes(mkt_out_climax, tick),
    }

    if verbose:
        _print_report(result, tick=tick, climax_threshold=climax_threshold, stop_window=stop_window, max_hold=max_hold)

    return result


def _print_report(
    r: dict,
    *,
    tick: float,
    climax_threshold: float,
    stop_window: int,
    max_hold: int,
) -> None:
    def _pct(x: float) -> str:
        return f"{x:.1%}"

    def _f(x: float) -> str:
        return f"{x:.1f}"

    print(f"\n===== Failed Breakout Event Study | {r['symbol'].upper()} =====")
    print(f"数据: {r['data_label']} | 区间: {r['start']} ~ {r['end']}")
    print(f"1m bars: {r['n_bars']:,} | 交易日: {r['trading_days']}")
    print("-" * 50)
    print("【Step1 突破频率】")
    print(f"  向上突破 prev_high(20): {r['breakout_up']:,} ({r['breakout_up']/r['n_bars']:.2%} of bars)")
    print(f"  向下突破 prev_low(20):  {r['breakout_down']:,} ({r['breakout_down']/r['n_bars']:.2%} of bars)")
    print("【Step2 假突破 K（四条件）】")
    print(f"  向上假突破 (fade short): {r['failed_up']:,} | {r['failed_up_per_day']:.1f}/日")
    print(f"  向下假突破 (fade long):  {r['failed_down']:,}")
    print(f"  + Climax (>{climax_threshold} ATR):  {r['climax_up']:,} | {r['climax_up_per_day']:.1f}/日")
    if r["failed_up"]:
        mfe_all = [x[0] for x in r["forward_mfe_up"]]
        mae_all = [x[1] for x in r["forward_mfe_up"]]
        print("-" * 50)
        print(f"【信号后 {max_hold} bar Forward  excursion（close 基准，fade short）】")
        print(f"  全样本 MFE ticks: avg={_f(np.mean(mfe_all))} med={_f(np.median(mfe_all))}")
        print(f"  全样本 MAE ticks: avg={_f(np.mean(mae_all))} med={_f(np.median(mae_all))}")
        if r["climax_up"]:
            mfe_c = [x[0] for x in r["forward_mfe_climax_up"]]
            mae_c = [x[1] for x in r["forward_mfe_climax_up"]]
            print(f"  Climax  MFE ticks: avg={_f(np.mean(mfe_c))} med={_f(np.median(mfe_c))}")
            print(f"  Climax  MAE ticks: avg={_f(np.mean(mae_c))} med={_f(np.median(mae_c))}")

    def _print_sim(label: str, s: dict) -> None:
        if s.get("n", 0) == 0:
            print(f"  {label}: 无成交")
            return
        print(
            f"  {label}: n={s['n']} fill={_pct(s['fill_rate'])} "
            f"1R={_pct(s['target_rate'])} STOP={_pct(s['stop_rate'])} TIME={_pct(s['time_rate'])} "
            f"WR={_pct(s['wr'])} avgPnL={s['avg_pnl_ticks']:+.1f}t medPnL={s['med_pnl_ticks']:+.1f}t "
            f"MFE={s['avg_mfe']:.1f} MAE={s['avg_mae']:.1f}"
        )

    print("-" * 50)
    print(f"【1R 模拟 | stop_window={stop_window} | max_hold={max_hold} | 向上假突破→空】")
    _print_sim("Stop Entry  全样本", r["stop_all_up"])
    _print_sim("Market Entry 全样本", r["market_all_up"])
    _print_sim("Stop Entry  Climax", r["stop_climax_up"])
    _print_sim("Market Entry Climax", r["market_climax_up"])
    print("=" * 50)
    print("注: 未含手续费/滑点；先验 WR/PF 预期须以上表实证为准。")


def _compare_symbols(
    symbols: tuple[str, ...],
    *,
    data: str,
    start: datetime,
    end: datetime,
) -> None:
    rows = []
    for sym in symbols:
        r = run_event_study(sym, data=data, start=start, end=end, verbose=False)
        s = r["stop_climax_up"]
        rows.append(
            {
                "symbol": sym.upper(),
                "bars": r["n_bars"],
                "failed_up/day": r["failed_up_per_day"],
                "climax/day": r["climax_up_per_day"],
                "stop_fill": s.get("fill_rate", 0.0),
                "1R_rate": s.get("target_rate", 0.0),
                "WR": s.get("wr", 0.0),
                "avg_pnl_t": s.get("avg_pnl_ticks", 0.0),
            }
        )
    print("\n===== 品种对比（Climax + Stop Entry + 1R）=====")
    print(f"{'品种':<6} {'bars':>8} {'假突破/日':>10} {'Climax/日':>10} {'fill':>7} {'1R率':>7} {'WR':>7} {'avgPnL':>8}")
    print("-" * 72)
    for row in rows:
        print(
            f"{row['symbol']:<6} {row['bars']:>8,} {row['failed_up/day']:>10.1f} "
            f"{row['climax/day']:>10.1f} {row['stop_fill']:>6.1%} {row['1R_rate']:>6.1%} "
            f"{row['WR']:>6.1%} {row['avg_pnl_t']:>+8.1f}t"
        )
    print("=" * 72)


def main() -> None:
    parser = argparse.ArgumentParser(description="Failed Breakout 事件研究")
    parser.add_argument("--symbol", default="rb")
    parser.add_argument("--data", choices=("1m", "tick"), default="tick")
    parser.add_argument("--start", default="2025-01-01")
    parser.add_argument("--end", default="2026-06-30")
    parser.add_argument("--climax", type=float, default=2.0)
    parser.add_argument("--stop-window", type=int, default=1)
    parser.add_argument("--max-hold", type=int, default=10)
    parser.add_argument(
        "--compare",
        action="store_true",
        help="对比 rb/ma/ta/hc（Climax + Stop Entry 摘要）",
    )
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d")
    end = datetime.strptime(args.end, "%Y-%m-%d")

    if args.compare:
        _compare_symbols(("rb", "ma", "ta", "hc"), data=args.data, start=start, end=end)
        return

    run_event_study(
        args.symbol,
        data=args.data,
        start=start,
        end=end,
        climax_threshold=args.climax,
        stop_window=args.stop_window,
        max_hold=args.max_hold,
    )


if __name__ == "__main__":
    main()
