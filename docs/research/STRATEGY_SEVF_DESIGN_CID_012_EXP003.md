# SEVF Design Note — STRAT_RO13DT_EXP003（H_EDGE diagnostic）

> **Status**: **DESIGNED** ✓  
> **Experiment ID**: `STRAT_RO13DT_EXP003`  
> **Authorization**: Delegation-25AX  
> **Spec**: `SEVF_SPEC_CID_012_V0_1`  
> **Parent**: EXP002 H_MECH KEEP（rb/2023 · n=4）

## Single hypothesis

```text
H_EDGE（diagnostic · rb/2023 · @0.1.0）:
  Under docs/07 · frozen hashes · real costs, closed trips show
  (A) favorable excursion structure（MFE vs MAE）AND
  (B) positive mean net_pnl after costs with one-sided test vs 0
  under pre-registered numeric gates（same template as prior CIDs）.

Honesty: parent H_MECH n=4 ≪ MIN_N=50 → HOLD is the expected branch
         if frequency does not jump under H_EDGE pairing.
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
HOLD ≠ REVERT · HOLD ≠ license to retune
REVERT ≠ delete H_MECH
```

## Non-goals

```text
❌ Alpha Candidate · parameter retune · CID_010 merge · inflate n
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-24 | Designed · Delegation-25AX |
