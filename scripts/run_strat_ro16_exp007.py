"""STRAT_RO16_EXP007 — H_CAPITAL_GATE smoke for @0.2.0 on i（≠ H_MECH）.

PRE-REGISTERED under SEVF Fill. Do NOT run without Observation auth.

Hypothesis H_CAPITAL_GATE:
  Under docs/07 · capital=200_000 · i · 2024 · frozen @0.2.0 defaults,
  positioning controls prevent engine capital≤0 death path
  OR trip equity kill-switch before wipe.

≠ Alpha · ≠ Bindable · ≠ H_MECH rewrite · ≠ parameter search.
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
from strategies.paaf.strat_rev_opp16_01_v020 import StratRevOpp1601StrategyV020

EXPERIMENT_ID = "STRAT_RO16_EXP007"
EXPECTED_SOURCE_HASH = (
    "0e796e226b5906f22bdc4ce622f522788985a05525d2f65ae05e40fb2c474012"
)
EXPECTED_PARAMETER_HASH = (
    "fce3f995d1421ada2152e591362700ed2a24d93c7ff3259394261f254cd7aa22"
)
BINDING_PATHS = [
    "strategies/paaf/adapters/vnpy_adapter.py",
    "strategies/paaf/detectors/opp16_two_bar_reversal.py",
    "strategies/paaf/strat_rev_opp16_01.py",
    "strategies/paaf/strat_rev_opp16_01_v011.py",
    "strategies/paaf/strat_rev_opp16_01_v020.py",
]
DETECTOR_BINDING = "OPP16@1.0.0"
FREEZE_ID = "SIF_CID_003_V0_2_0"
OUT_DIR = ROOT / "research" / "output" / "evidence" / EXPERIMENT_ID

WARMUP = datetime(2023, 12, 1)
PERIOD_START = datetime(2024, 1, 1)
PERIOD_END = datetime(2024, 12, 31)

SYMBOL = "i"
EXCHANGE = Exchange.DCE
SIZE = 100
PRICETICK = 0.5
CAPITAL = 200_000


def _source_hash() -> tuple[str, list[dict[str, str]]]:
    manifest = []
    for rel in sorted(BINDING_PATHS):
        digest = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        manifest.append({"path": rel, "sha256": digest})
    canon = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canon.encode()).hexdigest(), manifest


def _parameter_hash() -> str:
    params = {
        "body_ratio": {"type": "float", "unit": "fraction", "value": 0.5},
        "capital_floor_ratio": {"type": "float", "unit": "fraction_of_capital", "value": 0.5},
        "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
        "hard_max_lots": {"type": "int", "unit": "contracts", "value": 1},
        "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
        "risk_per_trade": {"type": "float", "unit": "fraction_of_equity", "value": 0.005},
        "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
        "sizing_mode": {"type": "str", "unit": "enum", "value": "RISK_FRACTION_OF_CAPITAL"},
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

    bars = load_stitched_raw_bars(SYMBOL, EXCHANGE, start=WARMUP, end=PERIOD_END)
    if not bars:
        print("no bars")
        return 1
    events = build_rollover_events(SYMBOL, start=bars[0].datetime, end=bars[-1].datetime)
    engine = RolloverBacktestingEngine()
    engine.set_parameters(
        vt_symbol=f"{SYMBOL}.{EXCHANGE.value}",
        interval=Interval.MINUTE,
        start=bars[0].datetime,
        end=bars[-1].datetime,
        rate=0.00003,
        slippage=1.0,
        size=SIZE,
        pricetick=PRICETICK,
        capital=CAPITAL,
    )
    engine.history_data = bars
    engine.set_rollover_events(events)
    engine.add_strategy(StratRevOpp1601StrategyV020, {})

    buf = io.StringIO()
    with redirect_stdout(buf):
        engine.run_backtesting()
        df = engine.calculate_result()
        stats = engine.calculate_statistics(df, output=False)
    log_text = buf.getvalue()

    strat = engine.strategy
    trade_log = list(getattr(strat, "_trade_log", []) or [])
    rows = []
    for item in trade_log:
        et = item.get("exit_time")
        if et is None:
            continue
        exit_cmp = et.replace(tzinfo=None) if getattr(et, "tzinfo", None) else et
        if exit_cmp < PERIOD_START or exit_cmp > PERIOD_END:
            continue
        rows.append(item)

    end_balance = stats.get("end_balance")
    if end_balance is not None:
        end_balance = float(end_balance)
    capital_breach = False
    if end_balance is not None:
        capital_breach = end_balance <= 0
    positive_balance = True
    if df is not None and len(df) > 0 and "balance" in df.columns:
        positive_balance = bool((df["balance"] > 0).all())
        capital_breach = capital_breach or (not positive_balance)
    if stats.get("total_net_pnl") is None and ("爆仓" in log_text or "资金小于等于0" in log_text):
        capital_breach = True

    kill_events = int(getattr(strat, "kill_events", 0) or 0)
    skip_zero = int(getattr(strat, "skip_zero_lot", 0) or 0)
    equity_est = float(getattr(strat, "equity_est", 0) or 0)
    halted = bool(getattr(strat, "entries_halted", False))
    gate_log = list(getattr(strat, "_capital_gate_log", []) or [])

    if capital_breach:
        outcome = "REVERT"
        reason = "engine capital path breached（balance<=0）under @0.2.0 controls"
    elif kill_events >= 1 or halted:
        outcome = "KEEP"
        reason = (
            f"kill-switch engaged kill_events={kill_events} halted={halted}; "
            f"no capital<=0; closed={len(rows)} skip_zero_lot={skip_zero}"
        )
    else:
        outcome = "KEEP"
        reason = (
            f"no capital<=0 under risk-fraction sizing; "
            f"closed={len(rows)} skip_zero_lot={skip_zero} kill_events={kill_events}"
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUT_DIR / "trades.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "experiment_id",
                "exit_reason",
                "direction",
                "strategy_version",
                "detector_binding",
            ],
        )
        w.writeheader()
        for item in rows:
            w.writerow(
                {
                    "experiment_id": EXPERIMENT_ID,
                    "exit_reason": item.get("exit_reason"),
                    "direction": item.get("direction"),
                    "strategy_version": item.get("strategy_version"),
                    "detector_binding": DETECTOR_BINDING,
                }
            )

    meta = {
        "experiment_id": EXPERIMENT_ID,
        "status": "OBSERVATION_COMPLETE",
        "authorization": "Authorize Offline Observation for STRAT_RO16_EXP007（required at run）",
        "hypothesis_family": "H_CAPITAL_GATE",
        "not_hypothesis": ["H_MECH", "H_EDGE", "H_ALPHA"],
        "parent_contrast": "STRAT_RO16_EXP005_i_breach_at_0.1.1",
        "strategy_id": "STRAT_REV_OPP16_01",
        "strategy_version": "0.2.0",
        "freeze_id": FREEZE_ID,
        "source_hash": source_hash,
        "parameter_hash": parameter_hash,
        "source_manifest": manifest,
        "detector_binding": DETECTOR_BINDING,
        "consumer_surface": "RISK",
        "symbol": SYMBOL,
        "capital_assumption": CAPITAL,
        "sizing_mode": "RISK_FRACTION_OF_CAPITAL",
        "risk_per_trade": 0.005,
        "hard_max_lots": 1,
        "capital_floor_ratio": 0.5,
        "contract_size": SIZE,
        "period": "2024",
        "closed_trade_count": len(rows),
        "kill_events": kill_events,
        "skip_zero_lot": skip_zero,
        "entries_halted": halted,
        "equity_est_end": equity_est,
        "end_balance": end_balance,
        "capital_breach": capital_breach,
        "positive_balance": positive_balance,
        "capital_gate_log_count": len(gate_log),
        "outcome": outcome,
        "outcome_reason": reason,
        "bindable": False,
        "alpha_claim": False,
        "trades_csv": str(csv_path.relative_to(ROOT)).replace("\\", "/"),
    }
    (OUT_DIR / "run_metadata.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    (OUT_DIR / "capital_gate_log.json").write_text(
        json.dumps(gate_log, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                k: meta[k]
                for k in (
                    "outcome",
                    "outcome_reason",
                    "closed_trade_count",
                    "kill_events",
                    "skip_zero_lot",
                    "capital_breach",
                    "end_balance",
                    "equity_est_end",
                )
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if outcome != "REVERT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
