# SEVF Fill / Pre-registration — STRAT_RO16_EXP004（H_EDGE OOS）

> **Status**: **PRE-REGISTERED** ✓  
> **Experiment ID**: `STRAT_RO16_EXP004`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-20  
> **Identity**: `SIF_CID_003_V0_1_1` · `@0.1.1`  
> **Parent**: EXP003 REVERT  
> **Gates**: identical to EXP003 §5–§6（A/B · min_n=50 · share≥0.55 · mean_net>0 · p<0.05）

## Record

```text
================================================
STRAT_RO16_EXP004 — PRE-REGISTERED ✓ · OBSERVATION CLOSED

Hypothesis: H_EDGE temporal OOS
Scope:      rb · 2025
Observation: EXECUTED 2026-07-23 → REVERT
================================================
```

## Bound identity

Same hashes / class as EXP003（`SIF_CID_003_V0_1_1`）.

## Market scope

```text
symbol: rb.SHFE · size 10 · pricetick 1.0
period: 2025-01-01 .. 2025-12-31
warmup: 2024-12-01
rate 0.00003 · slippage 1.0 · capital 200000
docs/07 TQ offline 1m CbC unadjusted
```

## Decision rule

Identical to [`STRATEGY_SEVF_FILL_CID_003_EXP003.md`](STRATEGY_SEVF_FILL_CID_003_EXP003.md) §6.

## Runner

`scripts/run_strat_ro16_exp004.py`

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | PRE-REGISTERED under Delegation-20 |
| 2026-07-23 | Observation CLOSED · REVERT |
