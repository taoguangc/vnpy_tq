# Component Split Design Note — CID_002

> **Type**: Design Note（≠ Implementation · ≠ Identity Freeze · ≠ Bindable）  
> **Status**: **DESIGN ONLY** ✓  
> **Note ID**: `CSD_CID_002_V0_1`  
> **Date**: 2026-07-22  
> **Authorization**: Delegation-50D  
> **Purpose**: Record preferred future shape for P2（dual-surface）without changing bytes now

## Current（accepted interim）

```text
One strategy_id · multiple versions as surfaces
  @0.1.1 = Mechanism Surface（Verified H_MECH）
  @0.2.0 = Risk Surface（capital controls）
Separated by Consumer Contract CC-CID_002-v1
```

## Preferred future（not implemented）

```text
BROOKS_SCALP_FP@…          → Strategy / Detector Component
Risk Controller@…          → Independent Component
        ↑
   composition at consumption time
```

```text
Benefits:
  • risk success cannot inflate mechanism claims
  • mechanism Verified survives risk redesign
  • matches PAAF layering（Detector ≠ Risk ≠ Execution）

Cost:
  • new identities · new freezes · migration EXPs
```

## Decision now

```text
DO NOT implement split in Delegation-50D.
KEEP versioned surfaces + CC-v1 until Bindable path requires split.
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Design note recorded |
