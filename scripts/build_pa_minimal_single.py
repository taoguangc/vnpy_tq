# -*- coding: utf-8 -*-
"""生成单文件 strategies/pa_minimal/pa_minimal.py（含 BrooksPaCtaStrategy）。

默认交易：OPP16 仅多 + OPP04/05/13。
仍依赖：vnpy / vnpy_ctastrategy / numpy / talib。
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "strategies" / "pa_minimal" / "pa_minimal.py"

# 拓扑顺序：父类依赖 → 父类 → minimal detectors → strategy body
# 已剔除全文内联（默认关）：volume_bar / exit_families / setup_shrinkage /
# shadow_ledger / shadow_dry_scan —— 改用 DEAD_FEATURE_STUBS。
INLINE_BEFORE_PARENT: list[tuple[str, str]] = [
    ("pa_cta/regime_gate.py", "REGIME_GATE"),
    ("pa_cta/context_layers.py", "CONTEXT_LAYERS"),
    ("pa_cta/aff_gate.py", "AFF_GATE"),
    ("pa_cta/symbol_adaptive.py", "SYMBOL_ADAPTIVE"),
    ("pa_cta/bar_patterns.py", "BAR_PATTERNS"),
    ("pa_cta/wedge.py", "WEDGE"),
    ("pa_cta/opp_tf.py", "OPP_TF"),
    ("pa_cta/vsa.py", "VSA"),
    # 仅保留当前单文件交易集所需 mixin：OPP13（04/05/16 走 detectors）
    ("pa_cta/opp/opp13.py", "MIXIN_OPP13"),
]

INLINE_AFTER_PARENT: list[tuple[str, str]] = [
    ("pa_minimal/detectors/schema.py", "SCHEMA"),
    ("pa_minimal/detectors/patterns_ii.py", "PATTERNS_II"),
    ("pa_minimal/detectors/opp04.py", "OPP04"),
    ("pa_minimal/detectors/opp05.py", "OPP05"),
    ("pa_minimal/detectors/opp13.py", "OPP13"),
    ("pa_minimal/detectors/opp16.py", "OPP16"),
]

DROP_IMPORT_PREFIXES = (
    "from strategies.pa_minimal",
    "from strategies.pa_cta",
    "from .",
)

# Multipart import patterns already covered by DROP; also strip try/except import blocks in strategy.py
TRY_IMPORT_BLOCK = re.compile(
    r"try:\n"
    r"(?:    from \..+\n)+"
    r"except \(ModuleNotFoundError, ImportError\):\n"
    r"(?:    from strategies\.pa_cta[\s\S]*?\n)+",
    re.M,
)


def _strip_module_doc_and_future(src: str) -> str:
    tree = ast.parse(src)
    lines = src.splitlines(keepends=True)
    cut = 0
    body = list(tree.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
        cut = max(cut, body[0].end_lineno or body[0].lineno)
        body = body[1:]
    if body and isinstance(body[0], ast.ImportFrom) and body[0].module == "__future__":
        cut = max(cut, body[0].end_lineno or body[0].lineno)
    return "".join(lines[cut:]).lstrip("\n")


def _drop_project_imports(src: str) -> str:
    lines = src.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.lstrip()
        if any(s.startswith(p) for p in DROP_IMPORT_PREFIXES):
            buf = line
            i += 1
            while i < len(lines) and (
                buf.count("(") > buf.count(")")
                or buf.rstrip().endswith("\\")
                or (buf.rstrip().endswith(",") and "(" in buf)
            ):
                buf += lines[i]
                i += 1
                if buf.count("(") <= buf.count(")") and not buf.rstrip().endswith("\\"):
                    break
            continue
        out.append(line)
        i += 1
    return "".join(out)


def _strip_try_except_imports(src: str) -> str:
    """Remove try/except import fallbacks used by pa_cta.strategy."""
    lines = src.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        is_import_try = (
            lines[i].rstrip() == "try:"
            and i + 1 < len(lines)
            and (
                lines[i + 1].lstrip().startswith("from .")
                or lines[i + 1].lstrip().startswith("from strategies.")
            )
        )
        if is_import_try:
            while i < len(lines) and not lines[i].startswith("except"):
                i += 1
            if i < len(lines) and "ModuleNotFoundError" in lines[i]:
                i += 1
                while i < len(lines):
                    cur = lines[i]
                    if cur.startswith(" ") or cur.startswith("\t"):
                        i += 1
                        continue
                    if cur.strip() == "":
                        k = i + 1
                        while k < len(lines) and lines[k].strip() == "":
                            k += 1
                        if k < len(lines) and (
                            lines[k].startswith(" ") or lines[k].startswith("\t")
                        ):
                            i += 1
                            continue
                        break
                    break
                continue
        out.append(lines[i])
        i += 1
    return "".join(out)


def _rewrite(src: str, *, tag: str = "") -> str:
    src = _strip_try_except_imports(src)
    src = TRY_IMPORT_BLOCK.sub("", src)
    src = _drop_project_imports(src)
    # empty try leftovers
    src = re.sub(
        r"try:\nexcept \(ModuleNotFoundError, ImportError\):\n+",
        "",
        src,
    )
    # drop package path bootstrap in strategy.py
    src = re.sub(
        r"if __package__ in \(None, \"\"\):\n"
        r"    _repo = Path\(__file__\)\.resolve\(\)\.parents\[2\]\n"
        r"    if str\(_repo\) not in sys\.path:\n"
        r"        sys\.path\.insert\(0, str\(_repo\)\)\n\n?",
        "",
        src,
    )
    # name collision: aff_gate vs context_layers
    if tag == "AFF_GATE":
        src = src.replace("def _efficiency_ratio(", "def _aff_efficiency_ratio(")
        src = src.replace("_efficiency_ratio(", "_aff_efficiency_ratio(")
        # undo if we double-replaced the def
        src = src.replace("def _aff_aff_efficiency_ratio(", "def _aff_efficiency_ratio(")
    if tag == "CONTEXT_LAYERS":
        src = src.replace("def _efficiency_ratio(", "def _context_efficiency_ratio(")
        src = src.replace("_efficiency_ratio(", "_context_efficiency_ratio(")
        src = src.replace("def _context_context_efficiency_ratio(", "def _context_efficiency_ratio(")
    # shadow_dry_scan PatternMatch → reuse detector PatternMatch later; rename dry one to avoid clash if schema comes after
    if tag == "SHADOW_DRY_SCAN":
        # Keep as PatternMatch for now; schema later will redefine — move dry scan AFTER schema instead?
        # We put dry_scan before schema; schema PatternMatch will overwrite. dry_scan functions close over name at call time → OK in Python (lookup at runtime).
        pass
    return src


DEAD_FEATURE_STUBS = '''
# ===== 已删研究模块桩（flags 默认关；保持父类符号可解析）=====

class VolumeBarGenerator:
    def __init__(self, on_bar=None, volume_threshold: float = 1.0) -> None:
        self.on_bar = on_bar
        self.volume_threshold = float(volume_threshold)

    def set_threshold(self, th: float) -> None:
        self.volume_threshold = float(th)

    def update_bar(self, bar) -> None:
        del bar


def resolve_volume_bar_threshold(symbol: str, override: float = 0.0) -> float:
    del symbol
    if override and float(override) > 0:
        return float(override)
    return 0.0


class ShadowLedger:
    def __init__(self, *_a, **_k) -> None:
        return None

    def mark_traded(self, *_a, **_k) -> None:
        return None

    def set_bar_winner(self, *_a, **_k) -> None:
        return None

    def bar_winner(self, *_a, **_k):
        return None

    def has_setup_at(self, *_a, **_k) -> bool:
        return False


def collect_production_matches(*_a, **_k) -> list:
    return []


def evaluate_production_gates(*_a, **_k) -> tuple[dict, str]:
    return {}, ""


def evaluate_opp15_direct_gates(*_a, **_k) -> tuple[dict, str]:
    return {}, ""


def build_candidate_from_strategy(*_a, **_k):
    return None


class ExitFamily(str, Enum):
    CONTINUATION = "CONTINUATION"
    REVERSAL = "REVERSAL"


@dataclass(frozen=True)
class ExitFamilyConfig:
    breakeven_atr_mult: float = 1.0
    enable_fast_lane_trail: bool = False
    enable_mm_half: bool = True
    enable_mm_runner: bool = True
    enable_profit_protect: bool = True
    enable_chandelier_trail: bool = True
    chandelier_active_atr_mult: float = 1.5
    time_stop_minutes: int | None = None
    partial_at_1r_fraction: float = 0.5


def family_for_setup(setup: str) -> tuple[ExitFamily, ExitFamilyConfig]:
    del setup
    return ExitFamily.REVERSAL, ExitFamilyConfig()


def parse_shrinkage_overrides(raw: str) -> list:
    del raw
    return []


def lookup_shrinkage_mult(setup: str, overrides, default: float = 1.0) -> float:
    del setup, overrides
    return float(default)
'''

OPP_MIXINS = '''
# ===== OppMixins（仅 OPP13 + 父类生命周期桩）=====
# OPP04/05/16 由 detectors 负责；OPP15/19 已从交易集删除，但父类 __init__/日切/on_15min
# 仍会调用 reset / mtf 更新，故保留空实现以免 AttributeError。

class _LifecycleStubMixin:
    def _reset_wedge_setup(self) -> None:
        self.wedge_setup_active = False
        self.wedge_confirmed_p3_high = 0.0
        self.wedge_trigger_line = 0.0
        self.wedge_arm_time = None
        self.wedge_current_alpha = 0.0
        self.wedge_p3_body_floor = 0.0
        self._wedge_direction = 0

    def _update_mtf_wedge_exhaustion_zone(self, atr_15: float) -> None:
        del atr_15
        return None

    def _reset_opening_drive(self) -> None:
        self._od_state = "IDLE"
        self._od_high = 0.0
        self._od_low = 0.0
        self._od_bars_collected = 0
        self._od_session_date = None
        self._od_bar1_shape = ""
        self._od_bar1_mid = 0.0
        self._od_bar1_range = 0.0


class OppMixins(Opp13Mixin, _LifecycleStubMixin):
    """单文件精简：仅 OPP13 mixin + 已删 OPP 的生命周期桩。"""
'''

SLIM_EXTRA = r'''
# ===== SLIM EXTRA OPP (04/05 only) =====
def init_extra_opp_state(strategy) -> None:
    strategy._ioi_setup_active = False
    strategy._ioi_mother_high = 0.0
    strategy._ioi_mother_low = 0.0
    strategy._ioi_lifecycle = 0


def advance_and_collect_extra_5m(
    strategy,
    bar,
    *,
    effective_context: str,
    atr_5: float,
    tick: float,
    stop_buffer: float,
    ema_20: float = 0.0,
    prev_high: float = 0.0,
    prev_low: float = 0.0,
    is_strong_bar: bool = False,
    is_oo: bool = False,
    is_long_climax: bool = False,
    is_short_climax: bool = False,
    bar_range: float = 0.0,
    body: float = 0.0,
    upper_shadow: float = 0.0,
    lower_shadow: float = 0.0,
    is_bull_reversal: bool = False,
    is_bear_reversal: bool = False,
    is_boundary_bull: bool = False,
    is_boundary_bear: bool = False,
) -> list:
    del (
        ema_20, prev_high, prev_low, is_long_climax, is_short_climax, body,
        upper_shadow, lower_shadow, is_bull_reversal, is_bear_reversal,
        is_boundary_bull, is_boundary_bear,
    )
    matches: list = []
    am = strategy.am_5min
    if getattr(strategy, "wedge_flag_enabled", False):
        matches.extend(
            match_opp04(
                strategy, bar, effective_context,
                atr_5=atr_5, tick=tick, stop_buffer=stop_buffer,
            )
        )
    if getattr(strategy, "ii_breakout_enabled", False):
        matches.extend(
            match_opp05_ii(
                strategy, bar, effective_context,
                atr_5=atr_5, tick=tick, is_strong_bar=is_strong_bar,
                is_oo=is_oo, bar_range=bar_range,
                ttr_rb_min_atr=float(getattr(strategy, "ttr_rb_min_atr", 5.0)),
                ttr_zone_max_atr_mult=float(getattr(strategy, "ttr_zone_max_atr_mult", 0.8)),
            )
        )
    if getattr(strategy, "ioi_breakout_enabled", False):
        if not strategy._ioi_setup_active:
            zone = detect_ioi_setup(
                am, atr_5=atr_5, tick=tick,
                ioi_min_zone_ticks=float(getattr(strategy, "ioi_min_zone_ticks", 4)),
                ioi_zone_max_atr_mult=float(getattr(strategy, "ioi_zone_max_atr_mult", 1.5)),
            )
            if zone:
                strategy._ioi_setup_active = True
                strategy._ioi_mother_high, strategy._ioi_mother_low = zone
                strategy._ioi_lifecycle = 0
        else:
            strategy._ioi_lifecycle += 1
            max_bars = int(getattr(strategy, "ioi_max_trigger_bars", 3))
            if strategy._ioi_lifecycle > max_bars:
                strategy._ioi_setup_active = False
            else:
                ioi_hits = match_opp05_ioi(
                    strategy, bar, effective_context,
                    atr_5=atr_5, tick=tick, is_strong_bar=is_strong_bar,
                    is_oo=is_oo,
                    ioi_setup_active=True,
                    mother_high=strategy._ioi_mother_high,
                    mother_low=strategy._ioi_mother_low,
                    ttr_rb_min_atr=float(getattr(strategy, "ttr_rb_min_atr", 5.0)),
                )
                if ioi_hits:
                    matches.extend(ioi_hits)
                    strategy._ioi_setup_active = False
    return matches


def collect_extra_15m(*_a, **_k) -> list:
    return []


def collect_extra_60m(*_a, **_k) -> list:
    return []


def note_failed_hl_on_close(*_a, **_k) -> None:
    return None


def try_failed_hl_fast_track_reverse(*_a, **_k) -> bool:
    return False


def try_failed_hl_on_stop(*_a, **_k) -> bool:
    return False


def is_h2l2_setup(*_a, **_k) -> bool:
    return False
'''

HEADER = '''# -*- coding: utf-8 -*-
"""pa_minimal 单文件策略（含精简 BrooksPaCtaStrategy）。

默认交易：OPP16 仅多 + OPP04 + OPP05 + OPP13。
版本：0.5.5_NO_AFF_ROUTER_LEDGER — 已剔除 AFF 路由、候选账本及
shadow/dry-scan/shrinkage/exit_v3/volume_bar 全文，
父类 on_5min_bar 死路径已剥离（子类覆盖）。

由 scripts/build_pa_minimal_single.py 生成。
外部依赖仅：vnpy / vnpy_ctastrategy / numpy / talib。
"""
from __future__ import annotations

import csv
import sys
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime, time
from enum import Enum
from pathlib import Path
from typing import Any, Literal, Optional, Protocol

import numpy as np
import talib
from vnpy.trader.constant import Direction, Offset
from vnpy.trader.object import BarData, OrderData, TradeData
from vnpy.trader.utility import ArrayManager, BarGenerator
from vnpy_ctastrategy import (
    ArrayManager as _CtaAM,
    BarData as _CtaBar,
    BarGenerator as _CtaBG,
    CtaTemplate,
    OrderData as _CtaOrder,
    TradeData as _CtaTrade,
)

# 统一别名（父类原文可能从 vnpy_ctastrategy 导入同名）
BarData = BarData
OrderData = OrderData
TradeData = TradeData
ArrayManager = ArrayManager
BarGenerator = BarGenerator

'''


def _patch_minimal_strategy(src: str) -> str:
    repls = [
        (
            'day_boundary_enabled = False     # OPP13',
            'day_boundary_enabled = True      # OPP13',
        ),
        (
            'wedge_flag_enabled = False       # OPP04',
            'wedge_flag_enabled = True        # OPP04',
        ),
        (
            'ii_breakout_enabled = False      # OPP05 II',
            'ii_breakout_enabled = True       # OPP05 II',
        ),
        (
            'ioi_breakout_enabled = False     # OPP05 IOI',
            'ioi_breakout_enabled = True      # OPP05 IOI',
        ),
        (
            'version = "0.5.1_OPP16_LONG_LAE"',
            'version = "0.5.5_NO_AFF_ROUTER_LEDGER"',
        ),
        (
            '"""冻结基线 OPP16_LONG_LAE：仅 OPP16 多 + defer invalid + LAE + 顺宽逆严。\n\n'
            '    空侧实验（2WAY / DYN）代码保留、默认关。PIN/1H 仍禁。\n'
            '    扩其它 OPP 须用 backtest overrides 对照，不得改 MINIMAL_BASE 为默认交易集。\n'
            '    """',
            '"""单文件精简：OPP16 仅多 + OPP04/05/13；已内联父类并剔除研究死路径。"""',
        ),
        (
            'disabled_setups = (\n'
            '        "OPP08_,OPP02_,OPP12_,OPP13_,OPP15_,OPP17_,OPP19_,"\n'
            '        "OPP03_,OPP04_,OPP05_,OPP06_,OPP07_,OPP09_,OPP10_,OPP11_,OPP14_,OPP18_,OPP20_,"\n'
            '        "OPP01_,"\n'
            '        "OPP16_5M_TWO_BAR_REV_SHORT,OPP16_5M_PIN_,OPP16_1H_"\n'
            '    )',
            'disabled_setups = (\n'
            '        "OPP08_,OPP02_,OPP12_,OPP15_,OPP17_,OPP19_,"\n'
            '        "OPP03_,OPP06_,OPP07_,OPP09_,OPP10_,OPP11_,OPP14_,OPP18_,OPP20_,"\n'
            '        "OPP01_,"\n'
            '        "OPP16_5M_TWO_BAR_REV_SHORT,OPP16_5M_PIN_,OPP16_1H_"\n'
            '    )',
        ),
    ]
    for a, b in repls:
        if a not in src:
            raise RuntimeError(f"patch missing: {a[:70]!r}")
        src = src.replace(a, b, 1)

    src = re.sub(
        r"\n        if self\.wedge_enabled:\n"
        r"            matches\.extend\(\n"
        r"                match_opp15_trigger\(\n"
        r"                    self, bar, atr_5=atr_5, tick=tick, is_strong_bar=is_strong_bar,\n"
        r"                \)\n"
        r"            \)\n",
        "\n",
        src,
        count=1,
    )
    src = re.sub(
        r"\n        matches\.extend\(\n"
        r"            match_opp08\(\n"
        r"[\s\S]*?"
        r"            \)\n"
        r"        \)\n",
        "\n",
        src,
        count=1,
    )
    src = re.sub(
        r"\n        if \(\n"
        r"            self\.overshoot_fail_enabled\n"
        r"            and effective_context in \(\"BULL_CHANNEL\", \"BEAR_CHANNEL\"\)\n"
        r"        \):\n"
        r"            matches\.extend\(\n"
        r"                match_opp12\(\n"
        r"[\s\S]*?"
        r"                \)\n"
        r"            \)\n",
        "\n",
        src,
        count=1,
    )
    src = re.sub(
        r"\n        if self\.ema_pullback_enabled:\n"
        r"            matches\.extend\(\n"
        r"                match_opp02\(\n"
        r"[\s\S]*?"
        r"                \)\n"
        r"            \)\n",
        "\n",
        src,
        count=1,
    )
    src = re.sub(
        r"\n        if self\.climax_rev_enabled:\n"
        r"            matches\.extend\(\n"
        r"                match_opp17\(\n"
        r"[\s\S]*?"
        r"                \)\n"
        r"            \)\n",
        "\n",
        src,
        count=1,
    )
    src = re.sub(
        r"\n        if self\.opening_drive_enabled:\n"
        r"            # 状态已由 _process_opening_drive 推进；此处仅作账本/对照候选\n"
        r"            matches\.extend\(\n"
        r"                match_opp19\(\n"
        r"[\s\S]*?"
        r"                \)\n"
        r"            \)\n",
        "\n",
        src,
        count=1,
    )
    src = re.sub(
        r"\n        # OPP15：先武装楔形 setup（检测器只读触发）\n"
        r"        if self\.wedge_enabled and not self\.wedge_setup_active and self\.machine_state == \"IDLE\" and not is_oo:\n"
        r"            self\._try_arm_wedge_setup\(bar, atr_5, tick\)\n",
        "\n",
        src,
        count=1,
    )
    src = re.sub(
        r"\n        # OPP19：状态机推进 \+ 可能直接武装（有副作用）\n"
        r"        if self\.opening_drive_enabled and self\.machine_state == \"IDLE\":\n"
        r"            if self\._process_opening_drive\(\n"
        r"                    bar, effective_context, atr_5, tick, stop_buffer, bar_range,\n"
        r"                    body, is_strong_bar, is_oo\):\n"
        r"                if not shadow:\n"
        r"                    self\._record_vsa_slot_volume\(bar\)\n"
        r"                    return\n",
        "\n",
        src,
        count=1,
    )
    src = re.sub(
        r"def _any_extra_opp_enabled\(self\) -> bool:\n"
        r"        return any\(\(\n"
        r"[\s\S]*?"
        r"        \)\)\n",
        "def _any_extra_opp_enabled(self) -> bool:\n"
        "        return any((\n"
        "            self.wedge_flag_enabled,\n"
        "            self.ii_breakout_enabled,\n"
        "            self.ioi_breakout_enabled,\n"
        "        ))\n",
        src,
        count=1,
    )
    src = re.sub(
        r"    ema_pullback_enabled = False     # OPP02\n"
        r"    climax_rev_enabled = False       # OPP17\n"
        r"    opening_drive_enabled = False    # OPP19\n"
        r"    opening_rev_enabled = False      # OPP19\n"
        r"    two_bar_rev_enabled = True       # OPP16（仅 LONG，见 disabled_setups）\n"
        r"    overshoot_fail_enabled = False   # OPP12\n"
        r"    day_boundary_enabled = True      # OPP13\n"
        r"    wedge_enabled = False            # OPP15\n"
        r"    # —— 其余 OPP 默认关；对照用 setting / CLI 打开 ——\n"
        r"    h1_l2_pullback_enabled = False   # OPP01\n"
        r"    m2_enabled = False               # OPP03\n"
        r"    wedge_flag_enabled = True        # OPP04\n"
        r"    ii_breakout_enabled = True       # OPP05 II\n"
        r"    ioi_breakout_enabled = True      # OPP05 IOI\n"
        r"    ttr_15m_enabled = False          # OPP06 15m\n"
        r"    ib_enabled = False               # OPP07 5m\n"
        r"    ib_15m_enabled = False           # OPP07 15m\n"
        r"    bp_enabled = False               # OPP09\n"
        r"    pdh_pdl_enabled = False          # OPP10\n"
        r"    tl_pullback_enabled = False      # OPP11\n"
        r"    hl_double_bottom_enabled = False # OPP14 5m\n"
        r"    hl_double_bottom_1h_enabled = False  # OPP14 1H\n"
        r"    two_bar_rev_pin_solo_enabled = False  # OPP16 Pin\n"
        r"    opp16_1h_enabled = False         # OPP16 1H\n"
        r"    failed_hl_enabled = False        # OPP18\n"
        r"    failed_hl_max_bars = 2           # H2/L2 进场后 N 根 5m 内快速止损才 pending\n"
        r"    gap_engine_enabled = False       # OPP20\n",
        "    two_bar_rev_enabled = True       # OPP16（仅 LONG，见 disabled_setups）\n"
        "    day_boundary_enabled = True      # OPP13\n"
        "    wedge_flag_enabled = True        # OPP04\n"
        "    ii_breakout_enabled = True       # OPP05 II\n"
        "    ioi_breakout_enabled = True      # OPP05 IOI\n"
        "    ema_pullback_enabled = False\n"
        "    climax_rev_enabled = False\n"
        "    opening_drive_enabled = False\n"
        "    opening_rev_enabled = False\n"
        "    overshoot_fail_enabled = False\n"
        "    wedge_enabled = False\n"
        "    failed_hl_enabled = False\n"
        "    failed_hl_max_bars = 2\n"
        "    ttr_15m_enabled = False\n"
        "    ib_enabled = False\n"
        "    ib_15m_enabled = False\n"
        "    hl_double_bottom_1h_enabled = False\n"
        "    opp16_1h_enabled = False\n"
        "    dryscan_compare_enabled = False\n",
        src,
        count=1,
    )
    src = re.sub(
        r"    parameters = list\(BrooksPaCtaStrategy\.parameters\) \+ \[\n"
        r"[\s\S]*?"
        r"    \]\n",
        "    parameters = list(BrooksPaCtaStrategy.parameters) + [\n"
        "        \"alpha_shadow_mode\",\n"
        "        \"context_mode\",\n"
        "        \"alt_r2_trend_min\",\n"
        "        \"alt_chop_trend_max\",\n"
        "        \"alt_chop_range_min\",\n"
        "        \"opp16_strict_shape\",\n"
        "        \"day_boundary_enabled\",\n"
        "        \"wedge_flag_enabled\",\n"
        "        \"ii_breakout_enabled\",\n"
        "        \"ioi_breakout_enabled\",\n"
        "        \"failed_hl_enabled\",\n"
        "        \"failed_hl_max_bars\",\n"
        "    ]\n",
        src,
        count=1,
    )
    # dry-scan 对照：保留空实现（默认关；避免删方法后误开炸）
    src = re.sub(
        r"\n    def _compare_with_dryscan\(\n"
        r"[\s\S]*?"
        r"(?=\n    def )",
        "\n    def _compare_with_dryscan(self, *_a, **_k) -> None:\n"
        "        return None\n",
        src,
        count=1,
    )
    return src


def _remove_methods(src: str, method_names: set[str], *, class_indent: int = 4) -> str:
    """按方法名删除类体内 def（含前置装饰器）。"""
    lines = src.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        # collect leading decorators at class_indent
        if lines[i].startswith(" " * class_indent + "@"):
            j = i
            while j < len(lines) and lines[j].startswith(" " * class_indent + "@"):
                j += 1
            if j < len(lines):
                m = re.match(
                    rf"^{' ' * class_indent}def (\w+)\(",
                    lines[j],
                )
                if m and m.group(1) in method_names:
                    i = j + 1
                    while i < len(lines):
                        line = lines[i]
                        if line.strip() == "":
                            i += 1
                            continue
                        ind = len(line) - len(line.lstrip(" \t"))
                        if ind <= class_indent and (
                            line.lstrip().startswith("def ")
                            or line.lstrip().startswith("@")
                            or line.lstrip().startswith("class ")
                        ):
                            break
                        i += 1
                    continue
        m = re.match(rf"^{' ' * class_indent}def (\w+)\(", lines[i])
        if m and m.group(1) in method_names:
            i += 1
            while i < len(lines):
                line = lines[i]
                if line.strip() == "":
                    i += 1
                    continue
                ind = len(line) - len(line.lstrip(" \t"))
                if ind <= class_indent and (
                    line.lstrip().startswith("def ")
                    or line.lstrip().startswith("@")
                    or line.lstrip().startswith("class ")
                ):
                    break
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return "".join(out)


def _remove_if_blocks(src: str, marker: str) -> str:
    """删除包含 marker 的完整 if 块。"""
    lines = src.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if marker in line and line.lstrip().startswith("if "):
            base_indent = len(line) - len(line.lstrip(" "))
            i += 1
            while i < len(lines):
                current = lines[i]
                if current.strip() == "":
                    i += 1
                    continue
                indent = len(current) - len(current.lstrip(" "))
                if indent <= base_indent:
                    break
                i += 1
            continue
        out.append(line)
        i += 1
    return "".join(out)


def _strip_parent_dead_paths(src: str) -> str:
    """删除子类已覆盖/单文件不可达的父类大块。"""
    dead = {
        "on_5min_bar",          # 子类完整覆盖
        "_shadow_dry_scan_bar", # shadow 研究路径
        "_aff_archetype_blocks_entry",
    }
    src = _remove_methods(src, dead)
    src = re.sub(
        r"    # EXP-013：AFF Archetype Router.*\n"
        r"(?:    aff_archetype_.+\n)+",
        "",
        src,
        count=1,
    )
    src = re.sub(
        r'        "aff_archetype_router_enabled".*\n'
        r'(?:        "aff_archetype_.+\n)+',
        "",
        src,
        count=1,
    )
    # 保留 AFF 基础 alpha 计算，删除 archetype 分类和路由。
    src = re.sub(
        r"\n        self\._aff_archetype = classify_aff_archetype\(\n"
        r"[\s\S]*?"
        r"\n        \)\n",
        "\n",
        src,
        count=1,
    )
    src = re.sub(
        r'^\s+self\._aff_archetype = "(?:NEUTRAL|LOW_ALPHA)"\n',
        "",
        src,
        flags=re.M,
    )
    src = re.sub(
        r"^\s+self\._aff_archetype_block_count = 0\n",
        "",
        src,
        flags=re.M,
    )
    src = re.sub(
        r"        self\._trend_bypass_prefixes = parse_prefix_list\(\n"
        r"            self\.aff_archetype_trend_bypass_prefixes or \"OPP08_\"\n"
        r"        \)\n",
        "",
        src,
        count=1,
    )
    src = _remove_if_blocks(src, "self._aff_archetype_blocks_entry(opportunity)")
    src = src.replace(
        '        if gate == "aff_archetype":\n'
        '            self._aff_archetype_block_count += 1\n'
        '        elif gate == "late_phase":\n',
        '        if gate == "late_phase":\n',
    )
    src = src.replace(
        '            "_aff_archetype_block_count": self._aff_archetype_block_count,\n',
        "",
    )
    return src


def _strip_candidate_ledger(src: str) -> str:
    """删除 pa_minimal 候选账本；不影响下单与成交归因。"""
    src = src.replace("    candidate_ledger_enabled = True\n", "")
    src = src.replace('        "candidate_ledger_enabled",\n', "")
    src = re.sub(
        r"\n        self\._candidate_ledger = CandidateLedger\(\n"
        r"            self\.vt_symbol\.split\(\"\.\"\)\[0\] if self\.vt_symbol else \"unknown\"\n"
        r"        \)\n",
        "\n",
        src,
        count=1,
    )
    src = _remove_if_blocks(
        src,
        'self.candidate_ledger_enabled and hasattr(self, "_candidate_ledger")',
    )
    src = src.replace(
        '        if self._aff_archetype_blocks_entry(opportunity):\n'
        '            return "aff_archetype"\n',
        "",
    )
    src = _remove_methods(src, {"get_candidate_ledger"})
    return src


def _append_file(parts: list[str], rel: str, tag: str) -> None:
    path = ROOT / "strategies" / rel
    body = _rewrite(_strip_module_doc_and_future(path.read_text(encoding="utf-8")), tag=tag)
    # drop duplicate std imports commonly repeated
    for line in (
        "import numpy as np\n",
        "import talib\n",
        "from datetime import datetime, time\n",
        "from datetime import time\n",
        "from datetime import datetime\n",
        "from pathlib import Path\n",
        "import sys\n",
        "from dataclasses import dataclass\n",
        "from dataclasses import dataclass, field\n",
        "from typing import Any, Literal\n",
        "from typing import Any\n",
        "from typing import Literal\n",
        "from typing import Optional, Protocol\n",
        "from typing import Protocol\n",
        "from typing import Optional\n",
        "from collections.abc import Callable\n",
        "from vnpy.trader.constant import Direction, Offset\n",
        "from vnpy_ctastrategy import ArrayManager\n",
    ):
        body = body.replace(line, "")
    # multi-line vnpy_ctastrategy import in strategy — keep CtaTemplate usage, drop block if present
    body = re.sub(
        r"from vnpy_ctastrategy import \(\n[\s\S]*?\)\n",
        "",
        body,
        count=1,
    )
    body = re.sub(
        r"from vnpy\.trader\.object import .+\n",
        "",
        body,
    )
    body = re.sub(
        r"from vnpy\.trader\.utility import .+\n",
        "",
        body,
    )
    parts.append(f"\n# ===== INLINE:{tag} ({rel}) =====\n")
    parts.append(body)
    if not body.endswith("\n"):
        parts.append("\n")


def main() -> None:
    parts: list[str] = [HEADER, DEAD_FEATURE_STUBS]
    for rel, tag in INLINE_BEFORE_PARENT:
        _append_file(parts, rel, tag)
    parts.append(OPP_MIXINS)

    # parent strategy（先内联再剥死路径）
    path = ROOT / "strategies" / "pa_cta" / "strategy.py"
    parent_body = _rewrite(
        _strip_module_doc_and_future(path.read_text(encoding="utf-8")),
        tag="BROOKS_PARENT",
    )
    for line in (
        "import numpy as np\n",
        "import talib\n",
        "from datetime import datetime, time\n",
        "from datetime import time\n",
        "from datetime import datetime\n",
        "from pathlib import Path\n",
        "import sys\n",
        "from vnpy.trader.constant import Direction, Offset\n",
    ):
        parent_body = parent_body.replace(line, "")
    parent_body = re.sub(
        r"from vnpy_ctastrategy import \(\n[\s\S]*?\)\n",
        "",
        parent_body,
        count=1,
    )
    parent_body = re.sub(r"from vnpy\.trader\.object import .+\n", "", parent_body)
    parent_body = re.sub(r"from vnpy\.trader\.utility import .+\n", "", parent_body)
    parent_body = _strip_parent_dead_paths(parent_body)
    parts.append("\n# ===== INLINE:BROOKS_PARENT (pa_cta/strategy.py, slimmed) =====\n")
    parts.append(parent_body)
    if not parent_body.endswith("\n"):
        parts.append("\n")

    # ensure bp aliases exist for parent + child
    parts.append(
        "\n# bar_patterns aliases\n"
        "bp_is_bear_reversal = is_bear_reversal\n"
        "bp_is_bull_reversal = is_bull_reversal\n"
        "bp_is_strong_bar = is_strong_bar\n"
    )

    for rel, tag in INLINE_AFTER_PARENT:
        _append_file(parts, rel, tag)

    parts.append(SLIM_EXTRA)

    strat = _rewrite(
        _strip_module_doc_and_future(
            (ROOT / "strategies" / "pa_minimal" / "strategy.py").read_text(encoding="utf-8")
        )
    )
    strat = re.sub(r"^import numpy as np\n", "", strat, count=1, flags=re.M)
    strat = re.sub(
        r"^from vnpy\.trader\.(object|constant|utility) import .+\n",
        "",
        strat,
        flags=re.M,
    )
    strat = _patch_minimal_strategy(strat)
    strat = _strip_candidate_ledger(strat)
    # dry-scan 已剔除：子类若仍调用 _compare_with_dryscan，用空实现兜底
    parts.append(
        "\n"
        "def dry_match_opp08(*_a, **_k) -> list:\n"
        "    return []\n\n"
        "def dry_match_opp16(*_a, **_k) -> list:\n"
        "    return []\n"
    )
    parts.append("\n# ===== STRATEGY BODY =====\n")
    parts.append(strat)

    text = re.sub(r"\n{4,}", "\n\n\n", "".join(parts))
    text = text.replace("def _aff_aff_efficiency_ratio", "def _aff_efficiency_ratio")
    text = text.replace("def _context_context_efficiency_ratio", "def _context_efficiency_ratio")

    OUT.write_text(text, encoding="utf-8")
    ast.parse(text)
    print(f"Wrote {OUT} ({OUT.stat().st_size:,} bytes, {text.count(chr(10)) + 1} lines)")
    assert "from strategies.pa_cta.strategy import" not in text
    assert "class BrooksPaCtaStrategy" in text
    assert "class PaMinimal0816Strategy" in text
    assert "class VolumeBarGenerator" in text
    assert "def on_5min_bar(self, bar: BarData) -> None:" in text  # child still has it
    # parent on_5min should be gone — count occurrences of signature after BROOKS marker
    parent_chunk = text.split("INLINE:BROOKS_PARENT")[1].split("STRATEGY BODY")[0]
    assert "def on_5min_bar(self, bar: BarData) -> None:" not in parent_chunk


if __name__ == "__main__":
    main()
