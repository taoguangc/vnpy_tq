"""STRAT_BS02_EXP011 — H_MECH temporal OOS for @0.1.1（rb/2025）.

Closes Verified residual R1 if KEEP（same-hash OOS）.
≠ Alpha · ≠ Bindable · ≠ capital surface.
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

EXPERIMENT_ID = "STRAT_BS02_EXP011"
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

WARMUP_START = datetime(2024, 12, 1)
PERIOD_START = datetime(2025, 1, 1)
PERIOD_END = datetime(2025, 12, 31)


def _source_hash() -> tuple[str, list[dict[str, str]]]:
    manifest = []
    for rel in sorted(BINDING_PATHS):
        digest = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        manifest.append({"path": rel, "sha256": digest})
    canon = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canon.encode()).hexdigest(), manifest


def main() -> int:
    source_hash, manifest = _source_hash()
    source_ok = source_hash == EXPECTED_SOURCE_HASH
    print(f"experiment_id={EXPERIMENT_ID}")
    print(f"source_hash match={source_ok}")
    if not source_ok:
        print("ABORT hash mismatch", source_hash)
        return 2

    bars = load_stitched_raw_bars("rb", Exchange.SHFE, start=WARMUP_START, end=PERIOD_END)
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
    engine.add_strategy(BrooksScalpPaafStrategyV011, {})

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
        if exit_cmp < PERIOD_START:
            continue
        rows.append(
            {
                "experiment_id": EXPERIMENT_ID,
                "strategy_id": "STRAT_TREND_BROOKS_SCALP_02",
                "strategy_version": "0.1.1",
                "freeze_id": "SIF_CID_002_V0_1_1",
                "detector_binding": DETECTOR_BINDING,
                "source_hash": source_hash,
                "parameter_hash": EXPECTED_PARAMETER_HASH,
                "exit_reason": item.get("exit_reason"),
                "entry_time": item.get("entry_time"),
                "exit_time": item.get("exit_time"),
                "direction": item.get("direction"),
            }
        )

    allowed = {"STOP", "TARGET", "TIME_STOP"}
    attributed = sum(1 for r in rows if r["exit_reason"] in allowed)
    if missing_hook_warn:
        outcome, reason = "REVERT", "missing on_rollover_adjust WARN present"
    elif not rows or attributed < 1:
        outcome, reason = "HOLD", "no auditable exits with allowed reasons"
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
        "authorization": "Delegation-100G",
        "hypothesis_family": "H_MECH",
        "validation_dimension": "temporal_OOS",
        "residual_target": "R1",
        "symbol": "rb",
        "period": "2025",
        "outcome": outcome,
        "outcome_reason": reason,
        "missing_hook_warn": missing_hook_warn,
        "adjust_log_seen": adjust_seen,
        "closed_trade_count": len(rows),
        "attributed_exit_count": attributed,
        "source_hash": source_hash,
        "parameter_hash": EXPECTED_PARAMETER_HASH,
        "source_manifest": manifest,
        "strategy_version": "0.1.1",
        "freeze_id": "SIF_CID_002_V0_1_1",
        "consumer_surface": "MECH",
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
