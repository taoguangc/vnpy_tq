# New Strategy Asset Design — CID_014 Path

> **Type**: Strategy Asset Design（≠ Identity Freeze · ≠ Implementation · ≠ Backtest · ≠ Alpha）  
> **Status**: **DESIGNED** ✓  
> **Design ID**: `NSAD_CID_014_V0_1`  
> **Date**: 2026-07-24  
> **Authorization**: Delegation-25BF（`授权你决定25次` · interpreted as menu **Option B**）  
> **Prior**: `CPD_CID_003`–`CPD_CID_013` PAUSED · AERC_003–013 Alpha NONE  
> **Contracts**: `SAC-v1` · `SAFIP-v1` · `SEVF-v1` · `SCIDR-v1`  
> **Data baseline（future）**: docs/07 · TQ offline · 1m · CbC · unadjusted · real costs

## Design record

```text
================================================
NSAD_CID_014_V0_1

Purpose: Open NEW strategy asset research path after
         CID_003–013 Pause（all Alpha NONE）.

CID_002–013: NOT resumed · NOT reopened for H_EDGE rescue
Alpha:   NONE（new asset starts at zero hypothesis）
Code / Identity Freeze / Observation: NOT AUTHORIZED here
================================================
```

## 0. Why a new asset now

```text
Closed Alpha-NONE:
  CID_003–012  opp/ PA shelf + residual DT
  CID_013      SMC OB-long structure（H_MECH KEEP · H_EDGE REVERT×2）

Lesson:
  First beyond-opp structure seed also failed frozen H_EDGE gates.
  CID_013 NSAD explicitly deferred Setup B（pure VWAP Z-score path）
  as a separate hypothesis — that residual is the next inventory-backed
  seed from SAFIP I008 without chat Spec invention.
```

## 1. Asset slot

| Field | Design value |
|-------|----------------|
| `campaign_id` | `CID_014` |
| `working_strategy_id`（provisional） | `STRAT_SMC_ZSCORE_LONG_01`（pending Identity Freeze） |
| `class_tags`（provisional） | `["smc","vwap","zscore","mean_reversion","long_only"]` |
| `lifecycle_start` | Candidate（after Identity Freeze） |
| `parent_asset` | none（**not** a fork of `STRAT_SMC_OB_LONG_01` / CID_013） |

```text
Explicit: ≠ CID_013 OB parameter transfer · ≠ hybrid restore · ≠ OB rescue
```

## 2. Preferred seed（inventory / git · not Bindable）

| Seed | Provenance | Why preferred |
|------|------------|---------------|
| **SMC Setup B — VWAP Z-score oversold long** | git `e2bfc0c…` · `smc_orderflow_vwap_strategy.py` · `_try_setup_b_stat` + `_update_zscore` | Pre-declared OUT of CID_013；statistical axis ≠ OB structure |

```text
Recovery mode intent: REWRITE_AS_PAAF_ASSET（SCIDR）
≠ WORKING_TREE_RESTORE · ≠ reopen Closed CID_013 EXPs
```

### Declared simplifications（at future rewrite）

```text
Scope IN:  5m · session VWAP（reset at night open 21:00 legacy）
           · z = (close − vwap) / std(close − vwap, vwap_length)
           · LONG when z < −zscore_threshold
           · stop = min(low[-lookback:]) − buffer（ticks）
Scope OUT: Order Block / Setup C / Setup A triple resonance
           · bar-delta hard gate（strip for single-axis Candidate）
           · scale-out · OPP16 slow channel
Keep defaults（legacy starting points）:
  zscore_threshold=2.5 · vwap_length=60 · setup_b_stop_lookback=5
  ob_stop_buffer=2（as stop pad）· long-only
Explicit PatternState: may hold rolling VWAP accumulators as PatternState
```

### Explicitly NOT preferred as CID_014 mainline

| Object | Reason |
|--------|--------|
| CID_003–013 assets | Alpha CLOSED · PAUSED |
| CID_013 OB identity | Separate freeze · do not merge / rescue |
| Chat-invented z-score Spec | Violates SAC |
| Full VWAP+Delta+OB hybrid | Multi-hypothesis · deferred |
| `pa_minimal` multi-OPP | Bundle · deferred |

## 3. Research question（CID_014）

```text
Primary:
  Can a simplified VWAP Z-score oversold long mechanism, rewritten as a
  Context-independent PAAF Detector under docs/07 costs, produce an
  auditable H_MECH AND a pre-registered H_EDGE that survives temporal OOS
  — without parameter shopping and without borrowing CID_013 OB bytes?

Secondary（only after H_EDGE structure exists）:
  Multi-symbol · capital surface · Context consumption
```

## 4. Planned evidence order（do not skip）

```text
1) Morphology Spec（z-score long only）+ Detector + Identity Freeze
2) SEVF Spec
3) H_MECH EXP
4) H_EDGE diagnostic（SAME gates as AERC CID_003–013）
5) H_EDGE OOS
6) Alpha petition OR Negative Alpha close
```

```text
FORBIDDEN:
  Bindable theater before H_EDGE
  Resume CID_013 idle KEEP hunting as substitute
  Bundle OB + z-score under one strategy_id
  Re-enable Delta/OB “to make it work”
```

## 5. Hard boundaries

```text
❌ Resume CID_003–013 under this Design
❌ PnL optimization / grid search as Design goal
❌ Implementation / Identity Freeze under this Design alone
❌ Claim Setup B is CID_013 rewrite
```

## 6. Inventory honesty

```text
After CID_014 consumes Setup B residual from I008 smc package,
further NSAD from that package is thin（Setup C / resonance A）.
Next would need pa_minimal scoped extract, new Spec, or Resume power.
```

## 7. Explicit non-grants

```text
❌ Identity Freeze · code · Observation · Alpha · Bindable · Production
❌ SCAP Bindable claim for smc package
```

## 8. Next（须另授 · pick）

```text
Authorize Identity Freeze · SMC Z-score long Detector + orchestrator @0.1.0
  — OR — leave CID_014 at Design-only
NOT: auto-implement · H_EDGE before Freeze · Resume paused · CID_013 merge
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-24 | NSAD_CID_014_V0_1 DESIGNED · Setup B z-score residual · Delegation-25BF |
