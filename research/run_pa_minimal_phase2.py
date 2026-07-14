# -*- coding: utf-8 -*-
"""EXP-M0-P2 — pa_minimal 第二阶段主运行器。

按计划顺序：
  1. lock-baselines — 冻结 M0-BASE cohort + manifest
  2. exit-cost — 固定入场 cohort 出场族 + 定仓敏感度
  3. shape-quality — OPP16 前棒审计 + 形态条件期望
  4. background-gates — 成本覆盖率 / 会话门禁 OOS
  5. arm-refinement — 仅离线 OPP 专属武装（若前置通过）
  6. cross-symbol — CROSS_SYMBOL_UNIVERSE 阶段 A 诊断（阶段 B 按停止条件）
  7. stop-or-promote — 汇总 KEEP/REVERT/HOLD

用法::
  python -m research.run_pa_minimal_phase2 --symbol rb
  python -m research.run_pa_minimal_phase2 --symbol rb --skip-sizing
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.pa_minimal_arm_variants import run_arm_variants
from research.pa_minimal_background_gates import run_background_gates, session_expectancy
from research.pa_minimal_baseline import (
    COST_RATE,
    WINDOW_END,
    WINDOW_START,
    export_frozen_cohort,
    load_frozen_cohort,
)
from research.pa_minimal_cross_symbol import run_cross_symbol_phase_a
from strategies.pa_cta.symbol_config import cross_symbol_list
from research.pa_minimal_exit_cost import (
    arm_fills_to_cohort,
    run_arm_then_exit,
    run_exit_family_lab,
    run_sizing_sensitivity,
)
from research.pa_minimal_shape_quality import (
    _bars_5m_from_1m,
    attach_forward_metrics,
    audit_opp16_prev_shape,
    best_feature_direction,
    compare_opp16_definitions,
    conditional_expectancy_table,
    extract_shape_features,
)
from research.arm_lab import run_arm_lab
from scripts.tq_rollover_data import load_stitched_raw_bars
from strategies.pa_minimal.backtest import run_minimal_backtest
from strategies.pa_minimal.symbol_config import resolve_minimal_profile


def _estimate_cost_1lot(profile: dict, mid_price: float = 3500.0) -> float:
    size = float(profile["size"])
    slip = float(profile["slippage"])
    rate = COST_RATE
    one_side = mid_price * size * rate + size * slip
    return 2.0 * one_side


def _append_experiments(md: str) -> None:
    path = ROOT / "research" / "experiments.md"
    with path.open("a", encoding="utf-8") as f:
        f.write("\n" + md + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="pa_minimal phase-2 runner")
    parser.add_argument("--symbol", default="rb")
    parser.add_argument("--output-dir", default=str(ROOT / "research" / "output"))
    parser.add_argument("--skip-sizing", action="store_true", help="跳过三档 max_position 回测（省配额）")
    parser.add_argument("--skip-cross", action="store_true")
    args = parser.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    symbol = args.symbol.lower()
    profile = resolve_minimal_profile(symbol, ROOT)
    tick = float(profile["pricetick"])
    size = float(profile["size"])
    slippage = float(profile["slippage"])
    cost_1lot = _estimate_cost_1lot(profile)

    decisions: dict[str, str] = {}
    print("=== EXP-M0-P2 pa_minimal 第二阶段 ===")
    print(f"品种={symbol} 窗口={WINDOW_START.date()}~{WINDOW_END.date()}")
    print(f"成本假设: rate={COST_RATE} slip={slippage} size={size} 估1手往返≈{cost_1lot:.1f}")

    # ---------- 1. lock-baselines ----------
    print("\n----- [1] 冻结 M0-BASE cohort -----")
    bt = run_minimal_backtest(symbol=symbol, verbose=False)
    records = bt.get("candidate_records") or []
    funnel = bt.get("candidate_funnel") or {}
    trips = bt["round_trips"]
    stats = bt["stats"]
    cpath, mpath = export_frozen_cohort(records, symbol=symbol, root=ROOT, out_dir=out)
    cohort_df = load_frozen_cohort(out, symbol)
    print(f"candidates={funnel.get('candidates')} gate_pass={len(cohort_df)} armed={funnel.get('armed')}")
    print(f"live RT={len(trips)} net={stats.get('total_net_pnl', sum(t.net_pnl for t in trips)):+,.0f}")
    print(f"cohort: {cpath}")
    print(f"manifest: {mpath}")
    decisions["lock_baselines"] = "DONE"

    bars = load_stitched_raw_bars(
        profile["file_stem"],
        profile["exchange"],
        symbol=symbol,
        start=WINDOW_START,
        end=WINDOW_END,
    )
    print(f"1m bars: {len(bars):,}")
    gate_records = cohort_df.to_dict("records")
    for r in gate_records:
        r["gate_pass"] = True

    # ---------- 2. exit-cost（计划优先） ----------
    print("\n----- [2] 出场族 + 定仓敏感度 -----")
    arm_detail, exit_sum, tm_cohort = run_arm_then_exit(
        gate_records, bars, symbol=symbol, root=ROOT,
    )
    arm_detail.to_csv(out / f"p2_arm_detail_{symbol}.csv", index=False, encoding="utf-8-sig")
    exit_sum.to_csv(out / f"p2_exit_summary_{symbol}.csv", index=False, encoding="utf-8-sig")
    print(f"arm A fills → TM cohort n={len(tm_cohort)}")
    print(exit_sum.to_string(index=False))

    exit_net = {}
    for _, row in exit_sum.iterrows():
        exit_net[row.get("rule") if "rule" in exit_sum.columns else row.iloc[0]] = float(
            row.get("net_pnl", row.get("total_net_pnl", 0))
        )
    # RuleSummary fields
    if "rule" in exit_sum.columns and "net_pnl" in exit_sum.columns:
        for _, row in exit_sum.iterrows():
            exit_net[str(row["rule"])] = float(row["net_pnl"])

    assigned = exit_net.get("FAMILY_ASSIGNED", float("nan"))
    actual = exit_net.get("ACTUAL", float("nan"))
    cont = exit_net.get("FAMILY_CONTINUATION", float("nan"))
    rev = exit_net.get("FAMILY_REVERSAL", float("nan"))
    print(f"ACTUAL={actual:+.0f} ASSIGNED={assigned:+.0f} CONT={cont:+.0f} REV={rev:+.0f}")

    sizing_df = pd.DataFrame()
    if not args.skip_sizing:
        print("\n三档 max_position 回测...")
        sizing_df = run_sizing_sensitivity(symbol, baseline_bt=bt)
        sizing_df.to_csv(out / f"p2_sizing_{symbol}.csv", index=False, encoding="utf-8-sig")
        print(sizing_df.to_string(index=False))
        one_lot_proxy = float(sizing_df.loc[sizing_df["tier"] == "LOW", "net_pnl"].iloc[0]) if len(sizing_df) else float("nan")
        # 1 手等价：用 LOW 档 + 看 arm A 扣成本
    else:
        print("跳过定仓回测（--skip-sizing）")
        one_lot_proxy = float("nan")

    a_filled = arm_detail[(arm_detail["rule"] == "A_CURRENT") & (arm_detail["filled"] == True)]  # noqa: E712
    a_gross = float(a_filled["net_pnl_1lot"].sum()) if len(a_filled) else 0.0
    a_after_cost = a_gross - cost_1lot * len(a_filled)
    print(f"固定 cohort 武装A：成交={len(a_filled)} 毛={a_gross:+.0f} 扣估成本后={a_after_cost:+.0f}")

    exit_positive = any(
        (isinstance(v, float) and v == v and v > 0)
        for k, v in exit_net.items()
        if k in ("FAMILY_ASSIGNED", "FAMILY_CONTINUATION", "FAMILY_REVERSAL", "FIXED_1R")
    )
    one_lot_positive = a_after_cost > 0
    if not exit_positive and not one_lot_positive:
        decisions["exit_cost"] = "STOP"
        print("停止条件触发：出场族与 1 手扣成本期望均未转正 → 停止 OPP08/16 策略优化")
    else:
        decisions["exit_cost"] = "CONTINUE" if (exit_positive or one_lot_positive) else "HOLD"
        print(f"exit_cost 判定: {decisions['exit_cost']}")

    # ---------- 3. shape-quality ----------
    print("\n----- [3] 形态质量 / OPP16 前棒审计 -----")
    bars_5 = _bars_5m_from_1m(bars)
    audit = audit_opp16_prev_shape(bars_5)
    audit_path = out / f"p2_opp16_shape_audit_{symbol}.csv"
    audit.to_csv(audit_path, index=False, encoding="utf-8-sig")
    mismatch_rate = float(audit["mismatch"].mean()) if len(audit) else 0.0
    print(f"前棒形态 mismatch 率: {mismatch_rate:.1%} ({int(audit['mismatch'].sum())}/{len(audit)})")

    defs = compare_opp16_definitions(bars_5)
    defs.to_csv(out / f"p2_opp16_def_compare_{symbol}.csv", index=False, encoding="utf-8-sig")
    n_loose = (defs["loose_legacy"] != "").sum() if len(defs) else 0
    n_strict = (defs["strict_legacy"] != "").sum() if len(defs) else 0
    n_fixed = (defs["loose_fixed_prev"] != "").sum() if len(defs) else 0
    print(f"OPP16 定义计数 loose={n_loose} strict={n_strict} loose_fixed_prev={n_fixed}")

    feats = extract_shape_features(cohort_df, bars_5)
    feats = attach_forward_metrics(
        feats, bars, tick=tick, contract_size=size, cost_per_rt=cost_1lot,
    )
    feats.to_csv(out / f"p2_shape_features_{symbol}.csv", index=False, encoding="utf-8-sig")

    feature_list = ["body_atr", "close_extreme_ratio", "breakout_atr", "range_convergence",
                    "prev_body_ratio", "close_over_mid_atr", "two_bar_overlap", "two_bar_disp_atr"]
    cond_tables = []
    for f in feature_list:
        if f in feats.columns:
            tbl = conditional_expectancy_table(feats, f)
            if not tbl.empty:
                cond_tables.append(tbl)
    if cond_tables:
        cond_all = pd.concat(cond_tables, ignore_index=True)
        cond_all.to_csv(out / f"p2_shape_conditional_{symbol}.csv", index=False, encoding="utf-8-sig")
        best = best_feature_direction(cond_tables, feats)
        best.to_csv(out / f"p2_shape_best_{symbol}.csv", index=False, encoding="utf-8-sig")
        print(best.to_string(index=False) if len(best) else "无稳定特征")
        shape_pass = bool(
            len(best)
            and (best["mono_up"] & (best["top_avg_net"] > 0) & best["is_oos_same"]).any()
        )
    else:
        best = pd.DataFrame()
        shape_pass = False
        print("条件期望表为空")
    decisions["shape_quality"] = "PASS" if shape_pass else "HOLD_ORIGINAL"
    print(f"形态门禁: {decisions['shape_quality']}")

    # ---------- 4. background-gates ----------
    print("\n----- [4] 背景门禁（成本覆盖率 / 会话） -----")
    sess_exp = session_expectancy(feats)
    if len(sess_exp):
        sess_exp.to_csv(out / f"p2_session_expectancy_{symbol}.csv", index=False, encoding="utf-8-sig")
        print(sess_exp.to_string(index=False))
    bg = run_background_gates(feats)
    bg.to_csv(out / f"p2_background_gates_{symbol}.csv", index=False, encoding="utf-8-sig")
    print(bg.to_string(index=False))
    bg_pass = bool(len(bg) and (bg["verdict"].isin(["KEEP", "HOLD"])).any() and (bg["oos_net"] > bg["base_oos_net"]).any())
    # 更严：至少一项 verdict 非 REVERT 且 oos 改善
    bg_keep = bool(len(bg) and (bg["verdict"] == "KEEP").any())
    decisions["background_gates"] = "KEEP" if bg_keep else ("HOLD" if bg_pass else "REVERT")
    print(f"背景门禁: {decisions['background_gates']}")

    # ---------- 5. arm-refinement ----------
    print("\n----- [5] OPP 专属武装微调 -----")
    allow_arm = decisions["shape_quality"] == "PASS" or decisions["background_gates"] in ("KEEP", "HOLD")
    if decisions["exit_cost"] == "STOP":
        allow_arm = False
        print("因 exit STOP，跳过武装微调")
    if allow_arm:
        sims, arm_var_sum = run_arm_variants(gate_records, bars, tick=tick, contract_size=size)
        pd.DataFrame([s.__dict__ for s in sims]).to_csv(
            out / f"p2_arm_variants_detail_{symbol}.csv", index=False, encoding="utf-8-sig"
        )
        arm_var_sum.to_csv(out / f"p2_arm_variants_summary_{symbol}.csv", index=False, encoding="utf-8-sig")
        print(arm_var_sum[arm_var_sum["group"] == "ALL"].to_string(index=False))
        base_pnl = float(
            arm_var_sum[(arm_var_sum.rule == "A_CURRENT") & (arm_var_sum.group == "ALL")]["sum_pnl_1lot"].iloc[0]
        )
        best_var = arm_var_sum[arm_var_sum.group == "ALL"].sort_values("sum_pnl_1lot", ascending=False).iloc[0]
        if float(best_var["sum_pnl_1lot"]) > base_pnl and best_var["rule"] != "A_CURRENT":
            decisions["arm_refinement"] = "HOLD_OFFLINE_ONLY"
        else:
            decisions["arm_refinement"] = "KEEP_A"
        print(f"武装: {decisions['arm_refinement']}（相对 A 最优={best_var['rule']}）")
    else:
        decisions["arm_refinement"] = "SKIPPED"
        print("前置未过门，跳过武装")

    # ---------- 6. cross-symbol ----------
    universe = cross_symbol_list()
    print(f"\n----- [6] 跨品种阶段 A（{','.join(universe)}） -----")
    if args.skip_cross or decisions["exit_cost"] == "STOP":
        cross = pd.DataFrame()
        decisions["cross_symbol"] = "SKIPPED"
        print("跳过跨品种（停止条件或 --skip-cross）")
    else:
        promote_cross = (
            decisions["shape_quality"] == "PASS"
            or decisions["background_gates"] in ("KEEP", "HOLD")
        )
        if not promote_cross:
            decisions["cross_symbol"] = "SKIPPED_NO_PROMOTE"
            print("未满足「形态或背景通过」→ 不做完整确认；仍做阶段 A 只读诊断")
        others = [s for s in universe if s != symbol.lower()]
        cross = run_cross_symbol_phase_a(others, ROOT) if others else pd.DataFrame()
        if symbol.lower() in universe:
            current_row = {
                "symbol": symbol.lower(),
                "candidates": funnel.get("candidates", 0),
                "gate_pass": len(cohort_df),
                "armed": funnel.get("armed", 0),
                "opp08_gate": int(sum(1 for r in gate_records if str(r.get("setup", "")).startswith("OPP08"))),
                "opp16_gate": int(sum(1 for r in gate_records if str(r.get("setup", "")).startswith("OPP16"))),
                "n_rt": len(trips),
                "gross": float(sum(t.gross_pnl for t in trips)),
                "net": float(sum(t.net_pnl for t in trips)),
                "cost": float(sum(t.gross_pnl - t.net_pnl for t in trips)),
                "sharpe": float(stats.get("sharpe_ratio") or 0.0),
                "median_cost_1lot": cost_1lot,
                "slippage": slippage,
                "size": size,
                "phase_b_eligible": bool(len(trips) >= 15 and sum(t.net_pnl for t in trips) / max(len(trips), 1) > -5000),
                "rate": COST_RATE,
            }
            cross = pd.concat([pd.DataFrame([current_row]), cross], ignore_index=True)
        cross.to_csv(out / "p2_cross_phase_a.csv", index=False, encoding="utf-8-sig")
        print(cross.to_string(index=False))
        eligible = cross[cross["phase_b_eligible"] == True]  # noqa: E712
        if promote_cross and len(eligible) >= 2:
            decisions["cross_symbol"] = "PHASE_B_CANDIDATE"
        elif len(cross):
            decisions["cross_symbol"] = "PHASE_A_ONLY"
        else:
            decisions["cross_symbol"] = "EMPTY"

    # ---------- 7. stop-or-promote ----------
    print("\n----- [7] 停止 / 升级汇总 -----")
    if decisions.get("exit_cost") == "STOP":
        final = "STOP_BASELINE"
        promote_msg = "保留 M0-BASE 简单基线；不增加新门禁/武装；OPP08/16 成本后 alpha 未证实。"
    elif decisions.get("background_gates") == "KEEP" and decisions.get("shape_quality") == "PASS":
        final = "PROMOTE_CANDIDATE"
        promote_msg = "形态+背景通过样本外门禁；可进入跨品种阶段 B（需用户确认回测）。"
    else:
        final = "HOLD_NO_PROMOTE"
        promote_msg = "未同时通过形态/背景/出场转正；默认保留武装 A + Dual Core + VSA，不升级规则。"
    decisions["final"] = final
    print(json.dumps(decisions, ensure_ascii=False, indent=2))
    print(promote_msg)

    summary = {
        "symbol": symbol,
        "decisions": decisions,
        "live_net": float(stats.get("total_net_pnl") or sum(t.net_pnl for t in trips)),
        "live_n": len(trips),
        "cohort_n": len(cohort_df),
        "arm_a_n": len(a_filled),
        "arm_a_after_cost": a_after_cost,
        "opp16_mismatch_rate": mismatch_rate,
        "cost_1lot_est": cost_1lot,
        "promote_msg": promote_msg,
    }
    (out / f"p2_summary_{symbol}.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 追加 experiments.md
    md = f"""## 2026-07-13 EXP-M0-P2 — 极简 OPP08/OPP16 第二阶段（{symbol}）

**目标**：冻结 cohort → 出场/定仓 → 形态质量 → 背景门禁 → 武装微调 → 跨品种诊断 → 停止/升级。

**CLI**：`python -m research.run_pa_minimal_phase2 --symbol {symbol}`

### 冻结基线
- candidates={funnel.get('candidates')} gate_pass={len(cohort_df)} armed={funnel.get('armed')}
- live RT={len(trips)} net={summary['live_net']:+,.0f}
- 成本估 1 手往返≈{cost_1lot:.1f}；manifest=`{mpath.name}`

### 出场 / 定仓
- 武装 A 成交={len(a_filled)} 毛={a_gross:+.0f} 扣估成本后={a_after_cost:+.0f}
- 出场族汇总见 `p2_exit_summary_{symbol}.csv`
- 定仓：{'跳过' if args.skip_sizing else '见 p2_sizing_' + symbol + '.csv'}
- **判定**：`{decisions.get('exit_cost')}`

### 形态
- OPP16 前棒形态 mismatch={mismatch_rate:.1%}
- 形态门禁：`{decisions.get('shape_quality')}`

### 背景
- `{decisions.get('background_gates')}`（见 `p2_background_gates_{symbol}.csv`）

### 武装
- `{decisions.get('arm_refinement')}`

### 跨品种
- `{decisions.get('cross_symbol')}`

### 最终
- **{final}**：{promote_msg}
"""
    _append_experiments(md)
    print("\n已追加 research/experiments.md")


if __name__ == "__main__":
    main()
