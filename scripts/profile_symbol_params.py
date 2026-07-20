# -*- coding: utf-8 -*-
"""按 rb 选择性客观推导各 TQ CbC 品种的 rb_min_atr / ttr_rb_min_atr / max_position。

方法：
- 以 rb 为锚：算 rb 的 5m ATR(14) 分布中，rb_min_atr=8.0 / ttr=5.5 各自所处分位。
- 其余品种取相同分位对应的 5m ATR 值（四舍五入到 pricetick），使入场选择性与 rb 一致。
- max_position 按名义敞口上限反推：rb(35 手 × size10 × rb中位价) 为基准，其余品种按 size×中位价缩放。

用法: .venv\\Scripts\\python.exe scripts\\profile_symbol_params.py
输出为可粘贴进 SYMBOL_PROFILES 的建议块；不写文件、不回测。
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.tq_rollover_data import load_stitched_raw_bars
from strategies.pa_cta.symbol_config import TQ_SYMBOL_ENGINE, resolve_symbol_profile

START = datetime(2021, 7, 1)
END = datetime(2026, 6, 30)
ATR_WINDOW = 14
RB_MIN_ATR = 8.0
RB_TTR = 5.5


def _atr5_series(bars) -> tuple[np.ndarray, float]:
    """1m bars → 5min 重采样 → ATR(14, SMA) 序列 + 中位收盘价。"""
    idx = pd.to_datetime([b.datetime for b in bars])
    df = pd.DataFrame(
        {
            "open": [float(b.open_price) for b in bars],
            "high": [float(b.high_price) for b in bars],
            "low": [float(b.low_price) for b in bars],
            "close": [float(b.close_price) for b in bars],
        },
        index=idx,
    ).sort_index()
    o = df["open"].resample("5min").first()
    h = df["high"].resample("5min").max()
    low = df["low"].resample("5min").min()
    c = df["close"].resample("5min").last()
    bar5 = pd.DataFrame({"open": o, "high": h, "low": low, "close": c}).dropna()
    prev_close = bar5["close"].shift(1)
    tr = pd.concat(
        [
            bar5["high"] - bar5["low"],
            (bar5["high"] - prev_close).abs(),
            (bar5["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr = tr.rolling(ATR_WINDOW).mean().dropna()
    return atr.to_numpy(), float(bar5["close"].median())


def _round_to_tick(value: float, tick: float) -> float:
    if tick <= 0:
        return round(value, 4)
    n = max(1, round(value / tick))
    return round(n * tick, 6)


def main() -> None:
    profiles: dict[str, tuple[np.ndarray, float, dict]] = {}
    for key in TQ_SYMBOL_ENGINE:
        prof = resolve_symbol_profile(key, _ROOT)
        try:
            bars = load_stitched_raw_bars(
                prof["file_stem"], prof["exchange"],
                symbol=prof["symbol"], start=START, end=END,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"# {key}: LOAD-ERROR {type(exc).__name__}: {str(exc)[:80]}")
            continue
        if len(bars) < ATR_WINDOW * 10:
            print(f"# {key}: 数据不足 ({len(bars)} 根 1m)")
            continue
        atr, med_price = _atr5_series(bars)
        profiles[key] = (atr, med_price, prof)

    if "rb" not in profiles:
        print("# 缺 rb，无法校准分位")
        return

    rb_atr, rb_price, rb_prof = profiles["rb"]
    pct_min = float((rb_atr < RB_MIN_ATR).mean())
    pct_ttr = float((rb_atr < RB_TTR).mean())
    notional_cap = 35 * int(rb_prof["size"]) * rb_price
    print(f"# rb 校准: 5m ATR 中位={np.median(rb_atr):.2f}, "
          f"min_atr=8 处于 {pct_min*100:.1f}% 分位, ttr=5.5 处于 {pct_ttr*100:.1f}% 分位")
    print(f"# 名义敞口上限锚(rb 35手)= {notional_cap:,.0f} 元\n")

    for key, (atr, med_price, prof) in profiles.items():
        tick = float(prof["pricetick"])
        size = int(prof["size"])
        min_atr = _round_to_tick(float(np.quantile(atr, pct_min)), tick)
        ttr = _round_to_tick(float(np.quantile(atr, pct_ttr)), tick)
        max_pos = int(np.clip(round(notional_cap / (size * med_price)), 3, 50))
        print(
            f'    "{key}": {{  # 中位价{med_price:,.0f} 5mATR中位{np.median(atr):.2f}\n'
            f'        "rb_min_atr": {min_atr}, "ttr_rb_min_atr": {ttr}, "max_position": {max_pos},\n'
            f'    }},'
        )


if __name__ == "__main__":
    main()
