# SEVF Evaluation — STRAT_RO15_EXP003

> **Status**: **CLOSED** ✓  
> **Experiment ID**: `STRAT_RO15_EXP003`  
> **Authorization**: Delegation-25AN  
> **Harness**: `scripts/run_strat_ro15_exp003.py`

## Outcome

```text
REVERT
H_EDGE OOS · STRAT_REV_OPP15_01@0.1.0 · rb/2025 · OPP15@1.0.0

n_gate = 398
median_mfe = 5.0 · median_mae = 6.0 · share = 0.399
mean_net = -28.49 · p_one ≈ 1.0
structure_ok = False · expectancy_ok = False
```

## Decision rule check

| Gate | Result |
|------|--------|
| Identity hashes | PASS |
| n_gate ≥ 50 | PASS |
| median_mfe > median_mae | FAIL |
| share ≥ 0.55 | FAIL（0.399） |
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
