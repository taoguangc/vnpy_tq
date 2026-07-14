# -*- coding: utf-8
"""P3 — delta_div_short 收盘段软禁 attribution（post-hoc，不改策略）。

假设：14:30–14:45 内，若过去 COOLDOWN 分钟出现 delta_div_short（tick-native 60s），
则禁止 TREND lane 追空（OPP02/08/19 breakout short）。

用法::
  .venv\\Scripts\\python.exe experiments/P3_regime_filter_attribution.py --symbol rb
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.E1_tick_native_micro import run_study
from scripts.backtest_trade_analysis import RoundTripTrade
from strategies.pa_cta.backtest import run_parquet_backtest
from strategies.pa_cta.symbol_config import resolve_symbol_profile

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
BAR_SEC = 60
COOLDOWN_MINUTES = 2
EVENT_TYPE = "delta_div_short"

CHASE_SHORT_SETUPS = frozenset(
    {
        "OPP02_5M_EMA_PULLBACK_SHORT",
        "OPP08_5M_STRONG_BREAKOUT_SHORT",
        "OPP19_5M_OD_BREAKOUT_SHORT",
    }
)


def _in_close_entry_window(ts: pd.Timestamp) -> bool:
    """与 pa_cta entry_window（14:45 关窗）对齐：14:30–14:44。"""
    t = ts.time() if hasattr(ts, "time") else ts
    if isinstance(t, time):
        return time(14, 30) <= t < time(14, 45)
    m = ts.hour * 60 + ts.minute
    return 870 <= m < 885


def _load_close_div_events(
    symbol: str,
    start: datetime,
    end: datetime,
) -> pd.DatetimeIndex:
    profile = resolve_symbol_profile(symbol, ROOT)
    tick = float(profile["pricetick"])
    events, _ = run_study(
        symbol=symbol,
        bar_sec=BAR_SEC,
        start=start,
        end=end,
        tick=tick,
        verbose=False,
        save_outputs=False,
    )
    if events.empty:
        return pd.DatetimeIndex([])
    ev = events[events["event_type"] == EVENT_TYPE].copy()
    ev["datetime"] = pd.to_datetime(ev["datetime"])
    if ev["datetime"].dt.tz is None:
        ev["datetime"] = ev["datetime"].dt.tz_localize("Asia/Shanghai")
    else:
        ev["datetime"] = ev["datetime"].dt.tz_convert("Asia/Shanghai")
    ev = ev[ev["datetime"].apply(_in_close_entry_window)]
    return pd.DatetimeIndex(ev["datetime"].sort_values())


def _event_active(event_times: pd.DatetimeIndex, entry_ts: pd.Timestamp) -> bool:
    if entry_ts.tzinfo is None:
        entry_ts = entry_ts.tz_localize("Asia/Shanghai")
    else:
        entry_ts = entry_ts.tz_convert("Asia/Shanghai")
    lo = entry_ts - pd.Timedelta(minutes=COOLDOWN_MINUTES)
    idx = event_times.searchsorted(entry_ts, side="right") - 1
    if idx < 0:
        return False
    return event_times[idx] >= lo


def _max_drawdown_from_trips(trips: list[RoundTripTrade]) -> float:
    if not trips:
        return 0.0
    ordered = sorted(trips, key=lambda t: t.exit_time)
    cum = 0.0
    peak = 0.0
    max_dd = 0.0
    for t in ordered:
        cum += t.net_pnl
        peak = max(peak, cum)
        max_dd = max(max_dd, peak - cum)
    return max_dd


def _prior_close_event(
    event_times: pd.DatetimeIndex,
    entry_ts: pd.Timestamp,
    *,
    within_hours: float = 36.0,
) -> bool:
    if len(event_times) == 0:
        return False
    if entry_ts.tzinfo is None:
        entry_ts = entry_ts.tz_localize("Asia/Shanghai")
    else:
        entry_ts = entry_ts.tz_convert("Asia/Shanghai")
    idx = event_times.searchsorted(entry_ts, side="right") - 1
    if idx < 0:
        return False
    last = event_times[idx]
    return (entry_ts - last).total_seconds() <= within_hours * 3600


def _eval_scope(
    trips: list[RoundTripTrade],
    event_times: pd.DatetimeIndex,
    *,
    chase_only: bool,
    close_window_only: bool,
    match_mode: str,
) -> dict:
    """match_mode: lookback2 | prior36h"""
    blocked: list[RoundTripTrade] = []
    cohort: list[RoundTripTrade] = []
    for rt in trips:
        if rt.direction != "空":
            continue
        if chase_only and rt.setup not in CHASE_SHORT_SETUPS:
            continue
        ets = pd.Timestamp(rt.entry_time)
        if close_window_only and not _in_close_entry_window(ets):
            continue
        cohort.append(rt)
        if match_mode == "lookback2":
            if _event_active(event_times, ets):
                blocked.append(rt)
        elif match_mode == "prior36h":
            if _prior_close_event(event_times, ets):
                blocked.append(rt)
    blocked_net = sum(t.net_pnl for t in blocked)
    return {
        "cohort_n": len(cohort),
        "blocked_n": len(blocked),
        "blocked_net_pnl": blocked_net,
        "blocked_wr": (
            sum(1 for t in blocked if t.net_pnl > 0) / len(blocked) if blocked else np.nan
        ),
    }


def run_attribution(
    *,
    symbol: str = "rb",
    start: datetime | None = None,
    end: datetime | None = None,
    verbose: bool = True,
) -> pd.DataFrame:
    start = start or datetime(2023, 5, 17)
    end = end or datetime(2026, 5, 16)

    if verbose:
        print(f"P3 attribution | {symbol} | {start.date()} ~ {end.date()}", flush=True)
        print("  [1/3] rb Core OPP 回测 ...", flush=True)

    bt = run_parquet_backtest(symbol=symbol, start=start, end=end, verbose=False)
    trips: list[RoundTripTrade] = bt["round_trips"]
    stats = bt["stats"]
    base_net = float(stats.get("total_net_pnl", 0))
    base_dd = float(stats.get("max_drawdown", 0))

    if verbose:
        print("  [2/3] 加载 delta_div_short 收盘事件 ...", flush=True)

    event_times = _load_close_div_events(symbol, start, end)
    if verbose:
        print(f"       事件数: {len(event_times)} (bar={BAR_SEC}s)", flush=True)

        ("S1_chase_close_2min", True, True, "lookback2"),
        ("S2_allshort_close_2min", False, True, "lookback2"),
        ("S3_chase_any_prior36h", True, False, "prior36h"),
    ]
    scope_rows: list[dict] = []
    for name, chase, close_only, mode in scopes:
        st = _eval_scope(trips, event_times, chase_only=chase, close_window_only=close_only, match_mode=mode)
        scope_rows.append({"scope": name, **st})

    detail_rows: list[dict] = []
    for rt in trips:
        if rt.direction != "空":
            continue
        ets = pd.Timestamp(rt.entry_time)
        detail_rows.append(
            {
                "setup": rt.setup,
                "entry_time": ets,
                "exit_time": rt.exit_time,
                "net_pnl": rt.net_pnl,
                "chase_short": rt.setup in CHASE_SHORT_SETUPS,
                "close_window": _in_close_entry_window(ets),
                "event_2min": _event_active(event_times, ets),
            }
        )
    detail = pd.DataFrame(detail_rows)
    s1 = scope_rows[0]
    blocked_net = float(s1["blocked_net_pnl"])
    filt_net = base_net - blocked_net
    filt_dd = _max_drawdown_from_trips(trips)

    summary = pd.DataFrame(
        [
            {
                "symbol": symbol,
                "baseline_net_pnl": base_net,
                "baseline_max_dd": base_dd,
                "baseline_sharpe": stats.get("sharpe_ratio", np.nan),
                "baseline_trades": len(trips),
                "close_chase_short_n": s1["cohort_n"],
                "blocked_n": s1["blocked_n"],
                "blocked_net_pnl": blocked_net,
                "filtered_net_pnl": filt_net,
                "delta_pnl": filt_net - base_net,
                "filtered_max_dd_rt": filt_dd,
                "delta_dd_rt": filt_dd - _max_drawdown_from_trips(trips),
                "event_count": len(event_times),
            }
        ]
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sp = OUTPUT_DIR / f"p3_filter_attribution_{symbol}.csv"
    sc = OUTPUT_DIR / f"p3_filter_scopes_{symbol}.csv"
    dp = OUTPUT_DIR / f"p3_filter_detail_{symbol}.csv"
    summary.to_csv(sp, index=False, encoding="utf-8-sig")
    pd.DataFrame(scope_rows).to_csv(sc, index=False, encoding="utf-8-sig")
    if not detail.empty:
        detail.to_csv(dp, index=False, encoding="utf-8-sig")

    if verbose:
        print("  [3/3] 汇总")
        print("\n===== P3 Regime Filter Attribution =====")
        print(f"品种: {symbol} | 追空 OPP: OPP02/08/19 breakout short")
        print(f"窗口: 14:30–14:44 | 事件: {EVENT_TYPE} +{COOLDOWN_MINUTES}min lookback")
        print("-" * 60)
        print(f"收盘追空样本(S1): {s1['cohort_n']} 笔 | 软禁命中: {s1['blocked_n']} 笔")
        print("\n【多口径 overlap】")
        print(f"{'Scope':<26} {'Cohort':>7} {'Hit':>5} {'HitPnL':>10} {'HitWR':>7}")
        for row in scope_rows:
            wr = row["blocked_wr"]
            wr_s = f"{wr:.1%}" if wr == wr else "—"
            print(
                f"{row['scope']:<26} {row['cohort_n']:7d} {row['blocked_n']:5d} "
                f"{row['blocked_net_pnl']:+10,.0f} {wr_s:>7}"
            )
        print(f"\n基线总净盈亏:     {base_net:+,.0f}  Sharpe={stats.get('sharpe_ratio', 0):.2f}")
        print(f"基线最大回撤:     {base_dd:,.0f}")
        print(f"模拟过滤后 PnL(S1): {filt_net:+,.0f}  ΔPnL={filt_net - base_net:+,.0f}")
        if s1["blocked_n"] == 0:
            print(
                "\n结论: rb Core OPP 与 delta_div 收盘事件 **零 overlap** — "
                "filter 在当前架构下 inoperative（非 filter 逻辑无效）"
            )
        elif blocked_net < 0:
            print("\n结论: 软禁 cohort 净亏 → filter 方向正确（待策略内验证）")
        else:
            print("\n结论: 软禁 cohort 净盈 → 不宜硬禁")
        print(f"\n输出: {sp}\n       {sc}\n       {dp}")
        print("=" * 60)

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="P3 delta_div 软禁 attribution")
    parser.add_argument("--symbol", default="rb")
    parser.add_argument("--start", default="2023-05-17")
    parser.add_argument("--end", default="2026-05-16")
    args = parser.parse_args()
    start = datetime.strptime(args.start, "%Y-%m-%d")
    end = datetime.strptime(args.end, "%Y-%m-%d")
    run_attribution(symbol=args.symbol.lower(), start=start, end=end)


if __name__ == "__main__":
    main()
