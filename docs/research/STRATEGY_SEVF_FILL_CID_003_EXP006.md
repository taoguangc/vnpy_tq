# SEVF Fill — STRAT_RO16_EXP006（H_MECH temporal OOS）

> **Status**: **PRE-REGISTERED** ✓  
> **Experiment ID**: `STRAT_RO16_EXP006`  
> **Authorization**: Delegation-50  
> **Identity**: `SIF_CID_003_V0_1_1`  
> **Family**: `H_MECH`  
> **Parent**: EXP005 KEEP

## Hypothesis

> Under docs/07 · rb · 2025 · frozen `@0.1.1`, ≥1 auditable closed exit with reason in {STOP,TARGET,TIME_STOP} and hash echo.

## Scope

```text
symbol rb.SHFE · 2025-01-01..2025-12-31 · warmup 2024-12-01
size 10 · pricetick 1 · rate 0.00003 · slippage 1 · capital 200000
```

## Decision rule

```text
ABORT: hash mismatch
HOLD:  attributed_exits < 1
KEEP:  attributed_exits ≥ 1 · no missing on_rollover_adjust WARN
REVERT: missing-hook WARN
PnL not a driver
```

## Runner

`scripts/run_strat_ro16_exp006.py`

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | PRE-REGISTERED under Delegation-50 |
| 2026-07-23 | Observation CLOSED · KEEP |
