# SEVF Design Note — STRAT_SO19R_EXP002（H_EDGE diagnostic）

> **Status**: **DESIGNED** ✓  
> **Experiment ID**: `STRAT_SO19R_EXP002`  
> **Authorization**: Delegation-25AT  
> **Spec**: `SEVF_SPEC_CID_011_V0_1`  
> **Parent**: EXP001 H_MECH KEEP

## Single hypothesis

```text
H_EDGE（diagnostic · rb/2024 · @0.1.0）:
  Under docs/07 · frozen hashes · real costs, closed trips show
  (A) favorable excursion structure（MFE vs MAE）AND
  (B) positive mean net_pnl after costs with one-sided test vs 0
  under pre-registered numeric gates（same template as prior CIDs）.
```

## Decision rule（pre-registered）

```text
ABORT: hash mismatch
HOLD:  n_gate < 50
KEEP:  n≥50 · median_mfe>median_mae · share_mfe_gt_mae≥0.55
       · mean_net_pnl>0 · p_one_sided<0.05
REVERT: n≥50 · KEEP conditions not all met
```

```text
KEEP ≠ Alpha Candidate
REVERT ≠ delete H_MECH · Negative Evidence first-class
HOLD ≠ REVERT
```

## Non-goals

```text
❌ Alpha Candidate · parameter retune · CID_007 merge
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | Designed · Delegation-25AT |
