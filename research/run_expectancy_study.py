# -*- coding: utf-8
"""EXP-006 — First Pullback Expectancy Surface。

用法::
  python -m research.run_expectancy_study --symbol rb --timeframe 30
  python -m research.run_expectancy_study --symbol rb --timeframe 30 --start 2024-01-01 --end 2025-06-30
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.event_engine.expectancy_surface import run_expectancy_study  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="EXP-006 FP Expectancy Surface")
    parser.add_argument("--setup", default="first_pullback")
    parser.add_argument("--symbol", default="rb")
    parser.add_argument("--timeframe", type=int, default=30, help="minutes (006A rb PASS TF)")
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--start", default="2024-01-01")
    parser.add_argument("--end", default="2025-06-30")
    parser.add_argument(
        "--direction",
        choices=("all", "short", "long"),
        default="all",
        help="cohort filter: short=-1, long=1",
    )
    parser.add_argument(
        "--is-start",
        default=None,
        help="in-sample sub-window start for OOS split report (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--is-end",
        default=None,
        help="in-sample sub-window end for OOS split report (YYYY-MM-DD)",
    )
    parser.add_argument("--tick", type=float, default=1.0)
    parser.add_argument("--cost-ticks", type=float, default=3.0)
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d") if args.start else None
    end = datetime.strptime(args.end, "%Y-%m-%d") if args.end else None
    is_start = datetime.strptime(args.is_start, "%Y-%m-%d") if args.is_start else None
    is_end = datetime.strptime(args.is_end, "%Y-%m-%d") if args.is_end else None
    direction = {"all": None, "short": -1, "long": 1}[args.direction]

    run_expectancy_study(
        args.setup,
        symbol=args.symbol,
        timeframe_min=args.timeframe,
        input_path=args.input,
        start=start,
        end=end,
        direction=direction,
        is_start=is_start,
        is_end=is_end,
        tick=args.tick,
        cost_ticks=args.cost_ticks,
    )


if __name__ == "__main__":
    main()
