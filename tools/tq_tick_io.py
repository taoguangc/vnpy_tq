"""天勤(TQSDK) tick parquet 读写规范。"""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from tools.tq_paths import symbol_dir, tick_dir

SESSION_NOTE = "TQ tick datetime stored as UTC ns; filter/display in Asia/Shanghai"

TICK_CORE_COLUMNS = (
    "datetime",
    "last_price",
    "average",
    "highest",
    "lowest",
    "volume",
    "amount",
    "open_interest",
    "bid_price1",
    "bid_volume1",
    "ask_price1",
    "ask_volume1",
)

PARQUET_WRITE_KWARGS = {"index": False, "engine": "pyarrow", "compression": "zstd"}
MANIFEST_FILE = "manifest.json"
LOCK_FILE = ".download_tick.lock"


def monthly_data_dir(prefix: str) -> Path:
    """1m / rollover_map 所在目录（data/tq/{prefix}）。"""
    return symbol_dir(prefix)


def tick_output_dir_for_prefix(prefix: str) -> Path:
    """品种 tick 落盘目录 data/tq/{prefix}/tick/。"""
    return tick_dir(prefix)


def contract_tag(symbol: str) -> str:
    return symbol.split(".")[-1].lower()


def resolve_prefix(symbol: str) -> str:
    """SHFE.rb2301 -> rb; CZCE.MA501 -> MA。"""
    parts = symbol.split(".", 1)
    if len(parts) != 2:
        tag = contract_tag(symbol)
        return "".join(c for c in tag if not c.isdigit()).lower() or tag
    exchange, code = parts[0], parts[1]
    if exchange == "CZCE":
        letters = "".join(c for c in code if c.isalpha())
        return letters.upper() if letters else code
    return "".join(c for c in code if not c.isdigit()).lower() or code.lower()


def canonical_tick_name(symbol: str) -> str:
    return f"{contract_tag(symbol)}_tick.parquet"


def part_tick_name(symbol: str, part_no: int) -> str:
    return f"{contract_tag(symbol)}_tick_part_{part_no:03d}.parquet"


def normalize_ticks(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or len(df) == 0:
        return pd.DataFrame(columns=list(TICK_CORE_COLUMNS))

    out = df.copy()
    if "datetime" not in out.columns:
        raise ValueError("missing datetime column")

    out["datetime"] = pd.to_numeric(out["datetime"], errors="coerce")
    out = out.dropna(subset=["datetime"])
    out["datetime"] = out["datetime"].astype("int64")
    out = out[out["datetime"] > 0]

    for col in TICK_CORE_COLUMNS:
        if col not in out.columns:
            out[col] = 0.0

    extra = [c for c in out.columns if c not in TICK_CORE_COLUMNS]
    cols = list(TICK_CORE_COLUMNS) + sorted(extra)
    out = out[cols]
    for col in cols:
        if col == "datetime":
            continue
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0.0)

    return out.drop_duplicates(subset=["datetime"]).sort_values("datetime").reset_index(drop=True)


def cst_bounds_ns(start_dt, end_dt) -> tuple[int, int]:
    start_ns = int(pd.Timestamp(start_dt).tz_localize("Asia/Shanghai").value)
    end_ns = int(pd.Timestamp(end_dt).tz_localize("Asia/Shanghai").value)
    return start_ns, end_ns


def max_datetime_ns(parquet_path: os.PathLike | str) -> int:
    df = pd.read_parquet(parquet_path, columns=["datetime"])
    if len(df) == 0:
        return 0
    return int(pd.to_numeric(df["datetime"], errors="coerce").max())


def list_part_files(output_dir: os.PathLike | str, symbol: str) -> list[str]:
    prefix = f"{contract_tag(symbol)}_tick_part_"
    odir = Path(output_dir)
    if not odir.is_dir():
        return []
    return sorted(
        f.name for f in odir.iterdir()
        if f.name.startswith(prefix) and f.name.endswith(".parquet")
    )


def atomic_write_parquet(df: pd.DataFrame, path: os.PathLike | str) -> None:
    p = Path(path)
    tmp = p.with_suffix(p.suffix + ".tmp")
    df.to_parquet(tmp, **PARQUET_WRITE_KWARGS)
    os.replace(tmp, p)
