# Beyond-opp Posture — Reaffirmation

> **Type**: Posture Reaffirmation  
> **Status**: **RETAINED** ✓  
> **Decision ID**: `RPP_BEYOND_OPP_V0_1_R1`  
> **Date**: 2026-07-24  
> **Parent**: `RPP_BEYOND_OPP_V0_1`  
> **Authorization**: Delegation-25AZ（`授权你决定25次`）

## Decision

```text
RPP_BEYOND_OPP_V0_1 remains in force.
CID_003–012 remain PAUSED.

This bare grant does NOT pick menu options A–E.
This grant does NOT open NSAD_CID_013.
This grant does NOT authorize smc seed, Spec recovery, or Resume.
```

## Why reaffirm（not auto-pick）

```text
RPP already stated:
  bare “授权你决定N次” without picking A–E is NOT a sufficient wake.

Auto-picking smc / inventing Spec / Resuming would convert a meta-grant
into an implicit seed choice the posture explicitly withheld.

Correct use: reaffirm posture · republish A–E menu · STOP.
```

## Menu retained（须明确句）

| Option | Example wake |
|--------|----------------|
| A | `Authorize NSAD seed: smc_orderflow_vwap` |
| B | `Authorize Morphology Spec recovery for OPP0X` + source bytes |
| C | `Resume CID_012` + scoped multi-symbol power |
| D | `Resume CID_010`（or other）+ scoped power |
| E | Leave shelf-exhausted posture · no new campaign |

## Revision record

| Date | Change |
|------|--------|
| 2026-07-24 | RPP_BEYOND_OPP_V0_1_R1 RETAINED · Delegation-25AZ |
