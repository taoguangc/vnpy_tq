# -*- coding: utf-8 -*-
"""Brooks PA CTA 品种配置（TQ 主力链 CbC；品种键与 data/tq/{folder} 一致）。"""
from __future__ import annotations

from pathlib import Path

from vnpy.trader.constant import Exchange

from strategies.pa_cta.symbol_adaptive import apply_symbol_adaptive

# 品种键 = TQ 目录名（小写）或郑商所 MA/TA；回测为分月 raw + rollover_map CbC
TQ_SYMBOL_ENGINE: dict[str, dict] = {
    "rb": {
        "folder": "rb",
        "file_stem": "rb",
        "exchange": Exchange.SHFE,
        "size": 10,
        "pricetick": 1.0,
        "slippage": 2,
    },
    "hc": {
        "folder": "hc",
        "file_stem": "hc",
        "exchange": Exchange.SHFE,
        "size": 10,
        "pricetick": 1.0,
        "slippage": 2,
    },
    "m": {
        "folder": "m",
        "file_stem": "m",
        "exchange": Exchange.DCE,
        "size": 10,
        "pricetick": 1.0,
        "slippage": 2,
    },
    "ma": {
        "folder": "MA",
        "file_stem": "MA",
        "exchange": Exchange.CZCE,
        "size": 10,
        "pricetick": 1.0,
        "slippage": 2,
    },
    "ta": {
        "folder": "TA",
        "file_stem": "TA",
        "exchange": Exchange.CZCE,
        "size": 5,
        "pricetick": 2.0,
        "slippage": 4,
    },
    # 以下品种 data/tq 已备 CbC；合约规格按国内交易所标准，slippage 取约 2 个 tick
    "ag": {  # 沪银 15kg/手
        "folder": "ag", "file_stem": "ag", "exchange": Exchange.SHFE,
        "size": 15, "pricetick": 1.0, "slippage": 2,
    },
    "au": {  # 沪金 1000g/手
        "folder": "au", "file_stem": "au", "exchange": Exchange.SHFE,
        "size": 1000, "pricetick": 0.02, "slippage": 0.04,
    },
    "c": {  # 玉米 10t/手
        "folder": "c", "file_stem": "c", "exchange": Exchange.DCE,
        "size": 10, "pricetick": 1.0, "slippage": 2,
    },
    "i": {  # 铁矿石 100t/手
        "folder": "i", "file_stem": "i", "exchange": Exchange.DCE,
        "size": 100, "pricetick": 0.5, "slippage": 1,
    },
    "j": {  # 焦炭 100t/手
        "folder": "j", "file_stem": "j", "exchange": Exchange.DCE,
        "size": 100, "pricetick": 0.5, "slippage": 1,
    },
    "jm": {  # 焦煤 60t/手
        "folder": "jm", "file_stem": "jm", "exchange": Exchange.DCE,
        "size": 60, "pricetick": 0.5, "slippage": 1,
    },
    "pb": {  # 沪铅 5t/手
        "folder": "pb", "file_stem": "pb", "exchange": Exchange.SHFE,
        "size": 5, "pricetick": 5.0, "slippage": 10,
    },
    "sa": {  # 纯碱 20t/手（目录 SA）
        "folder": "SA", "file_stem": "SA", "exchange": Exchange.CZCE,
        "size": 20, "pricetick": 1.0, "slippage": 2,
    },
    "v": {  # PVC 5t/手
        "folder": "v", "file_stem": "v", "exchange": Exchange.DCE,
        "size": 5, "pricetick": 1.0, "slippage": 2,
    },
    "al": {  # 沪铝 5t/手
        "folder": "al", "file_stem": "al", "exchange": Exchange.SHFE,
        "size": 5, "pricetick": 5.0, "slippage": 10,
    },
    "zn": {  # 沪锌 5t/手
        "folder": "zn", "file_stem": "zn", "exchange": Exchange.SHFE,
        "size": 5, "pricetick": 5.0, "slippage": 10,
    },
    "y": {  # 豆油 10t/手
        "folder": "y", "file_stem": "y", "exchange": Exchange.DCE,
        "size": 10, "pricetick": 2.0, "slippage": 4,
    },
    "p": {  # 棕榈油 10t/手
        "folder": "p", "file_stem": "p", "exchange": Exchange.DCE,
        "size": 10, "pricetick": 2.0, "slippage": 4,
    },
    "l": {  # 塑料 5t/手
        "folder": "l", "file_stem": "l", "exchange": Exchange.DCE,
        "size": 5, "pricetick": 1.0, "slippage": 2,
    },
    "fg": {  # 玻璃 20t/手（目录 FG）
        "folder": "FG", "file_stem": "FG", "exchange": Exchange.CZCE,
        "size": 20, "pricetick": 1.0, "slippage": 2,
    },
}

# 跨品种研究 / 多品种扫描固定品种池（2026-07-13 定稿）
CROSS_SYMBOL_UNIVERSE: tuple[str, ...] = (
    "i", "jm", "p", "y", "ag", "rb", "hc", "ta",
)


def cross_symbol_list() -> list[str]:
    """返回已配置 TQ 引擎的跨品种列表（保持 CROSS_SYMBOL_UNIVERSE 顺序）。"""
    return [s for s in CROSS_SYMBOL_UNIVERSE if s in TQ_SYMBOL_ENGINE]

LEAN_PROFILE_KEYS: tuple[str, ...] = (
    "rb_min_atr",
    "ttr_rb_min_atr",
    "risk_capital",
    "risk_pct_per_trade",
    "max_position",
    "use_compound_capital",
    "dual_core_enabled",
    "dual_core_soft_enabled",
    "vwap_regime_lookback",
    "vwap_chop_min_crosses",
    "vwap_slope_thresh_ticks",
    "vwap_trend_deadband_ticks",
    "vwap_fade_max_atr",
    "dual_core_exhaustion_atr",
    "dual_core_exhaustion_min_atr",
    "dual_core_soft_min_size_mult",
    "dual_core_soft_min_target_mult",
    "context_layers_enabled",
    "context_layer_fast_bars",
    "context_layer_slow_bars",
    "context_layer_gate_enabled",
    "context_layer_opp08_min_fit",
    "context_layer_opp16_min_fit",
    "vsa_enabled",
    "vsa_volume_window",
    "vsa_session_relative_enabled",
    "vsa_session_lookback_days",
    "vsa_session_min_samples",
    "vsa_low_volume_pct",
    "vsa_high_volume_pct",
    "vsa_spread_atr_mult",
    "vsa_weak_close_ratio",
    "vsa_stopping_close_ratio",
    "vsa_persistence_enabled",
    "vsa_persistence_bars",
    "vsa_persistence_displacement_ticks",
    "vsa_persistence_displacement_atr",
    "vsa_persistence_opposite_tolerance",
    "tf_arm_gate_enabled",
    "tf_counter_exit_mode",
    "setup_risk_mult_enabled",
    "setup_risk_mult_default",
    "late_phase_gate_enabled",
    "aff_gate_enabled",
    "aff_gate_mode",
    "aff_alpha_reject_threshold",
    "aff_alpha_high_threshold",
    "aff_risk_mult_low",
    "aff_risk_mult_high",
    "opp02_aff_gate_enabled",
    "opp02_r2_gate_enabled",
    "opp02_r2_min",
    "opp19_breakout_aff_gate_enabled",
    "opp19_breakout_r2_gate_enabled",
    "opp19_breakout_r2_min",
    "trend_gate_use_chop",
    "trend_gate_r2_period",
    "trend_gate_chop_period",
    "trend_gate_chop_max",
    "opp13_vol_filter_enabled",
    "opp13_min_volume_pct",
    "opp13_climax_volume_pct",
    "opp13_short_max_close_pos",
    "opp13_long_min_close_pos",
    "opp19_rev_gate_enabled",
    "opp19_rev_always_in_gate",
    "opp19_rev_block_strong_counter",
    "opp19_rev_min_bar1_range_atr",
    "opp19_rev_max_bar1_range_atr",
    "opp19_rev_contexts",
    "opp19_rev_morning_cutoff_minute",
    "opp19_rev_night_cutoff_minute",
    "opp19_rev_arm_mode",
    "aff_archetype_router_enabled",
    "aff_archetype_alpha_low",
    "aff_archetype_compression_min",
    "aff_archetype_expansion_env_min",
    "aff_archetype_exhaustion_env_max",
    "aff_archetype_use_lane_matrix",
    "aff_archetype_adaptive_enabled",
    "aff_archetype_minimal_enabled",
    "aff_archetype_trend_bypass_prefixes",
    "symbol_adaptive_enabled",
    "symbol_vol_baseline_1m",
    "symbol_liquidity_ref_1m",
    "symbol_liquidity_low_ratio",
    "symbol_liquidity_risk_floor",
    "symbol_liquidity_runtime_enabled",
    "symbol_liquidity_tier",
    "opening_rev_enabled",
    "disabled_setups",
    "setup_shrinkage_enabled",
    "setup_shrinkage_overrides",
    "setup_shrinkage_hard_disable",
    "exit_family_v3_enabled",
)

TQ_LEAN_DEFAULT_MODE = "cbc"
TQ_ROLLOVER_SWITCH = "21:00"

# 基准（CbC + rollover_map，2023-05-17~2026-05-16 含成本）:
#   54RT/38.9%WR/-43,543/Sharpe-0.45/PF0.75/MDD-23.8%
TQ_CBC_BASELINE_RB: dict[str, float | int] = {
    "rt": 54, "wr": 38.9, "pnl": -43_543, "sharpe": -0.45, "pf": 0.75,
}

# EXP-026 Phase-1 出场执行硬不变量基线（同上区间含成本；production profile）:
#   39RT/43.6%WR/+9,647/Sharpe0.14/MDD-12.24%/最长持有5.6h/换月0
# 状态：stop_price / stop_source / pending_exit_order / remaining_position
# 注：旧 EXP-006 +20k~+23k 与 EXP-026 初修 +6.5k 均为旧语义参考，不可直接比 alpha。
TQ_EXEC_BASELINE_RB: dict[str, float | int] = {
    "rt": 39, "wr": 43.6, "pnl": 9_647, "sharpe": 0.14, "pf": 1.10,
}

TQ_LEAN_RB_OVERRIDES: dict[str, float | int | bool] = {
    "max_position": 35,
    "rb_min_atr": 8.0,
    "ttr_rb_min_atr": 5.5,
}

# 每品种参数档：按 rb 选择性（5m ATR 85.4% 分位）推导的绝对 ATR 门槛 +
# 名义敞口上限（rb 35 手≈116 万元）反推的 max_position。
# 来源 scripts/profile_symbol_params.py，区间 2023-05~2026-05。rb 保持 RB_OVERRIDES 不覆盖。
TQ_SYMBOL_PARAM_OVERRIDES: dict[str, dict[str, float | int]] = {
    "hc": {"rb_min_atr": 8.0, "ttr_rb_min_atr": 5.0, "max_position": 33},
    "m": {"rb_min_atr": 8.0, "ttr_rb_min_atr": 5.0, "max_position": 38},
    "ma": {"rb_min_atr": 7.0, "ttr_rb_min_atr": 5.0, "max_position": 47},
    "ag": {"rb_min_atr": 37.0, "ttr_rb_min_atr": 12.0, "max_position": 10},
    "au": {"rb_min_atr": 1.28, "ttr_rb_min_atr": 0.52, "max_position": 3},
    "c": {"rb_min_atr": 4.0, "ttr_rb_min_atr": 3.0, "max_position": 49},
    "i": {"rb_min_atr": 3.0, "ttr_rb_min_atr": 2.0, "max_position": 15},
    "j": {"rb_min_atr": 8.5, "ttr_rb_min_atr": 6.0, "max_position": 6},
    "jm": {"rb_min_atr": 7.5, "ttr_rb_min_atr": 5.0, "max_position": 15},
    "pb": {"rb_min_atr": 30.0, "ttr_rb_min_atr": 15.0, "max_position": 14},
    "sa": {"rb_min_atr": 9.0, "ttr_rb_min_atr": 5.0, "max_position": 39},
    "ta": {"rb_min_atr": 16.0, "ttr_rb_min_atr": 10.0, "max_position": 43},
    "v": {"rb_min_atr": 13.0, "ttr_rb_min_atr": 9.0, "max_position": 43},
    # EXP-024：新品种机械尺度（非网格搜；与 profile_symbol_params 分位法待补）
    "al": {"rb_min_atr": 30.0, "ttr_rb_min_atr": 15.0, "max_position": 14},
    "zn": {"rb_min_atr": 30.0, "ttr_rb_min_atr": 15.0, "max_position": 14},
    "y": {"rb_min_atr": 10.0, "ttr_rb_min_atr": 6.0, "max_position": 25},
    "p": {"rb_min_atr": 10.0, "ttr_rb_min_atr": 6.0, "max_position": 25},
    "l": {"rb_min_atr": 8.0, "ttr_rb_min_atr": 5.0, "max_position": 43},
    "fg": {"rb_min_atr": 9.0, "ttr_rb_min_atr": 5.0, "max_position": 39},
}

# EXP-024：跨品种扫描用干净 Base（无禁单 / 无 Setup AFF / 无 Router / 无 hc 特化）
GENERIC_BASE_PROFILE: dict = {
    "risk_capital": 10_000.0,
    "risk_pct_per_trade": 0.05,
    "max_position": 35,
    "rb_min_atr": 7.0,
    "ttr_rb_min_atr": 5.0,
    "use_compound_capital": False,
    "dual_core_enabled": True,
    "vsa_enabled": True,
    "vsa_persistence_enabled": False,
    "setup_risk_mult_enabled": True,
    "late_phase_gate_enabled": True,
    "aff_gate_enabled": True,
    "aff_gate_mode": "sizing",
    "opp02_aff_gate_enabled": False,
    "opp19_breakout_aff_gate_enabled": False,
    "opp02_r2_gate_enabled": False,
    "opp19_breakout_r2_gate_enabled": False,
    "aff_archetype_router_enabled": False,
    "symbol_adaptive_enabled": False,
    "opp13_vol_filter_enabled": False,
    "disabled_setups": "",
}

SYMBOL_PROFILES: dict[str, dict] = {
    "rb": {
        "exchange": Exchange.SHFE,
        "size": 10,
        "pricetick": 1.0,
        "slippage": 2,
        "rb_min_atr": 7.0,
        "ttr_rb_min_atr": 5.0,
        "risk_capital": 10_000.0,
        "risk_pct_per_trade": 0.05,
        "max_position": 50,
        "use_compound_capital": False,
        "dual_core_enabled": True,
        "vsa_enabled": True,
        "vsa_persistence_enabled": False,
        "setup_risk_mult_enabled": True,
        "late_phase_gate_enabled": True,
        "aff_gate_enabled": True,
        "aff_gate_mode": "sizing",
        # EXP-006 KEEP（样本内 rb）：Setup AFF alpha≥0.25 硬拒 OPP02/OPP19 突破
        # EXP-007 REVERT：R²@0.30 替代 AFF → -29,434（劣于 +20,428），见 experiments.md
        "opp02_aff_gate_enabled": True,
        "opp19_breakout_aff_gate_enabled": True,
        "opp02_r2_gate_enabled": False,
        "opp19_breakout_r2_gate_enabled": False,
        # EXP-023 REVERT：OPP12_ OOS Δ=0（无效应）→ 撤禁单；见 experiments.md
    },
    "hc": {
        "exchange": Exchange.SHFE,
        "size": 10,
        "pricetick": 1.0,
        "slippage": 2,
        "rb_min_atr": 8.0,
        "ttr_rb_min_atr": 5.0,
        "risk_capital": 10_000.0,
        "risk_pct_per_trade": 0.05,
        "max_position": 33,
        "use_compound_capital": False,
        "dual_core_enabled": True,
        "vsa_enabled": True,
        "vsa_persistence_enabled": False,
        "setup_risk_mult_enabled": True,
        "late_phase_gate_enabled": True,
        "aff_gate_enabled": True,
        "aff_gate_mode": "sizing",
        "opp02_aff_gate_enabled": True,
        "opp19_breakout_aff_gate_enabled": True,
        "opp02_r2_gate_enabled": False,
        "opp19_breakout_r2_gate_enabled": False,
        # EXP-018：品种自适应 LOW 档（1m vol 936 vs rb 2861；仅 LOW 降仓，Router 关）
        "symbol_adaptive_enabled": True,
        "symbol_vol_baseline_1m": 936.0,
        "symbol_liquidity_ref_1m": 2861.0,
        "symbol_liquidity_tier": "LOW",
        "symbol_liquidity_runtime_enabled": True,
        "aff_archetype_router_enabled": False,
        # EXP-019：OPP13 边界量能筛选（LOW 流动性日低假反转过滤）
        "opp13_vol_filter_enabled": True,
        "opp13_min_volume_pct": 55.0,
        "opp13_climax_volume_pct": 70.0,
        # hc 保留 FAST_TRACK OD_REV（组合层与 pending 模式不兼容）；空头降仓见 _SETUP_RISK_MULT
        "opp19_rev_arm_mode": "FAST_TRACK",
        # EXP-009F KEEP（hc 样本内）；EXP-023 OOS HOLD（n 坍塌 6→1）
        "disabled_setups": "OPP13_,OPP15_,OPP19_5M_OD_REV_SHORT",
    },
    "au": {
        "exchange": Exchange.SHFE,
        "size": 1000,
        "pricetick": 0.02,
        "slippage": 0.04,
        "rb_min_atr": 1.28,
        "ttr_rb_min_atr": 0.52,
        "risk_capital": 10_000.0,
        "risk_pct_per_trade": 0.05,
        "max_position": 3,
        "use_compound_capital": False,
        "dual_core_enabled": True,
        "vsa_enabled": True,
        "setup_risk_mult_enabled": True,
        "late_phase_gate_enabled": True,
        "aff_gate_enabled": True,
        "aff_gate_mode": "sizing",
        "opp02_aff_gate_enabled": True,
        "opp19_breakout_aff_gate_enabled": True,
        # EXP-022 候选；EXP-023 OOS HOLD（极端单笔驱动嫌疑）
        "disabled_setups": "OPP15_,OPP12_,OPP13_",
    },
    "ma": {
        "exchange": Exchange.CZCE,
        "size": 10,
        "pricetick": 1.0,
        "slippage": 2,
        "rb_min_atr": 7.0,
        "ttr_rb_min_atr": 5.0,
        "risk_capital": 10_000.0,
        "risk_pct_per_trade": 0.05,
        "max_position": 47,
        "use_compound_capital": False,
        "dual_core_enabled": True,
        "vsa_enabled": True,
        "setup_risk_mult_enabled": True,
        "late_phase_gate_enabled": True,
        "aff_gate_enabled": True,
        "aff_gate_mode": "sizing",
        "opp02_aff_gate_enabled": True,
        "opp19_breakout_aff_gate_enabled": True,
        # EXP-022 候选；EXP-023 OOS HOLD（未过完整 KEEP-OOS gate）
        "disabled_setups": "OPP15_,OPP13_",
    },
    "j": {
        "exchange": Exchange.DCE,
        "size": 100,
        "pricetick": 0.5,
        "slippage": 1,
        "rb_min_atr": 8.5,
        "ttr_rb_min_atr": 6.0,
        "risk_capital": 10_000.0,
        "risk_pct_per_trade": 0.05,
        "max_position": 6,
        "use_compound_capital": False,
        "dual_core_enabled": True,
        "vsa_enabled": True,
        "setup_risk_mult_enabled": True,
        "late_phase_gate_enabled": True,
        "aff_gate_enabled": True,
        "aff_gate_mode": "sizing",
        "opp02_aff_gate_enabled": True,
        "opp19_breakout_aff_gate_enabled": True,
        # EXP-022 候选；EXP-023 OOS HOLD（IS/OOS 不同向 + PF 劣化）
        "disabled_setups": "OPP15_",
    },
}


def build_strategy_setting(
    profile: dict,
    *,
    capital: float = 200_000.0,
    max_position: int = 50,
) -> dict:
    """从 SYMBOL_PROFILES 构建 lean 策略 setting（仅 LEAN_PROFILE_KEYS）。"""
    setting = {
        "capital": capital,
        "contract_size": profile["size"],
        "rb_min_atr": profile.get("rb_min_atr", 7.0),
        "ttr_rb_min_atr": profile.get("ttr_rb_min_atr", 5.0),
        "risk_capital": profile.get("risk_capital", 5_000.0),
        "risk_pct_per_trade": profile.get("risk_pct_per_trade", 0.025),
        "max_position": profile.get("max_position", max_position),
        "use_compound_capital": profile.get("use_compound_capital", False),
    }
    for key in LEAN_PROFILE_KEYS:
        if key in profile:
            setting[key] = profile[key]
    return setting


def resolve_generic_base_profile(
    symbol: str,
    root: Path,
    **_: object,
) -> dict:
    """干净 Base profile：不读 SYMBOL_PROFILES，仅合约规格 + 机械参数。"""
    key = symbol.lower()
    if key not in TQ_SYMBOL_ENGINE:
        known = ", ".join(sorted(TQ_SYMBOL_ENGINE))
        raise ValueError(f"未知品种 {symbol}，可选: {known}")

    profile = GENERIC_BASE_PROFILE.copy()
    profile["symbol"] = key
    eng = TQ_SYMBOL_ENGINE[key]
    profile["exchange"] = eng["exchange"]
    profile["size"] = eng["size"]
    profile["pricetick"] = eng["pricetick"]
    profile["slippage"] = eng["slippage"]
    data_dir = root / "data" / "tq" / eng["folder"]
    profile["data_dir"] = data_dir
    profile["file_stem"] = eng["file_stem"]
    profile["rollover_map"] = data_dir / "rollover_map.parquet"
    profile.update(TQ_SYMBOL_PARAM_OVERRIDES.get(key, {}))
    return profile


def resolve_symbol_profile(
    symbol: str,
    root: Path,
) -> dict:
    """解析 TQ CbC 品种：data/tq/{folder} + rollover_map。"""
    key = symbol.lower()
    if key not in TQ_SYMBOL_ENGINE:
        known = ", ".join(sorted(TQ_SYMBOL_ENGINE))
        raise ValueError(f"未知品种 {symbol}，可选: {known}")

    template_key = key if key in SYMBOL_PROFILES else "rb"
    profile = SYMBOL_PROFILES[template_key].copy()
    profile["symbol"] = key
    eng = TQ_SYMBOL_ENGINE[key]
    profile["exchange"] = eng["exchange"]
    profile["size"] = eng["size"]
    profile["pricetick"] = eng["pricetick"]
    profile["slippage"] = eng["slippage"]
    data_dir = root / "data" / "tq" / eng["folder"]
    file_stem = eng["file_stem"]
    profile["data_dir"] = data_dir
    profile["file_stem"] = file_stem
    profile["rollover_map"] = data_dir / "rollover_map.parquet"
    if template_key == "rb":
        profile.update(TQ_LEAN_RB_OVERRIDES)
    profile.update(TQ_SYMBOL_PARAM_OVERRIDES.get(key, {}))
    profile.setdefault("symbol_adaptive_enabled", True)
    apply_symbol_adaptive(profile)
    return profile


def resolve_tq_cbc_paths(profile: dict) -> tuple[Path, str]:
    """从 profile 取 CbC 数据目录与分月 file_stem。"""
    if "data_dir" in profile and "file_stem" in profile:
        return Path(profile["data_dir"]), profile["file_stem"]
    raise KeyError("profile 缺少 data_dir / file_stem")
