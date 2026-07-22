# CID_002 Engineering Review — Rollover Integrity

> **Type**: Engineering Review（≠ Bindable · ≠ Alpha · ≠ multi-symbol）  
> **Status**: **COMPLETE** ✓  
> **Review ID**: `ENG_REV_CID_002_ROLLOVER_V0_1`  
> **Date**: 2026-07-22  
> **Authorization**: Delegation-50B  
> **Parent asset**: `STRAT_TREND_BROOKS_SCALP_02@0.1.0`（immutable）

## Findings

```text
RolloverBacktestingEngine calls strategy.on_rollover_adjust(event)
after forced flat-old / open-new when pos ≠ 0.

BrooksScalpPaafStrategy@0.1.0: hook ABSENT
→ WARN observed on EXP001/002/004
→ stop/target/entry/_entry_fill may remain on old contract scale

Legacy reference（strategies/brooks_scalp/rollover_strategy.py）:
  shifts entry_price, stop_price, target_price,
  pullback_low/high, _entry_fill by event.price_shift
```

## Decision

```text
DO NOT edit 0.1.0 binding bytes
CREATE repair lineage:
  strategy_id: STRAT_TREND_BROOKS_SCALP_02
  version:     0.1.1
  module:      strategies/paaf/brooks_scalp_paaf_strategy_v011.py
  change:      add on_rollover_adjust（same shift set as legacy）
  detector:    BROOKS_SCALP_FP@0.1.0 unchanged（morphology）

Residual uncertainty retained:
  Detector FSM pullback levels not shifted（rare cross-roll PULLBACK window）
  Documented; not blocking 0.1.1 smoke
```

## Non-goals

```text
❌ PnL improvement claim
❌ Parameter change
❌ Bindable designation
❌ Multi-symbol expansion in this review
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Engineering Review complete · repair lineage authorized under 50B |
