"""经典基线策略对照回测（Dual Thrust vs 海龟信号），品种默认 rb。

一次性加载 CbC 1m 数据，依次回测两个 vnpy 官方经典策略，输出并列指标表。
用途: 为本地 PA/SMC 策略建立"网上经典策略"的交易频率/收益基线对照。

用法:
    .venv/Scripts/python.exe scripts/run_classic_baseline_compare.py
    .venv/Scripts/python.exe scripts/run_classic_baseline_compare.py --prefix rb --start 2021-07-01 --end 2026-06-30
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from vnpy.trader.constant import Exchange, Interval

from scripts.rollover_backtest_engine import RolloverBacktestingEngine
from scripts.tq_rollover_data import build_rollover_events, load_stitched_raw_bars
from strategies.classic_dual_thrust_strategy import ClassicDualThrustStrategy
from strategies.classic_turtle_strategy import ClassicTurtleStrategy
from strategies.classic_boll_channel_strategy import ClassicBollChannelStrategy
from strategies.classic_keltner_channel_strategy import ClassicKeltnerChannelStrategy
from strategies.classic_aberration_strategy import ClassicAberrationStrategy
from strategies.classic_keltner_channel_15m_strategy import ClassicKeltnerChannel15mStrategy
from strategies.classic_aberration_15m_strategy import ClassicAberration15mStrategy
from strategies.classic_keltner_channel_15m_v2_strategy import ClassicKeltnerChannel15mV2Strategy
from strategies.classic_aberration_15m_v2_strategy import ClassicAberration15mV2Strategy
from strategies.classic_keltner_channel_15m_v3_strategy import ClassicKeltnerChannel15mV3Strategy
from strategies.classic_aberration_15m_v3_strategy import ClassicAberration15mV3Strategy

EXCHANGE_MAP = {
    "rb": Exchange.SHFE,
    "hc": Exchange.SHFE,
    "m": Exchange.DCE,
    "MA": Exchange.CZCE,
    "TA": Exchange.CZCE,
}

CONTRACT_SPEC = {
    "rb": {"size": 10, "pricetick": 1.0},
    "hc": {"size": 10, "pricetick": 1.0},
    "m": {"size": 10, "pricetick": 1.0},
    "MA": {"size": 10, "pricetick": 1.0},
    "TA": {"size": 5, "pricetick": 2.0},
}

DEFAULT_RATE = 0.00003
DEFAULT_SLIPPAGE = 1.0
DEFAULT_CAPITAL = 200_000

STRATEGIES = {
    "DualThrust": ClassicDualThrustStrategy,
    "Turtle": ClassicTurtleStrategy,
    "BollChannel": ClassicBollChannelStrategy,
    "Keltner": ClassicKeltnerChannelStrategy,
    "Aberration": ClassicAberrationStrategy,
    "Keltner15m": ClassicKeltnerChannel15mStrategy,
    "Aberration15m": ClassicAberration15mStrategy,
    "Keltner15mV2": ClassicKeltnerChannel15mV2Strategy,
    "Aberration15mV2": ClassicAberration15mV2Strategy,
    "Keltner15mV3": ClassicKeltnerChannel15mV3Strategy,
    "Aberration15mV3": ClassicAberration15mV3Strategy,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="经典基线策略对照回测")
    parser.add_argument("--prefix", default="rb")
    parser.add_argument("--start", default="2021-07-01")
    parser.add_argument("--end", default="2026-06-30")
    parser.add_argument("--capital", type=float, default=DEFAULT_CAPITAL)
    parser.add_argument("--rate", type=float, default=DEFAULT_RATE)
    parser.add_argument("--slippage", type=float, default=DEFAULT_SLIPPAGE)
    parser.add_argument(
        "--only",
        default=None,
        help="逗号分隔，仅跑指定策略（如 Keltner,Aberration），默认跑全部",
    )
    return parser.parse_args()


def _round_trip_win_rate(engine: BacktestingEngine) -> tuple[int, float]:
    """按方向配对成交，粗略统计完整回合数与胜率（FIFO 净头寸法）。"""
    trades = sorted(engine.get_all_trades(), key=lambda t: t.datetime)
    size = float(engine.size)
    pos = 0.0
    open_price = 0.0
    rounds = 0
    wins = 0
    for trade in trades:
        signed_volume = trade.volume if trade.direction.value == "多" else -trade.volume
        if pos == 0:
            pos = signed_volume
            open_price = trade.price
        elif (pos > 0 and signed_volume < 0) or (pos < 0 and signed_volume > 0):
            pnl = (trade.price - open_price) * size if pos > 0 else (open_price - trade.price) * size
            rounds += 1
            if pnl > 0:
                wins += 1
            pos += signed_volume
            if pos != 0:
                open_price = trade.price
        else:
            pos += signed_volume
    win_rate = (wins / rounds * 100) if rounds else 0.0
    return rounds, win_rate


def run_one(strategy_cls, bars, rollover_events, vt_symbol, spec, start, end, args):
    engine = RolloverBacktestingEngine()
    engine.set_parameters(
        vt_symbol=vt_symbol,
        interval=Interval.MINUTE,
        start=start,
        end=end,
        rate=args.rate,
        slippage=args.slippage,
        size=spec["size"],
        pricetick=spec["pricetick"],
        capital=args.capital,
    )
    engine.history_data = bars
    engine.set_rollover_events(rollover_events)
    engine.add_strategy(strategy_cls, {})
    engine.run_backtesting()
    df = engine.calculate_result()
    stats = engine.calculate_statistics(df, output=False)
    rounds, win_rate = _round_trip_win_rate(engine)
    stats["round_trips"] = rounds
    stats["win_rate"] = win_rate
    stats["rollover_count"] = engine.rollover_stats.count
    stats["rollover_gap_pnl"] = engine.rollover_stats.total_gap_pnl
    stats["rollover_missed"] = len(engine.rollover_stats.missed_switches)
    return stats


def main() -> None:
    args = parse_args()
    prefix = args.prefix
    exchange = EXCHANGE_MAP[prefix]
    spec = CONTRACT_SPEC.get(prefix, {"size": 10, "pricetick": 1.0})
    vt_symbol = f"{prefix}.{exchange.value}"

    start = datetime.strptime(args.start, "%Y-%m-%d")
    end = datetime.strptime(args.end, "%Y-%m-%d")

    print(f"加载 {vt_symbol} 分月 raw 拼接（换月引擎）1m 数据 {start.date()} ~ {end.date()} ...")
    bars = load_stitched_raw_bars(prefix, exchange, start=start, end=end)
    if not bars:
        print("未加载到任何 K 线数据")
        sys.exit(1)
    actual_start = bars[0].datetime
    actual_end = bars[-1].datetime
    rollover_events = build_rollover_events(prefix, start=actual_start, end=actual_end)
    print(
        f"已加载 {len(bars)} 根 1m K 线 ({actual_start} ~ {actual_end})，"
        f"识别 {len(rollover_events)} 次换月切点\n"
    )

    active_strategies = STRATEGIES
    if args.only:
        wanted = {s.strip() for s in args.only.split(",")}
        active_strategies = {k: v for k, v in STRATEGIES.items() if k in wanted}

    results = {}
    for name, cls in active_strategies.items():
        print(f"{'='*60}\n回测: {name}\n{'='*60}")
        stats = run_one(cls, bars, rollover_events, vt_symbol, spec, actual_start, actual_end, args)
        results[name] = stats

    print(f"\n{'='*110}")
    print("经典基线策略对照汇总（含成本+换月引擎，rate={:.5f} slippage={}）".format(args.rate, args.slippage))
    print(f"{'='*110}")
    header = (
        f"{'策略':<12}{'完整回合':>8}{'总盈亏':>14}{'年化收益':>10}"
        f"{'最大回撤':>10}{'夏普比率':>10}{'总成交次数':>10}{'胜率':>8}{'换月次数':>8}{'换月PnL':>10}"
    )
    print(header)
    for name, stats in results.items():
        total_net_pnl = stats.get("total_net_pnl", 0)
        annual_return = stats.get("annual_return", 0)
        max_ddpercent = stats.get("max_ddpercent", 0)
        sharpe_ratio = stats.get("sharpe_ratio", 0)
        total_trade_count = stats.get("total_trade_count", 0)
        round_trips = stats.get("round_trips", 0)
        win_rate = stats.get("win_rate", 0)
        rollover_count = stats.get("rollover_count", 0)
        rollover_gap_pnl = stats.get("rollover_gap_pnl", 0)
        line = (
            f"{name:<12}{round_trips:>8}{total_net_pnl:>14,.0f}"
            f"{annual_return:>9.2f}%{max_ddpercent:>9.2f}%"
            f"{sharpe_ratio:>10.2f}{total_trade_count:>10}{win_rate:>7.1f}%"
            f"{rollover_count:>8}{rollover_gap_pnl:>10,.0f}"
        )
        print(line)
        missed = stats.get("rollover_missed", 0)
        if missed:
            print(f"  [WARN] {name}: {missed} 次换月切点未匹配到 RolloverEvent")


if __name__ == "__main__":
    main()
