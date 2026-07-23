# SEVF Evaluation — STRAT_TO02_EXP002

> **Status**: **CLOSED** ✓  
> **Experiment ID**: `STRAT_TO02_EXP002`  
> **Authorization**: Delegation-25AK  
> **Harness**: `scripts/run_strat_to02_exp002.py`

## Outcome

```text
REVERT
H_EDGE · STRAT_TREND_OPP02_01@0.1.0 · rb/2024 · OPP02@1.0.0

n_gate = 2439
median_mfe = 3.0 · median_mae = 4.0 · share = 0.386
mean_net = -24.77 · p_one = 1.0
structure_ok = False · expectancy_ok = False
```

## Decision rule check

| Gate | Result |
|------|--------|
| Identity hashes | PASS |
| n_gate ≥ 50 | PASS |
| median_mfe > median_mae | FAIL |
| share ≥ 0.55 | FAIL（0.386） |
| mean_net > 0 | FAIL |
| p_one < 0.05 | FAIL |

## Non-claims

```text
❌ Alpha · Bindable · delete H_MECH KEEP · parameter retune under same id
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | CLOSED · REVERT |
