# SEVF Fill / Pre-registration — STRAT_RO16_EXP001（H_MECH）

> **Type**: Experiment Fill + Pre-registration（≠ Observation · ≠ Alpha）  
> **Status**: **PRE-REGISTERED** ✓  
> **Experiment ID**: `STRAT_RO16_EXP001`  
> **Date**: 2026-07-23  
> **Authorization**: `Authorize SEVF Fill / Pre-registration for STRAT_RO16_EXP001（H_MECH）`  
> **Spec**: [`STRATEGY_SEVF_SPECIFICATION_CID_003.md`](STRATEGY_SEVF_SPECIFICATION_CID_003.md) · `SEVF_SPEC_CID_003_V0_1`  
> **Design**: [`STRATEGY_SEVF_DESIGN_CID_003_EXP001.md`](STRATEGY_SEVF_DESIGN_CID_003_EXP001.md)  
> **Identity**: `SIF_CID_003_V0_1` · `STRAT_REV_OPP16_01@0.1.0`  
> **Observation**: **EXECUTED** · Evaluation **HOLD** · see [`STRATEGY_SEVF_EVALUATION_CID_003_EXP001.md`](STRATEGY_SEVF_EVALUATION_CID_003_EXP001.md)

## Record

```text
================================================
STRAT_RO16_EXP001 — PRE-REGISTERED ✓ · OBSERVATION CLOSED

Hypothesis family: H_MECH
Scope:             rb · 2024
Observation:       EXECUTED 2026-07-23 → HOLD（0 auditable exits）
Alpha / Bindable:  NONE / NO
================================================
```

## 1. Bound identity（abort on mismatch）

| Field | Value |
|-------|--------|
| `strategy_id` | `STRAT_REV_OPP16_01` |
| `version` | `0.1.0` |
| `freeze_id` | `SIF_CID_003_V0_1` |
| `source_hash` | `f87cdcc43e74060f23c08fa06364f0be90c538a1576566a0034ba096f0adc220` |
| `parameter_hash` | `76b124f47414af2da2e0cdfdc6afcd5025d2cca8ae3a5583ba667cc7e1e31c57` |
| `detector_binding` | `OPP16@1.0.0` |
| `strategy_class` | `StratRevOpp1601Strategy` |

```text
Binding paths（source_hash）:
  strategies/paaf/detectors/opp16_two_bar_reversal.py
  strategies/paaf/strat_rev_opp16_01.py
```

## 2. Primary hypothesis

**Family**: `H_MECH`

> Under docs/07 · rb · 2024 · frozen `@0.1.0` · real costs/fills, the frozen identity produces at least one closed round-trip whose audit record attributes exit to `OPP16@1.0.0` with `exit_reason ∈ {STOP, TARGET, TIME_STOP}`, and the run echoes frozen `source_hash` / `parameter_hash`.

**Null / baseline**:

```text
Null = no auditable closed round-trip attributable to OPP16 under this scope
（not a profitability null）
```

**Not claimed even on KEEP**:

```text
❌ expectancy > 0 · Alpha · Bindable · Verified
❌ H_EDGE
❌ Multi-symbol / OOS robustness
```

## 3. Single variable

```text
VARIABLE_0: first Observation under frozen identity + declared scope
HELD:       hashes · OPP16 · params · costs · rb · 2024
NO:         parameter change · symbol shopping · PnL tuning
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
data:     docs/07 @ 1.0.0 · TQ offline · 1m · CbC · unadjusted
fill_binding: VNPY_CTA_BACKTEST_ENGINE_DEFAULTS_AT_EXP_REGISTRATION
cost_binding: PROJECT_FROZEN_DATA_PROTOCOL
```

```text
Scope note: rb/2024 chosen for continuity with prior research calendar,
not because OPP16 was screened for profit on this year.
```

## 5. Metrics

### Primary（KEEP drivers）

```text
• identity hash echo
• attributed_exits = count of closed trade_log rows in eval window
  with exit_reason in {STOP, TARGET, TIME_STOP}
• on_rollover_adjust hook present（no missing-hook WARN）
```

### Descriptive only（NOT KEEP/REVERT drivers）

```text
total_net_pnl · Sharpe · max_dd · win_rate · MFE/MAE summaries
```

## 6. Decision rule（pre-registered）

```text
ABORT / do not evaluate:
  source_hash or parameter_hash mismatch

REVERT:
  identity OK but missing on_rollover_adjust capability WARN
  （engine logs “未实现 on_rollover_adjust”）

HOLD:
  identity OK · attributed_exits < 1

KEEP:
  identity OK · no missing-hook WARN · attributed_exits ≥ 1
```

```text
PnL / Sharpe / annual return: NOT decision metrics.
KEEP ≠ Alpha · ≠ Bindable · ≠ H_EDGE
```

## 7. Artifacts（when Observation authorized）

```text
research/output/evidence/STRAT_RO16_EXP001/
  run_metadata.json
  trades_audit.csv
```

## 8. Runner（prepared · not executed）

`scripts/run_strat_ro16_exp001.py`

```text
Requires separate:
  Authorize Offline Observation for STRAT_RO16_EXP001
  （or equivalent Observation authorization）
```

## 9. Explicit non-grants

```text
❌ Observation / backtest under this Fill
❌ Alpha / Bindable / Verified
❌ Parameter change
❌ CID_002 reopen
```

## Next（须另授）

```text
DONE: Observation → HOLD（0 trades / 0 attributed exits）
Next: Engineering Review · or EXP002 alternate scope · or pause
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | PRE-REGISTERED |
| 2026-07-23 | Observation CLOSED · HOLD |
