# Venue Binding Pack Protocol — Design（CID_002）

> **Type**: Protocol Design（≠ Live venue · ≠ go-live · ≠ Production Bindable）  
> **Status**: **DESIGNED** ✓  
> **Design ID**: `VBP_CID_002_V0_1_DESIGN`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-50M  
> **Parents**: `LRC-CID_002-v0.1` · `EI_CID_002_V0_2` · `DID_CID_002_V0_1`

## Problem

```text
LRC Article 2 requires a venue binding evidence pack before
Production Bindable. Without a protocol, packs can be invented
ad hoc or silently filled with backtest defaults.
```

## Design goals

```text
1. Define mandatory fields matching LRC Article 2
2. Separate TEMPLATE（empty）from FILLED pack（real venue）
3. Forbid citing research CEMB fill_binding as venue truth
4. Provide machine-checkable JSON schema shape
```

## Pack kinds

| Kind | Meaning | Production Bindable |
|------|---------|---------------------|
| `TEMPLATE` | Empty schema + checklists | Does **not** satisfy P5 venue |
| `FILLED` | Real venue/broker declarations + sources | Required（still not sufficient alone） |
| `ATTESTED` | FILLED + independent attestation | Future · out of scope here |

## Mandatory fields（FILLED）

```text
venue_id
broker_legal_name
account_class          # SIM | FUNDED
order_types[]
session_calendar_ref
fee_schedule_source
slippage_policy_source
failover_policy
disconnect_policy
ei_artifact_set_id     # maps to DID/EI
lrc_contract_id        # must be LRC-CID_002-v0.1+
fill_binding_id        # MUST ≠ VNPY_CTA_BACKTEST_ENGINE_DEFAULTS_AT_EXP_REGISTRATION
declared_by
declared_at
evidence_paths[]
```

## Explicit non-goals

```text
❌ Inventing a fake broker
❌ Authorizing live orders
❌ Closing Production Bindable by template alone
```

## Next

```text
Freeze as VBP-CID_002-v0.1 + ship TEMPLATE JSON
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | Design under Delegation-50M |
