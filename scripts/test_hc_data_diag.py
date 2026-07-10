# -*- coding: utf-8 -*-
"""hc vs rb TQ CbC 数据层诊断（一次性，stdout 摘要）。"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from vnpy.trader.constant import Exchange

from scripts.tq_rollover_data import build_rollover_events, build_stitched_raw_frame, load_stitched_raw_bars
from strategies.pa_cta.symbol_config import resolve_symbol_profile, resolve_tq_cbc_paths

START = datetime(2023, 5, 17)
END = datetime(2026, 5, 16)


def diag_prefix(prefix: str, symbol: str) -> dict:
    profile = resolve_symbol_profile(symbol, _ROOT)
    exchange = profile["exchange"]
    data_dir, file_stem = resolve_tq_cbc_paths(profile)

    df = build_stitched_raw_frame(file_stem)
    df = df[(df["dt_cst"] >= pd.Timestamp(START, tz="Asia/Shanghai")) &
            (df["dt_cst"] <= pd.Timestamp(END, tz="Asia/Shanghai"))].copy()

    bars = load_stitched_raw_bars(file_stem, exchange, symbol=symbol, start=START, end=END)
    events = build_rollover_events(file_stem, start=START, end=END)

    # 1m 缺口：相邻 bar > 3 分钟（夜盘跨段允许略大，>15min 记异常）
    dts = df["dt_cst"].sort_values()
    gaps = dts.diff().dt.total_seconds().fillna(0)
    big_gaps = df.loc[gaps > 900, ["dt_cst", "open", "close", "volume"]].copy()
    big_gaps["gap_min"] = gaps[gaps > 900].values / 60

    # OHLC 异常
    bad_hl = int((df["high"] < df["low"]).sum())
    bad_oc = int(((df["open"] > df["high"]) | (df["open"] < df["low"]) |
                  (df["close"] > df["high"]) | (df["close"] < df["low"])).sum())
    zero_vol = int((df["volume"] == 0).sum())
    dup_ts = int(df["dt_cst"].duplicated().sum())

    close = df["close"].astype(float)
    ret = close.pct_change()
    jump_5pct = int((ret.abs() > 0.05).sum())

    rollover_map = pd.read_parquet(data_dir / "rollover_map.parquet")
    cost_path = data_dir / "rollover_cost_detail.parquet"
    has_cost = cost_path.exists()
    cost_df = pd.read_parquet(cost_path) if has_cost else None

    ev_rows = []
    for ev in events:
        ev_rows.append({
            "switch": ev.switch_time.strftime("%Y-%m-%d"),
            "from_to": f"{ev.from_yymm}->{ev.to_yymm}",
            "old_close": ev.old_close,
            "new_open": ev.new_open,
            "price_diff": ev.price_diff,
            "slippage": ev.slippage_cost,
            "commission": ev.commission_cost,
        })

    # 连续合约 vs 拼接 close 抽样
    cont_path = data_dir / f"{file_stem}_continuous.parquet"
    cont_note = "missing"
    if cont_path.exists():
        cont = pd.read_parquet(cont_path)
        if "datetime" in cont.columns:
            cont["dt_cst"] = pd.to_datetime(cont["datetime"], utc=True).dt.tz_convert("Asia/Shanghai")
        elif "dt" in cont.columns:
            cont["dt_cst"] = pd.to_datetime(cont["dt"], utc=True).dt.tz_convert("Asia/Shanghai")
        cont = cont[(cont["dt_cst"] >= pd.Timestamp(START, tz="Asia/Shanghai")) &
                    (cont["dt_cst"] <= pd.Timestamp(END, tz="Asia/Shanghai"))]
        cont_note = f"rows={len(cont)} close_range={cont['close'].min():.0f}~{cont['close'].max():.0f}"

    return {
        "prefix": prefix,
        "bars": len(bars),
        "df_rows": len(df),
        "date_range": f"{df['dt_cst'].min()} ~ {df['dt_cst'].max()}",
        "close_range": f"{close.min():.0f} ~ {close.max():.0f}",
        "zero_vol": zero_vol,
        "zero_vol_pct": zero_vol / len(df) * 100 if len(df) else 0,
        "dup_ts": dup_ts,
        "bad_hl": bad_hl,
        "bad_oc": bad_oc,
        "gaps_gt15m": len(big_gaps),
        "jump_5pct": jump_5pct,
        "rollover_events": len(events),
        "rollover_map_rows": len(rollover_map),
        "has_cost_detail": has_cost,
        "cost_slippage_sum": float(cost_df["slippage_cost"].sum()) if cost_df is not None else None,
        "events": ev_rows,
        "big_gaps_sample": big_gaps.head(5).to_string(index=False) if len(big_gaps) else "",
        "cont": cont_note,
    }


def main() -> None:
    for sym in ("hc", "rb"):
        d = diag_prefix(sym, sym)
        print(f"\n{'='*60}\n{sym.upper()} 数据诊断 [{START.date()} ~ {END.date()}]")
        print(f"  拼接 bar 数: {d['bars']}  日期: {d['date_range']}")
        print(f"  close 区间: {d['close_range']}")
        print(f"  volume=0: {d['zero_vol']} ({d['zero_vol_pct']:.1f}%)  dup_ts: {d['dup_ts']}")
        print(f"  OHLC 异常 high<low: {d['bad_hl']}  O/C 越界: {d['bad_oc']}")
        print(f"  相邻缺口>15min: {d['gaps_gt15m']}  单bar涨跌>5%: {d['jump_5pct']}")
        print(f"  rollover_map: {d['rollover_map_rows']}  回测窗 events: {d['rollover_events']}")
        print(f"  cost_detail: {d['has_cost_detail']}  slippage_sum={d['cost_slippage_sum']}")
        print(f"  continuous: {d['cont']}")
        print("  换月切点:")
        for ev in d["events"]:
            print(
                f"    {ev['switch']} {ev['from_to']:12s} "
                f"diff={ev['price_diff']:+.0f} slip={ev['slippage']:.2f} comm={ev['commission']:.2f}"
            )
        if d["big_gaps_sample"]:
            print("  大缺口样例(前5):")
            print(d["big_gaps_sample"])


if __name__ == "__main__":
    main()
