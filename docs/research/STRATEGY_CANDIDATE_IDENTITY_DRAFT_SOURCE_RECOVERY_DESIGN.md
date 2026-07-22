# Candidate Identity Draft and Source Recovery — Design

> **Type**: Protocol Design（≠ Identity Freeze · ≠ Working-tree Recovery · ≠ Implementation · ≠ Backtest）  
> **Status**: **CONFIRMED** ✓ · authority frozen as `SCIDR-v1`  
> **Version**: 0.1  
> **Date**: 2026-07-22  
> **Authorization**: Five-round delegated decision — decisions 1–3  
> **Inputs**: `SAC-v1` / `SEVF-v1` / `SCAP-v1` — **FROZEN**  
> **Admitted source**: [`STRATEGY_CANDIDATE_ADMISSION_REVIEW.md`](STRATEGY_CANDIDATE_ADMISSION_REVIEW.md)

## Purpose

Govern how an admitted **Candidate Source** may receive a **Candidate Identity Draft**, and how source recovery is classified — without implying StrategyIdentity Freeze, code restoration into the working tree, or experimental authorization.

```text
Candidate Source
  → Candidate Identity Draft（incomplete SAC-v1 package）
  →（future）Identity Freeze · Testing
        ≠
working-tree recovery by default
        ≠
Bindable / Production
```

## Part A — Candidate Identity Draft

### Allowed

```text
• Propose provisional strategy_id / version labels（draft only）
• Record source_revision + ordered source_manifest of binding modules
• Record observed class-attribute defaults as parameter_manifest draft
• Declare market_scope / execution_model only when observable in source
• Enumerate missing SAC-v1 fields and architecture deviations
• Link to candidate_id / inventory_id
```

### Forbidden

```text
❌ Infer missing execution costs, fill model, or market universe
❌ Treat draft hashes as Identity Freeze
❌ Optimize or change parameters
❌ Claim Testing / Verified / Bindable
```

### Draft outcomes

| Outcome | Meaning |
|---------|---------|
| `DRAFT_COMPLETE_FOR_REVIEW` | All observable fields filled; remaining gaps listed |
| `DRAFT_HOLD` | Insufficient observable identity facts |
| `DRAFT_REJECT` | Source no longer qualifies under SCAP / SAC |

## Part B — Source Recovery classification

| Mode | Meaning | Default |
|------|---------|---------|
| `REFERENCE_ONLY_IN_GIT` | Identity Draft binds immutable git objects; no working-tree restore | **Default** |
| `WORKING_TREE_RESTORE` | Copy/checkout into `strategies/` under new explicit authorization | Not default |
| `REWRITE_AS_PAAF_ASSET` | New implementation under PAAF boundary; new strategy_id lineage | Separate Strategy Research auth |

```text
Identity Draft
        ≠
WORKING_TREE_RESTORE
        ≠
permission to run backtest
```

Recovery that changes bytes → new identity lineage; never silent rewrite of draft hashes.

## Confirmation / Freeze

Protocol Design confirmed and frozen as [`SCIDR-v1`](STRATEGY_CANDIDATE_IDENTITY_DRAFT_SOURCE_RECOVERY_FREEZE.md).

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Design → Confirmation → Freeze under five-round delegation |
