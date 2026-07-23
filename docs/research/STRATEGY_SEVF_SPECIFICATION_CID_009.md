# SEVF Specification — CID_009 / STRAT_REV_OPP15_01

> **Type**: Asset-bound SEVF Specification（≠ Fill · ≠ Observation alone）  
> **Status**: **SPECIFIED** ✓  
> **Spec ID**: `SEVF_SPEC_CID_009_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AM  
> **Framework**: `SEVF-v1`  
> **Identity**: `SIF_CID_009_V0_1` · `STRAT_REV_OPP15_01@0.1.0`  
> **Morphology**: `OPP15_MS_V0_1`

## Spec record

```text
================================================
SEVF_SPEC_CID_009_V0_1

Bound identity: STRAT_REV_OPP15_01@0.1.0
source_hash:    1b0f5858d8d22371906085cdf974b8378e60d6bdb8c3924a509bfce62e9cb8a1
parameter_hash: 960b1ae8abdf5011f6d7977bf99c4bae7a8f8264721afca0488e687b539af9f6
Alpha:          NONE at Spec time
================================================
```

## Hypothesis families

| Family | Intent |
|--------|--------|
| `H_MECH` | Auditable OPP15 Path-A→entry→exit（STOP/TARGET/TIME_STOP） |
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
❌ Path B' / MTF expand under this Spec
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | SPECIFIED · Delegation-25AM |
