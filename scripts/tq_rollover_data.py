"""TQ 分月 raw 拼接 + 换月切点元数据（CbC 无复权，切点 21:00 CST）。"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from tools.dominant_windows import build_segments_from_map, switch_cst
from tools.tq_parquet_io import load_monthly_parquet
from tools.tq_paths import symbol_dir
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData

CST = ZoneInfo("Asia/Shanghai")


def _as_cst(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=CST)
    return dt.astimezone(CST)


@dataclass(frozen=True)
class RolloverEvent:
    """换月切点：21:00 CST 平旧开新。"""

    switch_time: datetime
    from_yymm: str
    to_yymm: str
    old_close: float
    new_open: float
    price_diff: float
    slippage_cost: float
    commission_cost: float
    total_adjustment: float

    @property
    def price_shift(self) -> float:
        """new_open - old_close（多头换月价差）。"""
        return self.new_open - self.old_close


def _monthly_path(data_dir: Path, prefix: str, yymm: str) -> Path:
    return data_dir / f"{prefix}_{yymm}.parquet"


def _load_monthly_cache(data_dir: Path, prefix: str) -> dict[str, pd.DataFrame]:
    cache: dict[str, pd.DataFrame] = {}
    for path in sorted(data_dir.glob(f"{prefix}_*.parquet")):
        name = path.name
        if name.startswith("rollover") or "_continuous" in name or "_part_" in name:
            continue
        yymm = name.replace(f"{prefix}_", "").replace(".parquet", "")
        if not yymm.isdigit():
            continue
        df = load_monthly_parquet(str(path), yymm=yymm)
        if df is None or df.empty:
            continue
        df = df.copy()
        df["dt_cst"] = df["dt"].dt.tz_convert("Asia/Shanghai")
        cache[yymm] = df
    if not cache:
        raise FileNotFoundError(f"no monthly parquet under {data_dir}/{prefix}_*.parquet")
    return cache


def _slice_segment(df: pd.DataFrame, seg: dict) -> pd.DataFrame:
    out = df
    start = seg.get("start")
    end = seg.get("end")
    if start is not None:
        start_ts = pd.Timestamp(start)
        if start_ts.tzinfo is None:
            start_ts = start_ts.tz_localize("Asia/Shanghai")
        out = out[out["dt_cst"] >= start_ts]
    if end is not None:
        end_ts = pd.Timestamp(end)
        if end_ts.tzinfo is None:
            end_ts = end_ts.tz_localize("Asia/Shanghai")
        out = out[out["dt_cst"] < end_ts]
    return out.sort_values("dt_cst")


def build_rollover_events(
    prefix: str,
    *,
    start: datetime | None = None,
    end: datetime | None = None,
) -> list[RolloverEvent]:
    data_dir = symbol_dir(prefix)
    rollover_map = pd.read_parquet(data_dir / "rollover_map.parquet")
    monthly_cache = _load_monthly_cache(data_dir, prefix)
    cost_path = data_dir / "rollover_cost_detail.parquet"
    cost_by_id = None
    if cost_path.exists():
        cost_by_id = pd.read_parquet(cost_path).set_index("rollover_id")

    events: list[RolloverEvent] = []
    start_cst = _as_cst(start) if start else None
    end_cst = _as_cst(end) if end else None
    sort_col = "rollover_id" if "rollover_id" in rollover_map.columns else "rollover_date"
    for _, row in rollover_map.sort_values(sort_col).iterrows():
        rid = int(row["rollover_id"]) if "rollover_id" in row else 0
        switch = switch_cst(row["rollover_date"])
        if switch.tzinfo is None:
            switch = switch.tz_localize("Asia/Shanghai")
        switch_dt = switch.to_pydatetime()

        if start_cst and switch_dt < start_cst:
            continue
        if end_cst and switch_dt > end_cst:
            continue

        from_yymm = str(row["from_yymm"])
        to_yymm = str(row["to_yymm"])
        old_df = monthly_cache.get(from_yymm)
        new_df = monthly_cache.get(to_yymm)
        if old_df is None or new_df is None:
            continue

        old_tail = old_df[old_df["dt_cst"] < switch]
        new_head = new_df[new_df["dt_cst"] >= switch]
        if old_tail.empty or new_head.empty:
            continue

        old_close = float(old_tail.iloc[-1]["close"])
        new_open = float(new_head.iloc[0]["open"])
        if cost_by_id is not None and rid in cost_by_id.index:
            cost = cost_by_id.loc[rid]
            slippage_cost = float(cost.get("slippage_cost", 0.0))
            commission_cost = float(cost.get("commission_cost", 0.0))
            total_adjustment = float(cost.get("total_adjustment", 0.0))
            price_diff = float(cost.get("price_diff_only", new_open - old_close))
        else:
            slippage_cost = 0.0
            commission_cost = 0.0
            total_adjustment = 0.0
            price_diff = new_open - old_close

        events.append(
            RolloverEvent(
                switch_time=switch_dt,
                from_yymm=from_yymm,
                to_yymm=to_yymm,
                old_close=old_close,
                new_open=new_open,
                price_diff=price_diff,
                slippage_cost=slippage_cost,
                commission_cost=commission_cost,
                total_adjustment=total_adjustment,
            )
        )
    return events


def build_stitched_raw_frame(prefix: str) -> pd.DataFrame:
    """拼接分月原始 OHLC（无复权），每行带 yymm。"""
    data_dir = symbol_dir(prefix)
    monthly_cache = _load_monthly_cache(data_dir, prefix)
    rollover_map = pd.read_parquet(data_dir / "rollover_map.parquet")
    segments = build_segments_from_map(rollover_map)

    missing = {seg["yymm"] for seg in segments} - set(monthly_cache)
    if missing:
        raise FileNotFoundError(f"missing monthly files for yymm: {sorted(missing)}")

    chunks: list[pd.DataFrame] = []
    for seg in segments:
        part = _slice_segment(monthly_cache[seg["yymm"]], seg)
        if part.empty:
            continue
        chunks.append(part.assign(yymm=seg["yymm"]))

    if not chunks:
        raise RuntimeError(f"stitched raw series is empty for {prefix}")

    return pd.concat(chunks, ignore_index=True).sort_values("dt_cst")


def load_stitched_raw_bars(
    prefix: str,
    exchange: Exchange,
    *,
    symbol: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
) -> list[BarData]:
    """分月 raw 拼接 → BarData；每根 bar 附加 ``yymm`` 属性。"""
    df = build_stitched_raw_frame(prefix)
    sym = symbol or prefix

    if start is not None:
        start_ts = pd.Timestamp(_as_cst(start))
        df = df[df["dt_cst"] >= start_ts]
    if end is not None:
        end_ts = pd.Timestamp(_as_cst(end))
        df = df[df["dt_cst"] <= end_ts]

    bars: list[BarData] = []
    for row in df.itertuples(index=False):
        bar = BarData(
            gateway_name="TQ_STITCHED",
            symbol=sym,
            exchange=exchange,
            datetime=row.dt_cst.to_pydatetime(),
            interval=Interval.MINUTE,
            volume=float(row.volume),
            turnover=0.0,
            open_interest=float(getattr(row, "open_oi", 0) or 0),
            open_price=float(row.open),
            high_price=float(row.high),
            low_price=float(row.low),
            close_price=float(row.close),
        )
        bar.yymm = str(row.yymm)  # type: ignore[attr-defined]
        bars.append(bar)
    return bars
