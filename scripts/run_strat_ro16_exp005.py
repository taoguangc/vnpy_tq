"""STRAT_RO16_EXP005 — H_MECH multi-symbol {rb,i,MA} · @0.1.1 · 2024.

Delegation-50. ≠ Alpha · ≠ H_EDGE reopen · ≠ parameter search.
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
from strategies.paaf.strat_rev_opp16_01_v011 import StratRevOpp1601StrategyV011

EXPERIMENT_ID = "STRAT_RO16_EXP005"
EXPECTED_SOURCE_HASH = (
    "6dee22fe6c1eaf5958defa3f94db614ece5991bdbc58abc93d281bbd7b1164b5"
)
EXPECTED_PARAMETER_HASH = (
    "76b124f47414af2da2e0cdfdc6afcd5025d2cca8ae3a5583ba667cc7e1e31c57"
)
BINDING_PATHS = [
    "strategies/paaf/adapters/vnpy_adapter.py",
    "strategies/paaf/detectors/opp16_two_bar_reversal.py",
    "strategies/paaf/strat_rev_opp16_01.py",
    "strategies/paaf/strat_rev_opp16_01_v011.py",
]
DETECTOR_BINDING = "OPP16@1.0.0"
FREEZE_ID = "SIF_CID_003_V0_1_1"
OUT_DIR = ROOT / "research" / "output" / "evidence" / EXPERIMENT_ID

WARMUP = datetime(2023, 12, 1)
PERIOD_START = datetime(2024, 1, 1)
PERIOD_END = datetime(2024, 12, 31)

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
        "body_ratio": {"type": "float", "unit": "fraction", "value": 0.5},
        "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
        "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
        "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
    }
    canon = json.dumps(params, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def _run_one(symbol: str) -> dict:
    spec = SYMBOL_SPEC[symbol]
    exchange = spec["exchange"]
    bars = load_stitched_raw_bars(symbol, exchange, start=WARMUP, end=PERIOD_END)
    if not bars:
        return {"symbol": symbol, "status": "HOLD", "reason": "no_bars", "n": 0, "exit_ok": 0}
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
        capital=200_000,
    )
    engine.history_data = bars
    engine.set_rollover_events(events)
    engine.add_strategy(StratRevOpp1601StrategyV011, {})
    engine.run_backtesting()
    df = engine.calculate_result()
    stats = engine.calculate_statistics(df, output=False)
    trade_log = list(getattr(engine.strategy, "_trade_log", []) or [])
    allowed = {"STOP", "TARGET", "TIME_STOP"}
    rows = []
    for item in trade_log:
        et = item.get("exit_time")
        if et is None:
            continue
        exit_cmp = et.replace(tzinfo=None) if getattr(et, "tzinfo", None) else et
        if exit_cmp < PERIOD_START or exit_cmp > PERIOD_END:
            continue
        rows.append(item)
    n = len(rows)
    ok = sum(1 for r in rows if r.get("exit_reason") in allowed)
    if n < 1 or ok < 1:
        status, reason = "HOLD", "no_auditable_exits"
    else:
        status, reason = "KEEP", f"auditable_exits={n}"
    return {
        "symbol": symbol,
        "status": status,
        "reason": reason,
        "n": n,
        "exit_ok": ok,
        "engine_total_net_pnl": stats.get("total_net_pnl"),
        "slippage": 1.0,
        "rate": 0.00003,
    }


def _aggregate(per: list[dict]) -> tuple[str, str]:
    if any(p["status"] == "REVERT" for p in per):
        return "REVERT", "symbol_level_revert"
    if all(p["status"] == "KEEP" for p in per):
        return "KEEP", "all_symbols_KEEP"
    return "HOLD", "mixed_or_partial_HOLD"


def main() -> int:
    source_hash, manifest = _source_hash()
    parameter_hash = _parameter_hash()
    if source_hash != EXPECTED_SOURCE_HASH or parameter_hash != EXPECTED_PARAMETER_HASH:
        print("ABORT hash", source_hash, parameter_hash)
        return 2
    print(f"experiment_id={EXPERIMENT_ID} hash_ok=True")

    per = [_run_one(s) for s in ("rb", "i", "MA")]
    outcome, reason = _aggregate(per)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    meta = {
        "experiment_id": EXPERIMENT_ID,
        "status": "OBSERVATION_COMPLETE",
        "authorization": "Delegation-50（授权你决定50次）",
        "hypothesis_family": "H_MECH",
        "not_hypothesis": ["H_EDGE", "H_ALPHA", "H_CAPITAL_GATE"],
        "outcome": outcome,
        "outcome_reason": reason,
        "per_symbol": per,
        "source_hash": source_hash,
        "parameter_hash": parameter_hash,
        "source_manifest": manifest,
        "freeze_id": FREEZE_ID,
        "strategy_version": "0.1.1",
        "detector_binding": DETECTOR_BINDING,
        "market_scope": {
            "symbols": ["rb", "i", "MA"],
            "universe_policy": "CAP_CTX_CONTINUITY",
            "period_start": "2024-01-01",
            "period_end": "2024-12-31",
            "warmup_start": "2023-12-01",
            "data_protocol_version": "docs/07_DATA_SPEC.md@1.0.0",
            "slippage": 1.0,
            "rate": 0.00003,
        },
        "alpha_claim": False,
        "bindable": False,
    }
    (OUT_DIR / "run_metadata.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    with (OUT_DIR / "per_symbol.csv").open("w", newline="", encoding="utf-8") as fh:
        fields = ["symbol", "status", "reason", "n", "exit_ok", "engine_total_net_pnl", "slippage", "rate"]
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for row in per:
            w.writerow({k: row.get(k) for k in fields})
    print(f"outcome={outcome}")
    print(f"reason={reason}")
    print(json.dumps(per, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
