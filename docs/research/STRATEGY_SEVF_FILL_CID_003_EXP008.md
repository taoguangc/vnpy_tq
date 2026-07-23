# SEVF Fill — STRAT_RO16_EXP008（H_CAPITAL_GATE multi-symbol）

> **Status**: **PRE-REGISTERED** ✓ · Observation under Delegation-50C  
> **Experiment ID**: `STRAT_RO16_EXP008`  
> **Authorization**: Delegation-50C  
> **Identity**: `SIF_CID_003_V0_2_0` · `@0.2.0`  
> **Family**: `H_CAPITAL_GATE`（≠ H_MECH）  
> **Parent**: EXP007 KEEP（i smoke）

## Hypothesis

> Under docs/07 · capital=200_000 · @0.2.0 defaults · 2024, for **each** symbol in `{rb, i, MA}`: engine path does not hit capital≤0 **OR** equity kill-switch engages before wipe.

## Universe

| Symbol | Exchange | size | pricetick |
|--------|----------|------|-----------|
| rb | SHFE | 10 | 1.0 |
| i | DCE | 100 | 0.5 |
| MA | CZCE | 10 | 1.0 |

```text
period 2024-01-01..2024-12-31 · warmup 2023-12-01
rate 0.00003 · slippage 1.0 · capital 200000
```

## Decision rule

```text
Per symbol: REVERT if capital_breach；else KEEP
Bundle: KEEP iff all three KEEP；HOLD if any HOLD；REVERT if any REVERT
PnL not a driver · H_MECH not re-tested
```

## Runner

`scripts/run_strat_ro16_exp008.py`

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | PRE-REGISTERED under Delegation-50C |
