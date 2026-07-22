# SEVF Fill — STRAT_BS02_EXP010（H_CAPITAL_GATE multi-symbol）

> **Type**: Experiment Fill / Pre-registration  
> **Status**: **PRE-REGISTERED** ✓  
> **Experiment ID**: `STRAT_BS02_EXP010`  
> **Date**: 2026-07-22  
> **Authorization**: Delegation-100E  
> **Identity**: `SIF_CID_002_V0_2_0` · `@0.2.0`  
> **Hypothesis family**: `H_CAPITAL_GATE`（≠ H_MECH）  
> **Closes gap**: **G6**（if KEEP under pre-registered rule）

## Bound identity

| Field | Value |
|-------|--------|
| `strategy_id` | `STRAT_TREND_BROOKS_SCALP_02` |
| `version` | `0.2.0` |
| `source_hash` | `5c089251ac301cf7d5c8f72c25960d5a1e50b90907319d0e6bd54fa3880e2499` |
| `parameter_hash` | `7ff1fe9976ba809dce8f38325c33e6b7bf11a0817b2dce6d372f32258a7da346` |
| `freeze_id` | `SIF_CID_002_V0_2_0` |
| `detector_binding` | `BROOKS_SCALP_FP@0.1.0` |
| `consumer_surface` | `RISK`（CC-CID_002-v1） |

## Hypothesis

```text
H_CAPITAL_GATE（portability）:
  Under docs/07 · capital=200_000 · sizing defaults of @0.2.0 · 2024,
  for each symbol in predeclared universe {rb, i, MA}:
    engine path does not hit capital≤0 death
    OR equity kill-switch engages before wipe.
```

## Universe / protocol（predeclared · non-PnL）

| Symbol | Exchange | size | pricetick |
|--------|----------|------|-----------|
| rb | SHFE | 10 | 1.0 |
| i | DCE | 100 | 0.5 |
| MA | CZCE | 10 | 1.0 |

```text
period: 2024-01-01 .. 2024-12-31（warmup 2023-12）
rate: 0.00003 · slippage: 1.0 · capital: 200000
```

## Decision rule（pre-registered）

```text
Per symbol:
  REVERT if capital_breach（balance≤0 / non-positive balance path）
  KEEP if not capital_breach
      （kill_events≥1 OR skip_zero_lot≥0 OR closed≥0 all acceptable）

Bundle:
  KEEP if all three symbols KEEP
  HOLD if any HOLD / incomplete
  REVERT if any symbol REVERT
```

```text
PnL / Sharpe / trade count: NOT decision metrics.
H_MECH: NOT re-tested here.
```

## Explicit non-claims

```text
❌ Alpha · Bindable · Production
❌ Mechanism Verified upgrade
❌ Permission to live-trade
```

## Runner

`scripts/run_strat_bs02_exp010.py`

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Pre-registered under Delegation-100E |
