# -*- coding: utf-8
"""Phase-2：Production OPP 影子账本回测导出。

每个 production OPP 候选（含 gate 拦截 / arbitration 抢占 / 未成交）写入 CSV，
并附加 MFE/MAE、1R/2R、60/120min、EOD 含成本 forwards。

用法::
  python -m research.run_shadow_ledger --symbol rb
  python -m research.run_shadow_ledger --symbol rb --start 2024-01-01 --end 2025-12-31
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from strategies.pa_cta.backtest import run_parquet_backtest


def _parse_date(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d")


def main() -> None:
    parser = argparse.ArgumentParser(description="Production OPP 影子账本（Phase-2）")
    parser.add_argument("--symbol", default="rb", help="品种，如 rb hc ma")
    parser.add_argument("--start", default=None, help="YYYY-MM-DD")
    parser.add_argument("--end", default=None, help="YYYY-MM-DD")
    parser.add_argument("--zero-cost", action="store_true", help="零成本 forwards 对照")
    parser.add_argument(
        "--output",
        default=None,
        help="CSV 输出路径（默认 research/output/shadow_ledger_{symbol}.csv）",
    )
    args = parser.parse_args()

    start = _parse_date(args.start) if args.start else None
    end = _parse_date(args.end) if args.end else None
    out_path = Path(args.output) if args.output else None

    overrides: dict = {"shadow_ledger_enabled": True}
    if out_path is not None:
        overrides["shadow_export_path"] = str(out_path)

    print(f"=== Phase-2 Production OPP 影子账本 | {args.symbol} ===")
    result = run_parquet_backtest(
        symbol=args.symbol,
        zero_cost=args.zero_cost,
        verbose=True,
        start=start,
        end=end,
        strategy_overrides=overrides,
    )

    shadow_path = result.get("shadow_ledger_path")
    shadow_count = result.get("shadow_ledger_count", 0)
    if shadow_path:
        print(f"\n完成: {shadow_count:,} 条候选 → {shadow_path}")
    else:
        print("\n警告: 未生成影子账本（shadow_ledger_enabled 或零候选）")


if __name__ == "__main__":
    main()
