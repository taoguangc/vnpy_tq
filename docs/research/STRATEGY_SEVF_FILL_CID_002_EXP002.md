# SEVF Fill / Pre-registration — STRAT_BS02_EXP002（H_NULL）

> **Type**: Experiment Fill + Pre-registration  
> **Status**: **PRE-REGISTERED** ✓  
> **Experiment ID**: `STRAT_BS02_EXP002`  
> **Spec**: `SEVF_SPEC_CID_002_V0_1`  
> **Identity**: `SIF_CID_002_V0_1`  
> **Date**: 2026-07-22  
> **Authorization**: Fifty-round delegated decisions 2–6  
> **Prior**: `STRAT_BS02_EXP001` Closed KEEP（H_MECH）immutable

## Record

```text
================================================
STRAT_BS02_EXP002 — PRE-REGISTERED ✓

Hypothesis family: H_NULL
Scope:             rb · 2024-01-01..2024-12-31（same as EXP001）
Variable:          hypothesis class only（H_MECH → H_NULL）；identity/scope fixed
================================================
```

## 1. Identity binding

Identical to EXP001 / `SIF_CID_002_V0_1`（abort on hash mismatch）.

## 2. Primary hypothesis

**Family**: `H_NULL`

> Under the declared scope and frozen costs/fills, the mean round-trip **net_pnl** of `STRAT_TREND_BROOKS_SCALP_02@0.1.0` is **not distinguishable from zero**（two-sided one-sample test vs μ=0）.

```text
Not claimed: Alpha · profitable · Bindable
H_MECH remains independently retained from EXP001
```

## 3. Market scope

Same package as EXP001（continuity · not re-selected by PnL）:

```text
symbols: rb
period:  2024-01-01 .. 2024-12-31
warmup:  2023-12-01
data:    docs/07 v1.0.0
```

## 4. Metrics

**Primary**: mean `net_pnl` per closed round-trip in eval window（after costs）.

**Test**（pre-registered）:

```text
H0: μ_net_pnl = 0
two-sided one-sample t-test
α = 0.05
min_n = 30（else HOLD）
```

**Mandatory audit**: trade count · exit_reason · identity hashes（same as Spec §7.1）.

**Descriptive only**: total net PnL · Sharpe · max DD · win rate（not KEEP drivers）.

## 5. Decision rule

| Outcome | Rule |
|---------|------|
| **KEEP** | identity OK · n≥30 · p≥0.05（fail to reject μ=0）→ retain H_NULL |
| **HOLD** | identity OK · n&lt;30 or test inapplicable |
| **REVERT** | identity mismatch **or** n≥30 ∧ p&lt;0.05（μ distinguishable from 0） |

```text
REVERT of H_NULL ≠ delete H_MECH
REVERT of H_NULL ≠ Alpha proven（distinguishable can be negative）
KEEP of H_NULL ≠ Bindable
```

## 6. Outputs

```text
research/output/evidence/STRAT_BS02_EXP002/
  trades_roundtrips.csv
  run_metadata.json
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Pre-registered under Delegation-50 |
