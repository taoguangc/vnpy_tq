# SEVF Design Note — STRAT_RO17_EXP004（H_EDGE temporal OOS）

> **Status**: **DESIGNED** ✓  
> **Experiment ID**: `STRAT_RO17_EXP004`  
> **Authorization**: Delegation-25X  
> **Spec**: `SEVF_SPEC_CID_005_V0_1`  
> **Parent**: EXP003 REVERT（multi-year）· EXP001 H_MECH KEEP

## Single hypothesis

```text
H_EDGE（temporal OOS · rb/2025 · @0.1.0）:
  Under docs/07 · frozen hashes · real costs · SAME gates as EXP002/003,
  the forming-window REVERT does not reverse on the next calendar year.
```

## Decision rule（identical）

```text
ABORT: hash mismatch
HOLD:  n_gate < 50
KEEP:  n≥50 · median_mfe>median_mae · share≥0.55
       · mean_net>0 · p_one<0.05
REVERT: n≥50 · KEEP conditions not all met
```

## Non-goals

```text
❌ Alpha rescue · parameter retune · rewrite EXP002/003
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | Designed · Delegation-25X |
