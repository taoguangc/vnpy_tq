"""STRAT_RO17_EXP003 — H_EDGE multi-year sample for STRAT_REV_OPP17_01@0.1.0（rb/2023–2024）.

Delegation-25W Observation. Gates identical to EXP002; window expands for n only.
≠ Alpha Candidate · ≠ parameter search · ≠ rewrite EXP001/002 · ≠ lower MIN_N.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import sys
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vnpy.trader.constant import Exchange, Interval

from scripts.backtest_trade_analysis import pair_round_trips
from scripts.rollover_backtest_engine import RolloverBacktestingEngine
from scripts.tq_rollover_data import build_rollover_events, load_stitched_raw_bars
from strategies.paaf.strat_rev_opp17_01 import StratRevOpp1701Strategy

EXPERIMENT_ID = "STRAT_RO17_EXP003"
EXPECTED_SOURCE_HASH = (
    "9d85cf960f30715524f7224bdf3dd9750ce4fd1ad86a79d9122789c75e5cb576"
)
EXPECTED_PARAMETER_HASH = (
    "40ef1e1d594294e89e9872f08c5ac5d057dc36156081784e030c072fd19b0816"
)
BINDING_PATHS = [
    "strategies/paaf/detectors/opp17_climax_reversal.py",
    "strategies/paaf/strat_rev_opp17_01.py",
]
DETECTOR_BINDING = "OPP17@1.0.0"
FREEZE_ID = "SIF_CID_005_V0_1"
OUT_DIR = ROOT / "research" / "output" / "evidence" / EXPERIMENT_ID

WARMUP = datetime(2022, 12, 1)
PERIOD_START = datetime(2023, 1, 1)
PERIOD_END = datetime(2024, 12, 31)
MIN_N = 50
SHARE_GATE = 0.55
ALPHA = 0.05


def _source_hash() -> tuple[str, list[dict[str, str]]]:
    manifest = []
    for rel in sorted(BINDING_PATHS):
        digest = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        manifest.append({"path": rel, "sha256": digest})
    canon = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canon.encode()).hexdigest(), manifest


def _parameter_hash() -> str:
    params = {
        "atr_period": {"type": "int", "unit": "bars", "value": 14},
        "climax_range_atr": {"type": "float", "unit": "atr_multiple", "value": 2.5},
        "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
        "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
        "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
    }
    canon = json.dumps(params, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def _one_sided_ttest_gt_zero(values: list[float]) -> tuple[float, float]:
    n = len(values)
    if n < 2:
        return float("nan"), float("nan")
    mean = sum(values) / n
    var = sum((x - mean) ** 2 for x in values) / (n - 1)
    if var <= 0:
        if mean > 0:
            return float("inf"), 0.0
        return 0.0, 1.0
    t_stat = mean / math.sqrt(var / n)
    p_one = 0.5 * math.erfc(t_stat / math.sqrt(2.0))
    return t_stat, p_one


def _in_window(dt: datetime | None) -> bool:
    if dt is None:
        return False
    cmp = dt.replace(tzinfo=None) if getattr(dt, "tzinfo", None) else dt
    return PERIOD_START <= cmp <= PERIOD_END


def main() -> int:
    source_hash, manifest = _source_hash()
    parameter_hash = _parameter_hash()
    source_ok = source_hash == EXPECTED_SOURCE_HASH
    param_ok = parameter_hash == EXPECTED_PARAMETER_HASH
    print(f"experiment_id={EXPERIMENT_ID}")
    print(f"source_hash match={source_ok} parameter_hash match={param_ok}")
    if not source_ok or not param_ok:
        print("ABORT hash mismatch", source_hash, parameter_hash)
        return 2

    bars = load_stitched_raw_bars("rb", Exchange.SHFE, start=WARMUP, end=PERIOD_END)
    if not bars:
        print("no bars")
        return 1
    events = build_rollover_events("rb", start=bars[0].datetime, end=bars[-1].datetime)
    engine = RolloverBacktestingEngine()
    engine.set_parameters(
        vt_symbol="rb.SHFE",
        interval=Interval.MINUTE,
        start=bars[0].datetime,
        end=bars[-1].datetime,
        rate=0.00003,
        slippage=1.0,
        size=10,
        pricetick=1.0,
        capital=200_000,
    )
    engine.history_data = bars
    engine.set_rollover_events(events)
    engine.add_strategy(StratRevOpp1701Strategy, {})

    buf = io.StringIO()
    with redirect_stdout(buf):
        engine.run_backtesting()
        df = engine.calculate_result()
        stats = engine.calculate_statistics(df, output=False)

    trade_log = list(getattr(engine.strategy, "_trade_log", []) or [])
    log_rows = [item for item in trade_log if _in_window(item.get("exit_time"))]
    mfe_vals = [float(item.get("mfe_ticks") or 0.0) for item in log_rows]
    mae_vals = [float(item.get("mae_ticks") or 0.0) for item in log_rows]

    round_trips = pair_round_trips(
        engine.get_all_trades(),
        size=10,
        rate=0.00003,
        slippage=1.0,
        capital=200_000,
    )
    rt_in_window = [trip for trip in round_trips if _in_window(trip.exit_time)]
    net_pnls = [float(trip.net_pnl) for trip in rt_in_window]
    n = len(net_pnls)
    n_struct = len(log_rows)
    n_gate = min(n, n_struct) if (n and n_struct) else max(n, n_struct)

    median_mfe = median(mfe_vals) if mfe_vals else float("nan")
    median_mae = median(mae_vals) if mae_vals else float("nan")
    share = (
        sum(1 for mfe, mae in zip(mfe_vals, mae_vals) if mfe > mae) / len(mfe_vals)
        if mfe_vals
        else float("nan")
    )
    mean_net = sum(net_pnls) / n if n else float("nan")
    t_stat, p_one = _one_sided_ttest_gt_zero(net_pnls) if n >= 2 else (float("nan"), float("nan"))

    structure_ok = (
        n_struct >= MIN_N and median_mfe > median_mae and share >= SHARE_GATE
    )
    expectancy_ok = n >= MIN_N and mean_net > 0 and p_one < ALPHA

    if n_gate < MIN_N:
        outcome, reason = "HOLD", f"n_gate={n_gate} < {MIN_N}"
    elif structure_ok and expectancy_ok:
        outcome, reason = "KEEP", "structure_A and expectancy_B both PASS"
    else:
        outcome, reason = "REVERT", (
            f"structure_ok={structure_ok} expectancy_ok={expectancy_ok} "
            f"median_mfe={median_mfe:.4f} median_mae={median_mae:.4f} "
            f"share={share:.4f} mean_net={mean_net:.4f} p_one={p_one}"
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    audit_csv = OUT_DIR / "trades_audit.csv"
    with audit_csv.open("w", newline="", encoding="utf-8") as fh:
        fields = [
            "exit_reason",
            "mfe_ticks",
            "mae_ticks",
            "holding_minutes",
            "direction",
            "entry_time",
            "exit_time",
        ]
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for item in log_rows:
            row = {k: item.get(k) for k in fields}
            for k in ("entry_time", "exit_time"):
                v = row.get(k)
                if hasattr(v, "isoformat"):
                    row[k] = v.isoformat()
            w.writerow(row)

    rt_csv = OUT_DIR / "round_trips.csv"
    with rt_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["exit_time", "net_pnl"])
        w.writeheader()
        for trip in rt_in_window:
            et = trip.exit_time
            w.writerow(
                {
                    "exit_time": et.isoformat() if hasattr(et, "isoformat") else et,
                    "net_pnl": trip.net_pnl,
                }
            )

    diagnostics = {
        "n_trade_log": n_struct,
        "n_round_trips": n,
        "min_n": MIN_N,
        "median_mfe_ticks": median_mfe,
        "median_mae_ticks": median_mae,
        "share_mfe_gt_mae": share,
        "mean_net_pnl": mean_net,
        "t_stat": t_stat,
        "p_one_sided_gt0": p_one,
        "structure_ok": structure_ok,
        "expectancy_ok": expectancy_ok,
        "share_gate": SHARE_GATE,
        "alpha": ALPHA,
        "n_gate": n_gate,
    }
    (OUT_DIR / "edge_diagnostics.json").write_text(
        json.dumps(diagnostics, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    meta = {
        "experiment_id": EXPERIMENT_ID,
        "status": "OBSERVATION_COMPLETE",
        "authorization": "Delegation-25W Observation（授权你决定25次）",
        "hypothesis_family": "H_EDGE",
        "not_hypothesis": ["H_MECH", "H_ALPHA_CANDIDATE", "H_ALPHA_VERIFIED"],
        "parent_experiment": "STRAT_RO17_EXP002",
        "symbol": "rb",
        "period": "2023-2024",
        "sample_purpose": "multi_year_n_adjudication_same_gates",
        "outcome": outcome,
        "outcome_reason": reason,
        "diagnostics": diagnostics,
        "source_hash": source_hash,
        "parameter_hash": parameter_hash,
        "source_manifest": manifest,
        "freeze_id": FREEZE_ID,
        "strategy_version": "0.1.0",
        "detector_binding": DETECTOR_BINDING,
        "engine_total_net_pnl": stats.get("total_net_pnl"),
        "alpha_claim": False,
        "alpha_candidate": False,
        "bindable": False,
        "descriptive_only": {
            "sharpe_ratio": stats.get("sharpe_ratio"),
            "max_ddpercent": stats.get("max_ddpercent"),
            "total_net_pnl": stats.get("total_net_pnl"),
        },
    }
    (OUT_DIR / "run_metadata.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"outcome": outcome, "reason": reason, **diagnostics}, ensure_ascii=False, indent=2))
    return 0 if outcome != "REVERT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
