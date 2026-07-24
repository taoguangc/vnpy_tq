"""STRAT_SZL_EXP002 — H_EDGE for STRAT_SMC_ZSCORE_LONG_01@0.1.0（rb/2024）.

Delegation-25BH Observation. Gate template = prior CID H_EDGE A/B.
Parent: STRAT_SZL_EXP001.
≠ Alpha Candidate · ≠ parameter search · ≠ rewrite Closed EXPs.
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
from strategies.paaf.strat_smc_zscore_long_01 import StratSmcZscoreLong01Strategy

EXPERIMENT_ID = "STRAT_SZL_EXP002"
EXPECTED_SOURCE_HASH = (
    "d7b250179147bf61f6b55c0197abcb8deb6bb4db1a3b987e3b12e7c55830ec14"
)
EXPECTED_PARAMETER_HASH = (
    "de4e92d2e55be6526c6452ed1dbea4d11b99a9f09ea6de855980045967109836"
)
BINDING_PATHS = [
    "strategies/paaf/detectors/smc_zscore_long.py",
    "strategies/paaf/strat_smc_zscore_long_01.py",
]
DETECTOR_BINDING = "SMC_ZSCORE_LONG@1.0.0"
FREEZE_ID = "SIF_CID_014_V0_1"
OUT_DIR = ROOT / "research" / "output" / "evidence" / EXPERIMENT_ID

WARMUP = datetime(2023, 12, 1)
PERIOD_START = datetime(2024, 1, 1)
PERIOD_END = datetime(2024, 12, 31)
MIN_N = 50
SHARE_GATE = 0.55
ALPHA = 0.05


def _source_hash():
    manifest = []
    for rel in sorted(BINDING_PATHS):
        digest = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        manifest.append({"path": rel, "sha256": digest})
    canon = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canon.encode()).hexdigest(), manifest


def _parameter_hash():
    params = {
        "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
        "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
        "min_risk_ticks": {"type": "float", "unit": "ticks", "value": 5.0},
        "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
        "stop_buffer": {"type": "float", "unit": "ticks", "value": 2.0},
        "stop_lookback": {"type": "int", "unit": "bars_5m", "value": 5},
        "vwap_length": {"type": "int", "unit": "bars_5m", "value": 60},
        "zscore_threshold": {"type": "float", "unit": "dimensionless", "value": 2.5},
    }
    canon = json.dumps(params, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def _one_sided_ttest_gt_zero(values):
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


def _in_window(dt):
    if dt is None:
        return False
    cmp = dt.replace(tzinfo=None) if getattr(dt, "tzinfo", None) else dt
    return PERIOD_START <= cmp <= PERIOD_END


def main():
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
    engine.add_strategy(StratSmcZscoreLong01Strategy, {})

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
        engine.get_all_trades(), size=10, rate=0.00003, slippage=1.0, capital=200_000,
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
        if mfe_vals else float("nan")
    )
    mean_net = sum(net_pnls) / n if n else float("nan")
    t_stat, p_one = _one_sided_ttest_gt_zero(net_pnls) if n >= 2 else (float("nan"), float("nan"))

    structure_ok = n_struct >= MIN_N and median_mfe > median_mae and share >= SHARE_GATE
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
    with (OUT_DIR / "trades_audit.csv").open("w", newline="", encoding="utf-8") as fh:
        fields = ["exit_reason", "mfe_ticks", "mae_ticks", "holding_minutes", "direction", "entry_time", "exit_time"]
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for item in log_rows:
            row = {k: item.get(k) for k in fields}
            for k in ("entry_time", "exit_time"):
                v = row.get(k)
                if hasattr(v, "isoformat"):
                    row[k] = v.isoformat()
            w.writerow(row)

    with (OUT_DIR / "round_trips.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["exit_time", "net_pnl"])
        w.writeheader()
        for trip in rt_in_window:
            et = trip.exit_time
            w.writerow({"exit_time": et.isoformat() if hasattr(et, "isoformat") else et, "net_pnl": trip.net_pnl})

    diagnostics = {
        "n_trade_log": n_struct, "n_round_trips": n, "min_n": MIN_N,
        "median_mfe_ticks": median_mfe, "median_mae_ticks": median_mae,
        "share_mfe_gt_mae": share, "mean_net_pnl": mean_net,
        "t_stat": t_stat, "p_one_sided_gt0": p_one,
        "structure_ok": structure_ok, "expectancy_ok": expectancy_ok,
        "share_gate": SHARE_GATE, "alpha": ALPHA, "n_gate": n_gate,
    }
    (OUT_DIR / "edge_diagnostics.json").write_text(json.dumps(diagnostics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    meta = {
        "experiment_id": EXPERIMENT_ID,
        "status": "OBSERVATION_COMPLETE",
        "authorization": "Delegation-25BH Observation",
        "hypothesis_family": "H_EDGE",
        "not_hypothesis": ["H_MECH", "H_ALPHA_CANDIDATE", "H_ALPHA_VERIFIED"],
        "parent_experiment": "STRAT_SZL_EXP001",
        "symbol": "rb", "period": "2024",
        "outcome": outcome, "outcome_reason": reason,
        "diagnostics": diagnostics,
        "source_hash": source_hash, "parameter_hash": parameter_hash,
        "source_manifest": manifest, "freeze_id": FREEZE_ID,
        "strategy_version": "0.1.0", "detector_binding": DETECTOR_BINDING,
        "engine_total_net_pnl": stats.get("total_net_pnl"),
        "alpha_claim": False, "alpha_candidate": False, "bindable": False,
    }
    (OUT_DIR / "run_metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"outcome": outcome, "reason": reason, **diagnostics}, ensure_ascii=False, indent=2))
    return 0 if outcome != "REVERT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
