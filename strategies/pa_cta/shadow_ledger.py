# -*- coding: utf-8 -*-
"""Production OPP 影子账本 — Phase 2 分解：信号期望 → gate → arbitration → exit → sizing。"""
from __future__ import annotations

import csv
from dataclasses import asdict, dataclass, field
from datetime import datetime, time
from pathlib import Path
from typing import Any

import numpy as np

GATE_NAMES: tuple[str, ...] = (
    "setup_disabled",
    "aff_archetype",
    "late_phase",
    "context_layer",
    "aff_filter",
    "dual_core",
    "vsa",
    "tf_arm",
    "opp13_volume",
)

GLOBAL_SKIP_REASONS: tuple[str, ...] = (
    "ENTRY_WINDOW_CLOSED",
    "ATR_TOO_LOW",
    "HAS_POSITION",
    "REGIME_DISALLOW",
    "MAX_DAILY_TRADES",
    "STATE_MACHINE_BUSY",
)


@dataclass
class ShadowCandidate:
    """单条 production OPP 候选（含未成交）。"""

    candidate_id: int
    symbol: str
    signal_time: datetime
    setup: str
    direction: int  # +1 long / -1 short
    entry_price: float
    structural_stop: float
    initial_r_yuan: float
    trigger_price: float = 0.0
    arm_mode: str = ""
    market_context_5m: str = ""
    always_in: str = ""
    trend_phase: str = ""
    atr_ratio_5m_15m: float = 0.0
    aff_alpha: float = 0.0
    aff_archetype: str = ""
    vwap_regime: str = ""
    entry_lane: str = ""
    pos_at_signal: int = 0
    machine_state_at_signal: str = ""
    gates: dict[str, bool] = field(default_factory=dict)
    first_blocking_gate: str = ""
    disposition: str = ""  # ARMED | GATE_BLOCKED | PREEMPTED | POS_SKIP | GLOBAL_SKIP | TRADED
    preempted_by: str = ""
    global_skip_reason: str = ""
    source: str = "ARM"  # ARM | DRY_SCAN
    traded: bool = False
    trade_time: datetime | None = None
    # forwards (filled post-run)
    mfe_yuan: float = 0.0
    mae_yuan: float = 0.0
    hit_1r: bool = False
    hit_2r: bool = False
    fwd_60m_yuan: float = 0.0
    fwd_120m_yuan: float = 0.0
    eod_yuan_gross: float = 0.0
    eod_yuan_net: float = 0.0
    net_at_1r: float = 0.0
    net_at_2r: float = 0.0

    def to_row(self) -> dict[str, Any]:
        row = {
            "candidate_id": self.candidate_id,
            "symbol": self.symbol,
            "signal_time": self.signal_time,
            "setup": self.setup,
            "direction": self.direction,
            "entry_price": round(self.entry_price, 4),
            "structural_stop": round(self.structural_stop, 4),
            "initial_r_yuan": round(self.initial_r_yuan, 2),
            "trigger_price": round(self.trigger_price, 4),
            "arm_mode": self.arm_mode,
            "market_context_5m": self.market_context_5m,
            "always_in": self.always_in,
            "trend_phase": self.trend_phase,
            "atr_ratio_5m_15m": round(self.atr_ratio_5m_15m, 4),
            "aff_alpha": round(self.aff_alpha, 4),
            "aff_archetype": self.aff_archetype,
            "vwap_regime": self.vwap_regime,
            "entry_lane": self.entry_lane,
            "pos_at_signal": self.pos_at_signal,
            "machine_state_at_signal": self.machine_state_at_signal,
            "first_blocking_gate": self.first_blocking_gate,
            "disposition": self.disposition,
            "preempted_by": self.preempted_by,
            "global_skip_reason": self.global_skip_reason,
            "source": self.source,
            "traded": int(self.traded),
            "trade_time": self.trade_time or "",
            "mfe_yuan": round(self.mfe_yuan, 2),
            "mae_yuan": round(self.mae_yuan, 2),
            "hit_1r": int(self.hit_1r),
            "hit_2r": int(self.hit_2r),
            "fwd_60m_yuan": round(self.fwd_60m_yuan, 2),
            "fwd_120m_yuan": round(self.fwd_120m_yuan, 2),
            "eod_yuan_gross": round(self.eod_yuan_gross, 2),
            "eod_yuan_net": round(self.eod_yuan_net, 2),
            "net_at_1r": round(self.net_at_1r, 2),
            "net_at_2r": round(self.net_at_2r, 2),
        }
        for g in GATE_NAMES:
            val = self.gates.get(g)
            row[f"gate_{g}"] = "" if val is None else int(bool(val))
        return row


class ShadowLedger:
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self._next_id = 1
        self.records: list[ShadowCandidate] = []
        self._bar_winners: dict[datetime, str] = {}

    def reset_bar(self, bar_time: datetime) -> None:
        self._bar_winners.pop(bar_time, None)

    def bar_winner(self, bar_time: datetime) -> str:
        return self._bar_winners.get(bar_time, "")

    def set_bar_winner(self, bar_time: datetime, setup: str) -> None:
        if bar_time not in self._bar_winners:
            self._bar_winners[bar_time] = setup

    def has_setup_at(self, bar_time: datetime, setup: str) -> bool:
        for rec in self.records:
            if rec.signal_time == bar_time and rec.setup == setup:
                return True
        return False

    def add(self, rec: ShadowCandidate) -> None:
        self.records.append(rec)

    def mark_traded(self, setup: str, trade_time: datetime) -> None:
        for rec in reversed(self.records):
            if rec.setup == setup and not rec.traded and rec.disposition == "ARMED":
                rec.traded = True
                rec.trade_time = trade_time
                rec.disposition = "TRADED"
                return

    def attach_forwards(
        self,
        bars_1m: list,
        *,
        contract_size: float,
        pricetick: float,
        rate: float,
        slippage_ticks: float,
        mfe_window: int = 120,
    ) -> None:
        if not self.records or not bars_1m:
            return
        times = [b.datetime for b in bars_1m]
        highs = np.array([b.high_price for b in bars_1m], dtype=float)
        lows = np.array([b.low_price for b in bars_1m], dtype=float)
        closes = np.array([b.close_price for b in bars_1m], dtype=float)
        n = len(times)

        slip_cost = slippage_ticks * pricetick * contract_size
        round_cost = slip_cost * 2.0

        for rec in self.records:
            idx = int(np.searchsorted(times, rec.signal_time, side="right"))
            if idx >= n:
                continue
            entry = float(rec.entry_price)
            direction = int(rec.direction)
            r_yuan = float(rec.initial_r_yuan)
            if r_yuan <= 0:
                r_yuan = abs(entry - rec.structural_stop) * contract_size
            end = min(n, idx + max(mfe_window, 120) + 1)
            if end <= idx:
                continue
            seg_hi = highs[idx:end]
            seg_lo = lows[idx:end]
            if direction > 0:
                mfe_px = float(np.max(seg_hi) - entry) if len(seg_hi) else 0.0
                mae_px = float(entry - np.min(seg_lo)) if len(seg_lo) else 0.0
            else:
                mfe_px = float(entry - np.min(seg_lo)) if len(seg_lo) else 0.0
                mae_px = float(np.max(seg_hi) - entry) if len(seg_hi) else 0.0
            rec.mfe_yuan = mfe_px * contract_size
            rec.mae_yuan = mae_px * contract_size
            rec.hit_1r = rec.mfe_yuan >= r_yuan if r_yuan > 0 else False
            rec.hit_2r = rec.mfe_yuan >= 2.0 * r_yuan if r_yuan > 0 else False

            def _fwd(minutes: int) -> float:
                j = min(n - 1, idx + minutes - 1)
                px = float(closes[j])
                gross = direction * (px - entry) * contract_size
                comm = rate * (entry + px) * contract_size
                return gross - round_cost - comm

            rec.fwd_60m_yuan = _fwd(60)
            rec.fwd_120m_yuan = _fwd(120)
            rec.net_at_1r = r_yuan - round_cost - rate * entry * contract_size * 2 if rec.hit_1r else 0.0
            rec.net_at_2r = 2.0 * r_yuan - round_cost - rate * entry * contract_size * 2 if rec.hit_2r else 0.0

            eod_idx = _eod_bar_index(times, idx, rec.signal_time.date())
            if eod_idx is not None:
                eod_px = float(closes[eod_idx])
                gross = direction * (eod_px - entry) * contract_size
                comm = rate * (entry + eod_px) * contract_size
                rec.eod_yuan_gross = gross
                rec.eod_yuan_net = gross - round_cost - comm

    def export_csv(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        rows = [r.to_row() for r in self.records]
        if not rows:
            path.write_text("", encoding="utf-8")
            return path
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        return path


def _eod_bar_index(times: list[datetime], start_idx: int, session_date) -> int | None:
    """同日 14:55–15:00 最后一根 1m bar。"""
    best = None
    for i in range(start_idx, len(times)):
        dt = times[i]
        if dt.date() != session_date:
            break
        t = dt.time()
        if time(14, 55) <= t <= time(15, 0):
            best = i
    return best


def evaluate_production_gates(
    strategy,
    opportunity: str,
    direction: int,
    *,
    bar=None,
    include_opp13_volume: bool = False,
) -> tuple[dict[str, bool | None], str | None]:
    """只读评估 production gate 链（与 _arm_* 顺序一致）。"""
    gates: dict[str, bool | None] = {g: None for g in GATE_NAMES}
    lane = strategy._setup_entry_lane(opportunity)

    if include_opp13_volume:
        if bar is None:
            gates["opp13_volume"] = None
        else:
            blocked = not strategy._opp13_volume_allows_entry(bar, direction)
            gates["opp13_volume"] = not blocked
            if blocked:
                return gates, "opp13_volume"

    blocked = strategy._setup_disabled(opportunity)
    gates["setup_disabled"] = not blocked
    if blocked:
        return gates, "setup_disabled"

    blocked = strategy._aff_archetype_blocks_entry(opportunity)
    gates["aff_archetype"] = not blocked
    if blocked:
        return gates, "aff_archetype"

    blocked = strategy._late_phase_blocks_entry(
        direction, strategy.market_context, opportunity)
    gates["late_phase"] = not blocked
    if blocked:
        return gates, "late_phase"

    blocked = strategy._context_layer_blocks_entry(direction, opportunity)
    gates["context_layer"] = not blocked
    if blocked:
        return gates, "context_layer"

    blocked = strategy._aff_blocks_entry()
    gates["aff_filter"] = not blocked
    if blocked:
        return gates, "aff_filter"

    blocked = not strategy._dual_core_allows_entry(direction, lane)
    gates["dual_core"] = not blocked
    if blocked:
        return gates, "dual_core"

    blocked = strategy._vsa_blocks_entry(direction, bar=bar)
    gates["vsa"] = not blocked
    if blocked:
        return gates, "vsa"

    blocked = not strategy._opp_tf_arm_gate(direction, opportunity)
    gates["tf_arm"] = not blocked
    if blocked:
        return gates, "tf_arm"

    return gates, None


def evaluate_opp15_direct_gates(
    strategy,
    opportunity: str,
    direction: int,
) -> tuple[dict[str, bool | None], str | None]:
    """OPP15 B' 直进路径（仅 setup / dual_core / aff，与 production 一致）。"""
    gates: dict[str, bool | None] = {g: None for g in GATE_NAMES}
    blocked = strategy._setup_disabled(opportunity)
    gates["setup_disabled"] = not blocked
    if blocked:
        return gates, "setup_disabled"
    lane = strategy._setup_entry_lane(opportunity)
    blocked = not strategy._dual_core_allows_entry(direction, lane)
    gates["dual_core"] = not blocked
    if blocked:
        return gates, "dual_core"
    blocked = strategy._aff_blocks_entry()
    gates["aff_filter"] = not blocked
    if blocked:
        return gates, "aff_filter"
    return gates, None


def build_candidate_from_strategy(
    ledger: ShadowLedger,
    strategy,
    *,
    bar,
    opportunity: str,
    direction: int,
    entry_price: float,
    stop: float,
    trigger: float,
    arm_mode: str,
    gates: dict[str, bool | None],
    first_block: str | None,
    disposition: str,
    preempted_by: str = "",
    global_skip_reason: str = "",
    source: str = "ARM",
) -> ShadowCandidate:
    contract_size = float(strategy.contract_size)
    init_r = abs(entry_price - stop) * contract_size if stop > 0 else 0.0
    atr_5 = float(strategy.am_5min.atr(strategy.atr_window)) if strategy.am_5min.inited else 0.0
    atr_15 = float(strategy.am_15min.atr(strategy.atr_window)) if strategy.am_15min.inited else 0.0
    atr_ratio = round(atr_5 / atr_15, 4) if atr_15 > 0 and atr_5 > 0 else 0.0
    rec = ShadowCandidate(
        candidate_id=ledger._next_id,
        symbol=ledger.symbol,
        signal_time=bar.datetime,
        setup=opportunity,
        direction=int(direction),
        entry_price=float(entry_price),
        structural_stop=float(stop),
        initial_r_yuan=round(init_r, 2),
        trigger_price=float(trigger),
        arm_mode=arm_mode,
        market_context_5m=strategy.market_context,
        always_in=strategy.always_in,
        trend_phase=strategy.trend_phase,
        atr_ratio_5m_15m=atr_ratio,
        aff_alpha=float(getattr(strategy, "_aff_alpha_strength", 0.0)),
        aff_archetype=str(getattr(strategy, "_aff_archetype", "")),
        vwap_regime=strategy.vwap_regime,
        entry_lane=strategy._setup_entry_lane(opportunity),
        pos_at_signal=int(strategy.pos),
        machine_state_at_signal=strategy.machine_state,
        gates={k: v for k, v in gates.items() if v is not None},
        first_blocking_gate=first_block or "",
        disposition=disposition,
        preempted_by=preempted_by,
        global_skip_reason=global_skip_reason,
        source=source,
    )
    ledger._next_id += 1
    return rec
