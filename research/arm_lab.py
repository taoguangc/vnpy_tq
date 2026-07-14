# -*- coding: utf-8 -*-
"""固定 signal cohort 上的武装（arm）离线重放。

三种规则：
  A CURRENT     — OPP08 FAST_TRACK；OPP16 PENDING_CONFIRM（生产默认）
  B NEXT_CLOSE  — 统一下一根 5m 收盘确认
  C RETEST      — 触发位突破后，限时窗口内回踩并重新收回（retest/reclaim）

出场冻结为：止损 / 触及 1R 止盈 / 120 分钟超时（先到先出，同 bar 止损优先）。
不改变候选集合；每条候选独立重放，避免持仓路径污染。
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import numpy as np
import pandas as pd


class ArmRule(str, Enum):
    CURRENT = "A_CURRENT"
    NEXT_CLOSE = "B_NEXT_CLOSE"
    RETEST = "C_RETEST"


@dataclass
class ArmSim:
    rule: str
    setup: str
    direction: int
    signal_time: datetime
    trigger: float
    stop: float
    filled: bool
    fill_time: datetime | None = None
    fill_price: float = 0.0
    miss_reason: str = ""
    exit_time: datetime | None = None
    exit_price: float = 0.0
    exit_tag: str = ""
    net_pnl_1lot: float = 0.0  # 1 手价差毛额（未乘成本前）
    r_multiple: float = 0.0
    mfe_r: float = 0.0
    mae_r: float = 0.0
    hit_1r: bool = False
    hit_2r: bool = False
    slip_ticks: float = 0.0


def _to_naive(dt: datetime | str | None) -> datetime | None:
    if dt is None:
        return None
    if isinstance(dt, str):
        dt = pd.Timestamp(dt).to_pydatetime()
    if getattr(dt, "tzinfo", None) is not None:
        return dt.replace(tzinfo=None)
    return dt


def bars_to_frame(bars: list) -> pd.DataFrame:
    rows = []
    for b in bars:
        rows.append(
            {
                "datetime": _to_naive(b.datetime),
                "open": float(b.open_price),
                "high": float(b.high_price),
                "low": float(b.low_price),
                "close": float(b.close_price),
            }
        )
    df = pd.DataFrame(rows).sort_values("datetime").reset_index(drop=True)
    return df


def _next_5m_close_bar(df: pd.DataFrame, signal_time: datetime) -> dict | None:
    """信号 5m 收盘后的下一根完整 5m（用 1m 聚合：信号后第 5 根 1m 的收盘）。"""
    # 信号时刻通常是 5m 边界；下一根 5m = 信号后 (0,5] 分钟的 5 根 1m
    start = signal_time + timedelta(minutes=1)
    end = signal_time + timedelta(minutes=5)
    sub = df[(df["datetime"] >= start) & (df["datetime"] <= end)]
    if len(sub) < 1:
        return None
    return {
        "datetime": sub.iloc[-1]["datetime"],
        "open": float(sub.iloc[0]["open"]),
        "high": float(sub["high"].max()),
        "low": float(sub["low"].min()),
        "close": float(sub.iloc[-1]["close"]),
    }


def _stop_fill_price(direction: int, bar_open: float, trigger: float) -> float:
    if direction > 0:
        return max(bar_open, trigger)
    return min(bar_open, trigger)


def _try_fast_track_fill(
    df: pd.DataFrame,
    *,
    signal_time: datetime,
    direction: int,
    trigger: float,
    stop: float,
    max_minutes: int = 25,
) -> tuple[bool, datetime | None, float, str]:
    start = signal_time + timedelta(minutes=1)
    end = signal_time + timedelta(minutes=max_minutes)
    sub = df[(df["datetime"] >= start) & (df["datetime"] <= end)]
    for _, row in sub.iterrows():
        ts = row["datetime"]
        o, h, l = float(row["open"]), float(row["high"]), float(row["low"])
        # 先检查是否先打止损失效（未成交前结构破坏）
        if direction > 0 and l <= stop:
            return False, None, 0.0, "invalidated_stop"
        if direction < 0 and h >= stop:
            return False, None, 0.0, "invalidated_stop"
        if direction > 0 and h >= trigger:
            return True, ts, _stop_fill_price(1, o, trigger), ""
        if direction < 0 and l <= trigger:
            return True, ts, _stop_fill_price(-1, o, trigger), ""
    return False, None, 0.0, "timeout"


def _try_pending_confirm(
    df: pd.DataFrame,
    *,
    signal_time: datetime,
    direction: int,
    trigger: float,
    tick: float,
) -> tuple[bool, datetime | None, float, str]:
    bar5 = _next_5m_close_bar(df, signal_time)
    if bar5 is None:
        return False, None, 0.0, "no_next_5m"
    c, o = bar5["close"], bar5["open"]
    if direction > 0:
        if c > o and c > trigger:
            return True, bar5["datetime"], c + tick, ""
        return False, None, 0.0, "no_confirm"
    if c < o and c < trigger:
        return True, bar5["datetime"], c - tick, ""
    return False, None, 0.0, "no_confirm"


def _try_retest_reclaim(
    df: pd.DataFrame,
    *,
    signal_time: datetime,
    direction: int,
    trigger: float,
    stop: float,
    tick: float,
    window_minutes: int = 30,
) -> tuple[bool, datetime | None, float, str]:
    start = signal_time + timedelta(minutes=1)
    end = signal_time + timedelta(minutes=window_minutes)
    sub = df[(df["datetime"] >= start) & (df["datetime"] <= end)]
    broke = False
    pulled = False
    for _, row in sub.iterrows():
        ts = row["datetime"]
        o, h, l, c = (
            float(row["open"]),
            float(row["high"]),
            float(row["low"]),
            float(row["close"]),
        )
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
        if not pulled:
            # 回踩：回到触发位内侧至少一个 tick
            if direction > 0 and l <= trigger - tick:
                pulled = True
            elif direction < 0 and h >= trigger + tick:
                pulled = True
            continue
        # 收回：收盘重新越过触发位
        if direction > 0 and c >= trigger:
            return True, ts, c + tick, ""
        if direction < 0 and c <= trigger:
            return True, ts, c - tick, ""
    if not broke:
        return False, None, 0.0, "no_break"
    if not pulled:
        return False, None, 0.0, "no_retest"
    return False, None, 0.0, "no_reclaim"


def _path_stats(
    df: pd.DataFrame,
    *,
    fill_time: datetime,
    direction: int,
    fill_price: float,
    stop: float,
    horizon_minutes: int = 120,
) -> tuple[float, float, bool, bool, datetime, float, str, float]:
    """返回 mfe_r, mae_r, hit_1r, hit_2r, exit_time, exit_price, exit_tag, r_multiple。"""
    risk = abs(fill_price - stop)
    if risk <= 1e-12:
        return 0.0, 0.0, False, False, fill_time, fill_price, "ZERO_RISK", 0.0
    target_1r = fill_price + direction * risk
    target_2r = fill_price + direction * 2.0 * risk
    end = fill_time + timedelta(minutes=horizon_minutes)
    sub = df[(df["datetime"] > fill_time) & (df["datetime"] <= end)]
    mfe = 0.0
    mae = 0.0
    hit_1r = False
    hit_2r = False
    exit_time = fill_time
    exit_price = fill_price
    exit_tag = "TIME"
    r_mult = 0.0
    if sub.empty:
        return 0.0, 0.0, False, False, fill_time, fill_price, "NO_PATH", 0.0
    for _, row in sub.iterrows():
        ts = row["datetime"]
        o, h, l = float(row["open"]), float(row["high"]), float(row["low"])
        if direction > 0:
            mfe = max(mfe, (h - fill_price) / risk)
            mae = max(mae, (fill_price - l) / risk)
            stop_hit = l <= stop
            t1 = h >= target_1r
            t2 = h >= target_2r
            if stop_hit and t1:
                # 同 bar 止损优先
                exit_price = min(o, stop)
                exit_tag = "STOP"
                exit_time = ts
                r_mult = (exit_price - fill_price) / risk
                return mfe, mae, hit_1r or t1, hit_2r or t2, exit_time, exit_price, exit_tag, r_mult
            if stop_hit:
                exit_price = min(o, stop)
                exit_tag = "STOP"
                exit_time = ts
                r_mult = (exit_price - fill_price) / risk
                return mfe, mae, hit_1r, hit_2r, exit_time, exit_price, exit_tag, r_mult
            if t2:
                hit_1r = True
                hit_2r = True
                exit_price = max(o, target_1r)  # 按 1R 出场做可比期望
                exit_tag = "TARGET_1R"
                exit_time = ts
                r_mult = (exit_price - fill_price) / risk
                return mfe, mae, True, True, exit_time, exit_price, exit_tag, r_mult
            if t1:
                hit_1r = True
                exit_price = max(o, target_1r)
                exit_tag = "TARGET_1R"
                exit_time = ts
                r_mult = (exit_price - fill_price) / risk
                return mfe, mae, True, hit_2r, exit_time, exit_price, exit_tag, r_mult
        else:
            mfe = max(mfe, (fill_price - l) / risk)
            mae = max(mae, (h - fill_price) / risk)
            stop_hit = h >= stop
            t1 = l <= target_1r
            t2 = l <= target_2r
            if stop_hit and t1:
                exit_price = max(o, stop)
                exit_tag = "STOP"
                exit_time = ts
                r_mult = (fill_price - exit_price) / risk
                return mfe, mae, hit_1r or t1, hit_2r or t2, exit_time, exit_price, exit_tag, r_mult
            if stop_hit:
                exit_price = max(o, stop)
                exit_tag = "STOP"
                exit_time = ts
                r_mult = (fill_price - exit_price) / risk
                return mfe, mae, hit_1r, hit_2r, exit_time, exit_price, exit_tag, r_mult
            if t2:
                hit_1r = True
                hit_2r = True
                exit_price = min(o, target_1r)
                exit_tag = "TARGET_1R"
                exit_time = ts
                r_mult = (fill_price - exit_price) / risk
                return mfe, mae, True, True, exit_time, exit_price, exit_tag, r_mult
            if t1:
                hit_1r = True
                exit_price = min(o, target_1r)
                exit_tag = "TARGET_1R"
                exit_time = ts
                r_mult = (fill_price - exit_price) / risk
                return mfe, mae, True, hit_2r, exit_time, exit_price, exit_tag, r_mult
    # 超时：以最后收盘平
    last = sub.iloc[-1]
    exit_time = last["datetime"]
    exit_price = float(last["close"])
    exit_tag = "TIME_120"
    if direction > 0:
        r_mult = (exit_price - fill_price) / risk
    else:
        r_mult = (fill_price - exit_price) / risk
    return mfe, mae, hit_1r, hit_2r, exit_time, exit_price, exit_tag, r_mult


def resolve_arm_mode(rule: ArmRule, setup: str, default_mode: str) -> str:
    if rule == ArmRule.CURRENT:
        return default_mode or ("FAST_TRACK" if setup.startswith("OPP08_") else "PENDING_CONFIRM")
    if rule == ArmRule.NEXT_CLOSE:
        return "PENDING_CONFIRM"
    return "RETEST"


def simulate_one(
    df: pd.DataFrame,
    cand: dict[str, Any],
    rule: ArmRule,
    *,
    tick: float,
    contract_size: float,
    retest_window: int = 30,
) -> ArmSim:
    signal_time = _to_naive(cand["time"])
    setup = str(cand["setup"])
    direction = int(cand["direction"])
    trigger = float(cand["trigger"])
    stop = float(cand["stop"])
    default_mode = str(cand.get("arm_mode") or "")
    mode = resolve_arm_mode(rule, setup, default_mode)

    if mode == "FAST_TRACK":
        filled, ft, fp, miss = _try_fast_track_fill(
            df, signal_time=signal_time, direction=direction, trigger=trigger, stop=stop
        )
    elif mode == "PENDING_CONFIRM":
        filled, ft, fp, miss = _try_pending_confirm(
            df, signal_time=signal_time, direction=direction, trigger=trigger, tick=tick
        )
    else:
        filled, ft, fp, miss = _try_retest_reclaim(
            df,
            signal_time=signal_time,
            direction=direction,
            trigger=trigger,
            stop=stop,
            tick=tick,
            window_minutes=retest_window,
        )

    sim = ArmSim(
        rule=rule.value,
        setup=setup,
        direction=direction,
        signal_time=signal_time,
        trigger=trigger,
        stop=stop,
        filled=filled,
        fill_time=ft,
        fill_price=fp,
        miss_reason=miss,
    )
    if not filled:
        return sim

    sim.slip_ticks = abs(fp - trigger) / tick if tick > 0 else 0.0
    mfe, mae, h1, h2, et, ep, tag, rm = _path_stats(
        df,
        fill_time=ft,
        direction=direction,
        fill_price=fp,
        stop=stop,
    )
    sim.mfe_r = mfe
    sim.mae_r = mae
    sim.hit_1r = h1
    sim.hit_2r = h2
    sim.exit_time = et
    sim.exit_price = ep
    sim.exit_tag = tag
    sim.r_multiple = rm
    if direction > 0:
        sim.net_pnl_1lot = (ep - fp) * contract_size
    else:
        sim.net_pnl_1lot = (fp - ep) * contract_size
    return sim


def summarize_sims(sims: list[ArmSim], *, setup_filter: str | None = None) -> dict:
    rows = sims
    if setup_filter:
        rows = [s for s in sims if s.setup.startswith(setup_filter)]
    n = len(rows)
    filled = [s for s in rows if s.filled]
    nf = len(filled)
    miss = {}
    for s in rows:
        if not s.filled:
            miss[s.miss_reason] = miss.get(s.miss_reason, 0) + 1
    if not filled:
        return {
            "n_candidates": n,
            "n_filled": 0,
            "fill_rate": 0.0,
            "avg_slip_ticks": float("nan"),
            "hit_1r_rate": float("nan"),
            "hit_2r_rate": float("nan"),
            "avg_mfe_r": float("nan"),
            "avg_mae_r": float("nan"),
            "avg_r": float("nan"),
            "sum_pnl_1lot": 0.0,
            "pf": float("nan"),
            "miss": miss,
        }
    wins = [s for s in filled if s.net_pnl_1lot > 0]
    losses = [s for s in filled if s.net_pnl_1lot < 0]
    gp = sum(s.net_pnl_1lot for s in wins)
    gl = abs(sum(s.net_pnl_1lot for s in losses))
    return {
        "n_candidates": n,
        "n_filled": nf,
        "fill_rate": nf / n if n else 0.0,
        "avg_slip_ticks": float(np.mean([s.slip_ticks for s in filled])),
        "hit_1r_rate": sum(1 for s in filled if s.hit_1r) / nf,
        "hit_2r_rate": sum(1 for s in filled if s.hit_2r) / nf,
        "avg_mfe_r": float(np.mean([s.mfe_r for s in filled])),
        "avg_mae_r": float(np.mean([s.mae_r for s in filled])),
        "avg_r": float(np.mean([s.r_multiple for s in filled])),
        "sum_pnl_1lot": sum(s.net_pnl_1lot for s in filled),
        "pf": (gp / gl) if gl > 1e-9 else float("inf"),
        "miss": miss,
    }


def run_arm_lab(
    candidates: list[dict],
    bars: list,
    *,
    tick: float,
    contract_size: float,
    retest_window: int = 30,
) -> tuple[list[ArmSim], pd.DataFrame]:
    """仅对 gate_pass=True 的候选重放。"""
    cohort = [c for c in candidates if c.get("gate_pass")]
    df = bars_to_frame(bars)
    sims: list[ArmSim] = []
    for cand in cohort:
        for rule in ArmRule:
            sims.append(
                simulate_one(
                    df,
                    cand,
                    rule,
                    tick=tick,
                    contract_size=contract_size,
                    retest_window=retest_window,
                )
            )
    summary_rows = []
    for rule in ArmRule:
        rule_sims = [s for s in sims if s.rule == rule.value]
        for filt, label in ((None, "ALL"), ("OPP08_", "OPP08"), ("OPP16_", "OPP16")):
            m = summarize_sims(rule_sims, setup_filter=filt)
            summary_rows.append({"rule": rule.value, "group": label, **m, "miss": str(m["miss"])})
    return sims, pd.DataFrame(summary_rows)
