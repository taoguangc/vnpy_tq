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
}

LEAN_PROFILE_KEYS: tuple[str, ...] = (
    "rb_min_atr",
    "ttr_rb_min_atr",
    "risk_capital",
    "risk_pct_per_trade",
    "max_position",
    "use_compound_capital",
    "dual_core_enabled",
    "vwap_regime_lookback",
    "vwap_chop_min_crosses",
    "vwap_slope_thresh_ticks",
    "vwap_trend_deadband_ticks",
    "vwap_fade_max_atr",
    "vsa_enabled",
    "vsa_volume_window",
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
)

TQ_LEAN_DEFAULT_MODE = "cbc"
TQ_ROLLOVER_SWITCH = "21:00"

# 基准（CbC + rollover_map，2023-05-17~2026-05-16 含成本）:
#   54RT/38.9%WR/-43,543/Sharpe-0.45/PF0.75/MDD-23.8%
TQ_CBC_BASELINE_RB: dict[str, float | int] = {
    "rt": 54, "wr": 38.9, "pnl": -43_543, "sharpe": -0.45, "pf": 0.75,
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
