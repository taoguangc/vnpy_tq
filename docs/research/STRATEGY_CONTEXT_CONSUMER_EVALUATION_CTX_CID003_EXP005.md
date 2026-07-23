# Context Consumer Evaluation — CTX_CID003_EXP005

> **Status**: **CLOSED** ✓  
> **Experiment ID**: `CTX_CID003_EXP005`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25K  
> **Harness**: `scripts/run_ctx_cid003_exp005.py`  
> **OOS of**: `CTX_CID003_EXP004`

## Outcome

```text
KEEP
H_CTX_RISK_COMP temporal OOS · RISK @0.2.0 · rb/2025 · F1

N0 = 2033
N1 = 1196
D  = 931
source_hash / parameter_hash: MATCH
PnL used as decision metric: NO
```

## Decision rule check

| Gate | Result |
|------|--------|
| Identity hashes | PASS |
| Filter non-inert under RISK OOS | PASS |
| Context entries / sizing | NO |
| PnL primary | NO |

## Descriptive only

| Arm | total_net_pnl | end_balance |
|-----|---------------|-------------|
| B0 | （see run_metadata） | （see run_metadata） |
| B1 | （see run_metadata） | （see run_metadata） |

## Non-claims

```text
❌ Context Alpha · Production · live routing
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | CLOSED · KEEP |
