# SEVF Specification — CID_006 / STRAT_TREND_OPP08_01

> **Type**: Asset-bound SEVF Specification（≠ Fill · ≠ Observation alone）  
> **Status**: **SPECIFIED** ✓  
> **Spec ID**: `SEVF_SPEC_CID_006_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AA  
> **Framework**: `SEVF-v1`  
> **Identity**: `SIF_CID_006_V0_1` · `STRAT_TREND_OPP08_01@0.1.0`  
> **Morphology**: `OPP08_MS_V0_1`

## Spec record

```text
================================================
SEVF_SPEC_CID_006_V0_1

Bound identity: STRAT_TREND_OPP08_01@0.1.0
source_hash:    0a6023e581b8547d42c10a30f05324f0c841d131cbbd748ade4ad7476fd66f14
parameter_hash: 5c48a70f7666d033d340799e4fdf19972aeadfc15c98b068f85521ab32d0163e
Alpha:          NONE at Spec time
================================================
```

## Hypothesis families（one primary per EXP）

| Family | Intent |
|--------|--------|
| `H_MECH` | Auditable OPP08→entry→exit（STOP/TARGET/TIME_STOP） |
| `H_EDGE` | Edge structure（plan early · not this EXP） |
| `H_NULL` / `H_ROBUST` | As SEVF-v1 |

## Recommended order

```text
1) H_MECH  2) H_EDGE diagnostic  3) H_EDGE OOS / multi-year  4) Alpha petition OR negative close
```

## Non-grants

```text
❌ Observation by Spec alone
❌ PnL as H_MECH gate
❌ Prior CID Alpha transfer
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | SPECIFIED · Delegation-25AA |
