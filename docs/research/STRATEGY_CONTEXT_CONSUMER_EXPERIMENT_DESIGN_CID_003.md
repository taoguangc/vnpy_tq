# Context Consumer Experiment Design — CID_003 Bindable Asset

> **Type**: Experiment Design（≠ Fill · ≠ Observation alone）  
> **Status**: **DESIGNED** ✓  
> **Design ID**: `CCED_CID_003_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-50E（`授权你决定50次`）  
> **Parents**: `BDR_CID_003_V0_1` · `CC-CID_003-v1` · CAP-CTX A1 · Decision 019  
> **Mirror**: `CCED_CID_002_V0_1`（pattern only · not continuity claim）

## Design record

```text
================================================
CCED_CID_003_V0_1

Purpose: Define how Bindable CID_003 surfaces may be consumed
         by Context under Decision 019 roles ONLY.

First EXP: CTX_CID003_EXP001（MECH · Filter F1 · rb/2024）
Alpha / trading value of Context: NOT CLAIMED
================================================
```

## 1. Why this is now possible

```text
Before BDR: no Bindable StrategyIdentity for Context to consume.
After BDR_CID_003_V0_1:
  MECH @0.1.1 and RISK @0.2.0 are Research Bindable
  → Context Consumer Experiment Design is eligible.
BDR did NOT auto-authorize Observation；Delegation-50E does for EXP001.
```

## 2. Bound strategy objects（consumer must pick one surface）

| Role in EXP | Required binding |
|-------------|------------------|
| Primary signal asset | `MECH` · `STRAT_REV_OPP16_01@0.1.1` · `SIF_CID_003_V0_1_1` |
| Optional capital wrapper | `RISK` · `@0.2.0`（**OUT** of first EXP） |
| Detector | `OPP16@1.0.0` |
| Consumer Contract | `CC-CID_003-v1` |

```text
Default first EXP: MECH surface only.
Do not mix RISK sizing / kill-switch into H_CTX_FILTER first test.
```

## 3. Allowed Context roles（Decision 019）

```text
ALLOWED:
  Filter · Risk Modifier · Monitoring · Permission

FORBIDDEN:
  Context → entry generation
  Context score → sizing alpha
  Hidden regime gate duplicating unpublished Context
```

## 4. First hypothesis family

```text
H_CTX_FILTER:
  Under declared scope and frozen MECH @0.1.1,
  applying Context Filter F1（expansion-only）changes the auditable
  trade set vs unfiltered baseline in a non-PnL-primary way
  （N0 / N1 / D）without Context writing entries.
```

```text
PnL / Sharpe MUST NOT be the primary KEEP/REVERT gate.
```

## 5. Mandatory EXP bindings

```text
• new experiment_id CTX_CID003_EXP00x（never reopen Closed RO16 / CID_002 ids）
• source_hash / parameter_hash of MECH @0.1.1
• Context A1-CTX-PS-v1.0.0 · Filter F1_EXPANSION_ONLY
• docs/07 data protocol
• pre-registered decision rule
• CC-CID_003-v1 Surface ID = MECH in metadata
• Adapter subclass only — G5 MECH binding bytes untouched
```

## 6. Explicit non-claims

```text
❌ Context → Alpha / return / drawdown improvement
❌ Production routing
❌ Mutate CID_003 MECH binding bytes to “fit” Context
❌ Continuity claim with CTX_CID002_* outcomes
```

## 7. Consumer EXP status

```text
CTX_CID003_EXP001: CLOSED · KEEP（rb/2024 · MECH · F1）
CTX_CID003_EXP002: CLOSED · KEEP（rb/2025 temporal OOS · MECH · F1）
CTX_CID003_EXP003: CLOSED · KEEP（{rb,i,MA}/2024 multi-symbol · MECH · F1）
Context×RISK composition: CCRD_CID_003_V0_1 FROZEN（Fill not authorized here）
Further Context EXPs: new experiment_id + authorization required
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | Design COMPLETE under Delegation-50E |
| 2026-07-23 | CTX_CID003_EXP001 KEEP · CLOSED |
| 2026-07-23 | CTX_CID003_EXP002 KEEP · CLOSED（Delegation-50F） |
| 2026-07-23 | CTX_CID003_EXP003 KEEP · CLOSED（Delegation-50G） |
| 2026-07-23 | Pointer · CCRD_CID_003_V0_1 FROZEN（Delegation-25I） |
