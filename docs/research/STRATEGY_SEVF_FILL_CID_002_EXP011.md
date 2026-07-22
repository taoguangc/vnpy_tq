# SEVF Fill — STRAT_BS02_EXP011（H_MECH temporal OOS @0.1.1）

> **Type**: Experiment Fill / Pre-registration  
> **Status**: **PRE-REGISTERED** ✓  
> **Experiment ID**: `STRAT_BS02_EXP011`  
> **Date**: 2026-07-22  
> **Authorization**: Delegation-100G（scoped wake from Epoch 5 Pause）  
> **Identity**: `SIF_CID_002_V0_1_1` · `@0.1.1`  
> **Hypothesis**: `H_MECH`（auditability · temporal OOS）  
> **Closes residual**: Verified Review **R1**（same-hash OOS）if KEEP

## Bound identity

| Field | Value |
|-------|--------|
| `strategy_id` | `STRAT_TREND_BROOKS_SCALP_02` |
| `version` | `0.1.1` |
| `source_hash` | `1877dffe2108ba4237469b52bccc589d479811d4aea82c2764900cf74ad1d4c8` |
| `parameter_hash` | `3ff061891488a9d9f5641cf147efc1e70c8d4cb8410540858d8b727bd485d1ab` |
| `freeze_id` | `SIF_CID_002_V0_1_1` |
| `detector_binding` | `BROOKS_SCALP_FP@0.1.0` |
| `consumer_surface` | `MECH` |

## Hypothesis

```text
H_MECH（temporal OOS）:
  Under docs/07 · rb · 2025 · @0.1.1 frozen hashes,
  the mechanism produces auditable exits with reasons in
  {STOP, TARGET, TIME_STOP} attributable to BROOKS_SCALP_FP.
```

## Scope

```text
symbol: rb.SHFE · size=10 · pricetick=1.0
period: 2025-01-01 .. 2025-12-31
warmup: 2024-12-01
rate: 0.00003 · slippage: 1.0 · capital: 200000
```

## Decision rule

```text
REVERT if identity hash mismatch OR missing on_rollover_adjust WARN
HOLD  if run completes but attributed exits < 1
KEEP  if attributed exits ≥ 1 with allowed reasons

PnL / Sharpe: NOT decision metrics.
```

## Non-claims

```text
❌ Alpha · Bindable · Production · E4
❌ Capital surface claims
```

## Runner

`scripts/run_strat_bs02_exp011.py`

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Pre-registered under Delegation-100G |
