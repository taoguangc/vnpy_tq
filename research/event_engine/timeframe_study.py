# -*- coding: utf-8
"""EXP-006A — 同一 Setup 多周期 Event Study 对照。"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from research.event_engine.bars import load_bars, resample_minutes
from research.event_engine.detectors import get_detector
from research.event_engine.forwards import attach_forwards
from research.event_engine.schema import DEFAULT_COST_TICKS, DEFAULT_COST_TICKS_ALT, records_to_dataframe

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "output"
DEFAULT_TIMEFRAMES = (3, 5, 10, 15, 30)


def _exp_tag(setup: str) -> tuple[str, str]:
    """返回 (实验标签, 输出文件前缀)。"""
    if setup == "breakout_pullback":
        return "EXP-007A", "exp007a"
    if setup in ("failed_breakout", "S3", "S3_failed_breakout"):
        return "EXP-008A", "exp008a"
    return "EXP-006A", "exp006a"


def _metrics_row(
    events: pd.DataFrame,
    *,
    timeframe: int,
    tick: float,
    cost_ticks: float,
    cost_ticks_alt: float,
    wall_clock_h10_min: int,
) -> dict:
    row: dict = {
        "timeframe_m": timeframe,
        "bar_interval": f"{timeframe}m",
        "wall_clock_h10_min": wall_clock_h10_min,
        "n": len(events),
    }
    if events.empty:
        row.update(
            {
                "wr": np.nan,
                "pf": np.nan,
                "avg_f10_ticks": np.nan,
                "net_at_3": np.nan,
                "net_at_2": np.nan,
                "avg_mfe_ticks": np.nan,
                "avg_mae_ticks": np.nan,
                "gate_pass_n30_net3": False,
            }
        )
        return row

    f10 = events["future_10"] / tick
    wins = f10[f10 > 0]
    losses = f10[f10 < 0]
    gross_win = float(wins.sum()) if len(wins) else 0.0
    gross_loss = float(-losses.sum()) if len(losses) else 0.0
    pf = gross_win / gross_loss if gross_loss > 0 else np.nan

    avg_f10 = float(f10.mean())
    net3 = avg_f10 - cost_ticks
    net2 = avg_f10 - cost_ticks_alt

    row.update(
        {
            "wr": float((f10 > 0).mean()),
            "pf": pf,
            "avg_f10_ticks": avg_f10,
            "net_at_3": net3,
            "net_at_2": net2,
            "avg_mfe_ticks": float(events["mfe"].mean() / tick),
            "avg_mae_ticks": float(events["mae"].mean() / tick),
            "gate_pass_n30_net3": len(events) >= 30 and net3 > 0,
        }
    )
    return row


def run_timeframe_study(
    setup: str,
    *,
    symbol: str = "rb",
    timeframes: tuple[int, ...] = DEFAULT_TIMEFRAMES,
    input_path: Path | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    tick: float = 1.0,
    cost_ticks: float = DEFAULT_COST_TICKS,
    cost_ticks_alt: float = DEFAULT_COST_TICKS_ALT,
    output_dir: Path | None = None,
    verbose: bool = True,
) -> pd.DataFrame:
    spec = get_detector(setup)
    bars_1m, source = load_bars(symbol=symbol, input_path=input_path, start=start, end=end)

    rows: list[dict] = []
    out_dir = output_dir or DEFAULT_OUTPUT
    out_dir.mkdir(parents=True, exist_ok=True)

    for tf in timeframes:
        bars = resample_minutes(bars_1m, tf)
        work = spec.prepare(bars) if spec.prepare is not None else bars
        records = spec.detect(work, symbol=symbol)
        for rec in records:
            rec.bar_interval = f"{tf}m"
        records = attach_forwards(records, bars)
        events = records_to_dataframe(records)
        if not events.empty:
            events["mfe_gt_1r"] = (events["mfe"] > events["one_r"]).astype(int)

        rows.append(
            _metrics_row(
                events,
                timeframe=tf,
                tick=tick,
                cost_ticks=cost_ticks,
                cost_ticks_alt=cost_ticks_alt,
                wall_clock_h10_min=tf * 10,
            )
        )

        events_path = out_dir / f"events_{spec.name}_{symbol}_{tf}m.csv"
        events.to_csv(events_path, index=False, encoding="utf-8-sig")

    compare = pd.DataFrame(rows)
    tag_prefix = _exp_tag(spec.name)[1]
    compare_path = out_dir / f"{tag_prefix}_timeframe_{spec.name}_{symbol}.csv"
    compare.to_csv(compare_path, index=False, encoding="utf-8-sig")

    if verbose:
        _print_report(
            setup=spec.name,
            symbol=symbol,
            source=source,
            n_bars_1m=len(bars_1m),
            compare=compare,
            compare_path=compare_path,
            cost_ticks=cost_ticks,
            cost_ticks_alt=cost_ticks_alt,
        )

    return compare


def _print_report(
    *,
    setup: str,
    symbol: str,
    source: str,
    n_bars_1m: int,
    compare: pd.DataFrame,
    compare_path: Path,
    cost_ticks: float,
    cost_ticks_alt: float,
) -> None:
    exp_label, _ = _exp_tag(setup)
    print(f"\n===== {exp_label} Timeframe Selection | {setup} | {symbol} =====")
    print(f"数据源: {source} | 1m bars: {n_bars_1m:,}")
    print(f"forward: f10 = 10 bars @ each TF（wall-clock 见 wall_clock_h10_min 列）")
    print("-" * 72)
    print(
        f"{'TF':>4} {'n':>6} {'WR':>7} {'PF':>6} {'f10':>8} "
        f"{'net@3':>8} {'net@2':>8} {'gate':>5}"
    )
    print("-" * 72)
    for _, r in compare.iterrows():
        wr = f"{r['wr']:.1%}" if r["wr"] == r["wr"] else "  n/a"
        pf = f"{r['pf']:.2f}" if r["pf"] == r["pf"] else " n/a"
        f10 = f"{r['avg_f10_ticks']:+.2f}" if r["avg_f10_ticks"] == r["avg_f10_ticks"] else "    n/a"
        n3 = f"{r['net_at_3']:+.2f}" if r["net_at_3"] == r["net_at_3"] else "    n/a"
        n2 = f"{r['net_at_2']:+.2f}" if r["net_at_2"] == r["net_at_2"] else "    n/a"
        gate = "PASS" if r.get("gate_pass_n30_net3") else "FAIL"
        print(
            f"{int(r['timeframe_m']):>3}m {int(r['n']):>6} {wr:>7} {pf:>6} {f10:>8} "
            f"{n3:>8} {n2:>8} {gate:>5}"
        )
    print("-" * 72)
    passed = compare[compare["gate_pass_n30_net3"] == True]  # noqa: E712
    if not passed.empty:
        best = passed.sort_values("net_at_3", ascending=False).iloc[0]
        print(
            f"过 gate 最优（net@3）: {int(best['timeframe_m'])}m "
            f"n={int(best['n'])} net@3={best['net_at_3']:+.2f}"
        )
    else:
        print("无 TF 过 gate（n>=30 & net@3>0）— 待验证假设，不能宣布最优周期")
    print(f"输出: {compare_path}")
    print("=" * 72)
