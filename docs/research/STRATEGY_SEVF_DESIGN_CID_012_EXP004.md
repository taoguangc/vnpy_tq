# SEVF Design Note — STRAT_RO13DT_EXP004（H_EDGE OOS）

> **Status**: **DESIGNED** ✓  
> **Experiment ID**: `STRAT_RO13DT_EXP004`  
> **Authorization**: Delegation-25AX  
> **Spec**: `SEVF_SPEC_CID_012_V0_1`  
> **Parent**: EXP003 H_EDGE HOLD（rb/2023 · n_gate=4）

## Single hypothesis

```text
H_EDGE（temporal OOS · rb/2025 · @0.1.0）:
  Same pre-registered gates as EXP003 on a later calendar year.
  Does not reopen EXP003 · does not retune.
```

## Decision rule（pre-registered）

```text
ABORT: hash mismatch
HOLD:  n_gate < 50
KEEP:  n≥50 · median_mfe>median_mae · share≥0.55 · mean_net>0 · p_one<0.05
REVERT: n≥50 · KEEP conditions not all met
```

## Non-goals

```text
❌ Alpha Candidate · parameter retune · treat descriptive sub-MIN_N as KEEP
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-24 | Designed · Delegation-25AX |
