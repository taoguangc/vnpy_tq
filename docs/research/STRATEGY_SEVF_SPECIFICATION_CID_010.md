# SEVF Specification — CID_010 / STRAT_REV_OPP13_01

> **Type**: Asset-bound SEVF Specification（≠ Fill · ≠ Observation alone）  
> **Status**: **SPECIFIED** ✓  
> **Spec ID**: `SEVF_SPEC_CID_010_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AP  
> **Framework**: `SEVF-v1`  
> **Identity**: `SIF_CID_010_V0_1` · `STRAT_REV_OPP13_01@0.1.0`  
> **Morphology**: `OPP13_MS_V0_1`

## Spec record

```text
================================================
SEVF_SPEC_CID_010_V0_1

Bound identity: STRAT_REV_OPP13_01@0.1.0
source_hash:    d20147d23918edac9d94cdea5572155dacc8375218b62c0aa4a822eac303d1de
parameter_hash: 1f95584dfc3a17c18ad41210a53e53fbe050988850d656f881686d80e7c11405
Alpha:          NONE at Spec time
================================================
```

## Hypothesis families

| Family | Intent |
|--------|--------|
| `H_MECH` | Auditable OPP13 single-touch→entry→exit |
| `H_EDGE` | Edge structure（plan early · not this EXP） |

## Recommended order

```text
1) H_MECH  2) H_EDGE diagnostic  3) H_EDGE OOS  4) Alpha petition OR negative close
```

## Non-grants

```text
❌ Observation by Spec alone
❌ PnL as H_MECH gate
❌ Prior CID Alpha transfer
❌ Double-top expand under this Spec
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | SPECIFIED · Delegation-25AP |
