# -*- coding: utf-8
"""统一 Event Research 记录 schema。"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

FWD_HORIZONS = (5, 10, 20, 40, 80)
MFE_WINDOW = 20
DEFAULT_COST_TICKS = 3.0
DEFAULT_COST_TICKS_ALT = 2.0
GATE_MIN_N = 30


@dataclass
class EventRecord:
    """单条事件（研究层，非下单）。"""

    symbol: str
    datetime: Any
    setup: str
    direction: int
    entry_price: float
    bar_interval: str = "1m"
    features: dict[str, float] = field(default_factory=dict)
    f5: float = 0.0
    f10: float = 0.0
    f20: float = 0.0
    f40: float = 0.0
    f80: float = 0.0
    mfe: float = 0.0
    mae: float = 0.0
    extra: dict[str, Any] = field(default_factory=dict)

    def set_forward(self, horizon: int, value: float) -> None:
        if horizon == 5:
            self.f5 = value
        elif horizon == 10:
            self.f10 = value
        elif horizon == 20:
            self.f20 = value
        elif horizon == 40:
            self.f40 = value
        elif horizon == 80:
            self.f80 = value
        else:
            raise ValueError(f"unsupported horizon: {horizon}")

    def forward_ticks(self, horizon: int, *, tick: float) -> float:
        raw = getattr(self, f"f{horizon}")
        return float(raw) / tick

    def to_row(self) -> dict[str, Any]:
        row = {
            "symbol": self.symbol,
            "datetime": self.datetime,
            "setup": self.setup,
            "direction": self.direction,
            "entry_price": self.entry_price,
            "bar_interval": self.bar_interval,
            "future_5": self.f5,
            "future_10": self.f10,
            "future_20": self.f20,
            "future_40": self.f40,
            "future_80": self.f80,
            "mfe": self.mfe,
            "mae": self.mae,
        }
        for key, val in self.features.items():
            row[f"feat_{key}"] = val
        row.update(self.extra)
        return row

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> EventRecord:
        features = {
            k.replace("feat_", ""): float(v)
            for k, v in row.items()
            if k.startswith("feat_") and v == v
        }
        known = {
            "symbol", "datetime", "setup", "direction", "entry_price", "bar_interval",
            "future_5", "future_10", "future_20", "future_40", "future_80", "mfe", "mae",
        }
        known |= {f"feat_{k}" for k in features}
        extra = {k: v for k, v in row.items() if k not in known}
        return cls(
            symbol=str(row["symbol"]),
            datetime=row["datetime"],
            setup=str(row["setup"]),
            direction=int(row["direction"]),
            entry_price=float(row["entry_price"]),
            bar_interval=str(row.get("bar_interval", "1m")),
            features=features,
            f5=float(row.get("future_5", 0.0)),
            f10=float(row.get("future_10", 0.0)),
            f20=float(row.get("future_20", 0.0)),
            f40=float(row.get("future_40", 0.0)),
            f80=float(row.get("future_80", 0.0)),
            mfe=float(row.get("mfe", 0.0)),
            mae=float(row.get("mae", 0.0)),
            extra=extra,
        )


def records_to_dataframe(records: list[EventRecord]):
    import pandas as pd

    if not records:
        return pd.DataFrame()
    return pd.DataFrame([r.to_row() for r in records])


def dataframe_to_records(df) -> list[EventRecord]:
    if df.empty:
        return []
    return [EventRecord.from_row(row.to_dict()) for _, row in df.iterrows()]
