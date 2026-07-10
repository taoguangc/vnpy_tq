"""天勤 tick 流式分片落盘下载器（TqBacktest + get_tick_serial）。

无需 DataDownloader 专业版；边回放边切片落盘，规避 get_tick_serial 滑动窗口上限。

用法:
    .venv/Scripts/python.exe tools/download_tick_streaming.py \\
        --symbol SHFE.rb2301 --start "2023-01-03 09:00:00" --end "2023-01-03 15:00:00"
    .venv/Scripts/python.exe tools/download_tick_streaming.py -s SHFE.rb2301 -r
    .venv/Scripts/python.exe tools/download_tick_streaming.py -s SHFE.rb2301 --merge-only
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from tqsdk import BacktestFinished, TqApi, TqAuth, TqBacktest, TqSim
import pandas as pd

from tools.download_rb_monthly import get_auth
from tools.tq_tick_io import (
    LOCK_FILE,
    MANIFEST_FILE,
    SESSION_NOTE,
    atomic_write_parquet,
    canonical_tick_name,
    contract_tag,
    cst_bounds_ns,
    list_part_files,
    max_datetime_ns,
    normalize_ticks,
    part_tick_name,
    resolve_prefix,
    tick_output_dir_for_prefix,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

FLUSH_EVERY_TICKS = 3000
TICK_WINDOW = 12000
RESUME_OVERLAP = timedelta(hours=1)


def _output_dir(symbol: str) -> Path:
    return tick_output_dir_for_prefix(resolve_prefix(symbol))


def _load_manifest(output_dir: Path) -> dict:
    path = output_dir / MANIFEST_FILE
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_manifest(output_dir: Path, manifest: dict) -> None:
    path = output_dir / MANIFEST_FILE
    tmp = path.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def _slice_new_ticks(
    ticks: pd.DataFrame,
    last_saved_dt: int,
    *,
    start_ns: int = 0,
    end_ns: int | None = None,
    include_last: bool = False,
) -> tuple[pd.DataFrame, int]:
    n = len(ticks)
    if n == 0:
        return pd.DataFrame(), last_saved_dt
    end = n if include_last else n - 1
    if end <= 0:
        return pd.DataFrame(), last_saved_dt
    subset = ticks.iloc[:end]
    chunk = subset[subset["datetime"] > last_saved_dt]
    if start_ns > 0:
        chunk = chunk[chunk["datetime"] >= start_ns]
    if end_ns is not None:
        chunk = chunk[chunk["datetime"] <= end_ns]
    if len(chunk) == 0:
        return pd.DataFrame(), last_saved_dt
    return chunk.copy(), int(chunk["datetime"].max())


def _merge_parts(
    output_dir: Path,
    symbol: str,
    part_files: list[str],
    resume_file: str | None,
) -> pd.DataFrame:
    dfs: list[pd.DataFrame] = []
    if resume_file:
        rp = output_dir / resume_file
        if rp.exists():
            dfs.append(pd.read_parquet(rp))
    for pf in part_files:
        dfs.append(pd.read_parquet(output_dir / pf))
    if not dfs:
        return pd.DataFrame()
    return normalize_ticks(pd.concat(dfs, ignore_index=True))


def _acquire_lock(output_dir: Path, symbol: str) -> None:
    lock = output_dir / LOCK_FILE
    if lock.exists():
        raise RuntimeError(f"下载锁已存在: {lock}（可能另有进程在跑）")
    lock.write_text(
        json.dumps({"symbol": symbol, "pid": os.getpid(), "ts": time.time()}),
        encoding="utf-8",
    )


def _release_lock(output_dir: Path) -> None:
    lock = output_dir / LOCK_FILE
    if lock.exists():
        lock.unlink()


def download_ticks_streaming(
    symbol: str,
    start_dt: datetime,
    end_dt: datetime,
    *,
    resume: bool = False,
    flush_every: int = FLUSH_EVERY_TICKS,
    tick_window: int = TICK_WINDOW,
    keep_parts: bool = False,
    auth: TqAuth | None = None,
    skip_lock: bool = False,
) -> dict:
    if tick_window < flush_every * 2:
        raise ValueError(
            f"tick_window({tick_window}) 应 >= 2 * flush_every({flush_every})"
        )

    auth = auth or get_auth()
    output_dir = _output_dir(symbol)
    output_file = canonical_tick_name(symbol)
    output_path = output_dir / output_file

    part_files = list_part_files(output_dir, symbol)
    part_count = 0
    if part_files:
        part_count = max(int(f.rsplit("_part_", 1)[1].replace(".parquet", "")) for f in part_files)

    last_saved_dt = 0
    resume_source: str | None = None
    backtest_start = start_dt

    if resume and output_path.exists():
        last_saved_dt = max_datetime_ns(output_path)
        resume_source = output_file
        logger.info(
            f"断点续传: 已有 {output_file}, last_dt="
            f"{pd.to_datetime(last_saved_dt, unit='ns', utc=True).tz_convert('Asia/Shanghai')}"
        )
    elif part_files:
        for pf in part_files:
            last_saved_dt = max(last_saved_dt, max_datetime_ns(output_dir / pf))
        logger.info(
            f"从 {len(part_files)} 个未合并分片恢复, last_dt="
            f"{pd.to_datetime(last_saved_dt, unit='ns', utc=True).tz_convert('Asia/Shanghai')}"
        )

    if last_saved_dt > 0:
        last_cst = pd.to_datetime(last_saved_dt, unit="ns", utc=True).tz_convert("Asia/Shanghai")
        backtest_start = (last_cst - RESUME_OVERLAP).to_pydatetime().replace(tzinfo=None)
        backtest_start = max(backtest_start, start_dt)

    start_ns, end_ns = cst_bounds_ns(start_dt, end_dt)

    accumulated: list[pd.DataFrame] = []
    accumulated_rows = 0
    api = None
    ticks = None
    t0 = time.time()

    def _flush() -> None:
        nonlocal accumulated, accumulated_rows, part_count, part_files
        if not accumulated:
            return
        part_count += 1
        df = normalize_ticks(pd.concat(accumulated, ignore_index=True))
        part_file = part_tick_name(symbol, part_count)
        atomic_write_parquet(df, output_dir / part_file)
        part_files.append(part_file)
        accumulated = []
        accumulated_rows = 0
        logger.info(
            f"分片 {part_count}: {len(df)} 行 -> {part_file}, "
            f"末 tick {pd.to_datetime(df['datetime'].iloc[-1], unit='ns', utc=True).tz_convert('Asia/Shanghai')}"
        )

    try:
        api = TqApi(
            TqSim(init_balance=100_000),
            backtest=TqBacktest(start_dt=backtest_start, end_dt=end_dt),
            auth=auth,
            web_gui=False,
        )
        ticks = api.get_tick_serial(symbol, data_length=tick_window)
        saved_total = 0

        while True:
            api.wait_update()
            if len(ticks) == 0 or not api.is_changing(ticks):
                continue
            chunk, last_saved_dt = _slice_new_ticks(
                ticks, last_saved_dt, start_ns=start_ns, end_ns=end_ns,
            )
            if len(chunk) == 0:
                continue
            accumulated.append(chunk)
            accumulated_rows += len(chunk)
            saved_total += len(chunk)
            if saved_total % 5000 < len(chunk):
                logger.info(
                    f"回放中... 新增 {len(chunk)} 条, 缓冲 {accumulated_rows}, "
                    f"last={pd.to_datetime(last_saved_dt, unit='ns', utc=True).tz_convert('Asia/Shanghai')}"
                )
            if accumulated_rows >= flush_every:
                _flush()

    except BacktestFinished:
        if ticks is not None and len(ticks) > 0:
            chunk, last_saved_dt = _slice_new_ticks(
                ticks, last_saved_dt, start_ns=start_ns, end_ns=end_ns, include_last=True,
            )
            if len(chunk) > 0:
                accumulated.append(chunk)
                accumulated_rows += len(chunk)
    except Exception:
        if accumulated:
            try:
                _flush()
            except Exception:
                pass
        raise
    finally:
        if api:
            api.close()

    if accumulated:
        _flush()

    if not part_files and not output_path.exists():
        return {"status": "empty", "rows": 0, "file": output_file, "elapsed": time.time() - t0}

    full_df = _merge_parts(output_dir, symbol, part_files, resume_source)
    if not keep_parts:
        atomic_write_parquet(full_df, output_path)
        for pf in part_files:
            try:
                (output_dir / pf).unlink()
            except OSError:
                pass
        part_files = []

    rows = len(full_df)
    dt_min = pd.to_datetime(full_df["datetime"].iloc[0], unit="ns", utc=True).tz_convert("Asia/Shanghai")
    dt_max = pd.to_datetime(full_df["datetime"].iloc[-1], unit="ns", utc=True).tz_convert("Asia/Shanghai")

    manifest = _load_manifest(output_dir)
    manifest.setdefault("_meta", {})["session_note"] = SESSION_NOTE
    manifest.setdefault("_meta", {})["datetime_unit"] = "ns_utc"
    manifest[output_file] = {
        "symbol": symbol,
        "rows": rows,
        "start_date": dt_min.isoformat(),
        "end_date": dt_max.isoformat(),
        "download_time": datetime.now().isoformat(),
        "size_mb": round(output_path.stat().st_size / (1024 * 1024), 3) if output_path.exists() else 0,
        "flush_every": flush_every,
        "tick_window": tick_window,
        "keep_parts": keep_parts,
    }
    _save_manifest(output_dir, manifest)

    elapsed = time.time() - t0
    logger.info(f"完成 {output_file}: {rows:,} tick, {dt_min} ~ {dt_max}, 耗时 {elapsed:.1f}s")
    return {
        "status": "ok",
        "file": output_file,
        "rows": rows,
        "start": str(dt_min),
        "end": str(dt_max),
        "elapsed": elapsed,
    }


def merge_parts_only(symbol: str) -> dict:
    output_dir = _output_dir(symbol)
    output_file = canonical_tick_name(symbol)
    output_path = output_dir / output_file
    part_files = list_part_files(output_dir, symbol)
    if not part_files:
        raise SystemExit("无未合并分片")
    resume_source = output_file if output_path.exists() else None
    full_df = _merge_parts(output_dir, symbol, part_files, resume_source)
    atomic_write_parquet(full_df, output_path)
    for pf in part_files:
        (output_dir / pf).unlink(missing_ok=True)
    logger.info(f"合并完成: {output_file}, {len(full_df):,} 行")
    return {"status": "merged", "rows": len(full_df), "file": output_file}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="天勤 tick 流式分片下载")
    p.add_argument("-s", "--symbol", default="SHFE.rb2301", help="合约，如 SHFE.rb2301")
    p.add_argument("--start", default="2023-01-03 09:00:00", help="起始（北京时间）")
    p.add_argument("--end", default="2023-01-03 15:00:00", help="结束（北京时间）")
    p.add_argument("-r", "--resume", action="store_true", help="断点续传")
    p.add_argument("--merge-only", action="store_true", help="仅合并 orphan 分片")
    p.add_argument("--flush-every", type=int, default=FLUSH_EVERY_TICKS)
    p.add_argument("--tick-window", type=int, default=TICK_WINDOW)
    p.add_argument("--keep-parts", action="store_true", help="合并后保留分片")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if args.merge_only:
        merge_parts_only(args.symbol)
        return

    start_dt = datetime.strptime(args.start, "%Y-%m-%d %H:%M:%S")
    end_dt = datetime.strptime(args.end, "%Y-%m-%d %H:%M:%S")
    if end_dt <= start_dt:
        raise SystemExit("--end 必须晚于 --start")

    output_dir = _output_dir(args.symbol)
    _acquire_lock(output_dir, args.symbol)
    try:
        result = download_ticks_streaming(
            args.symbol,
            start_dt,
            end_dt,
            resume=args.resume,
            flush_every=args.flush_every,
            tick_window=args.tick_window,
            keep_parts=args.keep_parts,
        )
    finally:
        _release_lock(output_dir)

    logger.info(f"结果: {result}")
    if result.get("status") == "ok":
        print(
            f"\n下载完成: {result['file']} | {result.get('rows', 0):,} tick | "
            f"{result.get('start')} ~ {result.get('end')}"
        )


if __name__ == "__main__":
    main()
