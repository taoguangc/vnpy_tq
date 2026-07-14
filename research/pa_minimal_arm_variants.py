# -*- coding: utf-8 -*-
"""pa_minimal 第二阶段：OPP 专属武装微调（仅在固定 cohort 离线重放）。"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

import numpy as np
import pandas as pd

from research.arm_lab import (
    ArmRule,
    ArmSim,
    _path_stats,
    _stop_fill_price,
    _try_fast_track_fill,
    _try_pending_confirm,
    bars_to_frame,
    summarize_sims,
)


class ArmVariant(str, Enum):
    A_CURRENT = "A_CURRENT"
    D08_LIMITED = "D08_LIMITED"  # OPP08：突破后限时继续价确认（15m）
    E16_MAX_CHASE = "E16_MAX_CHASE"  # OPP16：确认后最大追价（2 tick）


def _try_opp08_limited_confirm(
    df: pd.DataFrame,
    *,
    signal_time: datetime,
    direction: int,
    trigger: float,
    stop: float,
    tick: float,
    window_minutes: int = 15,
) -> tuple[bool, datetime | None, float, str]:
    """突破后限时继续价确认：先破触发位，再在窗口内收盘维持突破侧。"""
    start = signal_time + timedelta(minutes=1)
    end = signal_time + timedelta(minutes=window_minutes)
    sub = df[(df["datetime"] >= start) & (df["datetime"] <= end)]
    broke = False
    for _, row in sub.iterrows():
        ts = row["datetime"]
        o, h, l, c = float(row["open"]), float(row["high"]), float(row["low"]), float(row["close"])
        if direction > 0 and l <= stop:
            return False, None, 0.0, "invalidated_stop"
        if direction < 0 and h >= stop:
            return False, None, 0.0, "invalidated_stop"
        if not broke:
            if direction > 0 and h >= trigger:
                broke = True
            elif direction < 0 and l <= trigger:
                broke = True
            continue
        if direction > 0 and c > trigger and c > o:
            return True, ts, c + tick, ""
        if direction < 0 and c < trigger and c < o:
            return True, ts, c - tick, ""
    if not broke:
        return False, None, 0.0, "no_break"
    return False, None, 0.0, "no_confirm"


def _try_opp16_max_chase(
    df: pd.DataFrame,
    *,
    signal_time: datetime,
    direction: int,
    trigger: float,
    tick: float,
    max_chase_ticks: float = 2.0,
) -> tuple[bool, datetime | None, float, str]:
    """收盘确认后，入场价不得劣于触发位超过 max_chase_ticks。"""
    ok, ft, fp, reason = _try_pending_confirm(
        df, signal_time=signal_time, direction=direction, trigger=trigger, tick=tick,
    )
    if not ok:
        return False, None, 0.0, reason
    limit = max_chase_ticks * tick
    if direction > 0 and fp > trigger + limit:
        return False, None, 0.0, "chase_too_wide"
    if direction < 0 and fp < trigger - limit:
        return False, None, 0.0, "chase_too_wide"
    return True, ft, fp, ""


def simulate_variant(
    df: pd.DataFrame,
    cand: dict,
    variant: ArmVariant,
    *,
    tick: float,
    contract_size: float,
) -> ArmSim:
    """单候选武装变体重放。"""
    setup = str(cand.get("setup") or "")
    direction = int(cand.get("direction") or 0)
    trigger = float(cand.get("trigger") or 0.0)
    stop = float(cand.get("stop") or 0.0)
    signal_time = pd.Timestamp(cand.get("time")).to_pydatetime()

    filled = False
    fill_time = None
    fill_price = 0.0
    miss = ""

    if variant == ArmVariant.A_CURRENT:
        if setup.startswith("OPP08"):
            filled, fill_time, fill_price, miss = _try_fast_track_fill(
                df, signal_time=signal_time, direction=direction, trigger=trigger, stop=stop,
            )
        else:
            filled, fill_time, fill_price, miss = _try_pending_confirm(
                df, signal_time=signal_time, direction=direction, trigger=trigger, tick=tick,
            )
    elif variant == ArmVariant.D08_LIMITED:
        if setup.startswith("OPP08"):
            filled, fill_time, fill_price, miss = _try_opp08_limited_confirm(
                df, signal_time=signal_time, direction=direction, trigger=trigger, stop=stop, tick=tick,
            )
        else:
            filled, fill_time, fill_price, miss = _try_pending_confirm(
                df, signal_time=signal_time, direction=direction, trigger=trigger, tick=tick,
            )
    elif variant == ArmVariant.E16_MAX_CHASE:
        if setup.startswith("OPP16"):
            filled, fill_time, fill_price, miss = _try_opp16_max_chase(
                df, signal_time=signal_time, direction=direction, trigger=trigger, tick=tick,
            )
        else:
            filled, fill_time, fill_price, miss = _try_fast_track_fill(
                df, signal_time=signal_time, direction=direction, trigger=trigger, stop=stop,
            )

    sim = ArmSim(
        rule=variant.value,
        setup=setup,
        direction=direction,
        signal_time=signal_time,
        trigger=trigger,
        stop=stop,
        filled=filled,
        miss_reason=miss,
    )
    if not filled:
        return sim

    mfe, mae, h1, h2, et, ep, tag, r_mult = _path_stats(
        df, fill_time=fill_time, direction=direction, fill_price=fill_price, stop=stop,
    )
    slip = abs(fill_price - trigger) / tick if tick > 0 else 0.0
    if direction > 0:
        gross = (ep - fill_price) * contract_size
    else:
        gross = (fill_price - ep) * contract_size
    sim.fill_time = fill_time
    sim.fill_price = fill_price
    sim.exit_time = et
    sim.exit_price = ep
    sim.exit_tag = tag
    sim.net_pnl_1lot = gross
    sim.r_multiple = r_mult
    sim.mfe_r = mfe
    sim.mae_r = mae
    sim.hit_1r = h1
    sim.hit_2r = h2
    sim.slip_ticks = slip
    return sim


def run_arm_variants(
    candidates: list[dict],
    bars: list,
    *,
    tick: float,
    contract_size: float,
) -> tuple[list[ArmSim], pd.DataFrame]:
    cohort = [c for c in candidates if c.get("gate_pass")]
    df = bars_to_frame(bars)
    sims: list[ArmSim] = []
    for cand in cohort:
        for variant in ArmVariant:
            sims.append(simulate_variant(df, cand, variant, tick=tick, contract_size=contract_size))
    rows = []
    for variant in ArmVariant:
        vs = [s for s in sims if s.rule == variant.value]
        for filt, label in ((None, "ALL"), ("OPP08_", "OPP08"), ("OPP16_", "OPP16")):
            m = summarize_sims(vs, setup_filter=filt)
            rows.append({"rule": variant.value, "group": label, **m})
    return sims, pd.DataFrame(rows)
