# SEVF Evaluation — STRAT_SO19R_EXP002

> **Status**: **CLOSED** ✓  
> **Experiment ID**: `STRAT_SO19R_EXP002`  
> **Authorization**: Delegation-25AT  
> **Harness**: `scripts/run_strat_so19r_exp002.py`

## Outcome

```text
REVERT
H_EDGE · STRAT_SESS_OPP19_REV_01@0.1.0 · rb/2024 · OPP19_REV@1.0.0

n_gate = 114
median_mfe = 3.0 · median_mae = 5.0 · share = 0.419
mean_net = -19.94 · p_one ≈ 0.998
structure_ok = False · expectancy_ok = False
```

## Decision rule check

| Gate | Result |
|------|--------|
| Identity hashes | PASS |
| n_gate ≥ 50 | PASS |
| median_mfe > median_mae | FAIL |
| share ≥ 0.55 | FAIL（0.419） |
| mean_net > 0 | FAIL |
| p_one < 0.05 | FAIL |

## Non-claims

```text
❌ Alpha · Bindable · delete H_MECH KEEP · parameter retune · CID_007 merge
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | CLOSED · REVERT |
