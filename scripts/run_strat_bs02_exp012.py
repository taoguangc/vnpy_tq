"""STRAT_BS02_EXP012 — H_CAPITAL_GATE temporal OOS for @0.2.0.

Universe predeclared: {rb, i, MA} · 2025 · capital=200_000.
Closes R-RISK-OOS if all symbols avoid capital≤0 under @0.2.0 controls.

≠ H_MECH · ≠ Alpha · ≠ Bindable · ≠ PnL gate.
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
from strategies.paaf.brooks_scalp_paaf_strategy_v020 import BrooksScalpPaafStrategyV020

EXPERIMENT_ID = "STRAT_BS02_EXP012"
EXPECTED_SOURCE_HASH = (
    "5c089251ac301cf7d5c8f72c25960d5a1e50b90907319d0e6bd54fa3880e2499"
)
EXPECTED_PARAMETER_HASH = (
    "7ff1fe9976ba809dce8f38325c33e6b7bf11a0817b2dce6d372f32258a7da346"
)
BINDING_PATHS = [
    "strategies/paaf/brooks_scalp_paaf_strategy.py",
    "strategies/paaf/brooks_scalp_paaf_strategy_v011.py",
    "strategies/paaf/brooks_scalp_paaf_strategy_v020.py",
    "strategies/paaf/detectors/brooks_scalp_first_pullback.py",
]
DETECTOR_BINDING = "BROOKS_SCALP_FP@0.1.0"
OUT_DIR = ROOT / "research" / "output" / "evidence" / EXPERIMENT_ID

WARMUP = datetime(2024, 12, 1)
PERIOD_START = datetime(2025, 1, 1)
PERIOD_END = datetime(2025, 12, 31)
CAPITAL = 200_000

SYMBOL_SPEC = {
    "rb": {"exchange": Exchange.SHFE, "size": 10, "pricetick": 1.0},
    "i": {"exchange": Exchange.DCE, "size": 100, "pricetick": 0.5},
    "MA": {"exchange": Exchange.CZCE, "size": 10, "pricetick": 1.0},
}


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
        "capital_floor_ratio": {"type": "float", "unit": "fraction_of_capital", "value": 0.5},
        "ema_period": {"type": "int", "unit": "bars", "value": 20},
        "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
        "hard_max_lots": {"type": "int", "unit": "contracts", "value": 1},
        "max_hold_bars": {"type": "int", "unit": "bars", "value": 10},
        "pullback_atr": {"type": "float", "unit": "atr_multiple", "value": 0.2},
        "risk_per_trade": {"type": "float", "unit": "fraction_of_equity", "value": 0.005},
        "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
        "sizing_mode": {"type": "str", "unit": "enum", "value": "RISK_FRACTION_OF_CAPITAL"},
        "trend_leg_atr": {"type": "float", "unit": "atr_multiple", "value": 1.0},
    }
    canon = json.dumps(params, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def _run_one(symbol: str) -> dict:
    spec = SYMBOL_SPEC[symbol]
    exchange = spec["exchange"]
    bars = load_stitched_raw_bars(symbol, exchange, start=WARMUP, end=PERIOD_END)
    if not bars:
        return {
            "symbol": symbol,
            "outcome": "HOLD",
            "reason": "no_bars",
            "capital_breach": None,
        }
    events = build_rollover_events(symbol, start=bars[0].datetime, end=bars[-1].datetime)
    engine = RolloverBacktestingEngine()
    engine.set_parameters(
        vt_symbol=f"{symbol}.{exchange.value}",
        interval=Interval.MINUTE,
        start=bars[0].datetime,
        end=bars[-1].datetime,
        rate=0.00003,
        slippage=1.0,
        size=spec["size"],
        pricetick=spec["pricetick"],
        capital=CAPITAL,
    )
    engine.history_data = bars
    engine.set_rollover_events(events)
    engine.add_strategy(BrooksScalpPaafStrategyV020, {})

    buf = io.StringIO()
    with redirect_stdout(buf):
        engine.run_backtesting()
        df = engine.calculate_result()
        stats = engine.calculate_statistics(df, output=False)

    strat = engine.strategy
    trade_log = list(getattr(strat, "_trade_log", []) or [])
    closed = 0
    for item in trade_log:
        et = item.get("exit_time")
        if et is None:
            continue
        exit_cmp = et.replace(tzinfo=None) if getattr(et, "tzinfo", None) else et
        if exit_cmp >= PERIOD_START:
            closed += 1

    end_balance = stats.get("end_balance")
    if end_balance is not None:
        end_balance = float(end_balance)
    positive_balance = True
    if df is not None and len(df) > 0 and "balance" in df.columns:
        positive_balance = bool((df["balance"] > 0).all())
    capital_breach = (end_balance is not None and end_balance <= 0) or (not positive_balance)

    kill_events = int(getattr(strat, "kill_events", 0) or 0)
    skip_zero = int(getattr(strat, "skip_zero_lot", 0) or 0)
    halted = bool(getattr(strat, "entries_halted", False))
    equity_est = float(getattr(strat, "equity_est", 0) or 0)

    if capital_breach:
        outcome = "REVERT"
        reason = "capital_breach under @0.2.0 controls"
    else:
        outcome = "KEEP"
        reason = (
            f"no capital<=0; closed={closed}; kill_events={kill_events}; "
            f"halted={halted}; skip_zero_lot={skip_zero}"
        )

    return {
        "symbol": symbol,
        "outcome": outcome,
        "reason": reason,
        "closed_trade_count": closed,
        "kill_events": kill_events,
        "skip_zero_lot": skip_zero,
        "entries_halted": halted,
        "end_balance": end_balance,
        "equity_est_end": equity_est,
        "capital_breach": capital_breach,
        "positive_balance": positive_balance,
        "contract_size": spec["size"],
    }


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

    per_symbol = []
    for symbol in ("rb", "i", "MA"):
        print(f"running {symbol} ...")
        row = _run_one(symbol)
        per_symbol.append(row)
        print(json.dumps(row, ensure_ascii=False, default=str))

    outcomes = [r["outcome"] for r in per_symbol]
    if any(o == "REVERT" for o in outcomes):
        bundle_outcome = "REVERT"
        bundle_reason = "at least one symbol capital_breach"
    elif any(o == "HOLD" for o in outcomes):
        bundle_outcome = "HOLD"
        bundle_reason = "incomplete symbol set"
    elif all(o == "KEEP" for o in outcomes):
        bundle_outcome = "KEEP"
        bundle_reason = (
            "all symbols {rb,i,MA} avoided capital<=0 under @0.2.0 on 2025 OOS"
        )
    else:
        bundle_outcome = "HOLD"
        bundle_reason = "unexpected outcome mix"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary_csv = OUT_DIR / "per_symbol_summary.csv"
    with summary_csv.open("w", newline="", encoding="utf-8") as f:
        fields = [
            "symbol",
            "outcome",
            "closed_trade_count",
            "kill_events",
            "skip_zero_lot",
            "end_balance",
            "capital_breach",
            "contract_size",
        ]
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for row in per_symbol:
            w.writerow(row)

    meta = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis": "H_CAPITAL_GATE",
        "not_hypothesis": ["H_MECH", "H_NULL", "H_ALPHA"],
        "gap_target": "R-RISK-OOS",
        "strategy_id": "STRAT_TREND_BROOKS_SCALP_02",
        "strategy_version": "0.2.0",
        "freeze_id": "SIF_CID_002_V0_2_0",
        "source_hash": source_hash,
        "parameter_hash": parameter_hash,
        "source_manifest": manifest,
        "detector_binding": DETECTOR_BINDING,
        "consumer_surface": "RISK",
        "consumer_contract": "CC-CID_002-v1",
        "universe": ["rb", "i", "MA"],
        "capital_assumption": CAPITAL,
        "sizing_mode": "RISK_FRACTION_OF_CAPITAL",
        "period": "2025",
        "oos_vs": "EXP008-010/2024",
        "per_symbol": per_symbol,
        "outcome": bundle_outcome,
        "reason": bundle_reason,
        "bindable": False,
        "alpha_claim": False,
    }
    (OUT_DIR / "run_metadata.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {"outcome": bundle_outcome, "reason": bundle_reason},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if bundle_outcome != "REVERT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
