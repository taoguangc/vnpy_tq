"""商品期货离线回测入口脚本。

数据链路: 分月 raw(data/tq) + rollover_map -> CbC 拼接 -> scripts/tq_data_loader.py -> vnpy BarData

用法:
    .venv/Scripts/python.exe scripts/run_backtest.py
    .venv/Scripts/python.exe scripts/run_backtest.py --prefix rb --start 2023-07-01 --end 2026-06-30

默认策略为 strategies/template_strategy.py 中的空骨架 TemplateStrategy，
仅用于验证回测链路能跑通；实盘前请替换为自己实现的策略类。
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from vnpy.trader.constant import Exchange, Interval
from vnpy_ctastrategy.backtesting import BacktestingEngine

from scripts.tq_data_loader import load_bars_from_tq
from strategies.template_strategy import TemplateStrategy

# 品种代码 -> 交易所映射（与 tools/build_rollover_map.py 的 SYMBOL_CONFIG 对齐）
EXCHANGE_MAP = {
    "rb": Exchange.SHFE,
    "hc": Exchange.SHFE,
    "au": Exchange.SHFE,
    "ag": Exchange.SHFE,
    "al": Exchange.SHFE,
    "zn": Exchange.SHFE,
    "pb": Exchange.SHFE,
    "sn": Exchange.SHFE,
    "fu": Exchange.SHFE,
    "m": Exchange.DCE,
    "c": Exchange.DCE,
    "p": Exchange.DCE,
    "i": Exchange.DCE,
    "j": Exchange.DCE,
    "jm": Exchange.DCE,
    "v": Exchange.DCE,
    "rm": Exchange.DCE,
    "MA": Exchange.CZCE,
    "TA": Exchange.CZCE,
    "SA": Exchange.CZCE,
    "FG": Exchange.CZCE,
    "SR": Exchange.CZCE,
    "RM": Exchange.CZCE,
}

# 品种合约乘数 / 最小变动价位（示例值，正式使用前请核对交易所最新规则）
CONTRACT_SPEC = {
    "rb": {"size": 10, "pricetick": 1.0},
    "hc": {"size": 10, "pricetick": 1.0},
    "m": {"size": 10, "pricetick": 1.0},
    "MA": {"size": 10, "pricetick": 1.0},
    "TA": {"size": 5, "pricetick": 2.0},
}

DEFAULT_PREFIX = "rb"
DEFAULT_RATE = 1e-4       # 手续费率（示例值）
DEFAULT_SLIPPAGE = 1.0    # 滑点（价格单位）
DEFAULT_CAPITAL = 200_000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="商品期货离线回测（vnpy_ctastrategy + TQSDK 原始无复权数据）")
    parser.add_argument("--prefix", default=DEFAULT_PREFIX, help="品种代码，如 rb, hc, m, MA, TA")
    parser.add_argument("--start", default="2023-07-01", help="回测起始日期 YYYY-MM-DD")
    parser.add_argument("--end", default="2026-06-30", help="回测结束日期 YYYY-MM-DD")
    parser.add_argument("--capital", type=float, default=DEFAULT_CAPITAL, help="初始资金")
    parser.add_argument("--rate", type=float, default=DEFAULT_RATE, help="手续费率")
    parser.add_argument("--slippage", type=float, default=DEFAULT_SLIPPAGE, help="滑点（价格单位）")
    parser.add_argument("--no-chart", action="store_true", help="不弹出净值曲线图")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    prefix = args.prefix

    if prefix not in EXCHANGE_MAP:
        print(f"未配置品种 {prefix} 的交易所映射，请在 EXCHANGE_MAP 中补充")
        sys.exit(1)

    exchange = EXCHANGE_MAP[prefix]
    spec = CONTRACT_SPEC.get(prefix, {"size": 10, "pricetick": 1.0})
    vt_symbol = f"{prefix}.{exchange.value}"

    start = datetime.strptime(args.start, "%Y-%m-%d")
    end = datetime.strptime(args.end, "%Y-%m-%d") if args.end else None

    print(f"{'='*60}")
    print(f"商品期货离线回测: {vt_symbol}")
    print(f"区间: {start.date()} ~ {end.date() if end else '数据末尾'}")
    print(f"策略: {TemplateStrategy.__name__}")
    print(f"{'='*60}")

    bars = load_bars_from_tq(prefix, exchange, start=start, end=end)
    if not bars:
        print("未加载到任何 K 线数据，请先运行 tools/download_rb_monthly.py 与 tools/build_rollover_map.py")
        sys.exit(1)

    actual_start = bars[0].datetime
    actual_end = bars[-1].datetime
    print(f"已加载 {len(bars)} 根原始无复权 1 分钟 K 线 ({actual_start} ~ {actual_end})")

    engine = BacktestingEngine()
    engine.set_parameters(
        vt_symbol=vt_symbol,
        interval=Interval.MINUTE,
        start=actual_start,
        end=actual_end,
        rate=args.rate,
        slippage=args.slippage,
        size=spec["size"],
        pricetick=spec["pricetick"],
        capital=args.capital,
    )
    engine.history_data = bars

    engine.add_strategy(TemplateStrategy, {})

    engine.run_backtesting()
    df = engine.calculate_result()
    stats = engine.calculate_statistics(df)

    if not args.no_chart and df is not None and not df.empty:
        engine.show_chart(df)

    print(f"\n{'='*60}")
    print("回测完成")
    print(f"{'='*60}")
    return stats


if __name__ == "__main__":
    main()
