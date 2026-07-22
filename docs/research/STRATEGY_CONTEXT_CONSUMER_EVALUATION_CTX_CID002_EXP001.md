# Context Consumer Evaluation — CTX_CID002_EXP001

> **Status**: **CLOSED** ✓  
> **Experiment ID**: `CTX_CID002_EXP001`  
> **Date**: 2026-07-22  
> **Authorization**: `Authorize Context Consumer Experiment Observation`  
> **Fill**: [`STRATEGY_CONTEXT_CONSUMER_FILL_CTX_CID002_EXP001.md`](STRATEGY_CONTEXT_CONSUMER_FILL_CTX_CID002_EXP001.md)  
> **Harness**: `scripts/run_ctx_cid002_exp001.py`  
> **Adapter**: `strategies/paaf/context_consumer/`（G5 binding bytes untouched）

## Outcome

```text
KEEP
H_CTX_FILTER · MECH @0.1.1 · rb/2024 · A1 Filter F1

N0 = 1303
N1 = 919
D  = 563
source_hash / parameter_hash: MATCH
PnL used as decision metric: NO
```

## Decision rule check

| Gate | Result |
|------|--------|
| Identity hashes match | PASS |
| N0 ≥ 1 | PASS（1303） |
| N1 ≠ N0 OR D ≥ 1 | PASS（919 ≠ 1303 · D=563） |
| B1 exits detector-attributed | PASS（STOP/TARGET/TIME_STOP only） |
| Context generates entries | NO |
| Context supplies sizing | NO |
| PnL primary gate | NO（descriptive only） |

## Descriptive only（not decision）

| Arm | total_net_pnl（descriptive） |
|-----|------------------------------|
| B0 | −34671.28 |
| B1 | −23752.23 |

## Artifacts

```text
research/output/evidence/CTX_CID002_EXP001/
  run_metadata.json
  baseline_trades_audit.csv
  filtered_trades_audit.csv
  permission_denials.csv
  context_state_sample.json
  pre_registration.json
```

## Non-claims

```text
❌ Context Alpha / trading value
❌ Production
❌ RISK @0.2.0 interaction
❌ RC001-B reopen
❌ PnL improvement as KEEP rationale
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | CLOSED · KEEP |
