# Working-Tree Restore Review — CID_001 / STRAT_CAND_001

> **Type**: Source Recovery Execution Review（≠ Identity Freeze · ≠ Rewrite · ≠ Backtest）  
> **Status**: **RESTORE_COMPLETE** ✓  
> **Date**: 2026-07-22  
> **Authorization**: User path **A** — `Authorize Working-Tree Restore of STRAT_CAND_001`  
> **Protocol**: [`SCIDR-v1`](STRATEGY_CANDIDATE_IDENTITY_DRAFT_SOURCE_RECOVERY_FREEZE.md)  
> **Draft**: [`STRATEGY_CANDIDATE_IDENTITY_DRAFT_001.md`](STRATEGY_CANDIDATE_IDENTITY_DRAFT_001.md)  
> **Candidate**: `STRAT_CAND_001_BROOKS_SCALP_SOURCE`

## Restore record

```text
================================================
WORKING_TREE_RESTORE — CID_001

recovery_mode:     WORKING_TREE_RESTORE
source_revision:   e2bfc0cf390a0a059fc04dce182082009e685a5b
target path:       strategies/brooks_scalp/
binding hashes:    MATCH CID_001 source_manifest（git-blob / LF bytes）
Identity Freeze:   NOT PERFORMED
Rewrite / Backtest: NOT PERFORMED
================================================
```

## Paths restored

| Path | Role | SHA256（working tree = git blob） |
|------|------|----------------------------------|
| `strategies/brooks_scalp/__init__.py` | binding | `3fe8ea0db447f6ed43a5fbb53400c98fe96aed308a070f0058661362ab76dea6` |
| `strategies/brooks_scalp/brooks_scalp.py` | binding | `cff5bdbbd4495c7c0aa438c1747de9cbe997a18f53e868cd4f04e009b60d9a85` |
| `strategies/brooks_scalp/rollover_strategy.py` | binding | `3bdb48813c05520f0b8ccc2f45c9146ef1968c6dafc2d8f22ebac88074a83149` |
| `strategies/brooks_scalp/backtest.py` | non-binding tooling | restored · not in `source_hash` |
| `strategies/brooks_scalp/backtest_tick.py` | non-binding tooling | restored · not in `source_hash` |

## Procedure notes

```text
1. git checkout <source_revision> -- strategies/brooks_scalp/
2. Windows core.autocrlf=true converted LF→CRLF on checkout
3. Files rewritten from git cat-file blobs so working-tree bytes
   match SAC/SCIDR identity hashes（LF canonical）
4. No edits to strategy logic
```

## Hard guarantees after restore

```text
✓ Working tree contains strategies/brooks_scalp/
✓ Binding module hashes match CID_001 draft
✗ Identity Freeze not performed
✗ PAAF rewrite not started
✗ Backtest / Observation not run
✗ market_scope not invented（still UNBOUND_AT_ASSET）
✗ RC001-B not reopened
```

## Residual blockers（unchanged for Freeze / Bindable）

```text
• market_scope UNBOUND_AT_ASSET
• evidence_lineage empty
• ADAP T4: Bindable blocked on legacy bytes
• Identity Freeze still requires separate authorization（option C）
• PAAF rewrite still requires separate authorization（option B）
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Working-tree restore authorized and completed under path A |
