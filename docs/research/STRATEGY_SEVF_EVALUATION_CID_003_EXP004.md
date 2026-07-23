# SEVF Evaluation — STRAT_RO16_EXP004

> **Status**: **CLOSED** ✓ · **REVERT**  
> **Experiment ID**: `STRAT_RO16_EXP004`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-20  
> **Artifacts**: `research/output/evidence/STRAT_RO16_EXP004/`

## Outcome

```text
Bundle outcome: REVERT
Hypothesis:     H_EDGE temporal OOS · rb/2025 · @0.1.1
Meaning:        Negative evidence continues on later calendar
                Temporal H_EDGE chain: EXP003+EXP004 both REVERT
```

## Diagnostics vs gates

| Metric | Value | Gate | Pass? |
|--------|-------|------|-------|
| n_trade_log / n_round_trips | 2033 / 1826 | ≥50 | yes |
| median_mfe / median_mae | 2.0 / 2.0 | mfe > mae | **no** |
| share_mfe_gt_mae | 0.420 | ≥0.55 | **no** |
| mean_net_pnl | ≈ −20.94 | >0 | **no** |
| p_one_sided (μ>0) | 1.0 | <0.05 | **no** |
| hash echo | match | — | yes |

## Non-claims

```text
❌ Alpha Candidate
❌ Permission to retune
❌ H_MECH deleted（EXP002 KEEP stands）
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | CLOSED · REVERT |
