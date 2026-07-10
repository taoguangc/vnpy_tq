"""全品种离线分月数据质量审计（v1.0）。

输出:
  1. 每品种: 文件数、总行数、日期范围、平均/最小重叠天数、gap 数、缺失合约
  2. 全品种汇总表
  3. 标记 "完美 / 可用 / 待修 / 严重缺失" 四档
"""
from __future__ import annotations

import os
import sys
import re
import logging
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 项目根目录（tools/ 的上一级）
sys.path.insert(0, ROOT)

import pandas as pd
import pyarrow.parquet as pq

from tools.tq_parquet_io import SESSION_NOTE, is_monthly_contract_file

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(ROOT, "data", "tq")

# 各品种合约月份规则（与 download_rb_monthly.py 一致）
DCE_MONTHS_LIST = [1, 3, 5, 7, 8, 9, 11, 12]
DCE_ODD_MONTHS = [1, 3, 5, 7, 9, 11]  # 玉米/玉米淀粉/鸡蛋/粳米等用奇数月
DCE_ODD_PRODUCTS = {"c", "cs", "jd", "rr"}
DCE_PRODUCTS = {"m", "i", "p", "y", "a", "b", "j", "jm", "l", "v", "pp", "eb", "eg"}
CZCE_MONTHS = {
    "MA": list(range(1, 13)),
    "TA": list(range(1, 13)),
    "SA": list(range(1, 13)),
    "FG": list(range(1, 13)),
    "ZC": list(range(1, 13)),
    "SR": [1, 3, 5, 7, 9, 11],
    "CF": [1, 3, 5, 7, 9, 11],
    "CJ": [1, 3, 5, 7, 9, 11],
    "CY": [1, 3, 5, 7, 9, 11],
    "UR": [1, 3, 5, 7, 9, 11],
    "OI": [1, 3, 5, 7, 9, 11],
    "RM": [1, 3, 5, 7, 8, 9, 11],
    "AP": [1, 3, 5, 7, 8, 9, 10, 11],
}
SHFE_MONTHS = list(range(1, 13))

GAP_THRESHOLD_SECONDS = 900


def get_expected_months(exchange: str, product: str) -> list[int]:
    if exchange == "DCE":
        if product.lower() in DCE_ODD_PRODUCTS:
            return DCE_ODD_MONTHS
        return DCE_MONTHS_LIST if product.lower() in DCE_PRODUCTS else SHFE_MONTHS
    elif exchange == "CZCE":
        return CZCE_MONTHS.get(product.upper(), SHFE_MONTHS)
    return SHFE_MONTHS


def detect_exchange_and_prefix(symbol_dir: str) -> tuple[str, str]:
    """根据目录名推断交易所和品种代码。"""
    symbol = symbol_dir
    # 已知的 CZCE 大写品种
    czce_set = {"MA", "TA", "SA", "FG", "ZC", "SR", "CF", "CJ", "CY", "UR", "OI", "RM", "AP", "PF", "SF", "SM"}
    if symbol.upper() in czce_set:
        return "CZCE", symbol.upper()
    # 已知的 SHFE 品种
    shfe_set = {"rb", "hc", "cu", "al", "zn", "pb", "sn", "ni", "ss", "ag", "au", "ru", "nr", "bu", "sp", "fu", "bc", "lu", "ao"}
    if symbol in shfe_set:
        return "SHFE", symbol
    # DCE 品种
    dce_set = {"m", "i", "c", "p", "y", "a", "b", "cs", "jd", "j", "jm", "l", "v", "pp", "eb", "eg", "pg", "rr"}
    if symbol in dce_set:
        return "DCE", symbol
    return "Unknown", symbol


def is_legal_trading_pause(prev_time: pd.Timestamp, curr_time: pd.Timestamp) -> bool:
    p_hm = (prev_time.hour, prev_time.minute)
    c_hm = (curr_time.hour, curr_time.minute)
    if p_hm == (2, 14) and c_hm == (2, 30):
        return True
    if p_hm == (3, 29) and c_hm == (5, 30):
        return True
    if p_hm == (6, 59) and c_hm == (13, 0):
        return True
    if c_hm == (1, 0):
        # 允许日期差 1~15 天（覆盖周末、春节、国庆等长假，春节+周末可达 11-12 天）
        day_diff = (curr_time.date() - prev_time.date()).days
        if 1 <= day_diff <= 15:
            if p_hm in [(6, 59), (14, 59), (16, 59), (18, 29)]:
                return True
    return False


def check_gap_count(df: pd.DataFrame) -> int:
    if len(df) < 2:
        return 0
    dt_series = pd.to_datetime(df["datetime"], unit="ns").sort_values().reset_index(drop=True)
    delta = dt_series.diff().dt.total_seconds()
    gap_mask = delta > GAP_THRESHOLD_SECONDS
    gaps = 0
    for i in gap_mask[gap_mask].index:
        prev_t, curr_t = dt_series.iloc[i - 1], dt_series.iloc[i]
        if not is_legal_trading_pause(prev_t, curr_t):
            gaps += 1
    return gaps


def analyze_symbol(symbol_dir: str) -> dict | None:
    symbol_path = os.path.join(DATA_DIR, symbol_dir)
    if not os.path.isdir(symbol_path):
        return None

    exchange, product = detect_exchange_and_prefix(symbol_dir)
    expected_months = get_expected_months(exchange, product)

    files = sorted([
        f for f in os.listdir(symbol_path)
        if is_monthly_contract_file(f, symbol_dir, 3 if len(symbol_dir) <= 3 and symbol_dir[0].isupper() else 4)
        or (
            f.startswith(f"{symbol_dir}_")
            and f.endswith(".parquet")
            and "_part_" not in f
            and not f.endswith("_continuous.parquet")
            and not f.startswith("rollover_")
            and re.search(r"_(\d{3,4})\.parquet$", f)
        )
    ])
    # 去重（is_monthly 与 fallback 可能重复）
    files = sorted(set(files))

    orphan_part_yymms: list[str] = []
    for f in os.listdir(symbol_path):
        if "_part_" in f and f.endswith(".parquet") and f.startswith(f"{symbol_dir}_"):
            yymm = f.split("_part_")[0].replace(f"{symbol_dir}_", "", 1)
            canonical = f"{symbol_dir}_{yymm}.parquet"
            if not os.path.exists(os.path.join(symbol_path, canonical)):
                if yymm not in orphan_part_yymms:
                    orphan_part_yymms.append(yymm)

    if not files:
        return None

    contracts = []
    total_rows = 0
    total_gaps = 0
    bad_contracts = 0
    min_date = None
    max_date = None
    overlaps = []

    for f in files:
        fp = os.path.join(symbol_path, f)
        try:
            pf = pq.ParquetFile(fp)
            rows = pf.metadata.num_rows
            if rows == 0:
                bad_contracts += 1
                continue
            df = pd.read_parquet(fp, columns=["datetime"])
            df = df[df["datetime"] > 0]
            if len(df) == 0:
                bad_contracts += 1
                continue
            dt = pd.to_datetime(df["datetime"], unit="ns")
            c_min, c_max = dt.min(), dt.max()
            gaps = check_gap_count(df)
            total_rows += rows
            total_gaps += gaps
            if gaps > 10:
                bad_contracts += 1
            if min_date is None or c_min < min_date:
                min_date = c_min
            if max_date is None or c_max > max_date:
                max_date = c_max
            contracts.append({
                "file": f,
                "rows": rows,
                "start": c_min,
                "end": c_max,
                "gaps": gaps,
            })
        except Exception as e:
            bad_contracts += 1
            logger.warning(f"[{symbol_dir}] 读取 {f} 失败: {e}")

    # 计算相邻合约重叠天数（按 yymm 排序）
    contracts.sort(key=lambda x: x["file"])
    for i in range(1, len(contracts)):
        prev_end = contracts[i - 1]["end"]
        curr_start = contracts[i]["start"]
        if curr_start <= prev_end:
            overlap_days = (prev_end - curr_start).days + 1
            overlaps.append(overlap_days)
        else:
            overlaps.append(-((curr_start - prev_end).days))

    # 检查缺失合约（基于实际最早合约 yymm 起算，避免误判数据起点之前的合约）
    yymm_list = []
    for c in contracts:
        m = re.search(r"_(\d{3,4})\.parquet$", c["file"])
        if m:
            yymm_list.append(m.group(1))

    expected_yymm = set()
    if yymm_list:
        # 用文件名中的最早 yymm 作为起点
        sorted_yymm = sorted(yymm_list)
        first_yymm = sorted_yymm[0]
        last_yymm = sorted_yymm[-1]
        # 解析起止年月
        if len(first_yymm) == 3:
            first_year = 2000 + int(first_yymm[0])
            first_month = int(first_yymm[1:3])
            last_year = 2000 + int(last_yymm[0])
            last_month = int(last_yymm[1:3])
        else:
            first_year = 2000 + int(first_yymm[:2])
            first_month = int(first_yymm[2:4])
            last_year = 2000 + int(last_yymm[:2])
            last_month = int(last_yymm[2:4])

        # 从最早合约年月开始，遍历到最新合约年月
        y, mth = first_year, first_month
        while (y < last_year) or (y == last_year and mth <= last_month):
            for em in expected_months:
                yy = str(y)[2:]
                mm = f"{em:02d}"
                # 跳过比 first_yymm 还早的合约
                code = f"{yy[-1]}{mm}" if len(first_yymm) == 3 else f"{yy}{mm}"
                if code >= first_yymm and code <= last_yymm:
                    expected_yymm.add(code)
            mth += 1
            if mth > 12:
                mth = 1
                y += 1

    actual_yymm = set(yymm_list)
    missing = sorted(expected_yymm - actual_yymm)

    avg_overlap = sum(overlaps) / len(overlaps) if overlaps else 0
    min_overlap = min(overlaps) if overlaps else 0

    has_continuous = os.path.exists(os.path.join(symbol_path, f"{symbol_dir}_continuous.parquet"))
    has_rollover = os.path.exists(os.path.join(symbol_path, "rollover_map.parquet"))

    continuous_stale = False
    manifest_path = os.path.join(symbol_path, "manifest.json")
    if has_continuous and os.path.exists(manifest_path):
        try:
            import json
            with open(manifest_path, "r", encoding="utf-8") as mf:
                manifest = json.load(mf)
            derived = manifest.get("derived", {}).get(f"{symbol_dir}_continuous.parquet", {})
            built_at = derived.get("built_at")
            src_dl = derived.get("source_monthly_max_download_time")
            if built_at and src_dl:
                continuous_stale = src_dl > built_at
            elif not derived:
                continuous_stale = True
        except Exception:
            continuous_stale = True

    cst_1500_bars = 0
    if contracts:
        try:
            sample_fp = os.path.join(symbol_path, contracts[0]["file"])
            sample_df = pd.read_parquet(sample_fp, columns=["datetime"])
            dt_bj = pd.to_datetime(sample_df["datetime"], unit="ns", utc=True).dt.tz_convert(
                "Asia/Shanghai"
            )
            cst_1500_bars = int((dt_bj.dt.hour == 15).sum())
        except Exception:
            pass

    return {
        "symbol": symbol_dir,
        "exchange": exchange,
        "contracts": len(contracts),
        "total_rows": total_rows,
        "date_range": f"{min_date.date()} ~ {max_date.date()}" if min_date else "N/A",
        "avg_overlap_days": round(avg_overlap, 1),
        "min_overlap_days": min_overlap,
        "total_gaps": total_gaps,
        "bad_contracts": bad_contracts,
        "missing_contracts": len(missing),
        "missing_list": missing[:10],
        "has_continuous": has_continuous,
        "has_rollover": has_rollover,
        "orphan_part_count": len(orphan_part_yymms),
        "orphan_part_list": orphan_part_yymms[:5],
        "continuous_stale": continuous_stale,
        "cst_1500_bars_sample": cst_1500_bars,
    }


def classify(r: dict) -> str:
    """评级: perfect / good / repair / severe"""
    if r["bad_contracts"] == 0 and r["total_gaps"] == 0 and r["missing_contracts"] == 0:
        if r.get("orphan_part_count", 0) > 0 or r.get("continuous_stale"):
            return "repair"
        return "perfect"
    if r["bad_contracts"] == 0 and r["missing_contracts"] == 0 and r["total_gaps"] < 20:
        return "good"
    if r["missing_contracts"] > 5 or r["bad_contracts"] > 5:
        return "severe"
    return "repair"


def main():
    if not os.path.isdir(DATA_DIR):
        logger.error(f"data 目录不存在: {DATA_DIR}")
        return

    symbols = sorted([
        d for d in os.listdir(DATA_DIR)
        if os.path.isdir(os.path.join(DATA_DIR, d))
    ])

    logger.info(f"发现 {len(symbols)} 个品种目录: {symbols}\n")
    logger.info("=" * 100)

    results = []
    for sym in symbols:
        r = analyze_symbol(sym)
        if r:
            r["grade"] = classify(r)
            results.append(r)

    # 打印汇总表
    logger.info("\n【全品种数据质量汇总】")
    header = f"{'品种':<6} {'交易所':<7} {'文件数':<6} {'总行数':<10} {'日期范围':<26} {'重叠avg/min':<14} {'gap':<5} {'坏合约':<6} {'缺失':<5} {'连续':<5} {'换月表':<6} {'评级':<8}"
    logger.info(header)
    logger.info("-" * 120)
    for r in results:
        line = (
            f"{r['symbol']:<6} "
            f"{r['exchange']:<7} "
            f"{r['contracts']:<6} "
            f"{r['total_rows']:<10} "
            f"{r['date_range']:<26} "
            f"{r['avg_overlap_days']}/{r['min_overlap_days']:<10} "
            f"{r['total_gaps']:<5} "
            f"{r['bad_contracts']:<6} "
            f"{r['missing_contracts']:<5} "
            f"{'Y' if r['has_continuous'] else 'N':<5} "
            f"{'Y' if r['has_rollover'] else 'N':<6} "
            f"{r['grade']:<8}"
        )
        logger.info(line)
        if r["missing_contracts"] > 0:
            logger.info(f"       缺失合约: {r['missing_list']}")
        if r.get("orphan_part_count", 0) > 0:
            logger.info(f"       orphan 分片(无 canonical): {r.get('orphan_part_list')}")
        if r.get("continuous_stale"):
            logger.info("       continuous 过期，需 rebuild")
        if r.get("cst_1500_bars_sample", 0) == 0:
            logger.info(f"       TQ 样本无 CST 15:00 bar（预期，{SESSION_NOTE[:40]}...）")

    # 分级统计
    logger.info("\n【评级分布】")
    for grade in ["perfect", "good", "repair", "severe"]:
        syms = [r["symbol"] for r in results if r["grade"] == grade]
        logger.info(f"  {grade}({len(syms)}): {syms}")

    # 待办建议
    logger.info("\n【下一步建议】")
    severe = [r for r in results if r["grade"] == "severe"]
    repair = [r for r in results if r["grade"] == "repair"]
    no_cont = [r["symbol"] for r in results if not r["has_continuous"]]
    logger.info(f"  严重缺失，需重新下载: {[r['symbol'] for r in severe]}")
    logger.info(f"  需要修复: {[r['symbol'] for r in repair]}")
    logger.info(f"  缺少连续合约/换月表，需运行 build_rollover_map.py: {no_cont}")


if __name__ == "__main__":
    main()
