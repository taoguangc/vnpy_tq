# -*- coding: utf-8 -*-
"""背景门禁前的 signal candidate 账本（固定 cohort / alpha shadow 对照用）。"""
from __future__ import annotations

import csv
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class SignalCandidate:
    time: datetime | None
    setup: str
    direction: int
    trigger: float
    stop: float
    arm_mode: str
    market_context: str = ""
    always_in: str = ""
    aff_alpha: float = 0.0
    # 15m 快/慢连续因子（只读记账；默认不参与拒单）
    ctx_trend_quality: float = 0.0
    ctx_vol_abnormality: float = 0.0
    ctx_opp08_fit: float = 0.5
    ctx_opp16_fit: float = 0.5
    fast_trend_r2: float = 0.0
    slow_trend_r2: float = 0.0
    slow_er: float = 0.0
    gate_pass: bool = False
    first_block: str = ""
    armed: bool = False
    disposition: str = "CANDIDATE"
    # --- alpha discovery 扩展字段 ---
    symbol: str = ""
    entry_price: float = 0.0
    structural_stop: float = 0.0
    initial_r_yuan: float = 0.0
    vwap_regime: str = ""
    session: str = ""
    env_block: str = ""
    preempted_by: str = ""
    gate_before: bool = False
    # forward 经济边际（1 手，保守成本后）
    mfe_yuan: float = 0.0
    mae_yuan: float = 0.0
    hit_1r: bool = False
    hit_2r: bool = False
    first_hit_1r_bars: int = -1
    first_hit_2r_bars: int = -1
    fwd_10m_gross: float = 0.0
    fwd_20m_gross: float = 0.0
    fwd_40m_gross: float = 0.0
    fwd_80m_gross: float = 0.0
    fwd_10m_net: float = 0.0
    fwd_20m_net: float = 0.0
    fwd_40m_net: float = 0.0
    fwd_80m_net: float = 0.0
    fwd_10m_net_r: float = 0.0
    fwd_20m_net_r: float = 0.0
    fwd_40m_net_r: float = 0.0
    fwd_80m_net_r: float = 0.0
    commission_yuan: float = 0.0
    slippage_yuan: float = 0.0
    cost_cover_40m: float = 0.0


@dataclass
class CandidateLedger:
    symbol: str
    records: list[SignalCandidate] = field(default_factory=list)

    def add(self, cand: SignalCandidate) -> None:
        if not cand.symbol:
            cand.symbol = self.symbol
        if cand.structural_stop == 0.0:
            cand.structural_stop = float(cand.stop)
        if cand.entry_price == 0.0:
            cand.entry_price = float(cand.trigger)
        self.records.append(cand)

    def to_rows(self) -> list[dict[str, Any]]:
        rows = []
        for r in self.records:
            d = asdict(r)
            if d.get("time") is not None:
                d["time"] = str(d["time"])
            rows.append(d)
        return rows

    def funnel(self) -> dict[str, Any]:
        total = len(self.records)
        by_setup: dict[str, int] = {}
        passed = 0
        armed = 0
        blocks: dict[str, int] = {}
        for r in self.records:
            by_setup[r.setup] = by_setup.get(r.setup, 0) + 1
            if r.gate_pass:
                passed += 1
            if r.armed:
                armed += 1
            if r.first_block:
                blocks[r.first_block] = blocks.get(r.first_block, 0) + 1
        return {
            "candidates": total,
            "gate_pass": passed,
            "armed": armed,
            "by_setup": by_setup,
            "blocks": blocks,
        }

    def attach_forwards(
        self,
        bars_1m: list,
        *,
        contract_size: float,
        pricetick: float,
        rate: float,
        slippage_ticks: float,
        horizons: tuple[int, ...] = (10, 20, 40, 80),
    ) -> None:
        """按 1m 路径附加 MFE/MAE、触及 1R/2R、固定时间退出净盈亏（1 手）。"""
        if not self.records or not bars_1m:
            return
        times = [b.datetime for b in bars_1m]
        highs = np.array([b.high_price for b in bars_1m], dtype=float)
        lows = np.array([b.low_price for b in bars_1m], dtype=float)
        closes = np.array([b.close_price for b in bars_1m], dtype=float)
        n = len(times)
        slip_1way = float(slippage_ticks) * float(pricetick) * float(contract_size)
        round_slip = slip_1way * 2.0
        max_h = max(horizons)

        for rec in self.records:
            if rec.time is None:
                continue
            idx = int(np.searchsorted(times, rec.time, side="right"))
            if idx >= n:
                continue
            entry = float(rec.entry_price or rec.trigger)
            stop = float(rec.structural_stop or rec.stop)
            direction = int(rec.direction)
            r_yuan = abs(entry - stop) * float(contract_size)
            if r_yuan <= 0:
                r_yuan = float(pricetick) * float(contract_size)
            rec.initial_r_yuan = r_yuan
            rec.slippage_yuan = round_slip

            end = min(n, idx + max_h + 1)
            if end <= idx:
                continue
            seg_hi = highs[idx:end]
            seg_lo = lows[idx:end]
            if direction > 0:
                mfe_px = float(np.max(seg_hi) - entry) if len(seg_hi) else 0.0
                mae_px = float(entry - np.min(seg_lo)) if len(seg_lo) else 0.0
                hit1 = hit2 = -1
                for k in range(len(seg_hi)):
                    fav = float(seg_hi[k] - entry) * contract_size
                    if hit1 < 0 and fav >= r_yuan:
                        hit1 = k + 1
                    if hit2 < 0 and fav >= 2.0 * r_yuan:
                        hit2 = k + 1
                        break
            else:
                mfe_px = float(entry - np.min(seg_lo)) if len(seg_lo) else 0.0
                mae_px = float(np.max(seg_hi) - entry) if len(seg_hi) else 0.0
                hit1 = hit2 = -1
                for k in range(len(seg_lo)):
                    fav = float(entry - seg_lo[k]) * contract_size
                    if hit1 < 0 and fav >= r_yuan:
                        hit1 = k + 1
                    if hit2 < 0 and fav >= 2.0 * r_yuan:
                        hit2 = k + 1
                        break

            rec.mfe_yuan = mfe_px * float(contract_size)
            rec.mae_yuan = mae_px * float(contract_size)
            rec.hit_1r = hit1 > 0
            rec.hit_2r = hit2 > 0
            rec.first_hit_1r_bars = hit1
            rec.first_hit_2r_bars = hit2

            def _fwd(minutes: int) -> tuple[float, float, float]:
                j = min(n - 1, idx + minutes - 1)
                px = float(closes[j])
                gross = direction * (px - entry) * float(contract_size)
                comm = float(rate) * (entry + px) * float(contract_size)
                net = gross - round_slip - comm
                return gross, net, comm

            g10, n10, c10 = _fwd(10)
            g20, n20, c20 = _fwd(20)
            g40, n40, c40 = _fwd(40)
            g80, n80, c80 = _fwd(80)
            rec.fwd_10m_gross, rec.fwd_10m_net = g10, n10
            rec.fwd_20m_gross, rec.fwd_20m_net = g20, n20
            rec.fwd_40m_gross, rec.fwd_40m_net = g40, n40
            rec.fwd_80m_gross, rec.fwd_80m_net = g80, n80
            rec.commission_yuan = c40
            rec.fwd_10m_net_r = n10 / r_yuan if r_yuan > 0 else 0.0
            rec.fwd_20m_net_r = n20 / r_yuan if r_yuan > 0 else 0.0
            rec.fwd_40m_net_r = n40 / r_yuan if r_yuan > 0 else 0.0
            rec.fwd_80m_net_r = n80 / r_yuan if r_yuan > 0 else 0.0
            cost40 = round_slip + c40
            rec.cost_cover_40m = (g40 / cost40) if cost40 > 0 else 0.0

    def export_csv(self, path: Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        rows = self.to_rows()
        if not rows:
            path.write_text("", encoding="utf-8")
            return path
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        return path
