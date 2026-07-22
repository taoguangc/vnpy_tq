# Strategy Candidate Admission Protocol — Design

> **Type**: Protocol Design（≠ StrategyIdentity Freeze · ≠ Source Recovery · ≠ Implementation · ≠ Backtest）  
> **Status**: **CONFIRMED** ✓ · authority frozen as `SCAP-v1`  
> **Version**: 0.1  
> **Date**: 2026-07-22  
> **Authorization**: Five-round delegated decision — decision 1  
> **Inputs**: `SAC-v1` / `SEVF-v1` / `SAFIP-v1` — **FROZEN**

## Purpose

Define how a `candidate_only` inventory item may be admitted as a **Candidate
Source** without being mistaken for a selected, frozen, verified, or bindable
strategy asset.

```text
Candidate Source
        ≠
SAC-v1 StrategyIdentity
        ≠
Testing-eligible asset
        ≠
code restoration
        ≠
strategy implementation
```

## Admission preconditions

An item can be admitted only if all are true:

| Requirement | Rule |
|-------------|------|
| Inventory status | `RECOVERABLE` or `AVAILABLE`, with `candidate_only` eligibility |
| Provenance | Immutable source revision and observed source hash recorded |
| Family basis | Observable signal logic supports one declared family tag |
| Context status | `independent`, or deviation explicitly disclosed and held |
| Architecture | All deviations explicitly recorded |
| Selection basis | Not selected by PnL, historical mention, or Context-routing need |
| Missing fields | Missing `SAC-v1` identity fields enumerated; not inferred |

## Admission outcomes

| Outcome | Meaning |
|---------|---------|
| `ADMIT_CANDIDATE_SOURCE` | Source is a governed research candidate; no identity or experiment exists |
| `HOLD_CANDIDATE_SOURCE` | Source may be reconsidered after missing classification facts are supplied |
| `REJECT_CANDIDATE_SOURCE` | Source violates a hard boundary or lacks meaningful candidate basis |

## Candidate Source record

```text
candidate_id              # not strategy_id
inventory_id
source_revision
source_path
observed_primary_sha256
family_tag + observable basis
context_status
architecture_deviations
missing_SAC_v1_fields
admission_outcome
admission_rationale
```

No `strategy_id`, version, parameter manifest, execution model, or evidence
lineage may be inferred at admission.

## Hard boundaries

```text
❌ Recover / copy source into current tree
❌ Modify legacy code
❌ Freeze a StrategyIdentity
❌ Claim Candidate Source is verified, bindable or profitable
❌ Backtest, optimize or run an experiment
❌ Use Context to decide admission
❌ Reopen RC001-B
```

## Confirmation result

Protocol Design v0.1 is confirmed and subsequently frozen as
[`SCAP-v1`](STRATEGY_CANDIDATE_ADMISSION_PROTOCOL_FREEZE.md).

```text
Confirmation PASS
        ≠
Protocol Freeze
        ≠
Candidate Source admission
        ≠
StrategyIdentity / code / backtest
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Candidate Admission Protocol Design v0.1 |
| 2026-07-22 | Protocol Confirmation **PASS** under five-round delegated decision |
| 2026-07-22 | Protocol frozen as [`SCAP-v1`](STRATEGY_CANDIDATE_ADMISSION_PROTOCOL_FREEZE.md) |
