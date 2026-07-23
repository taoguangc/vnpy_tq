# SEVF Evaluation — STRAT_RO12_EXP002

> **Status**: **CLOSED** ✓ · **REVERT**  
> **Experiment ID**: `STRAT_RO12_EXP002`  
> **Authorization**: Delegation-25Q

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
| n ≥ 50 | PASS |
| median_mfe > median_mae | FAIL（2 ≤ 4） |
| share ≥ 0.55 | FAIL（≈0.36） |
| mean_net > 0 | FAIL（≈−27.9） |
| p_one < 0.05 | FAIL（≈1.0） |

## Non-claims

```text
❌ Alpha · retune · delete H_MECH
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | CLOSED · REVERT |
