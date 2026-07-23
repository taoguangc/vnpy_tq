# SEVF Evaluation — STRAT_BS02_EXP013

> **Type**: Closed Evaluation  
> **Status**: **CLOSED** ✓  
> **Experiment ID**: `STRAT_BS02_EXP013`  
> **Date**: 2026-07-23  
> **Authorization**: `Authorize Offline Alpha Evidence Observation for STRAT_BS02_EXP013`  
> **Fill**: [`STRATEGY_SEVF_FILL_CID_002_EXP013.md`](STRATEGY_SEVF_FILL_CID_002_EXP013.md)  
> **Artifacts**: `research/output/evidence/STRAT_BS02_EXP013/`

## Outcome

```text
Bundle outcome: REVERT
Hypothesis:     H_EDGE（diagnostic · rb/2024 · @0.1.1）
Meaning:        Negative evidence for edge screen on this scope
                ≠ delete H_MECH · ≠ Alpha Candidate · ≠ Production
```

## Diagnostics（pre-registered gates）

| Metric | Value | Gate | Pass? |
|--------|-------|------|-------|
| n_trade_log | 1303 | ≥50 | yes（sample） |
| n_round_trips | 1209 | ≥50 | yes（sample） |
| median_mfe_ticks | 3.0 | > median_mae | **no**（mae=4.0） |
| share_mfe_gt_mae | 0.363 | ≥0.55 | **no** |
| mean_net_pnl | ≈ −26.18 | >0 | **no** |
| p_one_sided（μ>0） | 1.0 | <0.05 | **no** |

```text
structure_ok = False
expectancy_ok = False
→ REVERT under §6 Fill rule
```

## Rule fidelity

```text
✓ Identity hash match @0.1.1
✓ Scope rb/2024 · docs/07 costs
✓ PnL/Sharpe not used as sole tuning objective
✓ Decision followed pre-registered A+B gates only
✓ H_MECH not re-evaluated
```

## Descriptive only（not decision）

```text
engine total_net_pnl / Sharpe / DD: reported in run_metadata · not KEEP drivers
```

## Interpretation

```text
On the forming-year continuity scope（rb/2024）:
  excursion structure favors MAE over MFE
  mean round-trip net after costs is negative
H_EDGE diagnostic screen FAILS here.

This is first-class Negative Evidence for Alpha Candidate path.
It does not reopen or erase H_MECH Verified.
```

## Non-claims

```text
❌ Alpha / Alpha Candidate
❌ “strategy worthless forever”（only this H_EDGE screen/scope）
❌ Permission to retune parameters to flip KEEP
❌ Production Bindable
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | CLOSED · REVERT |
