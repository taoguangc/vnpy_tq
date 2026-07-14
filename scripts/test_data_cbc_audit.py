# -*- coding: utf-8
"""CbC 拼接层 + 换月成本 全品种快速审计（一次性诊断）。"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.tq_rollover_data import build_rollover_events, build_stitched_raw_frame
from strategies.pa_cta.symbol_config import resolve_symbol_profile, resolve_tq_cbc_paths

START = datetime(2023, 5, 17)
END = datetime(2026, 5, 16)
SYMS = sorted([d.name for d in (ROOT / "data" / "tq").iterdir() if d.is_dir()])


def audit_symbol(sym: str) -> dict:
    p = resolve_symbol_profile(sym, ROOT)
    stem = p["file_stem"]
    data_dir, _ = resolve_tq_cbc_paths(p)
    out = {"symbol": sym, "error": ""}
    try:
        df = build_stitched_raw_frame(stem)
    except Exception as e:
        out["error"] = str(e)
        return out
    df = df[
        (df["dt_cst"] >= pd.Timestamp(START, tz="Asia/Shanghai"))
        & (df["dt_cst"] <= pd.Timestamp(END, tz="Asia/Shanghai"))
    ].copy()
    dts = df["dt_cst"].sort_values()
    gaps = dts.diff().dt.total_seconds().fillna(0)
    out.update(
        {
            "bars": len(df),
            "dup_ts": int(df["dt_cst"].duplicated().sum()),
            "bad_hl": int((df["high"] < df["low"]).sum()),
            "bad_oc": int(
                (
                    (df["open"] > df["high"])
                    | (df["open"] < df["low"])
                    | (df["close"] > df["high"])
                    | (df["close"] < df["low"])
                ).sum()
            ),
            "zero_vol": int((df["volume"] == 0).sum()),
            "gap_gt_15m": int((gaps > 900).sum()),
            "rollover_n": len(build_rollover_events(stem, start=START, end=END)),
            "has_cost": (data_dir / "rollover_cost_detail.parquet").exists(),
            "has_map": (data_dir / "rollover_map.parquet").exists(),
        }
    )
    if out["has_cost"]:
        cdf = pd.read_parquet(data_dir / "rollover_cost_detail.parquet")
        out["cost_rows"] = len(cdf)
        out["cost_slip_nz"] = int(cdf.get("slippage_cost", pd.Series(dtype=float)).fillna(0).ne(0).sum())
        out["cost_comm_nz"] = int(cdf.get("commission_cost", pd.Series(dtype=float)).fillna(0).ne(0).sum())
    else:
        out["cost_rows"] = 0
        out["cost_slip_nz"] = 0
        out["cost_comm_nz"] = 0
    return out


def main() -> None:
    print(f"=== CbC 拼接层诊断 | {START.date()} ~ {END.date()} ===\n")
    rows = [audit_symbol(s) for s in SYMS]
    hdr = (
        f"{'sym':<6} {'bars':>8} {'dup':>5} {'badHL':>6} {'badOC':>6} "
        f"{'zeroV':>6} {'gap15':>6} {'rol':>4} {'map':>4} {'cost':>5} "
        f"{'slip':>5} {'err'}"
    )
    print(hdr)
    print("-" * len(hdr))
    issues = []
    for r in rows:
        if r.get("error"):
            print(f"{r['symbol']:<6} ERROR: {r['error']}")
            issues.append((r["symbol"], r["error"]))
            continue
        ok = (
            r["dup_ts"] == 0
            and r["bad_hl"] == 0
            and r["bad_oc"] == 0
            and r["has_map"]
        )
        flag = "" if ok else "!"
        print(
            f"{r['symbol']:<6} {r['bars']:>8} {r['dup_ts']:>5} {r['bad_hl']:>6} {r['bad_oc']:>6} "
            f"{r['zero_vol']:>6} {r['gap_gt_15m']:>6} {r['rollover_n']:>4} "
            f"{'Y' if r['has_map'] else 'N':>4} {'Y' if r['has_cost'] else 'N':>5} "
            f"{r['cost_slip_nz']:>5}{flag}"
        )
        if not r["has_cost"]:
            issues.append((r["symbol"], "缺 rollover_cost_detail.parquet"))
        elif r["cost_slip_nz"] == 0:
            issues.append((r["symbol"], "rollover_cost_detail 滑点全 0"))
        if r["dup_ts"] or r["bad_hl"] or r["bad_oc"]:
            issues.append((r["symbol"], "OHLC/重复时间戳异常"))
        if r["gap_gt_15m"] > 500:
            issues.append((r["symbol"], f"大缺口过多 gap>15m={r['gap_gt_15m']}"))
    print("\n=== 问题汇总 ===")
    if not issues:
        print("未发现阻塞性问题")
    else:
        for sym, msg in issues:
            print(f"  {sym}: {msg}")


if __name__ == "__main__":
    main()
