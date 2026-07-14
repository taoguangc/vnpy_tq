# -*- coding: utf-8 -*-
"""pa_minimal M0-BASE 样本内/样本外切分报告。

协议：整窗回测 1 次，按 entry_time 切 IS/OOS（与 EXP-023/025 日历一致）。
  IS:  2023-05-17 ~ 2024-12-31
  OOS: 2025-01-01 ~ 2026-05-16

用法::
  python -m research.run_pa_minimal_is_oos --symbol rb
  python -m research.run_pa_minimal_is_oos --symbol rb --ctx-gate-on
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.backtest_trade_analysis import RoundTripTrade, summarize_round_trips
from strategies.pa_minimal.backtest import run_minimal_backtest

CST = ZoneInfo("Asia/Shanghai")

WINDOW_START = datetime(2023, 5, 17)
WINDOW_END = datetime(2026, 5, 16)
IS_START = datetime(2023, 5, 17)
IS_END = datetime(2024, 12, 31, 23, 59, 59)
OOS_START = datetime(2025, 1, 1)
OOS_END = datetime(2026, 5, 16, 23, 59, 59)


def _ts(dt: datetime) -> pd.Timestamp:
    if dt.tzinfo is None:
        return pd.Timestamp(dt, tz=CST)
    return pd.Timestamp(dt).tz_convert(CST)


def _slice(
    trips: list[RoundTripTrade],
    *,
    start: datetime,
    end: datetime,
) -> list[RoundTripTrade]:
    s, e = _ts(start), _ts(end)
    return [rt for rt in trips if s <= _ts(rt.entry_time) <= e]


def _metrics(trips: list[RoundTripTrade]) -> dict:
    if not trips:
        return {
            "n": 0,
            "wr": float("nan"),
            "pf": float("nan"),
            "net_pnl": 0.0,
            "avg_pnl": 0.0,
            "max_win": 0.0,
            "max_loss": 0.0,
            "max_abs_share": float("nan"),
            "pnl_wo_max_abs": 0.0,
        }
    summary = summarize_round_trips(trips) or {}
    nets = [t.net_pnl for t in trips]
    net = sum(nets)
    abs_idx = max(range(len(nets)), key=lambda i: abs(nets[i]))
    max_abs = abs(nets[abs_idx])
    return {
        "n": len(trips),
        "wr": summary.get("win_rate"),
        "pf": summary.get("profit_factor"),
        "net_pnl": net,
        "avg_pnl": net / len(trips),
        "max_win": max(nets),
        "max_loss": min(nets),
        "max_abs_share": max_abs / abs(net) if abs(net) > 1e-9 else float("nan"),
        "pnl_wo_max_abs": net - nets[abs_idx],
    }


def _by_opp(trips: list[RoundTripTrade]) -> list[dict]:
    groups = {
        "ALL": trips,
        "OPP08": [t for t in trips if (t.setup or "").startswith("OPP08_")],
        "OPP16": [t for t in trips if (t.setup or "").startswith("OPP16_")],
        "OTHER": [
            t
            for t in trips
            if not (t.setup or "").startswith(("OPP08_", "OPP16_"))
        ],
    }
    rows = []
    for name, subset in groups.items():
        m = _metrics(subset)
        rows.append({"group": name, **m})
    return rows


def _gate_comment(is_m: dict, oos_m: dict) -> list[str]:
    notes: list[str] = []
    n_oos = int(oos_m["n"])
    if n_oos < 8:
        notes.append(f"OOS n={n_oos}<8 → 仅记「未知」")
    elif n_oos < 15:
        notes.append(f"OOS n={n_oos}∈[8,14] → HOLD 级样本，不可强结论")
    else:
        notes.append(f"OOS n={n_oos}≥15 → 可进入 OOS 门禁讨论")

    is_pnl = float(is_m["net_pnl"])
    oos_pnl = float(oos_m["net_pnl"])
    if is_pnl == 0 or oos_pnl == 0:
        notes.append("IS/OOS 一方净盈亏为 0，同向判定弱")
    elif (is_pnl > 0) == (oos_pnl > 0):
        notes.append(f"IS/OOS 同向（均为{'正' if is_pnl > 0 else '负'}）")
    else:
        notes.append("IS/OOS 不同向")

    share = oos_m.get("max_abs_share")
    if share == share and share is not None and share >= 0.5:
        notes.append(f"OOS 单笔极端占比 {share:.0%}（≥50% 视为主导风险）")
    return notes


def main() -> None:
    parser = argparse.ArgumentParser(description="pa_minimal M0-BASE IS/OOS")
    parser.add_argument("--symbol", default="rb")
    parser.add_argument(
        "--ctx-gate-on",
        action="store_true",
        help="开启 context_layer_gate_enabled（快/慢层软门禁）",
    )
    parser.add_argument("--output-dir", default=str(ROOT / "research" / "output"))
    args = parser.parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    tag = "CTX_GATE_ON" if args.ctx_gate_on else "M0_BASE"
    overrides = {"context_layer_gate_enabled": True} if args.ctx_gate_on else None

    print(f"=== pa_minimal {tag} 样本内/样本外 ===")
    print(f"品种: {args.symbol}")
    print(f"整窗: {WINDOW_START.date()} ~ {WINDOW_END.date()}")
    print(f"IS:   {IS_START.date()} ~ {IS_END.date()}")
    print(f"OOS:  {OOS_START.date()} ~ {OOS_END.date()}")
    print(
        "配置: MINIMAL_BASE（Brooks + Dual Core + VSA"
        + (" + context_layer_gate" if args.ctx_gate_on else "")
        + "，AFF Router 关）\n"
    )

    bt = run_minimal_backtest(
        symbol=args.symbol,
        verbose=False,
        strategy_overrides=overrides,
    )
    trips = bt["round_trips"]
    funnel = bt.get("candidate_funnel") or {}
    stats = bt["stats"]

    full = _slice(trips, start=WINDOW_START, end=WINDOW_END)
    is_trips = _slice(trips, start=IS_START, end=IS_END)
    oos_trips = _slice(trips, start=OOS_START, end=OOS_END)

    print(
        f"引擎统计: PnL={stats.get('total_net_pnl'):+.0f} "
        f"Sharpe={stats.get('sharpe_ratio')} "
        f"RT={len(trips)} cand={funnel.get('candidates')}"
    )

    rows: list[dict] = []
    for window, subset in (
        ("FULL", full),
        ("IS", is_trips),
        ("OOS", oos_trips),
    ):
        for r in _by_opp(subset):
            rows.append({"window": window, **r})

    df = pd.DataFrame(rows)
    path = out_dir / f"exp_m0_is_oos_{args.symbol.lower()}{'_ctx_on' if args.ctx_gate_on else ''}.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")

    def _print_block(title: str, window: str) -> None:
        sub = df[df["window"] == window]
        print(f"\n----- {title} -----")
        print(
            f"{'分组':<8} {'n':>4} {'胜率':>7} {'PF':>6} "
            f"{'净盈亏':>10} {'均PnL':>9} {'去极值PnL':>10} {'单笔占比':>8}"
        )
        for _, r in sub.iterrows():
            wr = r["wr"]
            pf = r["pf"]
            share = r["max_abs_share"]
            wr_s = f"{wr:.1f}%" if wr == wr else "n/a"
            pf_s = f"{pf:.2f}" if pf == pf else "n/a"
            sh_s = f"{share:.0%}" if share == share else "n/a"
            print(
                f"{r['group']:<8} {int(r['n']):>4} {wr_s:>7} {pf_s:>6} "
                f"{r['net_pnl']:>+10.0f} {r['avg_pnl']:>+9.0f} "
                f"{r['pnl_wo_max_abs']:>+10.0f} {sh_s:>8}"
            )

    _print_block("全样本 FULL", "FULL")
    _print_block("样本内 IS", "IS")
    _print_block("样本外 OOS", "OOS")

    is_all = df[(df["window"] == "IS") & (df["group"] == "ALL")].iloc[0].to_dict()
    oos_all = df[(df["window"] == "OOS") & (df["group"] == "ALL")].iloc[0].to_dict()
    notes = _gate_comment(is_all, oos_all)
    print("\n----- 门禁解读（相对「可交易正期望」）-----")
    for n in notes:
        print(f"- {n}")
    print(f"- OOS 净盈亏 {oos_all['net_pnl']:+.0f} "
          f"{'未过' if oos_all['net_pnl'] <= 0 else '通过'}「OOS ΔPnL>0」门槛（基线自身）")
    for grp in ("OPP08", "OPP16"):
        is_g = df[(df["window"] == "IS") & (df["group"] == grp)].iloc[0]
        oos_g = df[(df["window"] == "OOS") & (df["group"] == grp)].iloc[0]
        same = (is_g["net_pnl"] > 0) == (oos_g["net_pnl"] > 0)
        print(
            f"- {grp}: IS {is_g['net_pnl']:+.0f} (n={int(is_g['n'])}) | "
            f"OOS {oos_g['net_pnl']:+.0f} (n={int(oos_g['n'])}) | "
            f"{'同向' if same else '异向'}"
        )

    print(f"\n输出: {path}")


if __name__ == "__main__":
    main()
