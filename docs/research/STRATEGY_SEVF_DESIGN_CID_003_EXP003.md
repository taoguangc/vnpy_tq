# SEVF Design Note — STRAT_RO16_EXP003（H_EDGE diagnostic）

> **Type**: Experiment Design（companion to Fill）  
> **Status**: **DESIGNED** ✓  
> **Experiment ID**: `STRAT_RO16_EXP003`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-20  
> **Spec**: `SEVF_SPEC_CID_003_V0_1_1`  
> **Identity**: `SIF_CID_003_V0_1_1`

## Single hypothesis

```text
H_EDGE（diagnostic · rb/2024 · @0.1.1）:
  Under docs/07 · frozen hashes · real costs, closed trips show
  (A) favorable excursion structure（MFE vs MAE）AND
  (B) positive mean net_pnl after costs with one-sided test vs 0
  under pre-registered numeric gates（Fill §6）.
```

## Single variable

```text
VARIABLE = hypothesis family H_EDGE（first edge screen）
HELD     = @0.1.1 identity · params · OPP16 · costs · rb · 2024
BASELINE = H_MECH KEEP on same scope（EXP002）≠ edge proof
```

## Explicit non-goals

```text
❌ Alpha Candidate
❌ Parameter change
❌ PnL maximize as sole gate
❌ Rewrite EXP001/002
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | Designed under Delegation-20 |
