# Strategy Candidate Admission Review

> **Type**: Candidate Source Admission（≠ StrategyIdentity Freeze · ≠ Source Recovery · ≠ Implementation · ≠ Backtest）  
> **Status**: **COMPLETE** ✓  
> **Protocol**: [`SCAP-v1`](STRATEGY_CANDIDATE_ADMISSION_PROTOCOL_FREEZE.md)  
> **Date**: 2026-07-22  
> **Authorization**: Five-round delegated decision — decision 4  
> **Input inventory**: [`STRATEGY_ASSET_FAMILY_INVENTORY_REVIEW.md`](STRATEGY_ASSET_FAMILY_INVENTORY_REVIEW.md)

## Decision record

```text
================================================
STRATEGY CANDIDATE ADMISSION 001

ADMIT_CANDIDATE_SOURCE:
  STRAT_CAND_001_BROOKS_SCALP_SOURCE

HOLD_CANDIDATE_SOURCE:
  pa_minimal
  smc_orderflow_vwap

REJECT / not eligible:
  pa_cta

StrategyIdentity Freeze: NONE
Source Recovery: NONE
Implementation / Backtest: NONE
================================================
```

## 1. Admission outcomes

| Inventory row | Outcome | Evidence-based rationale |
|---------------|---------|--------------------------|
| I007 `brooks_scalp` | **ADMIT_CANDIDATE_SOURCE** | Immutable recoverable source; observable EMA/ATR trend-leg and pullback logic; classified `trend`; signal path has no discovered Context dependency |
| I006 `pa_minimal` | **HOLD_CANDIDATE_SOURCE** | Multi-OPP bundle prevents a single family hypothesis; Context status remains unknown; architecture deviation unresolved |
| I008 `smc_orderflow_vwap` | **HOLD_CANDIDATE_SOURCE** | SMC + VWAP Z-score hybrid is `other`, not forced into Mean-reversion; Context status and architecture deviation remain unresolved |
| I005 `pa_cta` | **REJECT_CANDIDATE_SOURCE** | Signal path embeds `context_layers`; fails independent-consumer boundary |

The admission basis contains no PnL rank, historical performance claim, or
Context-routing objective.

## 2. Admitted Candidate Source

```text
candidate_id:
  STRAT_CAND_001_BROOKS_SCALP_SOURCE

source_revision:
  e2bfc0cf390a0a059fc04dce182082009e685a5b

source_path:
  strategies/brooks_scalp/brooks_scalp.py

observed_primary_sha256:
  cff5bdbbd4495c7c0aa438c1747de9cbe997a18f53e868cd4f04e009b60d9a85

family:
  trend

context_status:
  independent (source classification only)

architecture_status:
  declared_deviation
```

### Mandatory qualifications

```text
Candidate Source
  ≠ strategy_id
  ≠ strategy version
  ≠ SAC-v1 source_manifest
  ≠ parameter_manifest
  ≠ evidence lineage
  ≠ Testing / Verified / Bindable

Historical source remains in git only.
No source recovery into the working tree occurred.
```

The legacy `CtaTemplate` encapsulates pattern/FSM and execution behavior,
therefore its architecture status is a declared deviation from the PAAF target
boundary. It must be resolved or separately accepted before any Bindable claim.

## 3. Why admission is not a strategy selection

Admission establishes a governed research object with explicit missing
information. It does not choose a strategy for trading, establish a Trend S1
asset, create a Mean-reversion peer, or authorize code work.

```text
Candidate Source admission
        ≠
asset selection for implementation
        ≠
RC001-B re-bind
        ≠
Context consumer experiment
```

## 4. Next boundary（updated）

Five-round delegated follow-on completed Identity Draft under `SCIDR-v1`.

```text
CID_001: DRAFT_COMPLETE_FOR_REVIEW
recovery_mode: REFERENCE_ONLY_IN_GIT
Identity Freeze / working-tree restore: NOT STARTED
```

See [`STRATEGY_CANDIDATE_IDENTITY_DRAFT_001.md`](STRATEGY_CANDIDATE_IDENTITY_DRAFT_001.md).

```text
Current next legal actions（另授）:
  Authorize Working-Tree Restore of STRAT_CAND_001
  Authorize PAAF Rewrite Design for STRAT_TREND_BROOKS_SCALP_01
  Authorize Candidate Identity Freeze（after market_scope / costs / architecture acceptance）
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | `brooks_scalp` admitted as Candidate Source only; no identity freeze or code work |
