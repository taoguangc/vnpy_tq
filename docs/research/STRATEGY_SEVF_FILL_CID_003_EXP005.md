# SEVF Fill / Pre-registration — STRAT_RO16_EXP005（H_MECH multi-symbol）

> **Status**: **PRE-REGISTERED** ✓  
> **Experiment ID**: `STRAT_RO16_EXP005`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-50（`授权你决定50次`）  
> **Spec**: `SEVF_SPEC_CID_003_V0_1_1`  
> **Identity**: `SIF_CID_003_V0_1_1` · `@0.1.1`  
> **Family**: `H_MECH` portability

## Record

```text
================================================
STRAT_RO16_EXP005 — PRE-REGISTERED ✓

Hypothesis: H_MECH multi-symbol
Universe:   {rb, i, MA} · 2024
Identity:   @0.1.1
Alpha:      NOT in scope（path CLOSED）
================================================
```

## 1. Bound identity

Same as EXP002（`SIF_CID_003_V0_1_1` hashes · `StratRevOpp1601StrategyV011`）.

## 2. Hypothesis

> Under docs/07 and 2024-01-01..2024-12-31, for **each** symbol in `{rb, i, MA}`, `STRAT_REV_OPP16_01@0.1.1` produces ≥1 auditable closed round-trip with `exit_reason ∈ {STOP,TARGET,TIME_STOP}` and matching identity hashes.

## 3. Universe

```text
{rb, i, MA} = CAP-CTX / CID_002 continuity set
NOT selected by historical return ranking
```

| Symbol | Exchange | size | pricetick |
|--------|----------|------|-----------|
| rb | SHFE | 10 | 1.0 |
| i | DCE | 100 | 0.5 |
| MA | CZCE | 10 | 1.0 |

```text
rate 0.00003 · slippage 1.0 · capital 200000 · warmup 2023-12-01
```

## 4. Decision rule

| Outcome | Rule |
|---------|------|
| **KEEP** | all three symbols individually meet H_MECH KEEP（≥1 attributed exit · hash OK） |
| **HOLD** | no REVERT, but ≥1 symbol HOLD（0 trades / no bars） |
| **REVERT** | identity hash failure at run start |

```text
Per-symbol PnL / equity survival: descriptive only（not KEEP drivers）
i capital stress ≠ H_MECH REVERT
```

## 5. Runner

`scripts/run_strat_ro16_exp005.py`（Observation under Delegation-50）

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | PRE-REGISTERED |
| 2026-07-23 | Observation CLOSED · KEEP（all symbols） |
