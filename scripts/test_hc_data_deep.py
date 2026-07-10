# -*- coding: utf-8
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.tq_rollover_data import build_stitched_raw_frame

START = pd.Timestamp("2023-05-17", tz="Asia/Shanghai")
END = pd.Timestamp("2026-05-16", tz="Asia/Shanghai")

for sym in ("hc", "rb"):
    df = build_stitched_raw_frame(sym)
    w = df[(df["dt_cst"] >= START) & (df["dt_cst"] <= END)].copy()
    ret = w["close"].pct_change()
    j = w.loc[ret.abs() > 0.05, ["dt_cst", "yymm", "open", "high", "low", "close", "volume"]]
    print(f"--- {sym} jump>5% ---")
    print(j.to_string(index=False) if len(j) else "none")
    print(
        f"vol median={w['volume'].median():.0f} mean={w['volume'].mean():.0f} "
        f"p95={w['volume'].quantile(0.95):.0f}"
    )

hc = build_stitched_raw_frame("hc")
rb = build_stitched_raw_frame("rb")
hcw = hc[(hc["dt_cst"] >= START) & (hc["dt_cst"] <= END)][["dt_cst", "close"]].rename(columns={"close": "hc"})
rbw = rb[(rb["dt_cst"] >= START) & (rb["dt_cst"] <= END)][["dt_cst", "close"]].rename(columns={"close": "rb"})
m = hcw.merge(rbw, on="dt_cst", how="inner")
m["spread"] = m["hc"] - m["rb"]
print(
    f"\nhc-rb spread: min={m.spread.min():.0f} max={m.spread.max():.0f} "
    f"mean={m.spread.mean():.1f} std={m.spread.std():.1f}"
)
print(f"bar align: {len(m)} corr={m.hc.corr(m.rb):.4f}")

rm = pd.read_parquet("data/tq/hc/rollover_map.parquet")
print("\nhc rollover_map:")
print(rm[["rollover_id", "rollover_date", "from_yymm", "to_yymm"]].to_string(index=False))

# 回测起点所在合约段
from tools.dominant_windows import build_segments_from_map
segs = build_segments_from_map(rm)
for seg in segs:
    s, e = seg.get("start"), seg.get("end")
    if s is None or pd.Timestamp(s) <= pd.Timestamp("2023-05-17"):
        if e is None or pd.Timestamp(e) > pd.Timestamp("2023-05-17"):
            print(f"\n2023-05-17 active segment: yymm={seg['yymm']} start={s} end={e}")
