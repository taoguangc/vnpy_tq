"""CTX_CID002_EXP002 — H_CTX_FILTER temporal OOS（rb/2025 · B0 vs B1）.

Identical Filter F1 and MECH @0.1.1 as EXP001; period is the OOS dimension.
Does not mutate G5 binding strategy bytes.
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
from strategies.paaf.brooks_scalp_paaf_strategy_v011 import BrooksScalpPaafStrategyV011
from strategies.paaf.context_consumer.brooks_scalp_ctx_filter_v011 import (
    BrooksScalpCtxFilterV011,
)

EXPERIMENT_ID = "CTX_CID002_EXP002"
EXPECTED_SOURCE_HASH = (
    "1877dffe2108ba4237469b52bccc589d479811d4aea82c2764900cf74ad1d4c8"
)
EXPECTED_PARAMETER_HASH = (
    "3ff061891488a9d9f5641cf147efc1e70c8d4cb8410540858d8b727bd485d1ab"
)
BINDING_PATHS = [
    "strategies/paaf/brooks_scalp_paaf_strategy.py",
    "strategies/paaf/brooks_scalp_paaf_strategy_v011.py",
    "strategies/paaf/detectors/brooks_scalp_first_pullback.py",
]
DETECTOR_BINDING = "BROOKS_SCALP_FP@0.1.0"
OUT_DIR = ROOT / "research" / "output" / "evidence" / EXPERIMENT_ID

WARMUP = datetime(2024, 12, 1)
PERIOD_START = datetime(2025, 1, 1)
PERIOD_END = datetime(2025, 12, 31)


def _source_hash() -> tuple[str, list[dict[str, str]]]:
    manifest = []
    for rel in sorted(BINDING_PATHS):
        digest = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        manifest.append({"path": rel, "sha256": digest})
    canon = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canon.encode()).hexdigest(), manifest


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


def _period_rows(trade_log: list[dict]) -> list[dict]:
    rows = []
    allowed = {"STOP", "TARGET", "TIME_STOP"}
    for item in trade_log:
        et = item.get("exit_time")
        if et is None:
            continue
        exit_cmp = et.replace(tzinfo=None) if getattr(et, "tzinfo", None) else et
        if exit_cmp < PERIOD_START:
            continue
        reason = item.get("exit_reason")
        if reason not in allowed:
            continue
        rows.append(item)
    return rows


def _run(strategy_cls) -> tuple[list[dict], list[dict], dict]:
    bars = load_stitched_raw_bars("rb", Exchange.SHFE, start=WARMUP, end=PERIOD_END)
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
    engine.add_strategy(strategy_cls, {})
    buf = io.StringIO()
    with redirect_stdout(buf):
        engine.run_backtesting()
        df = engine.calculate_result()
        stats = engine.calculate_statistics(df, output=False)
    trade_log = list(getattr(engine.strategy, "_trade_log", []) or [])
    rows = _period_rows(trade_log)
    denials = list(getattr(engine.strategy, "_permission_denials", []) or [])
    meta = {
        "closed_auditable": len(rows),
        "denial_count": len(denials),
        "total_net_pnl_descriptive": stats.get("total_net_pnl"),
    }
    return rows, denials, meta


def _write_trades(path: Path, rows: list[dict], *, arm: str) -> None:
    fields = [
        "arm",
        "experiment_id",
        "exit_reason",
        "direction",
        "strategy_version",
        "detector_binding",
        "entry_time",
        "exit_time",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for item in rows:
            et = item.get("entry_time")
            xt = item.get("exit_time")
            w.writerow(
                {
                    "arm": arm,
                    "experiment_id": EXPERIMENT_ID,
                    "exit_reason": item.get("exit_reason"),
                    "direction": item.get("direction"),
                    "strategy_version": item.get("strategy_version"),
                    "detector_binding": DETECTOR_BINDING,
                    "entry_time": et.isoformat() if hasattr(et, "isoformat") else et,
                    "exit_time": xt.isoformat() if hasattr(xt, "isoformat") else xt,
                }
            )


def _evaluate(n0: int, n1: int, d: int, source_ok: bool, param_ok: bool) -> tuple[str, str]:
    if not source_ok or not param_ok:
        return "REVERT", "identity hash mismatch"
    if n0 < 1:
        return "HOLD", "baseline N0 < 1"
    if n1 == n0 and d == 0:
        return "HOLD", "filter inert on OOS（N1==N0 and D==0）"
    if n1 != n0 or d >= 1:
        return (
            "KEEP",
            f"filter non-inert on OOS 2025：N0={n0} N1={n1} D={d}; "
            f"exits detector-attributed; Context did not generate entries",
        )
    return "HOLD", "inconclusive"


def main() -> int:
    source_hash, manifest = _source_hash()
    parameter_hash = _parameter_hash()
    source_ok = source_hash == EXPECTED_SOURCE_HASH
    param_ok = parameter_hash == EXPECTED_PARAMETER_HASH
    print(f"experiment_id={EXPERIMENT_ID}")
    print(f"source_hash match={source_ok} parameter_hash match={param_ok}")
    if not source_ok or not param_ok:
        print("ABORT", source_hash, parameter_hash)
        return 2

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "pre_registration.json").write_text(
        json.dumps(
            {
                "experiment_id": EXPERIMENT_ID,
                "status": "PRE_REGISTERED",
                "authorization": "Delegation-50J",
                "hypothesis_family": "H_CTX_FILTER",
                "oos_of": "CTX_CID002_EXP001",
                "period": "2025",
                "filter_id": "F1_EXPANSION_ONLY",
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    print("running B0 baseline（unfiltered V011 · 2025）...")
    rows0, _, meta0 = _run(BrooksScalpPaafStrategyV011)
    print(f"B0 N0={len(rows0)}")

    print("running B1 filtered（V011+F1 · 2025）...")
    rows1, denials, meta1 = _run(BrooksScalpCtxFilterV011)
    print(f"B1 N1={len(rows1)} D={len(denials)}")

    n0, n1, d = len(rows0), len(rows1), len(denials)
    outcome, reason = _evaluate(n0, n1, d, source_ok, param_ok)

    _write_trades(OUT_DIR / "baseline_trades_audit.csv", rows0, arm="B0")
    _write_trades(OUT_DIR / "filtered_trades_audit.csv", rows1, arm="B1")
    with (OUT_DIR / "permission_denials.csv").open("w", newline="", encoding="utf-8") as f:
        fields = [
            "event",
            "context_state",
            "filter_id",
            "signal_reason",
            "direction",
            "entry",
        ]
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for row in denials:
            w.writerow(row)

    denial_states: dict[str, int] = {}
    for row in denials:
        st = str(row.get("context_state") or "unknown")
        denial_states[st] = denial_states.get(st, 0) + 1
    (OUT_DIR / "context_state_sample.json").write_text(
        json.dumps(
            {
                "note": "denial-side context_state counts（B1 · 2025 OOS）",
                "denial_state_counts": denial_states,
                "context_version": "A1-CTX-PS-v1.0.0",
                "filter_id": "F1_EXPANSION_ONLY",
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    run_meta = {
        "experiment_id": EXPERIMENT_ID,
        "status": "OBSERVATION_COMPLETE",
        "authorization": "Delegation-50J",
        "hypothesis_family": "H_CTX_FILTER",
        "oos_of": "CTX_CID002_EXP001",
        "period": "2025",
        "consumer_surface": "MECH",
        "consumer_contract": "CC-CID_002-v1",
        "source_hash": source_hash,
        "parameter_hash": parameter_hash,
        "source_manifest": manifest,
        "source_ok": source_ok,
        "param_ok": param_ok,
        "N0": n0,
        "N1": n1,
        "D": d,
        "B0_meta": meta0,
        "B1_meta": meta1,
        "outcome": outcome,
        "reason": reason,
        "pnl_not_decision_metric": True,
        "alpha_claim": False,
        "rc001_b_reopened": False,
        "g5_bytes_mutated": False,
    }
    (OUT_DIR / "run_metadata.json").write_text(
        json.dumps(run_meta, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"outcome": outcome, "reason": reason, "N0": n0, "N1": n1, "D": d}, indent=2))
    return 0 if outcome != "REVERT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
