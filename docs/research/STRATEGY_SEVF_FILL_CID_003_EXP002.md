# SEVF Fill / Pre-registration — STRAT_RO16_EXP002（H_MECH @0.1.1）

> **Type**: Experiment Fill + Pre-registration（≠ Observation · ≠ Alpha）  
> **Status**: **PRE-REGISTERED** ✓  
> **Experiment ID**: `STRAT_RO16_EXP002`  
> **Date**: 2026-07-23  
> **Authorization**: `Authorize SEVF Fill / Pre-registration for STRAT_RO16_EXP002（H_MECH @0.1.1）`  
> **Spec**: [`STRATEGY_SEVF_SPECIFICATION_CID_003_V011.md`](STRATEGY_SEVF_SPECIFICATION_CID_003_V011.md) · `SEVF_SPEC_CID_003_V0_1_1`  
> **Design**: [`STRATEGY_SEVF_DESIGN_CID_003_EXP002.md`](STRATEGY_SEVF_DESIGN_CID_003_EXP002.md)  
> **Identity**: `SIF_CID_003_V0_1_1` · `STRAT_REV_OPP16_01@0.1.1`  
> **Parent evidence**: `STRAT_RO16_EXP001` HOLD（@0.1.0）· IMMUTABLE  
> **Observation**: **EXECUTED** · Evaluation **KEEP** · see [`STRATEGY_SEVF_EVALUATION_CID_003_EXP002.md`](STRATEGY_SEVF_EVALUATION_CID_003_EXP002.md)

## Record

```text
================================================
STRAT_RO16_EXP002 — PRE-REGISTERED ✓ · OBSERVATION CLOSED

Hypothesis family: H_MECH
Identity:          STRAT_REV_OPP16_01@0.1.1
Scope:             rb · 2024
Observation:       EXECUTED 2026-07-23 → KEEP（1920 attributed exits）
Alpha / Bindable:  NONE / NO
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
| `source_revision` | `7706213fe997189eeb9e1c9c6cfa9a4aecfd4f05` |

```text
Binding paths（source_hash）:
  strategies/paaf/adapters/vnpy_adapter.py
  strategies/paaf/detectors/opp16_two_bar_reversal.py
  strategies/paaf/strat_rev_opp16_01.py
  strategies/paaf/strat_rev_opp16_01_v011.py
```

## 2. Primary hypothesis

**Family**: `H_MECH`

> Under docs/07 · rb · 2024 · frozen `@0.1.1` · real costs/fills, the repaired identity produces at least one closed round-trip whose audit record attributes exit to `OPP16@1.0.0` with `exit_reason ∈ {STOP, TARGET, TIME_STOP}`, and the run echoes frozen `source_hash` / `parameter_hash`.

**Null / baseline**:

```text
Null = no auditable closed round-trip attributable to OPP16 under this scope
（not a profitability null）

Contrast（descriptive only）:
  EXP001 @0.1.0 HOLD was engineering-blocked（adapter window）；
  EXP002 tests whether repair restores observability — not EXP001 rewrite.
```

**Not claimed even on KEEP**:

```text
❌ expectancy > 0 · Alpha · Bindable · Verified
❌ H_EDGE
❌ Multi-symbol / OOS robustness
❌ “OPP16 proven”
```

## 3. Single variable

```text
VARIABLE: first Observation under repaired @0.1.1 identity
          + continuity scope rb/2024（same as EXP001）
HELD:     params · OPP16 morphology · costs · docs/07 · rb · 2024
CHANGED:  identity version / adapter included in source_manifest
NO:       parameter change · symbol shopping · PnL tuning · mutate @0.1.0
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
Scope note: rb/2024 continuity with EXP001 so the single variable is
the repair identity — not a new calendar or symbol screen.
```

## 5. Metrics

### Primary（KEEP drivers）

```text
• identity hash echo（@0.1.1 source_hash / parameter_hash）
• attributed_exits = count of closed trade_log rows in eval window
  with exit_reason in {STOP, TARGET, TIME_STOP}
• on_rollover_adjust hook present（no missing-hook WARN）
```

### Descriptive only（NOT KEEP/REVERT drivers）

```text
total_net_pnl · Sharpe · max_dd · win_rate · MFE/MAE summaries
detect/signal counts if logged
```

## 6. Decision rule（pre-registered）

```text
ABORT / do not evaluate:
  source_hash or parameter_hash mismatch vs SIF_CID_003_V0_1_1

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
KEEP ≠ rewrite of EXP001
```

## 7. Artifacts（when Observation authorized）

```text
research/output/evidence/STRAT_RO16_EXP002/
  run_metadata.json
  trades_audit.csv
```

## 8. Runner（prepared · executed under Observation auth）

`scripts/run_strat_ro16_exp002.py`

```text
DONE: Authorize Offline Observation for STRAT_RO16_EXP002 → KEEP
```

## 9. Explicit non-grants

```text
❌ Alpha / Bindable / Verified（still）
❌ Parameter change
❌ Reopen / mutate Closed EXP001
❌ CID_002 H_EDGE reopen
```

## Next（须另授）

```text
DONE: Observation → KEEP
Next: Lifecycle Review · next EXP Fill · or pause
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | PRE-REGISTERED · Observation NOT authorized |
| 2026-07-23 | Observation CLOSED · KEEP |
