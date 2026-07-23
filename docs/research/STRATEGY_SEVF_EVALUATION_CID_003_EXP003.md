# SEVF Evaluation — STRAT_RO16_EXP003

> **Status**: **CLOSED** ✓ · **REVERT**  
> **Experiment ID**: `STRAT_RO16_EXP003`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-20  
> **Artifacts**: `research/output/evidence/STRAT_RO16_EXP003/`

## Outcome

```text
Bundle outcome: REVERT
Hypothesis:     H_EDGE diagnostic · rb/2024 · @0.1.1
Meaning:        Negative evidence for edge on this scope
                H_MECH EXP002 KEEP retained · ≠ delete mechanism
                ≠ Alpha · ≠ permission to retune
```

## Diagnostics vs gates

| Metric | Value | Gate | Pass? |
|--------|-------|------|-------|
| n_trade_log / n_round_trips | 1920 / 1648 | ≥50 | yes |
| median_mfe_ticks | 3.0 | > median_mae | **no**（= 3.0） |
| median_mae_ticks | 3.0 | — | — |
| share_mfe_gt_mae | 0.406 | ≥0.55 | **no** |
| mean_net_pnl | ≈ −21.55 | >0 | **no** |
| p_one_sided (μ>0) | 1.0 | <0.05 | **no** |
| hash echo | match | — | yes |

```text
structure_ok=False · expectancy_ok=False → REVERT
```

## Non-claims

```text
❌ Alpha Candidate
❌ H_MECH invalidated
❌ Retune authorized
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | CLOSED · REVERT |
