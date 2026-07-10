# -*- coding: utf-8 -*-
"""OPP 多周期标签解析、优先级与跨周期 arm 冲突规则（pa_cta lean 用）。"""
from __future__ import annotations

import re

# 周期优先级：数值越大越优先（D > 1H > 15M > 5M）
TF_5M = "5M"
TF_15M = "15M"
TF_1H = "1H"
TF_D = "D"

TF_PRIORITY: dict[str, int] = {
    TF_5M: 1,
    TF_15M: 2,
    TF_1H: 3,
    TF_D: 4,
}

_KNOWN_TFS = frozenset(TF_PRIORITY)

_OPP_TAG_RE = re.compile(
    r"^(OPP\d+)_(" + "|".join(_KNOWN_TFS) + r")_(.+)$"
)


def build_opp_tag(opp_id: str, tf: str, suffix: str) -> str:
    """构造标准标签，如 build_opp_tag('OPP16', '5M', 'TWO_BAR_REV_LONG')."""
    opp = opp_id.upper()
    if not opp.startswith("OPP"):
        opp = f"OPP{opp}"
    tf_u = tf.upper()
    if tf_u not in _KNOWN_TFS:
        raise ValueError(f"未知周期 {tf}")
    return f"{opp}_{tf_u}_{suffix}"


def parse_opp_tf(setup: str) -> str:
    """从标签解析周期；无周期后缀时返回空串。"""
    if not setup:
        return ""
    m = _OPP_TAG_RE.match(setup)
    if m:
        return m.group(2)
    return ""


def tf_priority(tf: str) -> int:
    return TF_PRIORITY.get((tf or "").upper(), 0)


def setup_priority(setup: str) -> int:
    return tf_priority(parse_opp_tf(setup))


def should_upgrade_arm(current_setup: str, new_setup: str) -> bool:
    """新信号是否应覆盖当前 pending arm（仅当新周期更高或相等且同族）。"""
    cur_pri = setup_priority(current_setup)
    new_pri = setup_priority(new_setup)
    if new_pri > cur_pri:
        return True
    if new_pri < cur_pri:
        return False
    return current_setup != new_setup


def is_opposite_direction(pos: int, signal_dir: int) -> bool:
    return (pos > 0 and signal_dir < 0) or (pos < 0 and signal_dir > 0)
