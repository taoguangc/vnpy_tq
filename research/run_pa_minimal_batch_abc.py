# -*- coding: utf-8 -*-
"""pa_minimal 连续批次：B 一致性 → A 关 VSA → C 背景替代。

用法::
  python -m research.run_pa_minimal_batch_abc --symbol rb
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

from scripts.backtest_trade_analysis import summarize_round_trips
from strategies.pa_minimal.backtest import run_minimal_backtest


def _filter_setups(trips: list, prefixes: tuple[str, ...]) -> list:
    return [t for t in trips if (t.setup or "").startswith(prefixes)]


def _row(label: str, bt: dict) -> dict:
    stats = bt["stats"]
    trips = bt["round_trips"]
    rt = summarize_round_trips(trips) or {}
    t08 = _filter_setups(trips, ("OPP08_",))
    t16 = _filter_setups(trips, ("OPP16_",))
    other = [t for t in trips if not (t.setup or "").startswith(("OPP08_", "OPP16_"))]
    funnel = bt.get("candidate_funnel") or {}
    end_bal = stats.get("end_balance")
    bankrupt = end_bal is not None and float(end_bal) <= 0
    pnl = stats.get("total_net_pnl")
    if bankrupt:
        pnl = sum(t.net_pnl for t in trips)
    return {
        "label": label,
        "pnl": pnl,
        "bankrupt": bankrupt,
        "sharpe": stats.get("sharpe_ratio"),
        "mdd_pct": stats.get("max_ddpercent"),
        "rt": rt.get("total", 0),
        "wr": rt.get("win_rate"),
        "pf": rt.get("profit_factor"),
        "opp08_n": len(t08),
        "opp08_pnl": sum(t.net_pnl for t in t08),
        "opp16_n": len(t16),
        "opp16_pnl": sum(t.net_pnl for t in t16),
        "other_n": len(other),
        "candidates": funnel.get("candidates", 0),
        "gate_pass": funnel.get("gate_pass", 0),
        "armed": funnel.get("armed", 0),
        "blocks": str(funnel.get("blocks", {})),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="pa_minimal B→A→C batch")
    parser.add_argument("--symbol", default="rb")
    parser.add_argument("--output-dir", default=str(ROOT / "research" / "output"))
    args = parser.parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== pa_minimal 连续批次 B→A→C | {args.symbol} ===\n")
    rows: list[dict] = []

    # ----- B: dry-scan vs candidate ledger -----
    print("\n===== B: dry-scan（干扫） vs 候选账本一致性 =====")
    bt_b = run_minimal_backtest(
        symbol=args.symbol,
        verbose=False,
        strategy_overrides={"dryscan_compare_enabled": True},
    )
    cmp = bt_b.get("dryscan_compare") or {}
    funnel_b = bt_b.get("candidate_funnel") or {}
    print(f"候选账本: candidates={funnel_b.get('candidates')} "
          f"gate_pass={funnel_b.get('gate_pass')} armed={funnel_b.get('armed')}")
    print(
        f"对照: bars_checked={cmp.get('bars_checked')} "
        f"bars_with_signal={cmp.get('bars_with_signal')} "
        f"exact_match_bars={cmp.get('exact_match_bars')} "
        f"mismatch_bars={cmp.get('mismatch_bars')} "
        f"minimal_only={cmp.get('minimal_only')} dry_only={cmp.get('dry_only')}"
    )
    if cmp.get("mismatch_samples"):
        print("mismatch 样例(最多5):")
        for s in cmp["mismatch_samples"][:5]:
            print(f"  {s}")
    cmp_path = out_dir / f"exp_m0_dryscan_compare_{args.symbol.lower()}.json"
    cmp_path.write_text(json.dumps(cmp, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"对照输出: {cmp_path}")
    consistent = int(cmp.get("mismatch_bars", -1)) == 0
    print(f"一致性结论: {'PASS' if consistent else 'FAIL'}")
    row_b = _row("B-COMPARE-BASE", bt_b)
    rows.append(row_b)

    if not consistent:
        print("\n一致性 FAIL — 按协议停止后续消融（避免在污染定义上比收益）。")
        df = pd.DataFrame(rows)
        path = out_dir / f"exp_m0_batch_abc_{args.symbol.lower()}.csv"
        df.to_csv(path, index=False, encoding="utf-8-sig")
        print(df.to_string(index=False))
        print(f"输出: {path}")
        return

    # ----- A: VSA OFF -----
    print("\n===== A: M1-02 关 VSA（量价过滤）=====")
    bt_a = run_minimal_backtest(
        symbol=args.symbol,
        verbose=True,
        strategy_overrides={"vsa_enabled": False},
    )
    row_a = _row("M1-02-no-vsa", bt_a)
    rows.append(row_a)
    print(
        f"摘要: PnL={row_a['pnl']:+,.0f} RT={row_a['rt']} "
        f"cand={row_a['candidates']}→{row_a['gate_pass']}"
    )

    # ----- C1: R²+CHOP 三态背景 -----
    print("\n===== C1: R²+CHOP 三态替代 Brooks 背景 =====")
    bt_c1 = run_minimal_backtest(
        symbol=args.symbol,
        verbose=True,
        strategy_overrides={"context_mode": "r2_chop"},
    )
    row_c1 = _row("C1-r2-chop", bt_c1)
    rows.append(row_c1)
    print(
        f"摘要: PnL={row_c1['pnl']:+,.0f} RT={row_c1['rt']} "
        f"cand={row_c1['candidates']}→{row_c1['gate_pass']}"
    )

    # ----- C2: VWAP 三态背景（关 Dual Core，避免与 VWAP 背景双重计）-----
    print("\n===== C2: VWAP 三态背景（Dual Core 关）=====")
    bt_c2 = run_minimal_backtest(
        symbol=args.symbol,
        verbose=True,
        strategy_overrides={
            "context_mode": "vwap_tri",
            "dual_core_enabled": False,
        },
    )
    row_c2 = _row("C2-vwap-tri", bt_c2)
    rows.append(row_c2)
    print(
        f"摘要: PnL={row_c2['pnl']:+,.0f} RT={row_c2['rt']} "
        f"cand={row_c2['candidates']}→{row_c2['gate_pass']}"
    )

    # 附上 M0-BASE 参考行（来自上一轮 CSV，若不存在则本批 B 行即 BASE）
    df = pd.DataFrame(rows)
    path = out_dir / f"exp_m0_batch_abc_{args.symbol.lower()}.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print("\n===== 并列汇总 =====")
    print(df.to_string(index=False))
    print(f"\n输出: {path}")


if __name__ == "__main__":
    main()
