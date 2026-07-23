# VMP Live Ops Checklist — Freeze（CID_002）

> **Type**: Live-ops checklist Freeze（extends VMP · ≠ Production Bindable）  
> **Status**: **FROZEN** ✓  
> **Checklist ID**: `VMP_LIVE_CID_002_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-50N  
> **Parent**: `VMP_CID_002_V0_1` · `LEP-CID_002-v0.1` · `LRC-CID_002-v0.1`

## Purpose

```text
Close documentary half of R-VMP-live:
  name what must be declared for live drift / restart / session faults
  before Production Bindable can even be petitioned.
```

## Mandatory checklist fields

| Field | Meaning |
|-------|---------|
| `session_calendar_ref` | Trading session / holiday calendar source |
| `restart_policy` | Cold/warm restart · state reload rules |
| `drift_detection` | How clock/data/identity drift is detected |
| `failover_policy` | Broker/API failover |
| `disconnect_policy` | Disconnect / reconnect / flatten rules |
| `identity_pin_ref` | EI / DID artifact set citation |
| `lrc_contract_id` | Must be `LRC-CID_002-v0.1`+ |
| `vbp_pack_ref` | Must cite FILLED VBP pack path |
| `cxsd_contract_id` | Must be `CXSD-CID_002-v0.1`+ |
| `declared_by` / `declared_at` | Attribution |

## Rules

```text
1. Incomplete checklist → LEP gate FAIL.
2. Checklist alone ≠ live evidence pack.
3. Research Closed EXPs remain on VMP_CID_002_V0_1 research assumptions.
```

## Explicit non-grants

```text
❌ Live ops attestation completed
❌ Production Bindable
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | VMP_LIVE_CID_002_V0_1 FROZEN |
