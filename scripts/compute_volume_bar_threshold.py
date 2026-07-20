# -*- coding: utf-8 -*-
"""标定等量K阈值 V_bar = Median(近 lookback 交易日的 5m 成交量)。

用主力连续 1m CbC 合成 5m 量，默认回看 20 个交易日。

用法::
  python scripts/compute_volume_bar_threshold.py --symbols rb,i,ma,ta
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.tq_data_loader import load_raw_dataframe
from strategies.pa_cta.symbol_config import TQ_SYMBOL_ENGINE


def _folder(symbol: str) -> str:
    key = symbol.lower()
    if key not in TQ_SYMBOL_ENGINE:
        raise ValueError(f"未知品种 {symbol}")
    return str(TQ_SYMBOL_ENGINE[key]["folder"])


def compute_v_bar(
    symbol: str,
    *,
    end: datetime | None = None,
    lookback_days: int = 20,
    scale: str = "5m",
    round_to: int = 0,
) -> dict:
    end = end or datetime(2026, 6, 30, 23, 59, 59)
    # 多取日历日，确保有足够交易日
    start = end - timedelta(days=max(lookback_days * 3, 60))
    folder = _folder(symbol)
    df = load_raw_dataframe(folder, start=start, end=end)
    if df.empty:
        raise RuntimeError(f"{symbol}: 无 1m 数据")
    # load_cbc 输出列名多为 open/high/low/close/volume + dt
    if "dt" not in df.columns:
        raise RuntimeError(f"{symbol}: 缺 dt 列，cols={list(df.columns)}")
    work = df.copy()
    work["dt"] = pd.to_datetime(work["dt"])
    work = work.sort_values("dt")
    work = work.set_index("dt")
    if scale == "1m":
        # 1m 尺度：直接用原始 1m 量（>0）
        vol = work["volume"]
    else:
        # 5m 合成量：resample 求和
        vol = work["volume"].resample("5min", label="left", closed="left").sum()
    vol = vol[vol > 0]
    if vol.empty:
        raise RuntimeError(f"{symbol}: {scale} 量序列为空")
    # 按交易日取最近 lookback_days 天内的全部量
    days = sorted({ts.date() for ts in vol.index})
    if len(days) < lookback_days:
        use_days = set(days)
    else:
        use_days = set(days[-lookback_days:])
    sample = vol[[d in use_days for d in vol.index.date]]
    med = float(np.median(sample.to_numpy(dtype=float)))
    v_int = int(round(med))
    if round_to and round_to > 0:
        v_int = int(round(med / round_to) * round_to)
    return {
        "symbol": symbol.lower(),
        "folder": folder,
        "scale": scale,
        "lookback_days": lookback_days,
        "n_days": len(use_days),
        "n_bars": int(len(sample)),
        "v_bar": med,
        "v_bar_int": v_int,
        "end": end.isoformat(sep=" ", timespec="seconds"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbols", default="rb,i,ma,ta")
    parser.add_argument("--lookback-days", type=int, default=20)
    parser.add_argument("--end", default="2026-06-30")
    parser.add_argument("--scale", choices=["1m", "5m"], default="5m")
    parser.add_argument("--round-to", type=int, default=0, help="取整到该整数倍；0=不取整")
    args = parser.parse_args()
    symbols = [s.strip().lower() for s in args.symbols.split(",") if s.strip()]
    end = datetime.strptime(args.end, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

    print(f"=== V_bar = Median({args.scale} volume) | lookback trading days ===")
    print(f"end={end.date()} lookback={args.lookback_days} round_to={args.round_to}\n")
    print(f"{'sym':<4} {'folder':<6} {'n_day':>5} {'n_bars':>7} {'V_bar':>12} {'int':>10}")
    print("-" * 52)
    rows = []
    for sym in symbols:
        row = compute_v_bar(
            sym, end=end, lookback_days=args.lookback_days,
            scale=args.scale, round_to=args.round_to,
        )
        rows.append(row)
        print(
            f"{row['symbol']:<4} {row['folder']:<6} {row['n_days']:>5} "
            f"{row['n_bars']:>7} {row['v_bar']:>12,.1f} {row['v_bar_int']:>10,}"
        )
    print(f"\n# 建议写入 VOLUME_BAR_THRESHOLDS ({args.scale}):")
    print("VOLUME_BAR_THRESHOLDS = {")
    for row in rows:
        print(f'    "{row["symbol"]}": {row["v_bar_int"]}.0,')
    print("}")


if __name__ == "__main__":
    main()
