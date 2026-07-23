# SEVF Design Note — STRAT_RO13DT_EXP002（H_MECH alt-year power）

> **Status**: **DESIGNED** ✓  
> **Experiment ID**: `STRAT_RO13DT_EXP002`  
> **Authorization**: Delegation-25AW  
> **Spec**: `SEVF_SPEC_CID_012_V0_1`  
> **Parent**: EXP001 H_MECH HOLD（rb/2024 · n=0）

## Single hypothesis

```text
H_MECH（alt-year power · rb/2023 · @0.1.0）:
  Under docs/07 · frozen STRAT_REV_OPP13_DT_01@0.1.0 · SAME hashes,
  the mechanism produces ≥1 auditable closed exit with reason in
  {STOP, TARGET, TIME_STOP} attributable to OPP13_DT@1.0.0
  on calendar 2023（warmup from 2022-12）.

Purpose: test whether EXP001 HOLD was period scarcity vs mechanism silence.
≠ H_EDGE · ≠ parameter change · ≠ multi-symbol hunt beyond this one scope
```

## Decision rule

| Outcome | Condition |
|---------|-----------|
| **REVERT** | identity hash mismatch · OR missing on_rollover_adjust WARN |
| **HOLD** | no auditable attributed exits |
| **KEEP** | ≥1 attributed exit in period |

```text
PnL: descriptive only · KEEP ≠ Alpha
EXP002 KEEP does not reopen EXP001 · does not mint Alpha
```

## Explicit non-goals

```text
❌ H_EDGE under this EXP id
❌ Retune DT parameters
❌ CID_010 merge
❌ Claim Alpha from alt-year KEEP alone
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-24 | Designed · Delegation-25AW |
