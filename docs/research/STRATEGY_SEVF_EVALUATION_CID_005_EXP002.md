# SEVF Evaluation — STRAT_RO17_EXP002

> **Status**: **CLOSED** ✓ · **HOLD**  
> **Experiment ID**: `STRAT_RO17_EXP002`  
> **Authorization**: Delegation-25V  
> **Harness**: `scripts/run_strat_ro17_exp002.py`

## Outcome

```text
HOLD
H_EDGE · rb/2024 · @0.1.0

n_gate = 32 < 50 → structure/expectancy gates NOT adjudicated
```

## Gate check

| Gate | Result |
|------|--------|
| Identity hashes | PASS |
| n_gate ≥ 50 | **FAIL**（32）→ HOLD |
| median_mfe > median_mae | descriptive only（7 > 6） |
| share ≥ 0.55 | descriptive only（≈0.46） |
| mean_net > 0 | descriptive only（≈−4.6） |
| p_one < 0.05 | descriptive only（≈0.60） |

## Interpretation

```text
HOLD = insufficient sample for H_EDGE KEEP/REVERT under frozen MIN_N
     ≠ Alpha
     ≠ license to retune climax_range_atr
     ≠ delete H_MECH KEEP
```

## Non-claims

```text
❌ Alpha · retune · lower MIN_N · claim structure PASS
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | CLOSED · HOLD |
