# -*- coding: utf-8
"""EXP-007 — Breakout Pullback 多周期 Event Study。

用法::
  python -m research.run_bp_study --symbol rb
  python -m research.run_bp_study --symbol rb --start 2024-01-01 --end 2025-06-30
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.event_engine.timeframe_study import run_timeframe_study  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="EXP-007 Breakout Pullback Timeframe Selection")
    parser.add_argument("--symbol", default="rb")
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--start", default="2024-01-01")
    parser.add_argument("--end", default="2025-06-30")
    parser.add_argument("--tick", type=float, default=1.0)
    parser.add_argument("--cost-ticks", type=float, default=3.0)
    parser.add_argument(
        "--timeframes",
        default="3,5,10,15,30",
        help="comma-separated minutes",
    )
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d") if args.start else None
    end = datetime.strptime(args.end, "%Y-%m-%d") if args.end else None
    tfs = tuple(int(x.strip()) for x in args.timeframes.split(",") if x.strip())

    run_timeframe_study(
        "breakout_pullback",
        symbol=args.symbol,
        timeframes=tfs,
        input_path=args.input,
        start=start,
        end=end,
        tick=args.tick,
        cost_ticks=args.cost_ticks,
    )


if __name__ == "__main__":
    main()
