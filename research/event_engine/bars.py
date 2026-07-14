# -*- coding: utf-8 -*-
"""Event Study 用 1m K 线加载。"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def load_parquet_1m(path: Path) -> pd.DataFrame:
    raw = pd.read_parquet(path)
    if isinstance(raw.index, pd.DatetimeIndex):
        raw = raw.reset_index()
    if "datetime" not in raw.columns:
        raise ValueError(f"{path} 缺少 datetime 列")
    dt = pd.to_datetime(raw["datetime"])
    if dt.dt.tz is None:
        dt = dt.dt.tz_localize("Asia/Shanghai")
    else:
        dt = dt.dt.tz_convert("Asia/Shanghai")
    out = pd.DataFrame(
        {
            "dt_cst": dt,
            "open": pd.to_numeric(raw["open"], errors="coerce"),
            "high": pd.to_numeric(raw["high"], errors="coerce"),
            "low": pd.to_numeric(raw["low"], errors="coerce"),
            "close": pd.to_numeric(raw["close"], errors="coerce"),
        }
    )
    return out.dropna(subset=["open", "high", "low", "close"]).sort_values("dt_cst")


def load_tq_cbc_1m(symbol: str) -> pd.DataFrame:
    from scripts.tq_rollover_data import build_stitched_raw_frame

    df = build_stitched_raw_frame(symbol)
    return df[["dt_cst", "open", "high", "low", "close"]].copy()


def load_bars(
    *,
    symbol: str,
    input_path: Path | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
) -> tuple[pd.DataFrame, str]:
    if input_path is not None:
        if not input_path.is_file():
            raise FileNotFoundError(f"输入文件不存在: {input_path}")
        bars, source = load_parquet_1m(input_path), input_path.name
    else:
        bars = load_tq_cbc_1m(symbol)
        source = f"TQ CbC {symbol} 分月1m拼接"

    if start is not None:
        bars = bars[bars["dt_cst"] >= pd.Timestamp(start, tz="Asia/Shanghai")]
    if end is not None:
        bars = bars[bars["dt_cst"] <= pd.Timestamp(end, tz="Asia/Shanghai")]
    bars = bars.sort_values("dt_cst").reset_index(drop=True)
    return bars, source


def resample_ohlc(bars_1m: pd.DataFrame, rule: str) -> pd.DataFrame:
    work = bars_1m.set_index("dt_cst")
    out = pd.DataFrame(
        {
            "open": work["open"].resample(rule).first(),
            "high": work["high"].resample(rule).max(),
            "low": work["low"].resample(rule).min(),
            "close": work["close"].resample(rule).last(),
        }
    ).dropna(subset=["close"])
    return out


def resample_minutes(bars: pd.DataFrame, minutes: int) -> pd.DataFrame:
    """1m OHLC → N 分钟 OHLC（dt_cst 列保留）。"""
    if minutes <= 1:
        return bars.sort_values("dt_cst").reset_index(drop=True)
    ohlc = resample_ohlc(bars, f"{minutes}min")
    out = ohlc.reset_index()
    if "dt_cst" not in out.columns:
        out = out.rename(columns={out.columns[0]: "dt_cst"})
    return out.sort_values("dt_cst").reset_index(drop=True)
