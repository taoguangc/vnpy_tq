# SEVF Evaluation — STRAT_SO19_EXP003

> **Status**: **CLOSED** ✓ · **REVERT**  
> **Experiment ID**: `STRAT_SO19_EXP003`  
> **Authorization**: Delegation-25AH  
> **Harness**: `scripts/run_strat_so19_exp003.py`

## Outcome

```text
REVERT
H_EDGE OOS · rb/2025 · @0.1.0

structure_ok: False
expectancy_ok: False
```

## Gate check

| Gate | Result |
|------|--------|
| Identity hashes | PASS |
| n_gate ≥ 50 | PASS（330） |
| median_mfe > median_mae | FAIL（3 ≯ 4） |
| share ≥ 0.55 | FAIL（≈0.38） |
| mean_net > 0 | FAIL（≈−23.3） |
| p_one < 0.05 | FAIL（≈1.0） |

## Non-claims

```text
❌ Alpha · retune · delete H_MECH · OD_REV
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | CLOSED · REVERT |
