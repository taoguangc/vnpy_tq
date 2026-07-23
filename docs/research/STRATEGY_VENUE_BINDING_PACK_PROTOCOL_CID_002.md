# Venue Binding Pack Protocol — Freeze（CID_002）

> **Type**: Protocol Freeze  
> **Status**: **FROZEN** ✓ · **≠ Live trading** · **≠ Production Bindable** · **≠ Alpha**  
> **Contract ID**: `VBP-CID_002-v0.1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-50M  
> **Design**: [`STRATEGY_VENUE_BINDING_PACK_PROTOCOL_DESIGN_CID_002.md`](STRATEGY_VENUE_BINDING_PACK_PROTOCOL_DESIGN_CID_002.md)  
> **Template**: [`VBP_CID_002_venue_pack_template.json`](VBP_CID_002_venue_pack_TEMPLATE.json)  
> **Parent**: `LRC-CID_002-v0.1`

## Freeze record

```text
================================================
VBP-CID_002-v0.1

Purpose: Standardize how a live/sim venue binding
         evidence pack is declared and checked.

This freeze ships a TEMPLATE only.
No FILLED pack is claimed.
Production Bindable: STILL WITHHELD
================================================
```

## Normative rules

```text
1. Any Production Bindable petition MUST cite VBP-CID_002-v0.1
   and attach a FILLED pack whose fill_binding_id ≠
   VNPY_CTA_BACKTEST_ENGINE_DEFAULTS_AT_EXP_REGISTRATION.

2. TEMPLATE packs MUST set kind=TEMPLATE and filled=false.

3. Claiming FILLED without real venue/broker identity: FORBIDDEN.

4. Protocol changes → VBP-CID_002-v0.2（new freeze）.
```

## P5 residual update

```text
P5 LRC contract:     CLOSED（prior）
P5 VBP protocol:     CLOSED（this freeze）
P5 FILLED venue pack: OPEN（blocks Production Bindable）
```

## Explicit non-grants

```text
❌ Live / sim go-live
❌ Production Bindable
❌ Fake venue completion
❌ Alpha
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | VBP-CID_002-v0.1 FROZEN |
