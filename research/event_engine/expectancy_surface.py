# -*- coding: utf-8
"""EXP-006 — First Pullback Expectancy Surface（trend_leg × pullback × signal）。"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from research.event_engine.bars import load_bars, resample_minutes
from research.event_engine.detectors import get_detector
from research.event_engine.forwards import attach_forwards
from research.event_engine.schema import (
    DEFAULT_COST_TICKS,
    DEFAULT_COST_TICKS_ALT,
    records_to_dataframe,
)
from research.event_engine.summary import build_summary, gate_report, verdict_row

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "output"

# 与 first_pullback detector 阈值对齐的可解释分档
TREND_LEG_BINS = (1.5, 2.5)  # weak | mid | strong
PULLBACK_DEPTH_BINS = (0.25, 0.5)  # shallow | mid | deep
BODY_RATIO_BINS = (0.5, 0.65)  # weak | mid | strong signal bar


def _quartile_segments(events: pd.DataFrame, col: str, prefix: str):
    if events.empty or col not in events.columns:
        return
    try:
        for q, sub in events.groupby(
            pd.qcut(events[col], 4, duplicates="drop"), observed=True
        ):
            yield f"{prefix} Q{q}", sub
    except ValueError:
        return


def _fixed_bin(value: float, edges: tuple[float, ...], labels: tuple[str, ...]) -> str:
    for edge, label in zip(edges, labels[:-1]):
        if value < edge:
            return label
    return labels[-1]


def fp_expectancy_segments(events: pd.DataFrame):
    """1D 分层：方向 + 结构特征四分位 + 可解释固定档。"""
    if events.empty:
        return

    yield "LONG", events[events["direction"] == 1]
    yield "SHORT", events[events["direction"] == -1]

    yield from _quartile_segments(events, "trend_leg_atr", "TrendLeg")
    yield from _quartile_segments(events, "pullback_depth_atr", "PullbackDepth")
    yield from _quartile_segments(events, "body_ratio", "SignalBody")

    if "trend_leg_atr" in events.columns:
        tl_labels = ("TL weak", "TL mid", "TL strong")
        for label in tl_labels:
            sub = events[
                events["trend_leg_atr"].apply(
                    lambda v: _fixed_bin(float(v), TREND_LEG_BINS, tl_labels) == label
                )
            ]
            if not sub.empty:
                yield label, sub

    if "pullback_depth_atr" in events.columns:
        pd_labels = ("PD shallow", "PD mid", "PD deep")
        for label in pd_labels:
            sub = events[
                events["pullback_depth_atr"].apply(
                    lambda v: _fixed_bin(float(v), PULLBACK_DEPTH_BINS, pd_labels) == label
                )
            ]
            if not sub.empty:
                yield label, sub


def build_surface_grid(
    events: pd.DataFrame,
    *,
    tick: float,
    cost_ticks: float = DEFAULT_COST_TICKS,
    primary_horizon: int = 10,
) -> pd.DataFrame:
    """2D 网格：trend_leg_atr × pullback_depth_atr（固定三档）。"""
    if events.empty:
        return pd.DataFrame()

    tl_labels = ("TL weak", "TL mid", "TL strong")
    pd_labels = ("PD shallow", "PD mid", "PD deep")

    work = events.copy()
    work["tl_bin"] = work["trend_leg_atr"].apply(
        lambda v: _fixed_bin(float(v), TREND_LEG_BINS, tl_labels)
    )
    work["pd_bin"] = work["pullback_depth_atr"].apply(
        lambda v: _fixed_bin(float(v), PULLBACK_DEPTH_BINS, pd_labels)
    )

    rows: list[dict] = []
    for tl in tl_labels:
        for pd_l in pd_labels:
            sub = work[(work["tl_bin"] == tl) & (work["pd_bin"] == pd_l)]
            label = f"{tl} × {pd_l}"
            row = verdict_row(
                sub,
                tick=tick,
                cost_ticks=cost_ticks,
                label=label,
                primary_horizon=primary_horizon,
            )
            row["tl_bin"] = tl
            row["pd_bin"] = pd_l
            if not sub.empty and "future_10" in sub.columns:
                f10 = sub["future_10"] / tick
                wins = f10[f10 > 0]
                losses = f10[f10 < 0]
                gross_win = float(wins.sum()) if len(wins) else 0.0
                gross_loss = float(-losses.sum()) if len(losses) else 0.0
                row["wr"] = float((f10 > 0).mean())
                row["pf"] = gross_win / gross_loss if gross_loss > 0 else np.nan
            else:
                row["wr"] = np.nan
                row["pf"] = np.nan
            rows.append(row)
    return pd.DataFrame(rows)


def build_expectancy_summary(
    events: pd.DataFrame,
    *,
    tick: float,
    cost_ticks: float = DEFAULT_COST_TICKS,
    primary_horizon: int = 10,
) -> pd.DataFrame:
    return build_summary(
        events,
        tick=tick,
        cost_ticks=cost_ticks,
        primary_horizon=primary_horizon,
        segment_fn=fp_expectancy_segments,
    )


def _compact_row(summary_row: pd.Series) -> dict:
    n = int(summary_row.get("n", 0))
    avg_f10 = summary_row.get("avg_future_10", np.nan)
    net3 = summary_row.get("net_after_cost_10", np.nan)
    return {
        "segment": summary_row.get("segment"),
        "n": n,
        "wr": np.nan,
        "pf": np.nan,
        "avg_f10": avg_f10,
        "net_at_3": net3,
        "gate": bool(summary_row.get("gate_pass")),
    }


def _enrich_wr_pf(events: pd.DataFrame, summary: pd.DataFrame, *, tick: float) -> pd.DataFrame:
    """为打印表补充 WR / PF（summary 模块未含）。"""
    out = summary.copy()
    wr_list: list[float] = []
    pf_list: list[float] = []
    seg_col = out["segment"]

    for label in seg_col:
        if label == "ALL":
            sub = events
        elif label.startswith("LONG"):
            sub = events[events["direction"] == 1]
        elif label.startswith("SHORT"):
            sub = events[events["direction"] == -1]
        else:
            sub = pd.DataFrame()
            for seg_label, seg_sub in fp_expectancy_segments(events):
                if seg_label == label:
                    sub = seg_sub
                    break

        if sub.empty or "future_10" not in sub.columns:
            wr_list.append(np.nan)
            pf_list.append(np.nan)
            continue

        f10 = sub["future_10"] / tick
        wins = f10[f10 > 0]
        losses = f10[f10 < 0]
        gross_win = float(wins.sum()) if len(wins) else 0.0
        gross_loss = float(-losses.sum()) if len(losses) else 0.0
        wr_list.append(float((f10 > 0).mean()))
        pf_list.append(gross_win / gross_loss if gross_loss > 0 else np.nan)

    out["wr"] = wr_list
    out["pf"] = pf_list
    return out


def expectancy_lift_report(summary: pd.DataFrame) -> dict:
    if summary.empty:
        return {"lift": "NO_DATA"}
    all_row = summary[summary["segment"] == "ALL"]
    if all_row.empty:
        return {"lift": "NO_DATA"}
    all_net = all_row.iloc[0].get("net_after_cost_10")
    candidates = summary[(summary["segment"] != "ALL") & (summary["n"] >= 30)]
    if candidates.empty:
        return {"lift": "NONE", "all_net_h10": all_net, "best_segment": None}
    best = candidates.sort_values("net_after_cost_10", ascending=False).iloc[0]
    best_net = best.get("net_after_cost_10")
    out = {
        "all_n": int(all_row.iloc[0]["n"]),
        "all_net_h10": all_net,
        "best_segment": str(best["segment"]),
        "best_n": int(best["n"]),
        "best_net_h10": best_net,
        "best_gate": bool(best.get("gate_pass")),
    }
    if all_net == all_net and best_net == best_net:
        out["lift_vs_all"] = float(best_net) - float(all_net)
        out["lift"] = "POSITIVE" if best_net > all_net else "NEGATIVE"
    return out


def _cohort_gate_line(
    events: pd.DataFrame,
    label: str,
    *,
    tick: float,
    cost_ticks: float,
) -> str:
    row = verdict_row(events, tick=tick, cost_ticks=cost_ticks, label=label)
    n = int(row["n"])
    if n == 0:
        return f"{label:<22} n=0 —"
    f10 = row.get("avg_future_10", np.nan)
    net3 = row.get("net_after_cost_10", np.nan)
    g = "PASS" if row.get("gate_pass") else "FAIL"
    if "future_10" in events.columns and not events.empty:
        f10s = events["future_10"] / tick
        wr = float((f10s > 0).mean())
        wr_s = f"{wr * 100:.1f}%"
    else:
        wr_s = "—"
    f10_s = f"{f10:+.2f}" if f10 == f10 else "—"
    net3_s = f"{net3:+.2f}" if net3 == net3 else "—"
    return f"{label:<22} n={n:>4} WR={wr_s:>6} f10={f10_s:>7} net@3={net3_s:>7} {g}"


def _filter_events_by_time(
    events: pd.DataFrame,
    *,
    start: datetime | None = None,
    end: datetime | None = None,
) -> pd.DataFrame:
    if events.empty:
        return events
    dt = pd.to_datetime(events["datetime"])
    if dt.dt.tz is None:
        dt = dt.dt.tz_localize("Asia/Shanghai")
    mask = pd.Series(True, index=events.index)
    if start is not None:
        mask &= dt >= pd.Timestamp(start, tz="Asia/Shanghai")
    if end is not None:
        mask &= dt <= pd.Timestamp(end, tz="Asia/Shanghai")
    return events.loc[mask].reset_index(drop=True)


def run_expectancy_study(
    setup: str = "first_pullback",
    *,
    symbol: str = "rb",
    timeframe_min: int = 30,
    input_path: Path | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    direction: int | None = None,
    is_start: datetime | None = None,
    is_end: datetime | None = None,
    tick: float = 1.0,
    cost_ticks: float = DEFAULT_COST_TICKS,
    cost_ticks_alt: float = DEFAULT_COST_TICKS_ALT,
    output_dir: Path | None = None,
    verbose: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    spec = get_detector(setup)
    bars_1m, source = load_bars(symbol=symbol, input_path=input_path, start=start, end=end)
    bars = resample_minutes(bars_1m, timeframe_min)

    work = spec.prepare(bars) if spec.prepare is not None else bars
    records = spec.detect(work, symbol=symbol)
    for rec in records:
        rec.bar_interval = f"{timeframe_min}m"
    records = attach_forwards(records, bars)
    events = records_to_dataframe(records)
    if not events.empty:
        events["mfe_gt_1r"] = (events["mfe"] > events["one_r"]).astype(int)
        if direction is not None:
            events = events[events["direction"] == direction].reset_index(drop=True)

    summary = build_expectancy_summary(events, tick=tick, cost_ticks=cost_ticks)
    summary = _enrich_wr_pf(events, summary, tick=tick)
    surface = build_surface_grid(events, tick=tick, cost_ticks=cost_ticks)

    lift = expectancy_lift_report(summary)
    gate = gate_report(summary, cost_ticks_alt=cost_ticks_alt)

    out_dir = output_dir or DEFAULT_OUTPUT
    out_dir.mkdir(parents=True, exist_ok=True)
    dir_tag = ""
    if direction == 1:
        dir_tag = "_long"
    elif direction == -1:
        dir_tag = "_short"
    tag = f"exp006_{spec.name}_{symbol}_{timeframe_min}m{dir_tag}"
    events_path = out_dir / f"events_{tag}.csv"
    summary_path = out_dir / f"{tag}_summary.csv"
    surface_path = out_dir / f"{tag}_surface.csv"
    events.to_csv(events_path, index=False, encoding="utf-8-sig")
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")
    surface.to_csv(surface_path, index=False, encoding="utf-8-sig")

    if verbose:
        _print_report(
            setup=spec.name,
            symbol=symbol,
            timeframe_min=timeframe_min,
            source=source,
            n_bars=len(bars),
            events=events,
            summary=summary,
            surface=surface,
            gate=gate,
            lift=lift,
            cost_ticks=cost_ticks,
            tick=tick,
            direction=direction,
            window_start=start,
            window_end=end,
            is_start=is_start,
            is_end=is_end,
            paths=(events_path, summary_path, surface_path),
        )

    return events, summary, surface, {"gate": gate, "lift": lift}


def _print_report(
    *,
    setup: str,
    symbol: str,
    timeframe_min: int,
    source: str,
    n_bars: int,
    events: pd.DataFrame,
    summary: pd.DataFrame,
    surface: pd.DataFrame,
    gate: dict,
    lift: dict,
    cost_ticks: float,
    tick: float = 1.0,
    direction: int | None = None,
    window_start: datetime | None = None,
    window_end: datetime | None = None,
    is_start: datetime | None = None,
    is_end: datetime | None = None,
    paths: tuple[Path, Path, Path],
) -> None:
    dir_label = {1: "LONG-only", -1: "SHORT-only"}.get(direction, "ALL directions")
    print(f"\n===== EXP-006 Expectancy Surface | {setup} | {symbol} @ {timeframe_min}m | {dir_label} =====")
    if window_start or window_end:
        ws = window_start.date() if window_start else "…"
        we = window_end.date() if window_end else "…"
        print(f"窗口: {ws} ~ {we}")
    print(f"数据源: {source} | resampled bars: {n_bars:,} | events: {len(events)}")
    print(f"成本: net@3 = f10 − {cost_ticks} tick | gate: n≥30 & net@3>0")
    print("-" * 88)
    print(f"{'Segment':<28} {'n':>5} {'WR':>7} {'PF':>6} {'f10':>8} {'net@3':>8} {'Gate':>6}")
    print("-" * 88)
    for _, row in summary.iterrows():
        wr = row.get("wr", np.nan)
        pf = row.get("pf", np.nan)
        wr_s = f"{wr * 100:.1f}%" if wr == wr else "—"
        pf_s = f"{pf:.2f}" if pf == pf else "—"
        f10 = row.get("avg_future_10", np.nan)
        net3 = row.get("net_after_cost_10", np.nan)
        f10_s = f"{f10:+.2f}" if f10 == f10 else "—"
        net3_s = f"{net3:+.2f}" if net3 == net3 else "—"
        g = "PASS" if row.get("gate_pass") else "FAIL"
        print(
            f"{str(row['segment']):<28} {int(row['n']):>5} {wr_s:>7} {pf_s:>6} "
            f"{f10_s:>8} {net3_s:>8} {g:>6}"
        )

    print("\n--- 2D Surface (TrendLeg × PullbackDepth) ---")
    print(f"{'Cell':<32} {'n':>5} {'WR':>7} {'f10':>8} {'net@3':>8} {'Gate':>6}")
    print("-" * 72)
    for _, row in surface.iterrows():
        wr = row.get("wr", np.nan)
        wr_s = f"{wr * 100:.1f}%" if wr == wr else "—"
        f10 = row.get("avg_future_10", np.nan)
        net3 = row.get("net_after_cost_10", np.nan)
        f10_s = f"{f10:+.2f}" if f10 == f10 else "—"
        net3_s = f"{net3:+.2f}" if net3 == net3 else "—"
        g = "PASS" if row.get("gate_pass") else "FAIL"
        print(
            f"{str(row['segment']):<32} {int(row['n']):>5} {wr_s:>7} "
            f"{f10_s:>8} {net3_s:>8} {g:>6}"
        )

    print("-" * 88)
    print(f"ALL gate: {gate.get('gate')} | n={gate.get('n')} | net@3={gate.get('net_h10')}")
    if lift.get("best_segment"):
        print(
            f"最佳分层（n≥30）: {lift['best_segment']} n={lift['best_n']} "
            f"net@3={lift.get('best_net_h10')} gate={lift.get('best_gate')} "
            f"Δvs ALL={lift.get('lift_vs_all', '—')} ({lift.get('lift')})"
        )
    else:
        print("无 n≥30 分层 — 待验证假设")

    if is_start is not None and is_end is not None and not events.empty:
        print("\n--- 子窗口复验（同一批 events 切片，无二次检测）---")
        dt = pd.to_datetime(events["datetime"])
        if dt.dt.tz is None:
            dt = dt.dt.tz_localize("Asia/Shanghai")
        is_ts = pd.Timestamp(is_start, tz="Asia/Shanghai")
        ie_ts = pd.Timestamp(is_end, tz="Asia/Shanghai")
        is_ev = events[(dt >= is_ts) & (dt <= ie_ts)].reset_index(drop=True)
        pre_ev = events[dt < is_ts].reset_index(drop=True)
        post_ev = events[dt > ie_ts].reset_index(drop=True)
        if window_end is not None:
            we_ts = pd.Timestamp(window_end, tz="Asia/Shanghai")
            post_ev = post_ev[post_ev["datetime"].apply(
                lambda x: pd.Timestamp(x) <= we_ts
            )].reset_index(drop=True)
        print(_cohort_gate_line(events, "FULL", tick=tick, cost_ticks=cost_ticks))
        print(_cohort_gate_line(is_ev, "IN-SAMPLE", tick=tick, cost_ticks=cost_ticks))
        print(_cohort_gate_line(pre_ev, "OOS-PRE", tick=tick, cost_ticks=cost_ticks))
        print(_cohort_gate_line(post_ev, "OOS-POST", tick=tick, cost_ticks=cost_ticks))

    for p in paths:
        print(f"输出: {p}")
    print("=" * 88)
