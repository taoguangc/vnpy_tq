"""换月映射表生成 + 移仓成本明细（支持多品种）。

功能:
  1. 分析分月合约数据，自动检测换月时间点（主力 OI 链 + whipsaw 过滤）
  2. 按品种交割月白名单（tools/rollover_rules.py）过滤候选合约，如 rb 仅 1/5/10
  3. 生成换月映射表（Parquet）；切点执行时刻 21:00 CST（CbC 回测用）
  4. 生成 rollover_cost_detail.parquet（移仓滑点/手续费，供 RolloverBacktestingEngine）
  5. 写入 manifest.json derived 段

回测主路径为分月 raw CbC 拼接（无复权），不写 *_continuous.parquet。

使用方法:
    .\\.venv\\Scripts\\python.exe tools\\build_rollover_map.py -s rb
    .\\.venv\\Scripts\\python.exe tools\\build_rollover_map.py -s rb --map-only
    .\\.venv\\Scripts\\python.exe scripts\\compare_rollover_map_rules.py -s rb
"""
from __future__ import annotations

import json
import os
import sys
import argparse
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pandas as pd
import numpy as np

from tools.dominant_windows import (
    build_dominant_chain,
    build_dominant_windows,
    save_dominant_windows,
)
from tools.oi_daily_io import load_oi_daily_dict
from tools.rollover_rules import (
    ROLLOVER_CONFIRM_DAYS,
    ROLLOVER_SWITCH_TIME,
    allowed_months_for_symbol,
    contract_year_from_yymm,
    delivery_month_from_yymm,
    effective_yymm_len,
    filter_df_dict_by_delivery_months,
)
from tools.tq_parquet_io import (
    SESSION_NOTE,
    VERIFY_OHLCV_COLUMNS,
    is_monthly_contract_file,
    load_monthly_parquet,
)

MANIFEST_FILE = "manifest.json"

# ========== 品种配置 ==========
SYMBOL_CONFIG = {
    "rb": {
        "exchange": "SHFE",
        "prefix": "rb",
        "volume_multiple": 10,
        "tick_value": 1.0,
        "commission_per_lot": 3.0,
        "slippage_ticks": 1,
        "yymm_len": 4,
        "name": "螺纹钢",
    },
    "m": {
        "exchange": "DCE",
        "prefix": "m",
        "volume_multiple": 10,
        "tick_value": 1.0,
        "commission_per_lot": 2.0,
        "slippage_ticks": 1,
        "yymm_len": 4,
        "name": "豆粕",
    },
    "MA": {
        "exchange": "CZCE",
        "prefix": "MA",
        "volume_multiple": 10,
        "tick_value": 1.0,
        "commission_per_lot": 2.0,
        "slippage_ticks": 1,
        "yymm_len": 4,
        "name": "甲醇",
    },
    "TA": {
        "exchange": "CZCE",
        "prefix": "TA",
        "volume_multiple": 5,
        "tick_value": 2.0,
        "commission_per_lot": 2.0,
        "slippage_ticks": 1,
        "yymm_len": 4,
        "name": "PTA",
    },
    "rm": {
        "exchange": "DCE",
        "prefix": "rm",
        "volume_multiple": 10,
        "tick_value": 1.0,
        "commission_per_lot": 2.0,
        "slippage_ticks": 1,
        "yymm_len": 4,
        "name": "菜粕",
    },
    "SA": {
        "exchange": "CZCE",
        "prefix": "SA",
        "volume_multiple": 20,
        "tick_value": 1.0,
        "commission_per_lot": 2.0,
        "slippage_ticks": 1,
        "yymm_len": 3,
        "name": "纯碱",
    },
    "ag": {
        "exchange": "SHFE",
        "prefix": "ag",
        "volume_multiple": 15,
        "tick_value": 1.0,
        "commission_per_lot": 3.0,
        "slippage_ticks": 1,
        "yymm_len": 4,
        "name": "白银",
    },
    "i": {
        "exchange": "DCE",
        "prefix": "i",
        "volume_multiple": 100,
        "tick_value": 0.5,
        "commission_per_lot": 2.0,
        "slippage_ticks": 1,
        "yymm_len": 4,
        "name": "铁矿石",
    },
    "c": {
        "exchange": "DCE",
        "prefix": "c",
        "volume_multiple": 10,
        "tick_value": 1.0,
        "commission_per_lot": 2.0,
        "slippage_ticks": 1,
        "yymm_len": 4,
        "name": "玉米",
    },
    "p": {
        "exchange": "DCE",
        "prefix": "p",
        "volume_multiple": 10,
        "tick_value": 1.0,
        "commission_per_lot": 2.0,
        "slippage_ticks": 1,
        "yymm_len": 4,
        "name": "棕榈油",
    },
    "y": {
        "exchange": "DCE",
        "prefix": "y",
        "volume_multiple": 10,
        "tick_value": 2.0,
        "commission_per_lot": 2.0,
        "slippage_ticks": 1,
        "yymm_len": 4,
        "name": "豆油",
    },
    "l": {
        "exchange": "DCE",
        "prefix": "l",
        "volume_multiple": 5,
        "tick_value": 1.0,
        "commission_per_lot": 2.0,
        "slippage_ticks": 1,
        "yymm_len": 4,
        "name": "塑料",
    },
    "SR": {
        "exchange": "CZCE",
        "prefix": "SR",
        "volume_multiple": 10,
        "tick_value": 1.0,
        "commission_per_lot": 2.0,
        "slippage_ticks": 1,
        "yymm_len": 3,
        "name": "白糖",
    },
    "fu": {
        "exchange": "SHFE",
        "prefix": "fu",
        "volume_multiple": 50,
        "tick_value": 0.5,
        "commission_per_lot": 3.0,
        "slippage_ticks": 1,
        "yymm_len": 4,
        "name": "燃料油",
    },
    "FG": {
        "exchange": "CZCE",
        "prefix": "FG",
        "volume_multiple": 20,
        "tick_value": 1.0,
        "commission_per_lot": 2.0,
        "slippage_ticks": 1,
        "yymm_len": 3,
        "name": "玻璃",
    },
    "hc": {
        "exchange": "SHFE",
        "prefix": "hc",
        "volume_multiple": 10,
        "tick_value": 1.0,
        "commission_per_lot": 3.0,
        "slippage_ticks": 1,
        "yymm_len": 4,
        "name": "热轧卷板",
    },
    "au": {
        "exchange": "SHFE",
        "prefix": "au",
        "volume_multiple": 1000,
        "tick_value": 0.02,
        "commission_per_lot": 10.0,
        "slippage_ticks": 1,
        "yymm_len": 4,
        "name": "黄金",
    },
    "sn": {
        "exchange": "SHFE",
        "prefix": "sn",
        "volume_multiple": 1,
        "tick_value": 10.0,
        "commission_per_lot": 3.0,
        "slippage_ticks": 1,
        "yymm_len": 4,
        "name": "沪锡",
    },
    "al": {
        "exchange": "SHFE",
        "prefix": "al",
        "volume_multiple": 5,
        "tick_value": 5.0,
        "commission_per_lot": 3.0,
        "slippage_ticks": 1,
        "yymm_len": 4,
        "name": "沪铝",
    },
    "zn": {
        "exchange": "SHFE",
        "prefix": "zn",
        "volume_multiple": 5,
        "tick_value": 5.0,
        "commission_per_lot": 3.0,
        "slippage_ticks": 1,
        "yymm_len": 4,
        "name": "沪锌",
    },
    "jm": {
        "exchange": "DCE",
        "prefix": "jm",
        "volume_multiple": 60,
        "tick_value": 0.5,
        "commission_per_lot": 5.0,
        "slippage_ticks": 1,
        "yymm_len": 4,
        "name": "焦煤",
    },
    "j": {
        "exchange": "DCE",
        "prefix": "j",
        "volume_multiple": 100,
        "tick_value": 0.5,
        "commission_per_lot": 5.0,
        "slippage_ticks": 1,
        "yymm_len": 4,
        "name": "焦炭",
    },
    "pb": {
        "exchange": "SHFE",
        "prefix": "pb",
        "volume_multiple": 5,
        "tick_value": 5.0,
        "commission_per_lot": 3.0,
        "slippage_ticks": 1,
        "yymm_len": 4,
        "name": "沪铅",
    },
    "RM": {
        "exchange": "CZCE",
        "prefix": "RM",
        "volume_multiple": 10,
        "tick_value": 1.0,
        "commission_per_lot": 1.5,
        "slippage_ticks": 1,
        "yymm_len": 3,
        "name": "菜粕",
    },
    "v": {
        "exchange": "DCE",
        "prefix": "v",
        "volume_multiple": 5,
        "tick_value": 1.0,
        "commission_per_lot": 2.0,
        "slippage_ticks": 1,
        "yymm_len": 4,
        "name": "聚氯乙烯",
    },
}

ROLLOVER_DAYS = 5
ROLLOVER_CURVE = "linear"
ROLLOVER_METHOD = "dominant_oi"
DOMINANT_OI_PARAMS = {
    "min_oi_ratio": 0.05,
    "min_confirmation_days": ROLLOVER_CONFIRM_DAYS,
    "exclude_delivery_month": True,
    "whipsaw_min_gap_days": 45,
}


def _filter_whipsaw_events(
    events: list[dict],
    first_dominant: str | None,
    min_gap_days: int,
) -> tuple[list[dict], int]:
    """去掉短间隔 A→B 后又 B→A 的回切；并忽略与已确认主力不一致的噪声切换。

    检测到回切时撤销上一笔换月（pop），避免 effective 仍停在中间合约导致后续链条断裂。
    """
    if not events or not first_dominant:
        return events, 0

    filtered: list[dict] = []
    effective = first_dominant
    skipped = 0

    for ev in events:
        if ev["from_yymm"] != effective:
            skipped += 1
            continue

        if filtered:
            last = filtered[-1]
            gap = (ev["rollover_date"] - last["rollover_date"]).days
            if (
                gap <= min_gap_days
                and ev["to_yymm"] == last["from_yymm"]
                and ev["from_yymm"] == last["to_yymm"]
            ):
                filtered.pop()
                effective = last["from_yymm"]
                skipped += 2
                continue

        filtered.append(ev)
        effective = ev["to_yymm"]

    return filtered, skipped

CONFIG: dict
DATA_DIR: str


def _configure(symbol_key: str) -> None:
    global CONFIG, DATA_DIR
    resolved = symbol_key
    if symbol_key not in SYMBOL_CONFIG:
        folded = symbol_key.casefold()
        matches = [k for k in SYMBOL_CONFIG if k.casefold() == folded]
        if not matches:
            print(f"错误: 不支持的品种 '{symbol_key}'")
            print(f"支持的品种: {', '.join(SYMBOL_CONFIG.keys())}")
            sys.exit(1)
        # 郑商所键优先全大写（MA/RM）；否则取首个
        resolved = next((k for k in matches if k.isupper()), matches[0])
        if resolved != symbol_key:
            print(f"  品种键规范化: {symbol_key!r} → {resolved!r}")
    CONFIG = SYMBOL_CONFIG[resolved].copy()
    allowed = allowed_months_for_symbol(resolved)
    CONFIG["allowed_delivery_months"] = allowed
    CONFIG["rollover_switch_time"] = ROLLOVER_SWITCH_TIME
    # 数据目录跟落盘 prefix（CZCE 为大写），不跟 CLI 原样
    DATA_DIR = os.path.join(ROOT, "data", "tq", CONFIG["prefix"])


def parse_contract_code(filename: str) -> str | None:
    prefix = CONFIG["prefix"]
    yymm_len = CONFIG["yymm_len"]
    if is_monthly_contract_file(filename, prefix, yymm_len):
        return filename[len(prefix) + 1 : -8]
    return None


def load_contract_data(yymm: str) -> pd.DataFrame | None:
    prefix = CONFIG["prefix"]
    filepath = os.path.join(DATA_DIR, f"{prefix}_{yymm}.parquet")
    return load_monthly_parquet(filepath, yymm=yymm)


def _rollover_event_date(record: dict | pd.Series) -> date:
    rd = record["rollover_date"]
    if isinstance(rd, pd.Timestamp):
        return rd.date()
    if isinstance(rd, datetime):
        return rd.date()
    return rd


def _ordered_rollover_events(rollover_map: pd.DataFrame) -> list[dict]:
    """与 dominant_chain 一一对应：events[i] 为 chain[i] -> chain[i+1]。"""
    if len(rollover_map) == 0:
        return []
    df = rollover_map.sort_values("rollover_date").reset_index(drop=True)
    return df.to_dict("records")


def get_rollover_weights(days: int, curve: str = "linear") -> np.ndarray:
    if curve == "linear":
        return np.ones(days) / days
    if curve == "s_curve":
        t = np.arange(days) / (days - 1)
        weights = 1 / (1 + np.exp(-8 * (t - 0.5)))
        return weights / weights.sum()
    return np.ones(days) / days


def simulate_rollover_cost(
    from_df: pd.DataFrame,
    to_df: pd.DataFrame,
    rollover_date: date,
    days: int = ROLLOVER_DAYS,
) -> dict:
    volume_multiple = CONFIG["volume_multiple"]
    tick_value = CONFIG["tick_value"]
    commission_per_lot = CONFIG["commission_per_lot"]
    slippage_ticks = CONFIG["slippage_ticks"]
    curve = ROLLOVER_CURVE

    from_df = from_df.copy()
    to_df = to_df.copy()
    from_df["date"] = from_df["dt"].dt.date
    to_df["date"] = to_df["dt"].dt.date

    start_date = rollover_date
    common_dates = sorted(set(from_df["date"]) & set(to_df["date"]))
    rollover_dates = [d for d in common_dates if d >= start_date][:days]

    no_overlap = False
    if len(rollover_dates) < 2:
        rollover_dates = [d for d in common_dates if d >= start_date]
        if not rollover_dates:
            rollover_dates = [rollover_date]
            no_overlap = True

    weights = get_rollover_weights(len(rollover_dates), curve)

    daily_costs = []
    total_cost_per_ton = 0.0

    for i, d in enumerate(rollover_dates):
        from_close = (
            from_df[from_df["date"] == d]["close"].iloc[-1]
            if len(from_df[from_df["date"] == d]) > 0
            else None
        )
        to_close = (
            to_df[to_df["date"] == d]["close"].iloc[-1]
            if len(to_df[to_df["date"] == d]) > 0
            else None
        )

        if no_overlap and (from_close is None or to_close is None):
            from_dates_on_or_before = from_df[from_df["date"] <= d]
            to_dates_on_or_after = to_df[to_df["date"] >= d]
            if len(from_dates_on_or_before) > 0:
                from_close = from_dates_on_or_before["close"].iloc[-1]
            else:
                from_close = from_df["close"].iloc[-1]
            if len(to_dates_on_or_after) > 0:
                to_close = to_dates_on_or_after["close"].iloc[0]
            else:
                to_close = to_df["close"].iloc[0]

        if from_close is None or to_close is None:
            continue

        slippage_cost = slippage_ticks * tick_value * 2
        commission_cost = commission_per_lot * 2 / volume_multiple
        price_diff = to_close - from_close
        weighted_cost = (price_diff + slippage_cost + commission_cost) * weights[i]
        total_cost_per_ton += weighted_cost

        daily_costs.append({
            "date": d,
            "weight": weights[i],
            "from_close": from_close,
            "to_close": to_close,
            "price_diff": price_diff,
            "slippage_cost": slippage_cost,
            "commission_cost": commission_cost,
            "weighted_cost": weighted_cost,
        })

    return {
        "total_slippage": slippage_ticks * tick_value * 2,
        "total_commission": commission_per_lot * 2 / volume_multiple,
        "total_cost": total_cost_per_ton,
        "price_adjustment": total_cost_per_ton,
        "start_date": rollover_dates[0] if rollover_dates else rollover_date,
        "end_date": rollover_dates[-1] if rollover_dates else rollover_date,
        "daily_costs": pd.DataFrame(daily_costs),
    }


def detect_rollover_by_volume(df_dict: dict[str, pd.DataFrame]) -> list[dict]:
    rollover_events = []
    sorted_yymm = sorted(df_dict.keys())

    for i in range(len(sorted_yymm)):
        curr_yymm = sorted_yymm[i]
        curr_df = df_dict[curr_yymm]
        if curr_df is None:
            continue

        for j in range(i + 1, len(sorted_yymm)):
            nxt_yymm = sorted_yymm[j]
            nxt_df = df_dict[nxt_yymm]
            if nxt_df is None:
                continue

            overlap_start = max(curr_df["dt"].min(), nxt_df["dt"].min())
            overlap_end = min(curr_df["dt"].max(), nxt_df["dt"].max())

            if overlap_start >= overlap_end:
                continue

            overlap_curr = curr_df[(curr_df["dt"] >= overlap_start) & (curr_df["dt"] <= overlap_end)].copy()
            overlap_nxt = nxt_df[(nxt_df["dt"] >= overlap_start) & (nxt_df["dt"] <= overlap_end)].copy()

            if len(overlap_curr) == 0 or len(overlap_nxt) == 0:
                continue

            overlap_curr["date"] = overlap_curr["dt"].dt.date
            overlap_nxt["date"] = overlap_nxt["dt"].dt.date

            daily_curr = overlap_curr.groupby("date")["volume"].sum()
            daily_nxt = overlap_nxt.groupby("date")["volume"].sum()

            common_dates = daily_curr.index.intersection(daily_nxt.index)
            if len(common_dates) < 5:
                continue

            ratio = daily_nxt.loc[common_dates] / (daily_curr.loc[common_dates] + 1)
            crossover_dates = common_dates[ratio > 1]

            if len(crossover_dates) > 0:
                rollover_date = crossover_dates[0]
                roll_price_curr = curr_df[curr_df["dt"].dt.date == rollover_date]["close"].iloc[-1]
                roll_price_nxt = nxt_df[nxt_df["dt"].dt.date == rollover_date]["close"].iloc[-1]

                rollover_events.append({
                    "rollover_date": rollover_date,
                    "from_yymm": curr_yymm,
                    "to_yymm": nxt_yymm,
                    "from_price": roll_price_curr,
                    "to_price": roll_price_nxt,
                    "price_diff": roll_price_nxt - roll_price_curr,
                    "price_diff_pct": (roll_price_nxt - roll_price_curr) / roll_price_curr * 100,
                    "confidence": min(ratio[crossover_dates].min(), 2.0),
                    "method": "volume",
                })

    return rollover_events


def detect_rollover_by_open_interest(df_dict: dict[str, pd.DataFrame]) -> list[dict]:
    rollover_events = []
    sorted_yymm = sorted(df_dict.keys())

    for i in range(len(sorted_yymm)):
        curr_yymm = sorted_yymm[i]
        curr_df = df_dict[curr_yymm]
        if curr_df is None:
            continue

        for j in range(i + 1, len(sorted_yymm)):
            nxt_yymm = sorted_yymm[j]
            nxt_df = df_dict[nxt_yymm]
            if nxt_df is None:
                continue

            overlap_start = max(curr_df["dt"].min(), nxt_df["dt"].min())
            overlap_end = min(curr_df["dt"].max(), nxt_df["dt"].max())

            if overlap_start >= overlap_end:
                continue

            overlap_curr = curr_df[(curr_df["dt"] >= overlap_start) & (curr_df["dt"] <= overlap_end)].copy()
            overlap_nxt = nxt_df[(nxt_df["dt"] >= overlap_start) & (nxt_df["dt"] <= overlap_end)].copy()

            if len(overlap_curr) == 0 or len(overlap_nxt) == 0:
                continue

            overlap_curr["date"] = overlap_curr["dt"].dt.date
            overlap_nxt["date"] = overlap_nxt["dt"].dt.date

            daily_curr_oi = overlap_curr.groupby("date")["close_oi"].last()
            daily_nxt_oi = overlap_nxt.groupby("date")["close_oi"].last()

            common_dates = daily_curr_oi.index.intersection(daily_nxt_oi.index)
            if len(common_dates) < 5:
                continue

            ratio = daily_nxt_oi.loc[common_dates] / (daily_curr_oi.loc[common_dates] + 1)
            crossover_dates = common_dates[ratio > 1]

            if len(crossover_dates) > 0:
                rollover_date = crossover_dates[0]
                roll_price_curr = curr_df[curr_df["dt"].dt.date == rollover_date]["close"].iloc[-1]
                roll_price_nxt = nxt_df[nxt_df["dt"].dt.date == rollover_date]["close"].iloc[-1]

                rollover_events.append({
                    "rollover_date": rollover_date,
                    "from_yymm": curr_yymm,
                    "to_yymm": nxt_yymm,
                    "from_price": roll_price_curr,
                    "to_price": roll_price_nxt,
                    "price_diff": roll_price_nxt - roll_price_curr,
                    "price_diff_pct": (roll_price_nxt - roll_price_curr) / roll_price_curr * 100,
                    "confidence": min(ratio[crossover_dates].min(), 2.0),
                    "method": "open_interest",
                })

    return rollover_events


def detect_rollover_by_time(df_dict: dict[str, pd.DataFrame]) -> list[dict]:
    rollover_events = []
    sorted_yymm = sorted(df_dict.keys())

    for i in range(len(sorted_yymm)):
        curr_yymm = sorted_yymm[i]
        curr_df = df_dict[curr_yymm]
        if curr_df is None or len(curr_df) == 0:
            continue

        curr_end = curr_df["dt"].max()

        for j in range(i + 1, len(sorted_yymm)):
            nxt_yymm = sorted_yymm[j]
            nxt_df = df_dict[nxt_yymm]
            if nxt_df is None or len(nxt_df) == 0:
                continue

            nxt_start = nxt_df["dt"].min()

            gap_days = (nxt_start - curr_end).days
            if gap_days > 60:
                continue

            overlap_start = max(curr_df["dt"].min(), nxt_df["dt"].min())
            overlap_end = min(curr_df["dt"].max(), nxt_df["dt"].max())

            if overlap_start >= overlap_end:
                rollover_date = curr_end.date()
            else:
                rollover_date = overlap_start.date() + timedelta(days=5)

            roll_price_curr = (
                curr_df[curr_df["dt"].dt.date == rollover_date]["close"].iloc[-1]
                if len(curr_df[curr_df["dt"].dt.date == rollover_date]) > 0
                else curr_df["close"].iloc[-1]
            )
            roll_price_nxt = (
                nxt_df[nxt_df["dt"].dt.date == rollover_date]["close"].iloc[-1]
                if len(nxt_df[nxt_df["dt"].dt.date == rollover_date]) > 0
                else nxt_df["close"].iloc[0]
            )

            rollover_events.append({
                "rollover_date": rollover_date,
                "from_yymm": curr_yymm,
                "to_yymm": nxt_yymm,
                "from_price": roll_price_curr,
                "to_price": roll_price_nxt,
                "price_diff": roll_price_nxt - roll_price_curr,
                "price_diff_pct": (roll_price_nxt - roll_price_curr) / roll_price_curr * 100 if roll_price_curr != 0 else 0,
                "confidence": 0.5,
                "method": "time",
            })

    return rollover_events


def detect_dominant_chain(
    df_dict: dict[str, pd.DataFrame],
    min_oi_ratio: float = 0.05,
    min_confirmation_days: int = 3,
    exclude_delivery_month: bool = True,
    whipsaw_min_gap_days: int = 5,
    yymm_len: int = 4,
    allowed_delivery_months: tuple[int, ...] | None = None,
) -> tuple[list[dict], list[str]]:
    if not df_dict:
        return [], []

    df_dict, excluded = filter_df_dict_by_delivery_months(
        df_dict, allowed_delivery_months, yymm_len,
    )
    if excluded:
        print(
            f"  交割月白名单 {sorted(allowed_delivery_months)}: "
            f"排除 {len(excluded)} 个分月"
        )
    if len(df_dict) < 2:
        print("  错误: 白名单过滤后有效合约少于 2 个")
        return [], []

    daily_oi_list = []
    for yymm, df in df_dict.items():
        if df is None or len(df) == 0 or "close_oi" not in df.columns:
            continue
        df_temp = df[["dt", "close_oi"]].copy()
        df_temp["date"] = df_temp["dt"].dt.date
        daily = df_temp.groupby("date")["close_oi"].last().reset_index()
        daily["yymm"] = yymm
        daily_oi_list.append(daily)

    if not daily_oi_list:
        return [], []

    all_oi = pd.concat(daily_oi_list, ignore_index=True)
    pivot = all_oi.pivot(index="date", columns="yymm", values="close_oi").fillna(0)

    if exclude_delivery_month:
        for yymm in pivot.columns:
            mm = delivery_month_from_yymm(yymm, effective_yymm_len(yymm))
            ref = pivot.index[-1] if len(pivot.index) else date.today()
            yy = contract_year_from_yymm(yymm, effective_yymm_len(yymm), ref)
            expire_yy, expire_mm = (yy + 1, 1) if mm == 12 else (yy, mm + 1)
            expire_date = date(expire_yy, expire_mm, 1) - timedelta(days=5)
            mask = pivot.index >= expire_date
            if mask.any():
                pivot.loc[mask, yymm] = 0

    pivot["max_oi"] = pivot.max(axis=1)
    pivot["dominant"] = None
    for date_idx in pivot.index:
        max_oi = pivot.loc[date_idx, "max_oi"]
        if max_oi == 0:
            continue
        best_yymm = pivot.loc[date_idx].drop(["max_oi", "dominant"]).idxmax()
        best_oi = pivot.loc[date_idx, best_yymm]
        if best_oi >= max_oi * min_oi_ratio:
            pivot.loc[date_idx, "dominant"] = best_yymm

    pivot["dominant_smoothed"] = pivot["dominant"]
    pivot["prev_dominant"] = pivot["dominant_smoothed"].ffill()

    for i in range(min_confirmation_days, len(pivot)):
        curr = pivot["dominant"].iloc[i]
        prev = pivot["prev_dominant"].iloc[i - 1]
        if pd.isna(curr) or pd.isna(prev) or curr == prev:
            continue
        new_oi = [
            pivot.loc[pivot.index[j], curr] if j >= 0 and curr in pivot.columns else 0
            for j in range(i - min_confirmation_days + 1, i + 1)
        ]
        old_oi = [
            pivot.loc[pivot.index[j], prev] if j >= 0 and prev in pivot.columns else 0
            for j in range(i - min_confirmation_days + 1, i + 1)
        ]
        if all(n > o for n, o in zip(new_oi, old_oi)):
            pivot.loc[pivot.index[i], "dominant_smoothed"] = curr
        else:
            pivot.loc[pivot.index[i], "dominant_smoothed"] = prev

    pivot["dominant"] = pivot["dominant_smoothed"].ffill()
    pivot["prev_dominant"] = pivot["dominant"].shift()
    changes = pivot[(pivot["dominant"] != pivot["prev_dominant"]) & pivot["prev_dominant"].notna()].copy()

    rollover_events = []
    # 序列开头可能缺 OI（ffill 后仍为 NaN）；取首个有效主力，勿用 iloc[0]
    _dom_valid = pivot["dominant"].dropna()
    first_dominant = str(_dom_valid.iloc[0]) if len(_dom_valid) else None

    for _, row in changes.iterrows():
        from_yymm = row["prev_dominant"]
        to_yymm = row["dominant"]
        rollover_date = row.name

        if not from_yymm or not to_yymm or from_yymm == to_yymm:
            continue

        from_df = df_dict.get(from_yymm)
        to_df = df_dict.get(to_yymm)
        if from_df is None or to_df is None:
            continue

        from_rows = from_df[from_df["dt"].dt.date == rollover_date]
        to_rows = to_df[to_df["dt"].dt.date == rollover_date]
        from_price = from_rows["close"].iloc[-1] if len(from_rows) > 0 else from_df["close"].iloc[-1]
        to_price = to_rows["close"].iloc[-1] if len(to_rows) > 0 else to_df["close"].iloc[0]

        rollover_events.append({
            "rollover_date": rollover_date,
            "from_yymm": from_yymm,
            "to_yymm": to_yymm,
            "from_price": from_price,
            "to_price": to_price,
            "price_diff": to_price - from_price,
            "price_diff_pct": (to_price - from_price) / from_price * 100 if from_price != 0 else 0,
            "confidence": 1.0,
            "method": ROLLOVER_METHOD,
        })

    raw_count = len(rollover_events)
    rollover_events, whipsaw_skipped = _filter_whipsaw_events(
        rollover_events, first_dominant, whipsaw_min_gap_days,
    )

    if not first_dominant and rollover_events:
        first_dominant = str(rollover_events[0]["from_yymm"])

    if first_dominant:
        dominant_chain = [first_dominant] + [e["to_yymm"] for e in rollover_events]
    else:
        dominant_chain = []

    print(f"  主力链法: 发现 {len(rollover_events)} 个换月点 (原始 {raw_count}, whipsaw 过滤 {whipsaw_skipped})")
    print(
        f"    (最小OI比例={min_oi_ratio}, 确认天数={min_confirmation_days}, "
        f"排除交割月={exclude_delivery_month}, whipsaw间隔={whipsaw_min_gap_days}d)"
    )
    print(f"  主力合约数: {len(dominant_chain)} (vs 总合约数 {len(df_dict)})")

    return rollover_events, dominant_chain


def build_rollover_map(from_oi_daily: bool = False) -> tuple[pd.DataFrame, list[str]]:
    prefix = CONFIG["prefix"]
    yymm_len = CONFIG["yymm_len"]

    print(f"\n{'='*60}")
    print(f"{CONFIG['name']} ({prefix}) 换月映射表生成")
    allowed = CONFIG.get("allowed_delivery_months")
    switch = CONFIG.get("rollover_switch_time", ROLLOVER_SWITCH_TIME)
    if allowed:
        print(f"  交割月白名单: {sorted(allowed)} | OI确认 {ROLLOVER_CONFIRM_DAYS}d | 切点 {switch} CST")
    else:
        print(f"  交割月: 不限制 | OI确认 {ROLLOVER_CONFIRM_DAYS}d | 切点 {switch} CST")
    if from_oi_daily:
        print(f"  数据源: oi_daily/ (Phase-1 日频 OI)")
    print(f"{'='*60}")

    df_dict: dict[str, pd.DataFrame] = {}

    if from_oi_daily:
        df_dict = load_oi_daily_dict(DATA_DIR, prefix)
        print(f"\n发现 {len(df_dict)} 个 oi_daily 合约文件")
        for yymm, df in sorted(df_dict.items()):
            print(f"  {prefix}_{yymm}: {len(df):>5} days, "
                  f"{df['dt'].min().date()} ~ {df['dt'].max().date()}")
    else:
        contract_files = [
            f for f in os.listdir(DATA_DIR)
            if f.startswith(f"{prefix}_") and f.endswith(".parquet")
            and "_part_" not in f
            and not f.endswith("_continuous.parquet")
            and not f.startswith("rollover_")
        ]

        valid_files = []
        for f in contract_files:
            yymm = parse_contract_code(f)
            if yymm:
                valid_files.append((f, yymm))

        valid_files.sort(key=lambda x: x[1])
        print(f"\n发现 {len(valid_files)} 个分月合约数据文件")

        for f, yymm in valid_files:
            df = load_contract_data(yymm)
            if df is not None and len(df) > 100:
                df_dict[yymm] = df
                print(f"  {prefix}_{yymm}: {len(df):>7} rows, "
                      f"{df['dt'].min().date()} ~ {df['dt'].max().date()}")

    if len(df_dict) < 2:
        src = "oi_daily" if from_oi_daily else "分月 1m"
        print(f"\n错误: 有效合约数据少于 2 个，无法生成换月映射表（来源: {src}）")
        return pd.DataFrame(), []

    print("\n检测换月时间点...")

    dominant_events, dominant_chain = detect_dominant_chain(
        df_dict,
        yymm_len=yymm_len,
        allowed_delivery_months=CONFIG.get("allowed_delivery_months"),
        **DOMINANT_OI_PARAMS,
    )

    if not from_oi_daily:
        volume_events = detect_rollover_by_volume(df_dict)
        print(f"  成交量法(对照): 发现 {len(volume_events)} 个换月点")

        oi_events = detect_rollover_by_open_interest(df_dict)
        print(f"  持仓量法(对照): 发现 {len(oi_events)} 个换月点")

        time_events = detect_rollover_by_time(df_dict)
        print(f"  时间规则法(对照): 发现 {len(time_events)} 个换月点")

    rollover_map = pd.DataFrame(dominant_events)

    if len(rollover_map) > 0:
        rollover_map = rollover_map.sort_values("rollover_date").reset_index(drop=True)
        rollover_map["rollover_id"] = range(1, len(rollover_map) + 1)

    return rollover_map, dominant_chain


def _bounds_from_df_dict(df_dict: dict[str, pd.DataFrame]) -> dict[str, tuple[date, date]]:
    bounds: dict[str, tuple[date, date]] = {}
    for yymm, df in df_dict.items():
        bounds[yymm] = (df["dt"].min().date(), df["dt"].max().date())
    return bounds


def write_dominant_windows(
    rollover_map: pd.DataFrame,
    dominant_chain: list[str],
    df_dict: dict[str, pd.DataFrame],
    *,
    source: str = "oi_daily",
) -> str:
    if not dominant_chain and not rollover_map.empty:
        dominant_chain = build_dominant_chain(rollover_map)
        print(f"  主力链为空，已从 rollover_map 重建: {len(dominant_chain)} 合约")
    bounds = _bounds_from_df_dict(df_dict)
    payload = build_dominant_windows(
        rollover_map, dominant_chain, bounds, source=source,
    )
    map_path = os.path.join(DATA_DIR, "rollover_map.parquet")
    return save_dominant_windows(DATA_DIR, payload, rollover_map_path=map_path)


def compare_rollover_maps(
    new_map: pd.DataFrame,
    ref_path: str,
    *,
    max_day_diff: int = 2,
) -> bool:
    """对比换月日与参考 map；允许 max_day_diff 个日历日偏差。"""
    if not os.path.exists(ref_path):
        print(f"参考 map 不存在: {ref_path}")
        return False
    ref = pd.read_parquet(ref_path)
    if ref.empty or new_map.empty:
        print("新 map 或参考 map 为空")
        return False

    key_cols = ["from_yymm", "to_yymm"]
    merged = new_map.merge(
        ref, on=key_cols, how="outer", suffixes=("_new", "_ref"), indicator=True,
    )
    only_new = merged[merged["_merge"] == "left_only"]
    only_ref = merged[merged["_merge"] == "right_only"]
    if len(only_new) or len(only_ref):
        print(f"换月对不匹配: 仅新 {len(only_new)} | 仅参考 {len(only_ref)}")
        if len(only_new):
            print(only_new[key_cols].head())
        if len(only_ref):
            print(only_ref[key_cols].head())
        return False

    both = merged[merged["_merge"] == "both"].copy()
    both["rollover_date_new"] = pd.to_datetime(both["rollover_date_new"]).dt.date
    both["rollover_date_ref"] = pd.to_datetime(both["rollover_date_ref"]).dt.date
    both["day_diff"] = both.apply(
        lambda r: abs((r["rollover_date_new"] - r["rollover_date_ref"]).days),
        axis=1,
    )
    bad = both[both["day_diff"] > max_day_diff]
    if len(bad):
        print(f"换月日偏差 >{max_day_diff}d: {len(bad)} 条")
        print(bad[["from_yymm", "to_yymm", "rollover_date_new", "rollover_date_ref", "day_diff"]].head(10))
        return False

    exact = (both["day_diff"] == 0).sum()
    print(f"换月对比通过: {len(both)} 条, 完全相同 {exact}, 最大偏差 {both['day_diff'].max()}d")
    return True


def generate_rollover_cost_detail(
    rollover_map: pd.DataFrame,
    dominant_chain: list[str],
) -> pd.DataFrame:
    """按换月事件计算移仓滑点/手续费明细（不写复权连续合约）。"""
    volume_multiple = CONFIG["volume_multiple"]
    tick_value = CONFIG["tick_value"]
    commission_per_lot = CONFIG["commission_per_lot"]
    slippage_ticks = CONFIG["slippage_ticks"]

    if len(rollover_map) == 0 or not dominant_chain:
        print("\n无换月数据或主力链为空，无法生成成本明细")
        return pd.DataFrame()

    print(f"\n{'='*60}")
    print(f"生成移仓成本明细（主力链 {len(dominant_chain)} 合约）")
    print(f"  移仓天数: {ROLLOVER_DAYS} 天 | 分布: {ROLLOVER_CURVE}")
    print(f"  滑点: {slippage_ticks} tick ({slippage_ticks * tick_value} 元/吨, 双边)")
    print(
        f"  手续费: {commission_per_lot} 元/手 "
        f"(双边, 约 {commission_per_lot * 2 / volume_multiple:.3f} 元/吨)"
    )
    print(f"{'='*60}")

    df_dict = {}
    for yymm in dominant_chain:
        df = load_contract_data(yymm)
        if df is not None:
            df_dict[yymm] = df
        else:
            print(f"  警告: 主力合约 {yymm} 数据加载失败，跳过")

    chain_yymm = [y for y in dominant_chain if y in df_dict]
    if len(chain_yymm) < 1:
        print("\n错误: 主力链中无有效合约")
        return pd.DataFrame()

    rollover_events = [
        e for e in _ordered_rollover_events(rollover_map)
        if e["from_yymm"] in df_dict and e["to_yymm"] in df_dict
    ]
    if len(rollover_events) != len(chain_yymm) - 1:
        # 末段合约仅有 OI、尚无 1m 时，截断到有数据的连续前缀
        truncated: list[str] = [chain_yymm[0]]
        for ev in rollover_events:
            if ev["from_yymm"] != truncated[-1]:
                break
            if ev["to_yymm"] not in df_dict:
                break
            truncated.append(ev["to_yymm"])
        chain_yymm = truncated
        rollover_events = rollover_events[: max(0, len(chain_yymm) - 1)]
        print(
            f"  提示: 缺 1m 的主力合约已跳过，成本明细覆盖 "
            f"{len(chain_yymm)}/{len(dominant_chain)} 个链上合约"
        )
    if len(rollover_events) != len(chain_yymm) - 1:
        raise RuntimeError(
            f"换月事件数 ({len(rollover_events)}) 与主力链长度 ({len(chain_yymm)}) 不匹配"
        )

    rollover_details = []
    cumulative_spread = 0.0
    cumulative_cost = 0.0

    for idx in range(1, len(chain_yymm)):
        prev_yymm = chain_yymm[idx - 1]
        yymm = chain_yymm[idx]
        rollover_row = rollover_events[idx - 1]
        if rollover_row["from_yymm"] != prev_yymm or rollover_row["to_yymm"] != yymm:
            continue

        rollover_date = rollover_row["rollover_date"]
        spread = float(rollover_row["price_diff"])
        cumulative_spread += spread

        if isinstance(rollover_date, pd.Timestamp):
            rollover_date = rollover_date.date()
        elif isinstance(rollover_date, datetime):
            rollover_date = rollover_date.date()

        sim_result = simulate_rollover_cost(
            df_dict[prev_yymm],
            df_dict[yymm],
            rollover_date,
        )
        cost_adj = float(sim_result["price_adjustment"])
        cumulative_cost += cost_adj

        rollover_details.append({
            "rollover_id": rollover_row.get("rollover_id", idx),
            "rollover_date": rollover_date,
            "from_yymm": prev_yymm,
            "to_yymm": yymm,
            "price_diff_only": spread,
            "slippage_cost": sim_result["total_slippage"],
            "commission_cost": sim_result["total_commission"],
            "total_adjustment": cost_adj,
            "rollover_start_date": sim_result["start_date"],
            "rollover_end_date": sim_result["end_date"],
            "cumulative_spread": cumulative_spread,
            "cumulative_cost": cumulative_cost,
        })
        print(
            f"  {prev_yymm} -> {yymm}: "
            f"价差={spread:+.2f}, "
            f"滑点={sim_result['total_slippage']:+.2f}, "
            f"手续费={sim_result['total_commission']:+.3f}, "
            f"成本调整={cost_adj:+.2f} "
            f"(价差累计={cumulative_spread:+.2f}, 成本累计={cumulative_cost:+.2f})"
        )

    detail_df = pd.DataFrame(rollover_details)
    print(f"\n移仓次数: {len(detail_df)}")
    return detail_df


def _load_manifest() -> dict:
    path = os.path.join(DATA_DIR, MANIFEST_FILE)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_manifest(manifest: dict) -> None:
    path = os.path.join(DATA_DIR, MANIFEST_FILE)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def _latest_monthly_download_time(manifest: dict, prefix: str) -> str | None:
    times = []
    for key, entry in manifest.items():
        if not isinstance(entry, dict):
            continue
        if key.startswith(f"{prefix}_") and key.endswith(".parquet") and "_part_" not in key:
            t = entry.get("download_time")
            if t:
                times.append(t)
    return max(times) if times else None


def update_manifest_derived(
    prefix: str,
    rollover_map: pd.DataFrame,
    dominant_chain: list[str],
    rollover_detail: pd.DataFrame,
) -> None:
    manifest = _load_manifest()
    manifest.setdefault("_meta", {})
    manifest["_meta"].update({
        "session_note": SESSION_NOTE,
        "datetime_unit": "ns_utc",
        "monthly_schema": list(VERIFY_OHLCV_COLUMNS),
    })

    built_at = datetime.now().isoformat()
    derived = {
        "rollover_map.parquet": {
            "built_at": built_at,
            "rows": int(len(rollover_map)),
            "rollover_method": ROLLOVER_METHOD,
            "rollover_params": DOMINANT_OI_PARAMS,
            "dominant_chain": dominant_chain,
            "source_monthly_max_download_time": _latest_monthly_download_time(manifest, prefix),
        },
    }
    if len(rollover_detail) > 0:
        derived["rollover_cost_detail.parquet"] = {
            "built_at": built_at,
            "rows": int(len(rollover_detail)),
            "slippage_simulated": True,
            "note": "移仓滑点/手续费（元/吨），非行情复权",
        }

    # 清除历史 continuous 衍生记录
    old = manifest.get("derived") or {}
    cont_key = f"{prefix}_continuous.parquet"
    if cont_key in old:
        print(f"manifest derived 已移除过时项: {cont_key}")

    manifest["derived"] = derived
    _save_manifest(manifest)
    print(f"\nmanifest 已更新 derived 段: {os.path.join(DATA_DIR, MANIFEST_FILE)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="换月映射表 + 移仓成本明细")
    parser.add_argument("-s", "--symbol", required=True, help="品种代码，如 rb, m, MA")
    parser.add_argument(
        "--verify",
        action="store_true",
        help="保留兼容；当前全量构建不再校验 continuous",
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="保留兼容；当前全量构建不再校验 continuous",
    )
    parser.add_argument(
        "--map-only",
        action="store_true",
        help="仅生成 rollover_map.parquet + dominant_windows.json，不生成成本明细",
    )
    parser.add_argument(
        "--from-oi-daily",
        action="store_true",
        help="从 data/tq/{prefix}/oi_daily/ 日频 OI 建换月表（两阶段 Phase-1）",
    )
    parser.add_argument(
        "--compare-rollover",
        metavar="PATH",
        default=None,
        help="与参考 rollover_map.parquet 对比换月日（允许 ≤2 日偏差）",
    )
    args = parser.parse_args()

    _configure(args.symbol)
    prefix = CONFIG["prefix"]

    from_oi = args.from_oi_daily
    rollover_map, dominant_chain = build_rollover_map(from_oi_daily=from_oi)

    if len(rollover_map) == 0:
        src = "oi_daily" if from_oi else "分月 1m"
        print(f"\n未检测到换月时间点，请先下载数据（来源: {src}）")
        sys.exit(1)

    map_parquet = os.path.join(DATA_DIR, "rollover_map.parquet")
    rollover_map.to_parquet(map_parquet, index=False, engine="pyarrow")
    print(f"\n换月映射表已保存: {map_parquet}")

    if from_oi or args.map_only:
        df_for_bounds = (
            load_oi_daily_dict(DATA_DIR, prefix) if from_oi
            else {yymm: load_contract_data(yymm) for yymm in dominant_chain
                  if load_contract_data(yymm) is not None}
        )
        win_path = write_dominant_windows(
            rollover_map, dominant_chain, df_for_bounds,
            source="oi_daily" if from_oi else "monthly_1m",
        )
        print(f"主力下载窗口已保存: {win_path}")

    if args.compare_rollover:
        ok = compare_rollover_maps(rollover_map, args.compare_rollover)
        if not ok:
            sys.exit(3)

    display_cols = [
        "rollover_id", "rollover_date", "from_yymm",
        "to_yymm", "price_diff", "price_diff_pct", "method",
    ]
    print("\n换月时间点预览:")
    print(rollover_map[display_cols].to_string(index=False))

    if args.map_only:
        print(f"\n--map-only: 跳过成本明细（切点 {CONFIG.get('rollover_switch_time')} CST）")
        print(f"\n{'='*60}")
        print(f"{CONFIG['name']} rollover_map 完成")
        print(f"{'='*60}")
        return

    rollover_detail = generate_rollover_cost_detail(rollover_map, dominant_chain)
    if len(rollover_detail) == 0:
        print("\n移仓成本明细为空（无有效换月事件）")
        sys.exit(1)

    detail_parquet = os.path.join(DATA_DIR, "rollover_cost_detail.parquet")
    rollover_detail.to_parquet(detail_parquet, index=False, engine="pyarrow")
    print(f"移仓成本明细已保存: {detail_parquet}")

    # 清理历史复权 continuous 文件（回测主路径不使用）
    cont_file = os.path.join(DATA_DIR, f"{prefix}_continuous.parquet")
    if os.path.exists(cont_file):
        os.remove(cont_file)
        print(f"已删除过时 continuous: {cont_file}")

    update_manifest_derived(prefix, rollover_map, dominant_chain, rollover_detail)

    print(f"\n{'='*60}")
    print(f"{CONFIG['name']} 完成！")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
