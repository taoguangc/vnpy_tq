# SEVF Fill / Pre-registration — STRAT_RO16_EXP003（H_EDGE）

> **Type**: Experiment Fill + Pre-registration  
> **Status**: **PRE-REGISTERED** ✓  
> **Experiment ID**: `STRAT_RO16_EXP003`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-20（`授权你决定20次`）  
> **Spec**: `SEVF_SPEC_CID_003_V0_1_1`  
> **Design**: [`STRATEGY_SEVF_DESIGN_CID_003_EXP003.md`](STRATEGY_SEVF_DESIGN_CID_003_EXP003.md)  
> **Identity**: `SIF_CID_003_V0_1_1` · `@0.1.1`  
> **Parent**: EXP002 H_MECH KEEP（mechanism only）  
> **Gate template**: CID_002 EXP013 A/B screen（method continuity）

> **Observation**: **EXECUTED** · Evaluation **REVERT** · see [`STRATEGY_SEVF_EVALUATION_CID_003_EXP003.md`](STRATEGY_SEVF_EVALUATION_CID_003_EXP003.md)

## Record

```text
================================================
STRAT_RO16_EXP003 — PRE-REGISTERED ✓ · OBSERVATION CLOSED

Hypothesis family: H_EDGE（diagnostic screen）
Scope:             rb · 2024
Observation:       EXECUTED 2026-07-23 → REVERT
Alpha Candidate:   NONE
================================================
```

## 1. Bound identity（abort on mismatch）

| Field | Value |
|-------|--------|
| `strategy_id` | `STRAT_REV_OPP16_01` |
| `version` | `0.1.1` |
| `freeze_id` | `SIF_CID_003_V0_1_1` |
| `source_hash` | `6dee22fe6c1eaf5958defa3f94db614ece5991bdbc58abc93d281bbd7b1164b5` |
| `parameter_hash` | `76b124f47414af2da2e0cdfdc6afcd5025d2cca8ae3a5583ba667cc7e1e31c57` |
| `detector_binding` | `OPP16@1.0.0` |
| `strategy_class` | `StratRevOpp1601StrategyV011` |

## 2. Primary hypothesis

**Family**: `H_EDGE`

> Under docs/07 · rb · 2024 · frozen `@0.1.1` · real costs, closed round-trips satisfy pre-registered structure（A）and expectancy-sign（B）gates below. Failure → REVERT as Negative Evidence for H_EDGE on this scope（H_MECH retained）.

**Not claimed even on KEEP**:

```text
❌ Alpha Candidate · Alpha Verified · Bindable · Production
❌ Multi-symbol / multi-year edge
```

## 3. Single variable

```text
VARIABLE: H_EDGE diagnostic gates on continuity scope rb/2024
HELD:     identity · params · costs · symbol · calendar（vs EXP002）
NO:       retune · symbol shopping · Sharpe maximize
```

## 4. Market scope package

```text
symbol:   rb.SHFE
size:     10
pricetick: 1.0
period:   2024-01-01 .. 2024-12-31
warmup:   2023-12-01
rate:     0.00003
slippage: 1.0
capital:  200000
data:     docs/07 · TQ offline · 1m · CbC · unadjusted
```

## 5. Metrics

### Primary（KEEP drivers）

| ID | Metric | Definition |
|----|--------|------------|
| A1 | `median_mfe_ticks` | median of `_trade_log.mfe_ticks` in eval window |
| A2 | `median_mae_ticks` | median of `_trade_log.mae_ticks` |
| A3 | `share_mfe_gt_mae` | fraction with `mfe_ticks > mae_ticks` |
| B1 | `mean_net_pnl` | mean closed round-trip `net_pnl` via `pair_round_trips` |
| B2 | `p_one_sided` | one-sample test H1: μ_net_pnl > 0 · α = 0.05 |

```text
min_n = 50 closed round-trips in eval window（else HOLD）
```

### Descriptive only

```text
total_net_pnl · Sharpe · max_dd · win_rate · exit_reason counts
```

## 6. Decision rule（pre-registered）

```text
ABORT: hash mismatch

HOLD:  identity OK · n < 50

KEEP（all required）:
  identity OK · n ≥ 50
  · median_mfe_ticks > median_mae_ticks
  · share_mfe_gt_mae ≥ 0.55
  · mean_net_pnl > 0
  · p_one_sided < 0.05

REVERT:
  identity OK · n ≥ 50 · KEEP conditions not all met
```

```text
KEEP ≠ Alpha Candidate
REVERT ≠ delete H_MECH · retain Negative Evidence
```

## 7. Artifacts

```text
research/output/evidence/STRAT_RO16_EXP003/
  run_metadata.json · trades_audit.csv · round_trips.csv · edge_diagnostics.json
```

## 8. Runner

`scripts/run_strat_ro16_exp003.py`（Observation authorized under Delegation-20）

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | PRE-REGISTERED under Delegation-20 |
| 2026-07-23 | Observation CLOSED · REVERT |
