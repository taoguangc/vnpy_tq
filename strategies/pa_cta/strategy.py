# -*- coding: utf-8 -*-
"""
BrooksPaCtaStrategy — Al Brooks 价格行为（PA）深度精简版。

基于 pa_strategy.py v0.9.75 的 OPP 绩效统计精简而来：仅保留 rb888 3 年回测中
净盈利最高的 Top 8 OPP，删除全部 Mixin、诊断/审计代码与低盈利 OPP。
VWAP Dual Core 门禁 + Brooks 恒定风险金定仓 + MM/Chandelier/Breakeven 出场均保留。

保留 OPP（按净盈利排序）：
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
    from .bar_patterns import (
        BarMetrics,
        PatternThresholds,
        classify_bar_shape,
        is_bear_reversal as bp_is_bear_reversal,
        is_boundary_bear_reversal,
        is_boundary_bull_reversal,
        is_bull_reversal as bp_is_bull_reversal,
        is_outside_outside,
        is_quality_day_high_short,
        is_strong_bar as bp_is_strong_bar,
    )
    from .opp_tf import is_opposite_direction, should_upgrade_arm
    from .vsa import VsaFilterMixin
    from .wedge import WedgeBar, scan_latest_bearish_wedge, scan_latest_bullish_wedge
except (ModuleNotFoundError, ImportError):
    from strategies.pa_cta.aff_gate import compute_aff_snapshot
    from strategies.pa_cta.aff_router import classify_aff_archetype, setup_allowed_for_archetype
    from strategies.pa_cta.symbol_adaptive import (
        parse_prefix_list, runtime_liquidity_risk_mult, static_liquidity_risk_mult,
    )
    from strategies.pa_cta.regime_gate import compute_chop_index, compute_trend_r2
    from strategies.pa_cta.bar_patterns import (
        BarMetrics,
        PatternThresholds,
        classify_bar_shape,
        is_bear_reversal as bp_is_bear_reversal,
        is_boundary_bear_reversal,
        is_boundary_bull_reversal,
        is_bull_reversal as bp_is_bull_reversal,
        is_outside_outside,
        is_quality_day_high_short,
        is_strong_bar as bp_is_strong_bar,
    )
    from strategies.pa_cta.opp_tf import is_opposite_direction, should_upgrade_arm
    from strategies.pa_cta.vsa import VsaFilterMixin
    from strategies.pa_cta.wedge import (
        WedgeBar,
        scan_latest_bearish_wedge,
        scan_latest_bullish_wedge,
    )


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


class BrooksPaCtaStrategy(VsaFilterMixin, CtaTemplate):
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
    # 趋势寿命
    trend_late_counter_threshold = 3
    trend_late_atr_shrink_ratio = 0.7
    # VWAP Dual Core
    dual_core_enabled = True
    vwap_regime_lookback = 30
    vwap_chop_min_crosses = 4
    vwap_slope_thresh_ticks = 2
    vwap_trend_deadband_ticks = 4
    vwap_fade_max_atr = 1.2
    # VSA 开仓熔断（与 pa 旗舰同源 VsaFilterMixin）
    vsa_enabled = True
    vsa_volume_window = 40
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
    signal_stop_loss = 0.0
    entry_price = 0.0
    profit_protect_active = False
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
    _pending_exit_reason = ""
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
        "follow_through_bars", "max_daily_trades", "mm_atr_mult",
        "mm_half_close_enabled", "mm_runner_enabled",
        "trend_late_counter_threshold", "trend_late_atr_shrink_ratio",
        "dual_core_enabled", "vwap_regime_lookback", "vwap_chop_min_crosses",
        "vwap_slope_thresh_ticks", "vwap_trend_deadband_ticks", "vwap_fade_max_atr",
        "vsa_enabled", "vsa_volume_window", "vsa_low_volume_pct",
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
            self._pending_exit_reason = "STOP_LOSS"
            setup = self.active_setup_name or "UNKNOWN"
            self._entry_snapshot = {
                "setup": setup,
                "entry_time": trade.datetime,
                "entry_price": trade.price,
                "market_context": self.market_context,
                "always_in": self.always_in,
                "direction": "多" if trade.direction == Direction.LONG else "空",
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
        elif trade.offset in (Offset.CLOSE, Offset.CLOSETODAY):
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
                            "exit_reason": self._pending_exit_reason or "UNKNOWN",
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
                self._reset_machine()

    def on_stop(self) -> None:
        self._print_vsa_funnel()
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
        if self._is_noise_window(current_time):
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

        if time(14, 55) <= current_time <= time(15, 0):
            self.cancel_all()
            self._reset_machine()
            if self.pos > 0:
                self._close_long_position(bar.close_price, exit_reason="EOD_FLAT")
                self.write_log("【日内清仓】收盘价平多")
            elif self.pos < 0:
                self._close_short_position(bar.close_price, exit_reason="EOD_FLAT")
                self.write_log("【日内清仓】收盘价平空")
            return

        if current_time == time(9, 6) or self.day_high <= 0:
            self.day_high = bar.high_price
            self.day_low = bar.low_price
        else:
            self.day_high = max(self.day_high, bar.high_price)
            self.day_low = min(self.day_low, bar.low_price)

        if self.pos != 0:
            self._manage_stop_loss(bar)
            self._manage_mm_targets(bar)

        self._update_vwap(bar)
        self._update_vwap_regime(bar)
        self.bg_5.update_bar(bar)

    # ──────────────────────────────────────────────────────────────────────
    # on_5min_bar — 5m 信号引擎
    # ──────────────────────────────────────────────────────────────────────
    def on_5min_bar(self, bar: BarData) -> None:
        """5 分钟核心信号引擎：ATR regime gate + Top 8 OPP 入场。"""
        self.bg_15.update_bar(bar)
        self.am_5min.update_bar(bar)
        if not self.am_5min.inited:
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

        # ── 全局硬过滤 ──
        if not self.entry_window_open:
            self._reset_machine()
            return
        if atr_5 < self._min_atr_for_context(effective_context):
            self._reset_machine()
            return
        if self.pos != 0:
            return
        if not allow_new_entry:
            self._reset_machine()
            return
        if self.daily_trade_count >= self.max_daily_trades:
            return

        # ── OPP15 Wedge trigger + arm ──
        if self._process_wedge_trigger_phase(bar, atr_5, tick, is_strong_bar=is_strong_bar):
            return
        if (not self.wedge_setup_active and self.machine_state == "IDLE" and not is_oo):
            self._try_arm_wedge_setup(bar, atr_5, tick)

        boundary_tol = self.day_boundary_tolerance * tick
        day_high_touch_tol = self.day_high_second_test_ticks * tick
        lh_max_drop = self.day_high_lh_max_ticks * tick
        is_long_climax = (bar.close_price - ema_20) > (self.long_climax_atr_mult * atr_5)
        is_short_climax = (ema_20 - bar.close_price) > (self.long_climax_atr_mult * atr_5)

        # ── Context 路由 ──
        if effective_context == "STRONG_BULL":
            if (bar.close_price > ema_20 and is_strong_bar
                    and bar.close_price > bar.open_price
                    and bar.close_price > prev_high and not is_long_climax):
                self._arm_fast_track(
                    direction=1, opportunity="OPP08_5M_STRONG_BREAKOUT_LONG",
                    trigger=bar.high_price + tick,
                    stop=self._cap_long_stop(bar.low_price - stop_buffer, bar.close_price, atr_5),
                )
                return
        elif effective_context == "STRONG_BEAR":
            if (bar.close_price < ema_20 and is_strong_bar
                    and bar.close_price < bar.open_price):
                self._arm_fast_track(
                    direction=-1, opportunity="OPP08_5M_STRONG_BREAKOUT_SHORT",
                    trigger=bar.low_price - tick,
                    stop=self._cap_short_stop(bar.high_price + stop_buffer, bar.close_price, atr_5),
                )
                return
        elif effective_context == "BULL_CHANNEL":
            self._try_overshoot_fail(bar, atr_5, tick, stop_buffer, bar_range, ema_20,
                                     is_bull_reversal, is_bear_reversal, is_oo)
            if self.machine_state != "IDLE":
                return
        elif effective_context == "BEAR_CHANNEL":
            if (self.machine_state == "IDLE" and not is_oo and is_strong_bar
                    and bar_range > atr_5 * 1.5 and not is_short_climax
                    and bar.close_price < bar.open_price
                    and bar.low_price < recent_5bar_low
                    and bar.close_price < ema_20):
                self._arm_fast_track(
                    direction=-1, opportunity="OPP08_5M_STRONG_BREAKOUT_SHORT",
                    trigger=bar.low_price - tick,
                    stop=self._cap_short_stop(bar.high_price + stop_buffer, bar.close_price, atr_5),
                )
                return
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
        self._update_mtf_wedge_exhaustion_zone(atr_15)
        self._update_always_in_state(closes, ema_15, bar, self.get_pricetick(), atr_15)
        self._update_aff_state()
        self._update_trend_regime_state()

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
            self._close_long_position(bar.close_price, exit_reason=reason)
        else:
            self._close_short_position(bar.close_price, exit_reason=reason)
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
        for prefix in self._parse_disabled_setups(self.disabled_setups):
            if opp.startswith(prefix):
                return True
        return False

    def _arm_fast_track(self, *, direction, opportunity, trigger, stop, invalid_line=0.0) -> None:
        if self._setup_disabled(opportunity):
            return
        if self._aff_archetype_blocks_entry(opportunity):
            self._aff_archetype_block_count += 1
            return
        if self._late_phase_blocks_entry(
                direction, self.market_context, opportunity):
            self._late_phase_block_count += 1
            return
        if self._aff_blocks_entry():
            self._aff_block_count += 1
            return
        lane = self._setup_entry_lane(opportunity)
        if not self._dual_core_allows_entry(direction, lane):
            return
        if self._vsa_blocks_entry(direction):
            return
        if not self._opp_tf_arm_gate(direction, opportunity):
            return
        self.machine_state = "FAST_TRACK_ARMED"
        self.pending_dir = direction
        self.active_setup_name = opportunity
        self.trigger_level = trigger
        self.signal_stop_loss = stop
        self.signal_bar_invalid_line = invalid_line or stop
        self.entry_lane = "FAST_TRACK"

    def _arm_pending_confirm(self, *, direction, opportunity, trigger, stop, invalid_line=0.0) -> None:
        if self._setup_disabled(opportunity):
            return
        if self._aff_archetype_blocks_entry(opportunity):
            self._aff_archetype_block_count += 1
            return
        if self._late_phase_blocks_entry(
                direction, self.market_context, opportunity):
            self._late_phase_block_count += 1
            return
        if self._aff_blocks_entry():
            self._aff_block_count += 1
            return
        lane = self._setup_entry_lane(opportunity)
        if not self._dual_core_allows_entry(direction, lane):
            return
        if self._vsa_blocks_entry(direction):
            return
        if not self._opp_tf_arm_gate(direction, opportunity):
            return
        self.machine_state = "PENDING_CONFIRM"
        self.pending_dir = direction
        self.active_setup_name = opportunity
        self.trigger_level = trigger
        self.signal_stop_loss = stop
        self.signal_bar_invalid_line = invalid_line or trigger
        self.entry_lane = "PENDING_CONFIRM"

    def _arm_opp13_pending(
        self, bar, *, direction, opportunity, trigger, stop, invalid_line=0.0,
    ) -> None:
        """OPP13 专用 arm：叠加量能筛选后再走 PENDING_CONFIRM。"""
        if not self._opp13_volume_allows_entry(bar, direction):
            self._opp13_vol_block_count += 1
            return
        self._arm_pending_confirm(
            direction=direction,
            opportunity=opportunity,
            trigger=trigger,
            stop=stop,
            invalid_line=invalid_line,
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
                        self.entry_price, self.signal_stop_loss, atr_5=atr_5,
                        max_position_cap=self.max_position)
                    if volume > 0:
                        self.profit_protect_active = False
                        self.buy(self.entry_price, volume)
                        filled = True
                else:
                    volume = self._calc_brooks_volume(
                        self.signal_stop_loss, self.entry_price, atr_5=atr_5,
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
                    self.trigger_level, self.signal_stop_loss, atr_5=atr_5)
                if volume > 0:
                    self.profit_protect_active = False
                    self.buy(self.trigger_level, volume, stop=True)
            else:
                volume = self._calc_brooks_volume(
                    self.signal_stop_loss, self.trigger_level, atr_5=atr_5)
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
        return self.entry_lane == "FAST_TRACK"

    def _get_breakeven_trigger_atr_mult(self) -> float:
        setup = self.active_setup_name or ""
        if setup.startswith(_BREAKEVEN_FAST_SETUPS):
            return self.breakeven_trigger_atr_mult_fast
        return self.breakeven_trigger_atr_mult_slow

    def _get_setup_risk_mult(self) -> float:
        """按 active_setup_name 查表缩放单笔 risk_money（仅定仓，不改信号）。"""
        if not self.setup_risk_mult_enabled:
            return 1.0
        setup = self.active_setup_name or ""
        if not setup:
            return self.setup_risk_mult_default
        return _SETUP_RISK_MULT.get(setup, self.setup_risk_mult_default)

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

    def _reset_day_high_test(self) -> None:
        self.day_high_test_state = "IDLE"
        self.day_high_test_bar_count = 0
        self.first_test_high = 0.0

    def _reset_wedge_setup(self) -> None:
        self.wedge_setup_active = False
        self.wedge_confirmed_p3_high = 0.0
        self.wedge_trigger_line = 0.0
        self.wedge_arm_time = None
        self.wedge_current_alpha = 0.0
        self.wedge_p3_body_floor = 0.0
        self._wedge_direction = 0

    def _reset_opening_drive(self) -> None:
        self._od_state = "IDLE"
        self._od_high = 0.0
        self._od_low = 0.0
        self._od_bars_collected = 0
        self._od_session_date = None
        self._od_bar1_shape = ""
        self._od_bar1_mid = 0.0
        self._od_bar1_range = 0.0

    # ──────────────────────────────────────────────────────────────────────
    # OPP12 超调衰竭（BULL/BEAR_CHANNEL 共用）
    # ──────────────────────────────────────────────────────────────────────
    def _try_overshoot_fail(self, bar, atr_5, tick, stop_buffer, bar_range, ema_20,
                            is_bull_reversal, is_bear_reversal, is_oo) -> None:
        if is_oo:
            return
        overshoot_depth = ema_20 - bar.close_price
        if (atr_5 * self.overshoot_atr_mult <= overshoot_depth <= atr_5 * self.overshoot_max_atr_mult
                and is_bull_reversal and bar.close_price > bar.open_price
                and not self._pd_blocks_long_target(bar.close_price, atr_5)):
            self._arm_pending_confirm(
                direction=1, opportunity="OPP12_5M_OVERSHOOT_FAIL_LONG",
                trigger=bar.high_price,
                stop=self._cap_long_stop(bar.low_price - tick, bar.close_price, atr_5),
                invalid_line=bar.low_price)
            return
        if (bar.close_price > ema_20 + atr_5 * self.overshoot_atr_mult
                and is_bear_reversal
                and not self._pd_blocks_short_target(bar.close_price, atr_5)):
            self._arm_pending_confirm(
                direction=-1, opportunity="OPP12_5M_OVERSHOOT_FAIL_SHORT",
                trigger=bar.low_price,
                stop=self._cap_short_stop(bar.high_price + tick, bar.close_price, atr_5),
                invalid_line=bar.high_price)

    # ──────────────────────────────────────────────────────────────────────
    # OPP13 日边界反转（WIDE_RANGE: 日高/日低单触 + 日高双顶）
    # ──────────────────────────────────────────────────────────────────────
    def _try_day_boundary_reversal(
        self, bar, atr_5, tick, bar_range, upper_shadow, lower_shadow,
        is_boundary_bull, is_boundary_bear, boundary_tol, is_oo,
    ) -> bool:
        if is_oo:
            return False
        # Path A: 日高单触空
        if abs(bar.high_price - self.day_high) <= boundary_tol and is_boundary_bear:
            if (bar.close_price < bar.open_price and upper_shadow >= bar_range * 0.4
                    and not self._pd_blocks_short_target(bar.close_price, atr_5)):
                if (self.always_in == "LONG"
                        and self.market_context not in ("WIDE_RANGE",)):
                    return True
                if self._late_phase_blocks_entry(
                        -1, self.market_context, "OPP13_5M_RANGE_FAIL_HIGH"):
                    self._late_phase_block_count += 1
                    return True
                bulldozer_pulse = False
                if self.am_5min.count >= 4:
                    p1r = float(self.am_5min.high[-2]) - float(self.am_5min.low[-2])
                    p2r = float(self.am_5min.high[-3]) - float(self.am_5min.low[-3])
                    p1s = (float(self.am_5min.close[-2]) - float(self.am_5min.open[-2])) > p1r * 0.5
                    p2s = (float(self.am_5min.close[-3]) - float(self.am_5min.open[-3])) > p2r * 0.5
                    bulldozer_pulse = p1s and p2s
                if not bulldozer_pulse:
                    self._arm_opp13_pending(
                        bar,
                        direction=-1, opportunity="OPP13_5M_RANGE_FAIL_HIGH",
                        trigger=bar.low_price, stop=bar.high_price + tick,
                        invalid_line=bar.high_price)
                return True
        # Path A: 日低单触多
        if abs(bar.low_price - self.day_low) <= boundary_tol and is_boundary_bull:
            if (bar.close_price > bar.open_price and lower_shadow >= bar_range * 0.4
                    and not self._pd_blocks_long_target(bar.close_price, atr_5)
                    and self.always_in != "SHORT"):
                if self._late_phase_blocks_entry(
                        1, self.market_context, "OPP13_5M_RANGE_FAIL_LOW"):
                    self._late_phase_block_count += 1
                    return True
                bearish_pulse = False
                if self.am_5min.count >= 4:
                    p1r = float(self.am_5min.high[-2]) - float(self.am_5min.low[-2])
                    p2r = float(self.am_5min.high[-3]) - float(self.am_5min.low[-3])
                    p1b = (float(self.am_5min.open[-2]) - float(self.am_5min.close[-2])) > p1r * 0.5
                    p2b = (float(self.am_5min.open[-3]) - float(self.am_5min.close[-3])) > p2r * 0.5
                    bearish_pulse = p1b and p2b
                if not bearish_pulse:
                    self._arm_opp13_pending(
                        bar,
                        direction=1, opportunity="OPP13_5M_RANGE_FAIL_LOW",
                        trigger=bar.high_price, stop=bar.low_price - tick,
                        invalid_line=bar.low_price)
                return True
        return False

    def _try_day_high_double_top(
        self, bar, atr_5, tick, bar_range, upper_shadow, is_boundary_bear,
        effective_context, day_high_touch_tol, lh_max_drop,
    ) -> bool:
        if self.day_high_test_state == "FIRST_TEST":
            self.day_high_test_bar_count += 1
            if self.day_high_test_bar_count > self.day_high_second_test_max_bars:
                self._reset_day_high_test()
        # 首次触达日高 → FIRST_TEST
        if (self.day_high_test_state == "IDLE" and self.machine_state == "IDLE"
                and abs(bar.high_price - self.day_high) <= day_high_touch_tol
                and is_quality_day_high_short(
                    BarMetrics.from_bar(bar), bar_range, is_boundary_bear)):
            self.day_high_test_state = "FIRST_TEST"
            self.first_test_high = bar.high_price
            self.day_high_test_bar_count = 0
            return True
        # 二次测试（LH）+ 质量空棒 → 入场
        if self.day_high_test_state == "FIRST_TEST":
            lh_ok = (self.day_high_test_bar_count <= self.day_high_second_test_max_bars
                     and self.first_test_high > 0
                     and bar.high_price <= self.first_test_high
                     and bar.high_price >= self.first_test_high - lh_max_drop)
            if lh_ok and is_quality_day_high_short(
                    BarMetrics.from_bar(bar), bar_range, is_boundary_bear):
                if effective_context in ("STRONG_BEAR", "BEAR_CHANNEL", "WIDE_RANGE"):
                    if not (self.always_in == "LONG" and effective_context != "WIDE_RANGE"):
                        if not (self.trend_phase == "LATE" and self.trend_direction == -1
                                and effective_context != "WIDE_RANGE"):
                            if not self._pd_blocks_short_target(bar.close_price, atr_5):
                                self._arm_opp13_pending(
                                    bar,
                                    direction=-1, opportunity="OPP13_5M_RANGE_FAIL_HIGH",
                                    trigger=bar.low_price, stop=bar.high_price + tick,
                                    invalid_line=bar.high_price)
                self._reset_day_high_test()
                return True
        return False

    # ──────────────────────────────────────────────────────────────────────
    # OPP16 Two-Bar Reversal
    # ──────────────────────────────────────────────────────────────────────
    def _process_two_bar_reversal(
        self, bar, effective_context, atr_5, tick, stop_buffer, bar_range, body,
    ) -> bool:
        if bar_range <= tick or self.am_5min.count < 2:
            return False
        allowed_ctx = {s.strip() for s in self.two_bar_rev_context.split(",") if s.strip()}
        if effective_context not in allowed_ctx:
            return False
        prev_close = float(self.am_5min.close[-2])
        prev_open = float(self.am_5min.open[-2])
        prev_high = float(self.am_5min.high[-2])
        prev_low = float(self.am_5min.low[-2])
        prev_range = prev_high - prev_low
        if prev_range <= 0:
            return False
        prev_body_ratio = abs(prev_close - prev_open) / prev_range
        prev_mid = (prev_high + prev_low) / 2.0
        prev_shape = self.prev_bar_shape or ""
        is_strong_trend_bar = (
            prev_body_ratio >= self.two_bar_rev_body_ratio
            and prev_shape in ("UP_TREND", "DOWN_TREND", "OUTSIDE_UP", "OUTSIDE_DOWN"))
        if not is_strong_trend_bar and prev_body_ratio < self.two_bar_rev_body_ratio:
            return False
        # A: 空头趋势棒 → 后棒越过中点向上 → 做多
        if prev_close < prev_open and bar.close_price > prev_mid:
            stop = self._cap_long_stop(bar.low_price - stop_buffer, bar.close_price, atr_5)
            self._arm_pending_confirm(
                direction=1, opportunity="OPP16_5M_TWO_BAR_REV_LONG",
                trigger=bar.high_price + tick, stop=stop, invalid_line=bar.low_price)
            return True
        # B: 多头趋势棒 → 后棒越过中点向下 → 做空
        if prev_close > prev_open and bar.close_price < prev_mid:
            stop = self._cap_short_stop(bar.high_price + stop_buffer, bar.close_price, atr_5)
            self._arm_pending_confirm(
                direction=-1, opportunity="OPP16_5M_TWO_BAR_REV_SHORT",
                trigger=bar.low_price - tick, stop=stop, invalid_line=bar.high_price)
            return True
        return False

    # ──────────────────────────────────────────────────────────────────────
    # OPP02 EMA Pullback
    # ──────────────────────────────────────────────────────────────────────
    def _process_ema_pullback(
        self, bar, effective_context, atr_5, tick, stop_buffer, bar_range, body, ema_20, is_oo,
    ) -> bool:
        if is_oo or bar_range <= tick or ema_20 <= 0 or atr_5 <= 0:
            return False
        # EXP-007：15m R² 趋势门禁（替代 Setup AFF 时启用）
        if self.opp02_r2_gate_enabled and self._trend_regime_blocks_continuation(self.opp02_r2_min):
            return False
        if self.opp02_aff_gate_enabled and self._aff_alpha_strength < self.opp02_aff_alpha_min:
            return False
        touch_band = atr_5 * self.ema_pullback_touch_atr
        body_ratio = body / bar_range if bar_range > 0 else 0.0
        if self.always_in == "LONG":
            touched_ema = bar.low_price <= ema_20 + touch_band
            sig_long = (bar.close_price > bar.open_price
                        and body_ratio >= self.ema_pullback_min_body_ratio
                        and bar.high_price - max(bar.open_price, bar.close_price) < bar_range * 0.45)
            if touched_ema and sig_long and not self._pd_blocks_long_target(bar.close_price, atr_5):
                stop = self._cap_long_stop(bar.low_price - stop_buffer, bar.close_price, atr_5)
                self._arm_pending_confirm(
                    direction=1, opportunity="OPP02_5M_EMA_PULLBACK_LONG",
                    trigger=bar.high_price + tick, stop=stop, invalid_line=bar.low_price)
                return True
        if self.always_in == "SHORT":
            touched_ema = bar.high_price >= ema_20 - touch_band
            sig_short = (bar.close_price < bar.open_price
                         and body_ratio >= self.ema_pullback_min_body_ratio
                         and min(bar.open_price, bar.close_price) - bar.low_price < bar_range * 0.45)
            if touched_ema and sig_short and not self._pd_blocks_short_target(bar.close_price, atr_5):
                stop = self._cap_short_stop(bar.high_price + stop_buffer, bar.close_price, atr_5)
                self._arm_pending_confirm(
                    direction=-1, opportunity="OPP02_5M_EMA_PULLBACK_SHORT",
                    trigger=bar.low_price - tick, stop=stop, invalid_line=bar.high_price)
                return True
        return False

    # ──────────────────────────────────────────────────────────────────────
    # OPP17 Climax Reversal
    # ──────────────────────────────────────────────────────────────────────
    def _process_climax_reversal(
        self, bar, effective_context, atr_5, tick, stop_buffer, bar_range, is_oo,
    ) -> bool:
        if is_oo or bar_range <= tick or atr_5 <= 0:
            return False
        allowed_ctx = {s.strip() for s in self.climax_rev_context.split(",") if s.strip()}
        if effective_context not in allowed_ctx:
            return False
        prev_high = float(self.am_5min.high[-2])
        prev_low = float(self.am_5min.low[-2])
        prev_close = float(self.am_5min.close[-2])
        prev_open = float(self.am_5min.open[-2])
        prev_range = prev_high - prev_low
        if prev_range <= 0 or prev_range <= self.climax_rev_range_atr * atr_5:
            return False
        prev_mid = (prev_high + prev_low) / 2.0
        if prev_close < prev_open and bar.close_price > prev_mid:
            stop = self._cap_long_stop(bar.low_price - stop_buffer, bar.close_price, atr_5)
            self._arm_pending_confirm(
                direction=1, opportunity="OPP17_5M_CLIMAX_REV_LONG",
                trigger=bar.high_price + tick, stop=stop, invalid_line=bar.low_price)
            return True
        if prev_close > prev_open and bar.close_price < prev_mid:
            stop = self._cap_short_stop(bar.high_price + stop_buffer, bar.close_price, atr_5)
            self._arm_pending_confirm(
                direction=-1, opportunity="OPP17_5M_CLIMAX_REV_SHORT",
                trigger=bar.low_price - tick, stop=stop, invalid_line=bar.high_price)
            return True
        return False

    # ──────────────────────────────────────────────────────────────────────
    # OPP19 Opening Drive
    # ──────────────────────────────────────────────────────────────────────
    def _opening_drive_breakout_context_ok(
        self, direction: int, effective_context: str
    ) -> bool:
        """OPP19 BREAKOUT context 软禁：逆强势背景不做开盘区间突破。"""
        if direction > 0 and effective_context == "STRONG_BEAR":
            return False
        if direction < 0 and effective_context == "STRONG_BULL":
            return False
        return True

    def _opening_rev_allows_entry(
        self, direction: int, effective_context: str, atr_5: float,
    ) -> bool:
        """OPP19 OD_REV：过滤逆势 always_in、强趋势反向 fade、首棒振幅异常。"""
        if not self.opp19_rev_gate_enabled:
            return True
        if direction > 0:
            if self.opp19_rev_always_in_gate and self.always_in == "SHORT":
                return False
            if (self.opp19_rev_block_strong_counter
                    and effective_context == "STRONG_BEAR"):
                return False
        elif direction < 0:
            if self.opp19_rev_always_in_gate and self.always_in == "LONG":
                return False
            if (self.opp19_rev_block_strong_counter
                    and effective_context == "STRONG_BULL"):
                return False
        if self._od_bar1_range > 0 and atr_5 > 0:
            bar1_atr = self._od_bar1_range / atr_5
            if bar1_atr < self.opp19_rev_min_bar1_range_atr:
                return False
            if bar1_atr > self.opp19_rev_max_bar1_range_atr:
                return False
        allowed = {
            s.strip()
            for s in str(self.opp19_rev_contexts or "").split(",")
            if s.strip()
        }
        if allowed and effective_context not in allowed:
            return False
        return True

    def _opening_rev_in_time_window(
        self, bar_time: time, *, is_morning: bool, is_night: bool,
    ) -> bool:
        """开盘反转仅在 session 前 N 分钟内 arm（防 FAST_TRACK 止损单迟填）。"""
        if is_morning:
            return bar_time <= time(9, int(self.opp19_rev_morning_cutoff_minute))
        if is_night:
            return bar_time <= time(21, int(self.opp19_rev_night_cutoff_minute))
        return False

    def _arm_opening_rev(
        self, bar, *, direction: int, opportunity: str, atr_5: float,
        tick: float, stop_buffer: float, effective_context: str,
    ) -> bool:
        """OD_REV：PENDING_CONFIRM + 门禁 + 时间窗（替代 FAST_TRACK 迟填）。"""
        bar_time = bar.datetime.time()
        is_morning = time(9, 0) <= bar_time <= time(11, 30)
        is_night = time(21, 0) <= bar_time <= time(23, 0)
        if str(self.opp19_rev_arm_mode).upper() != "FAST_TRACK":
            if not self._opening_rev_in_time_window(
                    bar_time, is_morning=is_morning, is_night=is_night):
                return False
        if not self._opening_rev_allows_entry(direction, effective_context, atr_5):
            return False
        if str(self.opp19_rev_arm_mode).upper() == "FAST_TRACK":
            if direction > 0:
                stop = self._cap_long_stop(
                    bar.low_price - stop_buffer, bar.close_price, atr_5)
                self._arm_fast_track(
                    direction=1, opportunity=opportunity,
                    trigger=bar.high_price + tick, stop=stop,
                    invalid_line=bar.low_price)
            else:
                stop = self._cap_short_stop(
                    bar.high_price + stop_buffer, bar.close_price, atr_5)
                self._arm_fast_track(
                    direction=-1, opportunity=opportunity,
                    trigger=bar.low_price - tick, stop=stop,
                    invalid_line=bar.high_price)
        else:
            if direction > 0:
                stop = self._cap_long_stop(
                    bar.low_price - stop_buffer, bar.close_price, atr_5)
                self._arm_pending_confirm(
                    direction=1, opportunity=opportunity,
                    trigger=bar.high_price + tick, stop=stop,
                    invalid_line=bar.low_price)
            else:
                stop = self._cap_short_stop(
                    bar.high_price + stop_buffer, bar.close_price, atr_5)
                self._arm_pending_confirm(
                    direction=-1, opportunity=opportunity,
                    trigger=bar.low_price - tick, stop=stop,
                    invalid_line=bar.high_price)
        self._reset_opening_drive()
        return True

    def _process_opening_drive(
        self, bar, effective_context, atr_5, tick, stop_buffer, bar_range, body,
        is_strong_bar, is_oo,
    ) -> bool:
        if is_oo or bar_range <= tick or atr_5 <= 0:
            return False
        bar_time = bar.datetime.time()
        bar_date = bar.datetime.date()
        is_morning = time(9, 0) <= bar_time <= time(11, 30)
        is_night = time(21, 0) <= bar_time <= time(23, 0)
        if not (is_morning or is_night):
            if self._od_state != "IDLE":
                self._reset_opening_drive()
            return False
        session_changed = bar_date != self._od_session_date
        new_morning = is_morning and bar_time < time(9, 20) and self._od_state == "IDLE"
        new_night = is_night and bar_time < time(21, 20) and self._od_state == "IDLE"
        if session_changed or new_morning or new_night:
            self._reset_opening_drive()
            self._od_state = "COLLECTING"
            self._od_session_date = bar_date
            self._od_high = bar.high_price
            self._od_low = bar.low_price
            self._od_bars_collected = 1
            if self.opening_rev_enabled and bar_range > 0:
                if body / bar_range >= self.opening_rev_body_ratio:
                    if bar.close_price > bar.open_price:
                        self._od_bar1_shape = "UP"
                    elif bar.close_price < bar.open_price:
                        self._od_bar1_shape = "DOWN"
                    if self._od_bar1_shape:
                        self._od_bar1_mid = (bar.high_price + bar.low_price) / 2.0
                        self._od_bar1_range = bar_range
            return False
        if self._od_state == "IDLE":
            return False
        # COLLECTING
        if self._od_state == "COLLECTING":
            # Path B: Opening Reversal
            if (self.opening_rev_enabled and self.machine_state == "IDLE"
                    and self._od_bars_collected <= 2 and self._od_bar1_shape):
                body_ratio = body / bar_range if bar_range > 0 else 0.0
                if (self._od_bar1_shape == "DOWN" and bar.close_price > bar.open_price
                        and body_ratio >= self.opening_rev_body_ratio
                        and bar.close_price > self._od_bar1_mid):
                    if self._arm_opening_rev(
                            bar, direction=1,
                            opportunity="OPP19_5M_OD_REV_LONG",
                            atr_5=atr_5, tick=tick, stop_buffer=stop_buffer,
                            effective_context=effective_context):
                        return True
                if (self._od_bar1_shape == "UP" and bar.close_price < bar.open_price
                        and body_ratio >= self.opening_rev_body_ratio
                        and bar.close_price < self._od_bar1_mid):
                    if self._arm_opening_rev(
                            bar, direction=-1,
                            opportunity="OPP19_5M_OD_REV_SHORT",
                            atr_5=atr_5, tick=tick, stop_buffer=stop_buffer,
                            effective_context=effective_context):
                        return True
            # Path A: Range collection
            self._od_high = max(self._od_high, bar.high_price)
            self._od_low = min(self._od_low, bar.low_price)
            self._od_bars_collected += 1
            if self._od_bars_collected >= self.opening_drive_bars:
                if self._od_high - self._od_low >= atr_5 * self.opening_drive_range_atr_min:
                    self._od_state = "RANGE_SET"
                else:
                    self._reset_opening_drive()
            return False
        # RANGE_SET
        if self._od_state == "RANGE_SET":
            self._od_bars_collected += 1
            if self._od_bars_collected > 24:
                self._reset_opening_drive()
                return False
            body_ratio = body / bar_range if bar_range > 0 else 0.0
            # EXP-007：OPP19 突破 R² 门禁（替代 Setup AFF 时启用）
            if (self.opp19_breakout_r2_gate_enabled
                    and self._trend_regime_blocks_continuation(self.opp19_breakout_r2_min)):
                return False
            if (self.opp19_breakout_aff_gate_enabled
                    and self._aff_alpha_strength < self.opp19_breakout_aff_alpha_min):
                return False
            if (bar.close_price > self._od_high and bar.close_price > bar.open_price
                    and body_ratio >= self.opening_drive_min_body and is_strong_bar):
                if self._opening_drive_breakout_context_ok(1, effective_context):
                    self._arm_fast_track(
                        direction=1, opportunity="OPP19_5M_OD_BREAKOUT_LONG",
                        trigger=bar.high_price + tick,
                        stop=self._cap_long_stop(bar.low_price - stop_buffer, bar.close_price, atr_5))
                    self._reset_opening_drive()
                    return True
            if (bar.close_price < self._od_low and bar.close_price < bar.open_price
                    and body_ratio >= self.opening_drive_min_body and is_strong_bar):
                if self._opening_drive_breakout_context_ok(-1, effective_context):
                    self._arm_fast_track(
                        direction=-1, opportunity="OPP19_5M_OD_BREAKOUT_SHORT",
                        trigger=bar.low_price - tick,
                        stop=self._cap_short_stop(bar.high_price + stop_buffer, bar.close_price, atr_5))
                    self._reset_opening_drive()
                    return True
        return False

    # ──────────────────────────────────────────────────────────────────────
    # OPP15 Wedge
    # ──────────────────────────────────────────────────────────────────────
    @staticmethod
    def _array_manager_to_wedge_bars(am: ArrayManager) -> list[WedgeBar]:
        n = min(am.count, am.size)
        return [WedgeBar(
            open_price=float(am.open[-(n - i)]), high_price=float(am.high[-(n - i)]),
            low_price=float(am.low[-(n - i)]), close_price=float(am.close[-(n - i)]), index=i,
        ) for i in range(n)]

    def _update_mtf_wedge_exhaustion_zone(self, atr_15: float) -> None:
        if atr_15 <= 0 or self.am_15min.count < 7:
            self.mtf_wedge_exhaustion_zone = False
            self.mtf_bull_wedge_exhaustion_zone = False
            return
        tick = self.get_pricetick()
        bars = self._array_manager_to_wedge_bars(self.am_15min)
        verdict_bear = scan_latest_bearish_wedge(
            bars, atr_15, tick_size=tick, n_min=self.wedge_n_min_15m,
            alpha_threshold=self.wedge_mtf_alpha_threshold)
        self.mtf_wedge_exhaustion_zone = verdict_bear.get("status") == "wedge_valid:hh3"
        verdict_bull = scan_latest_bullish_wedge(
            bars, atr_15, tick_size=tick, n_min=self.wedge_n_min_15m,
            alpha_threshold=self.wedge_mtf_alpha_threshold)
        self.mtf_bull_wedge_exhaustion_zone = verdict_bull.get("status") == "wedge_valid:ll3"

    def _p3_body_from_idx(self, p3_idx: int, *, side: int = 0) -> float:
        n = min(self.am_5min.count, self.am_5min.size)
        neg = n - p3_idx
        if neg < 1 or neg > n:
            return self.wedge_confirmed_p3_high
        o = float(self.am_5min.open[-neg])
        c = float(self.am_5min.close[-neg])
        if o <= 0 or c <= 0:
            return self.wedge_confirmed_p3_high
        if side > 0:
            return max(o, c)
        if side < 0:
            return min(o, c)
        return min(o, c)

    def _process_wedge_trigger_phase(self, bar, atr_5, tick, *, is_strong_bar) -> bool:
        if not self.wedge_setup_active or self._wedge_direction == 0:
            return False
        d = self._wedge_direction
        # HH3 (bearish short)
        if d == -1:
            p3_price = self.wedge_confirmed_p3_high
            if bar.high_price > p3_price + tick:
                self._reset_wedge_setup()
                return False
            bars_since = (int((bar.datetime - self.wedge_arm_time).total_seconds() / 300)
                          if self.wedge_arm_time else 0)
            if bars_since > self.wedge_arm_trigger_max_bars:
                self._reset_wedge_setup()
                return False
            if self.am_5min.count >= 2:
                self.wedge_trigger_line = min(
                    float(self.am_5min.low[-1]), float(self.am_5min.low[-2]))
            p3_stop = p3_price + tick
            trigger = bar.low_price - tick
            # Path A: 强趋势棒反向突破
            if (is_strong_bar and bar.close_price < bar.open_price
                    and self.wedge_trigger_line > 0
                    and bar.close_price < self.wedge_trigger_line
                    and not self._pd_blocks_short_target(bar.close_price, atr_5)):
                self._arm_fast_track(
                    direction=-1, opportunity="OPP15_5M_WEDGE_REVERSAL",
                    trigger=trigger,
                    stop=self._cap_short_stop(p3_stop, bar.close_price, atr_5),
                    invalid_line=p3_price)
                self._reset_wedge_setup()
                return True
            # Path B': alpha 衰减 + 跌破 p3 body floor
            if (self.wedge_current_alpha < self.wedge_b_prime_alpha
                    and bar.close_price < bar.open_price
                    and self.wedge_p3_body_floor > 0
                    and bar.close_price < self.wedge_p3_body_floor
                    and bars_since <= self.wedge_arm_trigger_max_bars
                    and not self._pd_blocks_short_target(bar.close_price, atr_5)):
                if self._dual_core_allows_entry(-1, self._setup_entry_lane("OPP15_5M_WEDGE_B_PRIME")):
                    if self._aff_blocks_entry():
                        self._aff_block_count += 1
                        return False
                    entry_price = bar.close_price - tick
                    volume = self._calc_brooks_volume(p3_stop, entry_price, atr_5=atr_5)
                    if volume > 0:
                        self.active_setup_name = "OPP15_5M_WEDGE_B_PRIME"
                        self.signal_stop_loss = p3_stop
                        self.signal_bar_invalid_line = p3_price
                        self.profit_protect_active = False
                        self.short(entry_price, volume)
                        self._reset_wedge_setup()
                        return True
            return False
        # LL3 (bullish long)
        p3_price = self.wedge_confirmed_p3_high
        if bar.low_price < p3_price - tick:
            self._reset_wedge_setup()
            return False
        bars_since = (int((bar.datetime - self.wedge_arm_time).total_seconds() / 300)
                      if self.wedge_arm_time else 0)
        if bars_since > self.wedge_arm_trigger_max_bars:
            self._reset_wedge_setup()
            return False
        if self.am_5min.count >= 2:
            self.wedge_trigger_line = max(
                float(self.am_5min.high[-1]), float(self.am_5min.high[-2]))
        p3_stop = p3_price - tick
        trigger = bar.high_price + tick
        # Path B' (long)
        if (self.wedge_current_alpha < self.wedge_b_prime_alpha
                and bar.close_price > bar.open_price
                and self.wedge_p3_body_floor > 0
                and bar.close_price > self.wedge_p3_body_floor
                and bars_since <= self.wedge_arm_trigger_max_bars
                and not self._pd_blocks_long_target(bar.close_price, atr_5)):
            if self._dual_core_allows_entry(1, self._setup_entry_lane("OPP15_5M_WEDGE_B_PRIME_LONG")):
                if self._aff_blocks_entry():
                    self._aff_block_count += 1
                    return False
                entry_price = bar.close_price + tick
                volume = self._calc_brooks_volume(entry_price, p3_stop, atr_5=atr_5)
                if volume > 0:
                    self.active_setup_name = "OPP15_5M_WEDGE_B_PRIME_LONG"
                    self.signal_stop_loss = p3_stop
                    self.signal_bar_invalid_line = p3_price
                    self.profit_protect_active = False
                    self.buy(entry_price, volume)
                    self._reset_wedge_setup()
                    return True
        return False

    def _try_arm_wedge_setup(self, bar, atr_5, tick) -> None:
        if self.wedge_setup_active or self.machine_state != "IDLE":
            return
        if self.late_phase_gate_enabled and self.trend_phase == "LATE":
            return
        if bar.datetime.time() < time(self.wedge_session_start_hour, self.wedge_session_start_minute):
            return
        if atr_5 < self.ttr_rb_min_atr:
            return
        bars = self._array_manager_to_wedge_bars(self.am_5min)
        # HH3 (bearish wedge → short)
        if self.market_context in ("WIDE_RANGE", "TIGHT_RANGE"):
            if not self.wedge_require_mtf or self.mtf_wedge_exhaustion_zone:
                verdict = scan_latest_bearish_wedge(
                    bars, atr_5, tick_size=tick, n_min=self.wedge_n_min_5m,
                    alpha_threshold=self.wedge_alpha_threshold)
                if verdict.get("status") == "wedge_valid:hh3":
                    p3_idx = int(verdict["p3_idx"])
                    if len(bars) - 1 >= p3_idx + 2:
                        p3_high = float(verdict.get("p3_high", 0.0))
                        if p3_high > 0:
                            self.wedge_setup_active = True
                            self._wedge_direction = -1
                            self.wedge_confirmed_p3_high = p3_high
                            self.wedge_arm_time = bar.datetime
                            self.wedge_current_alpha = float(verdict.get("alpha", 0.0))
                            self.wedge_p3_body_floor = self._p3_body_from_idx(p3_idx)
                            if self.am_5min.count >= 2:
                                self.wedge_trigger_line = min(
                                    float(self.am_5min.low[-1]), float(self.am_5min.low[-2]))
                            return
        # LL3 (bullish wedge → long)
        if self.market_context in ("BULL_CHANNEL", "WIDE_RANGE"):
            if not (self.market_context == "WIDE_RANGE" and not self.mtf_bull_wedge_exhaustion_zone):
                if self.always_in in ("LONG", "NONE"):
                    verdict = scan_latest_bullish_wedge(
                        bars, atr_5, tick_size=tick, n_min=self.wedge_n_min_5m,
                        alpha_threshold=self.wedge_alpha_threshold)
                    if verdict.get("status") == "wedge_valid:ll3":
                        p3_idx = int(verdict["p3_idx"])
                        if len(bars) - 1 >= p3_idx + 2:
                            p3_low = float(verdict.get("p3_low", 0.0))
                            if p3_low > 0:
                                self.wedge_setup_active = True
                                self._wedge_direction = 1
                                self.wedge_confirmed_p3_high = p3_low
                                self.wedge_arm_time = bar.datetime
                                self.wedge_current_alpha = float(verdict.get("alpha", 0.0))
                                self.wedge_p3_body_floor = self._p3_body_from_idx(p3_idx, side=1)
                                if self.am_5min.count >= 2:
                                    self.wedge_trigger_line = max(
                                        float(self.am_5min.high[-1]), float(self.am_5min.high[-2]))
                                return

    # ──────────────────────────────────────────────────────────────────────
    # 出场管理
    # ──────────────────────────────────────────────────────────────────────
    def _close_long_position(self, price, *, exit_reason="") -> None:
        if self.pos <= 0:
            return
        self._pending_exit_reason = exit_reason or "CLOSE_LONG"
        self.sell(price, abs(self.pos))
        self.signal_stop_loss = 0.0

    def _close_short_position(self, price, *, exit_reason="") -> None:
        if self.pos >= 0:
            return
        self._pending_exit_reason = exit_reason or "CLOSE_SHORT"
        self.cover(price, abs(self.pos))
        self.signal_stop_loss = 0.0

    def _manage_stop_loss(self, bar: BarData) -> None:
        """1m 级逻辑止损：跳空用 min(open, stop) / max(open, target)（§2.1）。"""
        if self.signal_stop_loss <= 0 or self.pos == 0:
            return
        reason = self._pending_exit_reason or "STOP_LOSS"
        if self.pos > 0 and bar.low_price <= self.signal_stop_loss:
            exec_price = min(bar.open_price, self.signal_stop_loss)
            self._close_long_position(exec_price, exit_reason=reason)
            self.write_log(f"【逻辑止损】多头防线触发 @ {exec_price} ({reason})")
        elif self.pos < 0 and bar.high_price >= self.signal_stop_loss:
            exec_price = max(bar.open_price, self.signal_stop_loss)
            self._close_short_position(exec_price, exit_reason=reason)
            self.write_log(f"【逻辑止损】空头防线触发 @ {exec_price} ({reason})")

    def _manage_mm_targets(self, bar: BarData) -> None:
        """1m 级 Measured Move 止盈：0.5 目标位平半仓 + 完全目标位 runner 减仓。"""
        if self.pos == 0 or self.entry_price <= 0 or not self.mm_half_close_enabled:
            return
        if self.pos > 0:
            if self.mm_target_price <= self.entry_price:
                return
            half_target = (self.entry_price + self.mm_target_price) / 2.0
            if (not self.mm_half_closed and bar.high_price >= half_target
                    and self.volume_capable_half_close() and abs(self.pos) // 2 > 0):
                self._close_long_position(max(half_target, bar.open_price), exit_reason="MM_HALF")
                self.mm_half_closed = True
            if not self.mm_target_scaled and self.pos > 0 and bar.high_price >= self.mm_target_price:
                close_vol, runner_vol = self._calc_mm_runner_exit_volumes()
                exec_price = max(bar.open_price, self.mm_target_price)
                if runner_vol > 0 and close_vol > 0:
                    self._close_long_position(exec_price, exit_reason="MM_RUNNER_START")
                    self.mm_target_scaled = True
                    self.mm_runner_active = True
                else:
                    self._close_long_position(exec_price, exit_reason="MM_TARGET_FULL")
            return
        # pos < 0
        if not (0 < self.mm_target_price < self.entry_price):
            return
        half_target = (self.entry_price + self.mm_target_price) / 2.0
        if (not self.mm_half_closed and bar.low_price <= half_target
                and self.volume_capable_half_close() and abs(self.pos) // 2 > 0):
            self._close_short_position(min(half_target, bar.open_price), exit_reason="MM_HALF")
            self.mm_half_closed = True
        if not self.mm_target_scaled and self.pos < 0 and bar.low_price <= self.mm_target_price:
            close_vol, runner_vol = self._calc_mm_runner_exit_volumes()
            exec_price = min(bar.open_price, self.mm_target_price)
            if runner_vol > 0 and close_vol > 0:
                self._close_short_position(exec_price, exit_reason="MM_RUNNER_START")
                self.mm_target_scaled = True
                self.mm_runner_active = True
            else:
                self._close_short_position(exec_price, exit_reason="MM_TARGET_FULL")

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

    def _apply_chandelier_stop_long(self, atr_5) -> None:
        self.profit_protect_active = True
        self.signal_stop_loss = max(
            self.signal_stop_loss, self.highest_high_since_entry - self.chandelier_multiplier * atr_5)

    def _apply_chandelier_stop_short(self, atr_5) -> None:
        self.profit_protect_active = True
        chandelier_stop = self.lowest_low_since_entry + self.chandelier_multiplier * atr_5
        if self.signal_stop_loss <= 0:
            self.signal_stop_loss = chandelier_stop
        else:
            self.signal_stop_loss = min(self.signal_stop_loss, chandelier_stop)

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
                self.signal_stop_loss = max(self.signal_stop_loss, self.entry_price)
            else:
                self.signal_stop_loss = (min(self.signal_stop_loss, self.entry_price)
                                          if self.signal_stop_loss > 0 else self.entry_price)
            self._pending_exit_reason = "BREAKEVEN"
            self.breakeven_locked = True
        if self.mm_runner_active:
            if is_long:
                self._apply_chandelier_stop_long(atr_5)
            else:
                self._apply_chandelier_stop_short(atr_5)
            self._pending_exit_reason = "CHANDELIER_RUNNER"
        elif self._is_fast_lane_setup():
            invalid_breach = (self.bars_since_entry <= 2 and self.signal_bar_invalid_line > 0
                               and (bar.close_price < self.signal_bar_invalid_line if is_long
                                    else bar.close_price > self.signal_bar_invalid_line))
            if invalid_breach:
                if is_long:
                    self.signal_stop_loss = max(self.signal_stop_loss, self.signal_bar_invalid_line)
                else:
                    self.signal_stop_loss = (min(self.signal_stop_loss, self.signal_bar_invalid_line)
                                              if self.signal_stop_loss > 0 else self.signal_bar_invalid_line)
                self._pending_exit_reason = "SIGNAL_BAR_INVALID"
            else:
                trail = bar.low_price - stop_buffer if is_long else bar.high_price + stop_buffer
                if is_long:
                    self.signal_stop_loss = max(self.signal_stop_loss, trail)
                else:
                    self.signal_stop_loss = (min(self.signal_stop_loss, trail)
                                              if self.signal_stop_loss > 0 else trail)
                self._pending_exit_reason = "FAST_LANE_TRAIL"
        else:
            # 慢车道
            if current_time >= time(14, 40):
                self.profit_protect_active = True
                ref = prev_low if is_long else prev_high
                if is_long:
                    self.signal_stop_loss = max(self.signal_stop_loss, ref)
                else:
                    self.signal_stop_loss = (min(self.signal_stop_loss, ref)
                                              if self.signal_stop_loss > 0 else ref)
                self._pending_exit_reason = "PROFIT_PROTECT_1440"
            elif (self.bars_since_entry <= self.follow_through_bars
                    and self.signal_bar_invalid_line > 0
                    and (bar.close_price < self.signal_bar_invalid_line if is_long
                         else bar.close_price > self.signal_bar_invalid_line)):
                if is_long:
                    self.signal_stop_loss = max(self.signal_stop_loss, self.signal_bar_invalid_line)
                else:
                    self.signal_stop_loss = (min(self.signal_stop_loss, self.signal_bar_invalid_line)
                                              if self.signal_stop_loss > 0 else self.signal_bar_invalid_line)
                self._pending_exit_reason = "SIGNAL_BAR_INVALID"
            elif floating_profit > self.trailing_active_multiplier * atr_5:
                if is_long:
                    self._apply_chandelier_stop_long(atr_5)
                else:
                    self._apply_chandelier_stop_short(atr_5)
                self._pending_exit_reason = "CHANDELIER_STOP"

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
        return entry_price + base_move if direction > 0 else entry_price - base_move

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
