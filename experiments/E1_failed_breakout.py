# -*- coding: utf-8
"""BrooksFade E1 — Failed Breakout Event Study（委托 unified event_engine）。

用法::
  .venv\\Scripts\\python.exe experiments/E1_failed_breakout.py
  .venv\\Scripts\\python.exe -m research.run_event_study failed_breakout --symbol rb --legacy-output
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.event_engine.bars import load_bars
from research.event_engine.detectors import failed_breakout as _fb
from research.event_engine.forwards import attach_forwards
from research.event_engine.runner import EventStudyRunner  # noqa: E402
from research.event_engine.schema import FWD_HORIZONS, MFE_WINDOW, records_to_dataframe


def _prepare_features(df):
    """Legacy shim for E2 / context scripts."""
    return _fb.prepare_features(df)


def _detect_events(df):
    """Legacy shim: returns DataFrame with forwards (default symbol rb)."""
    recs = _fb.detect_events(df, symbol="rb")
    recs = attach_forwards(recs, df)
    out = records_to_dataframe(recs)
    if not out.empty:
        out["mfe_gt_1r"] = (out["mfe"] > out["one_r"]).astype(int)
    return out


def run_e1(
    *,
    input_path: Path | None = None,
    symbol: str = "rb",
    start: datetime | None = None,
    end: datetime | None = None,
    tick: float = 1.0,
    cost_ticks: float = 3.0,
    round2: bool = False,
    verbose: bool = True,
):
    events, summary, _gate = EventStudyRunner().run(
        "failed_breakout",
        symbol=symbol,
        input_path=input_path,
        start=start,
        end=end,
        tick=tick,
        cost_ticks=cost_ticks,
        round2=round2,
        legacy_output=True,
        verbose=verbose,
    )
    return events, summary


def main() -> None:
    parser = argparse.ArgumentParser(description="BrooksFade E1 Failed Breakout Event Study")
    parser.add_argument("--input", type=Path, default=None, help="Parquet 1m 路径（默认 TQ CbC）")
    parser.add_argument("--symbol", default="rb", help="TQ CbC 回退品种键")
    parser.add_argument("--start", default=None, help="YYYY-MM-DD")
    parser.add_argument("--end", default=None, help="YYYY-MM-DD")
    parser.add_argument("--tick", type=float, default=1.0, help="最小变动价位")
    parser.add_argument("--cost-ticks", type=float, default=3.0, help="往返成本 ticks（手续费+滑点）")
    parser.add_argument("--round2", action="store_true", help="Round 1 后输出 Filter A-D 分层")
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d") if args.start else None
    end = datetime.strptime(args.end, "%Y-%m-%d") if args.end else None

    run_e1(
        input_path=args.input,
        symbol=args.symbol,
        start=start,
        end=end,
        tick=args.tick,
        cost_ticks=args.cost_ticks,
        round2=args.round2,
    )


if __name__ == "__main__":
    main()
