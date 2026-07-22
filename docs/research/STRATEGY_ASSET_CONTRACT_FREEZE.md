# Strategy Asset Contract Freeze

> **Type**: Contract Freeze（≠ Asset Selection · ≠ Identity Freeze · ≠ Implementation · ≠ Backtest）  
> **Status**: **FROZEN** ✓  
> **Contract ID**: `SAC-v1`  
> **Date**: 2026-07-22  
> **Authorization**: `Authorize Strategy Asset Contract Freeze`  
> **Confirmed Design**: [`STRATEGY_ASSET_CONTRACT_DESIGN.md`](STRATEGY_ASSET_CONTRACT_DESIGN.md) v0.1  
> **Confirmation**: [`STRATEGY_ASSET_CONTRACT_CONFIRMATION.md`](STRATEGY_ASSET_CONTRACT_CONFIRMATION.md) — **PASS**

## Freeze record

```text
================================================
STRATEGY ASSET CONTRACT SAC-v1

Contract: FROZEN ✓
Asset selection: NONE
Strategy identities frozen: NONE
Strategy implementation: NONE
Backtest / Observation: NONE

CAP-CTX-001: CLOSED
RC001-B: PERMANENTLY CLOSED
================================================
```

## 1. Contract purpose

`SAC-v1` defines the minimum identity, reproducibility, architecture, and
evidence conditions for a PAAF **Bindable Strategy Asset**.

```text
Bindable Strategy Asset
        ≠
strategy claimed profitable
        ≠
Production / Live strategy
        ≠
Context trading value proven
```

The Contract is a prerequisite for later asset work. It does not create,
select, approve, or rank any strategy.

## 2. Frozen StrategyIdentity schema

Every asset record uses the following required fields:

| Field | Frozen rule |
|-------|-------------|
| `strategy_id` | Stable unique identifier; never reused for behaviorally different code |
| `version` | SemVer; behavior change requires a new version |
| `source_revision` | Full immutable repository revision; no abbreviated SHA |
| `source_manifest` | Canonical list of all binding source paths and content hashes |
| `source_hash` | Aggregate SHA256 defined in §3 |
| `parameter_manifest` | Canonical, typed parameter values and declared units |
| `parameter_hash` | SHA256 defined in §3 |
| `market_scope` | Symbol/universe, session, period and data-scope declaration |
| `execution_model` | Signal timeframe, order type, fill assumptions, stop/target, sizing-rule class, fee/slippage profile |
| `evidence_lineage` | Immutable experiment / artifact references as defined in §5 |
| `class_tags` | One or more: `trend`, `mean_reversion`, `volatility`, `other` |
| `context_independence` | Attestation and verification status defined in §4 |
| `not_fabricated_for_context` | Attestation that the asset was not created solely to force a Context result |
| `architecture_attestation` | PAAF boundary conformance and declared deviations |

Missing or unverifiable required data means the asset is **NOT BINDABLE**.

## 3. Frozen canonicalization and hash rules

### 3.1 `source_manifest`

```json
[
  {
    "path": "repository/relative/path.py",
    "sha256": "lowercase-64-hex-digest"
  }
]
```

Rules:

```text
• Paths are repository-relative, use "/" separators, unique and lexicographically sorted.
• Each SHA256 hashes the exact UTF-8 source file bytes.
• source_manifest is canonical JSON:
  UTF-8 without BOM; recursively sorted object keys; compact separators ",";
  and ":"; no insignificant whitespace.
• source_hash = SHA256(canonical source_manifest JSON bytes).
```

### 3.2 `parameter_manifest`

```json
{
  "parameter_name": {
    "value": 20,
    "type": "int",
    "unit": "bars"
  }
}
```

Rules:

```text
• Object keys are recursively sorted.
• Each parameter declares value, type and unit ("dimensionless" if applicable).
• NaN, Infinity and locale-dependent numeric text are forbidden.
• parameter_hash = SHA256(canonical UTF-8 JSON bytes using §3.1 encoding rules).
• The frozen asset record preserves both manifests, not only aggregate hashes.
```

## 4. Frozen architecture and Context-independence rules

New PAAF strategy assets must attest to the boundary:

```text
Context → Detector Registry → Risk → Execution → Logger
```

```text
Detector: identifies patterns / produces Signal | None
Strategy: orchestrates Context → Registry → Risk → Execution → Logger
```

For an asset to claim `context_independence = true`:

```text
• Its signal path must not consume Context.
• Context must not generate entries, expected return, or sizing alpha.
• Future Context use may only be Filter / Risk Modifier / Monitoring / Permission.
```

`architecture_attestation` must list all deviations. A legacy deviation is
allowed only as a declared Candidate record; it prevents `Bindable` status until
resolved or separately accepted. In particular, a strategy with an embedded
Context-like regime gate is not an independent Context consumer.

## 5. Frozen evidence-lineage requirements

| Lifecycle status | Minimum evidence rule |
|------------------|-----------------------|
| `Candidate` | `evidence_lineage` may be empty; asset is not Bindable |
| `Testing` | A pre-registered experiment reference and the exact source/parameter hashes are required |
| `Verified` | At least one immutable **Closed** experiment artifact tied to the same `source_hash` and `parameter_hash` |
| `Bindable` | All schema fields verified, architecture/context attestations accepted, and the Closed evidence package includes experiment ID, run ID, artifact location and evaluation result |

```text
Evidence result may be KEEP, HOLD, REVERT, or negative.
No PnL threshold is implied by SAC-v1.
```

Evidence sufficiency and promotion/falsification criteria will be specified by a
separately authorized Validation Framework. `SAC-v1` freezes provenance
requirements only; it does not declare an asset statistically effective.

## 6. Frozen lifecycle

```text
Idea
  → Candidate
  → Testing
  → Verified
  → Bindable
  → Deprecated
```

```text
Bindable
        ≠
Production
        ≠
Alpha proven
        ≠
permission for Context routing
```

## 7. Modification rule

```text
SAC-v1 is immutable.

Any schema, canonicalization, architecture, or evidence-lineage change:
  → new Contract ID / version
  → new confirmation and freeze
  → no silent rewrite of existing identity records
```

## 8. Explicit non-authorizations

```text
❌ Select Trend / Mean-Reversion / Volatility assets
❌ Create or modify strategy code
❌ Freeze an individual StrategyIdentity
❌ Parameter optimization or PnL ranking
❌ Backtest / Observation
❌ Portfolio construction
❌ Reopen RC001-B or mutate its frozen Contract
❌ Claim Context → Alpha / return / drawdown improvement
```

## 9. Next gate

The next phase decision is intentionally separate:

```text
Authorize Strategy Evidence and Validation Framework Design
```

That authorization, if granted, concerns promotion/falsification criteria only.
It does not authorize code, backtests, candidate family selection, or identity
freezes.

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | `SAC-v1` frozen after Design Confirmation PASS |
