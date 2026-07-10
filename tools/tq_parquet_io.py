"""TQSDK 离线分月 parquet 读写规范（共享 schema）。"""
from __future__ import annotations

import os
import re
from typing import Iterable

import pandas as pd

# TQSDK K 线 datetime 为 UTC 纳秒；日盘最后一根对应北京 14:59（无 15:00 bar）
SESSION_NOTE = "TQSDK 1m K-line day session ends 14:59 CST (UTC 06:59 bar start); no 15:00 bar"

MONTHLY_OHLCV_COLUMNS = (
    "datetime",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "open_oi",
    "close_oi",
)

VERIFY_OHLCV_COLUMNS = (
    "open",
    "high",
    "low",
    "close",
    "volume",
    "open_oi",
    "close_oi",
)


def normalize_monthly_klines(df: pd.DataFrame) -> pd.DataFrame:
    """将 TQSDK klines / 历史 parquet 规范为分月 canonical schema。"""
    if df is None or len(df) == 0:
        return pd.DataFrame(columns=list(MONTHLY_OHLCV_COLUMNS))

    out = df.copy()
    if "datetime" not in out.columns:
        raise ValueError("missing datetime column")

    out["datetime"] = pd.to_numeric(out["datetime"], errors="coerce")
    out = out.dropna(subset=["datetime"])
    out["datetime"] = out["datetime"].astype("int64")
    out = out[out["datetime"] > 0]

    for col in MONTHLY_OHLCV_COLUMNS[1:]:
        if col not in out.columns:
            out[col] = 0.0
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0.0)

    out = out[list(MONTHLY_OHLCV_COLUMNS)]
    out = out.drop_duplicates(subset=["datetime"]).sort_values("datetime").reset_index(drop=True)
    return out


def load_monthly_parquet(filepath: str, yymm: str | None = None) -> pd.DataFrame | None:
    """加载分月 parquet 并规范化；文件不存在或为空时返回 None。"""
    if not os.path.exists(filepath):
        return None
    df = pd.read_parquet(filepath)
    if len(df) == 0:
        return None
    df = normalize_monthly_klines(df)
    if len(df) == 0:
        return None
    df["dt"] = pd.to_datetime(df["datetime"], unit="ns", utc=True)
    if yymm is not None:
        df["yymm"] = yymm
    return df


def is_monthly_contract_file(filename: str, prefix: str, yymm_len: int = 4) -> bool:
    """rb_2405.parquet -> True; rb_2405_part_001.parquet / rb_continuous.parquet -> False。"""
    if not filename.startswith(f"{prefix}_") or not filename.endswith(".parquet"):
        return False
    if "_part_" in filename or filename.endswith("_continuous.parquet"):
        return False
    yymm = filename[len(prefix) + 1 : -8]
    if not yymm.isdigit():
        return False
    if yymm_len == 3:
        # CZCE 落盘文件名实际为 4 位 yyMM（如 MA_2101）
        return len(yymm) in (3, 4)
    return len(yymm) == yymm_len


def list_orphan_part_files(output_dir: str, prefix: str, yymm: str) -> list[str]:
    part_prefix = f"{prefix}_{yymm}_part_"
    if not os.path.isdir(output_dir):
        return []
    return sorted(
        f for f in os.listdir(output_dir)
        if f.startswith(part_prefix) and f.endswith(".parquet")
    )


def compare_ohlcv(
    left: pd.DataFrame,
    right: pd.DataFrame,
    on: str = "datetime",
    cols: Iterable[str] = VERIFY_OHLCV_COLUMNS,
    rtol: float = 1e-9,
    atol: float = 1e-6,
) -> tuple[int, int, pd.DataFrame]:
    """返回 (重叠行数, 不一致行数, 不一致样本)。"""
    l = left[[on, *cols]].copy()
    r = right[[on, *cols]].copy()
    merged = l.merge(r, on=on, how="inner", suffixes=("_l", "_r"))
    if len(merged) == 0:
        return 0, 0, pd.DataFrame()

    mismatch_mask = pd.Series(False, index=merged.index)
    for col in cols:
        a = merged[f"{col}_l"].astype(float)
        b = merged[f"{col}_r"].astype(float)
        mismatch_mask |= ~((a - b).abs() <= (atol + rtol * b.abs()))

    mismatches = merged[mismatch_mask]
    return len(merged), len(mismatches), mismatches.head(20)
