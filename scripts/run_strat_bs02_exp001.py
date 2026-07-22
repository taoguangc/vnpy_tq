"""STRAT_BS02_EXP001 — SEVF Observation runner（H_MECH）.

Authorized by: Authorize SEVF Observation for STRAT_BS02_EXP001
Does not modify frozen strategy/detector source bytes.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vnpy.trader.constant import Exchange, Interval

from scripts.rollover_backtest_engine import RolloverBacktestingEngine
from scripts.tq_rollover_data import build_rollover_events, load_stitched_raw_bars
from strategies.paaf.brooks_scalp_paaf_strategy import BrooksScalpPaafStrategy

EXPERIMENT_ID = "STRAT_BS02_EXP001"
FREEZE_ID = "SIF_CID_002_V0_1"
STRATEGY_ID = "STRAT_TREND_BROOKS_SCALP_02"
VERSION = "0.1.0"
DETECTOR_BINDING = "BROOKS_SCALP_FP@0.1.0"

EXPECTED_SOURCE_HASH = (
    "3ba12893e43db6805e5af2012d811a7f0034143dbedb102637afd7a5819b9589"
)
EXPECTED_PARAMETER_HASH = (
    "3ff061891488a9d9f5641cf147efc1e70c8d4cb8410540858d8b727bd485d1ab"
)

BINDING_PATHS = [
    "strategies/paaf/brooks_scalp_paaf_strategy.py",
    "strategies/paaf/detectors/brooks_scalp_first_pullback.py",
]

OUT_DIR = ROOT / "research" / "output" / "evidence" / "STRAT_BS02_EXP001"

WARMUP_START = datetime(2023, 12, 1)
PERIOD_START = datetime(2024, 1, 1)
PERIOD_END = datetime(2024, 12, 31)

PREFIX = "rb"
EXCHANGE = Exchange.SHFE
SIZE = 10
PRICETICK = 1.0
RATE = 0.00003
SLIPPAGE = 1.0
CAPITAL = 200_000


def _canonical_source_hash() -> tuple[str, list[dict[str, str]]]:
    manifest: list[dict[str, str]] = []
    for rel in sorted(BINDING_PATHS):
        raw = (ROOT / rel).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        manifest.append({"path": rel.replace("\\", "/"), "sha256": digest})
    canon = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest(), manifest


def _parameter_hash() -> str:
    params = {
        "atr_period": {"type": "int", "unit": "bars", "value": 20},
        "ema_period": {"type": "int", "unit": "bars", "value": 20},
        "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
        "max_hold_bars": {"type": "int", "unit": "bars", "value": 10},
        "pullback_atr": {"type": "float", "unit": "atr_multiple", "value": 0.2},
        "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
        "trend_leg_atr": {"type": "float", "unit": "atr_multiple", "value": 1.0},
    }
    canon = json.dumps(params, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def _evaluate(
    *,
    source_ok: bool,
    param_ok: bool,
    rows: list[dict],
) -> tuple[str, str]:
    if not source_ok or not param_ok:
        return "REVERT", "identity hash mismatch vs SIF_CID_002_V0_1"
    if not rows:
        return "HOLD", "run completed with identity echo but closed_trade_count=0"
    allowed = {"STOP", "TARGET", "TIME_STOP"}
    attributed = 0
    for row in rows:
        if row.get("detector_binding") != DETECTOR_BINDING:
            return "REVERT", "trade without detector attribution"
        if row.get("exit_reason") in allowed:
            attributed += 1
    if attributed < 1:
        return "HOLD", "trades present but no exit_reason in STOP/TARGET/TIME_STOP"
    return (
        "KEEP",
        f"auditable closed_trade_count={len(rows)} with detector attribution "
        f"and allowed exit reasons",
    )


def main() -> int:
    source_hash, manifest = _canonical_source_hash()
    parameter_hash = _parameter_hash()
    source_ok = source_hash == EXPECTED_SOURCE_HASH
    param_ok = parameter_hash == EXPECTED_PARAMETER_HASH

    print(f"experiment_id={EXPERIMENT_ID}")
    print(f"source_hash={source_hash} match={source_ok}")
    print(f"parameter_hash={parameter_hash} match={param_ok}")
    if not source_ok or not param_ok:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        meta = {
            "experiment_id": EXPERIMENT_ID,
            "outcome": "REVERT",
            "reason": "identity hash mismatch — abort before observation",
            "source_hash": source_hash,
            "expected_source_hash": EXPECTED_SOURCE_HASH,
            "parameter_hash": parameter_hash,
            "expected_parameter_hash": EXPECTED_PARAMETER_HASH,
            "observation_executed": False,
        }
        (OUT_DIR / "run_metadata.json").write_text(
            json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print("ABORT: identity mismatch")
        return 2

    vt_symbol = f"{PREFIX}.{EXCHANGE.value}"
    print(
        f"loading CbC 1m {vt_symbol} {WARMUP_START.date()} .. {PERIOD_END.date()} ..."
    )
    bars = load_stitched_raw_bars(
        PREFIX,
        EXCHANGE,
        start=WARMUP_START,
        end=PERIOD_END,
    )
    if not bars:
        print("no bars loaded")
        return 1

    actual_start = bars[0].datetime
    actual_end = bars[-1].datetime
    rollover_events = build_rollover_events(
        PREFIX, start=actual_start, end=actual_end
    )
    print(
        f"bars={len(bars)} ({actual_start} .. {actual_end}) "
        f"rollovers={len(rollover_events)}"
    )

    engine = RolloverBacktestingEngine()
    engine.set_parameters(
        vt_symbol=vt_symbol,
        interval=Interval.MINUTE,
        start=actual_start,
        end=actual_end,
        rate=RATE,
        slippage=SLIPPAGE,
        size=SIZE,
        pricetick=PRICETICK,
        capital=CAPITAL,
    )
    engine.history_data = bars
    engine.set_rollover_events(rollover_events)
    engine.add_strategy(BrooksScalpPaafStrategy, {})
    engine.run_backtesting()
    df = engine.calculate_result()
    stats = engine.calculate_statistics(df, output=False)

    strategy = engine.strategy
    trade_log = list(getattr(strategy, "_trade_log", []) or [])

    eval_rows: list[dict] = []
    for item in trade_log:
        exit_time = item.get("exit_time")
        if exit_time is None:
            continue
        if getattr(exit_time, "replace", None):
            exit_naive = exit_time.replace(tzinfo=None) if exit_time.tzinfo else exit_time
        else:
            exit_naive = exit_time
        if exit_naive < PERIOD_START:
            continue
        eval_rows.append(
            {
                "experiment_id": EXPERIMENT_ID,
                "strategy_id": STRATEGY_ID,
                "strategy_version": VERSION,
                "freeze_id": FREEZE_ID,
                "detector_binding": DETECTOR_BINDING,
                "source_hash": source_hash,
                "parameter_hash": parameter_hash,
                "symbol": PREFIX,
                "direction": item.get("direction"),
                "entry_time": item.get("entry_time"),
                "exit_time": item.get("exit_time"),
                "exit_reason": item.get("exit_reason"),
                "mfe_ticks": item.get("mfe_ticks"),
                "mae_ticks": item.get("mae_ticks"),
                "holding_minutes": item.get("holding_minutes"),
            }
        )

    outcome, reason = _evaluate(
        source_ok=source_ok,
        param_ok=param_ok,
        rows=eval_rows,
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUT_DIR / "trades_audit.csv"
    fieldnames = [
        "experiment_id",
        "strategy_id",
        "strategy_version",
        "freeze_id",
        "detector_binding",
        "source_hash",
        "parameter_hash",
        "symbol",
        "direction",
        "entry_time",
        "exit_time",
        "exit_reason",
        "mfe_ticks",
        "mae_ticks",
        "holding_minutes",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in eval_rows:
            out = dict(row)
            for key in ("entry_time", "exit_time"):
                val = out.get(key)
                out[key] = val.isoformat() if hasattr(val, "isoformat") else val
            writer.writerow(out)

    exit_counts: dict[str, int] = {}
    for row in eval_rows:
        key = str(row.get("exit_reason") or "other")
        exit_counts[key] = exit_counts.get(key, 0) + 1

    meta = {
        "experiment_id": EXPERIMENT_ID,
        "status": "OBSERVATION_COMPLETE",
        "authorization": "Authorize SEVF Observation for STRAT_BS02_EXP001",
        "hypothesis_family": "H_MECH",
        "outcome": outcome,
        "outcome_reason": reason,
        "uncertainty": (
            "Single-symbol in-sample mechanism test only; "
            "PnL metrics are descriptive and not KEEP drivers; "
            "detector attribution stamped from exclusive strategy binding."
        ),
        "strategy_id": STRATEGY_ID,
        "version": VERSION,
        "freeze_id": FREEZE_ID,
        "detector_binding": DETECTOR_BINDING,
        "source_hash": source_hash,
        "parameter_hash": parameter_hash,
        "source_manifest": manifest,
        "market_scope": {
            "symbols": [PREFIX],
            "period_start": PERIOD_START.date().isoformat(),
            "period_end": PERIOD_END.date().isoformat(),
            "warmup_start": WARMUP_START.date().isoformat(),
            "data_protocol_version": "docs/07_DATA_SPEC.md@1.0.0",
        },
        "cost_binding": "PROJECT_FROZEN_DATA_PROTOCOL",
        "fill_binding": "VNPY_CTA_BACKTEST_ENGINE_DEFAULTS_AT_EXP_REGISTRATION",
        "rate": RATE,
        "slippage": SLIPPAGE,
        "size": SIZE,
        "pricetick": PRICETICK,
        "capital": CAPITAL,
        "bars": len(bars),
        "bar_start": str(actual_start),
        "bar_end": str(actual_end),
        "rollover_count": getattr(engine.rollover_stats, "count", 0),
        "closed_trade_count": len(eval_rows),
        "exit_reason_counts": exit_counts,
        "engine_total_trade_count": stats.get("total_trade_count"),
        "engine_total_net_pnl": stats.get("total_net_pnl"),
        "engine_sharpe_ratio": stats.get("sharpe_ratio"),
        "engine_max_ddpercent": stats.get("max_ddpercent"),
        "trades_audit_csv": str(csv_path.relative_to(ROOT)).replace("\\", "/"),
        "alpha_claim": False,
        "bindable": False,
    }
    (OUT_DIR / "run_metadata.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )

    print(f"closed_trade_count={len(eval_rows)}")
    print(f"exit_reason_counts={exit_counts}")
    print(f"outcome={outcome}")
    print(f"reason={reason}")
    print(f"wrote {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
