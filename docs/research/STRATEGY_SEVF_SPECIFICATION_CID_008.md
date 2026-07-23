# SEVF Specification — CID_008 / STRAT_TREND_OPP02_01

> **Type**: Asset-bound SEVF Specification（≠ Fill · ≠ Observation alone）  
> **Status**: **SPECIFIED** ✓  
> **Spec ID**: `SEVF_SPEC_CID_008_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AJ  
> **Framework**: `SEVF-v1`  
> **Identity**: `SIF_CID_008_V0_1` · `STRAT_TREND_OPP02_01@0.1.0`  
> **Morphology**: `OPP02_MS_V0_1`

## Spec record

```text
================================================
SEVF_SPEC_CID_008_V0_1

Bound identity: STRAT_TREND_OPP02_01@0.1.0
source_hash:    c6e47760e11290b171aec8d50c7f727606ed5df147ecb6eaa3b660fa62de9f99
parameter_hash: 06b64730fa61b0b1c9411feb332140d5a7b4911339c035ac30f0ede406db7a86
Alpha:          NONE at Spec time
================================================
```

## Hypothesis families（one primary per EXP）

| Family | Intent |
|--------|--------|
| `H_MECH` | Auditable OPP02 EMA-pullback→entry→exit（STOP/TARGET/TIME_STOP） |
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
❌ BROOKS / OPP08 parameter transfer
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | SPECIFIED · Delegation-25AJ |
