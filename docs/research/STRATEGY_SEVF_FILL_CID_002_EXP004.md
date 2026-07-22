# SEVF Fill — STRAT_BS02_EXP004（H_ROBUST OOS · audit-join fix）

> **Type**: Experiment Fill + Pre-registration  
> **Status**: **PRE-REGISTERED** ✓  
> **Experiment ID**: `STRAT_BS02_EXP004`  
> **Date**: 2026-07-22  
> **Authorization**: Delegation-50  
> **Prior**: `STRAT_BS02_EXP003` Closed **HOLD**（exit_reason join incomplete on round-trip path）

## Hypothesis

Same as EXP003 H_ROBUST temporal OOS H_MECH replication（rb · 2025）.

## Single variable

```text
VARIABLE = evidence audit join method
  EXP003: round-trip rows + exit_time join to strategy log（failed → UNKNOWN）
  EXP004: primary audit rows from strategy._trade_log（same as EXP001）
Identity / scope / parameters unchanged
```

## Decision rule

Identical to EXP001 / EXP003 H_MECH audit rule.

## Scope

```text
rb · 2025-01-01..2025-12-31 · warmup 2024-12-01 · docs/07 v1.0.0
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Pre-registered after EXP003 HOLD |
