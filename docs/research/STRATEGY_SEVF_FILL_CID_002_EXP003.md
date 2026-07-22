# SEVF Fill / Pre-registration — STRAT_BS02_EXP003（H_ROBUST temporal OOS）

> **Type**: Experiment Fill + Pre-registration  
> **Status**: **PRE-REGISTERED** ✓  
> **Experiment ID**: `STRAT_BS02_EXP003`  
> **Spec**: `SEVF_SPEC_CID_002_V0_1`  
> **Identity**: `SIF_CID_002_V0_1`  
> **Date**: 2026-07-22  
> **Authorization**: Fifty-round delegated decisions 13–17  
> **Prior**: EXP001 H_MECH KEEP；EXP002 H_NULL（separate claim）

## Record

```text
================================================
STRAT_BS02_EXP003 — PRE-REGISTERED ✓

Hypothesis family: H_ROBUST（temporal OOS of H_MECH）
Variable:          period only（2025 vs EXP001 2024）
Symbol/identity:   unchanged
================================================
```

## 1. Primary hypothesis

**Family**: `H_ROBUST` / temporal

> Under rb and docs/07 baseline, the frozen identity still produces ≥1 auditable closed round-trip in **2025-01-01..2025-12-31** attributable to `BROOKS_SCALP_FP@0.1.0` with exit_reason ∈ {STOP, TARGET, TIME_STOP} and matching identity hashes.

Same KEEP/HOLD/REVERT structure as EXP001 H_MECH（mechanism replication on later window）.

## 2. Market scope

```text
symbols: rb
period:  2025-01-01 .. 2025-12-31
warmup:  2024-12-01
sample:  TEMPORAL_OOS_MECHANISM
data:    docs/07 v1.0.0
```

Period chosen as the contiguous next calendar year after EXP001 IS（not PnL-ranked）.

## 3. Decision rule

Identical to EXP001 H_MECH audit rule（mechanism）.

Expectancy / t-test vs 0 may be reported **descriptively only**（not KEEP driver for EXP003）.

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Pre-registered under Delegation-50 |
