# Positioning Charter — STRAT_REV_OPP16_01@0.2.0

> **Status**: **DESIGN FROZEN** ✓ · **Implementation DELIVERED** ✓ · Identity `SIF_CID_003_V0_2_0`  
> **Charter ID**: `PRC_OPP16_V020_V0_1`  
> **Date**: 2026-07-23  
> **Parent review**: [`STRATEGY_ENGINEERING_REVIEW_CID_003_POSITIONING.md`](STRATEGY_ENGINEERING_REVIEW_CID_003_POSITIONING.md)  
> **Delivery**: [`STRATEGY_POSITIONING_IMPL_DELIVERY_CID_003_V020.md`](STRATEGY_POSITIONING_IMPL_DELIVERY_CID_003_V020.md)

## Intent

```text
Capital survivability wrapper for OPP16 orchestration.
Morphology OPP16@1.0.0 unchanged.
H_MECH Verified claims stay on @0.1.1 hashes only.
```

## Frozen parameters（Identity Freeze）

```text
sizing_mode:         RISK_FRACTION_OF_CAPITAL
risk_per_trade:      0.005
hard_max_lots:       1
capital_floor_ratio: 0.5
capital_assumption:  200_000（engine default）
```

## Implementation gate

```text
Authorize Implementation of Positioning Lineage 0.2.0  → GRANTED（user A）
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | Design charter only |
| 2026-07-23 | Impl authorized（A）· delivered · freeze `SIF_CID_003_V0_2_0` |
