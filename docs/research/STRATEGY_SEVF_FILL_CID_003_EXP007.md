# SEVF Fill / Pre-registration — STRAT_RO16_EXP007（H_CAPITAL_GATE）

> **Type**: Experiment Fill + Pre-registration（≠ Observation · ≠ Alpha）  
> **Status**: **PRE-REGISTERED** ✓  
> **Experiment ID**: `STRAT_RO16_EXP007`  
> **Date**: 2026-07-23  
> **Authorization**: `Authorize SEVF Fill for STRAT_RO16_EXP007（H_CAPITAL_GATE · i/2024 @0.2.0）`  
> **Spec**: [`STRATEGY_SEVF_SPECIFICATION_CID_003_V020.md`](STRATEGY_SEVF_SPECIFICATION_CID_003_V020.md) · `SEVF_SPEC_CID_003_V0_2_0`  
> **Design**: [`STRATEGY_SEVF_DESIGN_CID_003_EXP007.md`](STRATEGY_SEVF_DESIGN_CID_003_EXP007.md)  
> **Identity**: `SIF_CID_003_V0_2_0` · `@0.2.0`  
> **Contrast parent**: EXP005 `i` @0.1.1 capital breach（descriptive）  
> **Observation**: **NOT AUTHORIZED** by this Fill

## Record

```text
================================================
STRAT_RO16_EXP007 — PRE-REGISTERED ✓

Hypothesis family: H_CAPITAL_GATE
Surface:           RISK @0.2.0
Scope:             i · 2024
Observation:       NOT AUTHORIZED
Alpha / Bindable:  NONE / NO
MECH @0.1.1:       NOT re-tested
================================================
```

## 1. Bound identity（abort on mismatch）

| Field | Value |
|-------|--------|
| `strategy_id` | `STRAT_REV_OPP16_01` |
| `version` | `0.2.0` |
| `freeze_id` | `SIF_CID_003_V0_2_0` |
| `source_hash` | `0e796e226b5906f22bdc4ce622f522788985a05525d2f65ae05e40fb2c474012` |
| `parameter_hash` | `fce3f995d1421ada2152e591362700ed2a24d93c7ff3259394261f254cd7aa22` |
| `detector_binding` | `OPP16@1.0.0` |
| `strategy_class` | `StratRevOpp1601StrategyV020` |
| `consumer_surface` | `RISK` |

```text
Binding paths（source_hash）:
  strategies/paaf/adapters/vnpy_adapter.py
  strategies/paaf/detectors/opp16_two_bar_reversal.py
  strategies/paaf/strat_rev_opp16_01.py
  strategies/paaf/strat_rev_opp16_01_v011.py
  strategies/paaf/strat_rev_opp16_01_v020.py
```

## 2. Primary hypothesis

**Family**: `H_CAPITAL_GATE`

> Under docs/07 · symbol `i` · 2024 · capital=200_000 · frozen `@0.2.0` sizing defaults（`RISK_FRACTION_OF_CAPITAL` · `risk_per_trade=0.005` · `hard_max_lots=1` · `capital_floor_ratio=0.5`）, the engine capital path does **not** hit `balance≤0` death, **or** the equity kill-switch engages before wipe. Hash echo required.

**Null / baseline**:

```text
Null = capital≤0 death path under these controls（same class as EXP005 @0.1.1 i breach）
（not a profitability null · not H_MECH null）
```

**Not claimed even on KEEP**:

```text
❌ Alpha · Bindable · Production
❌ H_MECH upgrade / rewrite
❌ Multi-symbol capital portability
❌ Permission to live-trade
```

## 3. Single variable

```text
VARIABLE: first H_CAPITAL_GATE Observation on stress symbol i under @0.2.0
HELD:     identity hashes · morphology · docs/07 · calendar 2024 · capital=200k
CHANGED:  positioning controls vs @0.1.1 fixed_size=1（lineage · not retune）
NO:       body_ratio / RR search · Alpha reopen
```

## 4. Market scope package

```text
symbol:   i.DCE
size:     100
pricetick: 0.5
period:   2024-01-01 .. 2024-12-31
warmup:   2023-12-01
rate:     0.00003
slippage: 1.0
capital:  200000
data:     docs/07 · TQ offline · 1m · CbC · unadjusted
fill_binding: VNPY_CTA_BACKTEST_ENGINE_DEFAULTS_AT_EXP_REGISTRATION
cost_binding: PROJECT_FROZEN_DATA_PROTOCOL
```

```text
Scope note: i chosen because EXP005 demonstrated capital breach under @0.1.1
fixed_size=1 — continuity stress symbol, not return-ranked.
```

## 5. Metrics

### Primary（KEEP / REVERT drivers）

| ID | Metric | Definition |
|----|--------|------------|
| C1 | `capital_breach` | `end_balance ≤ 0` OR any `balance ≤ 0` in daily path |
| C2 | `kill_events` / `entries_halted` | strategy equity kill-switch counters |
| C3 | hash echo | `source_hash` / `parameter_hash` match freeze |

### Descriptive only

```text
closed_trade_count · skip_zero_lot · equity_est_end · total_net_pnl · Sharpe
exit_reason mix（including KILL_SWITCH）
```

## 6. Decision rule（pre-registered）

```text
ABORT / do not evaluate:
  source_hash or parameter_hash mismatch

REVERT:
  identity OK · capital_breach == True
  （engine capital≤0 death path under @0.2.0 controls）

KEEP:
  identity OK · capital_breach == False
  （kill_events≥1 OR entries_halted OR skip_zero_lot≥0 OR closed≥0
   all acceptable as long as no capital≤0）

HOLD:
  identity OK · inconclusive harness（no balance series / incomplete run）
```

```text
PnL / Sharpe / trade count: NOT decision metrics.
KEEP ≠ Alpha · ≠ Bindable · ≠ H_MECH Verified upgrade
REVERT ≠ morphology failure（capital engineering only）
```

## 7. Artifacts（when Observation authorized）

```text
research/output/evidence/STRAT_RO16_EXP007/
  run_metadata.json
  trades.csv
  capital_gate_log.json
```

## 8. Runner（prepared · not executed）

`scripts/run_strat_ro16_exp007.py`

```text
Requires separate:
  Authorize Offline Observation for STRAT_RO16_EXP007
```

## 9. Explicit non-grants

```text
❌ Observation / backtest under this Fill
❌ Alpha / Bindable / Production
❌ Parameter change
❌ Reopen H_EDGE · mutate @0.1.1
```

## Next（须另授）

```text
Authorize Offline Observation for STRAT_RO16_EXP007
  — OR — Pause CID_003
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | PRE-REGISTERED · Observation NOT authorized |
