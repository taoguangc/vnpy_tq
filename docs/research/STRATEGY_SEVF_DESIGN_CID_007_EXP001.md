# SEVF Design Note — STRAT_SO19_EXP001（H_MECH）

> **Status**: **DESIGNED** ✓  
> **Experiment ID**: `STRAT_SO19_EXP001`  
> **Authorization**: Delegation-25AF  
> **Spec**: `SEVF_SPEC_CID_007_V0_1`

## Single hypothesis

```text
H_MECH:
  Under docs/07 · rb · 2024 · frozen STRAT_SESS_OPP19_01@0.1.0,
  the mechanism produces ≥1 auditable closed exit with reason in
  {STOP, TARGET, TIME_STOP} attributable to OPP19@1.0.0 OD-Breakout.
```

## Decision rule

| Outcome | Condition |
|---------|-----------|
| **REVERT** | identity hash mismatch · OR missing on_rollover_adjust WARN |
| **HOLD** | no auditable attributed exits |
| **KEEP** | ≥1 attributed exit in period |

```text
PnL: descriptive only
```

## Explicit non-goals

```text
❌ H_EDGE / Alpha · parameter change · Bindable · OD_REV
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | Designed · Delegation-25AF |
