"""换月规则：交割月白名单、OI 确认天数、切点时刻（与实盘「跟主力」对齐）。"""
from __future__ import annotations

from datetime import date

# 切点：换月日 21:00 CST 平旧开新（与 build_tq_continuous / tq_rollover_data 一致）
ROLLOVER_SWITCH_TIME = "21:00"
ROLLOVER_CONFIRM_DAYS = 3

# 两阶段 OI→1m：Phase-1 日 OI 回看 / Phase-2 主力段缓冲
OI_LOOKBACK_DAYS = 280
OI_FORWARD_BUFFER_DAYS = 14
SLICE_BUFFER_DAYS = 5

# 各品种可交易/可成为主力的交割月（None = 不限制，沿用全部分月）
SYMBOL_ALLOWED_DELIVERY_MONTHS: dict[str, tuple[int, ...] | None] = {
    "rb": (1, 5, 10),
    "hc": (1, 5, 10),
    "fu": (1, 5, 9),
    "m": (1, 3, 5, 7, 8, 9, 11, 12),
    "c": (1, 3, 5, 7, 9, 11),
    "p": (1, 5, 9),
    "rm": (1, 3, 5, 7, 8, 9, 11),
    "RM": (1, 3, 5, 7, 8, 9, 11),
    "i": None,
    "j": None,
    "jm": None,
    "MA": (1, 5, 9),
    "TA": (1, 5, 9),
    "SA": (1, 5, 9),
    "FG": (1, 5, 9),
    "SR": (1, 5, 9),
    "ag": None,
    "au": None,
    "al": None,
    "zn": None,
    "pb": None,
    "sn": None,
    "v": (1, 5, 9),
}


def effective_yymm_len(yymm: str) -> int:
    """磁盘文件名 yymm 长度（TQ 落盘均为 4 位 yyMM；历史 3 位码仍兼容）。"""
    if len(yymm) == 4:
        return 4
    if len(yymm) == 3:
        return 3
    raise ValueError(f"unsupported yymm length: {yymm!r}")


def delivery_month_from_yymm(yymm: str, yymm_len: int | None = None) -> int:
    """从合约代码解析交割月（1–12）。"""
    yl = effective_yymm_len(yymm) if yymm_len is None else yymm_len
    if yl == 4:
        return int(yymm[2:4])
    if yl == 3 and len(yymm) == 3:
        return int(yymm[1:3])
    raise ValueError(f"unsupported yymm={yymm!r} yymm_len={yl}")


def contract_year_from_yymm(yymm: str, yymm_len: int, ref: date | None = None) -> int:
    """解析合约年份（4 位）；郑商所 3 位码用 ref 推断世纪。"""
    ref = ref or date.today()
    if yymm_len == 4:
        yy = int(yymm[:2])
        return yy + 2000 if yy < 50 else yy + 1900
    if yymm_len == 3 and len(yymm) == 3:
        decade = ref.year // 10 * 10
        year = decade + int(yymm[0])
        if year > ref.year + 2:
            year -= 10
        elif year < ref.year - 8:
            year += 10
        return year
    raise ValueError(f"unsupported yymm={yymm!r} yymm_len={yymm_len}")


def is_allowed_contract(yymm: str, yymm_len: int, allowed: tuple[int, ...] | None) -> bool:
    if allowed is None:
        return True
    return delivery_month_from_yymm(yymm, effective_yymm_len(yymm)) in allowed


def filter_df_dict_by_delivery_months(
    df_dict: dict,
    allowed: tuple[int, ...] | None,
    yymm_len: int,
) -> tuple[dict, list[str]]:
    """按交割月白名单过滤分月数据；返回 (filtered, excluded_yymms)。"""
    if allowed is None:
        return df_dict, []
    kept: dict = {}
    excluded: list[str] = []
    for yymm, df in df_dict.items():
        if is_allowed_contract(yymm, yymm_len, allowed):
            kept[yymm] = df
        else:
            excluded.append(yymm)
    return kept, excluded


def allowed_months_for_symbol(symbol_key: str) -> tuple[int, ...] | None:
    return SYMBOL_ALLOWED_DELIVERY_MONTHS.get(symbol_key)
