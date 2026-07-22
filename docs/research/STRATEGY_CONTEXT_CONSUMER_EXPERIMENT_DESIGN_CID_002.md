# Context Consumer Experiment Design — CID_002 Bindable Asset

> **Type**: Experiment Design（≠ Fill · ≠ Pre-registration · ≠ Observation · ≠ Backtest）  
> **Status**: **DESIGNED** ✓ · First Fill **CLOSED KEEP**（`CTX_CID002_EXP001`）  
> **Design ID**: `CCED_CID_002_V0_1`  
> **Date**: 2026-07-22  
> **Authorization**: Delegation-50I（scoped after Bindable grant）  
> **Parents**: `BDR_CID_002_V0_1` · `CC-CID_002-v1` · CAP-CTX-001 **CLOSED** · Decision 019  
> **RC001-B**: **PERMANENTLY CLOSED**（not reopened）

## Design record

```text
================================================
CCED_CID_002_V0_1

Purpose: Define how a Bindable CID_002 surface may be consumed
         by Context under Decision 019 roles ONLY.

Fill / Observation: CTX_CID002_EXP001 CLOSED · KEEP（H_CTX_FILTER）
Alpha / Trading value of Context: NOT CLAIMED
RC001-B: NOT REOPENED
================================================
```

## 1. Why this is now possible

```text
Before Bindable: no stable StrategyIdentity for Context to consume
                 → RC001-B class failure mode.

After BDR_CID_002_V0_1:
  MECH @0.1.1 and RISK @0.2.0 are Bindable research assets
  → Context Consumer Experiment Design is eligible.
```

## 2. Bound strategy objects（consumer must pick one surface）

| Role in EXP | Required binding |
|-------------|------------------|
| Primary signal asset | `MECH` · `STRAT_TREND_BROOKS_SCALP_02@0.1.1` · `SIF_CID_002_V0_1_1` |
| Optional capital wrapper | `RISK` · `@0.2.0` · `SIF_CID_002_V0_2_0`（if testing survival under Context filters） |
| Detector | `BROOKS_SCALP_FP@0.1.0` |
| Consumer Contract | `CC-CID_002-v1` |

```text
Default first EXP: MECH surface only.
Do not mix RISK sizing changes into the first Context-filter EXP.
```

## 3. Allowed Context roles（Decision 019）

```text
ALLOWED:
  Filter · Risk Modifier · Monitoring · Permission

FORBIDDEN:
  Context → entry generation
  Context score → sizing alpha
  Hidden regime gate duplicating unpublished Context
  Reopening RC001-B under old experiment_id
```

## 4. Proposed first hypothesis family（not filled）

```text
H_CTX_FILTER（example shape only）:
  Under declared scope and frozen MECH @0.1.1,
  applying Context as Filter changes the auditable trade set
  in a pre-registered, non-PnL-primary way
  （e.g. trade-count / attribution integrity / permission denials）
  without Context writing entries.
```

```text
PnL / Sharpe must NOT be the primary KEEP/REVERT gate
for the first Context Consumer EXP.
```

## 5. Mandatory EXP bindings（when Fill later authorized）

```text
• new experiment_id（never RC001_B_EXP001）
• strategy source_hash / parameter_hash of chosen surface
• Context artifact identity / version（from CAP-CTX closed stack）
• docs/07 data protocol
• pre-registered decision rule
• CC-CID_002-v1 Surface ID in metadata
```

## 6. Explicit non-claims（still）

```text
❌ Claim Context → Alpha / return / drawdown improvement
❌ Production routing
❌ Mutate CID_002 binding bytes to “fit” Context
```

## 7. First consumer EXP status

```text
CTX_CID002_EXP001: CLOSED · KEEP · ER PASS
Further Context EXPs: new experiment_id + authorization required
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Design COMPLETE under Delegation-50I |
| 2026-07-22 | Fill PRE-REGISTERED · `CTX_CID002_EXP001` |
| 2026-07-22 | First Observation KEEP · CLOSED |
