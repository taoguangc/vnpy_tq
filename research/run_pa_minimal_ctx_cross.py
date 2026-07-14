# -*- coding: utf-8 -*-
"""跨品种 GATE_OFF vs GATE_ON（context_layer_gate）对照扫描。

品种池：CROSS_SYMBOL_UNIVERSE（i/jm/p/y/ag/rb/hc/ta）
协议：每品种 2 次回测（关闸 / 开闸），含成本，整窗。

用法::
  python -m research.run_pa_minimal_ctx_cross
  python -m research.run_pa_minimal_ctx_cross --symbols rb,hc,ag
"""
from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from strategies.pa_cta.symbol_config import cross_symbol_list
from strategies.pa_minimal.backtest import run_minimal_backtest


def _tier(net: float, sharpe: float) -> str:
    if net > 3000 and sharpe > 0.8:
        return "PROFIT"
    if net > 0:
        return "MARGINAL"
    return "LOSS"


def _opp_pnl(trips: list) -> dict[str, tuple[int, float]]:
    out: dict[str, tuple[int, float]] = {
        "OPP08": (0, 0.0),
        "OPP16": (0, 0.0),
    }
    for t in trips:
        setup = t.setup or ""
        if setup.startswith("OPP08_"):
            key = "OPP08"
        elif setup.startswith("OPP16_"):
            key = "OPP16"
        else:
            continue
        n, p = out[key]
        out[key] = (n + 1, p + t.net_pnl)
    return out


def run_one(symbol: str, *, gate_on: bool) -> dict:
    overrides = {"context_layer_gate_enabled": True} if gate_on else None
    bt = run_minimal_backtest(
        symbol=symbol,
        verbose=False,
        strategy_overrides=overrides,
    )
    stats = bt["stats"]
    trips = bt["round_trips"]
    funnel = bt.get("candidate_funnel") or {}
    blocks = funnel.get("blocks") or {}
    net = float(stats.get("total_net_pnl") or sum(t.net_pnl for t in trips))
    sharpe = float(stats.get("sharpe_ratio") or 0.0)
    mdd = float(stats.get("max_ddpercent") or 0.0)
    opp = _opp_pnl(trips)
    return {
        "symbol": symbol.lower(),
        "gate": "ON" if gate_on else "OFF",
        "net": net,
        "sharpe": sharpe,
        "mdd_pct": mdd,
        "n_rt": len(trips),
        "candidates": funnel.get("candidates"),
        "gate_pass": funnel.get("gate_pass"),
        "ctx_blocks": int(blocks.get("context_layer", 0) or 0),
        "vsa_blocks": int(blocks.get("vsa", 0) or 0),
        "dual_blocks": int(blocks.get("dual_core", 0) or 0),
        "opp08_n": opp["OPP08"][0],
        "opp08_pnl": opp["OPP08"][1],
        "opp16_n": opp["OPP16"][0],
        "opp16_pnl": opp["OPP16"][1],
        "tier": _tier(net, sharpe),
        "error": "",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="pa_minimal ctx gate cross-symbol")
    parser.add_argument(
        "--symbols",
        default=",".join(cross_symbol_list()),
        help="逗号分隔品种，默认 CROSS_SYMBOL_UNIVERSE",
    )
    parser.add_argument("--output-dir", default=str(ROOT / "research" / "output"))
    args = parser.parse_args()
    symbols = [s.strip().lower() for s in args.symbols.split(",") if s.strip()]
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=== pa_minimal CTX GATE 跨品种 OFF vs ON ===")
    print(f"品种: {symbols}")
    print("配置: MINIMAL_BASE + 单变量 context_layer_gate_enabled\n")

    rows: list[dict] = []
    for sym in symbols:
        for gate_on in (False, True):
            label = "ON" if gate_on else "OFF"
            print(f"--- {sym} GATE_{label} ---", flush=True)
            try:
                row = run_one(sym, gate_on=gate_on)
            except Exception as exc:  # noqa: BLE001 — 扫描须吞单品种失败
                traceback.print_exc()
                row = {
                    "symbol": sym,
                    "gate": label,
                    "net": float("nan"),
                    "sharpe": float("nan"),
                    "mdd_pct": float("nan"),
                    "n_rt": 0,
                    "candidates": None,
                    "gate_pass": None,
                    "ctx_blocks": 0,
                    "vsa_blocks": 0,
                    "dual_blocks": 0,
                    "opp08_n": 0,
                    "opp08_pnl": 0.0,
                    "opp16_n": 0,
                    "opp16_pnl": 0.0,
                    "tier": "ERROR",
                    "error": str(exc)[:200],
                }
            rows.append(row)
            print(
                f"  net={row['net']:+,.0f} sharpe={row['sharpe']:.2f} "
                f"n={row['n_rt']} ctx_blocks={row['ctx_blocks']} "
                f"tier={row['tier']}",
                flush=True,
            )

    detail = pd.DataFrame(rows)
    detail_path = out_dir / "exp_ctx_gate_cross_detail.csv"
    detail.to_csv(detail_path, index=False, encoding="utf-8-sig")

    # 宽表：每品种一行 OFF/ON/Δ
    summary_rows: list[dict] = []
    for sym in symbols:
        off = detail[(detail["symbol"] == sym) & (detail["gate"] == "OFF")]
        on = detail[(detail["symbol"] == sym) & (detail["gate"] == "ON")]
        if off.empty or on.empty:
            continue
        o, n = off.iloc[0], on.iloc[0]
        d_net = n["net"] - o["net"] if pd.notna(n["net"]) and pd.notna(o["net"]) else float("nan")
        summary_rows.append(
            {
                "symbol": sym,
                "off_net": o["net"],
                "on_net": n["net"],
                "delta_net": d_net,
                "off_sharpe": o["sharpe"],
                "on_sharpe": n["sharpe"],
                "off_n": int(o["n_rt"]),
                "on_n": int(n["n_rt"]),
                "delta_n": int(n["n_rt"]) - int(o["n_rt"]),
                "ctx_blocks": int(n["ctx_blocks"]),
                "off_tier": o["tier"],
                "on_tier": n["tier"],
                "off_opp08_pnl": o["opp08_pnl"],
                "on_opp08_pnl": n["opp08_pnl"],
                "off_opp16_pnl": o["opp16_pnl"],
                "on_opp16_pnl": n["opp16_pnl"],
            }
        )

    summary = pd.DataFrame(summary_rows)
    summary_path = out_dir / "exp_ctx_gate_cross_summary.csv"
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")

    print("\n===== 汇总 OFF → ON =====")
    print(
        f"{'品种':<4} {'OFF净盈亏':>10} {'ON净盈亏':>10} {'Δ净盈亏':>10} "
        f"{'OFF n':>5} {'ON n':>5} {'ctx拦':>5} {'OFF档':>8} {'ON档':>8}"
    )
    for _, r in summary.iterrows():
        print(
            f"{r['symbol']:<4} {r['off_net']:>+10,.0f} {r['on_net']:>+10,.0f} "
            f"{r['delta_net']:>+10,.0f} {int(r['off_n']):>5} {int(r['on_n']):>5} "
            f"{int(r['ctx_blocks']):>5} {r['off_tier']:>8} {r['on_tier']:>8}"
        )

    improved = summary[summary["delta_net"] > 0]["symbol"].tolist() if not summary.empty else []
    worsened = summary[summary["delta_net"] < 0]["symbol"].tolist() if not summary.empty else []
    on_profit = summary[summary["on_tier"] == "PROFIT"]["symbol"].tolist() if not summary.empty else []
    on_marg = summary[summary["on_tier"] == "MARGINAL"]["symbol"].tolist() if not summary.empty else []
    on_loss = summary[summary["on_tier"] == "LOSS"]["symbol"].tolist() if not summary.empty else []

    print("\n----- 聚类（GATE_ON）-----")
    print(f"PROFIT:   {on_profit or '—'}")
    print(f"MARGINAL: {on_marg or '—'}")
    print(f"LOSS:     {on_loss or '—'}")
    print(f"Δ净盈亏>0: {improved or '—'}")
    print(f"Δ净盈亏<0: {worsened or '—'}")
    print(f"\n输出: {detail_path}")
    print(f"输出: {summary_path}")


if __name__ == "__main__":
    main()
