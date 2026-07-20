"""批量验证 data/tq 分月数据 vs 公开源（新浪分钟/日线 + 交易所日线）。

对每个品种、每个日历年：
  1) 优先新浪 1m（对齐 -1min），抽 3×连续 5 根
  2) 无分钟交集则新浪日线抽 3 日（日盘聚合 close）
  3) CZCE/SHFE 另抽 3 日对照交易所 get_futures_daily（更权威）

用法:
  .venv/Scripts/python.exe scripts/verify_tq_public_batch.py
  .venv/Scripts/python.exe scripts/verify_tq_public_batch.py --skip rb i ma ta
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
SINA_SHIFT = pd.Timedelta(minutes=-1)
CZCE = {"ma", "ta", "fg", "sa", "rm", "sr", "cf", "oi", "ur", "ap", "pf", "sf", "sm", "zc"}
SHFE = {
    "rb", "hc", "cu", "al", "zn", "pb", "sn", "ni", "ss", "ag", "au",
    "ru", "nr", "bu", "sp", "fu", "ao",
}
DCE = {"m", "i", "c", "p", "y", "a", "b", "j", "jm", "l", "v", "pp", "eb", "eg", "pg"}


@dataclass
class SampleRow:
    symbol: str
    year: int
    source: str  # sina_minute | sina_daily | exchange_daily
    contract: str
    sample_id: int
    dt: str
    close_loc: float
    close_pub: float
    close_match: bool
    close_within_1tick: bool
    ohlc_match: bool


def _resolve_dir(prefix: str) -> Path | None:
    p = DATA_ROOT / prefix
    if p.is_dir():
        return p
    low = DATA_ROOT / prefix.lower()
    if low.is_dir():
        return low
    for d in DATA_ROOT.iterdir():
        if d.is_dir() and d.name.lower() == prefix.lower():
            return d
    return None


def _monthly_files(prefix: str) -> list[tuple[str, Path]]:
    d = _resolve_dir(prefix)
    if d is None:
        return []
    out: list[tuple[str, Path]] = []
    for p in sorted(d.glob("*.parquet")):
        name = p.name
        if any(x in name for x in ("continuous", "rollover_", "_part_", "tick")):
            continue
        stem = name[:-8]
        parts = stem.split("_")
        if len(parts) < 2:
            continue
        yymm = parts[-1]
        if yymm.isdigit() and len(yymm) == 4:
            out.append((yymm, p))
    return out


def _sina_sym(prefix: str, yymm: str) -> str:
    p = prefix.lower()
    if p in CZCE:
        return f"{p.upper()}{yymm}"
    return f"{p.upper()}{yymm}"


def _exch_sym(prefix: str, yymm: str) -> str:
    """交易所日行情合约代码：CZCE 用三位年码 TA505；SHFE/DCE 用小写+四位。"""
    p = prefix.lower()
    if p in CZCE:
        return f"{p.upper()}{yymm[1]}{yymm[2:]}"
    return f"{p.lower()}{yymm}"


def _market(prefix: str) -> str | None:
    p = prefix.lower()
    if p in CZCE:
        return "CZCE"
    if p in SHFE:
        return "SHFE"
    if p in DCE:
        return "DCE"
    return None


def _tick(prefix: str) -> float:
    p = prefix.lower()
    if p in {"i", "j", "jm", "m", "p", "y", "a", "c", "l", "v"}:
        return 0.5 if p == "i" else 1.0
    if p in {"ag"}:
        return 1.0
    if p in {"au"}:
        return 0.02
    if p in {"al", "zn", "pb", "sn"}:
        return 5.0
    return 1.0


def _load_local(path: Path, yymm: str) -> pd.DataFrame:
    df = load_monthly_parquet(str(path), yymm=yymm)
    if df is None or len(df) == 0:
        return pd.DataFrame()
    dt = (
        pd.to_datetime(df["datetime"], unit="ns", utc=True)
        .dt.tz_convert("Asia/Shanghai")
        .dt.tz_localize(None)
    )
    return df.assign(dt_sh=dt)


def _day_agg(df: pd.DataFrame) -> pd.DataFrame:
    day = df[df["dt_sh"].dt.hour.between(9, 14)].copy()
    if day.empty:
        return pd.DataFrame()
    day["date"] = day["dt_sh"].dt.normalize()
    return (
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


def _fetch_sina_minute(sym: str, cache: dict[str, pd.DataFrame]) -> pd.DataFrame:
    if sym in cache:
        return cache[sym]
    time.sleep(0.25)
    try:
        raw = ak.futures_zh_minute_sina(symbol=sym, period="1")
    except Exception:
        cache[sym] = pd.DataFrame()
        return cache[sym]
    if raw is None or len(raw) == 0:
        cache[sym] = pd.DataFrame()
        return cache[sym]
    out = raw.copy()
    out["datetime"] = pd.to_datetime(out["datetime"]) + SINA_SHIFT
    out = out.rename(
        columns={
            "open": "open_pub",
            "high": "high_pub",
            "low": "low_pub",
            "close": "close_pub",
            "volume": "volume_pub",
        }
    )
    cache[sym] = out[["datetime", "open_pub", "high_pub", "low_pub", "close_pub", "volume_pub"]]
    return cache[sym]


def _fetch_sina_daily(sym: str, cache: dict[str, pd.DataFrame]) -> pd.DataFrame:
    if sym in cache:
        return cache[sym]
    time.sleep(0.25)
    try:
        raw = ak.futures_zh_daily_sina(symbol=sym)
    except Exception:
        cache[sym] = pd.DataFrame()
        return cache[sym]
    if raw is None or len(raw) == 0:
        cache[sym] = pd.DataFrame()
        return cache[sym]
    out = raw.copy()
    out["date"] = pd.to_datetime(out["date"]).dt.normalize()
    cache[sym] = out.rename(
        columns={
            "open": "open_pub",
            "high": "high_pub",
            "low": "low_pub",
            "close": "close_pub",
            "volume": "volume_pub",
        }
    )
    return cache[sym]


def _fetch_exchange_day(market: str, d: pd.Timestamp, cache: dict[str, pd.DataFrame]) -> pd.DataFrame:
    key = f"{market}:{d.strftime('%Y%m%d')}"
    if key in cache:
        return cache[key]
    time.sleep(0.2)
    try:
        raw = ak.get_futures_daily(
            start_date=d.strftime("%Y%m%d"),
            end_date=d.strftime("%Y%m%d"),
            market=market,
        )
    except Exception:
        cache[key] = pd.DataFrame()
        return cache[key]
    cache[key] = raw if raw is not None else pd.DataFrame()
    return cache[key]


def _consec_starts(sub: pd.DataFrame, window: int) -> list[int]:
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


def _pick_windows(sub: pd.DataFrame, n: int, window: int, rng: np.random.Generator) -> list[pd.DataFrame]:
    starts = _consec_starts(sub, window)
    if not starts:
        return []
    picks: list[int] = []
    m = len(starts)
    for i in range(n):
        lo = int(i * m / n)
        hi = max(lo, int((i + 1) * m / n) - 1)
        picks.append(starts[int(rng.integers(lo, hi + 1))])
    uniq = list(dict.fromkeys(picks))
    remain = [s for s in starts if s not in uniq]
    rng.shuffle(remain)
    uniq.extend(remain[: max(0, n - len(uniq))])
    return [sub.iloc[s : s + window].copy() for s in uniq[:n]]


def _row(
    symbol: str,
    year: int,
    source: str,
    contract: str,
    sid: int,
    dt: str,
    loc: dict,
    pub: dict,
    tick: float,
) -> SampleRow:
    close_m = abs(float(loc["close"]) - float(pub["close"])) <= 1e-9
    within = abs(float(loc["close"]) - float(pub["close"])) <= tick + 1e-9
    ohlc = all(abs(float(loc[c]) - float(pub[c])) <= 1e-9 for c in ("open", "high", "low", "close"))
    return SampleRow(
        symbol=symbol,
        year=year,
        source=source,
        contract=contract,
        sample_id=sid,
        dt=dt,
        close_loc=float(loc["close"]),
        close_pub=float(pub["close"]),
        close_match=close_m,
        close_within_1tick=within,
        ohlc_match=ohlc,
    )


def verify_symbol(
    prefix: str,
    seed: int,
    n_windows: int = 3,
    window: int = 5,
    sina_min_cache: dict | None = None,
    sina_day_cache: dict | None = None,
    exch_cache: dict | None = None,
) -> tuple[list[SampleRow], dict]:
    sina_min_cache = sina_min_cache if sina_min_cache is not None else {}
    sina_day_cache = sina_day_cache if sina_day_cache is not None else {}
    exch_cache = exch_cache if exch_cache is not None else {}
    files = _monthly_files(prefix)
    summary = {
        "symbol": prefix,
        "contracts": len(files),
        "years": [],
        "minute_years": [],
        "sina_daily_years": [],
        "exchange_years": [],
        "no_public_years": [],
        "minute_close": [0, 0],
        "minute_within_1tick": [0, 0],
        "sina_daily_close": [0, 0],
        "exchange_close": [0, 0],
    }
    if not files:
        return [], summary

    locals_map: dict[str, pd.DataFrame] = {}
    ranges: list[tuple[str, pd.Timestamp, pd.Timestamp]] = []
    for yymm, path in files:
        df = _load_local(path, yymm)
        if df.empty:
            continue
        locals_map[yymm] = df
        ranges.append((yymm, df["dt_sh"].min(), df["dt_sh"].max()))

    years = sorted({int(y) for _, a, b in ranges for y in (a.year, b.year)} | set())
    # years that actually have bars
    year_set: set[int] = set()
    for df in locals_map.values():
        year_set.update(int(x) for x in df["dt_sh"].dt.year.unique())
    years = sorted(year_set)
    summary["years"] = years
    rng = np.random.default_rng(seed + sum(ord(c) for c in prefix.lower()))
    tick = _tick(prefix)
    market = _market(prefix)
    rows: list[SampleRow] = []

    for year in years:
        # candidates: local coverage in year, prefer later end (near delivery / sina window)
        cands = []
        for yymm, df in locals_map.items():
            mask = df["dt_sh"].dt.year == year
            if not mask.any():
                continue
            cands.append((df.loc[mask, "dt_sh"].max(), yymm, df))
        cands.sort(reverse=True)

        used_minute = False
        for _, yymm, df in cands[:4]:  # 最多试 4 个合约
            sym = _sina_sym(prefix, yymm)
            pub = _fetch_sina_minute(sym, sina_min_cache)
            if pub.empty:
                continue
            m = df.merge(pub, left_on="dt_sh", right_on="datetime", how="inner")
            m = m[m["dt_sh"].dt.year == year].sort_values("dt_sh").reset_index(drop=True)
            if len(m) < window:
                continue
            wins = _pick_windows(m, n_windows, window, rng)
            if not wins:
                continue
            used_minute = True
            summary["minute_years"].append(year)
            for sid, w in enumerate(wins, 1):
                for _, r in w.iterrows():
                    loc = {"open": r["open"], "high": r["high"], "low": r["low"], "close": r["close"]}
                    pubd = {
                        "open": r["open_pub"],
                        "high": r["high_pub"],
                        "low": r["low_pub"],
                        "close": r["close_pub"],
                    }
                    row = _row(prefix, year, "sina_minute", sym, sid, str(r["dt_sh"]), loc, pubd, tick)
                    rows.append(row)
                    summary["minute_close"][1] += 1
                    summary["minute_close"][0] += int(row.close_match)
                    summary["minute_within_1tick"][1] += 1
                    summary["minute_within_1tick"][0] += int(row.close_within_1tick)
            break

        if not used_minute:
            # sina daily fallback on longest local coverage contract that year
            if not cands:
                summary["no_public_years"].append(year)
            else:
                _, yymm, df = cands[0]
                sym = _sina_sym(prefix, yymm)
                daily_pub = _fetch_sina_daily(sym, sina_day_cache)
                daily_loc = _day_agg(df)
                if daily_pub.empty or daily_loc.empty:
                    summary["no_public_years"].append(year)
                else:
                    merged = daily_loc.merge(daily_pub, on="date", how="inner")
                    merged = merged[merged["date"].dt.year == year]
                    if merged.empty:
                        summary["no_public_years"].append(year)
                    else:
                        summary["sina_daily_years"].append(year)
                        k = min(n_windows, len(merged))
                        idx = sorted(rng.choice(len(merged), size=k, replace=False).tolist())
                        for sid, i in enumerate(idx, 1):
                            r = merged.iloc[i]
                            loc = {"open": r["open"], "high": r["high"], "low": r["low"], "close": r["close"]}
                            pubd = {
                                "open": r["open_pub"],
                                "high": r["high_pub"],
                                "low": r["low_pub"],
                                "close": r["close_pub"],
                            }
                            row = _row(
                                prefix, year, "sina_daily", sym, sid,
                                str(pd.Timestamp(r["date"]).date()), loc, pubd, tick,
                            )
                            rows.append(row)
                            summary["sina_daily_close"][1] += 1
                            summary["sina_daily_close"][0] += int(row.close_match)

        # exchange daily (CZCE/SHFE); DCE often broken — still try
        if market in {"CZCE", "SHFE"} and cands:
            _, yymm, df = cands[0]
            daily_loc = _day_agg(df)
            daily_loc = daily_loc[daily_loc["date"].dt.year == year]
            if not daily_loc.empty:
                k = min(n_windows, len(daily_loc))
                idx = sorted(rng.choice(len(daily_loc), size=k, replace=False).tolist())
                esym = _exch_sym(prefix, yymm)
                got = 0
                for sid, i in enumerate(idx, 1):
                    r = daily_loc.iloc[i]
                    d = pd.Timestamp(r["date"])
                    ex = _fetch_exchange_day(market, d, exch_cache)
                    if ex.empty:
                        continue
                    hit = ex[ex["symbol"].astype(str) == esym]
                    if hit.empty and market == "CZCE" and "variety" in ex.columns:
                        hit = ex[
                            (ex["variety"].astype(str).str.upper() == prefix.upper())
                            & (ex["symbol"].astype(str).str.endswith(yymm[1:]))
                        ]
                    if hit.empty:
                        continue
                    er = hit.iloc[0]
                    loc = {"open": r["open"], "high": r["high"], "low": r["low"], "close": r["close"]}
                    pubd = {
                        "open": er["open"],
                        "high": er["high"],
                        "low": er["low"],
                        "close": er["close"],
                    }
                    row = _row(
                        prefix, year, "exchange_daily", esym, sid,
                        str(d.date()), loc, pubd, tick,
                    )
                    rows.append(row)
                    summary["exchange_close"][1] += 1
                    summary["exchange_close"][0] += int(row.close_match)
                    got += 1
                if got:
                    summary["exchange_years"].append(year)

    # dedupe year lists
    for k in ("minute_years", "sina_daily_years", "exchange_years", "no_public_years"):
        summary[k] = sorted(set(summary[k]))
    return rows, summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols", nargs="+", default=None)
    ap.add_argument("--skip", nargs="+", default=["rb", "i", "ma", "ta"])
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", type=Path, default=ROOT / "_tmp_verify_all_public.csv")
    args = ap.parse_args()

    if args.symbols:
        symbols = args.symbols
    else:
        skip = {s.lower() for s in args.skip}
        symbols = sorted(
            p.name for p in DATA_ROOT.iterdir()
            if p.is_dir() and p.name.lower() not in skip
        )

    all_rows: list[SampleRow] = []
    summaries: list[dict] = []
    sina_min: dict = {}
    sina_day: dict = {}
    exch: dict = {}

    print(f"验证品种 ({len(symbols)}): {symbols}", flush=True)
    for sym in symbols:
        print(f"\n>> {sym} ...", flush=True)
        rows, summary = verify_symbol(
            sym, seed=args.seed,
            sina_min_cache=sina_min, sina_day_cache=sina_day, exch_cache=exch,
        )
        all_rows.extend(rows)
        summaries.append(summary)
        mc, mt = summary["minute_close"]
        sc, st = summary["sina_daily_close"]
        ec, et = summary["exchange_close"]
        print(
            f"  years={summary['years']}\n"
            f"  minute_y={summary['minute_years']} close={mc}/{mt} within1={summary['minute_within_1tick'][0]}/{summary['minute_within_1tick'][1]}\n"
            f"  sina_daily_y={summary['sina_daily_years']} close={sc}/{st}\n"
            f"  exchange_y={summary['exchange_years']} close={ec}/{et}\n"
            f"  no_public={summary['no_public_years']}",
            flush=True,
        )

    print("\n" + "=" * 72)
    print(f"{'sym':<6} {'min_close':>10} {'min_1tick':>10} {'sina_d':>10} {'exch_d':>10} {'min_yrs':>8} {'note'}")
    print("-" * 72)
    for s in summaries:
        mc, mt = s["minute_close"]
        wc, wt = s["minute_within_1tick"]
        sc, st = s["sina_daily_close"]
        ec, et = s["exchange_close"]
        note = ""
        if mt and (wc / wt) >= 0.95:
            note = "OK"
        elif st and sc == st:
            note = "OK-daily"
        elif et and (ec / et) >= 0.9:
            note = "OK-exch"
        elif mt == 0 and st == 0 and et == 0:
            note = "NO-PUBLIC"
        else:
            note = "CHECK"
        print(
            f"{s['symbol']:<6} {mc}/{mt!s:>7} {wc}/{wt!s:>7} {sc}/{st!s:>7} {ec}/{et!s:>7} "
            f"{len(s['minute_years']):>8} {note}"
        )

    out = pd.DataFrame([asdict(r) for r in all_rows])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False, encoding="utf-8-sig")
    sp = args.out.with_suffix(".summary.json")
    sp.write_text(json.dumps(summaries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n明细 {args.out}\n摘要 {sp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
