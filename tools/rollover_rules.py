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
    "fu": (3, 6, 9, 12),  # 沪燃油：常年主力为季月 03/06/09/12（非 1/5/9）；数据层待按白名单重建
    "m": (1, 5, 9),   # 豆粕：趋势跟踪缩至习惯主力，跳过 7/8/11/12 过渡月
    "c": (1, 5, 9),   # 玉米：同缩，跳过 3/7/11
    "p": (1, 5, 9),
    "y": (1, 5, 9),
    "l": (1, 5, 9),
    "RM": (1, 5, 9),  # 郑商所菜粕；resolve 大小写不敏感（rm/Rm 同命中）
    "i": (1, 5, 9),   # DCE 铁矿：习惯主力 1/5/9，跳过 3/7/11 等过渡月
    "j": (1, 5, 9),   # DCE 焦炭
    "jm": (1, 5, 9),  # DCE 焦煤
    "MA": (1, 5, 9),
    "TA": (1, 5, 9),
    "SA": (1, 5, 9),
    "FG": (1, 5, 9),
    "SR": (1, 5, 9),
    "ag": (6, 12),  # 实盘习惯主力：6/12 轮动；偶有 08/10/04 但不改白名单（见 2022–26 OI）
    "au": (6, 10, 12),  # 2022–26：常见 06→10→12；保留 06→12 老路径；不含 02/04/08
    "al": None,  # 沪铝：有色做市后逐月换主力，跟 OI
    "zn": None,  # 沪锌：同上
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


def resolve_rollover_symbol_key(symbol_key: str) -> str | None:
    """大小写不敏感解析白名单品种键，返回字典中的规范键；未登记返回 None。

    若大小写撞键（历史上曾有 rm/RM），优先返回全大写键（郑商所习惯）。
    """
    if not symbol_key:
        return None
    if symbol_key in SYMBOL_ALLOWED_DELIVERY_MONTHS:
        return symbol_key
    folded = symbol_key.casefold()
    matches = [k for k in SYMBOL_ALLOWED_DELIVERY_MONTHS if k.casefold() == folded]
    if not matches:
        return None
    for key in matches:
        if key.isupper():
            return key
    return matches[0]


def allowed_months_for_symbol(symbol_key: str) -> tuple[int, ...] | None:
    """查交割月白名单（键大小写不敏感）。

    返回 None 表示不限制交割月：既可能是「已登记为 None」（如 fu），
    也可能是「未登记品种」。调用方不必区分。
    """
    key = resolve_rollover_symbol_key(symbol_key)
    if key is None:
        return None
    return SYMBOL_ALLOWED_DELIVERY_MONTHS[key]
