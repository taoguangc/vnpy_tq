# SEVF Evaluation — STRAT_RO17_EXP004

> **Status**: **CLOSED** ✓ · **HOLD**  
> **Experiment ID**: `STRAT_RO17_EXP004`  
> **Authorization**: Delegation-25X  
> **Harness**: `scripts/run_strat_ro17_exp004.py`

## Outcome

```text
HOLD
H_EDGE OOS · rb/2025 · @0.1.0

n_gate = 40 < 50 → structure/expectancy NOT adjudicated
```

## Gate check

| Gate | Result |
|------|--------|
| Identity hashes | PASS |
| n_gate ≥ 50 | **FAIL**（40）→ HOLD |
| median_mfe > median_mae | descriptive（2.5 ≯ 5） |
| share ≥ 0.55 | descriptive（≈0.34） |
| mean_net > 0 | descriptive（≈−22.9） |
| p_one < 0.05 | descriptive（≈0.98） |

## Non-claims

```text
❌ Alpha · retune · treat HOLD as KEEP · delete H_MECH
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | CLOSED · HOLD |
