# Strategy Candidate Admission Protocol Freeze

> **Type**: Protocol Freeze（≠ Candidate Admission · ≠ Identity Freeze · ≠ Source Recovery · ≠ Backtest）  
> **Status**: **FROZEN** ✓  
> **Protocol ID**: `SCAP-v1`  
> **Date**: 2026-07-22  
> **Authorization**: Five-round delegated decision — decision 3  
> **Design**: [`STRATEGY_CANDIDATE_ADMISSION_PROTOCOL_DESIGN.md`](STRATEGY_CANDIDATE_ADMISSION_PROTOCOL_DESIGN.md) v0.1  
> **Confirmation**: [`STRATEGY_CANDIDATE_ADMISSION_PROTOCOL_CONFIRMATION.md`](STRATEGY_CANDIDATE_ADMISSION_PROTOCOL_CONFIRMATION.md) — **PASS**

## Frozen admission rule

```text
Inputs:
  SAFIP-v1 inventory row with candidate_only eligibility
  + immutable source revision
  + observed source hash
  + observable family basis
  + disclosed Context / architecture state

Outputs:
  ADMIT_CANDIDATE_SOURCE
  HOLD_CANDIDATE_SOURCE
  REJECT_CANDIDATE_SOURCE
```

An admitted Candidate Source is not a `SAC-v1` StrategyIdentity and may not be
treated as Testing, Verified, Bindable, profitable, or production-ready.

## Required record

```text
candidate_id              # never strategy_id
inventory_id
source_revision + source_path + observed_primary_sha256
family tag + observable basis
context_status
architecture_deviations
missing_SAC_v1_fields
admission_outcome + rationale
```

## Forbidden

```text
❌ Recover source into current tree
❌ Modify source
❌ Infer source manifest, parameters or execution model
❌ Freeze StrategyIdentity
❌ Backtest / experiment / parameter optimization
❌ Use Context to justify admission
❌ Reopen RC001-B
```

## Modification rule

```text
SCAP-v1 is immutable.

Any precondition, outcome or record requirement change:
  → new protocol version
  → new confirmation and freeze
```

## Delegated execution result

```text
Decision 4 completed:
  Candidate Source admission review
  → one Candidate Source admitted
  → no StrategyIdentity / code / backtest
```

See [`STRATEGY_CANDIDATE_ADMISSION_REVIEW.md`](STRATEGY_CANDIDATE_ADMISSION_REVIEW.md).

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | `SCAP-v1` frozen under five-round delegated decision |
