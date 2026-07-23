# Context Consumer Evaluation — CTX_CID003_EXP004

> **Status**: **CLOSED** ✓  
> **Experiment ID**: `CTX_CID003_EXP004`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25J  
> **Harness**: `scripts/run_ctx_cid003_exp004.py`  
> **Adapter**: `opp16_ctx_filter_v020.py`

## Outcome

```text
KEEP
H_CTX_RISK_COMP · RISK @0.2.0 · rb/2024 · F1

N0 = 1920
N1 = 1180
D  = 822
source_hash / parameter_hash: MATCH
PnL used as decision metric: NO
```

## Decision rule check

| Gate | Result |
|------|--------|
| Identity hashes | PASS |
| Filter non-inert under RISK | PASS |
| Context generates entries / sizing | NO |
| RISK capital controls retained | YES（V020 path） |
| PnL primary | NO |

## Descriptive only

| Arm | total_net_pnl | end_balance | kill_events |
|-----|---------------|-------------|-------------|
| B0 | −37703.02 | 162296.98 | 0 |
| B1 | −21668.91 | 178331.09 | 0 |

## Non-claims

```text
❌ Context Alpha · Production · live routing
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | CLOSED · KEEP |
