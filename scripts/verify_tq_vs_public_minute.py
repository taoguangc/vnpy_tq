"""抽样比对 data/tq 分月 1m 与公开源（新浪财经）是否一致。

方法:
  - 每年随机抽 3 处、每处连续 5 根 1 分钟 K（可复现 seed）
  - 优先用新浪分钟线（futures_zh_minute_sina）；时间戳按 bar 结束时刻对齐（新浪-1min）
  - 若该年本地与新浪分钟无交集（常见于主力截断早于新浪保留窗），则回退日线对照

用法:
  .venv/Scripts/python.exe scripts/verify_tq_vs_public_minute.py
  .venv/Scripts/python.exe scripts/verify_tq_vs_public_minute.py --symbols rb i ma ta --seed 42
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import akshare as ak
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.tq_parquet_io import load_monthly_parquet

DATA_ROOT = ROOT / "data" / "tq"
SINA_SHIFT = pd.Timedelta(minutes=-1)  # 新浪多为 bar 结束时刻；TQ 为 bar 开始
PRICE_TOL = 1e-9
VOL_TOL = 1  # 成交量允许 ±1（公开源常见四舍五入/边界差）


@dataclass
class BarCompare:
    symbol: str
    year: int
    sample_id: int
    mode: str  # minute | daily
    contract: str
    dt: str
    open_loc: float
    open_pub: float
    high_loc: float
    high_pub: float
    low_loc: float
    low_pub: float
    close_loc: float
    close_pub: float
    volume_loc: float
    volume_pub: float
    ohlc_match: bool
    close_match: bool
    volume_match: bool


def _prefix_dir(prefix: str) -> Path:
    return DATA_ROOT / prefix.lower()


def _monthly_files(prefix: str) -> list[tuple[str, Path]]:
    d = _prefix_dir(prefix)
    if not d.is_dir():
        return []
    out: list[tuple[str, Path]] = []
    for p in sorted(d.glob("*.parquet")):
        name = p.name
        if "continuous" in name or name.startswith("rollover_") or "_part_" in name:
            continue
        # rb_2505.parquet / MA_2505.parquet
        stem = name[:-8] if name.endswith(".parquet") else name
        parts = stem.split("_")
        if len(parts) < 2:
            continue
        yymm = parts[-1]
        if not yymm.isdigit() or len(yymm) not in (3, 4):
            continue
        if len(yymm) == 3:
            # CZCE legacy 3-digit unlikely in this repo; skip
            continue
        out.append((yymm, p))
    return out


def _sina_symbol(prefix: str, yymm: str) -> str:
    p = prefix.lower()
    if p in {"ma", "ta", "sr", "cf", "rm", "oi", "fg", "sa", "ur", "ap", "pf", "sf", "sm", "zc"}:
        return f"{p.upper()}{yymm}"
    return f"{p.upper()}{yymm}"


def _load_local(path: Path, yymm: str) -> pd.DataFrame:
    df = load_monthly_parquet(str(path), yymm=yymm)
    if df is None or len(df) == 0:
        return pd.DataFrame()
    dt = (
        pd.to_datetime(df["datetime"], unit="ns", utc=True)
        .dt.tz_convert("Asia/Shanghai")
        .dt.tz_localize(None)
    )
    out = df.copy()
    out["dt_sh"] = dt
    return out


def _fetch_sina_minute(symbol: str, sleep_s: float = 0.35) -> pd.DataFrame:
    time.sleep(sleep_s)
    try:
        raw = ak.futures_zh_minute_sina(symbol=symbol, period="1")
    except Exception:
        return pd.DataFrame()
    if raw is None or len(raw) == 0:
        return pd.DataFrame()
    out = raw.copy()
    out["datetime"] = pd.to_datetime(out["datetime"]) + SINA_SHIFT
    rename = {
        "open": "open_pub",
        "high": "high_pub",
        "low": "low_pub",
        "close": "close_pub",
        "volume": "volume_pub",
    }
    out = out.rename(columns=rename)
    return out[["datetime", "open_pub", "high_pub", "low_pub", "close_pub", "volume_pub"]]


def _fetch_sina_daily(symbol: str, sleep_s: float = 0.35) -> pd.DataFrame:
    time.sleep(sleep_s)
    try:
        raw = ak.futures_zh_daily_sina(symbol=symbol)
    except Exception:
        return pd.DataFrame()
    if raw is None or len(raw) == 0:
        return pd.DataFrame()
    out = raw.copy()
    out["date"] = pd.to_datetime(out["date"]).dt.normalize()
    return out.rename(
        columns={
            "open": "open_pub",
            "high": "high_pub",
            "low": "low_pub",
            "close": "close_pub",
            "volume": "volume_pub",
        }
    )


def _years_in_local(frames: list[pd.DataFrame]) -> list[int]:
    years: set[int] = set()
    for df in frames:
        if df.empty:
            continue
        years.update(int(y) for y in df["dt_sh"].dt.year.unique())
    return sorted(years)


def _overlap_minute(local: pd.DataFrame, pub: pd.DataFrame) -> pd.DataFrame:
    if local.empty or pub.empty:
        return pd.DataFrame()
    m = local.merge(pub, left_on="dt_sh", right_on="datetime", how="inner")
    return m.sort_values("dt_sh").reset_index(drop=True)


def _price_eq(a: float, b: float) -> bool:
    return abs(float(a) - float(b)) <= PRICE_TOL


def _vol_eq(a: float, b: float) -> bool:
    return abs(float(a) - float(b)) <= VOL_TOL


def _consecutive_starts(sub: pd.DataFrame, window: int) -> list[int]:
    """返回起点下标：其后 window 根在时钟上严格每分钟连续。"""
    if len(sub) < window:
        return []
    dts = sub["dt_sh"].to_numpy()
    starts: list[int] = []
    for i in range(len(sub) - window + 1):
        ok = True
        for j in range(window - 1):
            if pd.Timestamp(dts[i + j + 1]) - pd.Timestamp(dts[i + j]) != pd.Timedelta(minutes=1):
                ok = False
                break
        if ok:
            starts.append(i)
    return starts


def _sample_minute_windows(
    overlap: pd.DataFrame,
    year: int,
    n_windows: int,
    window: int,
    rng: np.random.Generator,
) -> list[pd.DataFrame]:
    sub = overlap[overlap["dt_sh"].dt.year == year].reset_index(drop=True)
    starts = _consecutive_starts(sub, window)
    if not starts or n_windows <= 0:
        return []
    # 按时间分散：把合法起点分成 n 段，段内随机
    picks: list[int] = []
    n = len(starts)
    for i in range(n_windows):
        lo = int(i * n / n_windows)
        hi = int((i + 1) * n / n_windows) - 1
        if hi < lo:
            hi = lo
        picks.append(starts[int(rng.integers(lo, hi + 1))])
    # 去重后若不足，从剩余合法起点补齐
    uniq = list(dict.fromkeys(picks))
    remain = [s for s in starts if s not in uniq]
    rng.shuffle(remain)
    for s in remain:
        if len(uniq) >= n_windows:
            break
        uniq.append(s)
    return [sub.iloc[s : s + window].copy() for s in uniq[:n_windows]]


def _agg_local_daily(local: pd.DataFrame) -> pd.DataFrame:
    """按日历日聚合日盘(09-15)分钟线，作日线粗对照（不含夜盘归属精细化）。"""
    day = local[local["dt_sh"].dt.hour.between(9, 14)].copy()
    if day.empty:
        return pd.DataFrame()
    day["date"] = day["dt_sh"].dt.normalize()
    g = (
        day.groupby("date", as_index=False)
        .agg(
            open=("open", "first"),
            high=("high", "max"),
            low=("low", "min"),
            close=("close", "last"),
            volume=("volume", "sum"),
        )
        .sort_values("date")
        .reset_index(drop=True)
    )
    return g


def _sample_daily_days(
    merged: pd.DataFrame,
    year: int,
    n: int,
    rng: np.random.Generator,
) -> pd.DataFrame:
    sub = merged[merged["date"].dt.year == year].reset_index(drop=True)
    if sub.empty:
        return sub
    k = min(n, len(sub))
    idx = sorted(rng.choice(len(sub), size=k, replace=False).tolist())
    return sub.iloc[idx].copy()


def verify_symbol(
    prefix: str,
    seed: int,
    n_windows: int = 3,
    window: int = 5,
) -> tuple[list[BarCompare], dict]:
    files = _monthly_files(prefix)
    summary = {
        "prefix": prefix,
        "contracts_local": len(files),
        "years": [],
        "minute_years": [],
        "daily_fallback_years": [],
        "no_public_years": [],
        "bars_compared": 0,
        "ohlc_match": 0,
        "close_match": 0,
        "volume_match": 0,
    }
    if not files:
        return [], summary

    locals_by_yymm: dict[str, pd.DataFrame] = {}
    for yymm, path in files:
        locals_by_yymm[yymm] = _load_local(path, yymm)

    years = _years_in_local(list(locals_by_yymm.values()))
    summary["years"] = years
    rng = np.random.default_rng(seed + sum(ord(c) for c in prefix))

    rows: list[BarCompare] = []
    sina_minute_cache: dict[str, pd.DataFrame] = {}
    sina_daily_cache: dict[str, pd.DataFrame] = {}

    for year in years:
        # 找该年分钟重叠最大的合约
        best_yymm = None
        best_overlap = pd.DataFrame()
        for yymm, loc in locals_by_yymm.items():
            if loc.empty:
                continue
            if not ((loc["dt_sh"].dt.year == year).any()):
                continue
            sym = _sina_symbol(prefix, yymm)
            if sym not in sina_minute_cache:
                sina_minute_cache[sym] = _fetch_sina_minute(sym)
            ov = _overlap_minute(loc, sina_minute_cache[sym])
            ov_y = ov[ov["dt_sh"].dt.year == year] if not ov.empty else ov
            if len(ov_y) > len(best_overlap):
                best_overlap = ov_y.reset_index(drop=True)
                best_yymm = yymm

        used_minute = False
        if best_yymm is not None and len(best_overlap) >= window:
            windows = _sample_minute_windows(best_overlap, year, n_windows, window, rng)
            if windows:
                used_minute = True
                summary["minute_years"].append(year)
                contract = _sina_symbol(prefix, best_yymm)
                for sid, wdf in enumerate(windows, start=1):
                    for _, r in wdf.iterrows():
                        ohlc_ok = all(
                            _price_eq(r[f"{c}"], r[f"{c}_pub"])
                            for c in ("open", "high", "low", "close")
                        )
                        close_ok = _price_eq(r["close"], r["close_pub"])
                        vol_ok = _vol_eq(r["volume"], r["volume_pub"])
                        rows.append(
                            BarCompare(
                                symbol=prefix,
                                year=year,
                                sample_id=sid,
                                mode="minute",
                                contract=contract,
                                dt=str(r["dt_sh"]),
                                open_loc=float(r["open"]),
                                open_pub=float(r["open_pub"]),
                                high_loc=float(r["high"]),
                                high_pub=float(r["high_pub"]),
                                low_loc=float(r["low"]),
                                low_pub=float(r["low_pub"]),
                                close_loc=float(r["close"]),
                                close_pub=float(r["close_pub"]),
                                volume_loc=float(r["volume"]),
                                volume_pub=float(r["volume_pub"]),
                                ohlc_match=ohlc_ok,
                                close_match=close_ok,
                                volume_match=vol_ok,
                            )
                        )

        if used_minute:
            continue

        # 日线回退：选该年本地覆盖最长的合约
        cand = []
        for yymm, loc in locals_by_yymm.items():
            if loc.empty:
                continue
            n = int((loc["dt_sh"].dt.year == year).sum())
            if n > 0:
                cand.append((n, yymm, loc))
        if not cand:
            summary["no_public_years"].append(year)
            continue
        cand.sort(reverse=True)
        _, yymm, loc = cand[0]
        sym = _sina_symbol(prefix, yymm)
        if sym not in sina_daily_cache:
            sina_daily_cache[sym] = _fetch_sina_daily(sym)
        daily_pub = sina_daily_cache[sym]
        daily_loc = _agg_local_daily(loc)
        if daily_loc.empty or daily_pub.empty:
            summary["no_public_years"].append(year)
            continue
        merged = daily_loc.merge(daily_pub, on="date", how="inner", suffixes=("_loc", "_pub"))
        # merge 后本地列无 suffix（open/high/...），公开为 *_pub
        picked = _sample_daily_days(merged, year, n_windows, rng)
        if picked.empty:
            summary["no_public_years"].append(year)
            continue
        summary["daily_fallback_years"].append(year)
        for sid, (_, r) in enumerate(picked.iterrows(), start=1):
            ohlc_ok = all(
                _price_eq(r[c], r[f"{c}_pub"]) for c in ("open", "high", "low", "close")
            )
            close_ok = _price_eq(r["close"], r["close_pub"])
            vol_ok = _vol_eq(r["volume"], r["volume_pub"])
            rows.append(
                BarCompare(
                    symbol=prefix,
                    year=year,
                    sample_id=sid,
                    mode="daily",
                    contract=sym,
                    dt=str(pd.Timestamp(r["date"]).date()),
                    open_loc=float(r["open"]),
                    open_pub=float(r["open_pub"]),
                    high_loc=float(r["high"]),
                    high_pub=float(r["high_pub"]),
                    low_loc=float(r["low"]),
                    low_pub=float(r["low_pub"]),
                    close_loc=float(r["close"]),
                    close_pub=float(r["close_pub"]),
                    volume_loc=float(r["volume"]),
                    volume_pub=float(r["volume_pub"]),
                    ohlc_match=ohlc_ok,
                    close_match=close_ok,
                    volume_match=vol_ok,
                )
            )

    summary["bars_compared"] = len(rows)
    summary["ohlc_match"] = sum(1 for r in rows if r.ohlc_match)
    summary["close_match"] = sum(1 for r in rows if r.close_match)
    summary["volume_match"] = sum(1 for r in rows if r.volume_match)
    return rows, summary


def _print_report(rows: list[BarCompare], summaries: list[dict]) -> None:
    print("=" * 72)
    print("TQ 离线 1m vs 公开源（新浪）抽样验证")
    print("对齐: 新浪 datetime + (-1min) ↔ TQ bar 开始时刻")
    print("分钟源限约 1023 根/合约；无交集年份回退日线（日盘聚合，粗对照）")
    print("=" * 72)
    for s in summaries:
        n = s["bars_compared"]
        ohlc = s["ohlc_match"]
        close = s["close_match"]
        vol = s["volume_match"]
        print(
            f"\n[{s['prefix']}] 合约文件={s['contracts_local']} 年份={s['years']}\n"
            f"  分钟验证年={s['minute_years']}  日线回退年={s['daily_fallback_years']}  "
            f"无公开对照年={s['no_public_years']}\n"
            f"  比对条数={n}  OHLC全同={ohlc}/{n}  close同={close}/{n}  volume±{VOL_TOL}={vol}/{n}"
        )

    # 展示每处抽样的简表
    if not rows:
        print("\n无比对结果")
        return
    df = pd.DataFrame([asdict(r) for r in rows])
    for (sym, year, mode, sid), g in df.groupby(
        ["symbol", "year", "mode", "sample_id"], sort=True
    ):
        flag = "OK" if g["close_match"].all() else "DIFF"
        print(
            f"\n--- {sym} {year} sample#{sid} mode={mode} contract={g['contract'].iloc[0]} "
            f"close_all_match={flag} ---"
        )
        show = g[
            [
                "dt",
                "open_loc",
                "open_pub",
                "high_loc",
                "high_pub",
                "low_loc",
                "low_pub",
                "close_loc",
                "close_pub",
                "volume_loc",
                "volume_pub",
                "ohlc_match",
                "close_match",
            ]
        ]
        print(show.to_string(index=False))


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify TQ parquet vs public (Sina) samples")
    ap.add_argument("--symbols", nargs="+", default=["rb", "i", "ma", "ta"])
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--windows", type=int, default=3, help="每年份抽样处数")
    ap.add_argument("--bars", type=int, default=5, help="每处连续 1m 根数")
    ap.add_argument(
        "--csv",
        type=Path,
        default=ROOT / "_tmp_verify_tq_public.csv",
        help="明细 CSV 输出路径",
    )
    args = ap.parse_args()

    all_rows: list[BarCompare] = []
    summaries: list[dict] = []
    for sym in args.symbols:
        print(f"\n>> verifying {sym} ...", flush=True)
        rows, summary = verify_symbol(
            sym, seed=args.seed, n_windows=args.windows, window=args.bars
        )
        all_rows.extend(rows)
        summaries.append(summary)

    _print_report(all_rows, summaries)

    out = pd.DataFrame([asdict(r) for r in all_rows])
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.csv, index=False, encoding="utf-8-sig")
    summary_path = args.csv.with_suffix(".summary.json")
    summary_path.write_text(
        json.dumps(summaries, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n明细: {args.csv}")
    print(f"摘要: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
