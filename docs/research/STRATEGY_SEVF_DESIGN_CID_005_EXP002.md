# SEVF Design Note — STRAT_RO17_EXP002（H_EDGE diagnostic）

> **Status**: **DESIGNED** ✓  
> **Experiment ID**: `STRAT_RO17_EXP002`  
> **Authorization**: Delegation-25V  
> **Spec**: `SEVF_SPEC_CID_005_V0_1`  
> **Parent**: EXP001 H_MECH KEEP

## Single hypothesis

```text
H_EDGE（diagnostic · rb/2024 · @0.1.0）:
  Under docs/07 · frozen hashes · real costs, closed trips show
  (A) favorable excursion structure（MFE vs MAE）AND
  (B) positive mean net_pnl after costs with one-sided test vs 0
  under pre-registered numeric gates（same template as CID_004 EXP002）.
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
HOLD ≠ rescue retune authorization
```

## Non-goals

```text
❌ Alpha Candidate · parameter retune · PnL maximize as sole gate
```

## Note on sample size

```text
EXP001 attributed=35 on same scope.
H_EDGE may HOLD under n_gate<50 without changing Identity.
HOLD is not a license to lower MIN_N post-hoc.
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | Designed · Delegation-25V |
