# Evidence Evaluation — STRAT_BS02_EXP001

> **Type**: SEVF Evidence Evaluation（Closed Observation）  
> **Status**: **CLOSED** ✓  
> **Experiment ID**: `STRAT_BS02_EXP001`  
> **Date**: 2026-07-22  
> **Authorization**: `Authorize SEVF Observation for STRAT_BS02_EXP001`  
> **Pre-registration**: [`STRATEGY_SEVF_FILL_CID_002_EXP001.md`](STRATEGY_SEVF_FILL_CID_002_EXP001.md)  
> **Identity**: [`SIF_CID_002_V0_1`](STRATEGY_IDENTITY_FREEZE_CID_002.md)  
> **Artifacts**: `research/output/evidence/STRAT_BS02_EXP001/`

## Evaluation record

```text
================================================
STRAT_BS02_EXP001 — CLOSED

Hypothesis family: H_MECH
Outcome:           KEEP ✓
Lifecycle:         Candidate → Testing（mechanism evidence only）
Bindable:          NO
Verified:          NO
Alpha claim:       NONE
================================================
```

## 1. Identity gate（pre-run）

| Check | Result |
|-------|--------|
| `source_hash` match freeze | **PASS** `3ba12893…` |
| `parameter_hash` match freeze | **PASS** `3ff06189…` |
| Abort on mismatch | not triggered |

## 2. Scope executed

```text
symbol:        rb
period:        2024-01-01 .. 2024-12-31（eval window）
warmup:        2023-12-01
bars:          89550
data:          docs/07_DATA_SPEC.md v1.0.0（TQ offline · 1m · CbC · unadjusted）
cost:          rate=0.00003 · slippage=1.0 · size=10 · pricetick=1.0
fill:          VNPY CTA backtest engine defaults
runner:        scripts/run_strat_bs02_exp001.py
```

## 3. Audit results（KEEP drivers）

| Metric | Value |
|--------|-------|
| `closed_trade_count`（eval window） | **1303** |
| `exit_reason` STOP | 333 |
| `exit_reason` TARGET | 312 |
| `exit_reason` TIME_STOP | 658 |
| detector attribution | **100%** `BROOKS_SCALP_FP@0.1.0`（exclusive strategy binding stamp） |
| identity echo in CSV | strategy_id / version / hashes present |

Auditable CSV: `research/output/evidence/STRAT_BS02_EXP001/trades_audit.csv`

## 4. Decision vs pre-registered rule

| Outcome | Pre-registered rule | Applied |
|---------|---------------------|---------|
| **KEEP** | auditable output ∧ trades≥1 ∧ detector attribution ∧ hash match ∧ exit∈{STOP,TARGET,TIME_STOP} | **MET** |

**Outcome: KEEP**

Supports retaining the **H_MECH** hypothesis in the declared rb/2024 scope:
the frozen identity produces auditable signal→entry→exit events attributable
to `BROOKS_SCALP_FP@0.1.0`.

## 5. Descriptive engine stats（NOT KEEP drivers）

```text
engine_total_trade_count: 2645
engine_total_net_pnl:     -34711.28（descriptive only）
engine_sharpe_ratio:      -10.38（descriptive only）
engine_max_ddpercent:     -17.37（descriptive only）
```

```text
Negative descriptive PnL
        ≠
REVERT under H_MECH
        ≠
Alpha falsification EXP（that would be H_NULL with its own pre-reg）
```

## 6. Uncertainty

```text
• Single-symbol · in-sample · mechanism only
• Detector attribution stamped from exclusive orchestrator binding
  （strategy constructs only BROOKS_SCALP_FP）
• RolloverBacktestingEngine warned: strategy lacks on_rollover_adjust
  → stop/target levels may not translate across contract switches
  （document for future EXP; not a hash/audit REVERT for H_MECH）
• KEEP ≠ Bindable ≠ Verified ≠ Production ≠ Alpha
```

## 7. Lifecycle consequence

```text
Evidence supports Testing-state mechanism claim under declared scope.
Does NOT promote to Verified or Bindable.
Next evidence steps require new EXP IDs（e.g. H_NULL · OOS · multi-symbol）.
```

## 8. Hard guarantees

```text
✓ Pre-registered rules applied without post-hoc metric shopping
✓ No parameter search
✓ No zero-cost / adjusted-price substitute
✓ No RC001-B / Context Consumer claim
✓ No Alpha claim
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Observation executed · Closed · Outcome **KEEP**（H_MECH） |
