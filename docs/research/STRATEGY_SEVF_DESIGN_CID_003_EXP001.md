# SEVF Design Note — STRAT_RO16_EXP001（H_MECH）

> **Type**: Experiment Design（companion to Fill）  
> **Status**: **DESIGNED** ✓  
> **Experiment ID**: `STRAT_RO16_EXP001`  
> **Date**: 2026-07-23  
> **Authorization**: `Authorize SEVF Fill / Pre-registration for STRAT_RO16_EXP001（H_MECH）`  
> **Spec**: `SEVF_SPEC_CID_003_V0_1`

## Single hypothesis

```text
H_MECH:
  Under docs/07 · rb · 2024 · frozen STRAT_REV_OPP16_01@0.1.0,
  the mechanism produces ≥1 auditable closed exit with reason in
  {STOP, TARGET, TIME_STOP} attributable to OPP16@1.0.0.
```

## Single variable

```text
VARIABLE_0 = first Observation under frozen identity + declared market_scope
HELD = hashes · detector · params · costs · symbol rb · calendar 2024
```

## Explicit non-goals

```text
❌ H_EDGE / Alpha
❌ Parameter change
❌ PnL gates
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | Designed with Fill |
