"""SMC-OrderFlow-VWAP 策略离线回测入口（rb 螺纹钢）。

数据：TQ CbC 分月 raw + rollover_map 拼接（无复权）+ 21:00 换月移仓模拟。

用法:
    .venv\\Scripts\\python.exe strategies/smc_orderflow_vwap/run_backtest.py
    .venv\\Scripts\\python.exe strategies/smc_orderflow_vwap/run_backtest.py --start 2023-07-01 --end 2026-06-30
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from vnpy.trader.constant import Direction, Exchange, Interval
from vnpy_ctastrategy.backtesting import BacktestingEngine

from scripts.rollover_backtest_engine import RolloverBacktestingEngine
from scripts.tq_rollover_data import build_rollover_events, load_stitched_raw_bars
from strategies.smc_orderflow_vwap.rollover_strategy import SmcOrderFlowVwapRolloverStrategy

WARMUP_DAYS = 20

# 品种规格：合约乘数(size)/最小变动价位(pricetick)/交易所参照官方合约手册核对。
SYMBOL_SPECS = {
    "rb": {
        "prefix": "rb",
        "exchange": Exchange.SHFE,
        "size": 10,
        "pricetick": 1.0,
        "rate": 1e-4,
        "slippage": 1.0,
        "capital": 200_000,
    },
    "i": {
        "prefix": "i",
        "exchange": Exchange.DCE,
        "size": 100,
        "pricetick": 0.5,
        "rate": 1e-4,
        "slippage": 0.5,
        "capital": 200_000,
    },
    "SA": {
        "prefix": "SA",
        "exchange": Exchange.CZCE,
        "size": 20,
        "pricetick": 1.0,
        "rate": 1e-4,
        "slippage": 1.0,
        "capital": 200_000,
    },
}
RB_SPEC = SYMBOL_SPECS["rb"]


def format_branch_diagnostic(
    engine: BacktestingEngine,
    events: list[tuple[datetime, str]],
) -> str:
    """按成交记录配对 round-trip，拆分 delta_reversal / delta_exhaustion。"""
    trades = sorted(engine.get_all_trades(), key=lambda t: t.datetime)
    size = float(engine.size)
    pending_branches = [branch for _, branch in events]
    stats: dict[str, dict[str, float | int]] = {
        "fast_reversal": {"entries": 0, "rounds": 0, "wins": 0, "gross_pnl": 0.0},
        "slow_reversal": {"entries": 0, "rounds": 0, "wins": 0, "gross_pnl": 0.0},
        "slow_opp16": {"entries": 0, "rounds": 0, "wins": 0, "gross_pnl": 0.0},
        "setup_c_structure": {"entries": 0, "rounds": 0, "wins": 0, "gross_pnl": 0.0},
        "setup_b_stat": {"entries": 0, "rounds": 0, "wins": 0, "gross_pnl": 0.0},
        "reversal": {"entries": 0, "rounds": 0, "wins": 0, "gross_pnl": 0.0},
        "exhaustion": {"entries": 0, "rounds": 0, "wins": 0, "gross_pnl": 0.0},
        "unknown": {"entries": 0, "rounds": 0, "wins": 0, "gross_pnl": 0.0},
    }

    idx = 0
    while idx < len(trades):
        trade = trades[idx]
        if trade.direction != Direction.LONG:
            idx += 1
            continue

        branch = pending_branches.pop(0) if pending_branches else "unknown"
        if branch not in stats:
            branch = "unknown"
        stats[branch]["entries"] = int(stats[branch]["entries"]) + 1

        buy_value = 0.0
        sell_value = 0.0
        open_volume = 0.0
        closed_volume = 0.0
        j = idx
        while j < len(trades):
            leg = trades[j]
            if j == idx:
                buy_value += leg.price * leg.volume
                open_volume += leg.volume
                j += 1
                continue
            if leg.direction == Direction.LONG:
                break
            if leg.direction == Direction.SHORT:
                sell_value += leg.price * leg.volume
                closed_volume += leg.volume
                j += 1
                if closed_volume >= open_volume:
                    break
                continue
            j += 1

        if closed_volume > 0:
            avg_buy = buy_value / open_volume
            avg_sell = sell_value / closed_volume
            gross_pnl = (avg_sell - avg_buy) * closed_volume * size
            stats[branch]["rounds"] = int(stats[branch]["rounds"]) + 1
            stats[branch]["gross_pnl"] = float(stats[branch]["gross_pnl"]) + gross_pnl
            if gross_pnl > 0:
                stats[branch]["wins"] = int(stats[branch]["wins"]) + 1

        idx = max(j, idx + 1)

    lines = [
        "【分支诊断】独立 Setup 拆分",
        "说明: 毛盈亏 = (卖均价-买均价)×手数×乘数，未扣手续费/滑点",
    ]
    total_rounds = 0
    total_gross = 0.0
    for branch, label in (
        ("fast_reversal", "SetupA-快通道"),
        ("slow_reversal", "SetupA-慢通道反转棒"),
        ("slow_opp16", "SetupA-慢通道OPP16"),
        ("setup_c_structure", "SetupC-纯结构单"),
        ("setup_b_stat", "SetupB-纯统计单"),
        ("reversal", "legacy reversal"),
        ("exhaustion", "delta_exhaustion"),
    ):
        row = stats[branch]
        rounds = int(row["rounds"])
        wins = int(row["wins"])
        gross = float(row["gross_pnl"])
        entries = int(row["entries"])
        wr = (wins / rounds * 100) if rounds else 0.0
        avg = (gross / rounds) if rounds else 0.0
        total_rounds += rounds
        total_gross += gross
        lines.append(
            f"  {label}: 开仓 {entries} | 回合 {rounds} | 胜率 {wr:.1f}% | "
            f"毛PnL {gross:,.0f} | 均笔 {avg:,.0f}"
        )
    unknown_rounds = int(stats["unknown"]["rounds"])
    if unknown_rounds:
        lines.append(f"  未匹配分支回合: {unknown_rounds}")
    lines.append(f"  合计回合: {total_rounds} | 合计毛PnL: {total_gross:,.0f}")
    return "\n".join(lines)


EXIT_COMPARE_CONFIGS: list[tuple[str, dict]] = [
    (
        "基线14:55固定",
        {
            "scale_out_mode": "fixed",
            "scale_out_remain_stop": "breakeven_plus",
            "scale_out_stop_buffer": 1,
        },
    ),
    (
        "盈利门槛15t",
        {
            "scale_out_mode": "profit_gated",
            "scale_out_min_profit_ticks": 15,
            "scale_out_remain_stop": "breakeven_plus",
            "scale_out_stop_buffer": 1,
        },
    ),
    (
        "VWAP回归平半",
        {
            "scale_out_mode": "vwap",
            "scale_out_remain_stop": "structure",
        },
    ),
    (
        "无ScaleOut",
        {
            "scale_out_mode": "none",
            "scale_out_remain_stop": "structure",
        },
    ),
]

MACRO_COMPARE_CONFIGS = [
    (
        "15m+休市断bar",
        {
            "macro_tf": "15m",
            "smc_pool_bars": 12,
            "smc_min_bars": 16,
        },
    ),
    (
        "60m基线",
        {
            "macro_tf": "60m",
            "smc_pool_bars": 10,
            "smc_min_bars": 12,
        },
    ),
]


def run_single_backtest(
    bars: list,
    rollover_events: list,
    *,
    start: datetime,
    end: datetime,
    capital: float,
    strategy_setting: dict | None = None,
    show_stats: bool = True,
    spec: dict = RB_SPEC,
) -> dict:
    prefix = spec["prefix"]
    exchange = spec["exchange"]
    vt_symbol = f"{prefix}.{exchange.value}"

    engine = RolloverBacktestingEngine()
    engine.set_rollover_events(rollover_events)
    engine.set_parameters(
        vt_symbol=vt_symbol,
        interval=Interval.MINUTE,
        start=start,
        end=end,
        rate=spec["rate"],
        slippage=spec["slippage"],
        size=spec["size"],
        pricetick=spec["pricetick"],
        capital=capital,
    )
    engine.history_data = bars
    engine.add_strategy(SmcOrderFlowVwapRolloverStrategy, strategy_setting or {})

    engine.run_backtesting()
    df = engine.calculate_result()
    stats = engine.calculate_statistics(df, output=show_stats)
    return {
        "engine": engine,
        "df": df,
        "stats": stats or {},
        "rollover_stats": engine.rollover_stats,
    }


def print_exit_compare_table(rows: list[dict]) -> None:
    print("\n| 版本 | 总PnL | 总收益率 | Sharpe | 最大回撤 | 成交笔数 | ΔPnL |")
    print("|------|-------|---------|--------|---------|---------|------|")
    base_pnl = rows[0]["net_pnl"] if rows else 0.0
    for row in rows:
        delta = row["net_pnl"] - base_pnl
        delta_s = "—" if row is rows[0] else f"{delta:+,.0f}"
        print(
            f"| {row['label']} | {row['net_pnl']:,.0f} | {row['total_return']:.2f}% | "
            f"{row['sharpe']:.2f} | {row['max_dd']:.2f}% | {row['trades']} | {delta_s} |"
        )
    best = max(rows, key=lambda r: r["net_pnl"])
    print(f"\n结论：{best['label']} 净盈亏最高（{best['net_pnl']:,.0f}）。")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SMC-OrderFlow-VWAP 策略离线回测")
    parser.add_argument(
        "--symbol", default="rb", choices=sorted(SYMBOL_SPECS.keys()), help="品种前缀",
    )
    parser.add_argument("--start", default="2023-07-01", help="回测起始 YYYY-MM-DD")
    parser.add_argument("--end", default="2026-06-30", help="回测结束 YYYY-MM-DD")
    parser.add_argument("--capital", type=float, default=None)
    parser.add_argument("--no-chart", action="store_true", help="不弹出净值曲线")
    parser.add_argument(
        "--compare-exit",
        action="store_true",
        help="出场规则对照（固定/盈利门槛/VWAP回归/无ScaleOut），整命令计 1 轮回测",
    )
    parser.add_argument(
        "--compare-macro",
        action="store_true",
        help="宏观周期对照（15m+休市断bar vs 60m基线），整命令计 1 轮回测",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    spec = SYMBOL_SPECS[args.symbol]
    capital = args.capital if args.capital is not None else spec["capital"]

    start = datetime.strptime(args.start, "%Y-%m-%d")
    end = datetime.strptime(args.end, "%Y-%m-%d")
    load_start = start - timedelta(days=WARMUP_DAYS)

    prefix = spec["prefix"]
    exchange = spec["exchange"]
    vt_symbol = f"{prefix}.{exchange.value}"

    print("=" * 60)
    print(f"策略: {SmcOrderFlowVwapRolloverStrategy.__name__}")
    print(f"品种: {vt_symbol}")
    print(f"回测: {start.date()} ~ {end.date()}（预热 {WARMUP_DAYS} 天）")
    print("数据: CbC 分月 raw + rollover_map | 换月移仓 21:00 CST")
    print("=" * 60)

    rollover_events = build_rollover_events(prefix, start=load_start, end=end)
    bars = load_stitched_raw_bars(
        prefix,
        exchange,
        start=load_start,
        end=end,
    )
    if not bars:
        print("未加载到 K 线，请先执行 download_rb_monthly + build_rollover_map")
        sys.exit(1)

    print(f"已加载 {len(bars)} 根 1m K 线 | 换月事件 {len(rollover_events)} 次")

    if args.compare_macro:
        compare_rows: list[dict] = []
        for label, setting in MACRO_COMPARE_CONFIGS:
            print(f"\n----- 宏观对照: {label} -----")
            result = run_single_backtest(
                bars,
                rollover_events,
                start=start,
                end=end,
                capital=capital,
                strategy_setting=setting,
                show_stats=False,
                spec=spec,
            )
            stats = result["stats"]
            compare_rows.append({
                "label": label,
                "net_pnl": float(stats.get("total_net_pnl", 0.0)),
                "total_return": float(stats.get("total_return", 0.0)),
                "sharpe": float(stats.get("sharpe_ratio", 0.0)),
                "max_dd": float(stats.get("max_ddpercent", 0.0)),
                "trades": int(stats.get("total_trade_count", 0)),
            })
        print_exit_compare_table(compare_rows)
        print("=" * 60)
        print("宏观周期对照完成")
        print("=" * 60)
        return

    if args.compare_exit:
        compare_rows: list[dict] = []
        for label, setting in EXIT_COMPARE_CONFIGS:
            print(f"\n----- 出场对照: {label} -----")
            result = run_single_backtest(
                bars,
                rollover_events,
                start=start,
                end=end,
                capital=capital,
                strategy_setting=setting,
                show_stats=False,
                spec=spec,
            )
            stats = result["stats"]
            compare_rows.append({
                "label": label,
                "net_pnl": float(stats.get("total_net_pnl", 0.0)),
                "total_return": float(stats.get("total_return", 0.0)),
                "sharpe": float(stats.get("sharpe_ratio", 0.0)),
                "max_dd": float(stats.get("max_ddpercent", 0.0)),
                "trades": int(stats.get("total_trade_count", 0)),
            })
        print_exit_compare_table(compare_rows)
        print("=" * 60)
        print("出场对照完成")
        print("=" * 60)
        return

    result = run_single_backtest(
        bars,
        rollover_events,
        start=start,
        end=end,
        capital=capital,
        show_stats=True,
        spec=spec,
    )
    engine = result["engine"]
    df = result["df"]

    strategy = engine.strategy
    events = getattr(strategy, "_entry_branch_events", [])
    print(format_branch_diagnostic(engine, events))

    rs = result["rollover_stats"]
    if rs.count:
        print("\n===== 换月移仓统计 =====")
        print(f"换月执行: {rs.count} 次 | 移仓手数: {rs.contracts_rolled}")
        print(f"换月价差盈亏: {rs.total_gap_pnl:,.2f}")
        if rs.total_rollover_slippage or rs.total_rollover_commission:
            print(
                f"换月滑点成本: {rs.total_rollover_slippage:,.2f} | "
                f"换月手续费: {rs.total_rollover_commission:,.2f}"
            )
    if rs.holiday_gap_events:
        print(f"\n【节假日换月顺延】{len(rs.holiday_gap_events)} 次（计划切点当晚无夜盘，顺延至下一可用 bar 执行）")
        for ev in rs.holiday_gap_events:
            print(
                f"  {ev['from']}->{ev['to']}: 计划 {ev['planned_switch']} -> "
                f"实际 {ev['actual_switch']}（延迟 {ev['gap_days']} 天）"
            )
    if rs.missed_switches:
        print(f"\n【未匹配换月，持仓未移仓】{len(rs.missed_switches)} 次，需人工核查")
        for ev in rs.missed_switches:
            print(f"  {ev['from']}->{ev['to']} @ {ev['bar_datetime']} pos={ev['pos']}")

    if not args.no_chart and df is not None and not df.empty:
        engine.show_chart(df)

    print("=" * 60)
    print("回测完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
