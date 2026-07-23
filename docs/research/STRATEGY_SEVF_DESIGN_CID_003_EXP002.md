# SEVF Design Note — STRAT_RO16_EXP002（H_MECH @0.1.1）

> **Type**: Experiment Design（companion to Fill）  
> **Status**: **DESIGNED** ✓  
> **Experiment ID**: `STRAT_RO16_EXP002`  
> **Date**: 2026-07-23  
> **Authorization**: `Authorize SEVF Fill / Pre-registration for STRAT_RO16_EXP002（H_MECH @0.1.1）`  
> **Spec**: `SEVF_SPEC_CID_003_V0_1_1`  
> **Identity**: `SIF_CID_003_V0_1_1`

## Single hypothesis

```text
H_MECH:
  Under docs/07 · rb · 2024 · frozen STRAT_REV_OPP16_01@0.1.1
  （adapter window repair）,
  the mechanism produces ≥1 auditable closed exit with reason in
  {STOP, TARGET, TIME_STOP} attributable to OPP16@1.0.0.
```

## Single variable

```text
VARIABLE = first Observation under repaired @0.1.1 identity
           with continuity scope rb/2024（same calendar as EXP001）
HELD     = params · OPP16 morphology · costs · docs/07 · rb · 2024
CHANGED  = identity version / adapter binding（engineering repair only）
BASELINE = EXP001 HOLD under @0.1.0（engineering-blocked；not morphology verdict）
```

## Explicit non-goals

```text
❌ H_EDGE / Alpha
❌ Parameter change（body_ratio / RR / size）
❌ PnL gates
❌ Rewrite Closed EXP001
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | Designed with Fill |
