# SEVF Fill — STRAT_BS02_EXP006（cost-stress · v0.1.1）

> **Status**: **PRE-REGISTERED** ✓  
> **Experiment ID**: `STRAT_BS02_EXP006`  
> **Identity**: `SIF_CID_002_V0_1_1`  
> **Authorization**: Delegation-50C  
> **Family**: `H_ROBUST`（cost sensitivity）

## Hypothesis

> Under rb/2024 and docs/07 baseline **except** `slippage=2.0`（2× EXP005 default 1.0）, `STRAT_TREND_BROOKS_SCALP_02@0.1.1` still produces ≥1 auditable closed round-trip with exit_reason ∈ {STOP,TARGET,TIME_STOP} and matching identity hashes.

## Single variable

```text
slippage: 1.0 → 2.0
identity / period / symbol / rate / size unchanged
```

## Decision rule

Same H_MECH audit KEEP/HOLD/REVERT as EXP005（mechanism under cost stress）.  
PnL descriptive only.

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Pre-registered |
