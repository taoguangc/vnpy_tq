# -*- coding: utf-8 -*-
"""pa_minimal 第二阶段：固定 cohort 出场族对照与定仓成本敏感度。"""
from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from research.arm_lab import ArmRule, bars_to_frame, run_arm_lab
from research.pa_minimal_baseline import COST_RATE, SIZING_TIERS
from research.trade_management_lab import (
    CohortTrade,
    ExitRule,
    _compute_atr5_map,
    format_summary_table,
    run_management_lab,
    summarize_by_setup,
)
from strategies.pa_minimal.backtest import run_minimal_backtest


def _direction_label(d: int) -> str:
    return "多" if d > 0 else "空"


def arm_fills_to_cohort(
    arm_detail: pd.DataFrame,
    bars_1m: list,
    *,
    contract_size: float,
    rule: str = "A_CURRENT",
) -> list[CohortTrade]:
    """将 arm_lab 成交记录转为 TM Lab cohort。"""
    filled = arm_detail[(arm_detail["rule"] == rule) & (arm_detail["filled"] == True)].copy()  # noqa: E712
    if filled.empty:
        return []
    df = bars_to_frame(bars_1m)
    df["dt_cst"] = pd.to_datetime(df["datetime"])
    if df["dt_cst"].dt.tz is None:
        df["dt_cst"] = df["dt_cst"].dt.tz_localize("Asia/Shanghai")
    else:
        df["dt_cst"] = df["dt_cst"].dt.tz_convert("Asia/Shanghai")
    atr_map = _compute_atr5_map(df)
    cohort: list[CohortTrade] = []
    for _, row in filled.iterrows():
        direction = int(row["direction"])
        entry_price = float(row["fill_price"])
        stop = float(row["stop"])
        init_r = abs(entry_price - stop) * contract_size
        if init_r <= 0:
            continue
        entry_time = pd.Timestamp(row["fill_time"])
        if entry_time.tzinfo is None:
            entry_time = entry_time.tz_localize("Asia/Shanghai")
        else:
            entry_time = entry_time.tz_convert("Asia/Shanghai")
        entry_time = entry_time.to_pydatetime()
        idx = df["dt_cst"].searchsorted(pd.Timestamp(entry_time))
        idx = min(max(int(idx), 0), len(df) - 1)
        atr_5 = float(atr_map.iloc[idx]) if len(atr_map) else 0.0
        gross_1lot = float(row["net_pnl_1lot"])
        cohort.append(
            CohortTrade(
                setup=str(row["setup"]),
                direction=_direction_label(direction),
                entry_time=entry_time,
                entry_price=entry_price,
                initial_stop=stop,
                initial_r_yuan=init_r,
                volume=1.0,
                actual_net_pnl=gross_1lot,
                actual_exit_reason=str(row.get("exit_tag") or "ARM_LAB"),
                atr_5_price=atr_5,
            )
        )
    return cohort


def run_exit_family_lab(
    cohort: list[CohortTrade],
    bars_1m: list,
    *,
    contract_size: float,
    slippage: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """固定入场 cohort 上对比 ACTUAL / 两族出场 / 路由出场。"""
    df = bars_to_frame(bars_1m)
    df["dt_cst"] = pd.to_datetime(df["datetime"])
    if df["dt_cst"].dt.tz is None:
        df["dt_cst"] = df["dt_cst"].dt.tz_localize("Asia/Shanghai")
    else:
        df["dt_cst"] = df["dt_cst"].dt.tz_convert("Asia/Shanghai")
    rules = [
        ExitRule.ACTUAL,
        ExitRule.FAMILY_CONTINUATION,
        ExitRule.FAMILY_REVERSAL,
        ExitRule.FAMILY_ASSIGNED,
        ExitRule.FIXED_1R,
        ExitRule.TIME_120,
    ]
    results, summaries = run_management_lab(
        cohort,
        df,
        contract_size=contract_size,
        rate=COST_RATE,
        slippage=slippage,
        rules=rules,
    )
    sum_df = pd.DataFrame([
        {
            "rule": s.rule.value if hasattr(s.rule, "value") else str(s.rule),
            "n": s.n,
            "skipped": s.skipped,
            "net_pnl": s.net_pnl,
            "win_rate": s.win_rate,
            "profit_factor": s.profit_factor,
            "avg_r": s.avg_r,
            "avg_holding_min": s.avg_holding_min,
            "vs_actual_delta": s.vs_actual_delta,
        }
        for s in summaries
    ])
    detail_rows = []
    for rule, sims in results.items():
        for sim in sims:
            detail_rows.append({
                "rule": rule.value,
                "setup": sim.setup,
                "net_pnl": sim.net_pnl,
                "r_multiple": sim.r_multiple,
                "exit_tag": sim.exit_tag,
            })
    return sum_df, pd.DataFrame(detail_rows)


def run_sizing_sensitivity(
    symbol: str,
    *,
    tiers: tuple[tuple[str, int], ...] | None = None,
    baseline_bt: dict | None = None,
) -> pd.DataFrame:
    """低/中/现行三档 max_position 成本敏感度。

    若传入 baseline_bt（现行档回测结果），则不再重复跑 CURRENT。
    """
    tiers = tiers or SIZING_TIERS
    rows: list[dict[str, Any]] = []
    for label, max_pos in tiers:
        if label == "CURRENT" and baseline_bt is not None:
            bt = baseline_bt
        else:
            bt = run_minimal_backtest(
                symbol=symbol,
                verbose=False,
                strategy_overrides={"max_position": max_pos},
            )
        stats = bt["stats"]
        trips = bt["round_trips"]
        gross = sum(t.gross_pnl for t in trips)
        net = sum(t.net_pnl for t in trips)
        cost = gross - net
        vols = [t.volume for t in trips]
        rows.append({
            "tier": label,
            "max_position": max_pos,
            "n_rt": len(trips),
            "gross_pnl": gross,
            "net_pnl": net,
            "cost": cost,
            "sharpe": float(stats.get("sharpe_ratio") or 0.0),
            "vol_median": float(pd.Series(vols).median()) if vols else 0.0,
            "vol_max": float(max(vols)) if vols else 0.0,
            "at_cap_pct": float(sum(1 for v in vols if v >= max_pos) / len(vols)) if vols else 0.0,
        })
    return pd.DataFrame(rows)


def run_arm_then_exit(
    cohort_records: list[dict],
    bars_1m: list,
    *,
    symbol: str,
    root,
    retest_window: int = 30,
) -> tuple[pd.DataFrame, pd.DataFrame, list[CohortTrade]]:
    """导出 A 武装成交 → 出场族 Lab。"""
    from strategies.pa_minimal.symbol_config import resolve_minimal_profile

    profile = resolve_minimal_profile(symbol, root)
    tick = float(profile["pricetick"])
    contract_size = float(profile["size"])
    slippage = float(profile["slippage"])
    sims, arm_summary = run_arm_lab(
        cohort_records,
        bars_1m,
        tick=tick,
        contract_size=contract_size,
        retest_window=retest_window,
    )
    arm_detail = pd.DataFrame([s.__dict__ for s in sims])
    cohort = arm_fills_to_cohort(arm_detail, bars_1m, contract_size=contract_size)
    exit_sum, exit_detail = run_exit_family_lab(
        cohort, bars_1m, contract_size=contract_size, slippage=slippage,
    )
    return arm_detail, exit_sum, cohort
