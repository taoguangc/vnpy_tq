# SEVF Fill — STRAT_BS02_EXP012（H_CAPITAL_GATE temporal OOS）

> **Type**: Experiment Fill / Pre-registration  
> **Status**: **PRE-REGISTERED** ✓  
> **Experiment ID**: `STRAT_BS02_EXP012`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-50M  
> **Identity**: `SIF_CID_002_V0_2_0` · `@0.2.0`  
> **Hypothesis family**: `H_CAPITAL_GATE`（≠ H_MECH）  
> **Design**: [`STRATEGY_SEVF_DESIGN_CID_002_EXP012.md`](STRATEGY_SEVF_DESIGN_CID_002_EXP012.md)  
> **Closes residual**: **R-RISK-OOS**（if KEEP）

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
H_CAPITAL_GATE（temporal OOS）:
  Under docs/07 · capital=200_000 · @0.2.0 sizing defaults · 2025,
  for each symbol in {rb, i, MA}:
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
period: 2025-01-01 .. 2025-12-31（warmup 2024-12-01）
rate: 0.00003 · slippage: 1.0 · capital: 200000
```

## Decision rule（pre-registered）

```text
Per symbol:
  REVERT if capital_breach（balance≤0 / non-positive balance path）
  KEEP if not capital_breach

Bundle:
  KEEP if all three symbols KEEP
  HOLD if any HOLD / incomplete
  REVERT if any symbol REVERT

PnL / Sharpe / trade count: NOT decision metrics.
```

## Explicit non-claims

```text
❌ Alpha · Bindable · Production · live
❌ Mechanism Verified upgrade
```

## Runner

`scripts/run_strat_bs02_exp012.py`

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | Pre-registered under Delegation-50M |
