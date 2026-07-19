"""CSV Logger：研究审计输出。"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, Optional

from strategies.paaf.domain import Opportunity, TRADE_RECORD_FIELDS, TradeRecord


class TradeLogger:
    """禁止用 print 替代研究日志。"""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialized = self.path.exists() and self.path.stat().st_size > 0

    def write(self, record: TradeRecord) -> None:
        write_header = not self._initialized
        with self.path.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(TRADE_RECORD_FIELDS))
            if write_header:
                writer.writeheader()
                self._initialized = True
            writer.writerow(record.to_dict())

    def write_many(self, records: Iterable[TradeRecord]) -> None:
        for record in records:
            self.write(record)

    def clear(self) -> None:
        if self.path.exists():
            self.path.unlink()
        self._initialized = False


class OpportunityLogger:
    """最小 JSONL Opportunity 审计输出；不改变 Pipeline 结果。"""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, opportunity: Opportunity) -> None:
        with self.path.open("a", encoding="utf-8", newline="") as handle:
            handle.write(
                json.dumps(
                    opportunity.to_dict(),
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
            handle.write("\n")

    def write_many(self, opportunities: Iterable[Opportunity]) -> None:
        for opportunity in opportunities:
            self.write(opportunity)

    def clear(self) -> None:
        if self.path.exists():
            self.path.unlink()


# 兼容旧骨架名
Logger = TradeLogger
