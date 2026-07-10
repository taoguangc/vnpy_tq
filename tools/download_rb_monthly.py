"""分月合约 1 分钟 K 线串行高速下载器（v2.7）。

  v2.7: 回测落盘改为采集已完成 K 线（窗口内 datetime > last_saved_dt，排除 forming bar），
        修复 volume 恒为 0；质检增加 volume_zero 检测。
  v2.8: 默认仅下载 tools/rollover_rules.py 交割月白名单（如 rb 1/5/10）；
        下载结束后自动 prune 非白名单分月；--all-months 恢复全月份；--prune-only 仅清理磁盘。

核心特性:
  1. 分片落盘：每累积 FLUSH_EVERY_BARS 根 K 线写一个独立分片文件，
     下载期间内存峰值恒定为单分片量级；合并阶段有一次全量 concat
     （K 线级别安全，tick 级别需改流式）。
  2. 原子写入：所有写盘操作先写 .tmp 再 os.replace()，中途崩溃不留损坏文件。
  3. 真正断点续传：TqBacktest 的 start_dt 从 last_dt-1天 开始；未合并分片在崩溃后可恢复。
  4. 动态 KL_WINDOW：CONTRACT_PRELOAD_DAYS（合约起点 365 天）与 KL_BUFFER_DAYS（滑动窗口 45 天）解耦；
     按 NIGHT_MINUTES 估算每日 K 线数，未列出品种按 DEFAULT_NIGHT_MINUTES=120 兜底。
  5. Gap 检测：基于 K 线特征时间点（UTC）判断合法休市时段，
     收盘→开盘的跨天差允许 1~15 天（覆盖周末和法定节假日），
     起点必须是合法收盘时间点，防止真实数据空洞被误豁免。
  6. manifest.json 原子写入，记录每个合约的行数、日期范围、gap 数等元数据。
  7. 串行 for 循环（TQSDK 推荐），同品种进程锁防并发，重试机制带 2 秒冷却。
  8. Parquet 默认 zstd 压缩；主循环用 is_changing 过滤无效 update。
  9. 年份跨度警告：CZCE 品种跨 >9 年时警告合约代码撞键风险。

  v2.9: 两阶段 OI→1m（默认）；--phase full 恢复传统全量 1m。

用法:
    .venv/Scripts/python.exe tools/download_rb_monthly.py --symbol SHFE.rb --years 2023 2026
    .venv/Scripts/python.exe tools/download_rb_monthly.py -s SHFE.rb -y 2023 2026 --phase full
    .venv/Scripts/python.exe tools/download_rb_monthly.py -s SHFE.rb -y 2023 2026 --phase oi
    .venv/Scripts/python.exe tools/download_rb_monthly.py -s SHFE.rb -y 2023 2026 --phase 1m
    .venv/Scripts/python.exe tools/download_rb_monthly.py -s DCE.m -y 2021 2026
    .venv/Scripts/python.exe tools/download_rb_monthly.py -s DCE.m -y 2021 2026 -r
    .venv/Scripts/python.exe tools/download_rb_monthly.py -s DCE.m -y 2021 2026 -u
    .venv/Scripts/python.exe tools/download_rb_monthly.py -s DCE.m -y 2021 2026 -v
    .venv/Scripts/python.exe tools/download_rb_monthly.py -s SHFE.rb --reconcile-only --rebuild-continuous
    .venv/Scripts/python.exe tools/download_rb_monthly.py -s SHFE.rb --prune-only
    .venv/Scripts/python.exe tools/download_rb_monthly.py -s SHFE.rb --all-months
"""

from __future__ import annotations

import os
import sys
import time
import json
import logging
import argparse
import subprocess
import ctypes
from datetime import datetime, timedelta
from contextlib import contextmanager

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 项目根目录（tools/ 的上一级）
sys.path.insert(0, ROOT)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, ".env"))
except ImportError:
    pass

from tqsdk import TqApi, TqBacktest, TqSim, TqAuth
from tqsdk.exceptions import BacktestFinished
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from tools.dominant_windows import (
    apply_windows_to_meta,
    load_dominant_windows,
)
from tools.oi_daily_io import (
    OI_DAILY_COLUMNS,
    normalize_oi_daily,
    oi_daily_dir,
    oi_daily_path,
    PARQUET_WRITE_KWARGS as OI_PARQUET_KWARGS,
)
from tools.rollover_rules import (
    OI_FORWARD_BUFFER_DAYS,
    OI_LOOKBACK_DAYS,
    allowed_months_for_symbol,
    delivery_month_from_yymm,
)
from tools.tq_parquet_io import (
    SESSION_NOTE,
    is_monthly_contract_file,
    normalize_monthly_klines,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# DCE 品种统一使用 1,3,5,7,8,9,11,12 月合约
DCE_MONTHS_LIST = [1, 3, 5, 7, 8, 9, 11, 12]
DCE_PRODUCTS = {"m", "i", "c", "p", "y", "a", "b", "cs", "jd", "j", "jm", "l", "v", "pp", "eb", "eg"}
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

CONTRACT_PRELOAD_DAYS = 365  # 合约 start_date 向前覆盖天数（主力激活期；75 天不够会导致 rb_2410 等缺失）
KL_DURATION_DAILY = 86400  # Phase-1 日 K 线周期（秒）
KL_BUFFER_DAYS = 45  # get_kline_serial 滑动窗口天数（与合约起点解耦，避免 data_length 过大）
KL_DURATION = 60
MIN_ROWS_PER_CONTRACT = 20000
MANIFEST_FILE = "manifest.json"
GAP_THRESHOLD_SECONDS = 900
FLUSH_EVERY_BARS = 5000  # 每累积N根K线就落盘一次，控制内存峰值
SAFETY_MARGIN_DAYS = 30  # KL_WINDOW 的安全裕量天数
UPDATE_TAIL_GAP_DAYS = 7  # --update 模式：尾部距 end_dt 超过此天数则续传补尾
ACTIVE_TRADING_DAYS = 240  # 估算 low_rows 时主力活跃期（约交割月前 8 个月）
LOCK_FILE = ".download.lock"
PARQUET_WRITE_KWARGS = {"index": False, "engine": "pyarrow", "compression": "zstd"}

# 各品种夜盘交易分钟数（白盘固定 225 分钟）
# 23:00 收盘 = 120 分钟夜盘
# 01:00 收盘 = 240 分钟夜盘
# 02:30 收盘 = 330 分钟夜盘
NIGHT_MINUTES = {
    "rb": 120, "hc": 120, "i": 120, "j": 120, "jm": 120,
    "m": 120, "p": 120, "y": 120, "a": 120, "b": 120,
    "MA": 120, "TA": 120, "SA": 120, "FG": 120,
    "ru": 120, "nr": 120, "bu": 120, "sp": 120, "fu": 120,
    "cu": 240, "al": 240, "zn": 240, "pb": 240, "sn": 240, "ni": 240, "ss": 240,
    "ag": 330, "au": 330,
    "pp": 120, "l": 120, "v": 120, "eb": 120, "eg": 120,
    "pg": 120, "rr": 120, "RM": 120, "PF": 120, "SF": 120, "SM": 120,
}
DEFAULT_NIGHT_MINUTES = 120
DAY_SESSION_MINUTES = 225
CZCE_YYMM_LEN3 = {"MA", "TA", "SA", "FG", "SR", "RM", "PF", "SF", "SM", "ZC", "CF", "CJ", "CY", "UR", "OI", "AP"}


def _yymm_len_for_prefix(prefix: str) -> int:
    """分月 parquet 文件名 yymm 位数（TQ 落盘均为 4 位 yyMM）。"""
    return 4


def _get_bars_per_day(symbol: str) -> int:
    """根据品种精确估算每日 1 分钟 K 线数量。"""
    parts = symbol.split(".")
    if len(parts) < 2:
        return DAY_SESSION_MINUTES
    product = parts[-1].rstrip("0123456789")
    night_min = NIGHT_MINUTES.get(product, DEFAULT_NIGHT_MINUTES)
    return DAY_SESSION_MINUTES + night_min


def _estimate_kline_window(bars_per_day: int, buffer_days: int, safety_margin_days: int = 30) -> int:
    """按品种动态估算 get_kline_serial 的 data_length 窗口大小。"""
    total_days = buffer_days + safety_margin_days
    return bars_per_day * total_days


def _part_file_prefix(prefix: str, yymm: str) -> str:
    return f"{prefix}_{yymm}_part_"


def _list_part_files(output_dir: str, prefix: str, yymm: str) -> list[str]:
    part_prefix = _part_file_prefix(prefix, yymm)
    if not os.path.exists(output_dir):
        return []
    return sorted(
        f for f in os.listdir(output_dir)
        if f.startswith(part_prefix) and f.endswith(".parquet")
    )


def _max_datetime_in_parquets(output_dir: str, filenames: list[str]) -> int:
    max_dt = 0
    for fname in filenames:
        try:
            df = pd.read_parquet(os.path.join(output_dir, fname), columns=["datetime"])
            if len(df) > 0:
                max_dt = max(max_dt, int(df["datetime"].max()))
        except Exception:
            continue
    return max_dt


def _remove_files(output_dir: str, filenames: list[str]) -> None:
    for fname in filenames:
        try:
            os.remove(os.path.join(output_dir, fname))
        except Exception:
            pass


def _has_night_session(symbol: str) -> bool:
    """判断品种是否有夜盘。"""
    return _get_bars_per_day(symbol) > DAY_SESSION_MINUTES


def get_auth() -> TqAuth:
    user = os.environ.get("TQ_USER", "")
    pwd = os.environ.get("TQ_PASSWORD", "")
    if user and pwd:
        return TqAuth(user, pwd)
    raise RuntimeError("未在环境或 .env 文件中检测到有效的 TQ_USER / TQ_PASSWORD 配置")


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if sys.platform == "win32":
        handle = ctypes.windll.kernel32.OpenProcess(0x100000, False, pid)
        if handle:
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _read_lock_info(lock_path: str) -> dict | None:
    try:
        with open(lock_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _find_win32_conflicting_downloader(symbol: str, shard: str | None = None) -> int | None:
    """Windows：检测同账号同品种的其他 download_rb_monthly 进程（AGENTS.md 并发约束）。

    shard 模式：仅与同 symbol 的全量下载或同片号 shard 冲突；不同片号可并行。
    """
    if sys.platform != "win32":
        return None
    current_pid = os.getpid()
    base = (
        "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
        f"Where-Object {{ [int]$_.ProcessId -ne {current_pid} -and "
        f"$_.CommandLine -like '*download_rb_monthly.py*' -and "
        f"$_.CommandLine -like '*{symbol}*'"
    )
    if shard:
        n_str, m_str = shard.split("/")
        shard_token = f"{n_str}/{m_str}"
        ps_cmd = (
            base
            + f" -and ($_.CommandLine -notlike '*--shard*' -or "
            f"$_.CommandLine -like '*--shard*{shard_token}*') }} | "
            "Select-Object -First 1 -ExpandProperty ProcessId"
        )
    else:
        ps_cmd = base + " } | Select-Object -First 1 -ExpandProperty ProcessId"
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            timeout=15,
        )
        pid_str = (result.stdout or "").strip()
        if pid_str.isdigit():
            return int(pid_str)
    except Exception as e:
        logger.debug(f"Win32 进程检查跳过: {e}")
    return None


def _lock_path(output_dir: str, shard: str | None) -> str:
    if not shard:
        return os.path.join(output_dir, LOCK_FILE)
    n_str, m_str = shard.split("/")
    return os.path.join(output_dir, f".download.shard{n_str}of{m_str}.lock")


def _acquire_download_lock(output_dir: str, symbol: str, shard: str | None = None) -> None:
    """获取同品种下载锁；已有活跃进程则拒绝启动。shard 模式使用独立锁文件。"""
    # 以 lock 文件为准；Win32 命令行检测在 IDE/包装进程下易误报，仅作 debug 参考
    conflict_pid = _find_win32_conflicting_downloader(symbol, shard)
    current_pid = os.getpid()
    if (
        conflict_pid is not None
        and conflict_pid != current_pid
        and _pid_alive(conflict_pid)
    ):
        logger.debug(
            f"Win32 可见其他 download_rb_monthly 进程 PID={conflict_pid} "
            f"(current={current_pid})，以 lock 文件为准继续"
        )

    lock_path = _lock_path(output_dir, shard)
    os.makedirs(output_dir, exist_ok=True)
    pid = os.getpid()

    if os.path.exists(lock_path):
        info = _read_lock_info(lock_path)
        if info:
            other_pid = int(info.get("pid", 0))
            if other_pid != pid and _pid_alive(other_pid):
                raise RuntimeError(
                    f"锁文件 {lock_path} 被 PID={other_pid} 占用 (symbol={info.get('symbol', '?')})。"
                    f"请勿对同品种并发下载。"
                )
        try:
            os.remove(lock_path)
        except Exception:
            pass

    payload = {
        "pid": pid,
        "symbol": symbol,
        "shard": shard,
        "started": time.time(),
        "started_at": datetime.now().isoformat(),
    }
    fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        os.write(fd, json.dumps(payload, ensure_ascii=False).encode("utf-8"))
    finally:
        os.close(fd)
    logger.debug(f"已获取下载锁: {lock_path} (PID={pid})")


def _release_download_lock(output_dir: str, shard: str | None = None) -> None:
    lock_path = _lock_path(output_dir, shard)
    if not os.path.exists(lock_path):
        return
    info = _read_lock_info(lock_path)
    if info and int(info.get("pid", 0)) == os.getpid():
        try:
            os.remove(lock_path)
            logger.debug(f"已释放下载锁: {lock_path}")
        except Exception:
            pass


@contextmanager
def download_lock(output_dir: str, symbol: str, shard: str | None = None):
    _acquire_download_lock(output_dir, symbol, shard)
    try:
        yield
    finally:
        _release_download_lock(output_dir, shard)


def _rollover_symbol_key(prefix: str) -> str:
    """映射落盘 prefix → rollover_rules 品种键（rb / MA / RM）。"""
    from tools.rollover_rules import SYMBOL_ALLOWED_DELIVERY_MONTHS

    if prefix in SYMBOL_ALLOWED_DELIVERY_MONTHS:
        return prefix
    low = prefix.lower()
    if low in SYMBOL_ALLOWED_DELIVERY_MONTHS:
        return low
    return prefix


def _exchange_month_list(exchange: str, product: str) -> list[int]:
    if exchange == "DCE":
        return DCE_MONTHS_LIST if product.lower() in DCE_PRODUCTS else SHFE_MONTHS
    if exchange == "CZCE":
        return CZCE_MONTHS.get(product.upper(), SHFE_MONTHS)
    return SHFE_MONTHS


def _delivery_months_for_download(
    prefix: str,
    exchange: str,
    product: str,
    *,
    all_months: bool = False,
) -> list[int]:
    """下载目标交割月；默认对齐 rollover_rules 白名单（跟主力）。"""
    base = _exchange_month_list(exchange, product)
    if all_months:
        return base
    allowed = allowed_months_for_symbol(_rollover_symbol_key(prefix))
    if allowed is None:
        return base
    filtered = [m for m in base if m in allowed]
    return filtered


def _parse_monthly_yymm(filename: str, prefix: str, yymm_len: int) -> str | None:
    if is_monthly_contract_file(filename, prefix, yymm_len):
        return filename[len(prefix) + 1 : -8]
    if filename.startswith(f"{prefix}_") and "_part_" in filename and filename.endswith(".parquet"):
        return filename.split("_part_")[0].split(f"{prefix}_", 1)[-1]
    return None


def prune_non_delivery_monthlies(
    output_dir: str,
    prefix: str,
    *,
    dry_run: bool = False,
) -> dict:
    """删除非交割月白名单的分月 parquet 及 orphan 分片。"""
    key = _rollover_symbol_key(prefix)
    allowed = allowed_months_for_symbol(key)
    if allowed is None:
        logger.info(f"[prune] {prefix} 无交割月白名单，跳过")
        return {"removed": [], "skipped": True, "allowed": None}

    yymm_len = _yymm_len_for_prefix(prefix)
    allowed_set = set(allowed)
    removed: list[str] = []

    for f in sorted(os.listdir(output_dir)):
        yymm = _parse_monthly_yymm(f, prefix, yymm_len)
        if not yymm:
            continue
        try:
            delivery_m = delivery_month_from_yymm(yymm, yymm_len)
        except ValueError:
            logger.warning(f"[prune] 无法解析 yymm={yymm!r} from {f}，跳过")
            continue
        if delivery_m in allowed_set:
            continue
        fp = os.path.join(output_dir, f)
        if dry_run:
            logger.info(
                f"[prune dry-run] {f} (交割月 {delivery_m} ∉ {sorted(allowed_set)})"
            )
        else:
            os.remove(fp)
            logger.info(f"[prune] 已删除 {f} (交割月 {delivery_m} ∉ {sorted(allowed_set)})")
        removed.append(f)

    if not dry_run and removed:
        manifest = _load_manifest(output_dir)
        for f in removed:
            if f in manifest:
                del manifest[f]
        _save_manifest(output_dir, manifest)
        reconcile_manifest(output_dir, prefix, None, yymm_len=yymm_len)

    logger.info(
        f"[prune] {prefix} 白名单 {sorted(allowed_set)} | "
        f"{'将删除' if dry_run else '已删除'} {len(removed)} 个文件"
    )
    return {"removed": removed, "skipped": False, "allowed": sorted(allowed_set)}


def _build_contract_dates(
    symbol: str, start_year: int, end_year: int, auth: TqAuth, use_real_expire: bool = False,
    *, all_months: bool = False,
) -> dict:
    parts = symbol.split(".", 1)
    if len(parts) != 2:
        raise ValueError(f"Symbol 格式错误: {symbol}，标准格式形如: EXCHANGE.product")
    exchange, product = parts[0], parts[1]
    prefix = product if exchange == "CZCE" else product.lower()
    months = _delivery_months_for_download(prefix, exchange, product, all_months=all_months)
    contracts = {}
    api = TqApi(auth=auth, web_gui=False) if use_real_expire else None

    try:
        for year in range(start_year, end_year + 1):
            for month in months:
                yy = str(year)[2:]
                mm = f"{month:02d}"
                yymm = f"{yy}{mm}"

                if exchange == "CZCE":
                    contract_code = f"{exchange}.{product.upper()}{yy[-1]}{mm}"
                else:
                    contract_code = f"{exchange}.{product}{yy}{mm}"

                start_dt = datetime(year, month, 1) - timedelta(days=CONTRACT_PRELOAD_DAYS)
                start_date = start_dt.strftime("%Y-%m-%d")
                end_date = None

                if api and use_real_expire:
                    try:
                        quote = api.get_quote(contract_code)
                        api.wait_update(timeout=2)
                        expire_dt = quote.get("expire_datetime", None)
                        if expire_dt:
                            end_date = pd.to_datetime(expire_dt).strftime("%Y-%m-%d")
                    except Exception as e:
                        logger.debug(f"[{contract_code}] 查询到期日失败，回退月底估算: {e}")

                if not end_date:
                    end_year_c = year + 1 if month == 12 else year
                    end_mm = "01" if month == 12 else f"{month + 1:02d}"
                    end_date = f"{end_year_c}-{end_mm}-01"

                contracts[contract_code] = {
                    "start_date": start_date,
                    "end_date": end_date,
                    "yymm": yymm,
                }
    finally:
        if api:
            api.close()

    return contracts


def _build_oi_contract_dates(
    symbol: str, start_year: int, end_year: int, auth: TqAuth, use_real_expire: bool = False,
    *, all_months: bool = False,
) -> dict:
    """Phase-1：缩短日期窗口，仅覆盖 OI 换月检测所需区间。"""
    contracts = _build_contract_dates(
        symbol, start_year, end_year, auth, use_real_expire, all_months=all_months,
    )
    for meta in contracts.values():
        yymm = meta["yymm"]
        year = 2000 + int(yymm[:2])
        month = int(yymm[2:])
        start_dt = datetime(year, month, 1) - timedelta(days=OI_LOOKBACK_DAYS)
        meta["start_date"] = start_dt.strftime("%Y-%m-%d")
        end_dt = datetime.strptime(meta["end_date"], "%Y-%m-%d") + timedelta(days=OI_FORWARD_BUFFER_DAYS)
        meta["end_date"] = end_dt.strftime("%Y-%m-%d")
        meta["phase"] = "oi_daily"
    return contracts


def _contract_month_start(meta_info: dict) -> datetime:
    """从 yymm（如 2410）解析交割月首日。"""
    yymm = meta_info["yymm"]
    year = 2000 + int(yymm[:2])
    month = int(yymm[2:])
    return datetime(year, month, 1)


def _expected_min_rows(symbol: str, meta_info: dict) -> int:
    """估算最小行数；dominant_1m 按窗口天数，否则按主力活跃期。"""
    bars_per_day = _get_bars_per_day(symbol)
    end_dt = datetime.strptime(meta_info["end_date"], "%Y-%m-%d")

    if meta_info.get("download_mode") == "dominant_1m":
        start_dt = datetime.strptime(meta_info["start_date"], "%Y-%m-%d")
        span_days = max(14, (end_dt - start_dt).days)
        return max(3000, int(span_days * bars_per_day * 0.55))

    contract_month = _contract_month_start(meta_info)
    active_start = contract_month - timedelta(days=ACTIVE_TRADING_DAYS)
    span_days = max(30, (end_dt - active_start).days)
    # 0.65 ≈ 交易日占比（含节假日裕量）
    return max(MIN_ROWS_PER_CONTRACT, int(span_days * bars_per_day * 0.65))


def _expected_min_oi_rows(meta_info: dict) -> int:
    start_dt = datetime.strptime(meta_info["start_date"], "%Y-%m-%d")
    end_dt = datetime.strptime(meta_info["end_date"], "%Y-%m-%d")
    span_days = max(30, (end_dt - start_dt).days)
    return max(20, int(span_days * 0.45))


def _get_parquet_metadata(file_path: str) -> dict | None:
    try:
        pf = pq.ParquetFile(file_path)
        return {"num_rows": pf.metadata.num_rows, "created_by": pf.metadata.created_by}
    except Exception:
        return None


def _is_legal_trading_pause(prev_time: pd.Timestamp, curr_time: pd.Timestamp) -> bool:
    """基于中国期货标准 K 线时间戳（UTC），判定是否属于合法的非交易停盘时段。

    注意：TQSDK 的 K 线时间戳是 UTC 时间，北京时间 = UTC + 8 小时

    合法休市时段（UTC 时间的 K 线起始点）：
    - 早盘休息：02:14 -> 02:30 (UTC) = 北京 10:15 收盘，10:30 开盘（K 线 datetime 为该分钟起始，故最后一根 K 线 datetime=10:14）
    - 午休：03:29 -> 05:30 (UTC) = 北京 11:30 收盘，13:30 开盘（适用商品期货；中金所 13:00 开盘，本脚本不涉及）
    - 日盘收盘 -> 夜盘开盘：06:59 -> 13:00 (UTC) = 14:59 -> 21:00 (北京时间)
    - 夜盘收盘 -> 次日开盘：06:59/14:59/16:59/18:29 -> 01:00 (UTC)
    - 周末/节假日：合法收盘点 -> 01:00 (跨天≥2天，起点必须是收盘时间)
    """
    p_hm = (prev_time.hour, prev_time.minute)
    c_hm = (curr_time.hour, curr_time.minute)

    # 早盘休息
    if p_hm == (2, 14) and c_hm == (2, 30):
        return True
    # 午休
    if p_hm == (3, 29) and c_hm == (5, 30):
        return True
    # 日盘收盘 -> 夜盘开盘
    if p_hm == (6, 59) and c_hm == (13, 0):
        return True
    # 夜盘收盘 -> 次日开盘：允许日期差 1~15 天（覆盖周末、春节、国庆等长假，
    # 春节+周末组合可达 11-12 天；起点必须是合法收盘时间点，防止盘中断档被误判为正常）
    if c_hm == (1, 0):
        day_diff = (curr_time.date() - prev_time.date()).days
        if 1 <= day_diff <= 15:
            if p_hm in [(6, 59), (14, 59), (16, 59), (18, 29)]:
                return True

    return False


VOLUME_NONZERO_MIN_RATIO = 0.05  # 1m 期货活跃段至少约 5% bar 应有成交


def _volume_nonzero_ratio(df: pd.DataFrame) -> float:
    if df is None or len(df) == 0 or "volume" not in df.columns:
        return 0.0
    vol = pd.to_numeric(df["volume"], errors="coerce").fillna(0)
    return float((vol > 0).mean())


def _has_valid_volume(df: pd.DataFrame) -> bool:
    """volume 全零或几乎全零视为下载逻辑错误或坏文件。"""
    ratio = _volume_nonzero_ratio(df)
    return ratio >= VOLUME_NONZERO_MIN_RATIO


def _slice_new_completed_bars(
    klines: pd.DataFrame,
    last_saved_dt: int,
    *,
    include_last_bar: bool = False,
) -> tuple[pd.DataFrame, int]:
    """从 kline 窗口取出已完成的 bar（默认排除 iloc[-1] 正在形成的 bar）。

    is_changing(klines.iloc[-1], 'datetime') 时，新 bar 在 -1 且 volume=0；
    应落盘的是 datetime <= 倒数第二根及此前、且 datetime > last_saved_dt 的 bar。
    """
    n = len(klines)
    if n == 0:
        return pd.DataFrame(), last_saved_dt
    end = n if include_last_bar else n - 1
    if end <= 0:
        return pd.DataFrame(), last_saved_dt
    subset = klines.iloc[:end]
    chunk = subset[subset["datetime"] > last_saved_dt]
    if len(chunk) == 0:
        return pd.DataFrame(), last_saved_dt
    return chunk, int(chunk["datetime"].max())


def _check_gap_count(df: pd.DataFrame) -> int:
    if len(df) < 2:
        return 0
    dt_series = pd.to_datetime(df["datetime"], unit="ns").sort_values().reset_index(drop=True)
    delta = dt_series.diff().dt.total_seconds()
    gap_mask = delta > GAP_THRESHOLD_SECONDS
    gaps = 0
    for i in gap_mask[gap_mask].index:
        prev_t, curr_t = dt_series.iloc[i - 1], dt_series.iloc[i]
        if not _is_legal_trading_pause(prev_t, curr_t):
            gaps += 1
    return gaps


def _try_manifest_quality_check(
    manifest_entry: dict,
    expected_min: int,
    start_dt: datetime,
    end_dt: datetime,
    *,
    skip_range_gap: bool = False,
) -> tuple[bool, str, dict | None] | None:
    """基于 manifest 的快速质检；返回 None 表示 manifest 信息不足，需读 parquet。"""
    if manifest_entry.get("skip_reason") == "no_data":
        return False, "no_data", None

    rows = manifest_entry.get("rows")
    if rows is None:
        return None
    if rows == 0:
        return False, "empty", None
    if rows < expected_min:
        return False, f"low_rows({rows}<{expected_min})", None

    gaps = manifest_entry.get("gaps", 0)
    if gaps > 10:
        return False, f"gaps({gaps})", None

    vnr = manifest_entry.get("volume_nonzero_ratio")
    if vnr is not None and vnr < VOLUME_NONZERO_MIN_RATIO:
        return False, "volume_zero", None
    if vnr is None:
        return None

    m_start = manifest_entry.get("start_date")
    m_end = manifest_entry.get("end_date")
    if not m_start or not m_end:
        return None

    dt_min = datetime.strptime(m_start, "%Y-%m-%d")
    dt_max = datetime.strptime(m_end, "%Y-%m-%d")
    gap_start = (dt_min - start_dt).total_seconds() / 86400.0
    dt_max_eod = dt_max + timedelta(hours=23, minutes=59, seconds=59)
    gap_end = (end_dt - dt_max_eod).total_seconds() / 86400.0

    if not skip_range_gap:
        if gap_start > 7:
            return False, f"gap_start({gap_start:.1f}d)", None
        if gap_end > 30:
            return False, f"gap_end({gap_end:.1f}d)", None

    max_datetime_ns = int(pd.Timestamp(dt_max_eod).value)
    stats = {
        "rows": rows,
        "gap_count": gaps,
        "date_range": f"{dt_min.date()} ~ {dt_max.date()}",
        "max_datetime_ns": max_datetime_ns,
    }
    return True, f"ok(manifest,{rows} rows, gaps={gaps})", stats


def _check_contract_quality(
    symbol: str,
    meta_info: dict,
    output_dir: str,
    prefix: str,
    manifest_entry: dict | None = None,
    deep: bool = True,
    repair_mode: bool = False,
) -> tuple[bool, str, dict | None]:
    """检查合约 parquet 质量。通过时第三项 stats 含 rows/gap_count/date_range/max_datetime_ns。

    deep=False 且提供 manifest_entry 时优先 manifest 轻量扫描；信息不足则回退读 parquet。
    """
    start_dt = datetime.strptime(meta_info["start_date"], "%Y-%m-%d")
    end_dt = datetime.strptime(meta_info["end_date"], "%Y-%m-%d") + timedelta(hours=23, minutes=59, seconds=59)

    output_file = f"{prefix}_{meta_info['yymm']}.parquet"
    output_path = os.path.join(output_dir, output_file)
    expected_min = _expected_min_rows(symbol, meta_info)

    if not os.path.exists(output_path):
        return False, "missing", None

    if not deep and manifest_entry is not None:
        fast = _try_manifest_quality_check(
            manifest_entry, expected_min, start_dt, end_dt,
            skip_range_gap=repair_mode,
        )
        if fast is not None:
            return fast

    meta = _get_parquet_metadata(output_path)
    if not meta:
        return False, "corrupt", None
    if meta["num_rows"] == 0:
        return False, "empty", None
    if meta["num_rows"] < expected_min:
        return False, f"low_rows({meta['num_rows']}<{expected_min})", None

    try:
        existing = pd.read_parquet(output_path, columns=["datetime", "volume"])
        if not _has_valid_volume(existing):
            return False, "volume_zero", None

        dt_existing = pd.to_datetime(existing["datetime"], unit="ns")
        dt_min, dt_max = dt_existing.min(), dt_existing.max()
        gap_start = (dt_min - start_dt).total_seconds() / 86400.0
        gap_end = (end_dt - dt_max).total_seconds() / 86400.0

        if not repair_mode:
            if gap_start > 7:
                return False, f"gap_start({gap_start:.1f}d)", None
            if gap_end > 30:
                return False, f"gap_end({gap_end:.1f}d)", None

        gap_count = _check_gap_count(existing)
        if gap_count > 10:
            return False, f"gaps({gap_count})", None

        stats = {
            "rows": meta["num_rows"],
            "gap_count": gap_count,
            "date_range": f"{dt_min.date()} ~ {dt_max.date()}",
            "max_datetime_ns": int(existing["datetime"].max()),
        }
        return True, f"ok({meta['num_rows']} rows, gaps={gap_count})", stats
    except Exception as e:
        return False, f"corrupt({str(e)[:30]})", None


def _tail_gap_days(stats: dict, end_dt: datetime) -> float:
    """已有数据末 bar 与计划 end_dt 之间的日历天数差。"""
    dt_max = pd.to_datetime(stats["max_datetime_ns"], unit="ns").to_pydatetime()
    return (end_dt - dt_max).total_seconds() / 86400.0


def _needs_tail_update(stats: dict, end_dt: datetime, update_mode: bool) -> bool:
    if not update_mode:
        return False
    return _tail_gap_days(stats, end_dt) > UPDATE_TAIL_GAP_DAYS


def _record_no_data_contract(output_dir: str, prefix: str, meta_info: dict, symbol: str) -> None:
    """将确认无数据的合约记入 manifest，避免反复 force 重试。"""
    output_file = f"{prefix}_{meta_info['yymm']}.parquet"
    manifest = _load_manifest(output_dir)
    manifest[output_file] = {
        "rows": 0,
        "skip_reason": "no_data",
        "contract": symbol,
        "download_time": datetime.now().isoformat(),
    }
    _save_manifest(output_dir, manifest)


def _load_manifest(output_dir: str) -> dict:
    manifest_path = os.path.join(output_dir, MANIFEST_FILE)
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_manifest(output_dir: str, manifest: dict):
    manifest_path = os.path.join(output_dir, MANIFEST_FILE)
    tmp_path = manifest_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, manifest_path)


def _merge_orphan_parts_only(
    output_dir: str,
    prefix: str,
    yymm: str,
    meta_info: dict,
) -> dict | None:
    """仅合并 orphan 分片为 canonical 文件，不连接 TQSDK。"""
    output_file = f"{prefix}_{yymm}.parquet"
    output_path = os.path.join(output_dir, output_file)
    if os.path.exists(output_path):
        return None
    part_files = _list_part_files(output_dir, prefix, yymm)
    if not part_files:
        return None

    dfs = [pd.read_parquet(os.path.join(output_dir, pf)) for pf in part_files]
    full_df = normalize_monthly_klines(pd.concat(dfs, ignore_index=True))
    if len(full_df) == 0:
        return {"status": "empty", "file": output_file}

    tmp_path = output_path + ".tmp"
    full_df.to_parquet(tmp_path, **PARQUET_WRITE_KWARGS)
    os.replace(tmp_path, output_path)

    for pf in part_files:
        try:
            os.remove(os.path.join(output_dir, pf))
        except Exception:
            pass

    dt_min = pd.to_datetime(full_df["datetime"].iloc[0], unit="ns")
    dt_max = pd.to_datetime(full_df["datetime"].iloc[-1], unit="ns")
    gap_count = _check_gap_count(full_df)

    manifest = _load_manifest(output_dir)
    manifest.setdefault("_meta", {})["session_note"] = SESSION_NOTE
    manifest[output_file] = {
        "rows": len(full_df),
        "start_date": dt_min.date().isoformat(),
        "end_date": dt_max.date().isoformat(),
        "download_time": datetime.now().isoformat(),
        "gaps": gap_count,
        "size_mb": round(os.path.getsize(output_path) / (1024 * 1024), 2),
        "merged_from_parts": len(part_files),
        "schema_version": 1,
    }
    _save_manifest(output_dir, manifest)
    logger.info(f"[仅合并分片] {output_file}: {len(full_df)} 行 (来自 {len(part_files)} 个 part)")
    return {
        "status": "ok",
        "file": output_file,
        "rows": len(full_df),
        "date_range": f"{dt_min.date()} ~ {dt_max.date()}",
    }


def reconcile_manifest(
    output_dir: str,
    prefix: str,
    contract_dates: dict | None = None,
    yymm_len: int = 4,
) -> dict:
    """扫描磁盘分月 parquet，刷新 manifest；移除 stale 条目；报告 orphan part。"""
    manifest = _load_manifest(output_dir)
    manifest.setdefault("_meta", {})["session_note"] = SESSION_NOTE
    manifest.setdefault("_meta", {})["datetime_unit"] = "ns_utc"

    on_disk: set[str] = set()
    orphan_only: list[str] = []

    if not os.path.isdir(output_dir):
        return {"updated": 0, "removed": 0, "orphan_only": []}

    for f in os.listdir(output_dir):
        if not is_monthly_contract_file(f, prefix, yymm_len):
            if f"{prefix}_" in f and "_part_" in f and f.endswith(".parquet"):
                yymm = f.split("_part_")[0].split(f"{prefix}_", 1)[-1]
                canonical = f"{prefix}_{yymm}.parquet"
                if not os.path.exists(os.path.join(output_dir, canonical)):
                    if yymm not in orphan_only:
                        orphan_only.append(yymm)
            continue

        fp = os.path.join(output_dir, f)
        on_disk.add(f)
        try:
            df = pd.read_parquet(fp, columns=["datetime", "volume"])
            if len(df) == 0:
                continue
            dt_min = pd.to_datetime(df["datetime"].iloc[0], unit="ns")
            dt_max = pd.to_datetime(df["datetime"].iloc[-1], unit="ns")
            gap_count = _check_gap_count(df)
            vol_ratio = _volume_nonzero_ratio(df)
            entry = manifest.get(f, {})
            if not isinstance(entry, dict):
                entry = {}
            entry.update({
                "rows": len(df),
                "start_date": dt_min.date().isoformat(),
                "end_date": dt_max.date().isoformat(),
                "gaps": gap_count,
                "volume_nonzero_ratio": round(vol_ratio, 4),
                "size_mb": round(os.path.getsize(fp) / (1024 * 1024), 2),
                "schema_version": 1,
            })
            if "download_time" not in entry:
                entry["download_time"] = datetime.fromtimestamp(
                    os.path.getmtime(fp)
                ).isoformat()
            manifest[f] = entry
        except Exception as e:
            logger.warning(f"[reconcile] 无法读取 {f}: {e}")

    removed = 0
    for key in list(manifest.keys()):
        if key.startswith("_") or key == "derived":
            continue
        if key.startswith(f"{prefix}_") and key.endswith(".parquet") and key not in on_disk:
            del manifest[key]
            removed += 1

    if contract_dates:
        for _sym, meta in contract_dates.items():
            yymm = meta["yymm"]
            merge_result = _merge_orphan_parts_only(output_dir, prefix, yymm, meta)
            if merge_result and merge_result.get("status") == "ok":
                on_disk.add(f"{prefix}_{yymm}.parquet")
                if yymm in orphan_only:
                    orphan_only.remove(yymm)

    for yymm in list(orphan_only):
        merge_result = _merge_orphan_parts_only(
            output_dir, prefix, yymm, {"yymm": yymm},
        )
        if merge_result and merge_result.get("status") == "ok":
            on_disk.add(f"{prefix}_{yymm}.parquet")
            orphan_only.remove(yymm)

    manifest["_meta"]["reconciled_at"] = datetime.now().isoformat()
    _save_manifest(output_dir, manifest)
    return {
        "updated": len(on_disk),
        "removed": removed,
        "orphan_only": orphan_only,
    }


def download_oi_daily_contract(
    symbol: str,
    meta_info: dict,
    auth: TqAuth,
    output_dir: str,
    prefix: str,
    force: bool,
) -> dict:
    """Phase-1：下载单合约日 K（close + close_oi）至 oi_daily/。"""
    start_dt = datetime.strptime(meta_info["start_date"], "%Y-%m-%d")
    end_dt = datetime.strptime(meta_info["end_date"], "%Y-%m-%d") + timedelta(hours=23, minutes=59, seconds=59)
    yymm = meta_info["yymm"]
    os.makedirs(oi_daily_dir(output_dir), exist_ok=True)
    output_path = oi_daily_path(output_dir, prefix, yymm)
    output_file = os.path.basename(output_path)
    min_rows = _expected_min_oi_rows(meta_info)

    if not force and os.path.exists(output_path):
        try:
            existing = pd.read_parquet(output_path)
            if len(existing) >= min_rows:
                dt = pd.to_datetime(existing["datetime"], unit="ns")
                return {
                    "symbol": symbol,
                    "file": output_file,
                    "rows": len(existing),
                    "status": "skipped",
                    "date_range": f"{dt.min().date()} ~ {dt.max().date()}",
                }
        except Exception:
            pass

    kl_window = OI_LOOKBACK_DAYS + OI_FORWARD_BUFFER_DAYS + SAFETY_MARGIN_DAYS + 30
    t0 = time.time()
    accumulated: list[pd.DataFrame] = []
    last_dt = 0
    api = None
    klines = None

    try:
        api = TqApi(
            TqSim(init_balance=100_000),
            backtest=TqBacktest(start_dt=start_dt, end_dt=end_dt),
            auth=auth,
            web_gui=False,
        )
        klines = api.get_kline_serial(symbol, KL_DURATION_DAILY, data_length=kl_window)

        while True:
            api.wait_update()
            if len(klines) == 0 or not api.is_changing(klines.iloc[-1], "datetime"):
                continue
            chunk, last_dt = _slice_new_completed_bars(klines, last_dt)
            if len(chunk) == 0:
                continue
            accumulated.append(chunk)
    except BacktestFinished:
        if klines is not None and len(klines) > 0:
            chunk, last_dt = _slice_new_completed_bars(klines, last_dt, include_last_bar=True)
            if len(chunk) > 0:
                accumulated.append(chunk)
    except Exception as e:
        elapsed = time.time() - t0
        return {
            "symbol": symbol,
            "file": output_file,
            "rows": 0,
            "status": "error",
            "error": str(e),
            "elapsed": elapsed,
        }
    finally:
        if api is not None:
            api.close()

    if not accumulated:
        elapsed = time.time() - t0
        return {
            "symbol": symbol,
            "file": output_file,
            "rows": 0,
            "status": "empty",
            "elapsed": elapsed,
        }

    try:
        df = normalize_oi_daily(pd.concat(accumulated, ignore_index=True))
        if len(df) < min_rows // 2:
            return {
                "symbol": symbol,
                "file": output_file,
                "rows": len(df),
                "status": "empty",
                "elapsed": time.time() - t0,
            }
        tmp_path = output_path + ".tmp"
        df.to_parquet(tmp_path, **OI_PARQUET_KWARGS)
        os.replace(tmp_path, output_path)
        dt = pd.to_datetime(df["datetime"], unit="ns")
        elapsed = time.time() - t0
        return {
            "symbol": symbol,
            "file": output_file,
            "rows": len(df),
            "status": "ok",
            "elapsed": elapsed,
            "date_range": f"{dt.min().date()} ~ {dt.max().date()}",
        }
    except Exception as e:
        return {
            "symbol": symbol,
            "file": output_file,
            "rows": 0,
            "status": "error",
            "error": str(e),
            "elapsed": time.time() - t0,
        }


def download_single_contract(
    symbol: str,
    meta_info: dict,
    auth: TqAuth,
    output_dir: str,
    prefix: str,
    force: bool,
    update: bool = False,
) -> dict:
    start_dt = datetime.strptime(meta_info["start_date"], "%Y-%m-%d")
    end_dt = datetime.strptime(meta_info["end_date"], "%Y-%m-%d") + timedelta(hours=23, minutes=59, seconds=59)

    output_file = f"{prefix}_{meta_info['yymm']}.parquet"
    output_path = os.path.join(output_dir, output_file)

    if not force and not os.path.exists(output_path):
        merged = _merge_orphan_parts_only(output_dir, prefix, meta_info["yymm"], meta_info)
        if merged and merged.get("status") == "ok":
            return {
                "symbol": symbol,
                "file": output_file,
                "rows": merged["rows"],
                "status": "ok",
                "elapsed": 0,
                "date_range": merged.get("date_range", ""),
            }

    if not force:
        manifest_entry = _load_manifest(output_dir).get(output_file)
        if manifest_entry and manifest_entry.get("skip_reason") == "no_data":
            return {
                "symbol": symbol,
                "file": output_file,
                "rows": 0,
                "status": "skipped",
                "skip_reason": "no_data",
            }

    yymm = meta_info["yymm"]
    orphan_parts = _list_part_files(output_dir, prefix, yymm)

    quality_result: tuple[bool, str, dict | None] | None = None
    if not force and os.path.exists(output_path):
        quality_result = _check_contract_quality(symbol, meta_info, output_dir, prefix)
        is_good, _reason, stats = quality_result
        if is_good and stats:
            parts_max_dt = _max_datetime_in_parquets(output_dir, orphan_parts) if orphan_parts else 0
            has_newer_parts = bool(orphan_parts) and parts_max_dt > stats["max_datetime_ns"]
            needs_tail = _needs_tail_update(stats, end_dt, update)
            if not has_newer_parts and not needs_tail:
                return {
                    "symbol": symbol,
                    "file": output_file,
                    "rows": stats["rows"],
                    "status": "skipped",
                    "date_range": stats["date_range"],
                    "gaps": stats["gap_count"],
                }
            if has_newer_parts:
                logger.info(
                    f"[{symbol}] 检测到 {len(orphan_parts)} 个未合并分片"
                    f"（分片最新 {pd.to_datetime(parts_max_dt, unit='ns').date()} > "
                    f"已有 {pd.to_datetime(stats['max_datetime_ns'], unit='ns').date()}），继续合并"
                )
            elif needs_tail:
                gap_d = _tail_gap_days(stats, end_dt)
                logger.info(
                    f"[{symbol}] --update: 尾部距计划终点还有 {gap_d:.1f} 天"
                    f"（>{UPDATE_TAIL_GAP_DAYS} 天），续传补尾"
                )

    # 动态计算 KL_WINDOW
    bars_per_day = _get_bars_per_day(symbol)
    has_night = bars_per_day > DAY_SESSION_MINUTES
    kl_window = _estimate_kline_window(bars_per_day, KL_BUFFER_DAYS, SAFETY_MARGIN_DAYS)
    logger.debug(f"[{symbol}] 动态KL窗口: {kl_window} (bars/day={bars_per_day}, 有夜盘={has_night})")

    t0 = time.time()
    accumulated = []
    accumulated_rows = 0
    last_dt = 0
    api = None
    part_count = 0
    elapsed = 0.0
    part_files = []
    resume_source = None  # 断点续传时的旧文件路径，独立于 part_files

    # 清理残留的 .tmp（分片 .parquet 在下面按场景保留或删除）
    if os.path.exists(output_dir):
        tmp_prefix = f"{prefix}_{yymm}"
        for f in os.listdir(output_dir):
            if f.endswith(".tmp") and f.startswith(tmp_prefix):
                try:
                    os.remove(os.path.join(output_dir, f))
                except Exception:
                    pass

    def _apply_resume_from_dt(max_dt: int) -> None:
        nonlocal last_dt, backtest_start
        if max_dt <= 0:
            return
        last_dt = max_dt
        last_dt_ts = pd.to_datetime(last_dt, unit="ns")
        backtest_start = last_dt_ts.to_pydatetime() - timedelta(days=1)
        if backtest_start < start_dt:
            backtest_start = start_dt

    # 断点续传 / 分片恢复：仅对质量合格的文件追加尾部；未合并分片优先保留
    backtest_start = start_dt
    if force:
        _remove_files(output_dir, orphan_parts)
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except Exception:
                pass
    elif os.path.exists(output_path):
        if quality_result is not None:
            is_good, reason, stats = quality_result
        else:
            is_good, reason, stats = _check_contract_quality(symbol, meta_info, output_dir, prefix)
        if is_good and stats:
            resume_source = output_file
            _apply_resume_from_dt(stats["max_datetime_ns"])
            if orphan_parts:
                parts_max_dt = _max_datetime_in_parquets(output_dir, orphan_parts)
                if parts_max_dt > last_dt:
                    part_files = orphan_parts
                    part_count = max(
                        int(f.rsplit("_part_", 1)[1].replace(".parquet", "")) for f in orphan_parts
                    )
                    _apply_resume_from_dt(parts_max_dt)
                    logger.info(
                        f"[{symbol}] 合并未落盘分片 {len(orphan_parts)} 个, "
                        f"续传起点 {pd.to_datetime(last_dt, unit='ns').date()}"
                    )
                else:
                    _remove_files(output_dir, orphan_parts)
            else:
                logger.debug(
                    f"[{symbol}] 断点续传: 已有 {stats['rows']} 行, "
                    f"从 {backtest_start.date()} 开始回测(原 {start_dt.date()})"
                )
        elif not is_good:
            logger.info(f"[{symbol}] 旧文件质量不合格({reason})，删除后完整重下")
            try:
                os.remove(output_path)
            except Exception:
                pass
            if orphan_parts:
                part_files = orphan_parts
                part_count = max(
                    int(f.rsplit("_part_", 1)[1].replace(".parquet", "")) for f in orphan_parts
                )
                parts_max_dt = _max_datetime_in_parquets(output_dir, orphan_parts)
                _apply_resume_from_dt(parts_max_dt)
                logger.info(
                    f"[{symbol}] 从 {len(orphan_parts)} 个未合并分片恢复, "
                    f"last_dt={pd.to_datetime(last_dt, unit='ns').date() if last_dt else 'N/A'}"
                )
    elif orphan_parts:
        part_files = orphan_parts
        part_count = max(
            int(f.rsplit("_part_", 1)[1].replace(".parquet", "")) for f in orphan_parts
        )
        parts_max_dt = _max_datetime_in_parquets(output_dir, orphan_parts)
        _apply_resume_from_dt(parts_max_dt)
        logger.info(
            f"[{symbol}] 从 {len(orphan_parts)} 个未合并分片恢复, "
            f"last_dt={pd.to_datetime(last_dt, unit='ns').date() if last_dt else 'N/A'}"
        )

    # 记录断点续传前是否已有分片，用于后续判断是否产生了新数据
    initial_part_count = len(part_files)

    def _flush_accumulated_atomic():
        """将 accumulated 中的数据原子写入分片文件并清空，内存峰值恒定。"""
        nonlocal accumulated, accumulated_rows, part_count, part_files
        if not accumulated:
            return
        part_count += 1
        df = normalize_monthly_klines(pd.concat(accumulated, ignore_index=True))

        part_file = f"{prefix}_{meta_info['yymm']}_part_{part_count:03d}.parquet"
        part_path = os.path.join(output_dir, part_file)
        tmp_path = part_path + ".tmp"

        df.to_parquet(tmp_path, **PARQUET_WRITE_KWARGS)
        os.replace(tmp_path, part_path)
        part_files.append(part_file)

        accumulated = []
        accumulated_rows = 0
        logger.debug(f"[{symbol}] 分片{part_count}: {len(df)} rows -> {part_file}")

    def _merge_parts():
        """合并 resume_source（旧文件）和所有新分片为最终输出，原子替换。"""
        nonlocal part_files, output_path, resume_source
        if not part_files and not resume_source:
            return None

        tmp_path = output_path + ".tmp"
        dfs = []
        # 先读旧文件（断点续传时）
        if resume_source and os.path.exists(os.path.join(output_dir, resume_source)):
            dfs.append(pd.read_parquet(os.path.join(output_dir, resume_source)))
        # 再读所有新分片
        for pf in part_files:
            dfs.append(pd.read_parquet(os.path.join(output_dir, pf)))

        full_df = normalize_monthly_klines(pd.concat(dfs, ignore_index=True))

        full_df.to_parquet(tmp_path, **PARQUET_WRITE_KWARGS)
        os.replace(tmp_path, output_path)

        # 清理临时分片文件（resume_source 是最终文件名，不删）
        for pf in part_files:
            try:
                os.remove(os.path.join(output_dir, pf))
            except Exception:
                pass
        part_files = []
        resume_source = None
        return full_df

    try:
        api = TqApi(
            TqSim(init_balance=100_000),
            backtest=TqBacktest(start_dt=backtest_start, end_dt=end_dt),
            auth=auth,
            web_gui=False,
        )
        klines = api.get_kline_serial(symbol, KL_DURATION, data_length=kl_window)

        try:
            while True:
                api.wait_update()
                if len(klines) == 0 or not api.is_changing(klines.iloc[-1], "datetime"):
                    continue
                chunk, last_dt = _slice_new_completed_bars(klines, last_dt)
                if len(chunk) == 0:
                    continue
                accumulated.append(chunk)
                accumulated_rows += len(chunk)

                if accumulated_rows >= FLUSH_EVERY_BARS:
                    _flush_accumulated_atomic()
                    logger.debug(
                        f"[{symbol}] 已写入分片{part_count}, 累计{accumulated_rows}根, "
                        f"last_saved={pd.to_datetime(last_dt, unit='ns')}"
                    )
        except BacktestFinished:
            chunk, last_dt = _slice_new_completed_bars(
                klines, last_dt, include_last_bar=True,
            )
            if len(chunk) > 0:
                accumulated.append(chunk)
                accumulated_rows += len(chunk)

    except Exception as e:
        if accumulated:
            try:
                _flush_accumulated_atomic()
            except Exception:
                pass
        elapsed = time.time() - t0
        return {
            "symbol": symbol,
            "file": output_file,
            "rows": 0,
            "status": "error",
            "error": str(e),
            "elapsed": elapsed,
        }
    finally:
        if api:
            api.close()

    if accumulated:
        _flush_accumulated_atomic()

    if not part_files and not os.path.exists(output_path):
        elapsed = time.time() - t0
        return {"symbol": symbol, "file": output_file, "rows": 0, "status": "empty", "elapsed": elapsed}

    is_incremental = backtest_start > start_dt
    has_new_data = len(part_files) > initial_part_count

    if is_incremental and not has_new_data and not part_files and os.path.exists(output_path):
        elapsed = time.time() - t0
        try:
            meta = _get_parquet_metadata(output_path)
            rows = meta["num_rows"] if meta else 0
            logger.info(f"[无需更新] {symbol} 已经是最新状态 ({rows} 行)")
            return {
                "symbol": symbol,
                "file": output_file,
                "rows": rows,
                "status": "skipped",
                "elapsed": elapsed,
            }
        except Exception:
            pass

    try:
        full_df = _merge_parts()
        if full_df is None:
            full_df = pd.read_parquet(output_path)

        rows = len(full_df)
        if rows == 0:
            elapsed = time.time() - t0
            return {"symbol": symbol, "file": output_file, "rows": 0, "status": "empty", "elapsed": elapsed}

        dt_min = pd.to_datetime(full_df["datetime"].iloc[0], unit="ns")
        dt_max = pd.to_datetime(full_df["datetime"].iloc[-1], unit="ns")
        gap_count = _check_gap_count(full_df)
        vol_ratio = _volume_nonzero_ratio(full_df)
        if vol_ratio < VOLUME_NONZERO_MIN_RATIO:
            elapsed = time.time() - t0
            return {
                "symbol": symbol,
                "file": output_file,
                "rows": rows,
                "status": "error",
                "error": f"volume_zero(ratio={vol_ratio:.4f})",
                "elapsed": elapsed,
            }

        manifest = _load_manifest(output_dir)
        manifest.setdefault("_meta", {})["session_note"] = SESSION_NOTE
        manifest[output_file] = {
            "rows": rows,
            "start_date": dt_min.date().isoformat(),
            "end_date": dt_max.date().isoformat(),
            "download_time": datetime.now().isoformat(),
            "gaps": gap_count,
            "volume_nonzero_ratio": round(vol_ratio, 4),
            "size_mb": round(os.path.getsize(output_path) / (1024 * 1024), 2),
            "part_count": part_count,
            "has_night_session": has_night,
            "kl_window": kl_window,
            "incremental": backtest_start > start_dt,
            "schema_version": 1,
        }
        _save_manifest(output_dir, manifest)

        elapsed = time.time() - t0
        logger.info(f"[落盘成功] {symbol} -> {output_file}: {rows} 行 ({elapsed:.1f}s, 空洞={gap_count})")
        return {
            "symbol": symbol,
            "file": output_file,
            "rows": rows,
            "status": "ok",
            "elapsed": elapsed,
            "date_range": f"{dt_min.date()} ~ {dt_max.date()}",
            "gaps": gap_count,
        }
    except Exception as e:
        elapsed = time.time() - t0
        return {
            "symbol": symbol,
            "file": output_file,
            "rows": 0,
            "status": "error",
            "error": str(e),
            "elapsed": elapsed,
        }


def main():
    parser = argparse.ArgumentParser(description="分月合约 1 分钟 K 线串行高速下载器（v2.6）")
    parser.add_argument("-s", "--symbol", default="SHFE.rb", help="品种标准代码，如 SHFE.rb, DCE.v, CZCE.RM")
    parser.add_argument("-y", "--years", nargs=2, type=int, default=[2021, 2026], help="起止年份范围，如：2021 2026")
    parser.add_argument("-o", "--output", default=None, help="目标输出目录（默认: data/tq/{prefix}）")
    parser.add_argument("-f", "--force", action="store_true", help="全面重洗下载模式，忽略本地已有文件")
    parser.add_argument(
        "-u", "--update", action="store_true",
        help="尾部更新模式：质检通过的合约若距 end_dt 超过 7 天仍续传补尾（不删旧文件）",
    )
    parser.add_argument("-r", "--repair", action="store_true", help="增量质量修复模式：仅检测并下载缺陷或残片合约")
    parser.add_argument(
        "--deep-check",
        action="store_true",
        help="与 -r 联用：强制全量读 parquet 做 gap 扫描（默认 manifest 优先，缺失条目才读 parquet）",
    )
    parser.add_argument("--real-expire", action="store_true", help="查询真实到期日（注意：对已退市的历史合约基本无效，仅对当前活跃合约有意义）")
    parser.add_argument("--max-retries", type=int, default=2, help="错误合约最大重试轮次")
    parser.add_argument(
        "--shard",
        default=None,
        help="分片并行下载，格式 'N/M'（第 N 片，共 M 片，从 1 开始）。"
        "各片使用独立进程锁（.download.shardNofM.lock），不同片号可并行；"
        "各片共享 manifest.json 可能互相覆盖，全部完成后建议再运行 -r 刷新 manifest。例：--shard 1/4",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="开启 DEBUG 级别日志")
    parser.add_argument(
        "--reconcile-only",
        action="store_true",
        help="仅刷新 manifest / 合并 orphan 分片，不连接 TQSDK 下载",
    )
    parser.add_argument(
        "--rebuild-continuous",
        action="store_true",
        help="pipeline 结束后运行 build_rollover_map.py -s {prefix}",
    )
    parser.add_argument(
        "--all-months",
        action="store_true",
        help="下载交易所全月份（忽略 rollover_rules 交割月白名单）",
    )
    parser.add_argument(
        "--prune-only",
        action="store_true",
        help="仅删除非交割月白名单的分月 parquet（不连接 TQSDK）",
    )
    parser.add_argument(
        "--prune-dry-run",
        action="store_true",
        help="与 --prune-only 联用：只打印将删除的文件",
    )
    parser.add_argument(
        "--phase",
        choices=["two", "oi", "1m", "full"],
        default="two",
        help="two=OI→建图→主力1m（默认）| oi | 1m | full=传统全量1m",
    )
    parser.add_argument(
        "--two-phase",
        action="store_true",
        help="等同 --phase two（保留兼容；默认已是两阶段）",
    )
    parser.add_argument(
        "--then-1m",
        action="store_true",
        help="与 --phase oi 联用：Phase-1 结束后自动跑 Phase-2",
    )
    parser.add_argument(
        "--compare-rollover",
        default=None,
        metavar="PATH",
        help="两阶段建图后与参考 rollover_map.parquet 对比",
    )
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        for h in logger.handlers:
            h.setLevel(logging.DEBUG)

    symbol = args.symbol
    prefix = symbol.split(".")[-1]
    start_year, end_year = args.years[0], args.years[1]
    output_dir = args.output or os.path.join(ROOT, "data", "tq", prefix)
    os.makedirs(output_dir, exist_ok=True)

    # 中金所品种校验（本脚本的 gap 检测不兼容中金所 13:00 开盘的午休时间）
    if symbol.startswith("CFFEX."):
        logger.warning(
            f"[警告] {symbol} 属于中金所品种，本脚本的 gap 检测基于商品期货交易时段，"
            f"中金所 13:00 开盘的午休时间会被误判为 gap，建议人工核对结果。"
        )

    # 年份跨度警告（CZCE 合约代码只用 yy[-1]，跨越10年会撞键）
    if end_year - start_year > 9:
        logger.warning(
            f"[警告] 年份跨度 {end_year - start_year} 年 > 9 年，"
            f"CZCE 品种合约代码可能发生冲突（如 2020 vs 2030 都变成 '0'），"
            f"建议拆分成多个小段下载！"
        )

    logger.info(f"{'='*60}")
    phase_label = (
        "two-phase" if args.phase == "two" or args.two_phase else args.phase
    )
    logger.info(f"分月合约下载（v2.9 two-phase）")
    logger.info(f"执行品种   : {symbol}")
    logger.info(f"模式       : {phase_label}")
    logger.info(f"年份范围   : {start_year} ~ {end_year}")
    logger.info(f"落盘目录   : {output_dir}")
    logger.info(f"强制覆盖   : {'是' if args.force else '否'}")
    logger.info(f"尾部更新   : {'是' if args.update else '否'}")
    logger.info(f"修复模式   : {'是' if args.repair else '否'}")
    if args.repair:
        logger.info(f"质检深度   : {'parquet 全量 (--deep-check)' if args.deep_check else 'manifest 优先'}")
    if args.all_months:
        logger.info("交割月范围 : 全月份 (--all-months)")
    else:
        allowed = allowed_months_for_symbol(_rollover_symbol_key(prefix))
        if allowed:
            logger.info(f"交割月范围 : 白名单 {sorted(allowed)} (rollover_rules)")
        else:
            logger.info("交割月范围 : 交易所默认全月份（该品种无白名单）")
    logger.info(f"{'='*60}")

    if args.prune_only:
        prune_non_delivery_monthlies(
            output_dir, prefix, dry_run=args.prune_dry_run,
        )
        return

    if args.reconcile_only:
        stats = reconcile_manifest(
            output_dir, prefix, None, yymm_len=_yymm_len_for_prefix(prefix),
        )
        logger.info(
            f"reconcile 完成: 磁盘分月 {stats['updated']} 个, "
            f"移除 stale manifest {stats['removed']} 条, "
            f"仍缺 canonical 的 orphan: {stats['orphan_only'][:10]}"
        )
        if args.rebuild_continuous:
            _run_rebuild_continuous(prefix)
        return

    try:
        with download_lock(output_dir, symbol, args.shard):
            auth = get_auth()

            run_oi = args.phase in ("oi", "two") or args.two_phase
            run_1m = args.phase in ("1m", "two") or args.two_phase or args.then_1m
            run_full = args.phase == "full"

            if run_oi:
                oi_dates = _build_oi_contract_dates(
                    symbol, start_year, end_year, auth, args.real_expire,
                    all_months=args.all_months,
                )
                _run_oi_pipeline(args, symbol, prefix, output_dir, oi_dates, auth)
                rc = _run_build_rollover_from_oi(prefix, compare_ref=args.compare_rollover)
                if rc != 0:
                    logger.error(f"build_rollover_map 失败 (exit {rc})")
                    sys.exit(rc)
                if not run_1m:
                    logger.info(
                        "Phase-1 完成。下一步: --phase 1m  或  --two-phase 已含 Phase-2"
                    )
                    return

            if run_1m:
                dw = load_dominant_windows(output_dir)
                if not dw or not dw.get("windows"):
                    logger.error(
                        "未找到 dominant_windows.json，请先 --phase oi 或 --two-phase"
                    )
                    sys.exit(1)
                contract_dates = _build_contract_dates(
                    symbol, start_year, end_year, auth, args.real_expire,
                    all_months=args.all_months,
                )
                _run_download_pipeline(
                    args, symbol, prefix, start_year, end_year, output_dir,
                    contract_dates, auth, dominant_windows=dw,
                )
                return

            if run_full:
                contract_dates = _build_contract_dates(
                    symbol, start_year, end_year, auth, args.real_expire,
                    all_months=args.all_months,
                )
                _run_download_pipeline(
                    args, symbol, prefix, start_year, end_year, output_dir,
                    contract_dates, auth,
                )
    except RuntimeError as e:
        logger.error(str(e))
        sys.exit(1)


def _run_oi_pipeline(
    args: argparse.Namespace,
    symbol: str,
    prefix: str,
    output_dir: str,
    contract_dates: dict,
    auth: TqAuth,
) -> None:
    logger.info(f"Phase-1 OI scout: {len(contract_dates)} 个合约")
    os.makedirs(oi_daily_dir(output_dir), exist_ok=True)
    t_start = time.time()
    total_ok = total_skip = total_empty = total_error = 0

    items = list(contract_dates.items())
    if args.shard:
        n_str, m_str = args.shard.split("/")
        n, m = int(n_str), int(m_str)
        items = items[n - 1::m]

    for idx, (sym, meta) in enumerate(items):
        result = download_oi_daily_contract(
            sym, meta, auth, output_dir, prefix, args.force,
        )
        tag = sym.split(".")[-1]
        if result["status"] == "ok":
            total_ok += 1
            logger.info(f"  [{idx+1}/{len(items)}] {tag}: {result['rows']} days OI")
        elif result["status"] == "skipped":
            total_skip += 1
            logger.info(f"  [{idx+1}/{len(items)}] {tag}: 跳过 ({result.get('date_range', '')})")
        elif result["status"] == "empty":
            total_empty += 1
            logger.warning(f"  [{idx+1}/{len(items)}] {tag}: 无 OI 数据")
        else:
            total_error += 1
            logger.error(f"  [{idx+1}/{len(items)}] {tag}: {result.get('error', '')}")

    elapsed = time.time() - t_start
    logger.info(
        f"Phase-1 完成 {elapsed:.0f}s | ok={total_ok} skip={total_skip} "
        f"empty={total_empty} err={total_error}"
    )


def _run_build_rollover_from_oi(prefix: str, compare_ref: str | None = None) -> int:
    script = os.path.join(ROOT, "tools", "build_rollover_map.py")
    cmd = [
        sys.executable, script, "-s", prefix,
        "--from-oi-daily", "--map-only", "--no-verify", "--no-compare-rq",
    ]
    if compare_ref:
        cmd.extend(["--compare-rollover", compare_ref])
    logger.info(f"Phase-1 建图: {' '.join(cmd[2:])}")
    rc = subprocess.run(cmd, cwd=ROOT, check=False)
    return rc.returncode


def _run_rebuild_continuous(prefix: str) -> int:
    script = os.path.join(ROOT, "tools", "build_rollover_map.py")
    cmd = [
        sys.executable, script, "-s", prefix,
        "--from-oi-daily", "--no-verify", "--no-compare-rq",
    ]
    logger.info(f"触发连续合约/移仓成本重建: {' '.join(cmd[2:])}")
    rc = subprocess.run(cmd, cwd=ROOT, check=False)
    if rc.returncode != 0:
        logger.error(f"build_rollover_map 重建失败 (exit {rc.returncode})")
    return rc.returncode
    if rc.returncode != 0:
        logger.error(f"build_rollover_map 退出码 {rc.returncode}")
    else:
        logger.info("连续合约重建完成")


def _run_download_pipeline(
    args: argparse.Namespace,
    symbol: str,
    prefix: str,
    start_year: int,
    end_year: int,
    output_dir: str,
    contract_dates: dict,
    auth: TqAuth,
    *,
    dominant_windows: dict | None = None,
) -> None:
    if dominant_windows:
        win_keys = set(dominant_windows.get("windows", {}).keys())
        contract_dates = {
            sym: apply_windows_to_meta(meta, dominant_windows, meta["yymm"])
            for sym, meta in contract_dates.items()
            if meta["yymm"] in win_keys
        }
        logger.info(f"Phase-2 主力 1m: {len(contract_dates)} 个窗口合约")
    logger.info(f"规划流水线内共有 {len(contract_dates)} 个目标合约")

    if args.repair:
        reconcile_manifest(
            output_dir, prefix, contract_dates, yymm_len=_yymm_len_for_prefix(prefix),
        )
        logger.info("触发动态质量扫描引擎...")
        manifest = _load_manifest(output_dir)
        good, bad = [], []
        manifest_hits = parquet_hits = 0
        for sym, meta_info in contract_dates.items():
            output_file = f"{prefix}_{meta_info['yymm']}.parquet"
            m_entry = manifest.get(output_file)
            is_good, reason, _ = _check_contract_quality(
                sym,
                meta_info,
                output_dir,
                prefix,
                manifest_entry=m_entry,
                deep=args.deep_check,
                repair_mode=True,
            )
            if is_good and reason.startswith("ok(manifest"):
                manifest_hits += 1
            elif is_good:
                parquet_hits += 1
            if is_good:
                good.append((sym, reason))
            else:
                bad.append((sym, reason))

        # orphan 分片无 canonical 文件
        for _sym, meta_info in contract_dates.items():
            yymm = meta_info["yymm"]
            canonical = f"{prefix}_{yymm}.parquet"
            if os.path.exists(os.path.join(output_dir, canonical)):
                continue
            parts = _list_part_files(output_dir, prefix, yymm)
            if parts and _sym not in [s for s, _ in bad]:
                bad.append((_sym, f"orphan_parts({len(parts)})"))

        logger.info(
            f"扫描结果 -> 达标: {len(good)} 个 (manifest {manifest_hits}, parquet {parquet_hits})"
            f" | 缺陷/缺失: {len(bad)} 个"
        )
        if bad:
            logger.info("待修复合约优先级队列 (前10个):")
            for sym, reason in bad[:10]:
                logger.info(f"  -> {sym}: 状态码={reason}")
            symbols_to_download = [sym for sym, _ in bad]
        else:
            logger.info("本地全量合约质量极佳，无需任何修复。")
            symbols_to_download = []
    else:
        symbols_to_download = list(contract_dates.keys())

    # 分片并行下载：按 --shard N/M 切片
    if args.shard:
        try:
            n_str, m_str = args.shard.split("/")
            n, m = int(n_str), int(m_str)
            if not (1 <= n <= m):
                raise ValueError(f"shard N 必须在 [1, M] 范围内，当前 N={n}, M={m}")
        except Exception as e:
            logger.error(f"--shard 参数解析失败: {e}（格式应为 N/M，如 1/4）")
            sys.exit(1)
        total = len(symbols_to_download)
        # 均匀切片：第 n 片（1-based）取索引 n-1, n-1+M, n-1+2M, ...
        sharded = symbols_to_download[n - 1::m]
        logger.info(f"分片模式: 第 {n}/{m} 片，本片合约 {len(sharded)}/{total} 个")
        logger.warning(
            "分片并行：各进程共享 manifest.json，后写可能覆盖先写条目；"
            "全部 shard 完成后建议运行 -r 刷新 manifest。"
        )
        logger.info(f"  本片起点: {sharded[0] if sharded else '无'}")
        logger.info(f"  本片终点: {sharded[-1] if sharded else '无'}")
        symbols_to_download = sharded

    t_start = time.time()
    total_ok = total_skip = total_empty = total_error = 0
    error_symbols = []
    empty_symbols = []

    total_count = len(symbols_to_download)
    for idx, sym in enumerate(symbols_to_download):
        t_contract = time.time()
        result = download_single_contract(
            sym, contract_dates[sym], auth, output_dir, prefix, args.force, update=args.update
        )

        if result["status"] == "ok":
            total_ok += 1
            logger.info(
                f"  [{idx+1}/{total_count}] {sym.split('.')[-1]}: "
                f"写入 {result['rows']} 行 ({time.time() - t_contract:.1f}s)"
            )
        elif result["status"] == "skipped":
            total_skip += 1
            logger.info(
                f"  [{idx+1}/{total_count}] {sym.split('.')[-1]}: "
                f"跳过校验良好数据 ({result.get('date_range', '')})"
            )
        elif result["status"] == "empty":
            total_empty += 1
            empty_symbols.append(sym)
            logger.warning(f"  [{idx+1}/{total_count}] {sym}: 暂无任何历史数据")
        else:
            total_error += 1
            error_symbols.append(sym)
            logger.error(f"  [{idx+1}/{total_count}] {sym}: 异常终止 -> {result.get('error', '')}")

        elapsed_so_far = time.time() - t_start
        avg_per_contract = elapsed_so_far / (idx + 1)
        remaining = (total_count - idx - 1) * avg_per_contract
        logger.info(f"  [调度面板] 已耗时: {elapsed_so_far:.0f}s, 队列剩余预计: {remaining/60:.1f}分钟")

    # 错误合约：force 重试；空序列：仅轻量重试 1 次（非 force），仍空则记入 manifest
    if error_symbols and args.max_retries > 0:
        failed_map = {sym: "error" for sym in error_symbols}
        logger.info(
            f"\n{'='*60}\n发现异常失败合约 ({len(failed_map)} 个)，切入 force 重试容灾流程..."
        )
        for retry in range(args.max_retries):
            if not failed_map:
                break
            retry_items = list(failed_map.items())
            failed_map = {}
            logger.info(f"--- 第 {retry+1} 轮 error 补偿拉取（force，冷却 2 秒...） ---")
            time.sleep(2)
            for sym, _orig in retry_items:
                result = download_single_contract(
                    sym, contract_dates[sym], auth, output_dir, prefix,
                    force=True, update=args.update,
                )
                if result["status"] in ["ok", "skipped"]:
                    total_ok += 1
                    total_error -= 1
                    logger.info(f"  [补偿成功] {sym} (error -> {result['status']})")
                elif result["status"] == "empty":
                    empty_symbols.append(sym)
                    total_error -= 1
                    total_empty += 1
                    logger.warning(f"  [补偿转空] {sym}: error -> empty")
                else:
                    failed_map[sym] = "error"
                    logger.error(f"  [补偿失败] {sym}: {result.get('error', '')}")

    if empty_symbols:
        logger.info(
            f"\n{'='*60}\n空序列合约 ({len(empty_symbols)} 个)，轻量重试 1 次（非 force）..."
        )
        time.sleep(2)
        still_empty = []
        for sym in empty_symbols:
            result = download_single_contract(
                sym, contract_dates[sym], auth, output_dir, prefix,
                force=False, update=args.update,
            )
            if result["status"] in ["ok", "skipped"]:
                total_ok += 1
                total_empty -= 1
                logger.info(f"  [空序列恢复] {sym} -> {result['status']}")
            else:
                still_empty.append(sym)
                _record_no_data_contract(output_dir, prefix, contract_dates[sym], sym)
                logger.warning(f"  [确认无数据] {sym}，已记入 manifest (skip_reason=no_data)")
        empty_symbols = still_empty

    elapsed = time.time() - t_start
    logger.info(
        f"\n{'='*60}\n pipeline 运行完毕! 总累计耗时: {elapsed:.0f}s ({elapsed/60:.1f}min)"
    )
    logger.info(
        f"  状态统计 -> 成功落盘: {total_ok} | 跳过缓存: {total_skip} | 空序列: {total_empty} | 彻底失败: {total_error}"
    )

    logger.info(f"\n目标仓储路径下 parquet 文件级元数据概览:")
    manifest = _load_manifest(output_dir)
    total_size = 0
    for f in sorted(os.listdir(output_dir)):
        fp = os.path.join(output_dir, f)
        if os.path.isfile(fp) and f.startswith(f"{prefix}_") and f.endswith(".parquet"):
            size_mb = os.path.getsize(fp) / 1024 / 1024
            # 优先读 manifest，避免逐文件解析 parquet metadata
            m_entry = manifest.get(f)
            if m_entry:
                rows = m_entry.get("rows", 0)
            else:
                meta = _get_parquet_metadata(fp)
                rows = meta["num_rows"] if meta else 0
            logger.info(f"   {f}: {rows} rows, {size_mb:.2f} MB")
            total_size += os.path.getsize(fp)

    logger.info(f"\n存储资产总物理大小: {total_size/1024/1024:.2f} MB")

    rec = reconcile_manifest(
        output_dir, prefix, contract_dates, yymm_len=_yymm_len_for_prefix(prefix),
    )
    logger.info(
        f"manifest reconcile: 分月 {rec['updated']} 个, 移除 stale {rec['removed']} 条, "
        f"orphan-only {len(rec['orphan_only'])} 个"
    )

    if not args.all_months:
        pr = prune_non_delivery_monthlies(output_dir, prefix, dry_run=False)
        if not pr.get("skipped"):
            logger.info(f"非白名单分月清理: 删除 {len(pr['removed'])} 个文件")

    logger.info(f"{'='*60}")
    _run_rebuild_continuous(prefix)


if __name__ == "__main__":
    main()
