# SEVF Design Note — STRAT_RO16_EXP005（H_MECH multi-symbol）

> **Status**: **DESIGNED** ✓  
> **Experiment ID**: `STRAT_RO16_EXP005`  
> **Authorization**: Delegation-50  
> **Identity**: `SIF_CID_003_V0_1_1`

## Hypothesis

```text
H_MECH portability:
  For each symbol in predeclared {rb, i, MA} under docs/07 · 2024 · @0.1.1,
  ≥1 auditable closed exit with reason in {STOP,TARGET,TIME_STOP}.
```

## Single variable

```text
VARIABLE = symbol universe expansion（continuity set）
HELD     = identity · params · calendar 2024 · costs · H_MECH gates
```

## Non-goals

```text
❌ H_EDGE / Alpha reopen
❌ Capital-survival KEEP（i sizing risk = descriptive only）
❌ PnL gates
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | Designed under Delegation-50 |
