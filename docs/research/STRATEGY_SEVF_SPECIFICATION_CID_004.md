# SEVF Specification — CID_004 / STRAT_REV_OPP12_01

> **Type**: Asset-bound SEVF Specification（≠ Fill · ≠ Observation alone）  
> **Status**: **SPECIFIED** ✓  
> **Spec ID**: `SEVF_SPEC_CID_004_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25P  
> **Framework**: `SEVF-v1`  
> **Identity**: `SIF_CID_004_V0_1` · `STRAT_REV_OPP12_01@0.1.0`  
> **Morphology**: `OPP12_MS_V0_1`

## Spec record

```text
================================================
SEVF_SPEC_CID_004_V0_1

Bound identity: STRAT_REV_OPP12_01@0.1.0
source_hash:    2efd2112a7ffd6eae70ac2761c0ba3559a07a3e0f6ef7f13ae4e35caba42de4d
parameter_hash: b6c767a8bf8afde7e5bba56a2777a036ab21f06b7b807ec630d9bd6edb9e1418
Alpha:          NONE at Spec time
================================================
```

## Hypothesis families（one primary per EXP）

| Family | Intent |
|--------|--------|
| `H_MECH` | Auditable OPP12→entry→exit（STOP/TARGET/TIME_STOP） |
| `H_EDGE` | Edge structure（plan early · not this EXP） |
| `H_NULL` / `H_ROBUST` | As SEVF-v1 |

## Recommended order

```text
1) H_MECH  2) H_EDGE diagnostic  3) H_EDGE OOS  4) Alpha petition OR negative close
```

## Non-grants

```text
❌ Observation by Spec alone
❌ PnL as H_MECH gate
❌ CID_002/003 Alpha transfer
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | SPECIFIED · Delegation-25P |
