# SEVF Evaluation — STRAT_SO19R_EXP003

> **Status**: **CLOSED** ✓  
> **Experiment ID**: `STRAT_SO19R_EXP003`  
> **Authorization**: Delegation-25AT  
> **Harness**: `scripts/run_strat_so19r_exp003.py`

## Outcome

```text
REVERT
H_EDGE OOS · STRAT_SESS_OPP19_REV_01@0.1.0 · rb/2025 · OPP19_REV@1.0.0

n_gate = 98
median_mfe = 3.0 · median_mae = 3.0 · share = 0.434
mean_net = -19.64 · p_one ≈ 1.0
structure_ok = False · expectancy_ok = False
```

## Decision rule check

| Gate | Result |
|------|--------|
| Identity hashes | PASS |
| n_gate ≥ 50 | PASS |
| median_mfe > median_mae | FAIL（3.0 ≯ 3.0） |
| share ≥ 0.55 | FAIL（0.434） |
| mean_net > 0 | FAIL |
| p_one < 0.05 | FAIL |

## Non-claims

```text
❌ Alpha rescue · parameter retune · reopen EXP002 · CID_007 merge
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | CLOSED · REVERT |
