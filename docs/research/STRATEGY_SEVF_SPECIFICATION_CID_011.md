# SEVF Specification — CID_011 / STRAT_SESS_OPP19_REV_01

> **Type**: Asset-bound SEVF Specification（≠ Fill · ≠ Observation alone）  
> **Status**: **SPECIFIED** ✓  
> **Spec ID**: `SEVF_SPEC_CID_011_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AS  
> **Framework**: `SEVF-v1`  
> **Identity**: `SIF_CID_011_V0_1` · `STRAT_SESS_OPP19_REV_01@0.1.0`  
> **Morphology**: `OPP19_REV_MS_V0_1`

## Spec record

```text
================================================
SEVF_SPEC_CID_011_V0_1

Bound identity: STRAT_SESS_OPP19_REV_01@0.1.0
source_hash:    731c908d810d6c5f61400ceaeb06beb37a8436bc2f8503261ba2fecd86060593
parameter_hash: 2f8f2170dc94cfa63ac9e99bfd365d239be4c4186672c5db54143ae0d21b8f71
Alpha:          NONE at Spec time
================================================
```

## Hypothesis families

| Family | Intent |
|--------|--------|
| `H_MECH` | Auditable OD_REV→entry→exit |
| `H_EDGE` | Edge structure（plan early · not this EXP） |

## Recommended order

```text
1) H_MECH  2) H_EDGE diagnostic  3) H_EDGE OOS  4) Alpha petition OR negative close
```

## Non-grants

```text
❌ Observation by Spec alone
❌ PnL as H_MECH gate
❌ Prior CID / CID_007 Alpha transfer
❌ OD-Breakout under this Spec
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | SPECIFIED · Delegation-25AS |
