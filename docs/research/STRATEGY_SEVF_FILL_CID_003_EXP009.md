# SEVF Fill — STRAT_RO16_EXP009（H_CAPITAL_GATE temporal OOS）

> **Status**: **PRE-REGISTERED** ✓ · Observation under Delegation-50C  
> **Experiment ID**: `STRAT_RO16_EXP009`  
> **Identity**: `SIF_CID_003_V0_2_0` · `@0.2.0`  
> **Family**: `H_CAPITAL_GATE`  
> **Parent**: EXP008 KEEP

## Hypothesis

> Same A/B capital gates as EXP008 on predeclared calendar **2025** for `{rb,i,MA}`.

## Scope

```text
universe {rb,i,MA} · 2025-01-01..2025-12-31 · warmup 2024-12-01
capital 200000 · rate 0.00003 · slippage 1.0 · @0.2.0 defaults
```

## Decision rule

Identical to EXP008（per-symbol no capital≤0 → KEEP；bundle all KEEP）.

## Runner

`scripts/run_strat_ro16_exp009.py`

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | PRE-REGISTERED under Delegation-50C |
