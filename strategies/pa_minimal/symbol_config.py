# -*- coding: utf-8 -*-
"""pa_minimal 品种配置：MINIMAL_BASE + 合约规格。"""
from __future__ import annotations

from pathlib import Path

from strategies.pa_cta.symbol_config import (
    TQ_SYMBOL_ENGINE,
    TQ_SYMBOL_PARAM_OVERRIDES,
    apply_symbol_adaptive,
    resolve_tq_cbc_paths,
)

# M0-BASE：生产式背景，但 AFF Router 关（跨品种不稳定）
MINIMAL_BASE_PROFILE: dict = {
    "risk_capital": 10_000.0,
    "risk_pct_per_trade": 0.05,
    "max_position": 50,
    "rb_min_atr": 7.0,
    "ttr_rb_min_atr": 5.0,
    "use_compound_capital": False,
    "dual_core_enabled": True,
    "dual_core_soft_enabled": False,
    "vsa_enabled": True,
    "vsa_session_relative_enabled": False,
    "vsa_session_lookback_days": 15,
    "vsa_session_min_samples": 8,
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
    "aff_archetype_adaptive_enabled": False,
    "symbol_adaptive_enabled": True,
    "opp13_vol_filter_enabled": False,
    "ema_pullback_enabled": False,
    "climax_rev_enabled": False,
    "opening_drive_enabled": False,
    "opening_rev_enabled": False,
    "two_bar_rev_enabled": True,
    "overshoot_fail_enabled": False,
    "day_boundary_enabled": False,
    "wedge_enabled": False,
    "disabled_setups": "",
    "exit_family_v3_enabled": False,
    "candidate_ledger_enabled": True,
    "alpha_shadow_mode": False,
    "shadow_ledger_enabled": False,
    "context_mode": "brooks",
    "dryscan_compare_enabled": False,
    "context_layers_enabled": True,
    "context_layer_fast_bars": 10,
    "context_layer_slow_bars": 30,
    "context_layer_gate_enabled": False,
}

# M0-NULL：背景门禁全关，测裸信号下限
MINIMAL_NULL_OVERRIDES: dict = {
    "dual_core_enabled": False,
    "vsa_enabled": False,
    "late_phase_gate_enabled": False,
    "aff_gate_enabled": False,
    "tf_arm_gate_enabled": False,
    "setup_risk_mult_enabled": False,
    "symbol_adaptive_enabled": False,
    # 放宽 ATR 比率门：用极宽区间近似关闭
    "atr_regime_min": 0.0,
    "atr_regime_max": 99.0,
}

MINIMAL_PROFILE_KEYS: tuple[str, ...] = tuple(MINIMAL_BASE_PROFILE.keys()) + (
    "atr_regime_min",
    "atr_regime_max",
    "tf_arm_gate_enabled",
    "alt_r2_trend_min",
    "alt_chop_trend_max",
    "alt_chop_range_min",
    "alpha_shadow_mode",
)


def resolve_minimal_profile(symbol: str, root: Path) -> dict:
    key = symbol.lower()
    if key not in TQ_SYMBOL_ENGINE:
        raise ValueError(f"未知品种 {symbol}")
    profile = MINIMAL_BASE_PROFILE.copy()
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
    profile.setdefault("symbol_adaptive_enabled", True)
    apply_symbol_adaptive(profile)
    return profile


def build_minimal_setting(profile: dict, *, capital: float = 200_000.0) -> dict:
    setting = {
        "capital": capital,
        "contract_size": profile["size"],
        "rb_min_atr": profile.get("rb_min_atr", 7.0),
        "ttr_rb_min_atr": profile.get("ttr_rb_min_atr", 5.0),
        "risk_capital": profile.get("risk_capital", 10_000.0),
        "risk_pct_per_trade": profile.get("risk_pct_per_trade", 0.05),
        "max_position": profile.get("max_position", 50),
        "use_compound_capital": profile.get("use_compound_capital", False),
    }
    for key in MINIMAL_PROFILE_KEYS:
        if key in profile:
            setting[key] = profile[key]
    return setting
