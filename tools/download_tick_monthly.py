"""分月合约 tick 批量下载（对齐 rollover_rules + download_rb_monthly 合约规划）。

在 download_tick_streaming 流式落盘之上，按品种串行拉取白名单交割月 tick。

默认 --span-mode rollover：仅下载 rollover_map / dominant_windows 主力链时段，与 CbC 回测一致。
落盘目录：data/tq/{prefix}/tick/（1m 仍在 data/tq/{prefix}/）。
可选 --span-mode active（交割月前 N 天）或 full（与 1m preload 全跨度）。

用法:
    .venv/Scripts/python.exe tools/download_tick_monthly.py -s SHFE.rb -y 2023 2023 --yymm 2301
    .venv/Scripts/python.exe tools/download_tick_monthly.py -s SHFE.rb -y 2021 2026 --span-mode rollover
    .venv/Scripts/python.exe tools/download_tick_monthly.py -s CZCE.MA -y 2023 2026 --yymm 2405
    .venv/Scripts/python.exe tools/download_tick_monthly.py -s SHFE.rb --reconcile-only
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

from tqsdk import TqAuth
import pandas as pd

from tools.download_rb_monthly import (
    ACTIVE_TRADING_DAYS,
    _build_contract_dates,
    _rollover_symbol_key,
    download_lock,
    get_auth,
)
from tools.download_tick_streaming import (
    FLUSH_EVERY_TICKS,
    TICK_WINDOW,
    download_ticks_streaming,
    merge_parts_only,
)
from tools.dominant_windows import load_segments_by_yymm
from tools.rollover_rules import allowed_months_for_symbol
from tools.tq_tick_io import (
    MANIFEST_FILE,
    canonical_tick_name,
    list_part_files,
    monthly_data_dir,
    tick_output_dir_for_prefix,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

TICK_ACTIVE_DAYS = ACTIVE_TRADING_DAYS
MIN_TICK_ROWS = 5000
TICKS_PER_DAY_EST = 500
UPDATE_TAIL_GAP_DAYS = 7


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


def _resolve_span_mode(args: argparse.Namespace) -> str:
    if args.full_span:
        return "full"
    return args.span_mode


def _contract_tick_window(
    meta_info: dict,
    *,
    span_mode: str = "rollover",
    active_days: int = TICK_ACTIVE_DAYS,
    segments_by_yymm: dict[str, dict] | None = None,
) -> tuple[datetime, datetime]:
    end_dt = datetime.strptime(meta_info["end_date"], "%Y-%m-%d") + timedelta(
        hours=23, minutes=59, seconds=59,
    )
    preload_start = datetime.strptime(meta_info["start_date"], "%Y-%m-%d")
    if span_mode == "full":
        return preload_start, end_dt

    if span_mode == "rollover" and segments_by_yymm:
        seg = segments_by_yymm.get(meta_info["yymm"])
        if seg is not None:
            if seg["start"] is None:
                start_dt = preload_start
            else:
                start_ts = pd.Timestamp(seg["start"])
                start_dt = start_ts.to_pydatetime().replace(tzinfo=None)
            if seg["end"] is None:
                end_out = end_dt
            else:
                end_ts = pd.Timestamp(seg["end"])
                end_out = end_ts.to_pydatetime().replace(tzinfo=None)
                if end_out.hour == 0 and end_out.minute == 0:
                    end_out = end_out + timedelta(hours=23, minutes=59, seconds=59)
                else:
                    end_out = end_out - timedelta(seconds=1)
            return start_dt, end_out
        logger.warning(
            f"yymm={meta_info['yymm']} 不在主力链，回退 active_days={active_days}"
        )

    yymm = meta_info["yymm"]
    year = 2000 + int(yymm[:2])
    month = int(yymm[2:])
    contract_month = datetime(year, month, 1)
    active_start = contract_month - timedelta(days=active_days)
    start_dt = max(active_start, preload_start)
    return start_dt, end_dt


def _expected_min_tick_rows(
    meta_info: dict,
    *,
    span_mode: str = "rollover",
    active_days: int = TICK_ACTIVE_DAYS,
    segments_by_yymm: dict[str, dict] | None = None,
) -> int:
    start_dt, end_dt = _contract_tick_window(
        meta_info,
        span_mode=span_mode,
        active_days=active_days,
        segments_by_yymm=segments_by_yymm,
    )
    span_days = max(7, (end_dt - start_dt).days)
    return max(MIN_TICK_ROWS, int(span_days * TICKS_PER_DAY_EST * 0.4))


def _tick_stats(output_dir: Path, symbol: str) -> dict | None:
    output_file = canonical_tick_name(symbol)
    path = output_dir / output_file
    if not path.exists():
        return None
    df = pd.read_parquet(path, columns=["datetime"])
    if len(df) == 0:
        return None
    dt_min = int(df["datetime"].min())
    dt_max = int(df["datetime"].max())
    return {
        "rows": len(df),
        "min_datetime_ns": dt_min,
        "max_datetime_ns": dt_max,
        "date_range": (
            f"{pd.to_datetime(dt_min, unit='ns', utc=True).tz_convert('Asia/Shanghai').date()} ~ "
            f"{pd.to_datetime(dt_max, unit='ns', utc=True).tz_convert('Asia/Shanghai').date()}"
        ),
    }


def _needs_tail_update(stats: dict, planned_end: datetime) -> bool:
    max_dt = pd.to_datetime(stats["max_datetime_ns"], unit="ns", utc=True).tz_convert("Asia/Shanghai")
    planned = pd.Timestamp(planned_end).tz_localize("Asia/Shanghai")
    gap_days = (planned - max_dt).total_seconds() / 86400.0
    return gap_days > UPDATE_TAIL_GAP_DAYS


def _check_tick_quality(
    symbol: str,
    meta_info: dict,
    output_dir: Path,
    *,
    span_mode: str = "rollover",
    active_days: int = TICK_ACTIVE_DAYS,
    segments_by_yymm: dict[str, dict] | None = None,
) -> tuple[bool, str, dict | None]:
    stats = _tick_stats(output_dir, symbol)
    if stats is None:
        parts = list_part_files(output_dir, symbol)
        if parts:
            return False, f"orphan_parts({len(parts)})", None
        return False, "missing", None

    expected = _expected_min_tick_rows(
        meta_info,
        span_mode=span_mode,
        active_days=active_days,
        segments_by_yymm=segments_by_yymm,
    )
    if stats["rows"] < expected:
        return False, f"low_rows({stats['rows']}<{expected})", stats

    _, planned_end = _contract_tick_window(
        meta_info,
        span_mode=span_mode,
        active_days=active_days,
        segments_by_yymm=segments_by_yymm,
    )
    if _needs_tail_update(stats, planned_end):
        return False, "tail_gap", stats

    return True, "ok", stats


def download_single_contract_tick(
    symbol: str,
    meta_info: dict,
    auth: TqAuth,
    output_dir: Path,
    *,
    force: bool = False,
    resume: bool = False,
    update: bool = False,
    flush_every: int = FLUSH_EVERY_TICKS,
    tick_window: int = TICK_WINDOW,
    keep_parts: bool = False,
    span_mode: str = "rollover",
    active_days: int = TICK_ACTIVE_DAYS,
    segments_by_yymm: dict[str, dict] | None = None,
) -> dict:
    start_dt, end_dt = _contract_tick_window(
        meta_info,
        span_mode=span_mode,
        active_days=active_days,
        segments_by_yymm=segments_by_yymm,
    )
    output_file = canonical_tick_name(symbol)
    output_path = output_dir / output_file

    if not force:
        parts = list_part_files(output_dir, symbol)
        if not output_path.exists() and parts:
            merge_parts_only(symbol)
        is_good, reason, stats = _check_tick_quality(
            symbol,
            meta_info,
            output_dir,
            span_mode=span_mode,
            active_days=active_days,
            segments_by_yymm=segments_by_yymm,
        )
        if is_good and not update:
            return {
                "symbol": symbol,
                "file": output_file,
                "rows": stats["rows"] if stats else 0,
                "status": "skipped",
                "date_range": stats["date_range"] if stats else "",
            }
        if is_good and update and stats and not _needs_tail_update(stats, end_dt):
            return {
                "symbol": symbol,
                "file": output_file,
                "rows": stats["rows"],
                "status": "skipped",
                "date_range": stats["date_range"],
            }
        if reason.startswith("orphan_parts"):
            resume = True
        elif stats and reason == "tail_gap":
            resume = True
            logger.info(f"[{symbol}] 尾部缺口，续传补尾")

    do_resume = resume or (output_path.exists() and not force)
    if force and output_path.exists():
        output_path.unlink(missing_ok=True)
        for pf in list_part_files(output_dir, symbol):
            (output_dir / pf).unlink(missing_ok=True)

    result = download_ticks_streaming(
        symbol,
        start_dt,
        end_dt,
        resume=do_resume,
        flush_every=flush_every,
        tick_window=tick_window,
        keep_parts=keep_parts,
        auth=auth,
        skip_lock=True,
    )
    result["symbol"] = symbol
    result["date_range"] = f"{start_dt.date()} ~ {end_dt.date()}"
    return result


def reconcile_tick_manifest(output_dir: Path, contract_dates: dict) -> dict:
    manifest = _load_manifest(output_dir)
    manifest.setdefault("_meta", {})["datetime_unit"] = "ns_utc"
    updated = 0
    for sym, meta in contract_dates.items():
        output_file = canonical_tick_name(sym)
        path = output_dir / output_file
        if not path.exists():
            continue
        stats = _tick_stats(output_dir, sym)
        if not stats:
            continue
        manifest[output_file] = {
            "symbol": sym,
            "yymm": meta["yymm"],
            "rows": stats["rows"],
            "start_date": pd.to_datetime(stats["min_datetime_ns"], unit="ns", utc=True)
            .tz_convert("Asia/Shanghai")
            .isoformat(),
            "end_date": pd.to_datetime(stats["max_datetime_ns"], unit="ns", utc=True)
            .tz_convert("Asia/Shanghai")
            .isoformat(),
            "reconciled_at": datetime.now().isoformat(),
            "size_mb": round(path.stat().st_size / (1024 * 1024), 3),
        }
        updated += 1
    manifest["_meta"]["reconciled_at"] = datetime.now().isoformat()
    _save_manifest(output_dir, manifest)
    return {"updated": updated}


def _filter_contracts(contract_dates: dict, yymm: str | None) -> dict:
    if not yymm:
        return contract_dates
    target = yymm.strip()
    if not target.isdigit() or len(target) not in (3, 4):
        raise ValueError(f"无效 --yymm: {yymm}")
    out = {k: v for k, v in contract_dates.items() if v["yymm"] == target}
    if not out:
        raise SystemExit(f"未找到 yymm={target} 对应合约（规划内共 {len(contract_dates)} 个）")
    return out


def _run_pipeline(args: argparse.Namespace) -> None:
    symbol = args.symbol
    if symbol.startswith("CZCE."):
        prefix = symbol.split(".")[-1]
    else:
        prefix = symbol.split(".")[-1].lower()
    start_year, end_year = args.years[0], args.years[1]
    output_dir = tick_output_dir_for_prefix(prefix)
    monthly_dir = monthly_data_dir(prefix)

    auth = get_auth()
    contract_dates = _build_contract_dates(
        symbol, start_year, end_year, auth, args.real_expire, all_months=args.all_months,
    )
    contract_dates = _filter_contracts(contract_dates, args.yymm)

    span_mode = _resolve_span_mode(args)
    segments_by_yymm = load_segments_by_yymm(str(monthly_dir)) if span_mode == "rollover" else {}
    if span_mode == "rollover" and not segments_by_yymm:
        logger.warning(
            f"未找到 {monthly_dir / 'rollover_map.parquet'} 或 dominant_windows.json，"
            f"回退 span_mode=active"
        )
        span_mode = "active"

    allowed = allowed_months_for_symbol(_rollover_symbol_key(prefix))
    logger.info("=" * 60)
    logger.info("分月 tick 批量下载")
    logger.info(f"品种       : {symbol}")
    logger.info(f"年份       : {start_year} ~ {end_year}")
    logger.info(f"合约数     : {len(contract_dates)}")
    logger.info(f"tick 目录  : {output_dir}")
    logger.info(f"1m 目录    : {monthly_dir}")
    if args.all_months:
        logger.info("交割月     : 全月份 (--all-months)")
    elif allowed:
        logger.info(f"交割月     : 白名单 {sorted(allowed)} (rollover_rules)")
    if span_mode == "rollover":
        logger.info(f"时间跨度   : 主力链（{len(segments_by_yymm)} 段）")
        for sym, meta in contract_dates.items():
            s, e = _contract_tick_window(
                meta, span_mode=span_mode, segments_by_yymm=segments_by_yymm,
            )
            logger.info(f"  {sym.split('.')[-1]}: {s} ~ {e}")
    elif span_mode == "full":
        logger.info("时间跨度   : 全跨度(含 preload)")
    else:
        logger.info(f"时间跨度   : 活跃期 {args.active_days} 天")
    logger.info("=" * 60)

    if args.reconcile_only:
        stats = reconcile_tick_manifest(output_dir, contract_dates)
        logger.info(f"reconcile 完成: 刷新 {stats['updated']} 个条目")
        return

    symbols_to_download = list(contract_dates.keys())
    if args.repair:
        good, bad = [], []
        for sym, meta in contract_dates.items():
            ok, reason, _ = _check_tick_quality(
                sym,
                meta,
                output_dir,
                span_mode=span_mode,
                active_days=args.active_days,
                segments_by_yymm=segments_by_yymm,
            )
            (good if ok else bad).append((sym, reason))
        logger.info(f"质检: 达标 {len(good)} | 待修 {len(bad)}")
        for sym, reason in bad[:10]:
            logger.info(f"  -> {sym.split('.')[-1]}: {reason}")
        symbols_to_download = [sym for sym, _ in bad]

    t0 = time.time()
    ok = skip = empty = err = 0
    for idx, sym in enumerate(symbols_to_download):
        meta = contract_dates[sym]
        tag = sym.split(".")[-1]
        t1 = time.time()
        try:
            result = download_single_contract_tick(
                sym,
                meta,
                auth,
                output_dir,
                force=args.force,
                resume=args.resume,
                update=args.update,
                flush_every=args.flush_every,
                tick_window=args.tick_window,
                keep_parts=args.keep_parts,
                span_mode=span_mode,
                active_days=args.active_days,
                segments_by_yymm=segments_by_yymm,
            )
        except Exception as exc:
            err += 1
            logger.error(f"[{idx+1}/{len(symbols_to_download)}] {tag} 失败: {exc}")
            continue

        status = result.get("status", "error")
        if status == "ok":
            ok += 1
            logger.info(
                f"[{idx+1}/{len(symbols_to_download)}] {tag}: {result.get('rows', 0):,} tick "
                f"({time.time() - t1:.1f}s) {result.get('date_range', '')}"
            )
        elif status == "skipped":
            skip += 1
            logger.info(
                f"[{idx+1}/{len(symbols_to_download)}] {tag}: 跳过 ({result.get('date_range', '')})"
            )
        elif status == "empty":
            empty += 1
            logger.warning(f"[{idx+1}/{len(symbols_to_download)}] {tag}: 无数据")
        else:
            err += 1
            logger.error(f"[{idx+1}/{len(symbols_to_download)}] {tag}: {result}")

    reconcile_tick_manifest(output_dir, contract_dates)
    elapsed = time.time() - t0
    logger.info(
        f"批量完成: ok={ok} skip={skip} empty={empty} err={err} | 耗时 {elapsed/60:.1f} min"
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="分月 tick 批量下载（rollover_rules 白名单）")
    p.add_argument("-s", "--symbol", default="SHFE.rb", help="品种，如 SHFE.rb / DCE.m / CZCE.MA")
    p.add_argument("-y", "--years", nargs=2, type=int, default=[2023, 2023], help="起止年份")
    p.add_argument("--yymm", help="仅下载指定交割月，如 2301")
    p.add_argument("-r", "--resume", action="store_true", help="断点续传")
    p.add_argument("-f", "--force", action="store_true", help="强制重下")
    p.add_argument("-u", "--update", action="store_true", help="尾部缺口时续传补尾")
    p.add_argument("--repair", action="store_true", help="仅重下质检不合格合约")
    p.add_argument("--all-months", action="store_true", help="忽略 rollover_rules 白名单")
    p.add_argument(
        "--span-mode",
        choices=("rollover", "active", "full"),
        default="rollover",
        help="rollover=主力链(默认); active=交割月前N天; full=1m preload全跨度",
    )
    p.add_argument("--full-span", action="store_true", help="等同 --span-mode full")
    p.add_argument("--active-days", type=int, default=TICK_ACTIVE_DAYS, help="active 模式天数")
    p.add_argument("--real-expire", action="store_true", help="向 TQ 查询真实到期日")
    p.add_argument("--reconcile-only", action="store_true", help="仅刷新 manifest")
    p.add_argument("--flush-every", type=int, default=FLUSH_EVERY_TICKS)
    p.add_argument("--tick-window", type=int, default=TICK_WINDOW)
    p.add_argument("--keep-parts", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    symbol = args.symbol
    if symbol.startswith("CZCE."):
        prefix = symbol.split(".")[-1]
    else:
        prefix = symbol.split(".")[-1].lower()
    output_dir = tick_output_dir_for_prefix(prefix)

    try:
        with download_lock(str(output_dir), symbol):
            _run_pipeline(args)
    except RuntimeError as exc:
        logger.error(str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()
