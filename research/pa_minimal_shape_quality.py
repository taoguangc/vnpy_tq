# -*- coding: utf-8 -*-
"""pa_minimal 第二阶段：形态质量特征与 OPP16 前棒索引审计。"""
from __future__ import annotations

from datetime import datetime, time
from typing import Any

import numpy as np
import pandas as pd

from research.arm_lab import ArmRule, bars_to_frame, simulate_one
from research.event_engine.bars import resample_minutes
from strategies.pa_cta.bar_patterns import BarMetrics, PatternThresholds, classify_bar_shape

ATR_WINDOW = 14
DEFAULT_TH = PatternThresholds(
    bar_outside_prev_ratio=1.0,
    bar_trend_body_ratio=0.5,
    bar_spike_tail_body_ratio=2.0,
    reversal_shadow_min_ratio=0.6,
    reversal_close_quarter=0.25,
    reversal_min_body_ratio=0.35,
    boundary_reversal_shadow_ratio=0.55,
    boundary_reversal_close_ratio=0.35,
    strong_bar_body_ratio=0.55,
    strong_bar_atr_mult=0.8,
)
TWO_BAR_BODY_RATIO = 0.55


def _simple_bar(o: float, h: float, l: float, c: float):
    return type("B", (), {
        "open_price": o,
        "high_price": h,
        "low_price": l,
        "close_price": c,
    })()


def _bars_5m_from_1m(bars_1m: list) -> pd.DataFrame:
    df = bars_to_frame(bars_1m)
    df = df.rename(columns={"datetime": "dt_cst"})
    return resample_minutes(df, 5)


def _shape_at_index(bars_5: pd.DataFrame, idx: int, th: PatternThresholds = DEFAULT_TH) -> str:
    if idx < 0 or idx >= len(bars_5):
        return ""
    row = bars_5.iloc[idx]
    bar = BarMetrics.from_bar(_simple_bar(
        float(row["open"]), float(row["high"]), float(row["low"]), float(row["close"]),
    ))
    prev = None
    if idx >= 1:
        prow = bars_5.iloc[idx - 1]
        prev = BarMetrics.from_bar(_simple_bar(
            float(prow["open"]), float(prow["high"]), float(prow["low"]), float(prow["close"]),
        ))
    return classify_bar_shape(bar, prev, th)


def audit_opp16_prev_shape(bars_5: pd.DataFrame) -> pd.DataFrame:
    """逐 5m bar：生产式 prev_bar_shape（当前棒）vs 正确前棒形态。"""
    rows = []
    for i in range(1, len(bars_5)):
        cur_shape = _shape_at_index(bars_5, i)
        prev_shape = _shape_at_index(bars_5, i - 1)
        rows.append({
            "bar_time": str(bars_5.iloc[i]["dt_cst"]),
            "shape_as_prev_bar_shape_prod": cur_shape,
            "shape_of_ohlc_prev_bar": prev_shape,
            "mismatch": cur_shape != prev_shape,
        })
    return pd.DataFrame(rows)


def _opp16_match_offline(
    bars_5: pd.DataFrame,
    idx: int,
    *,
    strict: bool,
    use_correct_prev_shape: bool,
    body_ratio_min: float = TWO_BAR_BODY_RATIO,
) -> list[str]:
    """离线复现 OPP16：宽松=实体阈值（形态可选）；严格=实体 AND 形态。"""
    if idx < 1:
        return []
    cur = bars_5.iloc[idx]
    prev = bars_5.iloc[idx - 1]
    prev_range = float(prev["high"] - prev["low"])
    if prev_range <= 0:
        return []
    prev_body_ratio = abs(float(prev["close"]) - float(prev["open"])) / prev_range
    prev_mid = (float(prev["high"]) + float(prev["low"])) / 2.0
    shape_prod = _shape_at_index(bars_5, idx)
    shape_correct = _shape_at_index(bars_5, idx - 1)
    prev_shape = shape_correct if use_correct_prev_shape else shape_prod
    strong_shapes = {"UP_TREND", "DOWN_TREND", "OUTSIDE_UP", "OUTSIDE_DOWN"}
    shape_ok = prev_shape in strong_shapes
    if strict:
        if not (prev_body_ratio >= body_ratio_min and shape_ok):
            return []
    else:
        # 宽松现行：实体达标即可；实体未达标才直接拒
        if prev_body_ratio < body_ratio_min:
            return []
    out: list[str] = []
    if float(prev["close"]) < float(prev["open"]) and float(cur["close"]) > prev_mid:
        out.append("OPP16_5M_TWO_BAR_REV_LONG")
    if float(prev["close"]) > float(prev["open"]) and float(cur["close"]) < prev_mid:
        out.append("OPP16_5M_TWO_BAR_REV_SHORT")
    return out


def compare_opp16_definitions(bars_5: pd.DataFrame) -> pd.DataFrame:
    """宽松/严格 × 生产式形态时点/正确前棒形态。"""
    rows = []
    for i in range(2, len(bars_5)):
        loose_legacy = _opp16_match_offline(bars_5, i, strict=False, use_correct_prev_shape=False)
        strict_legacy = _opp16_match_offline(bars_5, i, strict=True, use_correct_prev_shape=False)
        loose_fixed = _opp16_match_offline(bars_5, i, strict=False, use_correct_prev_shape=True)
        strict_fixed = _opp16_match_offline(bars_5, i, strict=True, use_correct_prev_shape=True)
        if not (loose_legacy or strict_legacy or loose_fixed or strict_fixed):
            continue
        rows.append({
            "bar_time": str(bars_5.iloc[i]["dt_cst"]),
            "loose_legacy": "|".join(loose_legacy),
            "strict_legacy": "|".join(strict_legacy),
            "loose_fixed_prev": "|".join(loose_fixed),
            "strict_fixed_prev": "|".join(strict_fixed),
        })
    return pd.DataFrame(rows)


def _session_bucket(ts: pd.Timestamp) -> str:
    t = ts.to_pydatetime().time() if hasattr(ts, "to_pydatetime") else ts.time()
    if t >= time(21, 0) or t < time(2, 30):
        return "night_open"
    if time(9, 0) <= t < time(10, 15):
        return "day_open"
    if time(10, 15) <= t < time(11, 30):
        return "morning"
    if time(13, 30) <= t < time(15, 0):
        return "afternoon"
    return "other"


def extract_shape_features(cohort: pd.DataFrame, bars_5: pd.DataFrame) -> pd.DataFrame:
    """为 gate_pass 候选附加形态质量特征（信号 bar 收盘可得）。"""
    bars_5 = bars_5.copy()
    bars_5["dt_cst"] = pd.to_datetime(bars_5["dt_cst"]).dt.tz_localize(None)
    bars_5 = bars_5.sort_values("dt_cst").reset_index(drop=True)
    h = bars_5["high"].astype(float)
    l = bars_5["low"].astype(float)
    c = bars_5["close"].astype(float)
    o = bars_5["open"].astype(float)
    tr = pd.concat([(h - l), (h - c.shift(1)).abs(), (l - c.shift(1)).abs()], axis=1).max(axis=1)
    bars_5["atr5"] = tr.rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean()
    bars_5["range5"] = h - l
    bars_5["body_ratio"] = (c - o).abs() / bars_5["range5"].replace(0, np.nan)
    bars_5["close_extreme_ratio"] = np.where(
        c >= o,
        (h - c) / bars_5["range5"].replace(0, np.nan),
        (c - l) / bars_5["range5"].replace(0, np.nan),
    )

    rows: list[dict[str, Any]] = []
    for _, cand in cohort.iterrows():
        t = pd.Timestamp(cand["time"]).tz_localize(None) if pd.Timestamp(cand["time"]).tzinfo else pd.Timestamp(cand["time"])
        diffs = (bars_5["dt_cst"] - t).abs()
        if diffs.min() > pd.Timedelta(minutes=5):
            continue
        i = int(diffs.idxmin())
        if i < 2:
            continue
        row = bars_5.iloc[i]
        prev = bars_5.iloc[i - 1]
        prev2 = bars_5.iloc[i - 2]
        atr = float(row["atr5"]) if row["atr5"] == row["atr5"] and row["atr5"] > 0 else 1.0
        setup = str(cand["setup"])
        direction = int(cand["direction"])
        feat: dict[str, Any] = {
            "time": str(cand["time"]),
            "setup": setup,
            "direction": direction,
            "trigger": float(cand["trigger"]),
            "stop": float(cand["stop"]),
            "arm_mode": str(cand.get("arm_mode") or ""),
            "session": _session_bucket(t),
            "body_atr": float(abs(row["close"] - row["open"]) / atr),
            "close_extreme_ratio": float(row["close_extreme_ratio"]) if row["close_extreme_ratio"] == row["close_extreme_ratio"] else np.nan,
        }
        if setup.startswith("OPP08"):
            prev_high = float(prev["high"])
            prev_low = float(prev["low"])
            if direction > 0:
                feat["breakout_atr"] = (float(row["close"]) - prev_high) / atr
            else:
                feat["breakout_atr"] = (prev_low - float(row["close"])) / atr
            if i >= 5:
                feat["range_convergence"] = float(bars_5.iloc[i - 5:i]["range5"].std() / atr)
            else:
                feat["range_convergence"] = np.nan
        if setup.startswith("OPP16"):
            pr = float(prev["high"] - prev["low"])
            feat["prev_body_ratio"] = abs(float(prev["close"]) - float(prev["open"])) / pr if pr > 0 else 0.0
            prev_mid = (float(prev["high"]) + float(prev["low"])) / 2.0
            if direction > 0:
                feat["close_over_mid_atr"] = (float(row["close"]) - prev_mid) / atr
            else:
                feat["close_over_mid_atr"] = (prev_mid - float(row["close"])) / atr
            overlap = max(0.0, min(float(row["high"]), float(prev["high"])) - max(float(row["low"]), float(prev["low"])))
            feat["two_bar_overlap"] = overlap / pr if pr > 0 else 0.0
            feat["two_bar_disp_atr"] = abs(float(row["close"]) - float(prev2["close"])) / atr
            feat["prev_shape_label"] = _shape_at_index(bars_5, i - 1)
            feat["prod_shape_as_prev"] = _shape_at_index(bars_5, i)
        rows.append(feat)
    return pd.DataFrame(rows)


def attach_forward_metrics(
    features: pd.DataFrame,
    bars_1m: list,
    *,
    tick: float,
    contract_size: float,
    cost_per_rt: float,
) -> pd.DataFrame:
    """用 arm_lab A 成交路径附加 MFE/MAE/1R/成本后净额。"""
    if features.empty:
        return features
    df = bars_to_frame(bars_1m)
    out = features.copy()
    mfe_list, mae_list, hit1r, net1, cost_cov, filled_list = [], [], [], [], [], []
    for _, row in features.iterrows():
        cand = {
            "time": row["time"],
            "setup": row["setup"],
            "direction": int(row["direction"]),
            "trigger": float(row["trigger"]),
            "stop": float(row["stop"]),
            "arm_mode": row.get("arm_mode") or ("FAST_TRACK" if str(row["setup"]).startswith("OPP08") else "PENDING_CONFIRM"),
            "gate_pass": True,
        }
        sim = simulate_one(df, cand, ArmRule.CURRENT, tick=tick, contract_size=contract_size)
        if not sim.filled:
            mfe_list.append(np.nan)
            mae_list.append(np.nan)
            hit1r.append(False)
            net1.append(np.nan)
            cost_cov.append(np.nan)
            filled_list.append(False)
            continue
        init_r = abs(sim.fill_price - sim.stop) * contract_size
        mfe_list.append(sim.mfe_r)
        mae_list.append(sim.mae_r)
        hit1r.append(sim.hit_1r)
        net1.append(sim.net_pnl_1lot - cost_per_rt)
        cost_cov.append(cost_per_rt / init_r if init_r > 0 else np.nan)
        filled_list.append(True)
    out["filled"] = filled_list
    out["mfe_r"] = mfe_list
    out["mae_r"] = mae_list
    out["hit_1r"] = hit1r
    out["net_1lot_after_cost"] = net1
    out["cost_over_1r"] = cost_cov
    return out


def conditional_expectancy_table(features: pd.DataFrame, feature: str, n_quantiles: int = 3) -> pd.DataFrame:
    """按特征分位汇总条件期望。"""
    if features.empty or feature not in features.columns:
        return pd.DataFrame()
    work = features.dropna(subset=[feature, "net_1lot_after_cost"]).copy()
    if len(work) < n_quantiles * 3:
        return pd.DataFrame()
    try:
        work["bucket"] = pd.qcut(work[feature], n_quantiles, duplicates="drop")
    except ValueError:
        return pd.DataFrame()
    agg = (
        work.groupby(["setup", "bucket"], observed=True)
        .agg(
            n=("net_1lot_after_cost", "count"),
            avg_net=("net_1lot_after_cost", "mean"),
            hit_1r_rate=("hit_1r", "mean"),
            avg_mfe=("mfe_r", "mean"),
            avg_mae=("mae_r", "mean"),
        )
        .reset_index()
    )
    agg["feature"] = feature
    return agg


def best_feature_direction(cond_tables: list[pd.DataFrame], features: pd.DataFrame | None = None) -> pd.DataFrame:
    """每个 setup 选特征方向；若提供 features 则附加 IS/OOS 同向标记。"""
    rows = []
    for tbl in cond_tables:
        if tbl.empty:
            continue
        for setup, g in tbl.groupby("setup"):
            g = g.sort_values("bucket")
            if len(g) < 2:
                continue
            top = g.iloc[-1]
            bottom = g.iloc[0]
            mono = float(top["avg_net"]) > float(bottom["avg_net"])
            is_oos_same = False
            if features is not None and "time" in features.columns:
                feat_name = str(g["feature"].iloc[0])
                sub = features[features["setup"] == setup].dropna(subset=[feat_name, "net_1lot_after_cost"])
                if len(sub) >= 6:
                    from research.pa_minimal_baseline import split_by_time
                    is_df, oos_df = split_by_time(sub, "time")
                    if len(is_df) >= 3 and len(oos_df) >= 3:
                        med = float(sub[feat_name].median())
                        is_hi = is_df[is_df[feat_name] >= med]["net_1lot_after_cost"].mean()
                        is_lo = is_df[is_df[feat_name] < med]["net_1lot_after_cost"].mean()
                        oos_hi = oos_df[oos_df[feat_name] >= med]["net_1lot_after_cost"].mean()
                        oos_lo = oos_df[oos_df[feat_name] < med]["net_1lot_after_cost"].mean()
                        if all(x == x for x in (is_hi, is_lo, oos_hi, oos_lo)):
                            is_oos_same = (is_hi > is_lo) == (oos_hi > oos_lo)
            rows.append({
                "setup": setup,
                "feature": str(g["feature"].iloc[0]),
                "top_avg_net": float(top["avg_net"]),
                "bottom_avg_net": float(bottom["avg_net"]),
                "mono_up": mono,
                "is_oos_same": is_oos_same,
                "top_n": int(top["n"]),
            })
    return pd.DataFrame(rows)
