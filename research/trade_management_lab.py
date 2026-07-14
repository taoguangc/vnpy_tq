# -*- coding: utf-8
"""EXP-009 — Trade Management Lab：同一 Entry cohort 上对比出场规则。"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from enum import Enum
from typing import Iterable

import numpy as np
import pandas as pd

from scripts.backtest_trade_analysis import RoundTripTrade, summarize_round_trips
from strategies.pa_cta.exit_families import (
    ExitFamily,
    ExitFamilyConfig,
    family_for_setup,
    get_exit_family_config,
    resolve_exit_family,
)


class ExitRule(str, Enum):
    ACTUAL = "ACTUAL"
    FIXED_1R = "FIXED_1R"
    FIXED_2R = "FIXED_2R"
    TIME_120 = "TIME_120"
    ATR_TRAIL = "ATR_TRAIL"
    STOP_EOD = "STOP_EOD"
    FAMILY_CONTINUATION = "FAMILY_CONTINUATION"
    FAMILY_REVERSAL = "FAMILY_REVERSAL"
    FAMILY_ASSIGNED = "FAMILY_ASSIGNED"


@dataclass
class CohortTrade:
    """一笔可重放的入场 cohort 记录。"""

    setup: str
    direction: str  # 多 / 空
    entry_time: datetime
    entry_price: float
    initial_stop: float
    initial_r_yuan: float
    volume: float
    actual_net_pnl: float
    actual_exit_reason: str = ""
    atr_5_price: float = 0.0


@dataclass
class SimResult:
    rule: ExitRule
    net_pnl: float
    gross_pnl: float
    exit_price: float
    exit_time: datetime | None
    exit_tag: str
    r_multiple: float
    holding_minutes: float
    setup: str = ""


@dataclass
class RuleSummary:
    rule: ExitRule
    n: int
    skipped: int
    net_pnl: float
    win_rate: float
    profit_factor: float
    avg_r: float
    avg_holding_min: float
    vs_actual_delta: float = 0.0


EOD_FLAT_START = time(14, 55)
EOD_FLAT_END = time(15, 0)
CHANDELIER_MULT = 2.5
ATR_WINDOW = 14


def _is_eod_flat(dt: pd.Timestamp) -> bool:
    t = dt.to_pydatetime().time()
    return EOD_FLAT_START <= t <= EOD_FLAT_END


def _trade_cost(price: float, volume: float, *, contract_size: float, rate: float, slippage: float) -> float:
    turnover = price * volume * contract_size
    return turnover * rate + volume * contract_size * slippage


def _net_pnl(
    *,
    direction: str,
    entry_price: float,
    exit_price: float,
    volume: float,
    contract_size: float,
    rate: float,
    slippage: float,
) -> tuple[float, float]:
    if direction == "多":
        gross = (exit_price - entry_price) * volume * contract_size
    else:
        gross = (entry_price - exit_price) * volume * contract_size
    cost = _trade_cost(entry_price, volume, contract_size=contract_size, rate=rate, slippage=slippage)
    cost += _trade_cost(exit_price, volume, contract_size=contract_size, rate=rate, slippage=slippage)
    return gross, gross - cost


def _compute_atr5_map(bars_1m: pd.DataFrame) -> pd.Series:
    """5m ATR(14) 对齐到每根 1m bar（ffill）。"""
    from research.event_engine.bars import resample_minutes

    bars_5 = resample_minutes(bars_1m, 5)
    if len(bars_5) < ATR_WINDOW + 2:
        return pd.Series(0.0, index=bars_1m.index)
    h = bars_5["high"].astype(float)
    l = bars_5["low"].astype(float)
    c = bars_5["close"].astype(float)
    prev_c = c.shift(1)
    tr = pd.concat([(h - l), (h - prev_c).abs(), (l - prev_c).abs()], axis=1).max(axis=1)
    atr5 = tr.rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean()
    atr5.index = bars_5["dt_cst"]
    work = bars_1m.copy()
    work["_atr5"] = work["dt_cst"].map(atr5.to_dict())
    work["_atr5"] = work["_atr5"].ffill().fillna(0.0)
    return work["_atr5"]


def build_cohort_from_backtest(
    round_trips: list[RoundTripTrade],
    trade_log: list[dict],
    *,
    bars_1m: pd.DataFrame | None = None,
    contract_size: float = 10.0,
) -> list[CohortTrade]:
    """trade_log 优先；缺失时从 round_trips 回填。"""
    atr_map: pd.Series | None = None
    bars_work = bars_1m.reset_index(drop=True) if bars_1m is not None and len(bars_1m) else None
    if bars_work is not None and len(bars_work) > 0:
        atr_map = _compute_atr5_map(bars_work)

    stop_loss_r: dict[str, list[float]] = {}
    for log in trade_log:
        if log.get("exit_reason") == "STOP_LOSS" and log.get("mae_ticks", 0) > 0:
            setup = log.get("setup") or "UNKNOWN"
            stop_loss_r.setdefault(setup, []).append(float(log["mae_ticks"]))
    for rt in round_trips:
        if rt.exit_reason == "STOP_LOSS" and rt.mae_ticks > 0:
            setup = rt.setup or "UNKNOWN"
            stop_loss_r.setdefault(setup, []).append(float(rt.mae_ticks))

    setup_median_r = {k: float(np.median(v)) for k, v in stop_loss_r.items() if v}

    cohort: list[CohortTrade] = []
    if trade_log:
        rt_by_key: dict[tuple, RoundTripTrade] = {}
        for rt in round_trips:
            rt_by_key[(rt.entry_time, rt.direction, rt.setup or "")] = rt

        for log in trade_log:
            setup = log.get("setup") or "UNKNOWN"
            direction = log.get("direction") or ""
            entry_time = log.get("entry_time")
            if entry_time is None:
                continue
            entry_price = float(log.get("entry_price") or 0.0)
            stop = float(log.get("initial_stop_loss") or 0.0)
            init_r = float(log.get("initial_r_yuan") or 0.0)
            if init_r <= 0 and stop > 0 and entry_price > 0:
                init_r = abs(entry_price - stop) * contract_size
            if init_r <= 0 and log.get("exit_reason") == "STOP_LOSS":
                init_r = float(log.get("mae_ticks") or 0.0)
            if init_r <= 0:
                init_r = setup_median_r.get(setup, 0.0)
            if init_r <= 0 or entry_price <= 0:
                continue

            key = (entry_time, direction, setup)
            rt = rt_by_key.get(key)
            if rt is None:
                for rt_cand in round_trips:
                    if rt_cand.direction != direction:
                        continue
                    if abs((rt_cand.entry_time - entry_time).total_seconds()) > 120:
                        continue
                    if rt_cand.setup and setup and rt_cand.setup != setup:
                        continue
                    rt = rt_cand
                    break
            actual_net = float(rt.net_pnl) if rt else float(log.get("gross_pnl") or 0.0)

            atr_5 = _atr_at_entry(bars_work, atr_map, entry_time)
            cohort.append(_make_cohort_trade(
                setup, direction, entry_time, entry_price, stop, init_r,
                float(log.get("volume") or 1.0), actual_net,
                log.get("exit_reason") or "", atr_5, contract_size,
            ))
        return cohort

    for rt in round_trips:
        setup = rt.setup or "UNKNOWN"
        init_r = float(rt.mae_ticks) if rt.exit_reason == "STOP_LOSS" and rt.mae_ticks > 0 else 0.0
        if init_r <= 0:
            init_r = setup_median_r.get(setup, 0.0)
        if init_r <= 0 and rt.mfe_ticks > 0:
            init_r = rt.mfe_ticks * 0.5
        if init_r <= 0 or rt.entry_price <= 0:
            continue
        stop = (
            rt.entry_price - init_r / contract_size if rt.direction == "多"
            else rt.entry_price + init_r / contract_size
        )
        atr_5 = _atr_at_entry(bars_work, atr_map, rt.entry_time)
        cohort.append(_make_cohort_trade(
            setup, rt.direction, rt.entry_time, rt.entry_price, stop, init_r,
            rt.volume, rt.net_pnl, rt.exit_reason or "", atr_5, contract_size,
        ))
    return cohort


def _to_cst_ts(dt: datetime) -> pd.Timestamp:
    ts = pd.Timestamp(dt)
    if ts.tzinfo is None:
        return ts.tz_localize("Asia/Shanghai")
    return ts.tz_convert("Asia/Shanghai")


def _atr_at_entry(
    bars_work: pd.DataFrame | None,
    atr_map: pd.Series | None,
    entry_time: datetime,
) -> float:
    if atr_map is None or bars_work is None or len(bars_work) == 0:
        return 0.0
    idx = bars_work["dt_cst"].searchsorted(_to_cst_ts(entry_time))
    idx = min(max(int(idx), 0), len(bars_work) - 1)
    return float(atr_map.iloc[idx])


def _make_cohort_trade(
    setup: str,
    direction: str,
    entry_time: datetime,
    entry_price: float,
    stop: float,
    init_r: float,
    volume: float,
    actual_net: float,
    exit_reason: str,
    atr_5: float,
    contract_size: float,
) -> CohortTrade:
    if stop <= 0 and init_r > 0:
        stop = (
            entry_price - init_r / contract_size if direction == "多"
            else entry_price + init_r / contract_size
        )
    return CohortTrade(
        setup=setup,
        direction=direction,
        entry_time=entry_time,
        entry_price=entry_price,
        initial_stop=stop,
        initial_r_yuan=init_r,
        volume=volume,
        actual_net_pnl=actual_net,
        actual_exit_reason=exit_reason,
        atr_5_price=atr_5,
    )


def _bar_slice(bars: pd.DataFrame, entry_time: datetime) -> pd.DataFrame:
    ts = _to_cst_ts(entry_time)
    idx = int(bars["dt_cst"].searchsorted(ts))
    if idx >= len(bars):
        return bars.iloc[0:0]
    return bars.iloc[idx:].reset_index(drop=True)


def _simulate_one(
    trade: CohortTrade,
    bars_slice: pd.DataFrame,
    rule: ExitRule,
    *,
    contract_size: float,
    rate: float,
    slippage: float,
) -> SimResult | None:
    if bars_slice.empty:
        return None

    ep = trade.entry_price
    stop = trade.initial_stop
    r_price = abs(ep - stop) if stop > 0 else trade.initial_r_yuan / contract_size
    if r_price <= 0:
        return None

    is_long = trade.direction == "多"
    vol = trade.volume
    entry_dt = _to_cst_ts(trade.entry_time)
    time_limit = entry_dt + timedelta(minutes=120)

    target_1 = ep + r_price if is_long else ep - r_price
    target_2 = ep + 2 * r_price if is_long else ep - 2 * r_price

    peak = ep
    trough = ep
    active_stop = stop
    atr_px = trade.atr_5_price if trade.atr_5_price > 0 else r_price

    for i, row in bars_slice.iterrows():
        dt = row["dt_cst"]
        if i == 0 and dt <= entry_dt:
            continue
        o, h, l, c = float(row["open"]), float(row["high"]), float(row["low"]), float(row["close"])

        if is_long:
            peak = max(peak, h)
        else:
            trough = min(trough, l)

        if rule == ExitRule.ATR_TRAIL:
            if is_long:
                trail = peak - CHANDELIER_MULT * atr_px
                active_stop = max(active_stop, trail)
            else:
                trail = trough + CHANDELIER_MULT * atr_px
                active_stop = min(active_stop, trail) if active_stop > 0 else trail

        # 止损优先（§2.1）
        if is_long and l <= active_stop:
            exit_px = min(o, active_stop)
            gross, net = _net_pnl(
                direction=trade.direction, entry_price=ep, exit_price=exit_px,
                volume=vol, contract_size=contract_size, rate=rate, slippage=slippage,
            )
            hold = (dt - entry_dt).total_seconds() / 60.0
            return SimResult(rule, net, gross, exit_px, dt.to_pydatetime(), "STOP", net / trade.initial_r_yuan, hold, trade.setup)

        if not is_long and h >= active_stop:
            exit_px = max(o, active_stop)
            gross, net = _net_pnl(
                direction=trade.direction, entry_price=ep, exit_price=exit_px,
                volume=vol, contract_size=contract_size, rate=rate, slippage=slippage,
            )
            hold = (dt - entry_dt).total_seconds() / 60.0
            return SimResult(rule, net, gross, exit_px, dt.to_pydatetime(), "STOP", net / trade.initial_r_yuan, hold, trade.setup)

        if rule in (ExitRule.FIXED_1R, ExitRule.FIXED_2R):
            tgt = target_1 if rule == ExitRule.FIXED_1R else target_2
            if is_long and h >= tgt:
                exit_px = max(o, tgt)
                gross, net = _net_pnl(
                    direction=trade.direction, entry_price=ep, exit_price=exit_px,
                    volume=vol, contract_size=contract_size, rate=rate, slippage=slippage,
                )
                hold = (dt - entry_dt).total_seconds() / 60.0
                tag = "TARGET_1R" if rule == ExitRule.FIXED_1R else "TARGET_2R"
                return SimResult(rule, net, gross, exit_px, dt.to_pydatetime(), tag, net / trade.initial_r_yuan, hold, trade.setup)
            if not is_long and l <= tgt:
                exit_px = min(o, tgt)
                gross, net = _net_pnl(
                    direction=trade.direction, entry_price=ep, exit_price=exit_px,
                    volume=vol, contract_size=contract_size, rate=rate, slippage=slippage,
                )
                hold = (dt - entry_dt).total_seconds() / 60.0
                tag = "TARGET_1R" if rule == ExitRule.FIXED_1R else "TARGET_2R"
                return SimResult(rule, net, gross, exit_px, dt.to_pydatetime(), tag, net / trade.initial_r_yuan, hold, trade.setup)

        if rule == ExitRule.TIME_120 and dt >= time_limit:
            exit_px = c
            gross, net = _net_pnl(
                direction=trade.direction, entry_price=ep, exit_price=exit_px,
                volume=vol, contract_size=contract_size, rate=rate, slippage=slippage,
            )
            hold = (dt - entry_dt).total_seconds() / 60.0
            return SimResult(rule, net, gross, exit_px, dt.to_pydatetime(), "TIME_120", net / trade.initial_r_yuan, hold, trade.setup)

        if _is_eod_flat(dt):
            exit_px = c
            gross, net = _net_pnl(
                direction=trade.direction, entry_price=ep, exit_price=exit_px,
                volume=vol, contract_size=contract_size, rate=rate, slippage=slippage,
            )
            hold = (dt - entry_dt).total_seconds() / 60.0
            return SimResult(rule, net, gross, exit_px, dt.to_pydatetime(), "EOD_FLAT", net / trade.initial_r_yuan, hold, trade.setup)

    last = bars_slice.iloc[-1]
    exit_px = float(last["close"])
    dt = last["dt_cst"]
    gross, net = _net_pnl(
        direction=trade.direction, entry_price=ep, exit_price=exit_px,
        volume=vol, contract_size=contract_size, rate=rate, slippage=slippage,
    )
    hold = (dt - entry_dt).total_seconds() / 60.0
    return SimResult(rule, net, gross, exit_px, dt.to_pydatetime(), "DATA_END", net / trade.initial_r_yuan, hold, trade.setup)


def _simulate_family(
    trade: CohortTrade,
    bars_slice: pd.DataFrame,
    config: ExitFamilyConfig,
    rule: ExitRule,
    *,
    contract_size: float,
    rate: float,
    slippage: float,
    tag_prefix: str,
) -> SimResult | None:
    """Phase-3 出场族重放（固定入场 cohort，只改出场路径）。"""
    if bars_slice.empty:
        return None

    ep = trade.entry_price
    stop = trade.initial_stop
    r_price = abs(ep - stop) if stop > 0 else trade.initial_r_yuan / contract_size
    if r_price <= 0:
        return None

    is_long = trade.direction == "多"
    vol_total = float(trade.volume)
    entry_dt = _to_cst_ts(trade.entry_time)
    time_limit = (
        entry_dt + timedelta(minutes=config.time_stop_minutes)
        if config.time_stop_minutes
        else None
    )
    target_1 = ep + r_price if is_long else ep - r_price
    atr_px = trade.atr_5_price if trade.atr_5_price > 0 else r_price

    peak = ep
    trough = ep
    active_stop = stop
    breakeven_locked = False
    partial_done = False
    rem_vol = vol_total
    total_net = 0.0
    total_gross = 0.0
    last_exit_px = ep
    last_exit_dt: datetime | None = None
    last_tag = tag_prefix

    def _close_fraction(exit_px: float, dt: pd.Timestamp, close_vol: float, tag: str) -> bool:
        nonlocal rem_vol, total_net, total_gross, last_exit_px, last_exit_dt, last_tag
        if close_vol <= 0 or rem_vol <= 0:
            return False
        close_vol = min(close_vol, rem_vol)
        gross, net = _net_pnl(
            direction=trade.direction,
            entry_price=ep,
            exit_price=exit_px,
            volume=close_vol,
            contract_size=contract_size,
            rate=rate,
            slippage=slippage,
        )
        total_gross += gross
        total_net += net
        rem_vol -= close_vol
        last_exit_px = exit_px
        last_exit_dt = dt.to_pydatetime()
        last_tag = tag
        return rem_vol <= 0

    for i, row in bars_slice.iterrows():
        dt = row["dt_cst"]
        if i == 0 and dt <= entry_dt:
            continue
        o, h, l, c = float(row["open"]), float(row["high"]), float(row["low"]), float(row["close"])

        if is_long:
            peak = max(peak, h)
            floating = c - ep
        else:
            trough = min(trough, l)
            floating = ep - c

        if not breakeven_locked and floating > config.breakeven_atr_mult * atr_px:
            active_stop = ep
            breakeven_locked = True

        if config.enable_chandelier_trail and floating > config.chandelier_active_atr_mult * atr_px:
            if is_long:
                trail = peak - CHANDELIER_MULT * atr_px
                active_stop = max(active_stop, trail)
            else:
                trail = trough + CHANDELIER_MULT * atr_px
                active_stop = min(active_stop, trail) if active_stop > 0 else trail

        if is_long and l <= active_stop:
            exit_px = min(o, active_stop)
            if _close_fraction(exit_px, dt, rem_vol, f"{tag_prefix}_STOP"):
                break
            continue
        if not is_long and h >= active_stop:
            exit_px = max(o, active_stop)
            if _close_fraction(exit_px, dt, rem_vol, f"{tag_prefix}_STOP"):
                break
            continue

        if config.partial_at_1r_fraction > 0 and not partial_done and config.enable_mm_half:
            hit_1r = (is_long and h >= target_1) or (not is_long and l <= target_1)
            if hit_1r:
                exit_px = max(o, target_1) if is_long else min(o, target_1)
                close_vol = max(1.0, round(vol_total * config.partial_at_1r_fraction))
                if _close_fraction(exit_px, dt, close_vol, f"{tag_prefix}_PARTIAL_1R"):
                    break
                partial_done = True

        if time_limit is not None and dt >= time_limit and rem_vol > 0:
            if _close_fraction(c, dt, rem_vol, f"{tag_prefix}_TIME"):
                break
            continue

        if _is_eod_flat(dt) and rem_vol > 0:
            if _close_fraction(c, dt, rem_vol, f"{tag_prefix}_EOD"):
                break
            continue

    if rem_vol > 0:
        last = bars_slice.iloc[-1]
        _close_fraction(float(last["close"]), last["dt_cst"], rem_vol, f"{tag_prefix}_DATA_END")

    if last_exit_dt is None:
        return None
    hold = (last_exit_dt - entry_dt).total_seconds() / 60.0
    r_mult = total_net / trade.initial_r_yuan if trade.initial_r_yuan > 0 else 0.0
    return SimResult(
        rule,
        total_net,
        total_gross,
        last_exit_px,
        last_exit_dt,
        last_tag,
        r_mult,
        hold,
        trade.setup,
    )


def run_management_lab(
    cohort: list[CohortTrade],
    bars_1m: pd.DataFrame,
    *,
    contract_size: float,
    rate: float,
    slippage: float,
    rules: Iterable[ExitRule] | None = None,
) -> tuple[dict[ExitRule, list[SimResult]], list[RuleSummary]]:
    """对 cohort 批量模拟各出场规则。"""
    rules = list(rules or [
        ExitRule.ACTUAL,
        ExitRule.FIXED_1R,
        ExitRule.FIXED_2R,
        ExitRule.TIME_120,
        ExitRule.ATR_TRAIL,
        ExitRule.STOP_EOD,
    ])
    bars = bars_1m.sort_values("dt_cst").reset_index(drop=True)
    results: dict[ExitRule, list[SimResult]] = {r: [] for r in rules}
    skipped = {r: 0 for r in rules}

    for trade in cohort:
        if ExitRule.ACTUAL in rules:
            r_mult = trade.actual_net_pnl / trade.initial_r_yuan if trade.initial_r_yuan > 0 else 0.0
            results[ExitRule.ACTUAL].append(
                SimResult(
                    ExitRule.ACTUAL,
                    trade.actual_net_pnl,
                    trade.actual_net_pnl,
                    0.0,
                    None,
                    trade.actual_exit_reason or "ACTUAL",
                    r_mult,
                    0.0,
                    trade.setup,
                )
            )

        slice_df = _bar_slice(bars, trade.entry_time)
        for rule in rules:
            if rule == ExitRule.ACTUAL:
                continue
            if rule == ExitRule.FAMILY_CONTINUATION:
                sim = _simulate_family(
                    trade, slice_df, get_exit_family_config(ExitFamily.CONTINUATION), rule,
                    contract_size=contract_size, rate=rate, slippage=slippage,
                    tag_prefix="F_CONT",
                )
            elif rule == ExitRule.FAMILY_REVERSAL:
                sim = _simulate_family(
                    trade, slice_df, get_exit_family_config(ExitFamily.REVERSAL), rule,
                    contract_size=contract_size, rate=rate, slippage=slippage,
                    tag_prefix="F_REV",
                )
            elif rule == ExitRule.FAMILY_ASSIGNED:
                fam, cfg = family_for_setup(trade.setup)
                sim = _simulate_family(
                    trade, slice_df, cfg, rule,
                    contract_size=contract_size, rate=rate, slippage=slippage,
                    tag_prefix=f"F_{fam.value[:4]}",
                )
            else:
                sim_rule = ExitRule.STOP_EOD if rule == ExitRule.STOP_EOD else rule
                sim = _simulate_one(
                    trade, slice_df, sim_rule,
                    contract_size=contract_size, rate=rate, slippage=slippage,
                )
                if sim is not None:
                    sim = SimResult(
                        rule,
                        sim.net_pnl,
                        sim.gross_pnl,
                        sim.exit_price,
                        sim.exit_time,
                        sim.exit_tag,
                        sim.r_multiple,
                        sim.holding_minutes,
                        sim.setup,
                    )
            if sim is None:
                skipped[rule] += 1
            else:
                results[rule].append(sim)

    actual_net = sum(t.actual_net_pnl for t in cohort)
    summaries: list[RuleSummary] = []
    for rule in rules:
        sims = results[rule]
        if not sims:
            summaries.append(RuleSummary(rule, 0, skipped.get(rule, 0), 0.0, 0.0, 0.0, 0.0, 0.0, -actual_net))
            continue
        nets = [s.net_pnl for s in sims]
        wins = [n for n in nets if n > 0]
        losses = [n for n in nets if n < 0]
        gp = sum(wins)
        gl = abs(sum(losses))
        pf = gp / gl if gl > 0 else (999.0 if gp > 0 else 0.0)
        rs = [s.r_multiple for s in sims if s.r_multiple != 0]
        summaries.append(
            RuleSummary(
                rule=rule,
                n=len(sims),
                skipped=skipped.get(rule, 0),
                net_pnl=sum(nets),
                win_rate=len(wins) / len(sims) * 100.0,
                profit_factor=pf,
                avg_r=float(np.mean(rs)) if rs else 0.0,
                avg_holding_min=float(np.mean([s.holding_minutes for s in sims if s.holding_minutes > 0])) if sims else 0.0,
                vs_actual_delta=sum(nets) - actual_net,
            )
        )
    return results, summaries


def pf_from_net_pnls(nets: list[float]) -> float:
    wins = [n for n in nets if n > 0]
    losses = [n for n in nets if n < 0]
    gp = sum(wins)
    gl = abs(sum(losses))
    return gp / gl if gl > 0 else (999.0 if gp > 0 else 0.0)


def summarize_by_setup(
    sim_results: dict[ExitRule, list[SimResult]],
) -> pd.DataFrame:
    """按 setup × rule 汇总 net / PF。"""
    rows = []
    for rule, sims in sim_results.items():
        by_setup: dict[str, list[float]] = {}
        for s in sims:
            by_setup.setdefault(s.setup or "UNKNOWN", []).append(s.net_pnl)
        for setup, nets in sorted(by_setup.items()):
            rows.append({
                "setup": setup,
                "rule": rule.value,
                "n": len(nets),
                "net_pnl": sum(nets),
                "pf": pf_from_net_pnls(nets),
            })
    return pd.DataFrame(rows)


def format_summary_table(summaries: list[RuleSummary]) -> str:
    lines = [
        "| Rule | n | WR | PF | Net PnL | avg R | Δ vs ACTUAL |",
        "|------|---|-----|-----|---------|-------|-------------|",
    ]
    for s in summaries:
        lines.append(
            f"| {s.rule.value} | {s.n} | {s.win_rate:.1f}% | {s.profit_factor:.2f} | "
            f"{s.net_pnl:+,.0f} | {s.avg_r:+.2f} | {s.vs_actual_delta:+,.0f} |"
        )
    return "\n".join(lines)
