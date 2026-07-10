"""天勤离线数据目录约定（1m 与 tick 路径集中定义）。"""
from __future__ import annotations

from pathlib import Path

TQ_DATA_ROOT_NAME = "tq"


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def tq_data_root() -> Path:
    return project_root() / "data" / TQ_DATA_ROOT_NAME


def symbol_dir(prefix: str) -> Path:
    """品种 1m / rollover_map / oi_daily 等：data/tq/{prefix}/。"""
    return tq_data_root() / prefix


def tick_dir(prefix: str) -> Path:
    """品种 tick：data/tq/{prefix}/tick/。"""
    out = symbol_dir(prefix) / "tick"
    out.mkdir(parents=True, exist_ok=True)
    return out
