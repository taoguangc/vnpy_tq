"""STRAT_BS02 EXP006/EXP007 runner for v0.1.1（Delegation-50C）."""
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
from strategies.paaf.brooks_scalp_paaf_strategy_v011 import BrooksScalpPaafStrategyV011

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


def _run_one(symbol: str, *, slippage: float, rate: float = 0.00003) -> dict:
    spec = SYMBOL_SPEC[symbol]
    exchange = spec["exchange"]
    bars = load_stitched_raw_bars(symbol, exchange, start=WARMUP, end=PERIOD_END)
    if not bars:
        return {"symbol": symbol, "status": "HOLD", "reason": "no_bars", "n": 0}
    events = build_rollover_events(symbol, start=bars[0].datetime, end=bars[-1].datetime)
    engine = RolloverBacktestingEngine()
    engine.set_parameters(
        vt_symbol=f"{symbol}.{exchange.value}",
        interval=Interval.MINUTE,
        start=bars[0].datetime,
        end=bars[-1].datetime,
        rate=rate,
        slippage=slippage,
        size=spec["size"],
        pricetick=spec["pricetick"],
        capital=200_000,
    )
    engine.history_data = bars
    engine.set_rollover_events(events)
    engine.add_strategy(BrooksScalpPaafStrategyV011, {})
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
        if exit_cmp < PERIOD_START:
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
        "slippage": slippage,
        "rate": rate,
    }


def _aggregate(per: list[dict]) -> tuple[str, str]:
    if any(p["status"] == "REVERT" for p in per):
        return "REVERT", "symbol_level_revert"
    if all(p["status"] == "KEEP" for p in per):
        return "KEEP", "all_symbols_KEEP"
    return "HOLD", "mixed_or_partial_HOLD"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--exp", required=True, choices=["STRAT_BS02_EXP006", "STRAT_BS02_EXP007"])
    args = parser.parse_args()
    exp_id = args.exp
    source_hash, manifest = _source_hash()
    if source_hash != EXPECTED_SOURCE_HASH:
        print("ABORT hash", source_hash)
        return 2
    print(f"experiment_id={exp_id} hash_ok=True")

    if exp_id == "STRAT_BS02_EXP006":
        per = [_run_one("rb", slippage=2.0)]
        outcome, reason = per[0]["status"], per[0]["reason"]
        family = "H_ROBUST"
        scope = {"symbols": ["rb"], "slippage": 2.0}
    else:
        per = [_run_one(s, slippage=1.0) for s in ("rb", "i", "MA")]
        outcome, reason = _aggregate(per)
        family = "H_MECH"
        scope = {"symbols": ["rb", "i", "MA"], "slippage": 1.0, "universe_policy": "CAP_CTX_CONTINUITY"}

    out_dir = ROOT / "research" / "output" / "evidence" / exp_id
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "experiment_id": exp_id,
        "status": "OBSERVATION_COMPLETE",
        "authorization": "Delegation-50C",
        "hypothesis_family": family,
        "outcome": outcome,
        "outcome_reason": reason,
        "per_symbol": per,
        "source_hash": source_hash,
        "parameter_hash": EXPECTED_PARAMETER_HASH,
        "source_manifest": manifest,
        "freeze_id": "SIF_CID_002_V0_1_1",
        "strategy_version": "0.1.1",
        "market_scope": {
            **scope,
            "period_start": "2024-01-01",
            "period_end": "2024-12-31",
            "warmup_start": "2023-12-01",
            "data_protocol_version": "docs/07_DATA_SPEC.md@1.0.0",
        },
        "alpha_claim": False,
        "bindable": False,
    }
    (out_dir / "run_metadata.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    with (out_dir / "per_symbol.csv").open("w", newline="", encoding="utf-8") as fh:
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
