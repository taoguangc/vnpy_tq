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
    return resolve_symbol(prefix)[0]


def resolve_symbol(prefix: str) -> tuple[Path, str]:
    """解析品种目录（大小写不敏感），返回 (data_dir, 文件前缀名)。"""
    root = tq_data_root()
    direct = root / prefix
    if direct.is_dir():
        return direct, direct.name
    key = prefix.lower()
    for child in sorted(root.iterdir()):
        if child.is_dir() and child.name.lower() == key:
            return child, child.name
    return direct, prefix


def tick_dir(prefix: str) -> Path:
    """品种 tick：data/tq/{prefix}/tick/。"""
    out = symbol_dir(prefix) / "tick"
    out.mkdir(parents=True, exist_ok=True)
    return out
