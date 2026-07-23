# SEVF Specification — CID_005 / STRAT_REV_OPP17_01

> **Type**: Asset-bound SEVF Specification（≠ Fill · ≠ Observation alone）  
> **Status**: **SPECIFIED** ✓  
> **Spec ID**: `SEVF_SPEC_CID_005_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25U  
> **Framework**: `SEVF-v1`  
> **Identity**: `SIF_CID_005_V0_1` · `STRAT_REV_OPP17_01@0.1.0`  
> **Morphology**: `OPP17_MS_V0_1`

## Spec record

```text
================================================
SEVF_SPEC_CID_005_V0_1

Bound identity: STRAT_REV_OPP17_01@0.1.0
source_hash:    9d85cf960f30715524f7224bdf3dd9750ce4fd1ad86a79d9122789c75e5cb576
parameter_hash: 40ef1e1d594294e89e9872f08c5ac5d057dc36156081784e030c072fd19b0816
Alpha:          NONE at Spec time
================================================
```

## Hypothesis families（one primary per EXP）

| Family | Intent |
|--------|--------|
| `H_MECH` | Auditable OPP17→entry→exit（STOP/TARGET/TIME_STOP） |
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
❌ CID_002/003/004 Alpha transfer
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | SPECIFIED · Delegation-25U |
