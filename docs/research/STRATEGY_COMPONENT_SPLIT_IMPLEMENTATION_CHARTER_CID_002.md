# Component Split Implementation Charter — CID_002

> **Type**: Implementation Charter（≠ Implementation · ≠ Identity Freeze · ≠ Bindable）  
> **Status**: **CHARTERED** ✓ · **Implementation NOT AUTHORIZED**  
> **Charter ID**: `CSDIC_CID_002_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-50O  
> **Parent design**: [`STRATEGY_COMPONENT_SPLIT_DESIGN_NOTE_CID_002.md`](STRATEGY_COMPONENT_SPLIT_DESIGN_NOTE_CID_002.md) · `CSD_CID_002_V0_1`  
> **Also cite**: `CC-CID_002-v1` · `ACL_CID_002_V0_1` · `LEP-CID_002-v0.1`

## Purpose

```text
Freeze the rules under which a future Component Split MAY be
implemented — without implementing it now.
```

## Current interim（retained）

```text
One strategy_id · versioned surfaces:
  @0.1.1 MECH · @0.2.0 RISK
Consumer Contract CC-CID_002-v1 remains binding.
Closed EXP hashes remain immutable.
```

## Target shape（future · not built）

```text
Detector / Mechanism component  →  independent identity + freeze
Risk Controller component       →  independent identity + freeze
Composition                    →  at harness / live orchestrator only
```

## Charter rules（normative）

```text
1. Implementation REQUIRES a separate explicit user authorization
   named “Authorize CSD Implementation” — this charter is insufficient.

2. MUST NOT mutate Closed EXP binding bytes or rewrite Verified stamps.
   New components get new strategy_id / version / freeze_id.

3. Dual-surface citation（CC-CID_002-v1）MUST survive the split:
   RISK KEEP MUST NOT inflate MECH / Alpha claims.

4. Migration MUST ship:
   · new identity freezes
   · ACL / LEP matrix updates
   · at least one non-PnL IVS per surface after split
   · PBDR re-review（expected still WITHHOLD until residuals clear）

5. Prefer composition-at-consumption over silent subclass coupling.
```

## Out of scope（this charter）

```text
❌ Writing split modules now
❌ Production Bindable
❌ Alpha / E4 / live
❌ Parameter / PnL work
```

## Residual effect

```text
R-CSD: OPEN（implementation）· PARTIAL（charter CLOSED）
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | CSDIC_CID_002_V0_1 CHARTERED · impl deferred |
