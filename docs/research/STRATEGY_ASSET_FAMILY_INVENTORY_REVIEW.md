# Strategy Asset Family Inventory Review

> **Type**: Bounded Inventory Review（≠ Asset Selection · ≠ Identity Freeze · ≠ Implementation · ≠ Backtest）  
> **Status**: **COMPLETE** ✓  
> **Protocol**: [`SAFIP-v1`](STRATEGY_ASSET_FAMILY_INVENTORY_PROTOCOL_FREEZE.md)  
> **Date**: 2026-07-22  
> **Authorization**: Ten-round delegated decision — decision 3  
> **Machine record**: `research/output/evidence/STRATEGY_ASSET_INVENTORY_001/inventory.json`

## Review record

```text
================================================
STRATEGY ASSET FAMILY INVENTORY 001

Scope: current tree + reachable git + existing artifacts
External archive search: NONE

AVAILABLE full strategy assets: NONE
RECOVERABLE source families: 4
Testing-eligible assets: NONE
Selected assets: NONE
Code / Backtest: NONE
================================================
```

## 1. Source scope

```text
IN:
  current strategies/
  reachable git revision e2bfc0cf390a0a059fc04dce182082009e685a5b
  existing research/output/evidence artifacts

OUT:
  chat descriptions
  unspecified external sources
  recovery from unnamed archives
```

`classic_*` is referenced by `scripts/run_classic_baseline_compare.py`, but
has no reachable source blob. It is classified `REFERENCED_ONLY`.

## 2. Inventory results

| ID | Object | Availability | Family tag / basis | Identity | Architecture | Context | Evidence | Eligibility |
|----|--------|--------------|--------------------|----------|--------------|---------|----------|-------------|
| I001 | `TemplateStrategy` | AVAILABLE | unclassified; skeleton only | partial | unknown | unknown | none | none |
| I002 | `PaafStrategy` | AVAILABLE | `other`; orchestration only | partial | conformant orchestration | embedded by design | none | none |
| I003 | OPP16 detector + artifact | AVAILABLE source / artifact partial | unclassified; detector ≠ strategy | partial | conformant detector | independent signal path | artifact partial | none |
| I004 | `classic_*` imports | REFERENCED_ONLY | unknown; source absent | none | unknown | unknown | none | none |
| I005 | `pa_cta` | RECOVERABLE | `other`; multi-OPP PA bundle | partial | declared deviation | embedded | none | none |
| I006 | `pa_minimal` | RECOVERABLE | `other`; multi-OPP PA bundle | partial | declared deviation | unknown | none | candidate_only |
| I007 | `brooks_scalp` | RECOVERABLE | `trend`; EMA + ATR trend-leg / pullback logic | partial | declared deviation | independent | none | candidate_only |
| I008 | `smc_orderflow_vwap` | RECOVERABLE | `other`; SMC + VWAP Z-score hybrid | partial | declared deviation | unknown | none | candidate_only |

### Observed source provenance

| Object | Immutable revision | Primary module | Observed SHA256 |
|--------|--------------------|----------------|-----------------|
| `TemplateStrategy` | working tree | `strategies/template_strategy.py` | `1207179e1882f61e66fdf968899bfb4e8569245c533819e87aced8b7ea158050` |
| `PaafStrategy` | working tree | `strategies/paaf/paaf_strategy.py` | `3ded2a40e545fa18cbb588ef72bc62e351d598159427afa3d1320521d1198a17` |
| `pa_cta` | `e2bfc0c…` | `strategies/pa_cta/strategy.py` | `86d9be1bdd47aef8ec29d70c289f03f74b1ba1bde43386bbe3a9d568dd89fa77` |
| `pa_minimal` | `e2bfc0c…` | `strategies/pa_minimal/strategy.py` | `d8124b242d98e2342d604633a09cb8d28c2826b2645e1d73abd8f7862385df79` |
| `brooks_scalp` | `e2bfc0c…` | `strategies/brooks_scalp/brooks_scalp.py` | `cff5bdbbd4495c7c0aa438c1747de9cbe997a18f53e868cd4f04e009b60d9a85` |
| `smc_orderflow_vwap` | `e2bfc0c…` | `strategies/smc_orderflow_vwap/smc_orderflow_vwap_strategy.py` | `fbab74ed18af727973e8a7a0473666f59447bd02290ee5ac6d665fb5e896c52a` |

These are **observed primary-module hashes**, not `SAC-v1 source_manifest`
hashes. No row has a complete StrategyIdentity package.

## 3. Classification evidence

```text
pa_cta:
  imports and calls context_layers
  → context_status = embedded
  → not an independent Context consumer

brooks_scalp:
  CtaTemplate with EMA / ATR trend-leg and pullback state logic
  → family tag = trend
  → source is only candidate_only due missing identity/evidence and architecture deviation

smc_orderflow_vwap:
  combines SMC, VWAP and Z-score paths
  → family tag = other; not forced into mean_reversion

classic_*:
  script imports exist; source blobs do not
  → REFERENCED_ONLY
```

## 4. Result

```text
No AVAILABLE or RECOVERABLE item is Testing-eligible.
No item is Verified, Bindable, Production, or selected.

Candidate-only is a classification status:
  ≠ selection
  ≠ identity freeze
  ≠ implementation authorization
```

The inventory cannot support a Consumer experiment or alter the permanent
closure of RC001-B.

## 5. Decision 4 — boundary

The remaining delegated authority is **not** used to select `brooks_scalp`,
`pa_minimal`, or another historical source. Their `candidate_only` status is
insufficient for selection: all lack a complete `SAC-v1` source/parameter
manifest, evidence lineage, and architecture acceptance.

```text
Stop condition reached:
  no Testing-eligible asset
  no named external archive
  no basis for a non-arbitrary selection
```

Further work requires a new explicit decision, for example:

```text
Authorize Strategy Candidate Admission Protocol Design
```

That future protocol would govern how a `candidate_only` source can be admitted
to a full identity draft. It would still not authorize code or backtests.

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Bounded `SAFIP-v1` inventory complete; no asset selected |
