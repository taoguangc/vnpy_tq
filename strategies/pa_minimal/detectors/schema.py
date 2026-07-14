# -*- coding: utf-8 -*-
"""极简 Alpha 检测器输出 schema（与 shadow_dry_scan.PatternMatch 对齐）。"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PatternMatch:
    setup: str
    direction: int
    trigger: float
    stop: float
    arm_mode: str
    include_opp13_volume: bool = False
    is_direct: bool = False
