# SEVF Fill / Pre-registration — STRAT_BS02_EXP014（H_EDGE OOS）

> **Type**: Experiment Fill + Pre-registration（≠ Observation · ≠ Alpha admitted）  
> **Status**: **PRE-REGISTERED** ✓  
> **Experiment ID**: `STRAT_BS02_EXP014`  
> **Date**: 2026-07-23  
> **Authorization**: `Authorize SEVF Fill for STRAT_BS02_EXP014`  
> **Design**: [`STRATEGY_SEVF_DESIGN_CID_002_EXP014.md`](STRATEGY_SEVF_DESIGN_CID_002_EXP014.md)  
> **Parent design**: `AERD_CID_002_V0_1`  
> **Prior Closed**: `STRAT_BS02_EXP013` · H_EDGE rb/2024 · **REVERT**（immutable）  
> **Identity**: `SIF_CID_002_V0_1_1` · `@0.1.1` · surface **MECH**  
> **Observation**: **EXECUTED** · Evaluation **REVERT** · see [`STRATEGY_SEVF_EVALUATION_CID_002_EXP014.md`](STRATEGY_SEVF_EVALUATION_CID_002_EXP014.md)

## Record

```text
================================================
STRAT_BS02_EXP014 — PRE-REGISTERED ✓ · OBSERVATION CLOSED

Hypothesis family: H_EDGE_OOS
Scope:             rb · 2025
Observation:       EXECUTED 2026-07-23 → REVERT
Prior EXP013:      REVERT retained
Alpha Candidate:   NOT ESTABLISHED
================================================
```

## Status alignment（binding context）

```text
CID_002
  H_MECH:            VERIFIED（unchanged）
  H_EDGE rb/2024:    REVERT（EXP013）
  Alpha Candidate:   NOT ESTABLISHED
  Alpha:             NONE
  Bindable/Production: unchanged（Research Bindable retained · Production WITHHELD）
```

## 1. Bound identity（abort on mismatch · same as EXP013）

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

## 2. Primary hypothesis

**Family**: `H_EDGE` / label `H_EDGE_OOS`

> Under docs/07 · rb · **2025** · frozen `@0.1.1` · real costs/fills, closed round-trips satisfy the **same** pre-registered gates (A) excursion structure and (B) positive mean net expectancy as EXP013.

**Null**:

```text
Same H0 structure as EXP013 on the OOS year.
```

**Not claimed even on KEEP**:

```text
❌ Alpha / Alpha Candidate stamp（only “reconsideration allowed”）
❌ Rescue or deletion of EXP013 REVERT
❌ Multi-symbol robustness
❌ Production / CSD
```

## 3. Single variable

```text
VARIABLE: calendar year 2025（OOS vs EXP013/2024）
HELD:     all identity · detector · entry/stop/target/params · costs ·
          symbol rb · metric definitions · thresholds
FORBIDDEN: any change listed in Design §Forbidden
```

## 4. Market scope

```text
symbol:   rb.SHFE
size:     10
pricetick: 1.0
period:   2025-01-01 .. 2025-12-31
warmup:   2024-12-01
rate:     0.00003
slippage: 1.0
capital:  200000
data:     docs/07 @ 1.0.0
fill_binding: VNPY_CTA_BACKTEST_ENGINE_DEFAULTS_AT_EXP_REGISTRATION
```

## 5. Metrics（identical to EXP013 · frozen）

| ID | Metric | Gate |
|----|--------|------|
| A1/A2 | median_mfe_ticks > median_mae_ticks | structure |
| A3 | share_mfe_gt_mae ≥ 0.55 | structure |
| B1 | mean_net_pnl > 0 | expectancy sign |
| B2 | one-sided t-test μ>0 · p < 0.05 | expectancy |
| n | min_n = 50 | else HOLD |

Descriptive only（not drivers）: total_net_pnl · Sharpe · max_dd · win_rate · annual_return.

## 6. Decision rule（identical to EXP013）

```text
ABORT: hash mismatch
HOLD:  n < 50
KEEP:  n≥50 ∧ A structure ∧ B expectancy（all）
REVERT: n≥50 ∧ not KEEP
```

## 7. Interpretation map（pre-declared）

| Outcome | Alpha Evidence meaning |
|---------|------------------------|
| REVERT | H_EDGE rejected on 2025 OOS · with EXP013 → temporal negative chain |
| KEEP | OOS screen PASS · Alpha Candidate reconsideration allowed · still NONE until multi-gate |
| HOLD | incomplete |

```text
Post-EXP014 decision fork（requires new auth）:
  1) Close CID_002 Alpha Research
  2) New strategy asset
  3) Portfolio Research（only if edge path warrants）
NOT: Production · CSD
```

## 8. Runner（prepared · not executed）

`scripts/run_strat_bs02_exp014.py`

## 9. Explicit non-grants

```text
❌ Observation / backtest under this Fill
❌ Metric/parameter changes
❌ Alpha Candidate grant
❌ Production / Epoch 7 / CSD
```

## Next（须另授）

```text
DONE: Observation EXP014 → REVERT
Temporal H_EDGE chain（rb 2024+2025）: both REVERT
Fork: Close Alpha Research · or New Asset Design
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | PRE-REGISTERED · OOS completeness framing |
| 2026-07-23 | Observation CLOSED · REVERT |
