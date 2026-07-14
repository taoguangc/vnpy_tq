"""TQ 分月 tick parquet → CbC 主力链拼接 → 1 分钟 BarData（供 on_bar 策略回测）。"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from tools.dominant_windows import build_segments_from_map
from tools.tq_paths import symbol_dir, tick_dir
from tools.tq_tick_io import MANIFEST_FILE, normalize_ticks
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData

CST = ZoneInfo("Asia/Shanghai")


def _as_cst(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=CST)
    return dt.astimezone(CST)


def _normalize_filename_yymm(code: str) -> str:
    """CZCE tick 文件名常为 3 位（501），rollover 用 4 位（2501）。"""
    if len(code) == 4 and code.isdigit():
        return code
    if len(code) == 3 and code.isdigit():
        return "2" + code
    raise ValueError(f"unsupported tick yymm code: {code!r}")


def _load_tick_manifest(tick_root: Path) -> dict[str, str]:
    import json

    path = tick_root / MANIFEST_FILE
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for fname, meta in data.items():
        if fname.startswith("_") or not isinstance(meta, dict):
            continue
        yymm = meta.get("yymm")
        if yymm:
            out[fname] = str(yymm)
    return out


def _load_tick_cache(tick_root: Path, prefix: str) -> dict[str, pd.DataFrame]:
    cache: dict[str, pd.DataFrame] = {}
    if not tick_root.is_dir():
        raise FileNotFoundError(f"tick 目录不存在: {tick_root}")

    manifest = _load_tick_manifest(tick_root)
    # tick 落盘名用 contract_tag（小写，如 ma501）；file_stem 可能为 MA
    glob_prefix = prefix.lower()
    for path in sorted(tick_root.glob(f"{glob_prefix}*_tick.parquet")):
        name = path.name
        if "_part_" in name:
            continue
        yymm_raw = name.replace(f"{glob_prefix}", "", 1).replace("_tick.parquet", "")
        if not yymm_raw.isdigit():
            continue
        yymm = manifest.get(name) or _normalize_filename_yymm(yymm_raw)
        raw = pd.read_parquet(path)
        df = normalize_ticks(raw)
        if df.empty:
            continue
        df = df.copy()
        df["dt_cst"] = pd.to_datetime(df["datetime"], unit="ns", utc=True).dt.tz_convert(
            "Asia/Shanghai"
        )
        cache[yymm] = df

    if not cache:
        raise FileNotFoundError(f"未找到 tick parquet: {tick_root}/{prefix}*_tick.parquet")
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
        out = out[out["dt_cst"] <= end_ts]
    return out.sort_values("dt_cst")


def _resample_ticks_to_1m(df: pd.DataFrame) -> pd.DataFrame:
    """last_price → 1m OHLC；volume 按 tick 增量求和。"""
    if df.empty:
        return pd.DataFrame()

    work = df.sort_values("dt_cst").set_index("dt_cst")
    price = work["last_price"]
    ohlc = price.resample("1min").ohlc()
    ohlc = ohlc.dropna(subset=["open"])

    vol = work["volume"].astype("float64").diff().fillna(work["volume"])
    vol = vol.clip(lower=0).resample("1min").sum()

    oi = work["open_interest"].resample("1min").last().fillna(0)

    out = ohlc.join(vol.rename("volume")).join(oi.rename("open_interest"))
    out = out[out["volume"] > 0].reset_index()
    return out


def build_stitched_tick_1m_frame(prefix: str) -> pd.DataFrame:
    """主力链 tick 切片 → 拼接 → 1m DataFrame（含 yymm）。"""
    data_dir = symbol_dir(prefix)
    tick_root = tick_dir(prefix)
    rollover_map = pd.read_parquet(data_dir / "rollover_map.parquet")
    segments = build_segments_from_map(rollover_map)
    tick_cache = _load_tick_cache(tick_root, prefix)

    chunks: list[pd.DataFrame] = []
    skipped: list[str] = []
    for seg in segments:
        yymm = seg["yymm"]
        if yymm not in tick_cache:
            skipped.append(yymm)
            continue
        seg_tick = _slice_segment(tick_cache[yymm], seg)
        if seg_tick.empty:
            continue
        bars_1m = _resample_ticks_to_1m(seg_tick)
        if bars_1m.empty:
            continue
        chunks.append(bars_1m.assign(yymm=yymm))

    if skipped:
        import logging

        logging.getLogger(__name__).info(
            "tick 跳过无文件合约: %s", ",".join(skipped[:20])
            + ("..." if len(skipped) > 20 else "")
        )

    if not chunks:
        raise RuntimeError(f"tick→1m 拼接结果为空: {prefix}（tick 目录 {tick_root}）")

    return pd.concat(chunks, ignore_index=True).sort_values("dt_cst")


def load_stitched_tick_bars(
    prefix: str,
    exchange: Exchange,
    *,
    symbol: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
) -> list[BarData]:
    """CbC tick 重采样 1m → BarData（每根 bar 带 yymm）。"""
    df = build_stitched_tick_1m_frame(prefix)
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
            gateway_name="TQ_TICK_1M",
            symbol=sym,
            exchange=exchange,
            datetime=row.dt_cst.to_pydatetime(),
            interval=Interval.MINUTE,
            volume=float(row.volume),
            turnover=0.0,
            open_interest=float(row.open_interest or 0),
            open_price=float(row.open),
            high_price=float(row.high),
            low_price=float(row.low),
            close_price=float(row.close),
        )
        bar.yymm = str(row.yymm)  # type: ignore[attr-defined]
        bars.append(bar)
    return bars
