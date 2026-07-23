"""STRAT_RO15_EXP001 — H_MECH smoke for STRAT_REV_OPP15_01@0.1.0.

PRE-REGISTERED under SEVF Fill. Authorization: Delegation-25AM.
≠ Alpha · ≠ H_EDGE · ≠ Bindable · ≠ parameter search.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vnpy.trader.constant import Exchange, Interval

from scripts.rollover_backtest_engine import RolloverBacktestingEngine
from scripts.tq_rollover_data import build_rollover_events, load_stitched_raw_bars
from strategies.paaf.strat_rev_opp15_01 import StratRevOpp1501Strategy

EXPERIMENT_ID = "STRAT_RO15_EXP001"
EXPECTED_SOURCE_HASH = (
    "1b0f5858d8d22371906085cdf974b8378e60d6bdb8c3924a509bfce62e9cb8a1"
)
EXPECTED_PARAMETER_HASH = (
    "960b1ae8abdf5011f6d7977bf99c4bae7a8f8264721afca0488e687b539af9f6"
)
BINDING_PATHS = [
    "strategies/paaf/detectors/opp15_wedge_path_a.py",
    "strategies/paaf/morphology/wedge.py",
    "strategies/paaf/strat_rev_opp15_01.py",
]
DETECTOR_BINDING = "OPP15@1.0.0"
FREEZE_ID = "SIF_CID_009_V0_1"
STRATEGY_VERSION = "0.1.0"
OUT_DIR = ROOT / "research" / "output" / "evidence" / EXPERIMENT_ID

WARMUP = datetime(2023, 12, 1)
PERIOD_START = datetime(2024, 1, 1)
PERIOD_END = datetime(2024, 12, 31)


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
        "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
        "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
        "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
        "strong_bar_atr_mult": {"type": "float", "unit": "atr_multiple", "value": 1.0},
        "strong_bar_body_ratio": {"type": "float", "unit": "fraction", "value": 0.6},
        "wedge_alpha_threshold": {"type": "float", "unit": "fraction", "value": 0.85},
        "wedge_arm_trigger_max_bars": {"type": "int", "unit": "bars", "value": 4},
        "wedge_n_min": {"type": "int", "unit": "bars", "value": 3},
    }
    canon = json.dumps(params, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


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
    engine.add_strategy(StratRevOpp1501Strategy, {})

    buf = io.StringIO()
    with redirect_stdout(buf):
        engine.run_backtesting()
        df = engine.calculate_result()
        stats = engine.calculate_statistics(df, output=False)
    log_text = buf.getvalue()

    missing_hook_warn = "未实现 on_rollover_adjust" in log_text
    adjust_seen = "on_rollover_adjust shift=" in log_text

    trade_log = list(getattr(engine.strategy, "_trade_log", []) or [])
    rows = []
    for item in trade_log:
        et = item.get("exit_time")
        if et is None:
            continue
        exit_cmp = et.replace(tzinfo=None) if getattr(et, "tzinfo", None) else et
        if exit_cmp < PERIOD_START or exit_cmp > PERIOD_END:
            continue
        rows.append(
            {
                "experiment_id": EXPERIMENT_ID,
                "strategy_id": "STRAT_REV_OPP15_01",
                "strategy_version": STRATEGY_VERSION,
                "freeze_id": FREEZE_ID,
                "detector_binding": DETECTOR_BINDING,
                "source_hash": source_hash,
                "parameter_hash": parameter_hash,
                "exit_reason": item.get("exit_reason"),
                "entry_time": item.get("entry_time"),
                "exit_time": item.get("exit_time"),
                "direction": item.get("direction"),
                "mfe_ticks": item.get("mfe_ticks"),
                "mae_ticks": item.get("mae_ticks"),
            }
        )

    allowed = {"STOP", "TARGET", "TIME_STOP"}
    attributed = sum(1 for r in rows if r["exit_reason"] in allowed)
    if missing_hook_warn:
        outcome, reason = "REVERT", "missing on_rollover_adjust WARN present"
    elif not rows or attributed < 1:
        outcome, reason = "HOLD", "no auditable attributed exits"
    else:
        outcome, reason = (
            "KEEP",
            f"auditable_trades={len(rows)}; attributed={attributed}; "
            f"adjust_log_seen={adjust_seen}",
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUT_DIR / "trades_audit.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        fieldnames = list(rows[0].keys()) if rows else ["experiment_id"]
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            out = dict(row)
            for k in ("entry_time", "exit_time"):
                v = out.get(k)
                if hasattr(v, "isoformat"):
                    out[k] = v.isoformat()
            w.writerow(out)

    meta = {
        "experiment_id": EXPERIMENT_ID,
        "status": "OBSERVATION_COMPLETE",
        "authorization": "Delegation-25AM（Authorize Offline Observation for STRAT_RO15_EXP001）",
        "hypothesis_family": "H_MECH",
        "not_hypothesis": ["H_EDGE", "H_ALPHA", "H_NULL"],
        "symbol": "rb",
        "period": "2024",
        "outcome": outcome,
        "outcome_reason": reason,
        "missing_hook_warn": missing_hook_warn,
        "adjust_log_seen": adjust_seen,
        "closed_trade_count": len(rows),
        "attributed_exit_count": attributed,
        "source_hash": source_hash,
        "parameter_hash": parameter_hash,
        "source_manifest": manifest,
        "strategy_version": STRATEGY_VERSION,
        "freeze_id": FREEZE_ID,
        "detector_binding": DETECTOR_BINDING,
        "engine_total_net_pnl": stats.get("total_net_pnl"),
        "alpha_claim": False,
        "bindable": False,
        "trades_audit_csv": str(csv_path.relative_to(ROOT)).replace("\\", "/"),
    }
    (OUT_DIR / "run_metadata.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    print(f"outcome={outcome}")
    print(f"reason={reason}")
    print(f"closed={len(rows)} attributed={attributed}")
    return 0 if outcome != "REVERT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
