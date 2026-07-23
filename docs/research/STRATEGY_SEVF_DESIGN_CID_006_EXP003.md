# SEVF Design Note — STRAT_TO08_EXP003（H_EDGE temporal OOS）

> **Status**: **DESIGNED** ✓  
> **Experiment ID**: `STRAT_TO08_EXP003`  
> **Authorization**: Delegation-25AC  
> **Spec**: `SEVF_SPEC_CID_006_V0_1`  
> **Parent**: EXP002 REVERT · EXP001 H_MECH KEEP

## Single hypothesis

```text
H_EDGE（temporal OOS · rb/2025 · @0.1.0）:
  Under docs/07 · frozen hashes · real costs · SAME gates as EXP002,
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
❌ Alpha rescue · parameter retune · rewrite EXP001/002
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | Designed · Delegation-25AC |
