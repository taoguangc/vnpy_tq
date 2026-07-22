# Positioning Lineage Charter — STRAT_TREND_BROOKS_SCALP_02@0.2.0

> **Type**: Repair / Positioning Charter  
> **Status**: **DESIGN FROZEN** ✓ · **Implementation DELIVERED** ✓ · Identity `SIF_CID_002_V0_2_0`  
> **Charter ID**: `PRC-BROOKS_SCALP-POSITIONING-v0.2`  
> **Date**: 2026-07-22  
> **Parent review**: [`STRATEGY_ENGINEERING_REVIEW_CID_002_POSITIONING.md`](STRATEGY_ENGINEERING_REVIEW_CID_002_POSITIONING.md)  
> **Parent identity**: `SIF_CID_002_V0_1_1`  
> **Delivery**: [`STRATEGY_POSITIONING_IMPL_DELIVERY_CID_002_V020.md`](STRATEGY_POSITIONING_IMPL_DELIVERY_CID_002_V020.md)

## Intent

Preserve morphology（`BROOKS_SCALP_FP@0.1.0`）while adding **capital-safety sizing** so the asset can be evaluated as a consumable candidate without conflating mechanism evidence with account survival.

## In scope（implemented）

```text
• risk_fraction or capped lots with predeclared tables
• equity kill-switch / capital_floor（cost-aware equity_est）
• EXP metadata: capital_assumption · sizing_mode · kill events
• new identity freeze @0.2.0（new source_hash / parameter_hash）
```

## Out of scope

```text
• detector logic changes
• exit RR / hold-time retune for PnL
• erasing @0.1.x evidence
• Bindable auto-promotion
```

## Implementation gate

```text
Authorize Implementation of Positioning Lineage 0.2.0  → GRANTED（user A）
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Charter design frozen · impl withheld |
| 2026-07-22 | Impl authorized（A）· delivered · freeze `SIF_CID_002_V0_2_0` |
