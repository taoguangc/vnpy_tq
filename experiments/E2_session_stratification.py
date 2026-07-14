# -*- coding: utf-8
"""E2 — 时段分层 Event Study（复用 pattern_delta_events.csv）。

在 E1 形态+微观事件上按交易时段分层，检验 edge 是否时段特异。
不写策略、不模拟下单。

时段（CST，RB 日/夜盘）::
  morning_0900_1030   09:00–10:30（开盘冲击）
  morning_1030_1130   10:30–11:30（小节恢复）
  afternoon_1330_1430 13:30–14:30（午后）
  afternoon_1430_1500 14:30–15:00（收盘前）
  night_2100_2300     21:00–23:00（夜盘）

微观子集（在 pattern 内计算分位）::
  ALL                 该 pattern 全部事件
  high_absorption     absorption ≥ 75% 分位
  high_abs+aligned    high_absorption 且 aligned_delta_30s > 0

成本 gate: net_after_cost = avg_future_10/tick - 3.0（往返 ~3 tick）

输入::
  experiments/output/pattern_delta_events.csv（默认）
  或 --input 指定 E1 输出

输出::
  experiments/output/session_strata_summary.csv
  experiments/output/session_strata_detail.csv

用法::
  .venv\\Scripts\\python.exe experiments/E2_session_stratification.py
  .venv\\Scripts\\python.exe experiments/E2_session_stratification.py \\
      --input experiments/output/pattern_delta_events.csv --min-n 30
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
DEFAULT_INPUT = OUTPUT_DIR / "pattern_delta_events.csv"
COST_TICKS = 3.0
FOCUS_PATTERNS = (
    "failed_breakout_up",
    "failed_breakdown_down",
    "failed_breakout_up|high_abs+aligned",
    "failed_breakdown_down|high_abs+aligned",
)

SESSIONS: list[tuple[str, tuple[tuple[int, int, int], tuple[int, int, int]]]] = [
    ("morning_0900_1030", ((9, 0, 0), (10, 30, 0))),
    ("morning_1030_1130", ((10, 30, 0), (11, 30, 0))),
    ("afternoon_1330_1430", ((13, 30, 0), (14, 30, 0))),
    ("afternoon_1430_1500", ((14, 30, 0), (15, 0, 0))),
    ("night_2100_2300", ((21, 0, 0), (23, 0, 0))),
]


def _time_in_session(ts: pd.Timestamp, start: tuple[int, int, int], end: tuple[int, int, int]) -> bool:
    t = ts.time()
    from datetime import time as dt_time

    lo = dt_time(*start)
    hi = dt_time(*end)
    if lo <= hi:
        return lo <= t < hi
    return t >= lo or t < hi


def assign_session(dt: pd.Series) -> pd.Series:
    ts = pd.to_datetime(dt)
    out = pd.Series("other", index=ts.index, dtype="object")
    for name, (start, end) in SESSIONS:
        mask = ts.apply(lambda x: _time_in_session(x, start, end))
        out.loc[mask] = name
    return out


def _stats(sub: pd.DataFrame, *, tick: float) -> dict:
    if sub.empty:
        return {
            "n": 0,
            "avg_future_10": np.nan,
            "wr": np.nan,
            "avg_mfe": np.nan,
            "avg_mae": np.nan,
            "net_after_cost": np.nan,
        }
    f10 = sub["future_10"] / tick
    return {
        "n": len(sub),
        "avg_future_10": float(f10.mean()),
        "wr": float((f10 > 0).mean()),
        "avg_mfe": float(sub["mfe"].mean() / tick),
        "avg_mae": float(sub["mae"].mean() / tick),
        "net_after_cost": float(f10.mean()) - COST_TICKS,
    }


def _micro_subsets(events: pd.DataFrame) -> list[tuple[str, pd.DataFrame]]:
    """返回 (subset_label, df) 列表；high_absorption 在 pattern 内算分位。"""
    out: list[tuple[str, pd.DataFrame]] = [("ALL", events)]
    if len(events) < 20:
        return out
    q75 = events["absorption"].quantile(0.75)
    ha = events[events["absorption"] >= q75]
    out.append(("high_absorption", ha))
    if len(ha) >= 10:
        out.append(("high_abs+aligned", ha[ha["aligned_delta_30s"] > 0]))
    return out


def build_summaries(events: pd.DataFrame, *, tick: float, min_n: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    events = events.copy()
    events["session"] = assign_session(events["datetime"])

    detail_rows: list[dict] = []
    summary_rows: list[dict] = []

    focus_patterns = {"failed_breakout_up", "failed_breakdown_down"}
    for pname in sorted(events["pattern"].unique()):
        pat = events[events["pattern"] == pname]
        for subset_label, sub in _micro_subsets(pat):
            seg_key = pname if subset_label == "ALL" else f"{pname}|{subset_label}"
            for sess_name, _ in SESSIONS:
                sess = sub[sub["session"] == sess_name]
                st = _stats(sess, tick=tick)
                row = {
                    "pattern": pname,
                    "micro_subset": subset_label,
                    "segment": seg_key,
                    "session": sess_name,
                    **st,
                }
                detail_rows.append(row)
                if pname in focus_patterns and st["n"] >= min_n:
                    summary_rows.append(row)

            other = sub[sub["session"] == "other"]
            st = _stats(other, tick=tick)
            detail_rows.append(
                {
                    "pattern": pname,
                    "micro_subset": subset_label,
                    "segment": seg_key,
                    "session": "other",
                    **st,
                }
            )

    detail = pd.DataFrame(detail_rows)
    summary = pd.DataFrame(summary_rows)
    if not summary.empty:
        summary = summary.sort_values(["segment", "avg_future_10"], ascending=[True, False])
    return summary, detail


def _gate_pass(row: pd.Series, *, min_n: int) -> bool:
    return (
        row["n"] >= min_n
        and pd.notna(row["net_after_cost"])
        and row["net_after_cost"] > 0
    )


def run_study(
    *,
    input_path: Path = DEFAULT_INPUT,
    tick: float = 1.0,
    min_n: int = 30,
    verbose: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not input_path.exists():
        raise FileNotFoundError(
            f"缺少 {input_path}，请先运行 experiments/E1_pattern_delta_micro.py --symbol rb"
        )

    events = pd.read_csv(input_path)
    summary, detail = build_summaries(events, tick=tick, min_n=min_n)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sp = OUTPUT_DIR / "session_strata_summary.csv"
    dp = OUTPUT_DIR / "session_strata_detail.csv"
    summary.to_csv(sp, index=False, encoding="utf-8-sig")
    detail.to_csv(dp, index=False, encoding="utf-8-sig")

    if verbose:
        _print_report(events, summary, detail, sp, dp, min_n=min_n)

    return summary, detail


def _print_report(
    events: pd.DataFrame,
    summary: pd.DataFrame,
    detail: pd.DataFrame,
    sp: Path,
    dp: Path,
    *,
    min_n: int,
) -> None:
    print("\n===== E2 时段分层 Event Study =====")
    print(f"输入事件: {len(events):,} | 成本假设: {COST_TICKS:.0f} tick 往返 | min_n={min_n}")
    print("-" * 72)

    focus = summary[
        summary["segment"].isin(
            [
                "failed_breakout_up",
                "failed_breakout_up|high_absorption",
                "failed_breakout_up|high_abs+aligned",
                "failed_breakdown_down",
                "failed_breakdown_down|high_absorption",
                "failed_breakdown_down|high_abs+aligned",
            ]
        )
    ].copy()

    if focus.empty:
        print("（无满足 min_n 的焦点 segment）")
    else:
        print(f"{'Segment':<42} {'Session':<22} {'N':>5} {'f10':>7} {'WR':>7} {'net':>7}")
        for seg in focus["segment"].unique():
            block = focus[focus["segment"] == seg].sort_values("avg_future_10", ascending=False)
            for _, row in block.iterrows():
                flag = " *" if _gate_pass(row, min_n=min_n) else ""
                print(
                    f"{row['segment']:<42} {row['session']:<22} {int(row['n']):5d} "
                    f"{row['avg_future_10']:+7.2f} {row['wr']:7.1%} {row['net_after_cost']:+7.2f}{flag}"
                )
            print()

    passed = summary[summary.apply(lambda r: _gate_pass(r, min_n=min_n), axis=1)]
    print("【成本 gate 通过】 net>0 且 n≥min_n")
    if passed.empty:
        print("  无 segment 通过成本 gate")
    else:
        for _, row in passed.sort_values("net_after_cost", ascending=False).iterrows():
            print(
                f"  {row['segment']:<40} {row['session']:<20} n={int(row['n']):4d} "
                f"f10={row['avg_future_10']:+.2f} net={row['net_after_cost']:+.2f}"
            )

    print("\n【全 pattern 时段最优（raw f10 top 5，n≥min_n）】")
    ok = summary[summary["n"] >= min_n].sort_values("avg_future_10", ascending=False).head(5)
    for _, row in ok.iterrows():
        print(
            f"  {row['segment']:<40} {row['session']:<20} n={int(row['n']):4d} "
            f"f10={row['avg_future_10']:+.2f} net={row['net_after_cost']:+.2f}"
        )

    print(f"\n输出:\n  {sp}\n  {dp}")
    print("=" * 72)
    print("* = 通过成本 gate（net>0）")


def main() -> None:
    parser = argparse.ArgumentParser(description="E2 时段分层 Event Study")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--tick", type=float, default=1.0)
    parser.add_argument("--min-n", type=int, default=30, help="汇总表最小样本量")
    args = parser.parse_args()

    run_study(input_path=args.input, tick=args.tick, min_n=args.min_n)


if __name__ == "__main__":
    main()
