"""将 data/tq/{prefix} 下的天勤(TQSDK)离线数据转换为 vnpy BarData 列表。

主路径（CbC，Contract-by-Contract）:
  - 分月原始无复权 parquet（rb_2410.parquet 等）
  - rollover_map.parquet 主力换月表
  - 按换月日切 bar 拼接主力序列，不做任何复权
  - 不依赖 *_continuous.parquet

单合约模式:
  - load_bars_from_tq(..., yymm="2410") 仅加载指定分月文件。

datetime 原始为 UTC 纳秒；输出 BarData 使用 Asia/Shanghai。
"""
from __future__ import annotations

import os
import sys
from datetime import date, datetime

import pandas as pd

from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.tq_parquet_io import load_monthly_parquet
DATA_DIR = os.path.join(ROOT, "data", "tq")

RAW_OHLCV_COLUMNS = ("datetime", "open", "high", "low", "close", "volume", "open_oi")

CZCE_YYMM_LEN3 = {
    "MA", "TA", "SA", "FG", "SR", "RM", "PF", "SF", "SM", "ZC",
    "CF", "CJ", "CY", "UR", "OI", "AP",
}


def _symbol_dir(prefix: str) -> str:
    return os.path.join(DATA_DIR, prefix)


def _monthly_path(prefix: str, yymm: str) -> str:
    return os.path.join(_symbol_dir(prefix), f"{prefix}_{yymm}.parquet")


def _rollover_map_path(prefix: str) -> str:
    return os.path.join(_symbol_dir(prefix), "rollover_map.parquet")


def yymm_len_for_prefix(prefix: str) -> int:
    return 4


def _rollover_event_date(record: dict | pd.Series) -> date:
    rd = record["rollover_date"]
    if isinstance(rd, pd.Timestamp):
        return rd.date()
    if isinstance(rd, datetime):
        return rd.date()
    return rd


def build_dominant_chain(rollover_map: pd.DataFrame) -> list[str]:
    """从 rollover_map 还原主力链：首段 from_yymm + 各段 to_yymm。"""
    if rollover_map.empty:
        raise ValueError("rollover_map 为空")
    df = rollover_map.sort_values("rollover_date").reset_index(drop=True)
    chain = [str(df.iloc[0]["from_yymm"])]
    for _, row in df.iterrows():
        chain.append(str(row["to_yymm"]))
    return chain


def ordered_rollover_events(rollover_map: pd.DataFrame) -> list[dict]:
    if rollover_map.empty:
        return []
    return (
        rollover_map.sort_values("rollover_date")
        .reset_index(drop=True)
        .to_dict("records")
    )


def slice_dominant_segment(
    df: pd.DataFrame,
    idx: int,
    chain_yymm: list[str],
    rollover_events: list[dict],
) -> pd.DataFrame:
    """按换月日切主力合约 bar（与 tools/build_rollover_map.py 一致）。"""
    out = df.copy()
    if idx > 0 and idx - 1 < len(rollover_events):
        start_date = _rollover_event_date(rollover_events[idx - 1])
        out = out[out["dt"].dt.date >= start_date]
    if idx < len(chain_yymm) - 1 and idx < len(rollover_events):
        end_date = _rollover_event_date(rollover_events[idx])
        out = out[out["dt"].dt.date < end_date]
    return out.sort_values("datetime").reset_index(drop=True)


def load_cbc_dataframe(
    prefix: str,
    *,
    start: datetime | None = None,
    end: datetime | None = None,
) -> pd.DataFrame:
    """CbC：分月 raw + rollover_map 拼接主力 1m 序列（无复权）。"""
    map_path = _rollover_map_path(prefix)
    if not os.path.exists(map_path):
        raise FileNotFoundError(
            f"未找到换月映射表: {map_path}\n"
            f"请先运行: tools/build_rollover_map.py -s {prefix} --map-only"
        )

    rollover_map = pd.read_parquet(map_path)
    chain = build_dominant_chain(rollover_map)
    events = ordered_rollover_events(rollover_map)

    segments: list[pd.DataFrame] = []
    for idx, yymm in enumerate(chain):
        monthly = load_monthly_parquet(_monthly_path(prefix, yymm), yymm=yymm)
        if monthly is None or len(monthly) == 0:
            continue
        sliced = slice_dominant_segment(monthly, idx, chain, events)
        if len(sliced) == 0:
            continue
        segments.append(sliced)

    if not segments:
        raise FileNotFoundError(
            f"CbC 拼接失败: {prefix} 主力链 {chain} 无有效分月数据"
        )

    df = pd.concat(segments, ignore_index=True)
    df = df.drop_duplicates(subset=["datetime"]).sort_values("datetime").reset_index(drop=True)
    df["dt"] = pd.to_datetime(df["datetime"], unit="ns", utc=True).dt.tz_convert(
        "Asia/Shanghai",
    )

    if start is not None:
        df = df[df["dt"] >= pd.Timestamp(start, tz="Asia/Shanghai")]
    if end is not None:
        df = df[df["dt"] <= pd.Timestamp(end, tz="Asia/Shanghai")]

    return df.reset_index(drop=True)


def load_monthly_dataframe(
    prefix: str,
    yymm: str,
    *,
    start: datetime | None = None,
    end: datetime | None = None,
) -> pd.DataFrame:
    """加载单个分月合约原始无复权序列。"""
    path = _monthly_path(prefix, yymm)
    if not os.path.exists(path):
        raise FileNotFoundError(f"未找到分月文件: {path}")

    df = load_monthly_parquet(path, yymm=yymm)
    if df is None or len(df) == 0:
        raise FileNotFoundError(f"分月文件为空: {path}")

    cols = [c for c in RAW_OHLCV_COLUMNS if c in df.columns]
    if "yymm" in df.columns:
        cols.append("yymm")
    df = df[cols].copy()
    df["dt"] = pd.to_datetime(df["datetime"], unit="ns", utc=True).dt.tz_convert(
        "Asia/Shanghai",
    )

    if start is not None:
        df = df[df["dt"] >= pd.Timestamp(start, tz="Asia/Shanghai")]
    if end is not None:
        df = df[df["dt"] <= pd.Timestamp(end, tz="Asia/Shanghai")]

    return df.reset_index(drop=True)


def load_raw_dataframe(
    prefix: str,
    *,
    yymm: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
) -> pd.DataFrame:
    """加载 OHLCV DataFrame（CST）。yymm=None 时走 CbC 主力拼接。"""
    if yymm:
        return load_monthly_dataframe(prefix, yymm, start=start, end=end)
    return load_cbc_dataframe(prefix, start=start, end=end)


def dataframe_to_bars(
    df: pd.DataFrame,
    exchange: Exchange,
    *,
    symbol: str,
    interval: Interval = Interval.MINUTE,
    gateway_name: str = "TQ",
) -> list[BarData]:
    bars: list[BarData] = []
    for row in df.itertuples(index=False):
        bars.append(
            BarData(
                gateway_name=gateway_name,
                symbol=symbol,
                exchange=exchange,
                datetime=row.dt.to_pydatetime(),
                interval=interval,
                volume=float(row.volume),
                open_interest=float(
                    getattr(row, "close_oi", None)
                    if getattr(row, "close_oi", None) is not None
                    else (getattr(row, "open_oi", 0) or 0)
                ),
                open_price=float(row.open),
                high_price=float(row.high),
                low_price=float(row.low),
                close_price=float(row.close),
            )
        )
    return bars


def load_bars_from_tq(
    prefix: str,
    exchange: Exchange,
    *,
    symbol: str | None = None,
    yymm: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    interval: Interval = Interval.MINUTE,
    gateway_name: str = "TQ",
) -> list[BarData]:
    """加载 K 线并转换为 vnpy BarData（默认 CbC 主力 raw，无复权）。"""
    df = load_raw_dataframe(prefix, yymm=yymm, start=start, end=end)
    return dataframe_to_bars(
        df, exchange, symbol=symbol or prefix, interval=interval, gateway_name=gateway_name,
    )


if __name__ == "__main__":
    import sys

    prefix_arg = sys.argv[1] if len(sys.argv) > 1 else "rb"
    sample = load_bars_from_tq(prefix_arg, Exchange.SHFE)
    print(f"[{prefix_arg}] CbC 加载 {len(sample)} 根原始无复权 1m K 线")
    if sample:
        print(f"  起: {sample[0].datetime}  {sample[0].close_price}")
        print(f"  止: {sample[-1].datetime}  {sample[-1].close_price}")
