# -*- coding: utf-8 -*-
"""将稳定性门禁排名第一的 OPP 单独转入 CTA 含成本验证（1 手/恒定风险）。

读取 research/output/alpha_discovery/top_promote.json；
若无 PROMOTE_TO_CTA 则跳过回测并记录 SKIP。

用法::
  python -m research.run_pa_minimal_alpha_promote
  python -m research.run_pa_minimal_alpha_promote --opp OPP08 --direction -1 --symbols rb,hc
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.pa_minimal_baseline import (
    ALPHA_SYMBOL_UNIVERSE,
    CTA_KEEP_MIN_PF,
    CTA_KEEP_MIN_RT,
    WINDOW_END,
    WINDOW_START,
)
from strategies.pa_cta.symbol_config import cross_symbol_list
from strategies.pa_minimal.backtest import run_minimal_backtest

OUT_DIR = ROOT / "research" / "output" / "alpha_discovery"

# 单 OPP 启用：其余关闭
_OPP_FLAG = {
    "OPP02": {"ema_pullback_enabled": True},
    "OPP08": {},  # 默认开；通过 disabled 关 16
    "OPP12": {"overshoot_fail_enabled": True},
    "OPP13": {"day_boundary_enabled": True},
    "OPP15": {"wedge_enabled": True},
    "OPP16": {"two_bar_rev_enabled": True},
    "OPP17": {"climax_rev_enabled": True},
    "OPP19": {"opening_drive_enabled": True, "opening_rev_enabled": True},
}

_ALL_OFF = {
    "alpha_shadow_mode": False,
    "ema_pullback_enabled": False,
    "two_bar_rev_enabled": False,
    "overshoot_fail_enabled": False,
    "day_boundary_enabled": False,
    "wedge_enabled": False,
    "climax_rev_enabled": False,
    "opening_drive_enabled": False,
    "opening_rev_enabled": False,
    "max_position": 1,
    "setup_risk_mult_enabled": False,
}


def build_single_opp_overrides(opp_family: str, direction: int | None) -> dict:
    overrides = dict(_ALL_OFF)
    fam = opp_family.upper()
    overrides.update(_OPP_FLAG.get(fam, {}))
    if fam == "OPP08":
        # OPP08 无独立开关，靠默认检测路径；关 16
        overrides["two_bar_rev_enabled"] = False
    if fam == "OPP16":
        overrides["two_bar_rev_enabled"] = True
    # 方向：用 disabled_setups 软禁对侧（粗粒度，按 setup 前缀）
    # 实际禁单依赖策略 _setup_disabled；此处写常见对侧标签占位
    if direction == 1:
        overrides["disabled_setups"] = (
            "OPP08_5M_STRONG_BREAKOUT_SHORT,OPP16_5M_TWO_BAR_REV_SHORT,"
            "OPP12_5M_OVERSHOOT_FAIL_SHORT,OPP13_5M_RANGE_FAIL_HIGH,"
            "OPP15_5M_WEDGE_REVERSAL,OPP15_5M_WEDGE_B_PRIME,"
            "OPP17_5M_CLIMAX_REV_SHORT,OPP19_5M_OD_BREAKOUT_SHORT,OPP19_5M_OD_REV_SHORT,"
            "OPP02_5M_EMA_PULLBACK_SHORT"
        )
    elif direction == -1:
        overrides["disabled_setups"] = (
            "OPP08_5M_STRONG_BREAKOUT_LONG,OPP16_5M_TWO_BAR_REV_LONG,"
            "OPP12_5M_OVERSHOOT_FAIL_LONG,OPP13_5M_RANGE_FAIL_LOW,"
            "OPP15_5M_WEDGE_B_PRIME_LONG,"
            "OPP17_5M_CLIMAX_REV_LONG,OPP19_5M_OD_BREAKOUT_LONG,OPP19_5M_OD_REV_LONG,"
            "OPP02_5M_EMA_PULLBACK_LONG"
        )
    return overrides


def _verdict(stats: dict, rt_summary: dict) -> str:
    net = float(stats.get("total_net_pnl") or 0.0)
    pf = rt_summary.get("profit_factor")
    n = int(rt_summary.get("count") or stats.get("total_trade_count") or 0)
    # round-trip 更可靠
    n_rt = int(rt_summary.get("count") or 0)
    n_use = n_rt if n_rt else n // 2
    if n_use < CTA_KEEP_MIN_RT:
        return "HOLD_LOW_N"
    if net <= 0:
        return "REVERT"
    if pf is None or float(pf) < CTA_KEEP_MIN_PF:
        return "REVERT"
    return "KEEP_CANDIDATE"


def main() -> None:
    parser = argparse.ArgumentParser(description="Promote top OPP to CTA cost check")
    parser.add_argument("--opp", default="", help="OPP 族，如 OPP08；默认读 top_promote.json")
    parser.add_argument("--direction", type=int, default=0, help="1 / -1；0=读文件")
    parser.add_argument("--symbols", default="rb", help="逗号分隔；默认 rb（配额友好）")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    top_path = OUT_DIR / "top_promote.json"
    opp = args.opp.strip().upper()
    direction = args.direction if args.direction in (1, -1) else None
    if not opp:
        if not top_path.exists():
            print("无 top_promote.json，且未指定 --opp；SKIP。")
            return
        raw = top_path.read_text(encoding="utf-8").strip()
        if raw in ("", "null", "null\n"):
            print("top_promote.json 为空（无 PROMOTE_TO_CTA）；CTA 晋级 SKIP。")
            (OUT_DIR / "cta_promote_result.json").write_text(
                json.dumps(
                    {
                        "status": "SKIP",
                        "reason": "no_PROMOTE_TO_CTA",
                        "label_ceiling": "PROVISIONAL_or_REJECT_only",
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            return
        top = json.loads(raw)
        opp = str(top["opp_family"]).upper()
        direction = int(top["direction"])

    symbols = [s.strip().lower() for s in args.symbols.split(",") if s.strip()]
    if not symbols:
        symbols = ["rb"]
    allowed = set(cross_symbol_list()) | set(ALPHA_SYMBOL_UNIVERSE)
    symbols = [s for s in symbols if s in allowed]

    overrides = build_single_opp_overrides(opp, direction)
    rows = []
    for sym in symbols:
        bt = run_minimal_backtest(
            symbol=sym,
            zero_cost=False,
            verbose=not args.quiet,
            start=WINDOW_START,
            end=WINDOW_END,
            strategy_overrides=overrides,
        )
        stats = bt.get("stats") or {}
        rt = bt.get("rt_summary") or {}
        verdict = _verdict(stats, rt)
        row = {
            "symbol": sym,
            "opp_family": opp,
            "direction": direction,
            "net_pnl": float(stats.get("total_net_pnl") or 0),
            "annual_return": float(stats.get("annual_return") or 0),
            "max_ddpercent": float(stats.get("max_ddpercent") or 0),
            "sharpe": float(stats.get("sharpe_ratio") or 0),
            "trade_count": int(stats.get("total_trade_count") or 0),
            "rt_count": int(rt.get("count") or 0),
            "profit_factor": rt.get("profit_factor"),
            "verdict": verdict,
        }
        rows.append(row)
        print(
            f"[{sym}] {opp} dir={direction} net={row['net_pnl']:+.0f} "
            f"RT={row['rt_count']} PF={row['profit_factor']} -> {verdict}"
        )

    df = pd.DataFrame(rows)
    out_csv = OUT_DIR / f"cta_promote_{opp}_{direction}.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    payload = {
        "status": "DONE",
        "opp_family": opp,
        "direction": direction,
        "rows": rows,
        "any_keep": any(r["verdict"] == "KEEP_CANDIDATE" for r in rows),
        "note": "历史窗最多 PROVISIONAL；CONFIRMED_ALPHA 须 2026-05-17+ holdout",
    }
    (OUT_DIR / "cta_promote_result.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"wrote {out_csv}")


if __name__ == "__main__":
    main()
