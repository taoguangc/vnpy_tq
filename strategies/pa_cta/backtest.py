# -*- coding: utf-8 -*-
"""Brooks PA CTA Parquet 回测入口（TQ CbC：分月 raw + rollover_map + 21:00 切点）。

用法:
    .venv\\Scripts\\python.exe -m strategies.pa_cta.backtest --symbol rb
    .venv\\Scripts\\python.exe strategies\\pa_cta\\backtest.py --symbol rb
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from time import perf_counter

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from vnpy.trader.constant import Exchange, Interval

from strategies.pa_cta.symbol_config import build_strategy_setting, resolve_symbol_profile


def _summarize_opp_from_round_trips(round_trips: list) -> list[dict]:
    """按 setup 聚合 round-trip 净盈亏（含手续费/滑点）。"""
    from collections import defaultdict

    by: dict[str, dict] = defaultdict(
        lambda: {"n": 0, "wins": 0, "net": 0.0}
    )
    for trip in round_trips:
        setup = getattr(trip, "setup", None) or "UNKNOWN"
        by[setup]["n"] += 1
        by[setup]["net"] += trip.net_pnl
        if trip.net_pnl > 0:
            by[setup]["wins"] += 1

    rows: list[dict] = []
    for setup, d in by.items():
        n = d["n"]
        rows.append(
            {
                "setup": setup,
                "n": n,
                "win_rate": d["wins"] / n * 100.0 if n else 0.0,
                "avg_pnl": d["net"] / n if n else 0.0,
                "net_pnl": d["net"],
            }
        )
    return sorted(rows, key=lambda r: r["net_pnl"], reverse=True)


def print_setup_pnl_report(
    round_trips: list | None = None,
    *,
    setup_pnl: dict | None = None,
    setup_trades: dict | None = None,
) -> None:
    """打印各 OPP 盈亏；优先 round-trip 含成本归因，否则回退 setup_pnl 价差毛额。"""
    if round_trips:
        rows = _summarize_opp_from_round_trips(round_trips)
        if not rows:
            return
        print("\n===== 各 OPP 盈亏（含成本 round-trip 归因）=====")
        print(f"  {'OPP':<42s} {'笔数':>4} {'胜率':>6} {'均PnL':>10} {'净盈亏':>12}")
        print("  " + "-" * 76)
        tot_n = tot_net = 0
        for row in rows:
            print(
                f"  {row['setup']:<42s} {row['n']:>4} "
                f"{row['win_rate']:>5.1f}% {row['avg_pnl']:>+10.0f} "
                f"{row['net_pnl']:>+12.0f}"
            )
            tot_n += row["n"]
            tot_net += row["net_pnl"]
        print("  " + "-" * 76)
        print(
            f"  {'合计':<42s} {tot_n:>4} {'':>6} {'':>10} {tot_net:>+12.0f}"
        )
        print("=" * 40)
        return

    if not setup_pnl:
        return
    items = sorted(setup_pnl.items(), key=lambda x: x[1], reverse=True)
    total = sum(setup_pnl.values())
    total_trades = sum(setup_trades.values()) if setup_trades else 0
    print("\n===== 各 OPP 收益贡献（价差毛额，无 round-trip 归因）=====")
    for setup, pnl in items:
        n = setup_trades.get(setup, 0) if setup_trades else 0
        avg = pnl / n if n else 0.0
        print(f"  {setup:<42s} {n:>3d}笔  {avg:>+10.0f}  {pnl:>+10.0f}")
    print("-" * 40)
    print(f"  {'合计':<42s} {total_trades:>3d}笔  {total:>+10.0f}")
    print("=" * 40)


def print_backtest_report(
    stats: dict,
    data_count: int,
    load_seconds: float,
    backtest_seconds: float,
    symbol: str,
    exchange: Exchange,
    start: datetime,
    end: datetime,
    *,
    zero_cost: bool = False,
    round_trips: list | None = None,
    open_position: object | None = None,
    initial_capital: float | None = None,
    strategy_setting: dict | None = None,
    funnel_diag: dict | None = None,
    setup_pnl: dict | None = None,
    setup_trades: dict | None = None,
) -> None:
    title = f"Parquet 回测统计 (Brooks PA CTA {symbol}"
    if zero_cost:
        title += " | 零成本"
    print(f"\n===== {title}) =====")
    print(f"品种: {symbol}.{exchange.value}")
    print(f"区间: {start.date()} -> {end.date()}")
    print(f"数据量(1m): {data_count:,}")
    from strategies.pa_cta.strategy import BrooksPaCtaStrategy as _cls
    cls = _cls
    print(
        f"信号K={cls.signal_bar_window}m, 背景K={cls.signal_bar_window * cls.context_bar_window}m, "
        f"EMA={cls.ema_window}, ATR={cls.atr_window}, rb_min_atr={cls.rb_min_atr}"
    )
    if strategy_setting:
        print(f"setting: {strategy_setting}")
    print(f"加载: {load_seconds:.2f}s  回测: {backtest_seconds:.2f}s")
    print("-" * 40)

    fields = [
        ("初始资金", "capital", ",.2f"),
        ("结束资金", "end_balance", ",.2f"),
        ("总收益率", "total_return", ".2f", "%"),
        ("年化收益", "annual_return", ".2f", "%"),
        ("最大回撤", "max_drawdown", ",.2f"),
        ("最大回撤率", "max_ddpercent", ".2f", "%"),
        ("总净盈亏", "total_net_pnl", ",.2f"),
        ("交易次数", "total_trade_count", ",.0f"),
        ("Sharpe Ratio", "sharpe_ratio", ".2f"),
        ("总手续费", "total_commission", ",.2f"),
        ("总滑点", "total_slippage", ",.2f"),
    ]
    for field in fields:
        label, key, fmt, *suffix = field
        value = stats.get(key)
        unit = suffix[0] if suffix else ""
        if value is None:
            print(f"{label}: N/A")
        else:
            print(f"{label}: {value:{fmt}}{unit}")

    if round_trips is not None:
        from scripts.backtest_trade_analysis import (
            print_open_position_report,
            print_top_round_trips,
            summarize_round_trips,
        )

        rt_summary = summarize_round_trips(round_trips)
        if rt_summary:
            print("\n----- Round-trip 汇总 -----")
            print(f"完整交易: {rt_summary.get('total', 0)} 笔")
            wr = rt_summary.get("win_rate")
            if wr is not None:
                print(f"胜率: {wr:.2f}%")
            pf = rt_summary.get("profit_factor")
            if pf is not None:
                print(f"盈亏比: {pf:.2f}")

        print_top_round_trips(round_trips, top_n=5)
        closed_rt_net = sum(t.net_pnl for t in round_trips)
        capital = initial_capital or stats.get("capital") or 0.0
        print_open_position_report(
            open_position,
            total_net_pnl=stats.get("total_net_pnl"),
            closed_rt_net_pnl=closed_rt_net,
            initial_capital=float(capital),
        )

    if funnel_diag:
        print("\n===== 漏斗诊断 =====")
        dc = funnel_diag.get("dual_core_block_count", 0)
        vsa_blk = funnel_diag.get("vsa_block_count", 0)
        vsa_exempt = funnel_diag.get("vsa_persistence_exempt_count", 0)
        print(f"VWAP Dual Core 拦截: {dc}")
        print(f"VSA 拦截: {vsa_blk}  持续性豁免: {vsa_exempt}")
        late_blk = funnel_diag.get("late_phase_block_count", 0)
        if late_blk:
            print(f"LATE 软禁拦截: {late_blk}")
        aff_blk = funnel_diag.get("aff_block_count", 0)
        if aff_blk:
            print(f"AFF 规则拦截: {aff_blk}")
        print("=" * 40)

    print_setup_pnl_report(
        round_trips,
        setup_pnl=setup_pnl,
        setup_trades=setup_trades,
    )


def _run_engine_backtest(
    engine,
    *,
    rate: float,
    slippage: float,
    mark_price: float | None = None,
    mark_time: datetime | None = None,
) -> dict:
    from scripts.backtest_trade_analysis import (
        pair_round_trips,
        snapshot_open_position_at_end,
        summarize_round_trips,
    )

    engine.run_backtesting()
    engine.calculate_result()
    stats = engine.calculate_statistics(output=False)
    strategy = engine.strategy
    all_trades = list(engine.get_all_trades())
    round_trips = pair_round_trips(
        all_trades,
        size=engine.size,
        rate=rate,
        slippage=slippage,
        capital=engine.capital,
    )
    # E3 归因：从策略内部 _trade_log 按 entry_time 对齐，填充 setup / exit_reason 等字段
    internal_log = list(getattr(strategy, "_trade_log", []) or [])
    if internal_log:
        _augment_round_trips_with_trade_log(round_trips, internal_log)
    open_position = None
    if mark_price is not None and mark_time is not None:
        open_position = snapshot_open_position_at_end(
            all_trades,
            size=engine.size,
            mark_price=mark_price,
            mark_time=mark_time,
            capital=engine.capital,
        )
    return {
        "stats": stats,
        "round_trips": round_trips,
        "rt_summary": summarize_round_trips(round_trips),
        "open_position": open_position,
        "trade_log": internal_log,
        "setup_perf": {
            k: list(v)
            for k, v in getattr(strategy, "_setup_perf", {}).items()
            if v
        },
        "funnel_diag": {
            "dual_core_block_count": int(getattr(strategy, "_dual_core_block_count", 0)),
            "dual_core_soft_reduce_count": int(
                getattr(strategy, "_dual_core_soft_reduce_count", 0)
            ),
            "vsa_block_count": int(getattr(strategy, "vsa_block_count", 0)),
            "vsa_persistence_exempt_count": int(
                getattr(strategy, "vsa_persistence_exempt_count", 0)
            ),
            "late_phase_block_count": int(
                getattr(strategy, "_late_phase_block_count", 0)
            ),
            "aff_block_count": int(getattr(strategy, "_aff_block_count", 0)),
            "aff_archetype_block_count": int(
                getattr(strategy, "_aff_archetype_block_count", 0)
            ),
        },
        "setup_pnl": dict(getattr(strategy, "_setup_pnl", {})),
        "setup_trades": dict(getattr(strategy, "_setup_trades", {})),
    }


def export_shadow_ledger(
    strategy,
    bars_1m: list,
    *,
    contract_size: float,
    pricetick: float,
    rate: float,
    slippage_ticks: float,
    export_path: Path | None = None,
) -> Path | None:
    """回测结束后附加 forwards 并导出 production OPP 影子账本 CSV。"""
    if not getattr(strategy, "shadow_ledger_enabled", False):
        return None
    ledger = getattr(strategy, "_shadow_ledger", None)
    if ledger is None or not ledger.records:
        return None
    path = export_path or getattr(strategy, "_shadow_export_path", None)
    if path is None:
        sym = getattr(ledger, "symbol", "unknown")
        path = _ROOT / "research" / "output" / f"shadow_ledger_{sym}.csv"
    path = Path(path)
    ledger.attach_forwards(
        bars_1m,
        contract_size=contract_size,
        pricetick=pricetick,
        rate=rate,
        slippage_ticks=slippage_ticks,
    )
    return ledger.export_csv(path)


def _augment_round_trips_with_trade_log(
    round_trips: list,
    trade_log: list[dict],
) -> None:
    """用策略内部 _trade_log（按 entry_time 近似对齐）回填 RoundTripTrade 的归因字段。"""
    if not round_trips or not trade_log:
        return
    # 以 entry_time 近似对齐：同方向 + 时间差最小者
    remaining = list(trade_log)
    for rt in round_trips:
        best_idx = -1
        best_delta = None
        for i, log in enumerate(remaining):
            if log.get("direction") != rt.direction:
                continue
            if log.get("entry_time") is None:
                continue
            delta = abs((log["entry_time"] - rt.entry_time).total_seconds())
            if best_delta is None or delta < best_delta:
                best_delta = delta
                best_idx = i
        if best_idx < 0:
            continue
        log = remaining.pop(best_idx)
        rt.setup = log.get("setup", "")
        rt.market_context = log.get("market_context", "")
        rt.always_in = log.get("always_in", "")
        rt.trend_age_bars = int(log.get("trend_age_bars", 0) or 0)
        rt.entry_atr = float(log.get("entry_atr", 0.0) or 0.0)
        rt.atr_ratio = float(log.get("atr_ratio", 0.0) or 0.0)
        rt.mfe_ticks = float(log.get("mfe_ticks", 0.0) or 0.0)
        rt.mae_ticks = float(log.get("mae_ticks", 0.0) or 0.0)
        rt.holding_minutes = float(log.get("holding_minutes", 0.0) or 0.0)
        rt.exit_reason = log.get("exit_reason", "")


def run_tq_cbc_backtest(
    *,
    symbol: str = "rb",
    zero_cost: bool = False,
    strategy_overrides: dict | None = None,
    verbose: bool = True,
    start: datetime | None = None,
    end: datetime | None = None,
    slippage_override: float | None = None,
    strategy_class: type | None = None,
    profile_resolver=None,
    build_setting=None,
    run_engine_backtest_fn=None,
    strategy_label: str = "Brooks PA CTA",
    base_strategy_class: type | None = None,
    rollover_strategy_class: type | None = None,
    bars_loader=None,
) -> dict:
    """TQ 分月 raw + 21:00 换月（CbC）。"""
    root = Path(__file__).parent.parent.parent.resolve()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from scripts.rollover_backtest_engine import RolloverBacktestingEngine
    from scripts.tq_rollover_data import build_rollover_events, load_stitched_raw_bars
    from strategies.pa_cta.rollover_strategy import BrooksPaCtaRolloverStrategy
    from strategies.pa_cta.strategy import BrooksPaCtaStrategy
    from strategies.pa_cta.symbol_config import (
        build_strategy_setting as lean_build_setting,
        resolve_symbol_profile as lean_resolve_profile,
        resolve_tq_cbc_paths,
    )

    resolve_profile = profile_resolver or lean_resolve_profile
    build_strategy_setting_fn = build_setting or lean_build_setting
    run_engine = run_engine_backtest_fn or _run_engine_backtest
    base_cls = base_strategy_class or BrooksPaCtaStrategy
    rollover_cls = rollover_strategy_class or BrooksPaCtaRolloverStrategy

    if profile_resolver is not None:
        profile = profile_resolver(symbol, root, data_source="tq")
    else:
        profile = resolve_profile(symbol, root)
    symbol = profile["symbol"]
    exchange = profile["exchange"]
    data_dir, file_stem = resolve_tq_cbc_paths(profile)
    map_path = data_dir / "rollover_map.parquet"
    if not map_path.exists():
        raise FileNotFoundError(f"未找到换月表: {map_path}（先运行 build_rollover_map.py -s {file_stem}")

    start = start or datetime(2023, 5, 17)
    end = end or datetime(2026, 5, 16)
    backtest_capital = 200_000

    rate = 0.0 if zero_cost else 0.00003
    slippage = 0 if zero_cost else profile["slippage"]
    if slippage_override is not None and not zero_cost:
        slippage = slippage_override

    prefix = file_stem
    events = build_rollover_events(prefix, start=start, end=end)
    load_start = perf_counter()
    if bars_loader is not None:
        bars = bars_loader(
            prefix,
            exchange,
            symbol=symbol,
            start=start,
            end=end,
        )
        data_label = "tick→1m 重采样"
    else:
        bars = load_stitched_raw_bars(
            prefix,
            exchange,
            symbol=symbol,
            start=start,
            end=end,
        )
        data_label = "分月 raw 1m"
    load_seconds = perf_counter() - load_start

    engine = RolloverBacktestingEngine()
    engine.set_rollover_events(events)
    engine.set_parameters(
        vt_symbol=f"{symbol}.{exchange.value}",
        interval=Interval.MINUTE,
        start=start,
        end=end,
        rate=rate,
        slippage=slippage,
        size=profile["size"],
        pricetick=profile["pricetick"],
        capital=backtest_capital,
    )

    strategy_class = strategy_class or rollover_cls
    if strategy_class is base_cls:
        strategy_class = rollover_cls
    strategy_setting = build_strategy_setting_fn(profile, capital=backtest_capital)
    shadow_export_path = None
    candidate_export_path = None
    if strategy_overrides:
        overrides = dict(strategy_overrides)
        shadow_export_path = overrides.pop("shadow_export_path", None) or overrides.pop(
            "_shadow_export_path", None
        )
        candidate_export_path = overrides.pop("candidate_export_path", None) or overrides.pop(
            "_candidate_export_path", None
        )
        strategy_setting.update(overrides)
    allowed_params = set(getattr(strategy_class, "parameters", []))
    filtered_setting = {k: v for k, v in strategy_setting.items() if k in allowed_params}
    engine.add_strategy(strategy_class, filtered_setting)
    engine.history_data = bars

    last_bar = bars[-1] if bars else None
    mark_price = last_bar.close_price if last_bar else None
    mark_time = last_bar.datetime if last_bar else end

    t0 = perf_counter()
    result = run_engine(
        engine,
        rate=rate,
        slippage=slippage,
        mark_price=mark_price,
        mark_time=mark_time,
    )
    backtest_seconds = perf_counter() - t0
    stats = result["stats"]
    strategy = engine.strategy
    shadow_path = export_shadow_ledger(
        strategy,
        bars,
        contract_size=float(engine.size),
        pricetick=float(engine.pricetick),
        rate=float(rate),
        slippage_ticks=float(slippage),
        export_path=Path(shadow_export_path) if shadow_export_path else None,
    )
    shadow_count = len(getattr(getattr(strategy, "_shadow_ledger", None), "records", []) or [])

    if verbose:
        title_extra = " | TQ CbC raw"
        if zero_cost:
            title_extra += " | 零成本"
        print(f"\n===== Parquet 回测统计 ({strategy_label} {symbol}{title_extra}) =====")
        print(f"品种: {symbol}.{exchange.value}")
        print(f"区间: {start.date()} -> {end.date()}")
        print(f"数据: {data_label} 拼接 | 换月 {len(events)} 次 | 切点 21:00 CST")
        print(f"数据量(1m): {len(bars):,}")
        print(f"加载: {load_seconds:.2f}s  回测: {backtest_seconds:.2f}s")
        print("-" * 40)
        for field in [
            ("初始资金", "capital", ",.2f"),
            ("结束资金", "end_balance", ",.2f"),
            ("总收益率", "total_return", ".2f", "%"),
            ("年化收益", "annual_return", ".2f", "%"),
            ("最大回撤", "max_drawdown", ",.2f"),
            ("最大回撤率", "max_ddpercent", ".2f", "%"),
            ("总净盈亏", "total_net_pnl", ",.2f"),
            ("交易次数", "total_trade_count", ",.0f"),
            ("Sharpe Ratio", "sharpe_ratio", ".2f"),
            ("总手续费", "total_commission", ",.2f"),
            ("总滑点", "total_slippage", ",.2f"),
        ]:
            label, key, fmt, *suffix = field
            value = stats.get(key)
            unit = suffix[0] if suffix else ""
            if value is None:
                print(f"{label}: N/A")
            else:
                print(f"{label}: {value:{fmt}}{unit}")

        from scripts.backtest_trade_analysis import (
            print_open_position_report,
            print_top_round_trips,
            summarize_round_trips,
        )

        round_trips = result["round_trips"]
        rt_summary = summarize_round_trips(round_trips)
        if rt_summary:
            print("\n----- Round-trip 汇总 -----")
            print(f"完整交易: {rt_summary.get('total', 0)} 笔")
            wr = rt_summary.get("win_rate")
            if wr is not None:
                print(f"胜率: {wr:.2f}%")
            pf = rt_summary.get("profit_factor")
            if pf is not None:
                print(f"盈亏比: {pf:.2f}")
        print_top_round_trips(round_trips, top_n=5)
        closed_rt_net = sum(t.net_pnl for t in round_trips)
        print_open_position_report(
            result["open_position"],
            total_net_pnl=stats.get("total_net_pnl"),
            closed_rt_net_pnl=closed_rt_net,
            initial_capital=float(backtest_capital),
        )

        rs = engine.rollover_stats
        print("\n===== 换月移仓统计 =====")
        print(f"换月执行: {rs.count} 次 | 移仓手数: {rs.contracts_rolled}")
        print(f"价差缺口 PnL(理论): {rs.total_gap_pnl:+,.0f}")
        print("=" * 40)

        funnel_diag = result.get("funnel_diag")
        if funnel_diag:
            print("\n===== 漏斗诊断 =====")
            print(f"VWAP Dual Core 拦截: {funnel_diag.get('dual_core_block_count', 0)}")
            print(f"VSA 拦截: {funnel_diag.get('vsa_block_count', 0)}")
            print("=" * 40)

        print_setup_pnl_report(
            round_trips,
            setup_pnl=result.get("setup_pnl"),
            setup_trades=result.get("setup_trades"),
        )
        if shadow_path is not None:
            print(f"\n===== Production OPP 影子账本 =====")
            print(f"  导出: {shadow_path}")
            print(f"  候选数: {shadow_count:,}")
            print("=" * 40)

    candidate_funnel = None
    candidate_records = None
    if hasattr(strategy, "get_candidate_ledger"):
        ledger = strategy.get_candidate_ledger()
        if ledger is not None:
            if hasattr(ledger, "attach_forwards") and ledger.records:
                ledger.attach_forwards(
                    bars,
                    contract_size=float(engine.size),
                    pricetick=float(engine.pricetick),
                    rate=float(rate),
                    slippage_ticks=float(slippage),
                )
            candidate_funnel = ledger.funnel()
            candidate_records = ledger.to_rows()
            if candidate_export_path and hasattr(ledger, "export_csv"):
                ledger.export_csv(Path(candidate_export_path))

    dryscan_compare = None
    if hasattr(strategy, "get_dryscan_compare"):
        dryscan_compare = strategy.get_dryscan_compare()

    return {
        "name": f"{strategy_label} {symbol} TQ CbC",
        "stats": stats,
        "round_trips": result["round_trips"],
        "rt_summary": result["rt_summary"],
        "open_position": result["open_position"],
        "trade_log": result.get("trade_log", []),
        "setup_pnl": result.get("setup_pnl", {}),
        "setup_trades": result.get("setup_trades", {}),
        "funnel_diag": result.get("funnel_diag", {}),
        "candidate_funnel": candidate_funnel,
        "candidate_records": candidate_records,
        "dryscan_compare": dryscan_compare,
        "load_seconds": load_seconds,
        "backtest_seconds": backtest_seconds,
        "rollover_stats": engine.rollover_stats,
        "data_count": len(bars),
        "shadow_ledger_path": str(shadow_path) if shadow_path else None,
        "shadow_ledger_count": shadow_count,
    }


def run_parquet_backtest(
    *,
    symbol: str = "rb",
    zero_cost: bool = False,
    strategy_overrides: dict | None = None,
    history_data: list | None = None,
    verbose: bool = True,
    start: datetime | None = None,
    end: datetime | None = None,
    slippage_override: float | None = None,
    strategy_class: type | None = None,
    profile_mode: str = "production",
) -> dict:
    if history_data is not None:
        raise ValueError("TQ CbC 回测不支持预加载 history_data")
    profile_resolver = None
    if profile_mode == "generic_base":
        from strategies.pa_cta.symbol_config import resolve_generic_base_profile

        profile_resolver = resolve_generic_base_profile
    elif profile_mode != "production":
        raise ValueError(f"未知 profile_mode: {profile_mode}")
    return run_tq_cbc_backtest(
        symbol=symbol,
        zero_cost=zero_cost,
        strategy_overrides=strategy_overrides,
        verbose=verbose,
        start=start,
        end=end,
        slippage_override=slippage_override,
        strategy_class=strategy_class,
        profile_resolver=profile_resolver,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Brooks PA CTA Parquet 回测（TQ CbC）")
    parser.add_argument("--symbol", default="rb", help="品种，如 rb hc")
    parser.add_argument("--zero-cost", action="store_true", help="零成本对照")
    parser.add_argument(
        "--slippage",
        type=float,
        default=None,
        help="滑点 tick 覆盖（如 rb 用 1）",
    )
    args = parser.parse_args()
    run_parquet_backtest(
        symbol=args.symbol,
        zero_cost=args.zero_cost,
        slippage_override=args.slippage,
    )
