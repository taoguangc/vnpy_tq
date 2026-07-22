# Strategy Asset Family Inventory and Classification Protocol — Design

> **Type**: Protocol Design（≠ Inventory Execution · ≠ Asset Selection · ≠ Implementation · ≠ Backtest）  
> **Status**: **CONFIRMED** ✓ · authority frozen as `SAFIP-v1`  
> **Version**: 0.1  
> **Date**: 2026-07-22  
> **Authorization**: Three-round delegated decision — round 3  
> **Identity Contract**: [`STRATEGY_ASSET_CONTRACT_FREEZE.md`](STRATEGY_ASSET_CONTRACT_FREEZE.md) — `SAC-v1` **FROZEN**  
> **Validation Framework**: [`STRATEGY_EVIDENCE_VALIDATION_FRAMEWORK_FREEZE.md`](STRATEGY_EVIDENCE_VALIDATION_FRAMEWORK_FREEZE.md) — `SEVF-v1` **FROZEN**

## Design record

```text
================================================
STRATEGY ASSET FAMILY INVENTORY PROTOCOL v0.1

Status: CONFIRMED ✓
Protocol Confirmation: PASS
Protocol Freeze: SAFIP-v1 FROZEN（subsequent delegated decision）
Inventory execution: NONE
Asset selection: NONE
Code / Backtest: NONE
================================================
```

## 1. Purpose

Define how existing strategy sources are inventoried and classified before any
asset is selected for a `SAC-v1` identity package.

```text
Inventory
        ≠
selection
        ≠
validation
        ≠
implementation
```

Primary question:

> 当前可访问的策略来源中，哪些对象具有可审计的资产候选资格，哪些仅是历史名称、引用或不可恢复代码？

## 2. Frozen inventory boundary

An executed inventory under this Protocol may inspect only:

| Source | Permitted status |
|--------|------------------|
| Current repository tree | In scope |
| Reachable git revisions / blobs | In scope |
| Existing research artifacts and manifests | In scope |
| User-provided archive path or source bundle | In scope only when explicitly named |
| Chat descriptions / recollections | Out of scope |
| Unspecified external repositories / web sources | Out of scope |

```text
No named external archive
        → no Recovery Review is implied
        → no unbounded search
```

## 3. Availability classification

Every inventory item receives exactly one source-availability status:

| Status | Meaning |
|--------|---------|
| `AVAILABLE` | Source is present in the current tree and readable |
| `RECOVERABLE` | Source is reachable at an immutable git revision but absent from the tree |
| `REFERENCED_ONLY` | Named/imported but no source object is available |
| `ARTIFACT_ONLY` | Research artifact exists but binding source is unavailable |
| `UNAVAILABLE` | Neither source nor sufficient artifact is reachable |

```text
AVAILABLE / RECOVERABLE
        ≠
Candidate
        ≠
Bindable
```

## 4. Candidate-qualification classification

For each available source, the protocol records independent dimensions:

| Dimension | Allowed values | Rule |
|-----------|----------------|------|
| `identity_readiness` | `none` / `partial` / `complete` | `complete` requires every `SAC-v1` field; no inferred values |
| `architecture_status` | `conformant` / `declared_deviation` / `unknown` | PAAF Strategy / Detector / Risk / Execution boundary must be observable |
| `context_status` | `independent` / `embedded` / `unknown` | Any Context-like signal-path gate is `embedded` until disproven |
| `evidence_status` | `none` / `artifact_partial` / `closed_linked` | `closed_linked` requires exact identity-hash linkage |
| `lifecycle_eligibility` | `none` / `candidate_only` / `testing_eligible` | Determined only from the above fields |

No inventory output may label an item `Verified`, `Bindable`, `Production`, or
“profitable.” Those labels require `SEVF-v1` evidence and separate identity
freeze decisions.

## 5. Family classification rules

Family tags are hypotheses about signal behavior, not performance labels:

| Tag | Minimum observable basis | Insufficient basis |
|-----|--------------------------|--------------------|
| `trend` | Entry/exit logic systematically follows directional continuation or breakout structure | File/class name, a moving average alone, or PnL |
| `mean_reversion` | Logic systematically trades return toward a declared reference/range center | Oscillator import alone or PnL |
| `volatility` | Logic is explicitly driven by a declared volatility state / expansion / contraction mechanism | ATR use only |
| `other` | Logic does not satisfy another tag, or evidence is insufficient | “Hybrid” as a way to avoid disclosure |

```text
Family tag
        ≠
orthogonality proof
        ≠
Context compatibility
        ≠
selection for implementation
```

An item may have multiple tags only with an explicit architecture explanation.
An ambiguous item is tagged `other` or left unclassified; it must not be forced
into `trend` or `mean_reversion`.

## 6. Inventory record minimum fields

```text
inventory_id
source_path / source_revision
availability_status
source hash if readable
candidate family tags + observable basis
identity_readiness
architecture_status
context_status
evidence_status
lifecycle_eligibility
reason / missing fields
```

The protocol requires a machine-readable inventory record plus a human review
summary. It does not require a backtest.

## 7. Explicit exclusions and retained boundaries

```text
❌ Choose a preferred strategy family
❌ Infer missing parameters, execution model or lineage
❌ Reconstruct a strategy from a description
❌ Modify recoverable legacy code to make it qualify
❌ Rank items by PnL / historical mention
❌ Treat a historical artifact as a source-equivalent asset
❌ Reopen RC001-B
```

`classic_*` names, deleted legacy PA modules, or previous strategy discussions
are treated only under their actual availability and classification record.

## 8. Confirmation result

Protocol Design v0.1 was confirmed and subsequently frozen as
[`SAFIP-v1`](STRATEGY_ASSET_FAMILY_INVENTORY_PROTOCOL_FREEZE.md).

```text
Confirmation PASS
        ≠
Protocol Freeze
        ≠
Inventory execution
        ≠
Asset selection / code / backtest
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Protocol Design v0.1 created under three-round delegated decision |
| 2026-07-22 | Protocol Confirmation **PASS** under ten-round delegated decision |
| 2026-07-22 | Protocol frozen as [`SAFIP-v1`](STRATEGY_ASSET_FAMILY_INVENTORY_PROTOCOL_FREEZE.md) |
