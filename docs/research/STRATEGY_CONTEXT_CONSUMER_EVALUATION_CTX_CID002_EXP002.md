# Context Consumer Evaluation — CTX_CID002_EXP002

> **Status**: **CLOSED** ✓  
> **Experiment ID**: `CTX_CID002_EXP002`  
> **Date**: 2026-07-22  
> **Authorization**: Delegation-50J  
> **Fill**: [`STRATEGY_CONTEXT_CONSUMER_FILL_CTX_CID002_EXP002.md`](STRATEGY_CONTEXT_CONSUMER_FILL_CTX_CID002_EXP002.md)  
> **Prior**: `CTX_CID002_EXP001` KEEP（rb/2024）  
> **Harness**: `scripts/run_ctx_cid002_exp002.py`

## Outcome

```text
KEEP
H_CTX_FILTER temporal OOS · MECH @0.1.1 · rb/2025 · A1 Filter F1

N0 = 1053
N1 = 828
D  = 365
source_hash / parameter_hash: MATCH
PnL used as decision metric: NO
```

## Continuity note（descriptive）

| EXP | Period | N0 | N1 | D | Outcome |
|-----|--------|----|----|---|---------|
| EXP001 | 2024 | 1303 | 919 | 563 | KEEP |
| EXP002 | 2025 | 1053 | 828 | 365 | KEEP |

Filter remained non-inert on the OOS year. This is **not** an Alpha claim.

## Non-claims

```text
❌ Context Alpha / Production
❌ PnL improvement as KEEP rationale
❌ Multi-symbol / RISK surface
❌ RC001-B reopen
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | CLOSED · KEEP |
