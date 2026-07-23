# Context Consumer Evaluation — CTX_CID003_EXP002

> **Status**: **CLOSED** ✓  
> **Experiment ID**: `CTX_CID003_EXP002`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-50F  
> **Fill**: [`STRATEGY_CONTEXT_CONSUMER_FILL_CTX_CID003_EXP002.md`](STRATEGY_CONTEXT_CONSUMER_FILL_CTX_CID003_EXP002.md)  
> **Harness**: `scripts/run_ctx_cid003_exp002.py`  
> **OOS of**: `CTX_CID003_EXP001`

## Outcome

```text
KEEP
H_CTX_FILTER temporal OOS · MECH @0.1.1 · rb/2025 · A1 Filter F1

N0 = 2033
N1 = 1196
D  = 931
source_hash / parameter_hash: MATCH
PnL used as decision metric: NO
```

## Decision rule check

| Gate | Result |
|------|--------|
| Identity hashes match | PASS |
| N0 ≥ 1 | PASS（2033） |
| N1 ≠ N0 OR D ≥ 1 | PASS（1196 ≠ 2033 · D=931） |
| B1 exits detector-attributed | PASS |
| Context generates entries / sizing | NO |
| PnL primary gate | NO |

## Descriptive only（not decision）

| Arm | total_net_pnl（descriptive） |
|-----|------------------------------|
| B0 | −41157.20 |
| B1 | −22451.47 |

## Non-claims

```text
❌ Context Alpha / trading value
❌ Production / live routing
❌ Continuity with CTX_CID002_*
❌ PnL improvement as KEEP rationale
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | CLOSED · KEEP |
