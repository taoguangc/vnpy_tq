# SEVF Evaluation — STRAT_RO17_EXP003

> **Status**: **CLOSED** ✓ · **REVERT**  
> **Experiment ID**: `STRAT_RO17_EXP003`  
> **Authorization**: Delegation-25W  
> **Harness**: `scripts/run_strat_ro17_exp003.py`

## Outcome

```text
REVERT
H_EDGE · rb/2023–2024 · @0.1.0

structure_ok: False
expectancy_ok: False
```

## Gate check

| Gate | Result |
|------|--------|
| Identity hashes | PASS |
| n_gate ≥ 50 | PASS（60） |
| median_mfe > median_mae | FAIL（6 ≯ 6） |
| share ≥ 0.55 | FAIL（≈0.42） |
| mean_net > 0 | FAIL（≈−7.4） |
| p_one < 0.05 | FAIL（≈0.68） |

## Non-claims

```text
❌ Alpha · retune · delete H_MECH · rewrite EXP002
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | CLOSED · REVERT |
