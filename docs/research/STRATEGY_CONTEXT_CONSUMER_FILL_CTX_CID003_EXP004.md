# Context Consumer Experiment Fill — CTX_CID003_EXP004

> **Status**: **CLOSED** ✓ · Observation **COMPLETE** · Outcome **KEEP**  
> **Experiment ID**: `CTX_CID003_EXP004`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25J  
> **Design**: `CCRD_CID_003_V0_1`  
> **Eval**: [`STRATEGY_CONTEXT_CONSUMER_EVALUATION_CTX_CID003_EXP004.md`](STRATEGY_CONTEXT_CONSUMER_EVALUATION_CTX_CID003_EXP004.md)  
> **ER**: [`STRATEGY_CONTEXT_CONSUMER_EVIDENCE_REVIEW_CTX_CID003_EXP004.md`](STRATEGY_CONTEXT_CONSUMER_EVIDENCE_REVIEW_CTX_CID003_EXP004.md)  
> **Machine**: `research/output/evidence/CTX_CID003_EXP004/`

## Record

```text
================================================
CTX_CID003_EXP004 — CLOSED · KEEP

Hypothesis:     H_CTX_RISK_COMP ADMITTED（filter active under RISK）
Surface:        RISK @0.2.0
N0 / N1 / D:    1920 / 1180 / 822
Alpha claim:    NONE
================================================
```

## Decision metrics

| Gate | Result |
|------|--------|
| Identity hashes | MATCH |
| N0≥1 ·（N1≠N0 OR D≥1） | PASS |
| Aggregate | **KEEP** |

```text
Note（descriptive）: N0/N1/D equal MECH EXP001 under hard_max_lots=1 on rb —
does NOT collapse Surface IDs; capital controls still RISK-owned.
```

## Non-claims

```text
❌ Context Alpha · Production · live routing
❌ Context sizing alpha
❌ MECH+RISK+CTX single edge narrative
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | PRE-REGISTERED |
| 2026-07-23 | CLOSED · KEEP |
