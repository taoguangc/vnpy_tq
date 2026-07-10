# -*- coding: utf-8
"""品种结构对比：hc vs rb/ma/ta（回测窗 2023-05-17~2026-05-16）。"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.tq_rollover_data import build_stitched_raw_frame
from strategies.pa_cta.symbol_config import resolve_symbol_profile, resolve_tq_cbc_paths

START = pd.Timestamp("2023-05-17", tz="Asia/Shanghai")
END = pd.Timestamp("2026-05-16", tz="Asia/Shanghai")
SYMS = ("hc", "rb", "ma", "ta")
ROOT = Path(__file__).resolve().parents[1]


def eff_ratio(close: pd.Series, n: int = 20) -> float:
    if len(close) < n + 1:
        return 0.0
    direction = abs(close.iloc[-1] - close.iloc[-n - 1])
    vol = close.diff().abs().iloc[-n:].sum()
    return direction / vol if vol > 0 else 0.0


def daily_stats(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["date"] = d["dt_cst"].dt.date
    g = d.groupby("date").agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        volume=("volume", "sum"),
    )
    g["range_pct"] = (g["high"] - g["low"]) / g["close"] * 100
    g["ret_pct"] = g["close"].pct_change() * 100
    return g


def analyze(sym: str) -> dict:
    profile = resolve_symbol_profile(sym, ROOT)
    _, file_stem = resolve_tq_cbc_paths(profile)
    raw = build_stitched_raw_frame(file_stem)
    df = raw[(raw["dt_cst"] >= START) & (raw["dt_cst"] <= END)].copy()
    close = df["close"].astype(float)
    hl = (df["high"] - df["low"]).astype(float)

    # 1m TR 近似
    tr = hl.copy()
    tr.iloc[1:] = np.maximum(
        hl.iloc[1:].values,
        np.maximum(
            (df["high"].iloc[1:].values - close.iloc[:-1].values),
            np.abs(df["low"].iloc[1:].values - close.iloc[:-1].values),
        ),
    )
    atr14 = tr.rolling(14).mean()

    daily = daily_stats(df)
    # 15m 重采样
    d15 = (
        df.set_index("dt_cst")
        .resample("15min", label="right", closed="right")
        .agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
        .dropna(subset=["close"])
    )

    total_ret = (close.iloc[-1] / close.iloc[0] - 1) * 100
    ann_vol = daily["ret_pct"].std() * np.sqrt(245)  # 交易日近似

    return {
        "sym": sym,
        "close_start": close.iloc[0],
        "close_end": close.iloc[-1],
        "total_ret_pct": total_ret,
        "close_range": f"{close.min():.0f}~{close.max():.0f}",
        "atr14_mean": atr14.mean(),
        "atr14_pct": atr14.mean() / close.mean() * 100,
        "bar_hl_pct_mean": (hl / close * 100).mean(),
        "bar_hl_pct_p95": (hl / close * 100).quantile(0.95),
        "daily_range_pct_mean": daily["range_pct"].mean(),
        "daily_range_pct_p95": daily["range_pct"].quantile(0.95),
        "daily_ret_std": daily["ret_pct"].std(),
        "ann_vol_pct": ann_vol,
        "vol_1m_median": df["volume"].median(),
        "vol_1m_mean": df["volume"].mean(),
        "vol_daily_mean": daily["volume"].mean(),
        "er_15m_last_mean": d15["close"].rolling(21).apply(lambda x: eff_ratio(x, 20), raw=False).mean(),
        "pct_up_days": (daily["ret_pct"] > 0).mean() * 100,
        "max_daily_move_pct": daily["ret_pct"].abs().max(),
    }


rows = [analyze(s) for s in SYMS]
tbl = pd.DataFrame(rows).set_index("sym")

print("=== 波动 / 振幅（越大=振幅越大）===")
cols = [
    "atr14_pct", "bar_hl_pct_mean", "bar_hl_pct_p95",
    "daily_range_pct_mean", "daily_range_pct_p95",
    "daily_ret_std", "ann_vol_pct", "max_daily_move_pct",
]
print(tbl[cols].round(3).to_string())

print("\n=== 流动性 / 趋势结构 ===")
cols2 = ["vol_1m_median", "vol_1m_mean", "vol_daily_mean", "er_15m_last_mean", "total_ret_pct", "pct_up_days"]
print(tbl[cols2].round(2).to_string())

# hc-rb 相对特征
_, hc_stem = resolve_tq_cbc_paths(resolve_symbol_profile("hc", ROOT))
_, rb_stem = resolve_tq_cbc_paths(resolve_symbol_profile("rb", ROOT))
hc = build_stitched_raw_frame(hc_stem)
rb = build_stitched_raw_frame(rb_stem)
hcw = hc[(hc["dt_cst"] >= START) & (hc["dt_cst"] <= END)][["dt_cst", "close"]]
rbw = rb[(rb["dt_cst"] >= START) & (rb["dt_cst"] <= END)][["dt_cst", "close"]]
m = hcw.merge(rbw, on="dt_cst", suffixes=("_hc", "_rb"))
m["spread"] = m["close_hc"] - m["close_rb"]
m["ratio"] = m["close_hc"] / m["close_rb"]
print("\n=== hc 相对 rb（热卷-螺纹价差）===")
print(f"spread mean={m.spread.mean():.1f} std={m.spread.std():.1f} min={m.spread.min():.0f} max={m.spread.max():.0f}")
print(f"ratio mean={m.ratio.mean():.4f} std={m.ratio.std():.4f}")
print(f"corr(1m close)={m.close_hc.corr(m.close_rb):.4f}")

# 排名
print("\n=== 相对排序（1=最小/最低）===")
rank = tbl[cols + ["vol_1m_median"]].rank()
for sym in SYMS:
    r = rank.loc[sym]
    print(f"{sym}: atr_pct rank {int(r.atr14_pct)}/4  daily_range rank {int(r.daily_range_pct_mean)}/4  vol rank {int(r.vol_1m_median)}/4")
