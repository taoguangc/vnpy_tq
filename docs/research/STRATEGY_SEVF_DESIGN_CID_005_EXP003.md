# SEVF Design Note — STRAT_RO17_EXP003（H_EDGE multi-year sample）

> **Status**: **DESIGNED** ✓  
> **Experiment ID**: `STRAT_RO17_EXP003`  
> **Authorization**: Delegation-25W  
> **Spec**: `SEVF_SPEC_CID_005_V0_1`  
> **Parent**: EXP002 HOLD（n_gate&lt;50）· EXP001 H_MECH KEEP

## Single hypothesis

```text
H_EDGE（multi-year sample · rb · 2023–2024 · @0.1.0）:
  Under docs/07 · frozen hashes · real costs · SAME numeric gates as EXP002,
  expanding the calendar window supplies n_gate≥50 so structure_A and
  expectancy_B can be adjudicated（KEEP or REVERT）.
```

## Decision rule（identical to EXP002）

```text
ABORT: hash mismatch
HOLD:  n_gate < 50
KEEP:  n≥50 · median_mfe>median_mae · share≥0.55
       · mean_net>0 · p_one<0.05
REVERT: n≥50 · KEEP conditions not all met
```

```text
Window change ≠ parameter change
MIN_N not lowered
KEEP ≠ Alpha Candidate
```

## Non-goals

```text
❌ Retune climax_range_atr · rewrite EXP002 · claim Alpha from multi-year alone
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | Designed · Delegation-25W |
