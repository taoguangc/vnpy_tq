# Candidate Identity Draft and Source Recovery Protocol Freeze

> **Type**: Protocol Freeze  
> **Status**: **FROZEN** ✓  
> **Protocol ID**: `SCIDR-v1`  
> **Date**: 2026-07-22  
> **Authorization**: Five-round delegated decision — decision 3  
> **Design / Confirmation**: Design **CONFIRMED** · Confirmation **PASS**

## Freeze record

```text
================================================
SCIDR-v1 FROZEN ✓

Allows: Candidate Identity Draft under REFERENCE_ONLY_IN_GIT
Does NOT allow by default:
  WORKING_TREE_RESTORE
  Identity Freeze
  Implementation rewrite
  Backtest / Observation
================================================
```

## Frozen rules（binding）

1. A Candidate Identity Draft may bind only admitted Candidate Sources (`SCAP-v1`).
2. Draft `strategy_id` / `version` are provisional labels, not frozen identities.
3. `source_manifest` lists **binding** modules only（strategy behavior）. Tooling runners may be listed as non-binding notes.
4. Parameter defaults must come from source class attributes / declared parameters; no invented fields.
5. Default recovery mode is `REFERENCE_ONLY_IN_GIT`.
6. `WORKING_TREE_RESTORE` and `REWRITE_AS_PAAF_ASSET` require new explicit authorization.
7. Any byte change after draft → new draft / new lineage.

## Modification rule

```text
SCIDR-v1 is immutable.
Change → new protocol version + confirmation + freeze.
```

## Delegated execution

```text
Decision 4: produce Identity Draft for STRAT_CAND_001_BROOKS_SCALP_SOURCE
Decision 5: recovery classification → REFERENCE_ONLY_IN_GIT（stop）
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | `SCIDR-v1` frozen |
