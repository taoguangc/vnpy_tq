# SEVF Design Note — STRAT_RO16_EXP007（H_CAPITAL_GATE）

> **Status**: **DESIGNED** ✓  
> **Experiment ID**: `STRAT_RO16_EXP007`  
> **Date**: 2026-07-23  
> **Authorization**: `Authorize SEVF Fill for STRAT_RO16_EXP007（H_CAPITAL_GATE · i/2024 @0.2.0）`  
> **Spec**: `SEVF_SPEC_CID_003_V0_2_0`  
> **Identity**: `SIF_CID_003_V0_2_0`

## Single hypothesis

```text
H_CAPITAL_GATE（smoke · i/2024 · @0.2.0）:
  Under docs/07 · capital=200_000 · frozen positioning defaults,
  engine path does not hit capital≤0 death
  OR equity kill-switch engages before wipe.
```

## Single variable

```text
VARIABLE = first capital-gate Observation under @0.2.0 on stress symbol i
HELD     = hashes · OPP16 morphology · calendar 2024 · docs/07 costs
BASELINE = EXP005 @0.1.1 i 爆仓（OPEN RISK · fixed_size=1）
```

## Non-goals

```text
❌ H_MECH / Alpha / Bindable
❌ PnL KEEP gates
❌ Multi-symbol yet（portability = later EXP）
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | Designed with Fill |
