# SEVF Evaluation — STRAT_TO02_EXP003

> **Status**: **CLOSED** ✓  
> **Experiment ID**: `STRAT_TO02_EXP003`  
> **Authorization**: Delegation-25AK  
> **Harness**: `scripts/run_strat_to02_exp003.py`

## Outcome

```text
REVERT
H_EDGE OOS · STRAT_TREND_OPP02_01@0.1.0 · rb/2025 · OPP02@1.0.0

n_gate = 2464
median_mfe = 2.0 · median_mae = 3.0 · share = 0.350
mean_net = -27.16 · p_one = 1.0
structure_ok = False · expectancy_ok = False
```

## Decision rule check

| Gate | Result |
|------|--------|
| Identity hashes | PASS |
| n_gate ≥ 50 | PASS |
| median_mfe > median_mae | FAIL |
| share ≥ 0.55 | FAIL（0.350） |
| mean_net > 0 | FAIL |
| p_one < 0.05 | FAIL |

## Non-claims

```text
❌ Alpha rescue · parameter retune · reopen EXP002
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | CLOSED · REVERT |
