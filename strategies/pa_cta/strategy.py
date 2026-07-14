# -*- coding: utf-8 -*-
"""
BrooksPaCtaStrategy — Al Brooks 价格行为（PA）深度精简版。

基于 pa_strategy.py v0.9.75 的 OPP 绩效统计精简而来：仅保留 rb888 3 年回测中
净盈利最高的 Top 8 OPP，删除全部 Mixin、诊断/审计代码与低盈利 OPP。
VWAP Dual Core 门禁 + Brooks 恒定风险金定仓 + MM/Chandelier/Breakeven 出场均保留。

保留 OPP（实现见 strategies/pa_cta/opp/）：
  OPP16 两棒反转 / OPP02 EMA 回调 / OPP13 日边界反转 / OPP12 超调衰竭 /
  OPP08 强突破 / OPP19 开幕式 / OPP15 楔形 / OPP17 高潮反转
"""
from __future__ import annotations

import sys
from datetime import datetime, time
from pathlib import Path

if __package__ in (None, ""):
    _repo = Path(__file__).resolve().parents[2]
    if str(_repo) not in sys.path:
        sys.path.insert(0, str(_repo))

import numpy as np
import talib
from vnpy.trader.constant import Direction, Offset
from vnpy_ctastrategy import (
    ArrayManager,
    BarData,
    BarGenerator,
    CtaTemplate,
    OrderData,
    TradeData,
)

try:
    from .aff_gate import compute_aff_snapshot
    from .aff_router import classify_aff_archetype, setup_allowed_for_archetype
    from .symbol_adaptive import parse_prefix_list, runtime_liquidity_risk_mult, static_liquidity_risk_mult
    from .regime_gate import compute_chop_index, compute_trend_r2
    from .context_layers import (
        ContextLayerSnapshot,
        compute_context_layers,
        empty_snapshot,
        layer_gate_blocks,
    )
    from .bar_patterns import (
        BarMetrics,
        PatternThresholds,
        classify_bar_shape,
        is_bear_reversal as bp_is_bear_reversal,
        is_boundary_bear_reversal,
        is_boundary_bull_reversal,
        is_bull_reversal as bp_is_bull_reversal,
        is_outside_outside,
        is_strong_bar as bp_is_strong_bar,
    )
    from .opp_tf import is_opposite_direction, should_upgrade_arm
    from .vsa import VsaFilterMixin
    from .opp import OppMixins
    from .shadow_ledger import (
        ShadowLedger,
        build_candidate_from_strategy,
        evaluate_opp15_direct_gates,
        evaluate_production_gates,
    )
    from .shadow_dry_scan import collect_production_matches
    from .exit_families import ExitFamilyConfig, family_for_setup
    from .setup_shrinkage import lookup_shrinkage_mult, parse_shrinkage_overrides
except (ModuleNotFoundError, ImportError):
    from strategies.pa_cta.aff_gate import compute_aff_snapshot
    from strategies.pa_cta.aff_router import classify_aff_archetype, setup_allowed_for_archetype
    from strategies.pa_cta.symbol_adaptive import (
        parse_prefix_list, runtime_liquidity_risk_mult, static_liquidity_risk_mult,
    )
    from strategies.pa_cta.regime_gate import compute_chop_index, compute_trend_r2
    from strategies.pa_cta.context_layers import (
        ContextLayerSnapshot,
        compute_context_layers,
        empty_snapshot,
        layer_gate_blocks,
    )
    from strategies.pa_cta.bar_patterns import (
        BarMetrics,
        PatternThresholds,
        classify_bar_shape,
        is_bear_reversal as bp_is_bear_reversal,
        is_boundary_bear_reversal,
        is_boundary_bull_reversal,
        is_bull_reversal as bp_is_bull_reversal,
        is_outside_outside,
        is_strong_bar as bp_is_strong_bar,
    )
    from strategies.pa_cta.opp_tf import is_opposite_direction, should_upgrade_arm
    from strategies.pa_cta.vsa import VsaFilterMixin
    from strategies.pa_cta.opp import OppMixins
    from strategies.pa_cta.shadow_ledger import (
        ShadowLedger,
        build_candidate_from_strategy,
        evaluate_opp15_direct_gates,
        evaluate_production_gates,
    )
    from strategies.pa_cta.shadow_dry_scan import collect_production_matches
    from strategies.pa_cta.exit_families import ExitFamilyConfig, family_for_setup
    from strategies.pa_cta.setup_shrinkage import lookup_shrinkage_mult, parse_shrinkage_overrides


# ── 入场 Lane 字典（双芯矩阵用）──
_ENTRY_LANE_MAP: dict[str, str] = {
    "OPP12_": "REVERSAL", "OPP13_": "REVERSAL", "OPP15_": "REVERSAL",
    "OPP16_": "REVERSAL", "OPP17_": "REVERSAL",
    "OPP02_EMA_": "TREND", "OPP08_": "TREND", "OPP19_": "TREND",
}
_BREAKEVEN_FAST_SETUPS = ("OPP08_", "OPP15_", "OPP19_")

# 实验1：rb888 三年 setup 毛利/笔粗分档 → 定仓风险乘子（待 walk-forward 验证）
_SETUP_RISK_MULT: dict[str, float] = {
    "OPP08_5M_STRONG_BREAKOUT_LONG": 1.30,
    "OPP08_5M_STRONG_BREAKOUT_SHORT": 1.30,
    "OPP16_5M_TWO_BAR_REV_LONG": 1.25,
    "OPP16_5M_TWO_BAR_REV_SHORT": 1.30,
    "OPP02_5M_EMA_PULLBACK_LONG": 1.00,
    "OPP02_5M_EMA_PULLBACK_SHORT": 1.30,
    "OPP13_5M_RANGE_FAIL_HIGH": 1.25,
    "OPP13_5M_RANGE_FAIL_LOW": 1.00,
    "OPP15_5M_WEDGE_B_PRIME": 1.20,
    "OPP15_5M_WEDGE_B_PRIME_LONG": 1.00,
    "OPP15_5M_WEDGE_REVERSAL": 1.15,
    "OPP12_5M_OVERSHOOT_FAIL_SHORT": 1.10,
    "OPP12_5M_OVERSHOOT_FAIL_LONG": 0.50,
    "OPP17_5M_CLIMAX_REV_LONG": 1.00,
    "OPP17_5M_CLIMAX_REV_SHORT": 1.00,
    "OPP19_5M_OD_BREAKOUT_LONG": 1.00,
    "OPP19_5M_OD_BREAKOUT_SHORT": 0.50,
    "OPP19_5M_OD_REV_LONG": 0.50,
    "OPP19_5M_OD_REV_SHORT": 0.50,
}


class BrooksPaCtaStrategy(OppMixins, VsaFilterMixin, CtaTemplate):
    """Al Brooks PA 极简版：5m 信号 + 15m Context + VWAP 双芯门禁 + VSA arm 滤网。"""

    author = "Tao"
    version = "1.0_LEAN"

    signal_bar_window = 5
    context_bar_window = 3
    # 资金/仓位
    risk_capital = 5_000.0
    risk_pct_per_trade = 0.025
    use_compound_capital = False
    contract_size = 10
    max_position = 50
    capital = 200_000.0
    # Setup 风险乘子（实验1：按 OPP 历史表现缩放 risk_money，总 cap 仍受 risk_capital 约束）
    setup_risk_mult_enabled = False
    setup_risk_mult_default = 1.0
    late_phase_gate_enabled = False
    # AFF 规则版门禁（实验 C：alpha_strength 过滤 + 定仓乘子）
    aff_gate_enabled = False
    aff_gate_mode = "sizing"  # sizing=仅缩放定仓; filter=低于阈值拒单
    aff_alpha_reject_threshold = 0.25
    aff_alpha_high_threshold = 0.50
    aff_risk_mult_low = 0.7
    aff_risk_mult_high = 1.2
    # EXP-013：AFF Archetype Router（默认关；开启后按 15m 分档允许 OPP 族）
    aff_archetype_router_enabled = False
    aff_archetype_alpha_low = 0.25
    aff_archetype_compression_min = 0.6
    aff_archetype_expansion_env_min = 0.75
    aff_archetype_exhaustion_env_max = 0.25
    aff_archetype_use_lane_matrix = True  # v1：TREND/REVERSAL 分轨；False=v0 前缀表
    aff_archetype_adaptive_enabled = True  # v2：always_in 顺势 + EXPANSION OPP16 多收紧
    aff_archetype_minimal_enabled = False  # 仅 LOW_ALPHA 拒 TREND（Setup AFF 等价层）
    aff_archetype_trend_bypass_prefixes = "OPP08_"  # v2 context 豁免前缀（逗号分隔）
    # 品种自适应（流动性分档；resolve 时按 symbol_vol_baseline_1m 注入）
    symbol_adaptive_enabled = True
    symbol_vol_baseline_1m = 0.0  # 0=未配置，不启用分档
    symbol_liquidity_ref_1m = 2861.0
    symbol_liquidity_low_ratio = 0.45
    symbol_liquidity_risk_floor = 0.55
    symbol_liquidity_runtime_enabled = True  # 15m 成交量动态缩放定仓
    symbol_liquidity_tier = ""  # resolve 注入：LOW / MID / HIGH
    atr_window = 14
    ema_window = 20
    rb_min_atr = 7.0
    atr_regime_min = 0.60
    atr_regime_max = 0.80
    ttr_rb_min_atr = 5.0
    atr_percentile_window = 100
    # Stop buffer
    day_boundary_tolerance = 5.0
    stop_buffer_min = 3.0
    stop_buffer_atr_mult = 0.3
    stop_buffer_atr_hi_pct = 80
    stop_buffer_atr_hi_mult = 1.3
    stop_buffer_atr_lo_pct = 20
    stop_buffer_atr_lo_mult = 0.7
    breakeven_trigger_atr_mult_slow = 2.0
    breakeven_trigger_atr_mult_fast = 1.0
    max_risk_multiplier = 2.0
    entry_risk_fuse_atr_mult = 2.5
    # Bar 质量
    strong_bar_atr_mult = 1.0
    strong_bar_body_ratio = 0.6
    bar_trend_body_ratio = 0.60
    bar_spike_tail_body_ratio = 1.5
    bar_outside_prev_ratio = 1.10
    # Context
    strong_context_trend_bar_ratio = 0.50
    strong_context_min_trend_bars = 6
    strong_context_avg_body_ratio = 0.45
    alwaysin_min_bars = 4
    # 反转棒
    reversal_shadow_min_ratio = 0.40
    reversal_close_quarter = 0.25
    reversal_min_body_ratio = 0.15
    boundary_reversal_shadow_ratio = 0.45
    boundary_reversal_close_ratio = 0.30
    long_climax_atr_mult = 2.5
    # OPP12 超调
    overshoot_atr_mult = 1.2
    overshoot_max_atr_mult = 2.5
    pd_level_block_atr_mult = 0.2
    # OPP13 日边界
    day_low_second_test_ticks = 2
    day_high_second_test_ticks = 3
    day_high_second_test_max_bars = 12
    day_high_lh_max_ticks = 10
    opp13_vol_filter_enabled = False
    opp13_min_volume_pct = 45.0
    opp13_climax_volume_pct = 65.0
    opp13_short_max_close_pos = 0.50
    opp13_long_min_close_pos = 0.50
    # OPP16 两棒反转
    two_bar_rev_enabled = True
    two_bar_rev_body_ratio = 0.55
    two_bar_rev_context = "WIDE_RANGE,BULL_CHANNEL,BEAR_CHANNEL"
    # 硬禁 setup 前缀列表（逗号分隔，EXP-012 Core Purification 等）
    disabled_setups = ""
    # OPP02 EMA Pullback
    ema_pullback_enabled = True
    ema_pullback_touch_atr = 1.0
    ema_pullback_min_body_ratio = 0.35
    # OPP02 专属 AFF alpha 门禁（H5，默认关；仅对 OPP02 拒单，不影响其余 setup 与全局 sizing）
    opp02_aff_gate_enabled = False
    opp02_aff_alpha_min = 0.25
    # OPP02 15m R² 趋势门禁（EXP-007 候选，替代 Setup AFF；默认关）
    opp02_r2_gate_enabled = False
    opp02_r2_min = 0.30
    # OPP17 Climax Reversal
    climax_rev_enabled = True
    climax_rev_range_atr = 2.5
    climax_rev_context = "WIDE_RANGE,BULL_CHANNEL,BEAR_CHANNEL,STRONG_BULL,STRONG_BEAR"
    # OPP19 Opening Drive
    opening_drive_enabled = True
    opening_drive_bars = 6
    opening_drive_min_body = 0.50
    opening_drive_range_atr_min = 0.2
    # OPP19 突破专属 AFF alpha 门禁（H6，默认关；趋势延续族，仅门 breakout 不门 OD_REV）
    opp19_breakout_aff_gate_enabled = False
    opp19_breakout_aff_alpha_min = 0.25
    # OPP19 突破 15m R² 趋势门禁（EXP-007 候选，默认关）
    opp19_breakout_r2_gate_enabled = False
    opp19_breakout_r2_min = 0.30
    # R² 门禁可选 CHOP 辅判：CHOP > chop_max 视为震荡拒单
    trend_gate_use_chop = False
    trend_gate_r2_period = 20
    trend_gate_chop_period = 14
    trend_gate_chop_max = 61.8
    opening_rev_enabled = True
    opening_rev_body_ratio = 0.45
    # OPP19 开盘反转门禁（OD_REV 专用；突破 breakout 仍走 AFF 门禁）
    opp19_rev_gate_enabled = False
    opp19_rev_always_in_gate = True
    opp19_rev_block_strong_counter = True
    opp19_rev_min_bar1_range_atr = 0.30
    opp19_rev_max_bar1_range_atr = 2.50
    opp19_rev_contexts = "WIDE_RANGE,TIGHT_RANGE,BULL_CHANNEL,BEAR_CHANNEL,STRONG_BULL,STRONG_BEAR"
    opp19_rev_morning_cutoff_minute = 25
    opp19_rev_night_cutoff_minute = 25
    opp19_rev_arm_mode = "PENDING_CONFIRM"  # FAST_TRACK | PENDING_CONFIRM
    # OPP15 Wedge
    wedge_alpha_threshold = 0.85
    wedge_mtf_alpha_threshold = 0.80
    wedge_n_min_5m = 3
    wedge_n_min_15m = 2
    wedge_session_start_hour = 14
    wedge_session_start_minute = 0
    wedge_require_mtf = True
    wedge_b_prime_alpha = 0.50
    wedge_arm_trigger_max_bars = 4
    # 出场
    trailing_active_multiplier = 1.5
    chandelier_multiplier = 2.5
    follow_through_bars = 2
    max_daily_trades = 3
    # Measured Move
    mm_atr_mult = 2.0
    mm_half_close_enabled = True
    mm_runner_enabled = True
    # Fast Lane 持仓期追踪（关则走慢车道 PP/Chandelier；入场 arm 不变）
    fast_lane_trail_enabled = True
    # Phase-3：两族出场（默认关；开则按 exit_families 路由，不改入场集合）
    exit_family_v3_enabled = False
    # Phase-4：setup 软收缩定仓（默认关；替代小样本 disabled_setups 硬禁）
    setup_shrinkage_enabled = False
    setup_shrinkage_overrides = ""
    setup_shrinkage_hard_disable = False
    # Phase-2：production OPP 影子账本（回测研究用，不影响下单）
    shadow_ledger_enabled = False
    # 趋势寿命
    trend_late_counter_threshold = 3
    trend_late_atr_shrink_ratio = 0.7
    # VWAP Dual Core（soft：不拒单，用偏离度降仓/缩目标；hard：旧硬门禁）
    dual_core_enabled = True
    dual_core_soft_enabled = False  # 默认 hard；rb 对照 NEW 更差，见 EXP-GATE-SOFT-BT
    vwap_regime_lookback = 30
    vwap_chop_min_crosses = 4
    vwap_slope_thresh_ticks = 2
    vwap_trend_deadband_ticks = 4
    vwap_fade_max_atr = 1.2
    dual_core_exhaustion_atr = 1.0       # OPP16 充分偏离（ATR 倍数）
    dual_core_exhaustion_min_atr = 0.4  # OPP16 最低偏离门槛
    dual_core_soft_min_size_mult = 0.25
    dual_core_soft_min_target_mult = 0.40
    dual_core_opp16_soft_enabled = True   # soft 模式下 OPP16 是否参与（False=仅 OPP08）
    dual_core_opp16_wrong_side_size_mult = 0.40
    dual_core_opp16_wrong_side_target_mult = 0.60
    dual_core_opp16_shallow_size_mult = 0.55
    dual_core_opp16_shallow_target_mult = 0.75
    dual_core_opp16_favor_size_floor = 0.85   # 有利侧衰竭区 size 下限
    dual_core_opp16_favor_target_floor = 0.90
    dual_core_opp16_favor_skip_extra = True   # 有利侧跳过 CHOP/强趋势附加罚
    dual_core_opp16_soft_min_size_mult = 0.70
    dual_core_opp16_soft_min_target_mult = 0.55
    # 15m 快/慢连续背景层（默认只计算；gate 默认关，不改变历史入场集合）
    context_layers_enabled = True
    context_layer_fast_bars = 10
    context_layer_slow_bars = 30  # 建议 20～40
    context_layer_gate_enabled = False
    context_layer_opp08_min_fit = 0.45
    context_layer_opp16_min_fit = 0.40
    # VSA 开仓熔断（与 pa 旗舰同源 VsaFilterMixin）
    vsa_enabled = True
    vsa_volume_window = 40
    vsa_session_relative_enabled = False  # 默认混窗；同时段版见 EXP-GATE-SOFT-BT
    vsa_session_lookback_days = 15
    vsa_session_min_samples = 8
    vsa_low_volume_pct = 35.0
    vsa_high_volume_pct = 70.0
    vsa_spread_atr_mult = 0.25
    vsa_weak_close_ratio = 0.40
    vsa_stopping_close_ratio = 0.60
    vsa_block_count = 0
    vsa_persistence_enabled = False
    vsa_persistence_bars = 4
    vsa_persistence_displacement_ticks = 4
    vsa_persistence_displacement_atr = 0.5
    vsa_persistence_opposite_tolerance = 1
    vsa_persistence_exempt_count = 0
    # 多周期 arm 优先级 / 反向排队平仓（与 pa 旗舰同源 opp_tf）
    tf_counter_exit_mode = "ON_1M_CLOSE"
    tf_arm_gate_enabled = True

    # ── 运行时状态（类属性默认）──
    market_context = "TRADING_RANGE"
    always_in = "NONE"
    active_setup_name = ""
    daily_trade_count = 0
    last_bar_day = 0
    day_high = 0.0
    day_low = 0.0
    vwap = 0.0
    vwap_regime = "UNINIT"
    vwap_slope_ticks = 0.0
    vwap_distance_atr = 0.0
    vwap_cross_count = 0
    h_counter = 0
    l_counter = 0
    h1_signal_low = 0.0
    h1_low_broken = False
    l1_signal_high = 0.0
    l1_high_broken = False
    last_context = ""
    day_high_test_state = "IDLE"
    day_high_test_bar_count = 0
    first_test_high = 0.0
    stop_price = 0.0
    stop_source = ""
    pending_exit_order: dict | None = None
    remaining_position = 0
    entry_price = 0.0
    profit_protect_active = False
    profit_protect_enabled = True
    eod_flat_enabled = True
    breakeven_locked = False
    highest_high_since_entry = 0.0
    lowest_low_since_entry = 0.0
    bars_since_entry = 0
    signal_bar_invalid_line = 0.0
    entry_window_open = True
    mm_target_price = 0.0
    mm_half_closed = False
    mm_entry_volume = 0
    mm_target_scaled = False
    mm_runner_active = False
    last_leg1_amplitude = 0.0
    mm_swing_low = 0.0
    mm_swing_high = 0.0
    last_exit_reason = ""
    trend_direction = 0
    trend_age_bars = 0
    trend_pullback_count = 0
    trend_phase = ""
    trend_entry_atr = 0.0
    prev_bar_shape = ""
    machine_state = "IDLE"
    pending_dir = 0
    trigger_level = 0.0
    entry_lane = ""
    active_entry_lane = ""
    active_exit_family = ""
    pd_open = 0.0
    pd_close = 0.0
    mtf_wedge_exhaustion_zone = False
    mtf_bull_wedge_exhaustion_zone = False
    wedge_setup_active = False
    wedge_confirmed_p3_high = 0.0
    wedge_trigger_line = 0.0
    wedge_arm_time: datetime | None = None
    wedge_current_alpha = 0.0
    wedge_p3_body_floor = 0.0

    parameters = [
        "signal_bar_window", "context_bar_window", "risk_capital",
        "risk_pct_per_trade", "use_compound_capital", "contract_size",
        "max_position", "capital", "setup_risk_mult_enabled",
        "setup_risk_mult_default", "late_phase_gate_enabled",
        "aff_gate_enabled", "aff_gate_mode", "aff_alpha_reject_threshold", "aff_alpha_high_threshold",
        "aff_risk_mult_low", "aff_risk_mult_high",
        "aff_archetype_router_enabled", "aff_archetype_alpha_low",
        "aff_archetype_compression_min", "aff_archetype_expansion_env_min",
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
        "opp02_aff_gate_enabled", "opp02_aff_alpha_min",
        "opp02_r2_gate_enabled", "opp02_r2_min",
        "atr_window", "ema_window", "rb_min_atr",
        "atr_regime_min", "atr_regime_max", "ttr_rb_min_atr",
        "atr_percentile_window", "day_boundary_tolerance", "stop_buffer_min",
        "stop_buffer_atr_mult", "stop_buffer_atr_hi_pct", "stop_buffer_atr_hi_mult",
        "stop_buffer_atr_lo_pct", "stop_buffer_atr_lo_mult",
        "breakeven_trigger_atr_mult_slow", "breakeven_trigger_atr_mult_fast",
        "max_risk_multiplier", "entry_risk_fuse_atr_mult", "strong_bar_atr_mult",
        "strong_bar_body_ratio", "bar_trend_body_ratio", "bar_spike_tail_body_ratio",
        "bar_outside_prev_ratio", "strong_context_trend_bar_ratio",
        "strong_context_min_trend_bars", "strong_context_avg_body_ratio",
        "alwaysin_min_bars", "reversal_shadow_min_ratio", "reversal_close_quarter",
        "reversal_min_body_ratio", "boundary_reversal_shadow_ratio",
        "boundary_reversal_close_ratio", "long_climax_atr_mult",
        "overshoot_atr_mult", "overshoot_max_atr_mult", "pd_level_block_atr_mult",
        "day_low_second_test_ticks", "day_high_second_test_ticks",
        "day_high_second_test_max_bars", "day_high_lh_max_ticks",
        "opp13_vol_filter_enabled", "opp13_min_volume_pct",
        "opp13_climax_volume_pct", "opp13_short_max_close_pos",
        "opp13_long_min_close_pos",
        "two_bar_rev_enabled", "two_bar_rev_body_ratio", "two_bar_rev_context",
        "disabled_setups",
        "ema_pullback_enabled", "ema_pullback_touch_atr",
        "ema_pullback_min_body_ratio", "climax_rev_enabled",
        "climax_rev_range_atr", "climax_rev_context", "opening_drive_enabled",
        "opening_drive_bars", "opening_drive_min_body",
        "opening_drive_range_atr_min",
        "opp19_breakout_aff_gate_enabled", "opp19_breakout_aff_alpha_min",
        "opp19_breakout_r2_gate_enabled", "opp19_breakout_r2_min",
        "trend_gate_use_chop", "trend_gate_r2_period", "trend_gate_chop_period",
        "trend_gate_chop_max",
        "opening_rev_enabled",
        "opening_rev_body_ratio",
        "opp19_rev_gate_enabled",
        "opp19_rev_always_in_gate",
        "opp19_rev_block_strong_counter",
        "opp19_rev_min_bar1_range_atr",
        "opp19_rev_max_bar1_range_atr",
        "opp19_rev_contexts",
        "opp19_rev_morning_cutoff_minute",
        "opp19_rev_night_cutoff_minute",
        "opp19_rev_arm_mode",
        "wedge_alpha_threshold",
        "wedge_mtf_alpha_threshold", "wedge_n_min_5m", "wedge_n_min_15m",
        "wedge_session_start_hour", "wedge_session_start_minute",
        "wedge_require_mtf", "wedge_b_prime_alpha", "wedge_arm_trigger_max_bars",
        "trailing_active_multiplier", "chandelier_multiplier",
        "profit_protect_enabled",
        "eod_flat_enabled",
        "follow_through_bars", "max_daily_trades", "mm_atr_mult",
        "mm_half_close_enabled", "mm_runner_enabled",
        "fast_lane_trail_enabled",
        "exit_family_v3_enabled",
        "setup_shrinkage_enabled",
        "setup_shrinkage_overrides",
        "setup_shrinkage_hard_disable",
        "shadow_ledger_enabled",
        "trend_late_counter_threshold", "trend_late_atr_shrink_ratio",
        "dual_core_enabled", "dual_core_soft_enabled",
        "vwap_regime_lookback", "vwap_chop_min_crosses",
        "vwap_slope_thresh_ticks", "vwap_trend_deadband_ticks", "vwap_fade_max_atr",
        "dual_core_exhaustion_atr", "dual_core_exhaustion_min_atr",
        "dual_core_soft_min_size_mult", "dual_core_soft_min_target_mult",
        "dual_core_opp16_soft_enabled",
        "dual_core_opp16_wrong_side_size_mult",
        "dual_core_opp16_wrong_side_target_mult",
        "dual_core_opp16_shallow_size_mult",
        "dual_core_opp16_shallow_target_mult",
        "dual_core_opp16_favor_size_floor",
        "dual_core_opp16_favor_target_floor",
        "dual_core_opp16_favor_skip_extra",
        "dual_core_opp16_soft_min_size_mult",
        "dual_core_opp16_soft_min_target_mult",
        "context_layers_enabled", "context_layer_fast_bars", "context_layer_slow_bars",
        "context_layer_gate_enabled", "context_layer_opp08_min_fit",
        "context_layer_opp16_min_fit",
        "vsa_enabled", "vsa_volume_window",
        "vsa_session_relative_enabled", "vsa_session_lookback_days",
        "vsa_session_min_samples",
        "vsa_low_volume_pct",
        "vsa_high_volume_pct", "vsa_spread_atr_mult", "vsa_weak_close_ratio",
        "vsa_stopping_close_ratio", "vsa_persistence_enabled",
        "vsa_persistence_bars", "vsa_persistence_displacement_ticks",
        "vsa_persistence_displacement_atr", "vsa_persistence_opposite_tolerance",
        "tf_counter_exit_mode", "tf_arm_gate_enabled",
    ]
    variables = [
        "market_context", "always_in", "active_setup_name", "daily_trade_count",
        "day_high", "day_low", "vwap", "vwap_regime", "machine_state", "pos",
        "vsa_block_count", "vsa_persistence_exempt_count",
        "ctx_trend_quality", "ctx_opp08_fit", "ctx_opp16_fit",
    ]

    # ──────────────────────────────────────────────────────────────────────
    # 生命周期
    # ──────────────────────────────────────────────────────────────────────
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.am_5min = ArrayManager(80)
        self.am_15min = ArrayManager(80)
        self.bg_5 = BarGenerator(self.on_bar, self.signal_bar_window, self.on_5min_bar)
        self.bg_15 = BarGenerator(self.on_5min_bar, self.context_bar_window, self.on_15min_bar)
        self._prev_5min_bar: BarData | None = None
        self._reset_machine()
        self._reset_day_high_test()
        self._reset_wedge_setup()
        self._reset_opening_drive()
        self._last_5min_date = None
        self._cur_day_first_open = 0.0
        self._cur_day_last_close = 0.0
        self._vwap_cum_pv = 0.0
        self._vwap_cum_vol = 0.0
        self._vwap_close_side = 0
        self._vwap_samples: list[float] = []
        self._reset_vwap()
        self._last_1m_close = 0.0
        self._wedge_direction = 0
        self._dual_core_block_count = 0
        self._dual_core_soft_reduce_count = 0
        self._dual_core_size_mult = 1.0
        self._dual_core_target_mult = 1.0
        self._vsa_slot_hist = None
        self._late_phase_block_count = 0
        self._aff_block_count = 0
        self._aff_alpha_strength = 0.0
        self._aff_compression_score = 0.0
        self._aff_env_score = 0.0
        self._aff_er = 0.0
        self._aff_archetype = "NEUTRAL"
        self._aff_archetype_block_count = 0
        self._symbol_liquidity_static_mult = 1.0
        self._symbol_liquidity_runtime_mult = 1.0
        self._trend_bypass_prefixes: tuple[str, ...] = ("OPP08_",)
        if (self.symbol_adaptive_enabled
                and self.symbol_vol_baseline_1m > 0
                and self.symbol_liquidity_tier == "LOW"):
            ratio = self.symbol_vol_baseline_1m / max(self.symbol_liquidity_ref_1m, 1.0)
            self._symbol_liquidity_static_mult = static_liquidity_risk_mult(
                ratio, floor=self.symbol_liquidity_risk_floor,
            )
        self._trend_bypass_prefixes = parse_prefix_list(
            self.aff_archetype_trend_bypass_prefixes or "OPP08_"
        )
        self._trend_r2 = 0.0
        self._trend_chop = 100.0
        self._vsa_block_count = 0
        self.vsa_block_count = 0
        self._vsa_persistence_exempt_count = 0
        self.vsa_persistence_exempt_count = 0
        self._opp13_vol_block_count = 0
        self._initial_capital = max(float(self.capital), 1.0)
        self._realized_pnl = 0.0
        self._current_atr_ratio = 0.0
        self._pattern_th = self._build_pattern_thresholds()
        # OPP19 Opening Drive state
        self._od_state = "IDLE"
        self._od_high = 0.0
        self._od_low = 0.0
        self._od_bars_collected = 0
        self._od_session_date = None
        self._od_bar1_shape = ""
        self._od_bar1_mid = 0.0
        self._od_bar1_range = 0.0
        self._clear_tf_counter_exit()
        self._reset_exit_state()
        self._shadow_ledger = None
        self._current_5min_bar: BarData | None = None
        self._shadow_bar_first_attempt = ""
        if self.shadow_ledger_enabled:
            sym = self.vt_symbol.split(".")[0] if self.vt_symbol else "unknown"
            self._shadow_ledger = ShadowLedger(sym)

    def on_init(self) -> None:
        self.write_log("Brooks PA CTA 策略初始化，预热历史数据...")
        self.load_bar(10)

    def on_start(self) -> None:
        self.daily_trade_count = 0
        self._reset_machine()
        self._reset_day_high_test()
        self._reset_wedge_setup()
        self._reset_opening_drive()
        self._reset_vwap()
        self.market_context = "TRADING_RANGE"
        self.always_in = "NONE"
        self._context_layers: ContextLayerSnapshot = empty_snapshot(
            fast_n=int(self.context_layer_fast_bars),
            slow_n=int(self.context_layer_slow_bars),
        )
        self.ctx_trend_quality = 0.0
        self.ctx_opp08_fit = 0.5
        self.ctx_opp16_fit = 0.5
        self._context_layer_block_count = 0
        self.h_counter = 0
        self.l_counter = 0
        self.h1_signal_low = 0.0
        self.h1_low_broken = False
        self.l1_signal_high = 0.0
        self.l1_high_broken = False
        self.mm_target_price = 0.0
        self.mm_half_closed = False
        self.mm_entry_volume = 0
        self.mm_target_scaled = False
        self.mm_runner_active = False
        self.mm_swing_low = 0.0
        self.mm_swing_high = 0.0
        self.last_leg1_amplitude = 0.0
        self.trend_direction = 0
        self.trend_age_bars = 0
        self.trend_pullback_count = 0
        self.trend_phase = ""
        self.trend_entry_atr = 0.0
        self.prev_bar_shape = ""
        self.last_context = ""
        self.active_entry_lane = ""
        self._reset_exit_state()
        self.pd_open = 0.0
        self.pd_close = 0.0
        self._last_5min_date = None
        self._cur_day_first_open = 0.0
        self._cur_day_last_close = 0.0
        self._initial_capital = max(float(self.capital), 1.0)
        self._realized_pnl = 0.0
        self._setup_pnl: dict[str, float] = {}
        self._setup_trades: dict[str, int] = {}
        self._entry_snapshot: dict | None = None
        self._trade_log: list[dict] = []
        self.mtf_wedge_exhaustion_zone = False
        self.mtf_bull_wedge_exhaustion_zone = False
        self._vsa_block_count = 0
        self.vsa_block_count = 0
        self._vsa_persistence_exempt_count = 0
        self.vsa_persistence_exempt_count = 0
        self._opp13_vol_block_count = 0
        self._dual_core_block_count = 0
        self._dual_core_soft_reduce_count = 0
        self._dual_core_size_mult = 1.0
        self._dual_core_target_mult = 1.0
        self._vsa_slot_hist = None
        self._late_phase_block_count = 0
        self._aff_block_count = 0
        self._aff_alpha_strength = 0.0
        self._aff_compression_score = 0.0
        self._aff_env_score = 0.0
        self._aff_er = 0.0
        self._aff_archetype = "NEUTRAL"
        self._aff_archetype_block_count = 0
        self._trend_r2 = 0.0
        self._trend_chop = 100.0
        self._clear_tf_counter_exit()
        if self.shadow_ledger_enabled:
            sym = self.vt_symbol.split(".")[0] if self.vt_symbol else "unknown"
            self._shadow_ledger = ShadowLedger(sym)

    def on_order(self, order: OrderData) -> None:
        pass

    def on_trade(self, trade: TradeData) -> None:
        if trade.offset == Offset.OPEN:
            self.entry_price = trade.price
            self.profit_protect_active = False
            self.breakeven_locked = False
            self.highest_high_since_entry = trade.price
            self.lowest_low_since_entry = trade.price
            self.bars_since_entry = 0
            self.daily_trade_count += 1
            self._set_stop(float(self.stop_price or 0.0), "INITIAL", force_source=True)
            setup = self.active_setup_name or "UNKNOWN"
            stop_px = float(self.stop_price or 0.0)
            init_r = abs(trade.price - stop_px) * self.contract_size if stop_px > 0 else 0.0
            self._entry_snapshot = {
                "setup": setup,
                "entry_time": trade.datetime,
                "entry_price": trade.price,
                "market_context": self.market_context,
                "always_in": self.always_in,
                "direction": "多" if trade.direction == Direction.LONG else "空",
                "initial_stop_loss": stop_px,
                "initial_r_yuan": round(init_r, 2),
            }
            if self.pending_dir != 0 and self.am_5min.inited:
                atr_5 = float(self.am_5min.atr(self.atr_window))
                self.mm_target_price = self._calc_measured_move_target(
                    direction=self.pending_dir, entry_price=trade.price,
                    signal_bar=None, atr_5=atr_5,
                )
                self.mm_half_closed = False
            else:
                self.mm_target_price = 0.0
                self.mm_half_closed = False
            self.mm_entry_volume = int(trade.volume)
            self.mm_target_scaled = False
            self.mm_runner_active = False
            if not self.active_entry_lane:
                setup = self.active_setup_name or ""
                self.active_entry_lane = self._setup_entry_lane(setup)
            if getattr(self, "exit_family_v3_enabled", False):
                fam, _ = family_for_setup(self.active_setup_name or setup)
                self.active_exit_family = fam.value
            self._entry_snapshot["exit_family"] = self.active_exit_family or ""
            signed = int(trade.volume) if trade.direction == Direction.LONG else -int(trade.volume)
            self.remaining_position = signed
            self.pending_exit_order = None
            self.last_exit_reason = ""
            if self.shadow_ledger_enabled and self._shadow_ledger is not None:
                self._shadow_ledger.mark_traded(
                    self.active_setup_name or setup, trade.datetime)
        elif trade.offset in (Offset.CLOSE, Offset.CLOSETODAY):
            fill_reason = ""
            if self.pending_exit_order:
                fill_reason = str(self.pending_exit_order.get("reason") or "")
            self.pending_exit_order = None
            self.remaining_position = int(self.pos)
            if fill_reason:
                self.last_exit_reason = fill_reason
            snap = self._entry_snapshot or {}
            closing_setup = snap.get("setup") or self.active_setup_name
            if not closing_setup:
                return
            entry_px = float(snap.get("entry_price") or self.entry_price or trade.price)
            # Direction.LONG 表示买入平空（cover）；SHORT 表示卖出平多（sell）
            if trade.direction == Direction.LONG:
                pnl = (entry_px - trade.price) * trade.volume * self.contract_size
            else:
                pnl = (trade.price - entry_px) * trade.volume * self.contract_size
            self._realized_pnl += pnl
            self._setup_pnl[closing_setup] = (
                self._setup_pnl.get(closing_setup, 0.0) + pnl
            )
            self._setup_trades[closing_setup] = (
                self._setup_trades.get(closing_setup, 0) + 1
            )
            if self.pos == 0:
                if snap:
                    ep = float(snap.get("entry_price") or entry_px)
                    hi = self.highest_high_since_entry or ep
                    lo = self.lowest_low_since_entry or ep
                    if snap.get("direction") == "多":
                        mfe_ticks = (hi - ep) * self.contract_size
                        mae_ticks = (ep - lo) * self.contract_size
                    else:
                        mfe_ticks = (ep - lo) * self.contract_size
                        mae_ticks = (hi - ep) * self.contract_size
                    self._trade_log.append(
                        {
                            **snap,
                            "exit_time": trade.datetime,
                            "exit_price": trade.price,
                            "exit_reason": self.last_exit_reason or "UNKNOWN",
                            "stop_source": self.stop_source or "",
                            "volume": trade.volume,
                            "holding_minutes": round(
                                (trade.datetime - snap["entry_time"]).total_seconds() / 60.0,
                                1,
                            ),
                            "mfe_ticks": round(mfe_ticks, 2),
                            "mae_ticks": round(mae_ticks, 2),
                            "gross_pnl": round(pnl, 2),
                        }
                    )
                    self._entry_snapshot = None
                self.active_setup_name = ""
                self.active_entry_lane = ""
                self._reset_exit_state()
                self._reset_machine()

    def on_stop(self) -> None:
        if self.shadow_ledger_enabled and self._shadow_ledger is not None:
            self._shadow_export_path = getattr(self, "_shadow_export_path", None)
        self._print_vsa_funnel()
        if self.dual_core_enabled:
            soft = getattr(self, "dual_core_soft_enabled", False)
            mode = "soft(降仓/缩目标)" if soft else "hard(拒单)"
            self.write_log(
                f"Dual Core[{mode}] hard_block={self._dual_core_block_count} "
                f"soft_reduce={getattr(self, '_dual_core_soft_reduce_count', 0)}"
            )
        items = sorted(
            self._setup_pnl.items(), key=lambda x: x[1], reverse=True
        )
        if not items:
            return
        lines = ["=" * 60, "各 OPP 收益贡献（净盈亏，含滑点手续费）", "=" * 60]
        total = 0.0
        total_trades = 0
        for setup, pnl in items:
            n = self._setup_trades.get(setup, 0)
            total += pnl
            total_trades += n
            lines.append(f"  {setup:<42s} {n:>3d}笔  {pnl:>+10.0f}")
        lines.append("-" * 60)
        lines.append(f"  {'合计':<42s} {total_trades:>3d}笔  {total:>+10.0f}")
        lines.append("=" * 60)
        self.write_log("\n".join(lines))

    # ──────────────────────────────────────────────────────────────────────
    # on_bar — 1m 风控主循环
    # ──────────────────────────────────────────────────────────────────────
    def on_bar(self, bar: BarData) -> None:
        """1 分钟 Bar：时间过滤、日切重置、尾盘清仓、1m 止损/止盈。"""
        current_time = bar.datetime.time()
        in_noise = self._is_noise_window(current_time)

        if in_noise:
            if self.pos != 0:
                if self._process_tf_counter_exit(bar):
                    return
                if self._manage_stop_loss(bar):
                    return
                self._manage_mm_targets(bar)
            return

        if self._process_tf_counter_exit(bar):
            return

        if bar.datetime.day != self.last_bar_day:
            self.daily_trade_count = 0
            self._reset_machine()
            self._reset_day_high_test()
            self._reset_wedge_setup()
            self._reset_opening_drive()
            self.h_counter = 0
            self.l_counter = 0
            self.h1_signal_low = 0.0
            self.h1_low_broken = False
            self.l1_signal_high = 0.0
            self.l1_high_broken = False
            self.mm_target_price = 0.0
            self.mm_half_closed = False
            self.mm_entry_volume = 0
            self.mm_target_scaled = False
            self.mm_runner_active = False
            self.mm_swing_low = 0.0
            self.mm_swing_high = 0.0
            self.last_leg1_amplitude = 0.0
            self.prev_bar_shape = ""
            self._reset_vwap()
            self.last_bar_day = bar.datetime.day

        if current_time >= time(14, 45):
            self.entry_window_open = False
        else:
            self.entry_window_open = True

        if self.eod_flat_enabled and time(14, 55) <= current_time <= time(15, 0):
            self._reset_machine()
            if self.pos != 0:
                side_msg = "【日内清仓】收盘价平多" if self.pos > 0 else "【日内清仓】收盘价平空"
                if self._submit_exit(
                        bar.close_price,
                        abs(int(self.pos)),
                        reason="EOD_FLAT",
                        kind="EOD",
                        allow_replace=True,
                ):
                    self.write_log(side_msg)
            return

        if current_time == time(9, 6) or self.day_high <= 0:
            self.day_high = bar.high_price
            self.day_low = bar.low_price
        else:
            self.day_high = max(self.day_high, bar.high_price)
            self.day_low = min(self.day_low, bar.low_price)

        if self.pos != 0:
            if self._manage_stop_loss(bar):
                return
            self._manage_mm_targets(bar)

        self._update_vwap(bar)
        self._update_vwap_regime(bar)
        self.bg_5.update_bar(bar)

    # ──────────────────────────────────────────────────────────────────────
    # on_5min_bar — 5m 信号引擎
    # ──────────────────────────────────────────────────────────────────────
    def on_5min_bar(self, bar: BarData) -> None:
        """5 分钟核心信号引擎：ATR regime gate + Top 8 OPP 入场。"""
        self._current_5min_bar = bar
        self._shadow_bar_first_attempt = ""
        self.bg_15.update_bar(bar)
        self.am_5min.update_bar(bar)
        if not self.am_5min.inited:
            self._record_vsa_slot_volume(bar)
            self._prev_5min_bar = bar
            return

        atr_5 = float(self.am_5min.atr(self.atr_window))
        atr_15 = float(self.am_15min.atr(self.atr_window)) if self.am_15min.inited else 0.0
        if atr_15 > 0 and atr_5 > 0:
            self._current_atr_ratio = round(atr_5 / atr_15, 3)
        else:
            self._current_atr_ratio = 0.0
        allow_new_entry = (
            self._current_atr_ratio >= self.atr_regime_min
            and self._current_atr_ratio <= self.atr_regime_max
        )

        bar_m = BarMetrics.from_bar(bar)
        self.prev_bar_shape = classify_bar_shape(
            bar_m,
            BarMetrics.from_bar(self._prev_5min_bar) if self._prev_5min_bar else None,
            self._pattern_th,
        )
        self._prev_5min_bar = bar
        self._update_pd_levels(bar)
        self.cancel_all()

        ema_20 = float(self.am_5min.ema(self.ema_window))
        tick = self.get_pricetick()
        stop_buffer = self._stop_buffer(atr_5, tick)

        if self.market_context != self.last_context:
            self.h_counter = 0
            self.l_counter = 0
            self.h1_signal_low = 0.0
            self.h1_low_broken = False
            self.l1_signal_high = 0.0
            self.l1_high_broken = False
            self._reset_day_high_test()
            self.last_context = self.market_context

        if self.pos != 0:
            self._update_position_risk(bar, atr_5, stop_buffer)

        bar_range = bar_m.bar_range
        if bar_range <= 0:
            bar_range = tick
        th = self._pattern_th
        is_bull_reversal = bp_is_bull_reversal(bar_m, bar_range, th)
        is_bear_reversal = bp_is_bear_reversal(bar_m, bar_range, th)
        is_boundary_bull = is_boundary_bull_reversal(bar_m, bar_range, th)
        is_boundary_bear = is_boundary_bear_reversal(bar_m, bar_range, th)
        is_strong_bar = bp_is_strong_bar(bar_m, bar_range, atr_5, th)
        upper_shadow = bar_m.upper_shadow
        lower_shadow = bar_m.lower_shadow
        body = bar_m.body
        prev_high = float(self.am_5min.high[-2])
        recent_5bar_low = float(np.min(self.am_5min.low_array[-6:-1]))
        is_oo = (
            is_outside_outside(
                tuple(float(self.am_5min.high[-i]) for i in (1, 2, 3)),
                tuple(float(self.am_5min.low[-i]) for i in (1, 2, 3)),
            )
            if self.am_5min.count >= 5
            else False
        )

        # ── 状态机执行（PENDING_CONFIRM / FAST_TRACK_ARMED）──
        if self.pos == 0 and self.machine_state != "IDLE":
            if self._execute_state_machine(bar, atr_5, tick, is_strong_bar):
                return

        effective_context = self.market_context
        boundary_tol = self.day_boundary_tolerance * tick
        day_high_touch_tol = self.day_high_second_test_ticks * tick
        lh_max_drop = self.day_high_lh_max_ticks * tick
        is_long_climax = (bar.close_price - ema_20) > (self.long_climax_atr_mult * atr_5)
        is_short_climax = (ema_20 - bar.close_price) > (self.long_climax_atr_mult * atr_5)

        dry_kwargs = dict(
            effective_context=effective_context,
            atr_5=atr_5,
            tick=tick,
            stop_buffer=stop_buffer,
            ema_20=ema_20,
            bar_range=bar_range,
            body=body,
            prev_high=prev_high,
            recent_5bar_low=recent_5bar_low,
            is_strong_bar=is_strong_bar,
            is_bull_reversal=is_bull_reversal,
            is_bear_reversal=is_bear_reversal,
            is_boundary_bull=is_boundary_bull,
            is_boundary_bear=is_boundary_bear,
            is_oo=is_oo,
            is_long_climax=is_long_climax,
            is_short_climax=is_short_climax,
            boundary_tol=boundary_tol,
            day_high_touch_tol=day_high_touch_tol,
            lh_max_drop=lh_max_drop,
            upper_shadow=upper_shadow,
            lower_shadow=lower_shadow,
        )

        # ── 全局硬过滤 ──
        global_skip = ""
        if not self.entry_window_open:
            self._reset_machine()
            global_skip = "ENTRY_WINDOW_CLOSED"
        elif atr_5 < self._min_atr_for_context(effective_context):
            self._reset_machine()
            global_skip = "ATR_TOO_LOW"
        elif self.pos != 0:
            global_skip = "HAS_POSITION"
        elif not allow_new_entry:
            self._reset_machine()
            global_skip = "REGIME_DISALLOW"
        elif self.daily_trade_count >= self.max_daily_trades:
            global_skip = "MAX_DAILY_TRADES"

        if global_skip:
            return

        self._shadow_bar_first_attempt = ""
        try:
            # ── OPP15 Wedge trigger + arm ──
            if self._process_wedge_trigger_phase(bar, atr_5, tick, is_strong_bar=is_strong_bar):
                return
            if (not self.wedge_setup_active and self.machine_state == "IDLE" and not is_oo):
                self._try_arm_wedge_setup(bar, atr_5, tick)

            # ── OPP08 强突破（STRONG_BULL/BEAR + BEAR_CHANNEL）──
            if self._process_strong_breakout(
                    bar, effective_context, atr_5, tick, stop_buffer, bar_range,
                    ema_20, prev_high, recent_5bar_low, is_strong_bar, is_oo,
                    is_long_climax, is_short_climax):
                return

            # ── Context 路由：通道超调 / 宽幅日边界 ──
            if effective_context in ("BULL_CHANNEL", "BEAR_CHANNEL"):
                self._try_overshoot_fail(bar, atr_5, tick, stop_buffer, bar_range, ema_20,
                                         is_bull_reversal, is_bear_reversal, is_oo)
                if self.machine_state != "IDLE":
                    return
            elif effective_context == "WIDE_RANGE":
                if self._try_day_boundary_reversal(
                        bar, atr_5, tick, bar_range, upper_shadow, lower_shadow,
                        is_boundary_bull, is_boundary_bear, boundary_tol, is_oo):
                    return
                if self._try_day_high_double_top(
                        bar, atr_5, tick, bar_range, upper_shadow, is_boundary_bear,
                        effective_context, day_high_touch_tol, lh_max_drop):
                    return

            # ── OPP16 Two-Bar Reversal ──
            if (self.two_bar_rev_enabled and self.machine_state == "IDLE" and self.pos == 0
                    and self._process_two_bar_reversal(
                        bar, effective_context, atr_5, tick, stop_buffer, bar_range, body)):
                return
            # ── OPP02 EMA Pullback ──
            if (self.ema_pullback_enabled and self.machine_state == "IDLE" and self.pos == 0
                    and self._process_ema_pullback(
                        bar, effective_context, atr_5, tick, stop_buffer, bar_range, body, ema_20, is_oo)):
                return
            # ── OPP17 Climax Reversal ──
            if (self.climax_rev_enabled and self.machine_state == "IDLE" and self.pos == 0
                    and self._process_climax_reversal(
                        bar, effective_context, atr_5, tick, stop_buffer, bar_range, is_oo)):
                return
            # ── OPP19 Opening Drive ──
            if (self.opening_drive_enabled and self.machine_state == "IDLE" and self.pos == 0
                    and self._process_opening_drive(
                        bar, effective_context, atr_5, tick, stop_buffer, bar_range,
                        body, is_strong_bar, is_oo)):
                return
        finally:
            self._record_vsa_slot_volume(bar)
            if self.shadow_ledger_enabled:
                # 若仅 FIRST_TEST 占位 return 且无 arm 记录，用占位标签抢占
                if (not getattr(self, "_shadow_bar_first_attempt", "")
                        and self.day_high_test_state == "FIRST_TEST"
                        and not self._shadow_ledger.bar_winner(bar.datetime)):
                    self._shadow_bar_first_attempt = "OPP13_DAY_HIGH_FIRST_TEST"
                self._shadow_dry_scan_bar(bar, **dry_kwargs)

    def on_15min_bar(self, bar: BarData) -> None:
        """15m Context Engine：market_context + always_in + MTF wedge 确认。"""
        self.am_15min.update_bar(bar)
        if not self.am_15min.inited:
            return
        atr_15 = float(self.am_15min.atr(self.atr_window))
        closes = self.am_15min.close_array
        highs = self.am_15min.high_array
        lows = self.am_15min.low_array
        opens = self.am_15min.open_array
        ema_15 = talib.EMA(closes, self.ema_window)
        if len(ema_15) < 12 or np.isnan(ema_15[-1]):
            return
        self.market_context = self._classify_market_context(
            highs, lows, closes, opens, ema_15, atr_15)
        self._update_context_layers(highs, lows, closes, ema_15, atr_15)
        self._update_mtf_wedge_exhaustion_zone(atr_15)
        self._update_always_in_state(closes, ema_15, bar, self.get_pricetick(), atr_15)
        self._update_aff_state()
        self._update_trend_regime_state()

    def _update_context_layers(
        self,
        highs,
        lows,
        closes,
        ema_15,
        atr_15: float,
    ) -> None:
        """刷新 15m 快/慢连续因子；离散 market_context 仍由 _classify_market_context 负责。"""
        if not self.context_layers_enabled:
            self._context_layers = empty_snapshot(
                fast_n=int(self.context_layer_fast_bars),
                slow_n=int(self.context_layer_slow_bars),
            )
            self.ctx_trend_quality = 0.0
            self.ctx_opp08_fit = 0.5
            self.ctx_opp16_fit = 0.5
            return
        snap = compute_context_layers(
            highs,
            lows,
            closes,
            ema_15,
            float(atr_15),
            fast_n=int(self.context_layer_fast_bars),
            slow_n=int(self.context_layer_slow_bars),
        )
        self._context_layers = snap
        self.ctx_trend_quality = float(snap.trend_quality)
        self.ctx_opp08_fit = float(snap.opp08_fit)
        self.ctx_opp16_fit = float(snap.opp16_fit)

    def context_layer_snapshot(self) -> ContextLayerSnapshot:
        return getattr(self, "_context_layers", None) or empty_snapshot(
            fast_n=int(self.context_layer_fast_bars),
            slow_n=int(self.context_layer_slow_bars),
        )

    def _context_layer_blocks_entry(self, direction: int, opportunity: str) -> bool:
        if not self.context_layer_gate_enabled or not self.context_layers_enabled:
            return False
        reason = layer_gate_blocks(
            self.context_layer_snapshot(),
            setup=opportunity,
            direction=direction,
            min_opp08_fit=float(self.context_layer_opp08_min_fit),
            min_opp16_fit=float(self.context_layer_opp16_min_fit),
        )
        if reason:
            self._context_layer_block_count = int(
                getattr(self, "_context_layer_block_count", 0)
            ) + 1
            return True
        return False

    def _update_trend_regime_state(self) -> None:
        """15m 收盘后刷新 R² / CHOP（Setup 趋势延续门禁用）。"""
        period = int(self.trend_gate_r2_period)
        if not self.am_15min.inited or self.am_15min.count < period:
            self._trend_r2 = 0.0
            self._trend_chop = 100.0
            return
        closes = self.am_15min.close_array
        self._trend_r2 = compute_trend_r2(closes, period=period)
        chop_p = int(self.trend_gate_chop_period)
        if self.am_15min.count >= chop_p:
            self._trend_chop = compute_chop_index(
                self.am_15min.high_array,
                self.am_15min.low_array,
                closes,
                period=chop_p,
            )
        else:
            self._trend_chop = 100.0

    def _trend_regime_blocks_continuation(self, r2_min: float) -> bool:
        """R² 低于阈值或（可选）CHOP 过高 → 趋势延续 setup 拒单。"""
        if self._trend_r2 < r2_min:
            return True
        if self.trend_gate_use_chop and self._trend_chop > self.trend_gate_chop_max:
            return True
        return False

    def _update_aff_state(self) -> None:
        """15m 收盘后刷新 AFF alpha（Compression × ER）。"""
        if not self.am_15min.inited or self.am_15min.count < 30:
            self._aff_alpha_strength = 0.0
            self._aff_compression_score = 0.0
            self._aff_env_score = 0.0
            self._aff_er = 0.0
            self._aff_archetype = "LOW_ALPHA"
            return
        n = min(self.am_15min.count, 300)
        snap = compute_aff_snapshot(
            self.am_15min.close_array[-n:],
            self.am_15min.high_array[-n:],
            self.am_15min.low_array[-n:],
            self.am_15min.open_array[-n:],
            er_period=self.ema_window,
        )
        self._aff_alpha_strength = snap.alpha_strength
        self._aff_compression_score = snap.compression_score
        self._aff_env_score = snap.env_score
        self._aff_er = snap.er
        self._aff_archetype = classify_aff_archetype(
            alpha=self._aff_alpha_strength,
            compression=self._aff_compression_score,
            env=self._aff_env_score,
            alpha_low=self.aff_archetype_alpha_low,
            compression_min=self.aff_archetype_compression_min,
            expansion_env_min=self.aff_archetype_expansion_env_min,
            exhaustion_env_max=self.aff_archetype_exhaustion_env_max,
        )
        self._update_symbol_liquidity_runtime()

    def _update_symbol_liquidity_runtime(self) -> None:
        if (self.symbol_liquidity_tier != "LOW"
                or not self.symbol_liquidity_runtime_enabled
                or self.symbol_vol_baseline_1m <= 0
                or not self.am_15min.inited):
            self._symbol_liquidity_runtime_mult = 1.0
            return
        n = min(int(self.am_15min.count), 20)
        if n < 5:
            self._symbol_liquidity_runtime_mult = 1.0
            return
        recent = float(np.median(self.am_15min.volume_array[-n:]))
        self._symbol_liquidity_runtime_mult = runtime_liquidity_risk_mult(
            recent, self.symbol_vol_baseline_1m,
            floor=self.symbol_liquidity_risk_floor * 0.9,
        )

    def _get_symbol_liquidity_risk_mult(self) -> float:
        if (not self.symbol_adaptive_enabled
                or self.symbol_liquidity_tier != "LOW"
                or self.symbol_vol_baseline_1m <= 0):
            return 1.0
        return self._symbol_liquidity_static_mult * self._symbol_liquidity_runtime_mult

    def _aff_archetype_blocks_entry(self, opportunity: str) -> bool:
        if not self.aff_archetype_router_enabled:
            return False
        lane = self._setup_entry_lane(opportunity)
        if setup_allowed_for_archetype(
            opportunity,
            self._aff_archetype,
            lane=lane,
            use_lane_matrix=self.aff_archetype_use_lane_matrix,
            adaptive_enabled=self.aff_archetype_adaptive_enabled,
            minimal_enabled=self.aff_archetype_minimal_enabled,
            always_in=self.always_in,
            market_context=self.market_context,
            trend_bypass_prefixes=self._trend_bypass_prefixes,
        ):
            return False
        return True

    # ──────────────────────────────────────────────────────────────────────
    # Context / 市场结构
    # ──────────────────────────────────────────────────────────────────────
    @staticmethod
    def _is_noise_window(t: time) -> bool:
        return (time(21, 0) <= t <= time(21, 5) or time(9, 0) <= t <= time(9, 5)
                or time(13, 0) <= t <= time(13, 5))

    def _min_atr_for_context(self, context: str | None = None) -> float:
        ctx = context or self.market_context
        return self.ttr_rb_min_atr if ctx == "TIGHT_RANGE" else self.rb_min_atr

    def _classify_market_context(self, highs, lows, closes, opens, ema, atr) -> str:
        if len(ema) < 12 or np.isnan(ema[-1]) or len(highs) < 10:
            return "TRADING_RANGE"
        h10, l10, c10, o10 = highs[-10:], lows[-10:], closes[-10:], opens[-10:]
        ranges = h10 - l10
        bodies = np.abs(c10 - o10)
        # 趋势棒计数
        bull_cnt = bear_cnt = 0
        for i in range(len(c10)):
            r = float(ranges[i])
            if r <= 0 or float(bodies[i]) / r < self.strong_context_trend_bar_ratio:
                continue
            if c10[i] > o10[i]:
                bull_cnt += 1
            elif c10[i] < o10[i]:
                bear_cnt += 1
        avg_body_ratio = float(np.mean(bodies / np.where(ranges == 0, 1.0, ranges)))
        strong_by_body = avg_body_ratio > self.strong_context_avg_body_ratio
        strong_bull = bull_cnt >= self.strong_context_min_trend_bars or strong_by_body
        strong_bear = bear_cnt >= self.strong_context_min_trend_bars or strong_by_body
        cross_count = sum(1 for i in range(-10, 0) if highs[i] > ema[i] and lows[i] < ema[i])
        # 结构
        struct_bull = (len(highs) >= 5 and highs[-1] > highs[-3] > highs[-5]
                       and lows[-2] > lows[-4])
        struct_bear = (len(lows) >= 5 and lows[-1] < lows[-3] < lows[-5]
                       and highs[-2] < highs[-4])
        if atr < self.rb_min_atr * 1.5:
            return "TIGHT_RANGE"
        if cross_count <= 1:
            if closes[-1] > ema[-1] and len(ema) >= 3 and ema[-1] > ema[-3] and strong_bull:
                return "STRONG_BULL"
            if closes[-1] < ema[-1] and len(ema) >= 3 and ema[-1] < ema[-3] and strong_bear:
                return "STRONG_BEAR"
            return "WIDE_RANGE"
        if cross_count <= 2 and (np.all(np.diff(ema[-5:]) > 0) or np.all(np.diff(ema[-5:]) < 0)):
            return "BULL_CHANNEL" if np.all(np.diff(ema[-5:]) > 0) else "BEAR_CHANNEL"
        if struct_bull and (ema[-1] - ema[-5]) > 0:
            return "BULL_CHANNEL"
        if struct_bear and (ema[-1] - ema[-5]) < 0:
            return "BEAR_CHANNEL"
        return "WIDE_RANGE"

    def _update_always_in_state(self, closes, ema_15, bar, tick, atr_15=0.0) -> None:
        n = self.alwaysin_min_bars
        m = min(len(closes), len(ema_15))
        if m < n + 2:
            self.always_in = "NONE"
            return
        cr, er = closes[-n:], ema_15[-n:]
        all_above = bool(np.all(cr > er))
        all_below = bool(np.all(cr < er))
        if not all_above and not all_below:
            self.always_in = "NONE"
            return
        ema_slope = float(ema_15[-1] - ema_15[-n])
        if (all_above and ema_slope <= 0) or (all_below and ema_slope >= 0):
            self.always_in = "NONE"
            return
        self.always_in = "LONG" if all_above else "SHORT"
        target_dir = 1 if self.always_in == "LONG" else -1
        if target_dir != self.trend_direction or target_dir == 0:
            self.trend_direction = target_dir
            self.trend_age_bars = 1 if target_dir != 0 else 0
            self.trend_pullback_count = 0
            self.trend_entry_atr = atr_15 if target_dir != 0 else 0.0
            self.trend_phase = "EARLY" if target_dir != 0 else ""
        else:
            self.trend_age_bars += 1
            self.trend_pullback_count = int(
                self.h_counter if self.trend_direction > 0 else self.l_counter)
            if self.trend_age_bars < 8:
                self.trend_phase = "EARLY"
            elif self.trend_age_bars < 20:
                self.trend_phase = "MATURE"
            else:
                if (self.trend_entry_atr > 0
                        and atr_15 / self.trend_entry_atr < self.trend_late_atr_shrink_ratio
                        or self.trend_pullback_count >= self.trend_late_counter_threshold):
                    self.trend_phase = "LATE"
                else:
                    self.trend_phase = "MATURE"

    # ──────────────────────────────────────────────────────────────────────
    # VWAP + Dual Core
    # ──────────────────────────────────────────────────────────────────────
    def _reset_vwap(self) -> None:
        self.vwap = 0.0
        self._vwap_cum_pv = 0.0
        self._vwap_cum_vol = 0.0
        self.vwap_regime = "UNINIT"
        self.vwap_slope_ticks = 0.0
        self.vwap_distance_atr = 0.0
        self.vwap_cross_count = 0
        self._vwap_close_side = 0
        self._vwap_samples.clear()
        self._last_1m_close = 0.0

    def _update_vwap(self, bar: BarData) -> None:
        vol = float(bar.volume)
        if vol <= 0:
            return
        typical = (bar.high_price + bar.low_price + bar.close_price) / 3.0
        self._vwap_cum_pv += typical * vol
        self._vwap_cum_vol += vol
        self.vwap = self._vwap_cum_pv / self._vwap_cum_vol

    def _update_vwap_regime(self, bar: BarData) -> None:
        self._last_1m_close = bar.close_price
        if self.vwap <= 0:
            self.vwap_regime = "UNINIT"
            return
        tick = self.get_pricetick()
        side = 1 if bar.close_price > self.vwap else (-1 if bar.close_price < self.vwap else 0)
        if self._vwap_close_side != 0 and side != 0 and side != self._vwap_close_side:
            self.vwap_cross_count += 1
        if side != 0:
            self._vwap_close_side = side
        self._vwap_samples.append(self.vwap)
        lookback = max(int(self.vwap_regime_lookback), 2)
        if len(self._vwap_samples) > lookback:
            self._vwap_samples.pop(0)
        if len(self._vwap_samples) >= 2:
            self.vwap_slope_ticks = (self._vwap_samples[-1] - self._vwap_samples[0]) / tick
        else:
            self.vwap_slope_ticks = 0.0
        if self.am_5min.inited:
            atr_5 = float(self.am_5min.atr(self.atr_window))
            if atr_5 > 0:
                self.vwap_distance_atr = (bar.close_price - self.vwap) / atr_5
        deadband = self.vwap_trend_deadband_ticks * tick
        if self.vwap_cross_count >= self.vwap_chop_min_crosses:
            self.vwap_regime = "CHOP"
        elif (self.vwap_slope_ticks > self.vwap_slope_thresh_ticks
              and bar.close_price > self.vwap + deadband):
            self.vwap_regime = "TREND_UP"
        elif (self.vwap_slope_ticks < -self.vwap_slope_thresh_ticks
              and bar.close_price < self.vwap - deadband):
            self.vwap_regime = "TREND_DOWN"
        else:
            self.vwap_regime = "CHOP"

    @staticmethod
    def _setup_entry_lane(opportunity: str) -> str:
        name = opportunity or ""
        for prefix, lane in _ENTRY_LANE_MAP.items():
            if name.startswith(prefix):
                return lane
        return "TREND"

    def _dual_core_allows_entry(self, direction: int, lane: str) -> bool:
        if not self.dual_core_enabled or self.vwap_regime == "UNINIT":
            return True
        # 软模式：不拒单，由 _dual_core_soft_adjust 降仓/缩目标
        if getattr(self, "dual_core_soft_enabled", False):
            return True
        ctx = self.market_context
        close = self._last_1m_close
        tick = self.get_pricetick()
        deadband = self.vwap_trend_deadband_ticks * tick
        tr_ctx = {"TRADING_RANGE", "TIGHT_RANGE"}
        if lane == "TREND":
            if self.vwap_regime == "CHOP" and ctx in tr_ctx:
                self._dual_core_block_count += 1
                return False
            if direction > 0 and self.vwap_regime == "TREND_DOWN":
                self._dual_core_block_count += 1
                return False
            if direction < 0 and self.vwap_regime == "TREND_UP":
                self._dual_core_block_count += 1
                return False
            if self.vwap > 0:
                if direction > 0 and close < self.vwap - deadband:
                    self._dual_core_block_count += 1
                    return False
                if direction < 0 and close > self.vwap + deadband:
                    self._dual_core_block_count += 1
                    return False
            return True
        if self.vwap_regime in ("TREND_UP", "TREND_DOWN"):
            if abs(self.vwap_distance_atr) > self.vwap_fade_max_atr:
                self._dual_core_block_count += 1
                return False
        if self.vwap_regime == "CHOP" and ctx in ("STRONG_BULL", "STRONG_BEAR"):
            self._dual_core_block_count += 1
            return False
        return True

    def _dual_core_soft_adjust(
        self, direction: int, opportunity: str = ""
    ) -> tuple[float, float]:
        """软 Dual Core：返回 (size_mult, target_mult)，不拒单。

        OPP08：突破后须在 VWAP 同侧；与日内 VWAP 反向/震荡时降仓缩目标。
        OPP16：看相对 VWAP 的衰竭偏离，而非仅 VWAP 三态硬切。
        """
        size_m, tgt_m = 1.0, 1.0
        if (
            not self.dual_core_enabled
            or not getattr(self, "dual_core_soft_enabled", False)
            or self.vwap_regime == "UNINIT"
            or direction == 0
        ):
            return 1.0, 1.0

        opp = opportunity or getattr(self, "active_setup_name", "") or ""
        lane = self._setup_entry_lane(opp) if opp else "TREND"
        ctx = self.market_context
        close = float(self._last_1m_close or 0.0)
        dist = float(self.vwap_distance_atr or 0.0)
        regime = self.vwap_regime
        tr_ctx = {"TRADING_RANGE", "TIGHT_RANGE"}
        tick = self.get_pricetick()
        deadband = self.vwap_trend_deadband_ticks * tick
        exh_full = float(getattr(self, "dual_core_exhaustion_atr", 1.0))
        exh_min = float(getattr(self, "dual_core_exhaustion_min_atr", 0.4))
        min_size = float(getattr(self, "dual_core_soft_min_size_mult", 0.25))
        min_tgt = float(getattr(self, "dual_core_soft_min_target_mult", 0.40))

        is_opp08 = opp.startswith("OPP08_") or lane == "TREND"

        if is_opp08 and not opp.startswith("OPP16_"):
            # 突破后是否仍在 VWAP 同侧
            if self.vwap > 0 and close > 0:
                same_side = (
                    (direction > 0 and close >= self.vwap)
                    or (direction < 0 and close <= self.vwap)
                )
                if not same_side:
                    size_m *= 0.50
                    tgt_m *= 0.65
                if direction > 0 and close < self.vwap - deadband:
                    size_m *= 0.55
                    tgt_m *= 0.75
                if direction < 0 and close > self.vwap + deadband:
                    size_m *= 0.55
                    tgt_m *= 0.75
            # Brooks 趋势 vs 日内 VWAP 冲突 → 降仓而非拒单
            if regime == "CHOP" and ctx in tr_ctx:
                size_m *= 0.55
                tgt_m *= 0.75
            if direction > 0 and regime == "TREND_DOWN":
                size_m *= 0.40
                tgt_m *= 0.60
            if direction < 0 and regime == "TREND_UP":
                size_m *= 0.40
                tgt_m *= 0.60

        opp16_soft = (
            opp.startswith("OPP16_")
            and getattr(self, "dual_core_opp16_soft_enabled", True)
        )
        if opp16_soft or opp.startswith(("OPP13_", "OPP17_")):
            wrong_size = float(
                getattr(self, "dual_core_opp16_wrong_side_size_mult", 0.40)
            )
            wrong_tgt = float(
                getattr(self, "dual_core_opp16_wrong_side_target_mult", 0.60)
            )
            shallow_size = float(
                getattr(self, "dual_core_opp16_shallow_size_mult", 0.55)
            )
            shallow_tgt = float(
                getattr(self, "dual_core_opp16_shallow_target_mult", 0.75)
            )
            favor_size_floor = float(
                getattr(self, "dual_core_opp16_favor_size_floor", 0.85)
            )
            favor_tgt_floor = float(
                getattr(self, "dual_core_opp16_favor_target_floor", 0.90)
            )
            skip_extra = bool(
                getattr(self, "dual_core_opp16_favor_skip_extra", True)
            )
            # 反转有利侧：多在下、空在上
            favorable = (direction > 0 and dist < 0) or (direction < 0 and dist > 0)
            wrong_side = (direction > 0 and dist >= 0) or (direction < 0 and dist <= 0)
            if wrong_side:
                size_m *= wrong_size
                tgt_m *= wrong_tgt
            elif abs(dist) < exh_min:
                size_m *= shallow_size
                tgt_m *= shallow_tgt
            elif abs(dist) < exh_full:
                frac = (abs(dist) - exh_min) / max(exh_full - exh_min, 1e-6)
                if favorable:
                    size_m *= favor_size_floor + (1.0 - favor_size_floor) * frac
                    tgt_m *= favor_tgt_floor + (1.0 - favor_tgt_floor) * frac
                else:
                    size_m *= shallow_size + (1.0 - shallow_size) * frac
                    tgt_m *= shallow_tgt + (1.0 - shallow_tgt) * frac
            extra_ok = not (skip_extra and favorable and opp.startswith("OPP16_"))
            if extra_ok:
                if regime in ("TREND_UP", "TREND_DOWN") and abs(dist) > self.vwap_fade_max_atr:
                    size_m *= 0.50
                    tgt_m *= 0.55
                if regime == "CHOP" and ctx in ("STRONG_BULL", "STRONG_BEAR"):
                    size_m *= 0.60
                    tgt_m *= 0.80

        if opp.startswith("OPP16_"):
            min_size = float(
                getattr(self, "dual_core_opp16_soft_min_size_mult", min_size)
            )
            min_tgt = float(
                getattr(self, "dual_core_opp16_soft_min_target_mult", min_tgt)
            )

        size_m = max(min_size, min(1.0, size_m))
        tgt_m = max(min_tgt, min(1.0, tgt_m))
        if size_m < 0.999 or tgt_m < 0.999:
            self._dual_core_soft_reduce_count = (
                getattr(self, "_dual_core_soft_reduce_count", 0) + 1
            )
        return size_m, tgt_m

    def _refresh_dual_core_soft_mults(
        self, direction: int | None = None, opportunity: str | None = None
    ) -> None:
        d = int(direction if direction is not None else (self.pending_dir or 0))
        opp = opportunity if opportunity is not None else (self.active_setup_name or "")
        size_m, tgt_m = self._dual_core_soft_adjust(d, opp)
        self._dual_core_size_mult = size_m
        self._dual_core_target_mult = tgt_m

    def _clear_tf_counter_exit(self) -> None:
        self._tf_counter_exit_setup = ""
        self._tf_counter_exit_dir = 0
        self._tf_counter_exit_reason = ""
        self._tf_counter_exit_pending = False

    def _queue_tf_counter_exit(self, setup: str, signal_dir: int) -> None:
        cur = getattr(self, "_tf_counter_exit_setup", "") or ""
        if cur and not should_upgrade_arm(cur, setup):
            return
        self._tf_counter_exit_setup = setup
        self._tf_counter_exit_dir = signal_dir
        self._tf_counter_exit_reason = f"TF_COUNTER_{setup}"
        self._tf_counter_exit_pending = True

    def _opp_tf_arm_gate(self, direction: int, opportunity: str) -> bool:
        if not getattr(self, "tf_arm_gate_enabled", True):
            return True
        if self.pos != 0 and is_opposite_direction(self.pos, direction):
            self._queue_tf_counter_exit(opportunity, direction)
            return False
        if self.machine_state in ("PENDING_CONFIRM", "FAST_TRACK_ARMED"):
            cur_setup = self.active_setup_name or ""
            cur_dir = int(self.pending_dir)
            if cur_dir == direction:
                if not should_upgrade_arm(cur_setup, opportunity):
                    return False
            elif not should_upgrade_arm(cur_setup, opportunity):
                return False
        return True

    def _process_tf_counter_exit(self, bar: BarData) -> bool:
        if not getattr(self, "_tf_counter_exit_pending", False):
            return False
        if self.pos == 0:
            self._clear_tf_counter_exit()
            return False
        mode = getattr(self, "tf_counter_exit_mode", "ON_1M_CLOSE")
        if mode == "OFF":
            return False
        sig_dir = int(getattr(self, "_tf_counter_exit_dir", 0))
        if not is_opposite_direction(self.pos, sig_dir):
            self._clear_tf_counter_exit()
            return False
        reason = self._tf_counter_exit_reason or "TF_COUNTER"
        if self.pos > 0:
            self._close_long_position(
                bar.close_price, exit_reason=reason, kind="TF_COUNTER", allow_replace=True)
        else:
            self._close_short_position(
                bar.close_price, exit_reason=reason, kind="TF_COUNTER", allow_replace=True)
        self._clear_tf_counter_exit()
        return True

    # ──────────────────────────────────────────────────────────────────────
    # Arm / Cap / 状态机执行
    # ──────────────────────────────────────────────────────────────────────
    @staticmethod
    def _parse_disabled_setups(raw: str) -> tuple[str, ...]:
        if not raw or not str(raw).strip():
            return ()
        return tuple(p.strip() for p in str(raw).split(",") if p.strip())

    def _setup_disabled(self, opportunity: str) -> bool:
        """前缀匹配硬禁（如 OPP12_ / OPP16_5M_TWO_BAR_REV_SHORT）。"""
        opp = opportunity or ""
        if not opp:
            return False
        if getattr(self, "setup_shrinkage_enabled", False) and getattr(self, "setup_shrinkage_hard_disable", False):
            mult = self._get_setup_shrinkage_mult(opp)
            if mult <= 0:
                return True
        for prefix in self._parse_disabled_setups(self.disabled_setups):
            if opp.startswith(prefix):
                return True
        return False

    def _get_setup_shrinkage_mult(self, setup: str | None = None) -> float:
        if not getattr(self, "setup_shrinkage_enabled", False):
            return 1.0
        name = setup or self.active_setup_name or ""
        overrides = parse_shrinkage_overrides(getattr(self, "setup_shrinkage_overrides", "") or "")
        default = 0.5
        return lookup_shrinkage_mult(name, overrides, default)

    def _shadow_increment_gate_block(self, gate: str) -> None:
        if gate == "aff_archetype":
            self._aff_archetype_block_count += 1
        elif gate == "late_phase":
            self._late_phase_block_count += 1
        elif gate == "aff_filter":
            self._aff_block_count += 1
        elif gate == "opp13_volume":
            self._opp13_vol_block_count += 1

    def _shadow_entry_price(self, bar: BarData, direction: int, tick: float) -> float:
        if direction > 0:
            return bar.close_price + tick
        return bar.close_price - tick

    def _shadow_log_candidate(
        self,
        *,
        bar: BarData,
        direction: int,
        opportunity: str,
        entry_price: float,
        trigger: float,
        stop: float,
        arm_mode: str,
        gates: dict,
        first_block: str | None,
        allow_preempt: bool = True,
        global_skip_reason: str = "",
        source: str = "ARM",
        force_disposition: str = "",
        preempted_by: str = "",
    ) -> str:
        ledger = self._shadow_ledger
        if not getattr(self, "_shadow_bar_first_attempt", ""):
            self._shadow_bar_first_attempt = opportunity
        if force_disposition:
            disposition = force_disposition
        elif first_block:
            disposition = "GATE_BLOCKED"
            # 计数已在 _production_gates_pass 完成；此处不重复 increment
        elif self.pos != 0:
            disposition = "POS_SKIP"
        elif global_skip_reason:
            disposition = "GLOBAL_SKIP"
        elif allow_preempt and ledger.bar_winner(bar.datetime):
            preempted_by = preempted_by or ledger.bar_winner(bar.datetime)
            disposition = "PREEMPTED"
        else:
            disposition = "ARMED"
        if disposition == "PREEMPTED" and not preempted_by:
            preempted_by = (
                ledger.bar_winner(bar.datetime)
                or getattr(self, "_shadow_bar_first_attempt", "")
                or ""
            )
        rec = build_candidate_from_strategy(
            ledger,
            self,
            bar=bar,
            opportunity=opportunity,
            direction=direction,
            entry_price=entry_price,
            stop=stop,
            trigger=trigger,
            arm_mode=arm_mode,
            gates=gates,
            first_block=first_block,
            disposition=disposition,
            preempted_by=preempted_by,
            global_skip_reason=global_skip_reason,
            source=source,
        )
        ledger.add(rec)
        return disposition

    def _shadow_mark_bar_winner(self, bar: BarData, setup: str) -> None:
        if self.shadow_ledger_enabled and self._shadow_ledger is not None:
            self._shadow_ledger.set_bar_winner(bar.datetime, setup)

    def _shadow_gate_counters_snapshot(self) -> dict:
        return {
            "_aff_archetype_block_count": self._aff_archetype_block_count,
            "_late_phase_block_count": self._late_phase_block_count,
            "_aff_block_count": self._aff_block_count,
            "_dual_core_block_count": self._dual_core_block_count,
            "_opp13_vol_block_count": self._opp13_vol_block_count,
            "vsa_block_count": int(getattr(self, "vsa_block_count", 0)),
            "_vsa_block_count": int(getattr(self, "_vsa_block_count", 0)),
        }

    def _shadow_gate_counters_restore(self, snap: dict) -> None:
        for k, v in snap.items():
            setattr(self, k, v)

    def _shadow_dry_scan_bar(
        self,
        bar: BarData,
        *,
        effective_context: str,
        atr_5: float,
        tick: float,
        stop_buffer: float,
        ema_20: float,
        bar_range: float,
        body: float,
        prev_high: float,
        recent_5bar_low: float,
        is_strong_bar: bool,
        is_bull_reversal: bool,
        is_bear_reversal: bool,
        is_boundary_bull: bool,
        is_boundary_bear: bool,
        is_oo: bool,
        is_long_climax: bool,
        is_short_climax: bool,
        boundary_tol: float,
        day_high_touch_tol: float,
        lh_max_drop: float,
        upper_shadow: float,
        lower_shadow: float,
        global_skip_reason: str = "",
    ) -> None:
        """Phase-2.1：补记未到达 arm 的 pattern 命中（PREEMPTED / GLOBAL_SKIP）。"""
        if not self.shadow_ledger_enabled or self._shadow_ledger is None:
            return
        matches = collect_production_matches(
            self,
            bar,
            effective_context=effective_context,
            atr_5=atr_5,
            tick=tick,
            stop_buffer=stop_buffer,
            ema_20=ema_20,
            bar_range=bar_range,
            body=body,
            prev_high=prev_high,
            recent_5bar_low=recent_5bar_low,
            is_strong_bar=is_strong_bar,
            is_bull_reversal=is_bull_reversal,
            is_bear_reversal=is_bear_reversal,
            is_boundary_bull=is_boundary_bull,
            is_boundary_bear=is_boundary_bear,
            is_oo=is_oo,
            is_long_climax=is_long_climax,
            is_short_climax=is_short_climax,
            boundary_tol=boundary_tol,
            day_high_touch_tol=day_high_touch_tol,
            lh_max_drop=lh_max_drop,
            upper_shadow=upper_shadow,
            lower_shadow=lower_shadow,
        )
        if not matches:
            return
        winner = self._shadow_ledger.bar_winner(bar.datetime)
        first_attempt = getattr(self, "_shadow_bar_first_attempt", "") or ""
        preempt_label = winner or first_attempt
        for m in matches:
            if self._shadow_ledger.has_setup_at(bar.datetime, m.setup):
                continue
            # 无抢占/无全局跳过 → production 应已走到该 OPP；缺记录则视为未命中，不补记
            if not preempt_label and not global_skip_reason:
                continue
            entry_price = (
                float(m.trigger) if m.is_direct
                else self._shadow_entry_price(bar, m.direction, tick)
            )
            snap = self._shadow_gate_counters_snapshot()
            try:
                if m.is_direct:
                    gates, first_block = evaluate_opp15_direct_gates(
                        self, m.setup, m.direction)
                else:
                    gates, first_block = evaluate_production_gates(
                        self,
                        m.setup,
                        m.direction,
                        bar=bar,
                        include_opp13_volume=m.include_opp13_volume,
                    )
            finally:
                self._shadow_gate_counters_restore(snap)
            if global_skip_reason:
                force = "GLOBAL_SKIP"
                preempted_by = ""
            else:
                force = "PREEMPTED"
                preempted_by = preempt_label
            self._shadow_log_candidate(
                bar=bar,
                direction=m.direction,
                opportunity=m.setup,
                entry_price=entry_price,
                trigger=m.trigger,
                stop=m.stop,
                arm_mode=m.arm_mode,
                gates=gates,
                first_block=first_block,
                allow_preempt=False,
                global_skip_reason=global_skip_reason,
                source="DRY_SCAN",
                force_disposition=force,
                preempted_by=preempted_by,
            )

    def _production_gates_pass(
        self,
        *,
        direction: int,
        opportunity: str,
        bar: BarData | None,
        include_opp13_volume: bool = False,
    ) -> bool:
        if include_opp13_volume and bar is not None:
            if not self._opp13_volume_allows_entry(bar, direction):
                self._opp13_vol_block_count += 1
                return False
        if self._setup_disabled(opportunity):
            return False
        if self._aff_archetype_blocks_entry(opportunity):
            self._aff_archetype_block_count += 1
            return False
        if self._late_phase_blocks_entry(
                direction, self.market_context, opportunity):
            self._late_phase_block_count += 1
            return False
        if self._context_layer_blocks_entry(direction, opportunity):
            return False
        if self._aff_blocks_entry():
            self._aff_block_count += 1
            return False
        lane = self._setup_entry_lane(opportunity)
        if not self._dual_core_allows_entry(direction, lane):
            return False
        if self._vsa_blocks_entry(direction, bar=bar):
            return False
        if not self._opp_tf_arm_gate(direction, opportunity):
            return False
        return True

    def _commit_production_arm(
        self,
        *,
        arm_mode: str,
        direction: int,
        opportunity: str,
        trigger: float,
        stop: float,
        invalid_line: float = 0.0,
    ) -> None:
        if arm_mode == "FAST_TRACK":
            self.machine_state = "FAST_TRACK_ARMED"
            self.entry_lane = "FAST_TRACK"
            self.active_entry_lane = "FAST_TRACK"
            self.signal_bar_invalid_line = invalid_line or stop
        else:
            self.machine_state = "PENDING_CONFIRM"
            self.entry_lane = "PENDING_CONFIRM"
            self.active_entry_lane = "PENDING_CONFIRM"
            self.signal_bar_invalid_line = invalid_line or trigger
        self.pending_dir = direction
        self.active_setup_name = opportunity
        self.trigger_level = trigger
        self._set_stop(stop, "INITIAL", force_source=True)
        self._refresh_dual_core_soft_mults(direction, opportunity)

    def _try_production_arm(
        self,
        *,
        direction: int,
        opportunity: str,
        trigger: float,
        stop: float,
        invalid_line: float = 0.0,
        arm_mode: str = "FAST_TRACK",
        include_opp13_volume: bool = False,
    ) -> bool:
        bar = self._current_5min_bar
        if bar is None:
            return False
        tick = self.get_pricetick()
        entry_price = self._shadow_entry_price(bar, direction, tick)
        passed = self._production_gates_pass(
            direction=direction,
            opportunity=opportunity,
            bar=bar,
            include_opp13_volume=include_opp13_volume,
        )
        if self.shadow_ledger_enabled and self._shadow_ledger is not None:
            snap = self._shadow_gate_counters_snapshot()
            try:
                gates, first_block = evaluate_production_gates(
                    self,
                    opportunity,
                    direction,
                    bar=bar,
                    include_opp13_volume=include_opp13_volume,
                )
            finally:
                self._shadow_gate_counters_restore(snap)
            if not passed:
                first_block = first_block or "production_gates"
            disposition = self._shadow_log_candidate(
                bar=bar,
                direction=direction,
                opportunity=opportunity,
                entry_price=entry_price,
                trigger=trigger,
                stop=stop,
                arm_mode=arm_mode,
                gates=gates,
                first_block=first_block if not passed else None,
                allow_preempt=passed,
            )
            if not passed:
                return False
        elif not passed:
            return False
        self._commit_production_arm(
            arm_mode=arm_mode,
            direction=direction,
            opportunity=opportunity,
            trigger=trigger,
            stop=stop,
            invalid_line=invalid_line,
        )
        if self.shadow_ledger_enabled and bar is not None:
            self._shadow_mark_bar_winner(bar, opportunity)
        return True

    def _try_opp15_direct_entry(
        self,
        *,
        bar: BarData,
        direction: int,
        opportunity: str,
        entry_price: float,
        stop: float,
        invalid_line: float,
        atr_5: float,
    ) -> bool:
        """OPP15 B' 直进：shadow 记录 + 与 production 相同的 gate 子集。"""
        passed = True
        if self._setup_disabled(opportunity):
            passed = False
        elif not self._dual_core_allows_entry(
                direction, self._setup_entry_lane(opportunity)):
            passed = False
        elif self._aff_blocks_entry():
            self._aff_block_count += 1
            passed = False
        self._refresh_dual_core_soft_mults(direction, opportunity)
        volume = self._calc_brooks_volume(
            entry_price if direction > 0 else stop,
            stop if direction > 0 else entry_price,
            atr_5=atr_5,
        )
        if volume <= 0:
            passed = False
        if self.shadow_ledger_enabled and self._shadow_ledger is not None:
            snap = self._shadow_gate_counters_snapshot()
            try:
                gates, first_block = evaluate_opp15_direct_gates(
                    self, opportunity, direction)
            finally:
                self._shadow_gate_counters_restore(snap)
            if not passed:
                first_block = first_block or "production_gates"
            self._shadow_log_candidate(
                bar=bar,
                direction=direction,
                opportunity=opportunity,
                entry_price=entry_price,
                trigger=entry_price,
                stop=stop,
                arm_mode="DIRECT",
                gates=gates,
                first_block=first_block if not passed else None,
                allow_preempt=passed,
            )
            if not passed:
                return False
        elif not passed:
            return False
        self.active_setup_name = opportunity
        self._set_stop(stop, "INITIAL", force_source=True)
        self.signal_bar_invalid_line = invalid_line
        self.profit_protect_active = False
        if direction > 0:
            self.buy(entry_price, volume)
        else:
            self.short(entry_price, volume)
        self._shadow_mark_bar_winner(bar, opportunity)
        return True

    def _arm_fast_track(self, *, direction, opportunity, trigger, stop, invalid_line=0.0) -> None:
        self._try_production_arm(
            direction=direction,
            opportunity=opportunity,
            trigger=trigger,
            stop=stop,
            invalid_line=invalid_line,
            arm_mode="FAST_TRACK",
        )

    def _arm_pending_confirm(self, *, direction, opportunity, trigger, stop, invalid_line=0.0) -> None:
        self._try_production_arm(
            direction=direction,
            opportunity=opportunity,
            trigger=trigger,
            stop=stop,
            invalid_line=invalid_line,
            arm_mode="PENDING_CONFIRM",
        )
    def _execute_state_machine(self, bar, atr_5, tick, is_strong_bar) -> bool:
        """执行 PENDING_CONFIRM / FAST_TRACK_ARMED 状态机，返回是否已处理。"""
        if self.machine_state == "PENDING_CONFIRM":
            confirmed = False
            if self.pending_dir == 1:
                if (bar.close_price > bar.open_price
                        and bar.close_price > self.trigger_level):
                    confirmed = True
                    self.entry_price = bar.close_price + tick
            elif self.pending_dir == -1:
                if (bar.close_price < bar.open_price
                        and bar.close_price < self.trigger_level):
                    confirmed = True
                    self.entry_price = bar.close_price - tick
            filled = False
            if confirmed:
                if self.pending_dir == 1:
                    volume = self._calc_brooks_volume(
                        self.entry_price, self.stop_price, atr_5=atr_5,
                        max_position_cap=self.max_position)
                    if volume > 0:
                        self.profit_protect_active = False
                        self.buy(self.entry_price, volume)
                        filled = True
                else:
                    volume = self._calc_brooks_volume(
                        self.stop_price, self.entry_price, atr_5=atr_5,
                        max_position_cap=self.max_position)
                    if volume > 0:
                        self.profit_protect_active = False
                        self.short(self.entry_price, volume)
                        filled = True
            self._reset_machine()
            return filled
        if self.machine_state == "FAST_TRACK_ARMED":
            if self.pending_dir == 1:
                volume = self._calc_brooks_volume(
                    self.trigger_level, self.stop_price, atr_5=atr_5)
                if volume > 0:
                    self.profit_protect_active = False
                    self.buy(self.trigger_level, volume, stop=True)
            else:
                volume = self._calc_brooks_volume(
                    self.stop_price, self.trigger_level, atr_5=atr_5)
                if volume > 0:
                    self.profit_protect_active = False
                    self.short(self.trigger_level, volume, stop=True)
            self._reset_machine()
            return True
        return False

    def _cap_long_stop(self, raw_stop, ref_price, atr_5) -> float:
        return max(raw_stop, ref_price - self.max_risk_multiplier * atr_5)

    def _cap_short_stop(self, raw_stop, ref_price, atr_5) -> float:
        return min(raw_stop, ref_price + self.max_risk_multiplier * atr_5)

    def _stop_buffer(self, atr_5, tick) -> float:
        del tick
        base_buffer = max(self.stop_buffer_min, self.stop_buffer_atr_mult * atr_5)
        pct = self._atr_percentile(atr_5)
        if pct >= self.stop_buffer_atr_hi_pct:
            base_buffer *= self.stop_buffer_atr_hi_mult
        elif pct <= self.stop_buffer_atr_lo_pct:
            base_buffer *= self.stop_buffer_atr_lo_mult
        return base_buffer

    def _atr_percentile(self, atr_5) -> float:
        n = min(self.atr_percentile_window, self.am_5min.count)
        if n < self.atr_window + 20:
            return 50.0
        atr_series = talib.ATR(
            self.am_5min.high_array[-n:], self.am_5min.low_array[-n:],
            self.am_5min.close_array[-n:], self.atr_window)
        valid = atr_series[~np.isnan(atr_series)]
        if len(valid) < 20:
            return 50.0
        return float(np.searchsorted(np.sort(valid), atr_5) / len(valid) * 100.0)

    def _is_fast_lane_setup(self) -> bool:
        if not getattr(self, "fast_lane_trail_enabled", True):
            return False
        if getattr(self, "exit_family_v3_enabled", False):
            cfg = self._active_exit_family_config()
            if cfg is not None:
                return cfg.enable_fast_lane_trail
        return self.active_entry_lane == "FAST_TRACK"

    def _active_exit_family_config(self) -> ExitFamilyConfig | None:
        if not getattr(self, "exit_family_v3_enabled", False):
            return None
        setup = self.active_setup_name or ""
        if not setup:
            return None
        _, cfg = family_for_setup(setup)
        return cfg

    def _get_breakeven_trigger_atr_mult(self) -> float:
        cfg = self._active_exit_family_config()
        if cfg is not None:
            return cfg.breakeven_atr_mult
        setup = self.active_setup_name or ""
        if setup.startswith(_BREAKEVEN_FAST_SETUPS):
            return self.breakeven_trigger_atr_mult_fast
        return self.breakeven_trigger_atr_mult_slow

    def _mm_runner_allowed(self) -> bool:
        if not getattr(self, "mm_runner_enabled", True):
            return False
        cfg = self._active_exit_family_config()
        if cfg is not None:
            return cfg.enable_mm_runner
        return True

    def _profit_protect_allowed(self) -> bool:
        if not getattr(self, "profit_protect_enabled", True):
            return False
        cfg = self._active_exit_family_config()
        if cfg is not None:
            return cfg.enable_profit_protect
        return True

    def _get_setup_risk_mult(self) -> float:
        """按 active_setup_name 查表缩放单笔 risk_money（仅定仓，不改信号）。"""
        if not self.setup_risk_mult_enabled:
            return 1.0
        setup = self.active_setup_name or ""
        if not setup:
            return self.setup_risk_mult_default
        base = _SETUP_RISK_MULT.get(setup, self.setup_risk_mult_default)
        if getattr(self, "setup_shrinkage_enabled", False):
            return base * self._get_setup_shrinkage_mult(setup)
        return base

    def _late_phase_blocks_entry(
        self, direction: int, effective_context: str, opportunity: str = "",
    ) -> bool:
        """LATE 软禁（对齐 pa 旗舰）：顺趋势末段 / OPP13 双顶底 / 楔形 arm。"""
        if not self.late_phase_gate_enabled or self.trend_phase != "LATE":
            return False
        opp = opportunity or self.active_setup_name or ""
        if opp.startswith("OPP15_"):
            return True
        if opp.startswith("OPP13_"):
            if effective_context == "WIDE_RANGE":
                return False
            if direction < 0 and self.trend_direction == -1:
                return True
            if direction > 0 and self.trend_direction == 1:
                return True
            return False
        if opp.startswith(("OPP08_", "OPP02_", "OPP12_", "OPP19_")):
            if effective_context == "WIDE_RANGE":
                return False
            if direction > 0 and self.trend_direction == 1:
                return True
            if direction < 0 and self.trend_direction == -1:
                return True
        return False

    def _aff_blocks_entry(self) -> bool:
        """filter 模式：alpha_strength 低于激活阈值时拒单。"""
        if not self.aff_gate_enabled or self.aff_gate_mode != "filter":
            return False
        return self._aff_alpha_strength < self.aff_alpha_reject_threshold

    def _get_aff_risk_mult(self) -> float:
        """按 alpha_strength 分档缩放 risk_money（sizing 模式不拒单）。"""
        if not self.aff_gate_enabled:
            return 1.0
        alpha = self._aff_alpha_strength
        if self.aff_gate_mode == "filter":
            if alpha < self.aff_alpha_reject_threshold:
                return 0.0
            if alpha >= self.aff_alpha_high_threshold:
                return self.aff_risk_mult_high
            return self.aff_risk_mult_low
        # sizing：多数时段 compression=0 → alpha=0，降仓但不拒单
        if alpha >= self.aff_alpha_high_threshold:
            return self.aff_risk_mult_high
        if alpha >= self.aff_alpha_reject_threshold:
            return 1.0
        if alpha > 0:
            return 0.85
        return self.aff_risk_mult_low

    @staticmethod
    def _build_pattern_thresholds_from_params(
        *,
        bar_outside_prev_ratio: float,
        bar_trend_body_ratio: float,
        bar_spike_tail_body_ratio: float,
        reversal_shadow_min_ratio: float,
        reversal_close_quarter: float,
        reversal_min_body_ratio: float,
        boundary_reversal_shadow_ratio: float,
        boundary_reversal_close_ratio: float,
        strong_bar_body_ratio: float,
        strong_bar_atr_mult: float,
    ) -> PatternThresholds:
        return PatternThresholds(
            bar_outside_prev_ratio=bar_outside_prev_ratio,
            bar_trend_body_ratio=bar_trend_body_ratio,
            bar_spike_tail_body_ratio=bar_spike_tail_body_ratio,
            reversal_shadow_min_ratio=reversal_shadow_min_ratio,
            reversal_close_quarter=reversal_close_quarter,
            reversal_min_body_ratio=reversal_min_body_ratio,
            boundary_reversal_shadow_ratio=boundary_reversal_shadow_ratio,
            boundary_reversal_close_ratio=boundary_reversal_close_ratio,
            strong_bar_body_ratio=strong_bar_body_ratio,
            strong_bar_atr_mult=strong_bar_atr_mult,
        )

    def _build_pattern_thresholds(self) -> PatternThresholds:
        return self._build_pattern_thresholds_from_params(
            bar_outside_prev_ratio=self.bar_outside_prev_ratio,
            bar_trend_body_ratio=self.bar_trend_body_ratio,
            bar_spike_tail_body_ratio=self.bar_spike_tail_body_ratio,
            reversal_shadow_min_ratio=self.reversal_shadow_min_ratio,
            reversal_close_quarter=self.reversal_close_quarter,
            reversal_min_body_ratio=self.reversal_min_body_ratio,
            boundary_reversal_shadow_ratio=self.boundary_reversal_shadow_ratio,
            boundary_reversal_close_ratio=self.boundary_reversal_close_ratio,
            strong_bar_body_ratio=self.strong_bar_body_ratio,
            strong_bar_atr_mult=self.strong_bar_atr_mult,
        )

    # ──────────────────────────────────────────────────────────────────────
    # PD levels
    # ──────────────────────────────────────────────────────────────────────
    def _update_pd_levels(self, bar: BarData) -> None:
        bar_date = bar.datetime.date()
        if self._last_5min_date is None:
            self._last_5min_date = bar_date
            self._cur_day_first_open = bar.open_price
            self._cur_day_last_close = bar.close_price
            return
        if bar_date != self._last_5min_date:
            self.pd_open = self._cur_day_first_open
            self.pd_close = self._cur_day_last_close
            self._cur_day_first_open = bar.open_price
            self._cur_day_last_close = bar.close_price
            self._last_5min_date = bar_date
        else:
            self._cur_day_last_close = bar.close_price

    def _pd_blocks_long_target(self, ref_price, atr_5) -> bool:
        if self.pd_close <= 0 or ref_price >= self.pd_close:
            return False
        return (self.pd_close - ref_price) <= atr_5 * self.pd_level_block_atr_mult

    def _pd_blocks_short_target(self, ref_price, atr_5) -> bool:
        if self.pd_open <= 0 or ref_price <= self.pd_open:
            return False
        return (ref_price - self.pd_open) <= atr_5 * self.pd_level_block_atr_mult

    # ──────────────────────────────────────────────────────────────────────
    # 重置函数
    # ──────────────────────────────────────────────────────────────────────
    def _reset_machine(self) -> None:
        self.machine_state = "IDLE"
        self.pending_dir = 0
        self.trigger_level = 0.0
        self.entry_lane = ""

    # ──────────────────────────────────────────────────────────────────────
    # 出场管理（Phase-1 硬不变量）
    # 1) 持仓时任何时段都必须检查止损
    # 2) 同 bar 止损与目标同时触发，只允许止损单
    # 3) 半仓必须真实按指定 volume 平仓
    # 4) 平仓单未成交前，不清空止损保护、不重复下全平单
    # 状态拆分：stop_price / stop_source / pending_exit_order / remaining_position
    # ──────────────────────────────────────────────────────────────────────
    _EXIT_REPLACE_KINDS = frozenset({"STOP", "EOD", "TF_COUNTER"})

    def _reset_exit_state(self) -> None:
        self.stop_price = 0.0
        self.stop_source = ""
        self.pending_exit_order = None
        self.remaining_position = 0
        self.last_exit_reason = ""

    def _set_stop(self, price: float, source: str, *, force_source: bool = False) -> None:
        if price <= 0:
            return
        prev = float(self.stop_price or 0.0)
        if price != prev or force_source:
            self.stop_source = source
        self.stop_price = float(price)

    def _tighten_stop_long(self, new_stop: float, source: str) -> None:
        if new_stop <= 0:
            return
        prev = float(self.stop_price or 0.0)
        tightened = max(prev, new_stop) if prev > 0 else new_stop
        if tightened != prev:
            self._set_stop(tightened, source)
        else:
            self.stop_price = tightened

    def _tighten_stop_short(self, new_stop: float, source: str) -> None:
        if new_stop <= 0:
            return
        prev = float(self.stop_price or 0.0)
        tightened = min(prev, new_stop) if prev > 0 else new_stop
        if tightened != prev:
            self._set_stop(tightened, source)
        else:
            self.stop_price = tightened

    def _submit_exit(
        self,
        price: float,
        volume: int,
        *,
        reason: str,
        kind: str,
        allow_replace: bool = False,
    ) -> bool:
        """提交平仓；未成交前保留 stop_price，禁止无授权的重复全平。"""
        pos = int(self.pos)
        if pos == 0:
            return False
        close_vol = min(int(volume), abs(pos))
        if close_vol <= 0:
            return False
        is_full = close_vol >= abs(pos)
        pend = self.pending_exit_order

        if pend is not None:
            same_full = bool(pend.get("is_full")) and is_full
            same_order = (
                int(pend.get("volume", 0)) == close_vol
                and str(pend.get("reason", "")) == reason
                and str(pend.get("kind", "")) == kind
            )
            if same_order:
                return False
            if same_full and not allow_replace and kind not in self._EXIT_REPLACE_KINDS:
                return False
            if not allow_replace and kind not in self._EXIT_REPLACE_KINDS:
                return False
            # 允许升级（STOP/EOD/TF）：撤挂单后重挂；止损价仍保留至成交
            self.cancel_all()

        if pos > 0:
            self.sell(price, close_vol)
            self.remaining_position = pos - close_vol
        else:
            self.cover(price, close_vol)
            self.remaining_position = pos + close_vol

        self.pending_exit_order = {
            "kind": kind,
            "reason": reason,
            "volume": close_vol,
            "price": float(price),
            "is_full": is_full,
            "side": "LONG" if pos > 0 else "SHORT",
        }
        self.last_exit_reason = reason
        # 硬不变量 4：未成交前不清空 stop_price / stop_source
        return True

    def _close_long_position(
        self, price, *, volume: int | None = None, exit_reason: str = "",
        kind: str = "MANUAL", allow_replace: bool = False,
    ) -> bool:
        if self.pos <= 0:
            return False
        close_vol = abs(int(self.pos)) if volume is None else int(volume)
        return self._submit_exit(
            price, close_vol,
            reason=exit_reason or "CLOSE_LONG",
            kind=kind,
            allow_replace=allow_replace,
        )

    def _close_short_position(
        self, price, *, volume: int | None = None, exit_reason: str = "",
        kind: str = "MANUAL", allow_replace: bool = False,
    ) -> bool:
        if self.pos >= 0:
            return False
        close_vol = abs(int(self.pos)) if volume is None else int(volume)
        return self._submit_exit(
            price, close_vol,
            reason=exit_reason or "CLOSE_SHORT",
            kind=kind,
            allow_replace=allow_replace,
        )

    def _manage_stop_loss(self, bar: BarData) -> bool:
        """1m 级逻辑止损：跳空用 min(open, stop) / max(open, stop)（§2.1）。"""
        if self.stop_price <= 0 or self.pos == 0:
            return False
        pend = self.pending_exit_order
        if pend and pend.get("is_full") and pend.get("kind") == "STOP":
            return True  # 止损全平已在途：挡掉同 bar 目标单
        reason = self.stop_source or "STOP_LOSS"
        if self.pos > 0 and bar.low_price <= self.stop_price:
            exec_price = min(bar.open_price, self.stop_price)
            if self._submit_exit(
                    exec_price, abs(int(self.pos)),
                    reason=reason, kind="STOP", allow_replace=True):
                self.write_log(f"【逻辑止损】多头防线触发 @ {exec_price} ({reason})")
                return True
        elif self.pos < 0 and bar.high_price >= self.stop_price:
            exec_price = max(bar.open_price, self.stop_price)
            if self._submit_exit(
                    exec_price, abs(int(self.pos)),
                    reason=reason, kind="STOP", allow_replace=True):
                self.write_log(f"【逻辑止损】空头防线触发 @ {exec_price} ({reason})")
                return True
        return False

    def _manage_mm_targets(self, bar: BarData) -> None:
        """1m 级 Measured Move 止盈：0.5 目标位按 volume 平半仓 + 完全目标位 runner 减仓。"""
        if self.pos == 0 or self.entry_price <= 0 or not self.mm_half_close_enabled:
            return
        # 有未成交平仓单时不做目标单（硬不变量 2/4：止损优先、不叠单）
        if self.pending_exit_order is not None:
            return
        if self.pos > 0:
            if self.mm_target_price <= self.entry_price:
                return
            half_target = (self.entry_price + self.mm_target_price) / 2.0
            if (not self.mm_half_closed and bar.high_price >= half_target
                    and self.volume_capable_half_close()):
                half_vol = abs(int(self.pos)) // 2
                if half_vol > 0 and self._submit_exit(
                        max(half_target, bar.open_price), half_vol,
                        reason="MM_HALF", kind="MM"):
                    self.mm_half_closed = True
                    return
            if not self.mm_target_scaled and self.pos > 0 and bar.high_price >= self.mm_target_price:
                close_vol, runner_vol = self._calc_mm_runner_exit_volumes()
                exec_price = max(bar.open_price, self.mm_target_price)
                if runner_vol > 0 and close_vol > 0 and self._mm_runner_allowed():
                    if self._submit_exit(
                            exec_price, close_vol,
                            reason="MM_RUNNER_START", kind="MM"):
                        self.mm_target_scaled = True
                        self.mm_runner_active = True
                else:
                    self._submit_exit(
                        exec_price, abs(int(self.pos)),
                        reason="MM_TARGET_FULL", kind="MM")
            return
        # pos < 0
        if not (0 < self.mm_target_price < self.entry_price):
            return
        half_target = (self.entry_price + self.mm_target_price) / 2.0
        if (not self.mm_half_closed and bar.low_price <= half_target
                and self.volume_capable_half_close()):
            half_vol = abs(int(self.pos)) // 2
            if half_vol > 0 and self._submit_exit(
                    min(half_target, bar.open_price), half_vol,
                    reason="MM_HALF", kind="MM"):
                self.mm_half_closed = True
                return
        if not self.mm_target_scaled and self.pos < 0 and bar.low_price <= self.mm_target_price:
            close_vol, runner_vol = self._calc_mm_runner_exit_volumes()
            exec_price = min(bar.open_price, self.mm_target_price)
            if runner_vol > 0 and close_vol > 0 and self._mm_runner_allowed():
                if self._submit_exit(
                        exec_price, close_vol,
                        reason="MM_RUNNER_START", kind="MM"):
                    self.mm_target_scaled = True
                    self.mm_runner_active = True
            else:
                self._submit_exit(
                    exec_price, abs(int(self.pos)),
                    reason="MM_TARGET_FULL", kind="MM")

    def volume_capable_half_close(self) -> bool:
        return abs(int(self.pos)) >= 2

    def _calc_mm_runner_exit_volumes(self) -> tuple[int, int]:
        current = abs(int(self.pos))
        if current <= 0 or not self.mm_runner_enabled:
            return current, 0
        entry = int(self.mm_entry_volume) or current
        if entry <= 1:
            return current, 0
        runner_vol = min(max(1, entry // 3), current)
        if runner_vol <= 0 or runner_vol >= current:
            return current, 0
        return current - runner_vol, runner_vol

    def _apply_chandelier_stop_long(self, atr_5, *, reason: str = "CHANDELIER_STOP") -> None:
        self.profit_protect_active = True
        self._tighten_stop_long(
            self.highest_high_since_entry - self.chandelier_multiplier * atr_5,
            reason,
        )

    def _apply_chandelier_stop_short(self, atr_5, *, reason: str = "CHANDELIER_STOP") -> None:
        self.profit_protect_active = True
        self._tighten_stop_short(
            self.lowest_low_since_entry + self.chandelier_multiplier * atr_5,
            reason,
        )

    def _update_position_risk(self, bar, atr_5, stop_buffer) -> None:
        """快车道闪电防线 / 慢车道变频风控（5m on_5min_bar 调用）。"""
        if self.pos == 0 or self.entry_price <= 0:
            return
        self.bars_since_entry += 1
        if self.highest_high_since_entry <= 0:
            self.highest_high_since_entry = self.entry_price
        if self.lowest_low_since_entry <= 0:
            self.lowest_low_since_entry = self.entry_price
        self.highest_high_since_entry = max(self.highest_high_since_entry, bar.high_price)
        self.lowest_low_since_entry = min(self.lowest_low_since_entry, bar.low_price)
        current_time = bar.datetime.time()
        prev_low = float(self.am_5min.low[-2])
        prev_high = float(self.am_5min.high[-2])
        is_long = self.pos > 0
        floating_profit = (bar.close_price - self.entry_price) if is_long else (self.entry_price - bar.close_price)
        # Breakeven
        if not self.breakeven_locked and floating_profit > self._get_breakeven_trigger_atr_mult() * atr_5:
            if is_long:
                self._tighten_stop_long(self.entry_price, "BREAKEVEN")
            else:
                self._tighten_stop_short(self.entry_price, "BREAKEVEN")
            self.breakeven_locked = True
        if self.mm_runner_active:
            if is_long:
                self._apply_chandelier_stop_long(atr_5, reason="CHANDELIER_RUNNER")
            else:
                self._apply_chandelier_stop_short(atr_5, reason="CHANDELIER_RUNNER")
        elif self._is_fast_lane_setup():
            invalid_breach = (self.bars_since_entry <= 2 and self.signal_bar_invalid_line > 0
                               and (bar.close_price < self.signal_bar_invalid_line if is_long
                                    else bar.close_price > self.signal_bar_invalid_line))
            if invalid_breach:
                if is_long:
                    self._tighten_stop_long(self.signal_bar_invalid_line, "SIGNAL_BAR_INVALID")
                else:
                    self._tighten_stop_short(self.signal_bar_invalid_line, "SIGNAL_BAR_INVALID")
            else:
                trail = bar.low_price - stop_buffer if is_long else bar.high_price + stop_buffer
                if is_long:
                    self._tighten_stop_long(trail, "FAST_LANE_TRAIL")
                else:
                    self._tighten_stop_short(trail, "FAST_LANE_TRAIL")
        else:
            # 慢车道
            if self._profit_protect_allowed() and current_time >= time(14, 40):
                self.profit_protect_active = True
                ref = prev_low if is_long else prev_high
                if is_long:
                    self._tighten_stop_long(ref, "PROFIT_PROTECT_1440")
                else:
                    self._tighten_stop_short(ref, "PROFIT_PROTECT_1440")
            elif (self.bars_since_entry <= self.follow_through_bars
                    and self.signal_bar_invalid_line > 0
                    and (bar.close_price < self.signal_bar_invalid_line if is_long
                         else bar.close_price > self.signal_bar_invalid_line)):
                if is_long:
                    self._tighten_stop_long(self.signal_bar_invalid_line, "SIGNAL_BAR_INVALID")
                else:
                    self._tighten_stop_short(self.signal_bar_invalid_line, "SIGNAL_BAR_INVALID")
            elif floating_profit > self.trailing_active_multiplier * atr_5:
                cfg = self._active_exit_family_config()
                chandelier_ok = cfg.enable_chandelier_trail if cfg is not None else True
                if chandelier_ok:
                    if is_long:
                        self._apply_chandelier_stop_long(atr_5)
                    else:
                        self._apply_chandelier_stop_short(atr_5)

    # ──────────────────────────────────────────────────────────────────────
    # Brooks 定仓 + MM 目标
    # ──────────────────────────────────────────────────────────────────────
    def _calc_measured_move_target(self, direction, entry_price, signal_bar, atr_5) -> float:
        tick = self.get_pricetick()
        leg1 = self.last_leg1_amplitude
        if leg1 <= 0 and self.mm_swing_high > self.mm_swing_low > 0:
            leg1 = self.mm_swing_high - self.mm_swing_low
        if leg1 > 0:
            base_move = leg1
        else:
            base_move = atr_5 * self.mm_atr_mult
            if signal_bar is not None:
                sb_range = float(signal_bar.high_price) - float(signal_bar.low_price)
                if sb_range > 0:
                    base_move = max(base_move, sb_range * 2.0)
        if base_move < tick * 2:
            base_move = tick * 2
        tgt = entry_price + base_move if direction > 0 else entry_price - base_move
        mult = float(getattr(self, "_dual_core_target_mult", 1.0) or 1.0)
        if mult < 0.999 and abs(tgt - entry_price) > 0:
            move = abs(tgt - entry_price) * mult
            tgt = entry_price + move if direction > 0 else entry_price - move
        return tgt

    def _calc_brooks_volume(self, high_price, low_price, *, atr_5=None, max_position_cap=None) -> int:
        """Brooks 恒定风险金定仓；超额风险熔断时拒单。F2: Regime-weighted sizing。"""
        risk_span = high_price - low_price
        if risk_span <= 0:
            return 0
        if atr_5 is None and self.am_5min.inited:
            atr_5 = float(self.am_5min.atr(self.atr_window))
        if atr_5 is not None and atr_5 > 0 and risk_span > atr_5 * self.entry_risk_fuse_atr_mult:
            return 0
        risk_per_contract = risk_span * self.contract_size
        equity_risk = self._get_capital() * self.risk_pct_per_trade
        risk_money = min(float(self.risk_capital), equity_risk) if self.risk_capital > 0 else equity_risk
        risk_money *= self._get_setup_risk_mult()
        aff_mult = self._get_aff_risk_mult()
        if aff_mult <= 0:
            return 0
        risk_money *= aff_mult
        risk_money *= self._get_symbol_liquidity_risk_mult()
        dc_mult = float(getattr(self, "_dual_core_size_mult", 1.0) or 1.0)
        if getattr(self, "dual_core_soft_enabled", False):
            risk_money *= max(dc_mult, 0.0)
        atr_5_rt = float(self.am_5min.atr(self.atr_window)) if self.am_5min.inited else 0.0
        atr_15_rt = float(self.am_15min.atr(self.atr_window)) if self.am_15min.inited else 0.0
        atr_ratio = round(atr_5_rt / atr_15_rt, 3) if atr_15_rt > 0 and atr_5_rt > 0 else 0.0
        if self.atr_regime_min <= atr_ratio < 0.70:
            sizing_factor = 1.5
        elif 0.70 <= atr_ratio < self.atr_regime_max:
            sizing_factor = 1.0
        else:
            sizing_factor = 0.0
        if sizing_factor <= 0:
            return 0
        volume = int(risk_money * sizing_factor / risk_per_contract)
        if volume < 1:
            return 0
        pos_cap = self.max_position if max_position_cap is None else min(max_position_cap, self.max_position)
        return min(volume, pos_cap)

    def _get_capital(self) -> float:
        if self.use_compound_capital:
            return max(self._initial_capital + self._realized_pnl, 1.0)
        engine = self.cta_engine
        for attr in ("capital", "balance"):
            val = getattr(engine, attr, None)
            if val is not None and float(val) > 0:
                return float(val)
        return max(float(self.capital), 1.0)
