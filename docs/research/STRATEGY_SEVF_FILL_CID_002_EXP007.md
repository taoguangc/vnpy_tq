# SEVF Fill — STRAT_BS02_EXP007（multi-symbol H_MECH · v0.1.1）

> **Status**: **PRE-REGISTERED** ✓  
> **Experiment ID**: `STRAT_BS02_EXP007`  
> **Identity**: `SIF_CID_002_V0_1_1`  
> **Authorization**: Delegation-50C  
> **Family**: `H_MECH` portability

## Hypothesis

> Under docs/07 and 2024-01-01..2024-12-31, for **each** symbol in the predeclared universe `{rb, i, MA}`, `STRAT_TREND_BROOKS_SCALP_02@0.1.1` produces ≥1 auditable closed round-trip with exit_reason ∈ {STOP,TARGET,TIME_STOP} and matching identity hashes.

## Universe selection

```text
{rb, i, MA} = project research continuity set（CAP-CTX primary pattern）
NOT selected by historical return ranking
```

## Aggregate decision rule

| Outcome | Rule |
|---------|------|
| **KEEP** | all three symbols individually meet H_MECH KEEP |
| **HOLD** | no REVERT, but ≥1 symbol HOLD（0 trades / incomplete） |
| **REVERT** | any symbol identity hash failure or missing detector attribution |

Per-symbol results recorded in artifact. PnL not KEEP driver.

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Pre-registered |
