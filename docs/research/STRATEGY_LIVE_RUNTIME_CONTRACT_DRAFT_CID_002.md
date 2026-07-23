# Live Runtime Contract — Draft（CID_002）

> **Type**: Contract Draft（≠ Frozen · ≠ Live trading auth · ≠ Alpha）  
> **Status**: **DRAFT** ✓ · **NOT FROZEN**  
> **Draft ID**: `LRC-CID_002-v0.1-DRAFT`  
> **Date**: 2026-07-23  
> **Parent**: `DID_CID_002_V0_1` · `EI_CID_002_V0_2` · `CEMB-v1`  
> **Closes**: documentary start of P5（backtest fill ≠ live）

## Purpose

```text
Forbid silent reuse of CTA backtest fill/cost bindings as live truth.
```

## Normative intent（draft）

```text
1. Research / backtest path remains:
     CEMB-v1 · docs/07 · VNPY_CTA_BACKTEST_ENGINE_DEFAULTS_AT_EXP_REGISTRATION

2. Live / simulation brokerage path MUST declare a distinct binding:
     venue · account class · order types · fee schedule source ·
     session calendar · failover

3. Citing backtest KEEP as live performance: FORBIDDEN

4. Production Bindable requires this draft to be frozen as LRC-CID_002-v0.1
   AND matched to a real venue binding evidence pack.
```

## Non-grants

```text
❌ Live trading permission
❌ Production Bindable
❌ Freeze of this draft（needs Authorize Live Runtime Contract Freeze）
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | v0.1-DRAFT under Deploy Identity Delivery |
