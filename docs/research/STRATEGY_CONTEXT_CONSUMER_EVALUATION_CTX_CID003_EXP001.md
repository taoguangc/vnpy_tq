# Context Consumer Evaluation — CTX_CID003_EXP001

> **Status**: **CLOSED** ✓  
> **Experiment ID**: `CTX_CID003_EXP001`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-50E  
> **Fill**: [`STRATEGY_CONTEXT_CONSUMER_FILL_CTX_CID003_EXP001.md`](STRATEGY_CONTEXT_CONSUMER_FILL_CTX_CID003_EXP001.md)  
> **Harness**: `scripts/run_ctx_cid003_exp001.py`  
> **Adapter**: `strategies/paaf/context_consumer/opp16_ctx_filter_v011.py`（G5 binding untouched）

## Outcome

```text
KEEP
H_CTX_FILTER · MECH @0.1.1 · rb/2024 · A1 Filter F1

N0 = 1920
N1 = 1180
D  = 822
source_hash / parameter_hash: MATCH
PnL used as decision metric: NO
```

## Decision rule check

| Gate | Result |
|------|--------|
| Identity hashes match | PASS |
| N0 ≥ 1 | PASS（1920） |
| N1 ≠ N0 OR D ≥ 1 | PASS（1180 ≠ 1920 · D=822） |
| B1 exits detector-attributed | PASS（STOP/TARGET/TIME_STOP only） |
| Context generates entries | NO |
| Context supplies sizing | NO |
| PnL primary gate | NO（descriptive only） |

## Descriptive only（not decision）

| Arm | total_net_pnl（descriptive） |
|-----|------------------------------|
| B0 | −37703.02 |
| B1 | −21668.91 |

## Artifacts

```text
research/output/evidence/CTX_CID003_EXP001/
  run_metadata.json
  baseline_trades_audit.csv
  filtered_trades_audit.csv
  permission_denials.csv
  context_state_sample.json
```

## Non-claims

```text
❌ Context Alpha / trading value
❌ Production
❌ RISK @0.2.0 interaction
❌ Continuity with CTX_CID002_*
❌ PnL improvement as KEEP rationale
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | CLOSED · KEEP |
