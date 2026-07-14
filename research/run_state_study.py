# -*- coding: utf-8
"""CLI: Phase 4 Market State + Setup 允许矩阵。

用法::
  python -m research.run_state_study compression_breakout --symbol rb
  python -m research.run_state_study S3 --symbol rb --start 2024-01-01 --end 2024-06-01 --quality
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.event_engine.runner import EventStudyRunner  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Event Study + Market State matrix (Phase 4)")
    parser.add_argument("setup", help="failed_breakout|S3, compression_breakout|S1, first_pullback|S2")
    parser.add_argument("--symbol", default="rb")
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--start", default=None, help="YYYY-MM-DD")
    parser.add_argument("--end", default=None, help="YYYY-MM-DD")
    parser.add_argument("--tick", type=float, default=1.0)
    parser.add_argument("--cost-ticks", type=float, default=3.0)
    parser.add_argument("--quality", action="store_true", help="Quality score on ALLOWED cohort")
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d") if args.start else None
    end = datetime.strptime(args.end, "%Y-%m-%d") if args.end else None

    EventStudyRunner().run(
        args.setup,
        symbol=args.symbol,
        input_path=args.input,
        start=start,
        end=end,
        tick=args.tick,
        cost_ticks=args.cost_ticks,
        attach_aff=True,
        market_state=True,
        quality_score=args.quality,
    )


if __name__ == "__main__":
    main()
