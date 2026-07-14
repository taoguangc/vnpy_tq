"""Phase-1 日频 OI scout 数据读写（两阶段 OI→1m 管线）。"""
from __future__ import annotations

import os

import pandas as pd

from tools.tq_parquet_io import trim_czce_decade_collision

OI_DAILY_DIR = "oi_daily"
OI_DAILY_COLUMNS = ("datetime", "close", "close_oi")

# 与 download_rb_monthly.CZCE_YYMM_LEN3 对齐：仅郑商所合约会十年撞键
CZCE_OI_TRIM_PREFIXES = {
    "MA", "TA", "SA", "FG", "SR", "RM", "PF", "SF", "SM", "ZC",
    "CF", "CJ", "CY", "UR", "OI", "AP",
}

PARQUET_WRITE_KWARGS = {"index": False, "engine": "pyarrow", "compression": "zstd"}


def oi_daily_dir(data_dir: str) -> str:
    return os.path.join(data_dir, OI_DAILY_DIR)


def oi_daily_path(data_dir: str, prefix: str, yymm: str) -> str:
    return os.path.join(oi_daily_dir(data_dir), f"{prefix}_{yymm}.parquet")


def normalize_oi_daily(df: pd.DataFrame) -> pd.DataFrame:
    """将 TQSDK 日 K 规范为 oi_daily canonical schema。"""
    if df is None or len(df) == 0:
        return pd.DataFrame(columns=list(OI_DAILY_COLUMNS))

    out = df.copy()
    if "datetime" not in out.columns:
        raise ValueError("missing datetime column")

    out["datetime"] = pd.to_numeric(out["datetime"], errors="coerce")
    out = out.dropna(subset=["datetime"])
    out["datetime"] = out["datetime"].astype("int64")
    out = out[out["datetime"] > 0]

    for col in OI_DAILY_COLUMNS[1:]:
        if col not in out.columns:
            out[col] = 0.0
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0.0)

    out = out[list(OI_DAILY_COLUMNS)]
    out = out.drop_duplicates(subset=["datetime"]).sort_values("datetime").reset_index(drop=True)
    return out


def load_oi_daily_parquet(
    filepath: str,
    yymm: str | None = None,
    *,
    prefix: str | None = None,
) -> pd.DataFrame | None:
    if not os.path.exists(filepath):
        return None
    df = pd.read_parquet(filepath)
    if len(df) == 0:
        return None
    df = normalize_oi_daily(df)
    if yymm is not None and prefix in CZCE_OI_TRIM_PREFIXES:
        df, _ = trim_czce_decade_collision(df, yymm)
    if len(df) == 0:
        return None
    df["dt"] = pd.to_datetime(df["datetime"], unit="ns", utc=True)
    if yymm is not None:
        df["yymm"] = yymm
    return df


def load_oi_daily_dict(data_dir: str, prefix: str) -> dict[str, pd.DataFrame]:
    """加载 oi_daily/ 下全部分月，供 detect_dominant_chain 使用。"""
    odir = oi_daily_dir(data_dir)
    if not os.path.isdir(odir):
        return {}

    out: dict[str, pd.DataFrame] = {}
    for fname in sorted(os.listdir(odir)):
        if not fname.startswith(f"{prefix}_") or not fname.endswith(".parquet"):
            continue
        yymm = fname[len(prefix) + 1 : -8]
        if not yymm.isdigit():
            continue
        df = load_oi_daily_parquet(
            os.path.join(odir, fname), yymm=yymm, prefix=prefix,
        )
        if df is not None and len(df) > 5:
            out[yymm] = df
    return out


def oi_date_bounds(df_dict: dict[str, pd.DataFrame]) -> dict[str, tuple[pd.Timestamp, pd.Timestamp]]:
    bounds: dict[str, tuple[pd.Timestamp, pd.Timestamp]] = {}
    for yymm, df in df_dict.items():
        bounds[yymm] = (df["dt"].min(), df["dt"].max())
    return bounds
