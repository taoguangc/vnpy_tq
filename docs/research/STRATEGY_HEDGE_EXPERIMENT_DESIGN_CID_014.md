# Strategy H_EDGE Experiment Design — CID_014

> Status: **OBSERVATION COMPLETE** · Date: 2026-07-24 · Authorization: **Delegation-25BH Observation**
> Asset: `STRAT_SMC_ZSCORE_LONG_01@0.1.0` · Spec: `SMC_ZSCORE_LONG_MS_V0_1`
> Freeze: `SIF_CID_014_V0_1`
> Parent H_MECH: `STRAT_SZL_EXP001` KEEP (n=123, dual-surface ≠ Alpha)

## Experiments

| ID | Role | Symbol/Period | Outcome |
|----|------|---------------|---------|
| `STRAT_SZL_EXP002` | H_EDGE diagnostic | rb/2024 | **REVERT** |
| `STRAT_SZL_EXP003` | H_EDGE OOS | rb/2025 | **REVERT** |

## Gate (frozen)

```
ABORT: hash mismatch
HOLD:  n_gate < 50
KEEP:  n≥50 · median_mfe>median_mae · share≥0.55 · mean_net>0 · p_one<0.05
REVERT: n≥50 · KEEP conditions not all met
```

## Results

### EXP002 (rb/2024)

| Metric | Value |
|--------|-------|
| n_trade_log / n_round_trips / n_gate | 123 / 105 / **105** |
| median_mfe / median_mae | 5.0 / **8.0** |
| share_mfe_gt_mae | **0.276** (<0.55) |
| mean_net_pnl | **-45.14** |
| p_one_sided_gt0 | **0.99997** |
| Outcome | **REVERT** (structure_A FAIL + expectancy_B FAIL) |

### EXP003 (rb/2025 OOS)

| Metric | Value |
|--------|-------|
| n_trade_log / n_round_trips / n_gate | 87 / 77 / **77** |
| median_mfe / median_mae | 5.0 / 5.0 |
| share_mfe_gt_mae | **0.402** (<0.55) |
| mean_net_pnl | **-28.38** |
| p_one_sided_gt0 | **0.9987** |
| Outcome | **REVERT** (structure_A FAIL + expectancy_B FAIL) |

## Dual-surface note

H_MECH KEEP showed path existence (median_mfe 14 > mae 5, share 0.78).
H_EDGE shows that under real RR/cost/holding, edge does **not** survive — adverse MAE dominance and negative expectancy on both years.

## Scripts

- `scripts/run_strat_szl_exp002.py`
- `scripts/run_strat_szl_exp003.py`

## Evidence (local gitignored)

- `research/output/evidence/STRAT_SZL_EXP002/`
- `research/output/evidence/STRAT_SZL_EXP003/`

## Forbidden

- Retune zscore / VWAP / RR under same experiment_id
- Merge CID_013 OB story with CID_014 z-score
- Claim Alpha from H_MECH KEEP or from REVERT

## Next

`AERC_CID_014` Alpha NONE → `CPD_CID_014` Pause
（见 `STRATEGY_ALPHA_EVIDENCE_RESEARCH_CLOSURE_CID_014.md` / `STRATEGY_CAMPAIGN_PAUSE_CID_014.md`）。
