# Context Consumer Experiment Fill — CTX_CID003_EXP002

> **Type**: Experiment Fill / Pre-registration（Observation CLOSED）  
> **Status**: **CLOSED** ✓ · Observation **COMPLETE** · Outcome **KEEP**  
> **Experiment ID**: `CTX_CID003_EXP002`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-50F  
> **Prior**: `CTX_CID003_EXP001` CLOSED KEEP · `CCED_CID_003_V0_1`  
> **Eval**: [`STRATEGY_CONTEXT_CONSUMER_EVALUATION_CTX_CID003_EXP002.md`](STRATEGY_CONTEXT_CONSUMER_EVALUATION_CTX_CID003_EXP002.md)  
> **ER**: [`STRATEGY_CONTEXT_CONSUMER_EVIDENCE_REVIEW_CTX_CID003_EXP002.md`](STRATEGY_CONTEXT_CONSUMER_EVIDENCE_REVIEW_CTX_CID003_EXP002.md)  
> **Parents**: `BDR_CID_003_V0_1` · `CC-CID_003-v1` · `SIF_CID_003_V0_1_1` · A1 · Decision 019  
> **Machine**: `research/output/evidence/CTX_CID003_EXP002/`

## Record

```text
================================================
CTX_CID003_EXP002 — CLOSED · KEEP

Hypothesis:     H_CTX_FILTER temporal OOS ADMITTED（non-inert）
Strategy:       MECH @0.1.1 only
Context role:   Filter F1（identical to EXP001）
Scope:          rb · 2025
N0 / N1 / D:    2033 / 1196 / 931
Alpha claim:    NONE
================================================
```

## 1. Identity bindings（matched）

| Field | Value |
|-------|-------|
| `consumer_surface` | `MECH` |
| `freeze_id` | `SIF_CID_003_V0_1_1` |
| `source_hash` / `parameter_hash` | MATCH |
| `filter_id` | `F1_EXPANSION_ONLY` |
| `oos_of` | `CTX_CID003_EXP001` |

## 2. Decision rule（applied）

| Outcome | Result |
|---------|--------|
| REVERT | no |
| HOLD | no |
| **KEEP** | **YES**（N0=2033 · N1=1196 · D=931） |

## 3. Explicit non-claims（retained）

```text
❌ Context Alpha · Production · live routing
❌ Filter retune · RISK interaction
❌ Continuity with CTX_CID002_*
❌ PnL as KEEP rationale
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | PRE-REGISTERED under Delegation-50F |
| 2026-07-23 | Observation COMPLETE · CLOSED · KEEP |
