# SEVF Evaluation — STRAT_TO08_EXP002

> **Status**: **CLOSED** ✓ · **REVERT**  
> **Experiment ID**: `STRAT_TO08_EXP002`  
> **Authorization**: Delegation-25AB  
> **Harness**: `scripts/run_strat_to08_exp002.py`

## Outcome

```text
REVERT
H_EDGE · rb/2024 · @0.1.0

structure_ok: False
expectancy_ok: False
```

## Gate check

| Gate | Result |
|------|--------|
| Identity hashes | PASS |
| n_gate ≥ 50 | PASS（1251） |
| median_mfe > median_mae | FAIL（5 ≯ 5） |
| share ≥ 0.55 | FAIL（≈0.43） |
| mean_net > 0 | FAIL（≈−17.7） |
| p_one < 0.05 | FAIL（≈1.0） |

## Non-claims

```text
❌ Alpha · retune · delete H_MECH
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | CLOSED · REVERT |
