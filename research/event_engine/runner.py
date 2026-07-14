# -*- coding: utf-8
"""Event Study 统一 runner。"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from research.event_engine.bars import load_bars
from research.event_engine.detectors import get_detector
from research.event_engine.features import attach_regime_features
from research.event_engine.forwards import attach_forwards
from research.event_engine.schema import (
    DEFAULT_COST_TICKS,
    records_to_dataframe,
)
from research.event_engine.adaptive_sizing import (
    attach_sizing,
    build_sizing_summary,
    sizing_gate_report,
)
from research.event_engine.market_state import SETUP_ALLOWED_STATES, attach_market_state
from research.event_engine.quality_report import build_quality_summary, quality_lift_report
from research.event_engine.quality_score import score_events
from research.event_engine.state_report import build_state_summary, state_matrix_report
from research.event_engine.summary import build_summary, gate_report

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "output"


class EventStudyRunner:
    def run(
        self,
        setup: str,
        *,
        symbol: str = "rb",
        input_path: Path | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
        tick: float = 1.0,
        cost_ticks: float = DEFAULT_COST_TICKS,
        attach_aff: bool = True,
        round2: bool = False,
        quality_score: bool = False,
        market_state: bool = False,
        adaptive_sizing: bool = False,
        output_dir: Path | None = None,
        legacy_output: bool = False,
        verbose: bool = True,
    ) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
        if adaptive_sizing:
            quality_score = True
            market_state = True

        spec = get_detector(setup)
        bars, source = load_bars(symbol=symbol, input_path=input_path, start=start, end=end)

        work = spec.prepare(bars) if spec.prepare is not None else bars
        records = spec.detect(work, symbol=symbol)
        records = attach_forwards(records, bars)
        if attach_aff or quality_score or market_state:
            records = attach_regime_features(records, bars)
        if market_state:
            records = attach_market_state(records, bars)

        events = records_to_dataframe(records)
        if not events.empty:
            events["mfe_gt_1r"] = (events["mfe"] > events["one_r"]).astype(int)
            if "setup_allowed" in events.columns:
                events["setup_allowed"] = events["setup_allowed"].astype(bool)

        quality_summary = None
        lift: dict = {}
        state_summary = None
        matrix: dict = {}
        if quality_score and not events.empty:
            events = score_events(events, spec.name)
            quality_summary = build_quality_summary(events, tick=tick, cost_ticks=cost_ticks)
            lift = quality_lift_report(quality_summary)

        if market_state and not events.empty:
            state_summary = build_state_summary(events, spec.name, tick=tick, cost_ticks=cost_ticks)
            matrix = state_matrix_report(state_summary, spec.name)
            if quality_score and "setup_allowed" in events.columns:
                allowed = events[events["setup_allowed"]]
                if not allowed.empty:
                    q_allowed = build_quality_summary(allowed, tick=tick, cost_ticks=cost_ticks)
                    quality_summary = q_allowed
                    lift = quality_lift_report(q_allowed)

        sizing_summary = None
        sizing_gate: dict = {}
        if adaptive_sizing and not events.empty:
            events = attach_sizing(events)
            sizing_summary = build_sizing_summary(events, tick=tick, cost_ticks=cost_ticks)
            sizing_gate = sizing_gate_report(sizing_summary)

        segment_fn = spec.segment if round2 else None
        if segment_fn is not None and not events.empty:
            events["_tick"] = tick

            def _wrapped(ev: pd.DataFrame):
                ev2 = ev.copy()
                if "breakout_size" in ev2.columns:
                    ev2["breakout_ticks"] = ev2["breakout_size"] / tick
                for label, sub in segment_fn(ev2):
                    yield label, sub

            segment_fn = _wrapped

        summary = build_summary(events, tick=tick, cost_ticks=cost_ticks, segment_fn=segment_fn)
        gate = gate_report(summary)

        out_dir = output_dir or DEFAULT_OUTPUT
        out_dir.mkdir(parents=True, exist_ok=True)
        setup_key = spec.name
        events_path = out_dir / f"events_{setup_key}_{symbol}.csv"
        summary_path = out_dir / f"summary_{setup_key}_{symbol}.csv"
        events.to_csv(events_path, index=False, encoding="utf-8-sig")
        summary.to_csv(summary_path, index=False, encoding="utf-8-sig")

        if quality_score and quality_summary is not None:
            q_events_path = out_dir / f"events_scored_{setup_key}_{symbol}.csv"
            q_summary_path = out_dir / f"quality_{setup_key}_{symbol}.csv"
            events.to_csv(q_events_path, index=False, encoding="utf-8-sig")
            quality_summary.to_csv(q_summary_path, index=False, encoding="utf-8-sig")
        else:
            q_events_path = q_summary_path = None

        state_summary_path = None
        if market_state and state_summary is not None:
            state_summary_path = out_dir / f"state_{setup_key}_{symbol}.csv"
            state_summary.to_csv(state_summary_path, index=False, encoding="utf-8-sig")
            if not events.empty:
                events.to_csv(
                    out_dir / f"events_state_{setup_key}_{symbol}.csv",
                    index=False,
                    encoding="utf-8-sig",
                )

        sizing_summary_path = None
        if adaptive_sizing and sizing_summary is not None:
            sizing_summary_path = out_dir / f"sizing_{setup_key}_{symbol}.csv"
            sizing_summary.to_csv(sizing_summary_path, index=False, encoding="utf-8-sig")
            events.to_csv(
                out_dir / f"events_sized_{setup_key}_{symbol}.csv",
                index=False,
                encoding="utf-8-sig",
            )

        if legacy_output and setup_key == "failed_breakout":
            legacy_dir = ROOT.parent / "experiments" / "output"
            legacy_dir.mkdir(parents=True, exist_ok=True)
            events.to_csv(legacy_dir / "failed_breakout_events.csv", index=False, encoding="utf-8-sig")
            summary.to_csv(legacy_dir / "summary.csv", index=False, encoding="utf-8-sig")

        if verbose:
            self._print_report(
                setup=setup_key,
                source=source,
                n_bars=len(bars),
                events=events,
                summary=summary,
                gate=gate,
                tick=tick,
                cost_ticks=cost_ticks,
                events_path=events_path,
                summary_path=summary_path,
                round2=round2,
                quality_summary=quality_summary,
                lift=lift,
                q_summary_path=q_summary_path,
                state_summary=state_summary,
                matrix=matrix,
                state_summary_path=state_summary_path,
                sizing_summary=sizing_summary,
                sizing_gate=sizing_gate,
                sizing_summary_path=sizing_summary_path,
            )

        result_gate = gate
        if quality_score and lift:
            result_gate = {**gate, "quality": lift}
        if market_state and matrix:
            result_gate = {**result_gate, "market_state": matrix}
        if adaptive_sizing and sizing_gate:
            result_gate = {**result_gate, "sizing": sizing_gate}

        return events, summary, result_gate

    @staticmethod
    def _print_report(
        *,
        setup: str,
        source: str,
        n_bars: int,
        events: pd.DataFrame,
        summary: pd.DataFrame,
        gate: dict,
        tick: float,
        cost_ticks: float,
        events_path: Path,
        summary_path: Path,
        round2: bool,
        quality_summary: pd.DataFrame | None = None,
        lift: dict | None = None,
        q_summary_path: Path | None = None,
        state_summary: pd.DataFrame | None = None,
        matrix: dict | None = None,
        state_summary_path: Path | None = None,
        sizing_summary: pd.DataFrame | None = None,
        sizing_gate: dict | None = None,
        sizing_summary_path: Path | None = None,
    ) -> None:
        r1 = summary.iloc[0]
        print(f"\n===== Event Study | {setup} | {events['symbol'].iloc[0] if not events.empty else '?'} =====")
        print(f"数据源: {source}")
        print(f"1m bars: {n_bars:,} | 事件数: {len(events):,}")
        if not events.empty:
            days = events["datetime"].apply(lambda x: pd.Timestamp(x).date()).nunique()
            print(
                f"事件涉及交易日: {days} | SHORT: {(events['direction']==-1).sum()} "
                f"| LONG: {(events['direction']==1).sum()}"
            )
        print("-" * 55)
        print("【Gate: n>=30 & net@cost h=10>0】")
        net_h10 = gate.get("net_h10")
        net_str = f"{net_h10:+.2f}" if net_h10 == net_h10 else "nan"
        print(f"  Gate: {gate['gate']} | n={gate['n']} | net_h10={net_str} ticks (@{cost_ticks:.0f}t cost)")
        for h in (5, 10, 20, 40, 80):
            col = f"avg_future_{h}"
            if col in r1 and r1[col] == r1[col]:
                print(f"  Avg future_{h}: {r1[col]:+.2f} ticks")
        print(f"  Avg MFE: {r1.get('avg_mfe', np.nan):.2f} | Avg MAE: {r1.get('avg_mae', np.nan):.2f}")
        print(f"  输出: {events_path}")
        print(f"        {summary_path}")
        if quality_summary is not None and not quality_summary.empty:
            print("-" * 55)
            print("【Quality Score | FULL>=0.8 HALF>=0.6 SKIP<0.6】")
            for _, row in quality_summary.iterrows():
                seg = row["segment"]
                if seg == "ALL":
                    continue
                net = row.get("net_after_cost_10", np.nan)
                net_s = f"{net:+.2f}" if net == net else "nan"
                print(
                    f"  {seg:<22} n={int(row['n']):4d} "
                    f"f10={row.get('avg_future_10', np.nan):+.2f}t net={net_s} "
                    f"gate={row.get('gate_pass', False)}"
                )
            if lift:
                print(
                    f"  Lift FULL vs ALL: {lift.get('lift', '?')} "
                    f"(Δnet={lift.get('lift_full_vs_all', 'n/a')})"
                )
            if q_summary_path:
                print(f"  Quality 输出: {q_summary_path}")
        if state_summary is not None and not state_summary.empty:
            allowed = SETUP_ALLOWED_STATES.get(setup, frozenset())
            print("-" * 55)
            print(f"【Market State | allowed={sorted(allowed)}】")
            for _, row in state_summary.iterrows():
                seg = row["segment"]
                if seg == "ALL":
                    continue
                net = row.get("net_after_cost_10", np.nan)
                net_s = f"{net:+.2f}" if net == net else "nan"
                print(
                    f"  {seg:<22} n={int(row['n']):4d} "
                    f"f10={row.get('avg_future_10', np.nan):+.2f}t net={net_s} "
                    f"gate={row.get('gate_pass', False)}"
                )
            if matrix:
                print(
                    f"  Matrix gate: {'PASS' if matrix.get('matrix_pass') else 'FAIL'} | "
                    f"ALLOWED n={matrix.get('allowed_n', 0)} "
                    f"net={matrix.get('allowed_net_h10', 'n/a')}"
                )
            if state_summary_path:
                print(f"  State 输出: {state_summary_path}")
        if sizing_summary is not None and not sizing_summary.empty:
            print("-" * 55)
            print("【Adaptive Sizing | size_mult = quality x state, deny=0】")
            for _, row in sizing_summary.iterrows():
                seg = row["segment"]
                wnet = row.get("weighted_net_h10", np.nan)
                wnet_s = f"{wnet:+.2f}" if wnet == wnet else "nan"
                net = row.get("net_after_cost_10", np.nan)
                net_s = f"{net:+.2f}" if net == net else "nan"
                ru = row.get("risk_units", 0)
                print(
                    f"  {seg:<18} n={int(row['n']):4d} ru={ru:6.1f} "
                    f"avg_net={net_s} w_net={wnet_s}"
                )
            if sizing_gate:
                print(
                    f"  Sizing gate: {sizing_gate.get('gate')} | "
                    f"active={sizing_gate.get('n_active', 0)} "
                    f"ru={sizing_gate.get('risk_units', 0):.1f} "
                    f"lift={sizing_gate.get('lift_vs_all', 'n/a')}"
                )
            if sizing_summary_path:
                print(f"  Sizing 输出: {sizing_summary_path}")
        if round2 and len(summary) > 1:
            print("\n【Round 2 分层 Top 8 by future_10】")
            sub = summary[summary["segment"] != "ALL"].copy()
            sub = sub.sort_values("avg_future_10", ascending=False).head(8)
            for _, row in sub.iterrows():
                print(
                    f"  {row['segment']:<18} n={int(row['n']):4d} "
                    f"f10={row['avg_future_10']:+.2f}t gate={row.get('gate_pass', False)}"
                )
        print("=" * 55)


def run_event_study(setup: str, **kwargs):
    return EventStudyRunner().run(setup, **kwargs)
