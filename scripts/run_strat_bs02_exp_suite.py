"""STRAT_BS02 EXP002/EXP003 Observation runner（Delegation-50）.

Does not modify frozen strategy/detector source bytes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vnpy.trader.constant import Exchange, Interval

from scripts.backtest_trade_analysis import pair_round_trips
from scripts.rollover_backtest_engine import RolloverBacktestingEngine
from scripts.tq_rollover_data import build_rollover_events, load_stitched_raw_bars
from strategies.paaf.brooks_scalp_paaf_strategy import BrooksScalpPaafStrategy

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
DETECTOR_BINDING = "BROOKS_SCALP_FP@0.1.0"
STRATEGY_ID = "STRAT_TREND_BROOKS_SCALP_02"
VERSION = "0.1.0"
FREEZE_ID = "SIF_CID_002_V0_1"

PREFIX = "rb"
EXCHANGE = Exchange.SHFE
SIZE = 10.0
PRICETICK = 1.0
RATE = 0.00003
SLIPPAGE = 1.0
CAPITAL = 200_000.0

CONFIGS = {
    "STRAT_BS02_EXP002": {
        "family": "H_NULL",
        "warmup": datetime(2023, 12, 1),
        "period_start": datetime(2024, 1, 1),
        "period_end": datetime(2024, 12, 31),
        "mode": "null",
    },
    "STRAT_BS02_EXP003": {
        "family": "H_ROBUST",
        "warmup": datetime(2024, 12, 1),
        "period_start": datetime(2025, 1, 1),
        "period_end": datetime(2025, 12, 31),
        "mode": "mech",
        "mech_source": "roundtrip_join",
    },
    "STRAT_BS02_EXP004": {
        "family": "H_ROBUST",
        "warmup": datetime(2024, 12, 1),
        "period_start": datetime(2025, 1, 1),
        "period_end": datetime(2025, 12, 31),
        "mode": "mech",
        "mech_source": "strategy_trade_log",
    },
}


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


def _t_test_mu0(values: list[float]) -> tuple[float, float, float]:
    """Return mean, t_stat, two-sided p using normal approx if scipy absent."""
    n = len(values)
    mean = sum(values) / n
    if n < 2:
        return mean, float("nan"), float("nan")
    var = sum((x - mean) ** 2 for x in values) / (n - 1)
    se = math.sqrt(var / n) if var > 0 else 0.0
    if se == 0.0:
        # Exact zero variance: if mean==0, p=1; else p=0
        return mean, float("inf") if mean != 0 else 0.0, 0.0 if mean != 0 else 1.0
    t_stat = mean / se
    # SciPy if available
    try:
        from scipy import stats  # type: ignore

        p = float(stats.t.sf(abs(t_stat), df=n - 1) * 2)
    except Exception:
        # Normal approximation for large n
        p = float(math.erfc(abs(t_stat) / math.sqrt(2.0)))
    return mean, float(t_stat), p


def _evaluate_null(rows: list[dict], source_ok: bool, param_ok: bool) -> tuple[str, str, dict]:
    if not source_ok or not param_ok:
        return "REVERT", "identity hash mismatch", {}
    pnls = [float(r["net_pnl"]) for r in rows]
    n = len(pnls)
    if n < 30:
        return "HOLD", f"n={n}<30", {"n": n}
    mean, t_stat, p = _t_test_mu0(pnls)
    stats = {"n": n, "mean_net_pnl": mean, "t_stat": t_stat, "p_value": p, "alpha": 0.05}
    if p < 0.05:
        return (
            "REVERT",
            f"reject μ=0 at α=0.05 (p={p:.4g}, mean={mean:.4f})",
            stats,
        )
    return (
        "KEEP",
        f"fail to reject μ=0 at α=0.05 (p={p:.4g}, mean={mean:.4f})",
        stats,
    )


def _evaluate_mech(rows: list[dict], source_ok: bool, param_ok: bool) -> tuple[str, str, dict]:
    if not source_ok or not param_ok:
        return "REVERT", "identity hash mismatch", {}
    if not rows:
        return "HOLD", "closed_trade_count=0", {"n": 0}
    allowed = {"STOP", "TARGET", "TIME_STOP"}
    ok = 0
    for row in rows:
        if row.get("detector_binding") != DETECTOR_BINDING:
            return "REVERT", "trade without detector attribution", {}
        if row.get("exit_reason") in allowed:
            ok += 1
    if ok < 1:
        return "HOLD", "no allowed exit_reason", {"n": len(rows)}
    return "KEEP", f"auditable closed_trade_count={len(rows)}", {"n": len(rows)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp", required=True, choices=sorted(CONFIGS))
    args = parser.parse_args()
    exp_id = args.exp
    cfg = CONFIGS[exp_id]
    out_dir = ROOT / "research" / "output" / "evidence" / exp_id
    out_dir.mkdir(parents=True, exist_ok=True)

    source_hash, manifest = _canonical_source_hash()
    parameter_hash = _parameter_hash()
    source_ok = source_hash == EXPECTED_SOURCE_HASH
    param_ok = parameter_hash == EXPECTED_PARAMETER_HASH
    print(f"experiment_id={exp_id}")
    print(f"source_hash match={source_ok} parameter_hash match={param_ok}")
    if not source_ok or not param_ok:
        meta = {
            "experiment_id": exp_id,
            "outcome": "REVERT",
            "reason": "identity hash mismatch — abort",
            "observation_executed": False,
        }
        (out_dir / "run_metadata.json").write_text(
            json.dumps(meta, indent=2) + "\n", encoding="utf-8"
        )
        return 2

    warmup = cfg["warmup"]
    period_start = cfg["period_start"]
    period_end = cfg["period_end"]
    vt_symbol = f"{PREFIX}.{EXCHANGE.value}"
    print(f"loading {vt_symbol} {warmup.date()} .. {period_end.date()}")
    bars = load_stitched_raw_bars(PREFIX, EXCHANGE, start=warmup, end=period_end)
    if not bars:
        print("no bars")
        return 1
    actual_start, actual_end = bars[0].datetime, bars[-1].datetime
    events = build_rollover_events(PREFIX, start=actual_start, end=actual_end)
    print(f"bars={len(bars)} rollovers={len(events)}")

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
    engine.set_rollover_events(events)
    engine.add_strategy(BrooksScalpPaafStrategy, {})
    engine.run_backtesting()
    df = engine.calculate_result()
    stats = engine.calculate_statistics(df, output=False)

    strategy = engine.strategy
    trade_log = list(getattr(strategy, "_trade_log", []) or [])
    reason_by_exit: dict[str, str] = {}
    for item in trade_log:
        et = item.get("exit_time")
        if et is None:
            continue
        key = et.isoformat() if hasattr(et, "isoformat") else str(et)
        reason_by_exit[key] = str(item.get("exit_reason") or "")

    round_trips = pair_round_trips(
        engine.get_all_trades(),
        size=SIZE,
        rate=RATE,
        slippage=SLIPPAGE,
        capital=CAPITAL,
    )

    rows: list[dict] = []
    mech_source = cfg.get("mech_source", "roundtrip_join")
    if cfg["mode"] == "mech" and mech_source == "strategy_trade_log":
        for item in trade_log:
            exit_time = item.get("exit_time")
            if exit_time is None:
                continue
            exit_cmp = (
                exit_time.replace(tzinfo=None) if getattr(exit_time, "tzinfo", None) else exit_time
            )
            if exit_cmp < period_start:
                continue
            rows.append(
                {
                    "experiment_id": exp_id,
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
                    "net_pnl": "",
                    "gross_pnl": "",
                    "volume": "",
                }
            )
    else:
        for rt in round_trips:
            exit_time = rt.exit_time
            exit_cmp = (
                exit_time.replace(tzinfo=None) if getattr(exit_time, "tzinfo", None) else exit_time
            )
            if exit_cmp < period_start:
                continue
            exit_key = exit_time.isoformat()
            exit_reason = reason_by_exit.get(exit_key) or rt.exit_reason or "UNKNOWN"
            if exit_reason == "UNKNOWN":
                for k, v in reason_by_exit.items():
                    if k.startswith(exit_time.strftime("%Y-%m-%dT%H:%M")):
                        exit_reason = v
                        break
            rows.append(
                {
                    "experiment_id": exp_id,
                    "strategy_id": STRATEGY_ID,
                    "strategy_version": VERSION,
                    "freeze_id": FREEZE_ID,
                    "detector_binding": DETECTOR_BINDING,
                    "source_hash": source_hash,
                    "parameter_hash": parameter_hash,
                    "symbol": PREFIX,
                    "direction": rt.direction,
                    "entry_time": rt.entry_time,
                    "exit_time": rt.exit_time,
                    "exit_reason": exit_reason,
                    "net_pnl": rt.net_pnl,
                    "gross_pnl": rt.gross_pnl,
                    "volume": rt.volume,
                }
            )

    if cfg["mode"] == "null":
        outcome, reason, test_stats = _evaluate_null(rows, source_ok, param_ok)
    else:
        outcome, reason, test_stats = _evaluate_mech(rows, source_ok, param_ok)

    csv_path = out_dir / "trades_roundtrips.csv"
    fields = [
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
        "net_pnl",
        "gross_pnl",
        "volume",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for row in rows:
            out = dict(row)
            for k in ("entry_time", "exit_time"):
                v = out.get(k)
                out[k] = v.isoformat() if hasattr(v, "isoformat") else v
            w.writerow(out)

    exit_counts: dict[str, int] = {}
    for row in rows:
        k = str(row.get("exit_reason") or "other")
        exit_counts[k] = exit_counts.get(k, 0) + 1

    meta = {
        "experiment_id": exp_id,
        "status": "OBSERVATION_COMPLETE",
        "authorization": "Delegation-50",
        "hypothesis_family": cfg["family"],
        "mech_source": cfg.get("mech_source"),
        "outcome": outcome,
        "outcome_reason": reason,
        "test_stats": test_stats,
        "uncertainty": (
            "Same rollover on_rollover_adjust gap as EXP001; "
            "H_NULL uses round-trip net_pnl after costs; "
            "descriptive engine stats are not KEEP drivers for H_ROBUST."
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
            "period_start": period_start.date().isoformat(),
            "period_end": period_end.date().isoformat(),
            "warmup_start": warmup.date().isoformat(),
            "data_protocol_version": "docs/07_DATA_SPEC.md@1.0.0",
        },
        "cost_binding": "PROJECT_FROZEN_DATA_PROTOCOL",
        "fill_binding": "VNPY_CTA_BACKTEST_ENGINE_DEFAULTS_AT_EXP_REGISTRATION",
        "rate": RATE,
        "slippage": SLIPPAGE,
        "closed_trade_count": len(rows),
        "exit_reason_counts": exit_counts,
        "engine_total_net_pnl": stats.get("total_net_pnl"),
        "engine_sharpe_ratio": stats.get("sharpe_ratio"),
        "engine_max_ddpercent": stats.get("max_ddpercent"),
        "trades_csv": str(csv_path.relative_to(ROOT)).replace("\\", "/"),
        "alpha_claim": False,
        "bindable": False,
    }
    (out_dir / "run_metadata.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    print(f"closed_trade_count={len(rows)}")
    print(f"outcome={outcome}")
    print(f"reason={reason}")
    print(f"test_stats={test_stats}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
