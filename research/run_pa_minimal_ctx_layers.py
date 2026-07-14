# -*- coding: utf-8 -*-
"""CTX layers: gate OFF vs ON 单变量对照（pa_minimal rb）。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from strategies.pa_minimal.backtest import run_minimal_backtest


def summarize(label: str, bt: dict) -> tuple[float, int, dict]:
    stats = bt["stats"]
    trips = bt["round_trips"]
    funnel = bt.get("candidate_funnel") or {}
    net = float(stats.get("total_net_pnl") or sum(t.net_pnl for t in trips))
    sharpe = float(stats.get("sharpe_ratio") or 0)
    mdd = float(stats.get("max_ddpercent") or 0)
    wr = float(stats.get("win_rate") or 0)
    print(f"===== {label} =====")
    print(
        f"net={net:+,.0f} sharpe={sharpe:.2f} mdd={mdd:.1f}% "
        f"n={len(trips)} wr={wr:.1f}%"
    )
    print(
        f"candidates={funnel.get('candidates')} "
        f"gate_pass={funnel.get('gate_pass')} "
        f"armed={funnel.get('armed')} "
        f"blocks={funnel.get('blocks')}"
    )
    by: dict[str, list] = {}
    for t in trips:
        k = (t.setup or "")[:32]
        by.setdefault(k, [0, 0.0])
        by[k][0] += 1
        by[k][1] += t.net_pnl
    for k, (n, p) in sorted(by.items()):
        print(f"  {k}: n={n} pnl={p:+,.0f}")
    return net, len(trips), funnel


def main() -> None:
    print("pa_minimal rb | CTX layers gate OFF vs ON")
    bt0 = run_minimal_backtest(symbol="rb", verbose=False)
    n0, t0, _ = summarize("GATE_OFF (default)", bt0)
    bt1 = run_minimal_backtest(
        symbol="rb",
        verbose=False,
        strategy_overrides={"context_layer_gate_enabled": True},
    )
    n1, t1, _ = summarize("GATE_ON", bt1)
    print("===== DELTA ON-OFF =====")
    print(f"delta_net={n1 - n0:+,.0f} delta_n={t1 - t0}")


if __name__ == "__main__":
    main()
