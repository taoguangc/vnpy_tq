# SEVF Specification — CID_007 / STRAT_SESS_OPP19_01

> **Type**: Asset-bound SEVF Specification（≠ Fill · ≠ Observation alone）  
> **Status**: **SPECIFIED** ✓  
> **Spec ID**: `SEVF_SPEC_CID_007_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AF  
> **Framework**: `SEVF-v1`  
> **Identity**: `SIF_CID_007_V0_1` · `STRAT_SESS_OPP19_01@0.1.0`  
> **Morphology**: `OPP19_MS_V0_1`（OD-Breakout only）

## Spec record

```text
================================================
SEVF_SPEC_CID_007_V0_1

Bound identity: STRAT_SESS_OPP19_01@0.1.0
source_hash:    f7cbcb3f9b556af5478d7f88fa9d7f51627887250273b4bd4c153e38e43d90d6
parameter_hash: 3f9793feda3d0ca20ba238197acbf120a469a486620b0f23a002dcceb5762a05
Alpha:          NONE at Spec time
================================================
```

## Hypothesis families（one primary per EXP）

| Family | Intent |
|--------|--------|
| `H_MECH` | Auditable OPP19 OD-Breakout→entry→exit（STOP/TARGET/TIME_STOP） |
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
❌ Prior CID Alpha transfer
❌ OD_REV under this Spec
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | SPECIFIED · Delegation-25AF |
