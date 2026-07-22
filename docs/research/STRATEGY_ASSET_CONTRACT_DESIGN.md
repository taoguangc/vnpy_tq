# Strategy Asset Contract — Design（Draft）

> **Type**: Contract Design（≠ Freeze · ≠ Implementation · ≠ Backtest）  
> **Status**: **CONFIRMED** ✓ · superseded as authority by `SAC-v1` **FROZEN**  
> **Version**: 0.1  
> **Date**: 2026-07-22  
> **Path**: `docs/research/STRATEGY_ASSET_CONTRACT_DESIGN.md`  
> **Phase Auth**: [`STRATEGY_RESEARCH_PHASE_AUTHORIZATION.md`](STRATEGY_RESEARCH_PHASE_AUTHORIZATION.md) — **GRANTED**  
> **Positioning**: [`EPOCH_5_POSITIONING.md`](../releases/EPOCH_5_POSITIONING.md)  
> **Data baseline**（future Observation）: TQ offline · 1m · CbC · unadjusted · real costs

### Design Record

```text
================================================
STRATEGY ASSET CONTRACT DESIGN v0.1

Status: CONFIRMED ✓
Confirmation: PASS
Freeze: NOT STARTED
Code / Backtest: NONE
================================================
```

---

## 0. Purpose

Define what counts as a **bindable strategy asset** for PAAF research consumption（including future Context Consumer experiments）.

```text
Strategy asset
        ≠
chat description
        ≠
unhashed script
        ≠
temporary adapter written to unblock a Context experiment
```

Primary question:

> 什么样的策略才值得被 Context 安全消费？

---

## 1. StrategyIdentity（required fields）

Every candidate asset must expose a frozen identity package:

| Field | Requirement |
|-------|-------------|
| `strategy_id` | Stable string ID（e.g. `STRAT_TREND_DONCHIAN_01`） |
| `version` | SemVer；behavior change → new version |
| `source_revision` | Git commit（or equivalent immutable revision） |
| `source_manifest` | Ordered repository-relative source paths; each path's SHA256 |
| `source_hash` | SHA256 of the canonical `source_manifest` |
| `parameter_manifest` | Explicit parameters, types, units and defaults/overrides |
| `parameter_hash` | SHA256 of canonical JSON `parameter_manifest` |
| `market_scope` | Symbols / universe declaration |
| `execution_model` | Bar TF · order type · stop/target policy · sizing rule class |
| `evidence_lineage` | Parent experiment_id(s) / Closed artifacts; empty only for a pre-evidence Candidate |
| `class_tags` | At least one: `trend` · `mean_reversion` · `volatility` · `other` |
| `context_independence` | Attestation: no Context inside strategy signal path |
| `not_fabricated_for_context` | Attestation: not created solely to pass a Context trial |
| `architecture_attestation` | Signal / Detector / Risk / Execution boundary status; legacy deviations declared |

```text
StrategyIdentity
 ├── strategy_id
 ├── version
 ├── source_manifest + source_hash
 ├── parameter_manifest
 ├── market_scope
 ├── execution_model
 └── evidence lineage
```

Missing any required field → **NOT BINDABLE**.

### 1.1 Canonical hash rules

```text
source_manifest:
  repository-relative paths sorted lexicographically
  each content SHA256 recorded
  source_hash = SHA256(canonical UTF-8 JSON source_manifest)

parameter_manifest:
  UTF-8 JSON; object keys recursively sorted
  numbers serialized without locale-dependent formatting
  parameter_hash = SHA256(the canonical JSON bytes)
```

The frozen record must preserve both manifests. A bare aggregate hash is not
reproducible evidence.

---

## 2. Asset classes（research families）

Target families（governance classes · not yet implementations）:

| Class | Role hypothesis | Notes |
|-------|-----------------|-------|
| **Trend** | Benefits from expansion-like regimes | Candidate S1-class for future routing |
| **Mean-reversion** | Benefits from compression / range-like regimes | Candidate S2-class |
| **Volatility** | Optional third orthognal axis | Not required for first pair |

```text
Family name discussion
        ≠
Frozen identity package
```

Historical names（Turtle / Donchian / DualThrust / …）are **inventory labels only** until Contract-compliant packages exist.

---

## 3. Lifecycle

```text
Idea
  → Candidate（source present · identity incomplete）
  → Testing（identity draft · experiments running）
  → Verified（Closed evidence · identity freeze eligible）
  → Bindable（identity frozen · hashes locked）
  → Deprecated（immutable archive）
```

```text
Bindable
        ≠
Production / Live
        ≠
Alpha proven
```

Promotion requires Evidence Chain Spec（sub-phase 5.2 · not yet authorized for Freeze）.

---

## 4. Independence & consumption rules

Aligned with Decision 019 / Narrow Candidate:

```text
Strategy generates signals independently
Context（future）may only:
  Filter · Risk Modifier · Monitoring · Permission
```

Forbidden inside a Strategy Asset claiming Context-independence:

```text
❌ Embedded Context Engine driving entries
❌ Context score → position size alpha
❌ Hidden regime gate that duplicates unpublished Context
```

（Legacy deleted `pa_cta` with `context_layers` is **not** a qualifying independent asset without redesign + new identity.）

`architecture_attestation` must state whether the asset follows the PAAF
boundary:

```text
Context → Detector Registry → Risk → Execution → Logger
```

Any legacy exception is explicit and prevents a `Bindable` designation until
resolved or separately accepted.

---

## 5. Explicit non-goals of this Design

```text
❌ Implement strategies in this document
❌ Choose concrete S1/S2 code paths yet
❌ Reopen RC001-B C-BIND under old experiment_id
❌ Optimize parameters for return
❌ Portfolio weights
```

---

## 6. Relationship to CAP-CTX / RC001-B

| Object | Relation |
|--------|----------|
| CAP-CTX-001 | **CLOSED** · not continued here |
| RC001-B Contract | **FROZEN archive** · not mutated |
| Future Context Consumer Experiment | New `experiment_id` only after bindable assets exist |
| A1 ContextState | Optional future consumer input · not a strategy |

---

## 7. Confirmation gate

Confirmation **PASS** was granted on 2026-07-22. The Design is now binding as
the required content for a future Strategy Asset Contract Freeze.

```text
Confirmation PASS
        ≠
Contract Freeze
        ≠
Identity Freeze
        ≠
Implementation / Backtest authorization
```

Contract Freeze was authorized and completed as [`SAC-v1`](STRATEGY_ASSET_CONTRACT_FREEZE.md).

---

## 修订记录

| 日期 | 说明 |
|------|------|
| 2026-07-22 | Strategy Asset Contract Design **DRAFT** v0.1 |
| 2026-07-22 | Confirmation **PASS**; added reproducible source/parameter hash rules and architecture attestation |
| 2026-07-22 | Contract frozen as [`SAC-v1`](STRATEGY_ASSET_CONTRACT_FREEZE.md) |
