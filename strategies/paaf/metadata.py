"""Detector 元数据辅助。"""

from __future__ import annotations

from dataclasses import dataclass

from strategies.paaf.domain import DetectorInfo


@dataclass(frozen=True)
class DetectorMetadata:
    """类属性形式的元数据声明，可转换成 DetectorInfo。"""

    name: str
    version: str
    description: str = ""
    author: str = "PAAF"
    status: str = "Candidate"
    category: str = "Other"
    timeframe: str = "5m"
    evidence_level: str = "E0"

    def to_info(self) -> DetectorInfo:
        return DetectorInfo(
            name=self.name,
            version=self.version,
            description=self.description,
            author=self.author,
            status=self.status,
        )
