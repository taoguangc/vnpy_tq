# Context Consumer Experiment Fill — CTX_CID003_EXP001

> **Type**: Experiment Fill / Pre-registration（Observation CLOSED）  
> **Status**: **CLOSED** ✓ · Observation **COMPLETE** · Outcome **KEEP**  
> **Experiment ID**: `CTX_CID003_EXP001`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-50E（Fill + Observation）  
> **Design**: [`STRATEGY_CONTEXT_CONSUMER_EXPERIMENT_DESIGN_CID_003.md`](STRATEGY_CONTEXT_CONSUMER_EXPERIMENT_DESIGN_CID_003.md) · `CCED_CID_003_V0_1`  
> **Eval**: [`STRATEGY_CONTEXT_CONSUMER_EVALUATION_CTX_CID003_EXP001.md`](STRATEGY_CONTEXT_CONSUMER_EVALUATION_CTX_CID003_EXP001.md)  
> **ER**: [`STRATEGY_CONTEXT_CONSUMER_EVIDENCE_REVIEW_CTX_CID003_EXP001.md`](STRATEGY_CONTEXT_CONSUMER_EVIDENCE_REVIEW_CTX_CID003_EXP001.md)  
> **Parents**: `BDR_CID_003_V0_1` · `CC-CID_003-v1` · `SIF_CID_003_V0_1_1` · CAP-CTX A1 · Decision 019  
> **Machine**: `research/output/evidence/CTX_CID003_EXP001/`

## Record

```text
================================================
CTX_CID003_EXP001 — CLOSED · KEEP

Hypothesis:     H_CTX_FILTER ADMITTED（filter active）
Strategy:       MECH @0.1.1 only（RISK wrapper OUT）
Context role:   Filter / Permission only（Decision 019）
N0 / N1 / D:    1920 / 1180 / 822
Observation:    COMPLETE
Alpha claim:    NONE
================================================
```

## 1. Identity bindings（matched at run）

| Field | Value |
|-------|-------|
| `consumer_surface` | `MECH` |
| `freeze_id` | `SIF_CID_003_V0_1_1` |
| `source_hash` | `6dee22fe…1164b5` · MATCH |
| `parameter_hash` | `76b124f4…1c57` · MATCH |
| `detector_binding` | `OPP16@1.0.0` |
| `context_version` | `A1-CTX-PS-v1.0.0` |
| `filter_id` | `F1_EXPANSION_ONLY` |
| `consumer_contract` | `CC-CID_003-v1` |

## 2. Decision rule（pre-registered · applied）

| Outcome | Condition | Result |
|---------|-----------|--------|
| REVERT | identity hash mismatch | no |
| HOLD | N0 < 1 · OR · inert | no |
| **KEEP** | N0 ≥ 1 AND（N1 ≠ N0 OR D ≥ 1） | **YES** |

## 3. Scope

```text
rb · SHFE · 2024 · TQ offline 1m CbC 无复权 · real costs · capital 200k
```

## 4. Explicit non-claims（retained）

```text
❌ Context Alpha / trading value
❌ Production
❌ RISK @0.2.0 interaction
❌ Continuity with CTX_CID002_*
❌ PnL as KEEP rationale
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | PRE-REGISTERED under Delegation-50E |
| 2026-07-23 | Observation COMPLETE · CLOSED · KEEP |
