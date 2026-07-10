# -*- coding: utf-8 -*-
"""从 vn.py 回测成交记录配对 round-trip，并输出极值盈亏统计。"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Iterable

from vnpy.trader.constant import Direction, Offset

if TYPE_CHECKING:
    from vnpy.trader.object import TradeData


@dataclass
class RoundTripTrade:
    """一笔完整开平交易。"""

    entry_time: datetime
    exit_time: datetime
    direction: str
    entry_price: float
    exit_price: float
    volume: float
    gross_pnl: float
    net_pnl: float
    pnl_pct: float
    capital_pct: float
    # E3 归因扩展字段（可选，来自策略内部 _trade_log）
    setup: str = ""
    market_context: str = ""
    always_in: str = ""
    trend_age_bars: int = 0
    entry_atr: float = 0.0
    atr_ratio: float = 0.0
    mfe_ticks: float = 0.0
    mae_ticks: float = 0.0
    holding_minutes: float = 0.0
    exit_reason: str = ""


@dataclass
class OpenPositionSnapshot:
    """回测结束时仍未平仓的净持仓（用于解释 total_net_pnl 与 round-trip 差异）。"""

    direction: str
    volume: float
    avg_entry_price: float
    first_entry_time: datetime
    last_entry_time: datetime
    mark_price: float
    mark_time: datetime
    gross_unrealized: float
    capital_pct: float


def pair_round_trips(
    trades: Iterable[TradeData],
    *,
    size: float,
    rate: float,
    slippage: float,
    capital: float,
) -> list[RoundTripTrade]:
    """按净持仓归零配对 round-trip（适配同秒多笔 OPEN 成交）。"""
    sorted_trades = sorted(trades, key=lambda t: t.datetime)
    pos = 0.0
    entry_side = 0
    entry_dt: datetime | None = None
    entry_notional = 0.0
    entry_volume = 0.0
    entry_cost = 0.0
    round_trips: list[RoundTripTrade] = []

    for trade in sorted_trades:
        leg_cost = _trade_cost(trade, size, rate, slippage)
        delta = trade.volume if trade.direction == Direction.LONG else -trade.volume

        if trade.offset == Offset.OPEN:
            if abs(pos) < 1e-9:
                entry_side = 1 if delta > 0 else -1
                entry_dt = trade.datetime
                entry_notional = trade.price * trade.volume
                entry_volume = trade.volume
                entry_cost = leg_cost
            elif (pos > 0 and delta > 0) or (pos < 0 and delta < 0):
                entry_notional += trade.price * trade.volume
                entry_volume += trade.volume
                entry_cost += leg_cost
            pos += delta
            continue

        if trade.offset != Offset.CLOSE:
            continue

        pos += delta
        exit_cost = leg_cost

        if abs(pos) >= 1e-9 or entry_volume <= 0 or entry_dt is None:
            continue

        avg_entry = entry_notional / entry_volume
        volume = entry_volume
        if entry_side > 0:
            gross = (trade.price - avg_entry) * volume * size
            direction_label = "多"
        else:
            gross = (avg_entry - trade.price) * volume * size
            direction_label = "空"

        net = gross - entry_cost - exit_cost
        notional = avg_entry * volume * size
        pnl_pct = (net / notional * 100.0) if notional > 0 else 0.0
        cap_pct = (net / capital * 100.0) if capital > 0 else 0.0

        round_trips.append(
            RoundTripTrade(
                entry_time=entry_dt,
                exit_time=trade.datetime,
                direction=direction_label,
                entry_price=avg_entry,
                exit_price=trade.price,
                volume=volume,
                gross_pnl=gross,
                net_pnl=net,
                pnl_pct=pnl_pct,
                capital_pct=cap_pct,
            )
        )
        entry_side = 0
        entry_dt = None
        entry_notional = 0.0
        entry_volume = 0.0
        entry_cost = 0.0

    return round_trips


def snapshot_open_position_at_end(
    trades: Iterable[TradeData],
    *,
    size: float,
    mark_price: float,
    mark_time: datetime,
    capital: float,
) -> OpenPositionSnapshot | None:
    """
    按与 pair_round_trips 相同的持仓记账，读取回测结束时的未平净仓。
    gross_unrealized 为按 mark_price 计算的毛利（未扣平仓侧成本）。
    """
    sorted_trades = sorted(trades, key=lambda t: t.datetime)
    pos = 0.0
    entry_side = 0
    first_entry_dt: datetime | None = None
    last_entry_dt: datetime | None = None
    entry_notional = 0.0
    entry_volume = 0.0

    for trade in sorted_trades:
        delta = trade.volume if trade.direction == Direction.LONG else -trade.volume

        if trade.offset == Offset.OPEN:
            if abs(pos) < 1e-9:
                entry_side = 1 if delta > 0 else -1
                first_entry_dt = trade.datetime
                entry_notional = trade.price * trade.volume
                entry_volume = trade.volume
            elif (pos > 0 and delta > 0) or (pos < 0 and delta < 0):
                entry_notional += trade.price * trade.volume
                entry_volume += trade.volume
            last_entry_dt = trade.datetime
            pos += delta
            continue

        if trade.offset != Offset.CLOSE:
            continue

        pos += delta
        if abs(pos) < 1e-9:
            entry_side = 0
            first_entry_dt = None
            last_entry_dt = None
            entry_notional = 0.0
            entry_volume = 0.0

    if abs(pos) < 1e-9 or entry_volume <= 0 or first_entry_dt is None:
        return None

    avg_entry = entry_notional / entry_volume
    volume = abs(pos)
    if entry_side > 0:
        gross = (mark_price - avg_entry) * volume * size
        direction_label = "多"
    else:
        gross = (avg_entry - mark_price) * volume * size
        direction_label = "空"

    notional = avg_entry * volume * size
    pnl_pct = (gross / notional * 100.0) if notional > 0 else 0.0
    cap_pct = (gross / capital * 100.0) if capital > 0 else 0.0

    return OpenPositionSnapshot(
        direction=direction_label,
        volume=volume,
        avg_entry_price=avg_entry,
        first_entry_time=first_entry_dt,
        last_entry_time=last_entry_dt or first_entry_dt,
        mark_price=mark_price,
        mark_time=mark_time,
        gross_unrealized=gross,
        capital_pct=cap_pct,
    )


def print_open_position_report(
    snapshot: OpenPositionSnapshot | None,
    *,
    total_net_pnl: float | None,
    closed_rt_net_pnl: float,
    initial_capital: float,
) -> None:
    """打印期末持仓与盈亏构成（闭环 RT 与总净盈亏的对照）。"""
    print("\n----- 期末持仓 / 盈亏构成 -----")
    if snapshot is None:
        print("期末净持仓: 0（全部平仓或未成交）")
        if total_net_pnl is not None and closed_rt_net_pnl is not None:
            print(f"已平仓 round-trip 净盈亏合计: {closed_rt_net_pnl:,.2f}")
            print(f"回测总净盈亏: {total_net_pnl:,.2f}")
        return

    entry_ts = snapshot.first_entry_time.strftime("%Y-%m-%d %H:%M")
    last_ts = snapshot.last_entry_time.strftime("%Y-%m-%d %H:%M")
    mark_ts = snapshot.mark_time.strftime("%Y-%m-%d %H:%M")
    print(
        f"期末净持仓: {snapshot.direction} {snapshot.volume:.0f} 手  "
        f"均价 {snapshot.avg_entry_price:.1f}  "
        f"首次开仓 {entry_ts}  末次加仓 {last_ts}"
    )
    print(
        f"盯市价格: {snapshot.mark_price:.1f} ({mark_ts})  "
        f"浮盈(毛利): {snapshot.gross_unrealized:,.2f}  "
        f"占资金 {snapshot.capital_pct:.2f}%"
    )
    print(f"已平仓 round-trip 净盈亏合计: {closed_rt_net_pnl:,.2f}")
    if total_net_pnl is not None:
        residual = total_net_pnl - closed_rt_net_pnl
        print(
            f"回测总净盈亏: {total_net_pnl:,.2f}  "
            f"≈ 已平仓 {closed_rt_net_pnl:,.2f} + 未平仓贡献约 {residual:,.2f}"
        )
        print(
            "说明: 未平仓贡献含开仓成本、盯市盈亏及回测结束强平计价；"
            "与上表「浮盈(毛利)」口径不同，勿与 round-trip 胜率直接对比。"
        )


def _trade_cost(trade: TradeData, size: float, rate: float, slippage: float) -> float:
    turnover = trade.price * trade.volume * size
    return turnover * rate + trade.volume * size * slippage


def summarize_round_trips(round_trips: list[RoundTripTrade]) -> dict[str, float]:
    """汇总 round-trip 胜率、笔均盈亏比、利润因子与持有时间统计。"""
    total = len(round_trips)
    if total == 0:
        base = {
            "total": 0,
            "wins": 0,
            "losses": 0,
            "breakeven": 0,
            "win_rate": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "payoff_ratio": 0.0,
            "profit_factor": 0.0,
        }
        holding_stats = analyze_holding_times(round_trips)
        return {**base, **holding_stats}

    wins = [t for t in round_trips if t.net_pnl > 0]
    losses = [t for t in round_trips if t.net_pnl < 0]
    breakeven = total - len(wins) - len(losses)
    gross_profit = sum(t.net_pnl for t in wins)
    gross_loss = abs(sum(t.net_pnl for t in losses))
    avg_win = gross_profit / len(wins) if wins else 0.0
    avg_loss = gross_loss / len(losses) if losses else 0.0

    base = {
        "total": float(total),
        "wins": float(len(wins)),
        "losses": float(len(losses)),
        "breakeven": float(breakeven),
        "win_rate": len(wins) / total * 100.0,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "payoff_ratio": avg_win / avg_loss if avg_loss > 0 else 0.0,
        "profit_factor": gross_profit / gross_loss if gross_loss > 0 else 0.0,
    }
    holding_stats = analyze_holding_times(round_trips)
    return {**base, **holding_stats}


def print_round_trip_summary(
    round_trips: list[RoundTripTrade],
    *,
    title: str = "Round-trip 汇总",
) -> None:
    """打印胜率、笔均盈亏比（均盈/均亏）与持有时间统计。"""
    summary = summarize_round_trips(round_trips)
    print(f"\n----- {title} -----")
    if summary["total"] == 0:
        print("无完整开平配对记录")
        return

    print(f"完整交易: {int(summary['total'])} 笔")
    print(
        f"胜率: {summary['win_rate']:.2f}%  "
        f"(盈 {int(summary['wins'])} / 亏 {int(summary['losses'])} / "
        f"平 {int(summary['breakeven'])})"
    )
    print(f"平均盈利: {summary['avg_win']:,.2f}  平均亏损: {summary['avg_loss']:,.2f}")
    payoff = summary["payoff_ratio"]
    payoff_text = f"{payoff:.2f}" if payoff > 0 else "N/A(无亏损)"
    print(f"笔均盈亏比(均盈/均亏): {payoff_text}")
    
    print("\n----- 持有时间统计 -----")
    print(f"平均持有: {summary['avg_holding_hours']:.1f} 小时")
    print(f"中位数持有: {summary['median_holding_hours']:.1f} 小时")
    print(f"最长持有: {summary['max_holding_hours']:.1f} 小时")
    print(f"最短持有: {summary['min_holding_hours']:.1f} 小时")
    
    if summary['avg_holding_hours_long'] > 0 or summary['avg_holding_hours_short'] > 0:
        print(f"多头平均持有: {summary['avg_holding_hours_long']:.1f} 小时")
        print(f"空头平均持有: {summary['avg_holding_hours_short']:.1f} 小时")
    
    if summary['avg_holding_hours_win'] > 0 or summary['avg_holding_hours_loss'] > 0:
        print(f"盈利交易平均持有: {summary['avg_holding_hours_win']:.1f} 小时")
        print(f"亏损交易平均持有: {summary['avg_holding_hours_loss']:.1f} 小时")


def print_top_round_trips(
    round_trips: list[RoundTripTrade],
    *,
    top_n: int = 5,
    title: str = "极值交易统计",
) -> None:
    """打印盈利/亏损最大的各 top_n 笔（含盈亏百分比）。"""
    if not round_trips:
        print(f"\n----- {title} -----")
        print("无完整开平配对记录")
        return

    print_round_trip_summary(round_trips, title="Round-trip 汇总")

    winners = sorted(
        [t for t in round_trips if t.net_pnl > 0],
        key=lambda t: t.net_pnl,
        reverse=True,
    )[:top_n]
    losers = sorted(
        [t for t in round_trips if t.net_pnl < 0],
        key=lambda t: t.net_pnl,
    )[:top_n]

    print(f"\n----- {title}（共 {len(round_trips)} 笔 round-trip）-----")
    print(
        "盈亏% = 净盈亏 / (开仓价×乘数×手数)；"
        "资金% = 净盈亏 / 初始资金"
    )

    print(f"\n【盈利 Top {len(winners)}】")
    _print_trip_table(winners)

    print(f"\n【亏损 Top {len(losers)}】")
    _print_trip_table(losers)


def analyze_holding_times(round_trips: list[RoundTripTrade]) -> dict:
    """分析 round-trip 交易的持有时间。"""
    total = len(round_trips)
    if total == 0:
        return {
            "avg_holding_hours": 0.0,
            "median_holding_hours": 0.0,
            "max_holding_hours": 0.0,
            "min_holding_hours": 0.0,
            "avg_holding_hours_long": 0.0,
            "avg_holding_hours_short": 0.0,
            "avg_holding_hours_win": 0.0,
            "avg_holding_hours_loss": 0.0,
        }

    holding_hours_list = []
    holding_hours_long = []
    holding_hours_short = []
    holding_hours_win = []
    holding_hours_loss = []

    for trip in round_trips:
        duration = trip.exit_time - trip.entry_time
        hours = duration.total_seconds() / 3600.0
        holding_hours_list.append(hours)

        if trip.direction == "多":
            holding_hours_long.append(hours)
        else:
            holding_hours_short.append(hours)

        if trip.net_pnl > 0:
            holding_hours_win.append(hours)
        elif trip.net_pnl < 0:
            holding_hours_loss.append(hours)

    def safe_avg(data):
        return statistics.mean(data) if data else 0.0

    def safe_median(data):
        return statistics.median(data) if data else 0.0

    return {
        "avg_holding_hours": safe_avg(holding_hours_list),
        "median_holding_hours": safe_median(holding_hours_list),
        "max_holding_hours": max(holding_hours_list) if holding_hours_list else 0.0,
        "min_holding_hours": min(holding_hours_list) if holding_hours_list else 0.0,
        "avg_holding_hours_long": safe_avg(holding_hours_long),
        "avg_holding_hours_short": safe_avg(holding_hours_short),
        "avg_holding_hours_win": safe_avg(holding_hours_win),
        "avg_holding_hours_loss": safe_avg(holding_hours_loss),
    }


def _print_trip_table(trips: list[RoundTripTrade]) -> None:
    header = (
        f"{'#':>2}  {'方向':^4}  {'开仓':^16}  {'平仓':^16}  "
        f"{'开价':>7}  {'平价':>7}  {'净盈亏':>9}  {'盈亏%':>8}  {'资金%':>8}  {'持有(h)':>8}"
    )
    print(header)
    print("-" * 112)

    for idx, trip in enumerate(trips, 1):
        entry_ts = trip.entry_time.strftime("%Y-%m-%d %H:%M")
        exit_ts = trip.exit_time.strftime("%Y-%m-%d %H:%M")
        duration = trip.exit_time - trip.entry_time
        holding_hours = duration.total_seconds() / 3600.0
        print(
            f"{idx:>2}  {trip.direction:^4}  {entry_ts:^16}  {exit_ts:^16}  "
            f"{trip.entry_price:>7.1f}  {trip.exit_price:>7.1f}  "
            f"{trip.net_pnl:>9.2f}  {trip.pnl_pct:>7.2f}%  {trip.capital_pct:>7.3f}%  "
            f"{holding_hours:>8.1f}"
        )
