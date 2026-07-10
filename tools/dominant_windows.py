"""主力合约 1m 下载窗口（由 rollover_map + OI 边界推导）。"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import date, datetime, timedelta

import pandas as pd

from tools.rollover_rules import SLICE_BUFFER_DAYS

DOMINANT_WINDOWS_FILE = "dominant_windows.json"


def _rollover_event_date(record: dict | pd.Series) -> date:
    rd = record["rollover_date"]
    if isinstance(rd, pd.Timestamp):
        return rd.date()
    if isinstance(rd, datetime):
        return rd.date()
    return rd


def build_dominant_chain(rollover_map: pd.DataFrame) -> list[str]:
    if rollover_map.empty:
        return []
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


def slice_window_dates(
    idx: int,
    yymm: str,
    chain: list[str],
    events: list[dict],
    bounds: dict[str, tuple[date, date]],
    *,
    slice_buffer_days: int = SLICE_BUFFER_DAYS,
) -> tuple[date, date, date | None, date | None]:
    """返回 (start, end, rollover_in, rollover_out)，与 slice_dominant_segment 对齐。"""
    bmin, bmax = bounds.get(yymm, (None, None))
    if bmin is None or bmax is None:
        raise ValueError(f"缺少 {yymm} 的 OI 日期边界")

    rollover_in: date | None = None
    rollover_out: date | None = None

    if idx > 0 and idx - 1 < len(events):
        rollover_in = _rollover_event_date(events[idx - 1])
        start = rollover_in
    else:
        start = bmin if isinstance(bmin, date) else bmin.date()

    if idx < len(chain) - 1 and idx < len(events):
        rollover_out = _rollover_event_date(events[idx])
        end = rollover_out
    else:
        end = bmax if isinstance(bmax, date) else bmax.date()

    if slice_buffer_days > 0:
        start = start - timedelta(days=slice_buffer_days)
        if idx < len(chain) - 1:
            end = end + timedelta(days=slice_buffer_days)

    return start, end, rollover_in, rollover_out


def build_dominant_windows(
    rollover_map: pd.DataFrame,
    dominant_chain: list[str],
    bounds: dict[str, tuple[date, date]],
    *,
    slice_buffer_days: int = SLICE_BUFFER_DAYS,
    source: str = "oi_daily",
) -> dict:
    events = ordered_rollover_events(rollover_map)
    windows: dict[str, dict] = {}

    for idx, yymm in enumerate(dominant_chain):
        start, end, rin, rout = slice_window_dates(
            idx, yymm, dominant_chain, events, bounds,
            slice_buffer_days=slice_buffer_days,
        )
        windows[yymm] = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "chain_idx": idx,
            "rollover_in": rin.isoformat() if rin else None,
            "rollover_out": rout.isoformat() if rout else None,
        }

    meta = {
        "built_at": datetime.now().isoformat(),
        "source": source,
        "slice_buffer_days": slice_buffer_days,
        "chain_len": len(dominant_chain),
        "rollover_events": len(events),
    }
    return {"_meta": meta, "windows": windows}


def dominant_windows_path(data_dir: str) -> str:
    return os.path.join(data_dir, DOMINANT_WINDOWS_FILE)


def save_dominant_windows(data_dir: str, payload: dict, rollover_map_path: str | None = None) -> str:
    path = dominant_windows_path(data_dir)
    if rollover_map_path and os.path.exists(rollover_map_path):
        with open(rollover_map_path, "rb") as f:
            payload["_meta"]["rollover_map_sha256"] = hashlib.sha256(f.read()).hexdigest()[:16]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


def load_dominant_windows(data_dir: str) -> dict | None:
    path = dominant_windows_path(data_dir)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def apply_windows_to_meta(
    meta_info: dict,
    windows: dict,
    yymm: str,
) -> dict:
    """复制 meta 并按 dominant_windows 覆盖 start/end（Phase-2 1m）。"""
    w = windows.get("windows", {}).get(yymm)
    if not w:
        return meta_info
    out = dict(meta_info)
    out["start_date"] = w["start"]
    out["end_date"] = w["end"]
    out["download_mode"] = "dominant_1m"
    return out


def switch_cst(rollover_date) -> pd.Timestamp:
    """换月切点 21:00 CST（与 CbC / build_rollover_map 一致）。"""
    ts = pd.Timestamp(rollover_date)
    return ts.replace(hour=21, minute=0, second=0, microsecond=0)


def build_segments_from_map(rollover_map: pd.DataFrame) -> list[dict]:
    """按 rollover_map 切主力时段（tick 下载 rollover 模式用）。"""
    rolls = rollover_map.sort_values("rollover_id").reset_index(drop=True)
    if rolls.empty:
        raise ValueError("rollover_map is empty")

    segments: list[dict] = []
    first = rolls.iloc[0]
    segments.append({
        "yymm": str(first["from_yymm"]),
        "start": None,
        "end": switch_cst(first["rollover_date"]),
    })
    for _, roll in rolls.iterrows():
        segments.append({
            "yymm": str(roll["to_yymm"]),
            "start": switch_cst(roll["rollover_date"]),
            "end": None,
        })
    for i in range(len(segments) - 1):
        segments[i]["end"] = segments[i + 1]["start"]
    return segments


def load_segments_by_yymm(monthly_data_dir: str) -> dict[str, dict]:
    """加载 tick 主力段：优先 dominant_windows.json，否则 rollover_map。"""
    dw = load_dominant_windows(monthly_data_dir)
    if dw and dw.get("windows"):
        out: dict[str, dict] = {}
        for yymm, w in dw["windows"].items():
            out[str(yymm)] = {
                "yymm": str(yymm),
                "start": pd.Timestamp(w["start"]),
                "end": pd.Timestamp(w["end"]) + pd.Timedelta(hours=23, minutes=59, seconds=59),
            }
        return out

    map_path = os.path.join(monthly_data_dir, "rollover_map.parquet")
    if not os.path.exists(map_path):
        return {}
    rollover_map = pd.read_parquet(map_path)
    segments = build_segments_from_map(rollover_map)
    return {str(seg["yymm"]): seg for seg in segments}
