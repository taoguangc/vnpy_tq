# Positioning Charter — STRAT_REV_OPP16_01@0.2.0（design only）

> **Status**: **DESIGNED** ✓ · **NOT IMPLEMENTED**  
> **Charter ID**: `PRC_OPP16_V020_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-50B  
> **Parent review**: [`ENG_REV_CID_003_POSITIONING_V0_1`](STRATEGY_ENGINEERING_REVIEW_CID_003_POSITIONING.md)  
> **Parent identity**: `SIF_CID_003_V0_1_1`（immutable）

## Intent

```text
Capital survivability wrapper for OPP16 orchestration.
Morphology OPP16@1.0.0 unchanged.
H_MECH Verified claims stay on @0.1.1 hashes only.
```

## Parameters（design · not frozen hashes）

```text
sizing_mode:           RISK_FRACTION_OF_CAPITAL | FIXED_LOTS
risk_per_trade:        e.g. 0.005（0.5% of capital）— finalize at Identity Freeze
hard_max_lots:         e.g. 1–2 for research smoke
capital_floor_ratio:   e.g. 0.5
capital_assumption:    200_000（docs/07 research default）
```

## Non-goals

```text
❌ Improve mean_net / flip H_EDGE KEEP
❌ Change body_ratio / risk_reward morphology params
❌ Replace @0.1.1 Verified package
```

## Implementation gate

```text
Requires: Authorize Implementation of Positioning Lineage 0.2.0
Then:     new module + SIF_CID_003_V0_2_0 + SEVF Spec append + capital EXP
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | Design charter only |
