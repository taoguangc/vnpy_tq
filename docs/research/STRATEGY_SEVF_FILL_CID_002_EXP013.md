# SEVF Fill / Pre-registration — STRAT_BS02_EXP013（H_EDGE）

> **Type**: Experiment Fill + Pre-registration（≠ Observation · ≠ Alpha admitted）  
> **Status**: **PRE-REGISTERED** ✓  
> **Experiment ID**: `STRAT_BS02_EXP013`  
> **Date**: 2026-07-23  
> **Authorization**: `Authorize SEVF Fill for STRAT_BS02_EXP013`  
> **Design**: [`STRATEGY_SEVF_DESIGN_CID_002_EXP013.md`](STRATEGY_SEVF_DESIGN_CID_002_EXP013.md)  
> **Parent design**: [`STRATEGY_ALPHA_EVIDENCE_RESEARCH_DESIGN_CID_002.md`](STRATEGY_ALPHA_EVIDENCE_RESEARCH_DESIGN_CID_002.md) · `AERD_CID_002_V0_1`  
> **Identity**: `SIF_CID_002_V0_1_1` · `@0.1.1` · surface **MECH**  
> **Observation**: **EXECUTED** · Evaluation **REVERT** · see [`STRATEGY_SEVF_EVALUATION_CID_002_EXP013.md`](STRATEGY_SEVF_EVALUATION_CID_002_EXP013.md)

## Record

```text
================================================
STRAT_BS02_EXP013 — PRE-REGISTERED ✓ · OBSERVATION CLOSED

Hypothesis family: H_EDGE（diagnostic screen）
Scope:             rb · 2024
Observation:       EXECUTED 2026-07-23 → REVERT
Alpha Candidate:   NOT CLAIMABLE
================================================
```

## 1. Bound identity（abort on mismatch）

| Field | Value |
|-------|--------|
| `strategy_id` | `STRAT_TREND_BROOKS_SCALP_02` |
| `version` | `0.1.1` |
| `freeze_id` | `SIF_CID_002_V0_1_1` |
| `source_hash` | `1877dffe2108ba4237469b52bccc589d479811d4aea82c2764900cf74ad1d4c8` |
| `parameter_hash` | `3ff061891488a9d9f5641cf147efc1e70c8d4cb8410540858d8b727bd485d1ab` |
| `detector_binding` | `BROOKS_SCALP_FP@0.1.0` |
| `consumer_surface` | `MECH`（CC-CID_002-v1） |
| `strategy_class` | `BrooksScalpPaafStrategyV011` |

```text
Binding paths（source_hash）:
  strategies/paaf/brooks_scalp_paaf_strategy.py
  strategies/paaf/brooks_scalp_paaf_strategy_v011.py
  strategies/paaf/detectors/brooks_scalp_first_pullback.py
```

## 2. Primary hypothesis（one · falsifiable）

**Family**: `H_EDGE`

> Under docs/07 · rb · 2024 · frozen `@0.1.1` · real costs/fills, closed round-trips in the evaluation window jointly satisfy **excursion structure (A)** and **positive mean net expectancy (B)** as pre-registered below.

**Null / baseline**:

```text
H0 for this EXP =
  either unfavorable/noise-like MFE–MAE structure
  or mean net_pnl ≤ 0 after costs
  （or insufficient n）
```

**Not claimed even on KEEP**:

```text
❌ Alpha Candidate / Alpha Verified
❌ Multi-symbol / multi-year robustness
❌ Production Bindable
❌ H_MECH upgrade
❌ RISK capital-gate as edge proof
```

## 3. Single variable

```text
VARIABLE: evaluate H_EDGE diagnostic gates on forming-year continuity scope
HELD:     identity hashes · detector · costs · symbol rb · calendar 2024
NO:       parameter change · symbol shopping · PnL tuning
```

## 4. Market scope package（CEMB / docs/07）

```text
symbol:   rb.SHFE
size:     10
pricetick: 1.0
period:   2024-01-01 .. 2024-12-31
warmup:   2023-12-01
rate:     0.00003
slippage: 1.0
capital:  200000
data:     TQ offline · 1m · CbC · unadjusted（docs/07 @ 1.0.0）
fill_binding: VNPY_CTA_BACKTEST_ENGINE_DEFAULTS_AT_EXP_REGISTRATION
```

```text
Scope continuity: same calendar/symbol family as EXP001/002（not re-picked by return）.
@version change 0.1.0→0.1.1 is rollover repair only（frozen hashes）.
```

## 5. Metrics

### Primary（KEEP drivers）

| ID | Metric | Definition |
|----|--------|------------|
| A1 | `median_mfe_ticks` | median of `_trade_log.mfe_ticks` in eval window |
| A2 | `median_mae_ticks` | median of `_trade_log.mae_ticks` |
| A3 | `share_mfe_gt_mae` | fraction of closed trips with `mfe_ticks > mae_ticks` |
| B1 | `mean_net_pnl` | mean of closed round-trip `net_pnl` via `pair_round_trips`（after costs） |
| B2 | `p_one_sided` | one-sample t-test H1: μ_net_pnl > 0 · α = 0.05 |

### Sample size

```text
min_n = 50 closed round-trips in eval window（else HOLD）
```

### Descriptive only（NOT KEEP/REVERT drivers）

```text
total_net_pnl · Sharpe · max_dd · win_rate · annual_return
exit_reason counts · holding_minutes distribution
```

## 6. Decision rule（pre-registered）

```text
ABORT / do not evaluate:
  source_hash or parameter_hash mismatch

HOLD:
  identity OK · n < 50

KEEP（all required）:
  identity OK
  · n ≥ 50
  · median_mfe_ticks > median_mae_ticks          （A structure）
  · share_mfe_gt_mae ≥ 0.55                       （A structure）
  · mean_net_pnl > 0                             （B expectancy sign）
  · p_one_sided < 0.05                           （B vs 0）

REVERT:
  identity OK · n ≥ 50 · and KEEP conditions not all met
```

```text
Interpretation:
  KEEP  = edge structure+sign passes THIS diagnostic screen only
  REVERT = negative evidence for H_EDGE on rb/2024（retain；≠ delete H_MECH）
  Neither outcome = Alpha Candidate
```

## 7. Dual-surface / citation rules

```text
✓ Cite as MECH · @0.1.1 · H_EDGE diagnostic
❌ Cite RISK @0.2.0 Verified as edge support
❌ Cite Context Filter KEEP as Alpha
❌ Cite annual return / Sharpe as decision
```

## 8. Artifacts（when Observation authorized）

```text
research/output/evidence/STRAT_BS02_EXP013/
  run_metadata.json
  trades_audit.csv          # trade_log join
  round_trips.csv           # pair_round_trips net_pnl
  edge_diagnostics.json     # A1–A3 · B1–B2 · n · outcome
```

## 9. Runner（prepared · not executed under Fill）

`scripts/run_strat_bs02_exp013.py`

```text
Running this script requires:
  Authorize Offline Alpha Evidence Observation for STRAT_BS02_EXP013
  （or equivalent Observation authorization）
```

## 10. Explicit non-grants

```text
❌ Observation / backtest execution
❌ Alpha Candidate / Alpha Verified
❌ Parameter change
❌ Epoch 7 / Production Bindable
```

## Next（须另授）

```text
DONE: Observation EXP013 → REVERT（negative evidence retained）
Next: EXP014 temporal H_EDGE · or pause Alpha path · or new asset
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | PRE-REGISTERED under SEVF Fill auth |
| 2026-07-23 | Observation CLOSED · REVERT |
