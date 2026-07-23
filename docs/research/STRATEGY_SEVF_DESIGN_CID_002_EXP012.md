# SEVF Design — STRAT_BS02_EXP012（H_CAPITAL_GATE temporal OOS）

> **Type**: Experiment Design  
> **Status**: **DESIGNED** ✓  
> **Experiment ID**: `STRAT_BS02_EXP012`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-50M  
> **Identity**: `SIF_CID_002_V0_2_0` · `@0.2.0` · surface `RISK`  
> **Closes residual**: `R-RISK-OOS`（if KEEP under pre-registered non-PnL rule）

## Single hypothesis

```text
H_CAPITAL_GATE（temporal OOS）:
  Same frozen @0.2.0 hashes and capital controls as EXP010,
  on calendar year 2025（OOS vs EXP008–010 2024）,
  for predeclared universe {rb, i, MA}:
    no capital≤0 death path（or kill engages before wipe）.
```

## Single variable

```text
VARIABLE = evaluation calendar year（2025 vs 2024）
HELD CONSTANT = identity hashes · universe · capital · sizing · cost model · decision rule
```

## Explicit non-goals

```text
❌ H_MECH / PnL / Sharpe gates
❌ Production Bindable / Alpha
❌ Parameter change
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | Designed under Delegation-50M |
