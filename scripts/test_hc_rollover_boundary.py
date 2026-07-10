# -*- coding: utf-8
"""换月切点前后 bar 连续性 + 与 rb 结构对照。"""
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.tq_rollover_data import build_rollover_events, build_stitched_raw_frame
from tools.dominant_windows import build_segments_from_map, switch_cst

START = pd.Timestamp("2023-05-17", tz="Asia/Shanghai")
END = pd.Timestamp("2026-05-16", tz="Asia/Shanghai")

for sym in ("hc", "rb"):
    df = build_stitched_raw_frame(sym)
    events = build_rollover_events(sym, start=START.to_pydatetime(), end=END.to_pydatetime())
    print(f"\n=== {sym} rollover boundary check ===")
    for ev in events[:3]:
        sw = pd.Timestamp(ev.switch_time).tz_convert("Asia/Shanghai")
        around = df[(df["dt_cst"] >= sw - pd.Timedelta(hours=2)) &
                    (df["dt_cst"] <= sw + pd.Timedelta(hours=2))]
        print(f"  {ev.from_yymm}->{ev.to_yymm} @ {sw}")
        for _, r in around.tail(6).iterrows():
            print(f"    {r.dt_cst} yymm={r.yymm} O={r.open:.0f} C={r.close:.0f} V={r.volume:.0f}")

# 段覆盖：回测窗内每段 bar 数
rm = pd.read_parquet("data/tq/hc/rollover_map.parquet")
segs = build_segments_from_map(rm)
df = build_stitched_raw_frame("hc")
print("\n=== hc segments in backtest window ===")
for seg in segs:
    part = df[(df["dt_cst"] >= pd.Timestamp(seg["start"], tz="Asia/Shanghai")) &
              (df["dt_cst"] < pd.Timestamp(seg["end"], tz="Asia/Shanghai"))]
    if part.empty:
        continue
    if part["dt_cst"].max() < START or part["dt_cst"].min() > END:
        continue
    print(f"  {seg['yymm']:4s} bars={len(part):6d}  {part['dt_cst'].min()} ~ {part['dt_cst'].max()}")

# manifest 异常：2210 提前结束
import json
man = json.loads(Path("data/tq/hc/manifest.json").read_text(encoding="utf-8"))
for k, v in man.items():
    if k.startswith("hc_2210"):
        print(f"\nmanifest hc_2210: end={v.get('end_date')} (回测窗外，仅记录)")
