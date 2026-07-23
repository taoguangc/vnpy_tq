# SEVF Specification — CID_012 / STRAT_REV_OPP13_DT_01

> **Type**: Asset-bound SEVF Specification（≠ Fill · ≠ Observation alone）  
> **Status**: **SPECIFIED** ✓  
> **Spec ID**: `SEVF_SPEC_CID_012_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AV  
> **Framework**: `SEVF-v1`  
> **Identity**: `SIF_CID_012_V0_1` · `STRAT_REV_OPP13_DT_01@0.1.0`  
> **Morphology**: `OPP13_DT_MS_V0_1`

## Spec record

```text
================================================
SEVF_SPEC_CID_012_V0_1

Bound identity: STRAT_REV_OPP13_DT_01@0.1.0
source_hash:    b01715d8e4ff68e0fb15b228dfcd9f263651b070362bf83f301961859fa24207
parameter_hash: 910989850b1620d4db2c9fa99d539b039c316b834216b25ad0dc7ef155dc1f8b
Alpha:          NONE at Spec time
================================================
```

## Hypothesis families

| Family | Intent |
|--------|--------|
| `H_MECH` | Auditable OPP13_DT double-top→entry→exit |
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
❌ CID_010 single-touch merge / HOLD rescue
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | SPECIFIED · Delegation-25AV |
