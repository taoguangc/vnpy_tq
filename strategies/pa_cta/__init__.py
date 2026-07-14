# -*- coding: utf-8 -*-
"""Brooks PA CTA 精简策略包（自 pa_lean 复制，适配 vnpy_tq 数据路径）。

默认 ``run_parquet_backtest()`` → 天勤 CbC + ``BrooksPaCtaRolloverStrategy``。
"""
from .backtest import print_backtest_report, run_parquet_backtest, run_tq_cbc_backtest
from .rollover_strategy import BrooksPaCtaRolloverStrategy
from .strategy import BrooksPaCtaStrategy
from .symbol_config import (
    SYMBOL_PROFILES,
    TQ_CBC_BASELINE_RB,
    TQ_EXEC_BASELINE_RB,
    TQ_LEAN_DEFAULT_MODE,
    build_strategy_setting,
    resolve_symbol_profile,
    resolve_tq_cbc_paths,
)

__all__ = [
    "BrooksPaCtaStrategy",
    "BrooksPaCtaRolloverStrategy",
    "print_backtest_report",
    "run_parquet_backtest",
    "run_tq_cbc_backtest",
    "SYMBOL_PROFILES",
    "TQ_CBC_BASELINE_RB",
    "TQ_EXEC_BASELINE_RB",
    "TQ_LEAN_DEFAULT_MODE",
    "build_strategy_setting",
    "resolve_symbol_profile",
    "resolve_tq_cbc_paths",
]
