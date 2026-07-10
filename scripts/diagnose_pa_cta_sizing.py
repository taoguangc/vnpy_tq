# -*- coding: utf-8 -*-
"""pa_cta 定仓乘子诊断：setup_risk_mult / aff_mult / atr_ratio sizing 与 OPP 盈亏。"""
from __future__ import annotations

import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from strategies.pa_cta.backtest import run_tq_cbc_backtest
from strategies.pa_cta.rollover_strategy import BrooksPaCtaRolloverStrategy


@dataclass
class SizingEvent:
    setup: str
    entry_time: datetime
    volume: int
    risk_span: float
    setup_mult: float
    aff_mult: float
    aff_alpha: float
    atr_ratio: float
    sizing_factor: float
    combined_mult: float


class SizingDiagRolloverStrategy(BrooksPaCtaRolloverStrategy):
    """回测时记录每次成功定仓的乘子快照。"""

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting) -> None:
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.sizing_events: list[SizingEvent] = []

    def _snapshot_sizing(self, atr_5: float | None) -> dict:
        atr_5_rt = float(self.am_5min.atr(self.atr_window)) if self.am_5min.inited else 0.0
        atr_15_rt = float(self.am_15min.atr(self.atr_window)) if self.am_15min.inited else 0.0
        atr_ratio = (
            round(atr_5_rt / atr_15_rt, 3) if atr_15_rt > 0 and atr_5_rt > 0 else 0.0
        )
        if self.atr_regime_min <= atr_ratio < 0.70:
            sizing_factor = 1.5
        elif 0.70 <= atr_ratio < self.atr_regime_max:
            sizing_factor = 1.0
        else:
            sizing_factor = 0.0
        setup_mult = self._get_setup_risk_mult()
        aff_mult = self._get_aff_risk_mult()
        return {
            "setup": self.active_setup_name or "",
            "setup_mult": setup_mult,
            "aff_mult": aff_mult,
            "aff_alpha": float(self._aff_alpha_strength),
            "atr_ratio": atr_ratio,
            "sizing_factor": sizing_factor,
            "combined_mult": setup_mult * aff_mult * sizing_factor,
        }

    def _calc_brooks_volume(
        self,
        high_price: float,
        low_price: float,
        *,
        atr_5=None,
        max_position_cap=None,
    ) -> int:
        snap = self._snapshot_sizing(atr_5)
        volume = super()._calc_brooks_volume(
            high_price,
            low_price,
            atr_5=atr_5,
            max_position_cap=max_position_cap,
        )
        if volume > 0:
            dt = getattr(self.cta_engine, "datetime", None)
            self.sizing_events.append(
                SizingEvent(
                    setup=snap["setup"],
                    entry_time=dt or datetime.min,
                    volume=volume,
                    risk_span=abs(high_price - low_price),
                    setup_mult=snap["setup_mult"],
                    aff_mult=snap["aff_mult"],
                    aff_alpha=snap["aff_alpha"],
                    atr_ratio=snap["atr_ratio"],
                    sizing_factor=snap["sizing_factor"],
                    combined_mult=snap["combined_mult"],
                )
            )
        return volume


def _match_event(
    events: list[SizingEvent],
    setup: str,
    entry_time: datetime,
) -> SizingEvent | None:
    best: SizingEvent | None = None
    best_delta: float | None = None
    for ev in events:
        if ev.setup != setup:
            continue
        delta = abs((ev.entry_time - entry_time).total_seconds())
        if best_delta is None or delta < best_delta:
            best_delta = delta
            best = ev
    if best is not None and best_delta is not None and best_delta <= 600:
        return best
    return None


def run_diag(symbol: str = "rb") -> None:
    from strategies.pa_cta import backtest as bt_mod

    orig_run = bt_mod._run_engine_backtest
    events_holder: list[SizingEvent] = []

    def _wrapped_run(engine, **kw):
        out = orig_run(engine, **kw)
        strat = engine.strategy
        if hasattr(strat, "sizing_events"):
            events_holder.extend(strat.sizing_events)
        return out

    result = run_tq_cbc_backtest(
        symbol=symbol,
        verbose=False,
        rollover_strategy_class=SizingDiagRolloverStrategy,
        run_engine_backtest_fn=_wrapped_run,
    )
    events = events_holder
    round_trips = result["round_trips"]

    rows: list[dict] = []
    for rt in round_trips:
        setup = rt.setup or "UNKNOWN"
        ev = _match_event(events, setup, rt.entry_time)
        rows.append(
            {
                "setup": setup,
                "net_pnl": rt.net_pnl,
                "volume": ev.volume if ev else 0,
                "setup_mult": ev.setup_mult if ev else None,
                "aff_mult": ev.aff_mult if ev else None,
                "aff_alpha": ev.aff_alpha if ev else None,
                "atr_ratio": ev.atr_ratio if ev else None,
                "sizing_factor": ev.sizing_factor if ev else None,
                "combined_mult": ev.combined_mult if ev else None,
                "risk_span": ev.risk_span if ev else None,
            }
        )

    by_opp: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_opp[row["setup"]].append(row)

    print(f"=== pa_cta 定仓诊断 | {symbol} | CbC 含成本 ===")
    matched_n = sum(1 for r in rows if r["combined_mult"] is not None)
    print(
        f"Round-trip: {len(round_trips)} | 定仓快照: {len(events)} | "
        f"匹配: {matched_n}"
    )
    print()
    print(
        f"{'OPP':<42} {'笔':>3} {'净盈亏':>10} {'均组合乘子':>8} "
        f"{'setup':>5} {'aff':>5} {'sz':>4} {'均ATR比':>6} {'均手':>4}"
    )
    print("-" * 95)

    totals = sorted(
        by_opp.items(),
        key=lambda x: sum(i["net_pnl"] for i in x[1]),
        reverse=True,
    )
    for opp, items in totals:
        n = len(items)
        net = sum(i["net_pnl"] for i in items)
        matched = [i for i in items if i["combined_mult"] is not None]
        if matched:
            avg_comb = sum(i["combined_mult"] for i in matched) / len(matched)
            avg_setup = sum(i["setup_mult"] for i in matched) / len(matched)
            avg_aff = sum(i["aff_mult"] for i in matched) / len(matched)
            avg_sz = sum(i["sizing_factor"] for i in matched) / len(matched)
            avg_atr = sum(i["atr_ratio"] for i in matched) / len(matched)
            avg_vol = sum(i["volume"] for i in matched) / len(matched)
        else:
            avg_comb = avg_setup = avg_aff = avg_sz = avg_atr = avg_vol = 0.0
        print(
            f"{opp:<42} {n:>3} {net:>+10.0f} {avg_comb:>8.2f} "
            f"{avg_setup:>5.2f} {avg_aff:>5.2f} {avg_sz:>4.2f} {avg_atr:>6.3f} {avg_vol:>4.1f}"
        )

    print("-" * 95)
    print(
        "组合乘子 = setup_risk_mult × aff_mult × sizing_factor(atr_ratio)"
    )
    print(
        "sz=1.5 → ATR比∈[0.6,0.7)；sz=1.0 → [0.7,0.8)；sz=0 → 拒单"
    )

    for label, prefix in (("盈利楔 OPP15", "OPP15_"), ("亏损核 OPP02", "OPP02_")):
        sub = [r for r in rows if r["setup"].startswith(prefix)]
        if not sub:
            continue
        m = [r for r in sub if r["combined_mult"] is not None]
        print(f"\n--- {label} ({len(sub)} 笔, 净盈亏 {sum(r['net_pnl'] for r in sub):+.0f}) ---")
        if m:
            print(
                f"  均组合乘子 {sum(r['combined_mult'] for r in m) / len(m):.2f} | "
                f"setup {sum(r['setup_mult'] for r in m) / len(m):.2f} | "
                f"aff {sum(r['aff_mult'] for r in m) / len(m):.2f} | "
                f"sizing {sum(r['sizing_factor'] for r in m) / len(m):.2f}"
            )
            hi_sz = sum(1 for r in m if r["sizing_factor"] >= 1.5)
            print(f"  sizing_factor=1.5 的笔数: {hi_sz}/{len(m)}")


if __name__ == "__main__":
    sym = sys.argv[1] if len(sys.argv) > 1 else "rb"
    run_diag(sym)
