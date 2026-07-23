# SEVF Evaluation — STRAT_RO13_EXP002

> **Status**: **CLOSED** ✓  
> **Experiment ID**: `STRAT_RO13_EXP002`  
> **Authorization**: Delegation-25AQ  
> **Harness**: `scripts/run_strat_ro13_exp002.py`

## Outcome

```text
HOLD
H_EDGE · STRAT_REV_OPP13_01@0.1.0 · rb/2024 · OPP13@1.0.0

n_gate = 40 < MIN_N=50
（structure/expectancy gates not evaluated for KEEP/REVERT）
descriptive: share≈0.439 · mean_net≈−22.6 · p_one≈0.964
```

## Decision rule check

| Gate | Result |
|------|--------|
| Identity hashes | PASS |
| n_gate ≥ 50 | **FAIL** → HOLD |
| KEEP/REVERT structure+expectancy | NOT REACHED |

## Non-claims

```text
❌ Alpha · Bindable · treat HOLD as REVERT · parameter retune under same id
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | CLOSED · HOLD |
