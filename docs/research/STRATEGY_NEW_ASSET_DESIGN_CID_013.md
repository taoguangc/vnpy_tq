# New Strategy Asset Design — CID_013 Path

> **Type**: Strategy Asset Design（≠ Identity Freeze · ≠ Implementation · ≠ Backtest · ≠ Alpha）  
> **Status**: **DESIGNED** ✓  
> **Design ID**: `NSAD_CID_013_V0_1`  
> **Date**: 2026-07-24  
> **Authorization**: Delegation-25BC（`授权你决定25次` · agent pick **RPP Option A** after repeated bare grants）  
> **Prior**: `RPP_BEYOND_OPP_V0_1`（R1–R3）· `CPD_CID_003`–`CPD_CID_012` PAUSED · AERC_003–012 Alpha NONE  
> **Contracts**: `SAC-v1` · `SAFIP-v1` · `SEVF-v1` · `SCIDR-v1`  
> **Data baseline（future）**: docs/07 · TQ offline · 1m · CbC · unadjusted · real costs

## Design record

```text
================================================
NSAD_CID_013_V0_1

Purpose: Open NEW strategy asset research path BEYOND
         exhausted residual opp/ PA shelf（RPP Option A）.

CID_002–012: NOT resumed · NOT reopened for H_EDGE rescue
Alpha:   NONE（new asset starts at zero hypothesis）
Family honesty: non-PA / SMC-structure seed（inventory I008）
Code / Identity Freeze / Observation: NOT AUTHORIZED here
================================================
```

## 0. Why a new asset now（and why this pick）

```text
Closed Alpha-NONE campaigns: CID_003–012（opp/ PA shelf + residual DT）.
RPP_BEYOND_OPP forbade chat-invented Spec and required explicit A–E.
User continued bare “授权你决定25次”（historical menu-pick ritual）.

Agent decision under Delegation-25BC:
  Pick Option A — Authorize NSAD seed: smc_orderflow_vwap
  Rationale: only RECOVERABLE beyond-opp inventory seed（SAFIP I008）;
             ≠ Spec fabrication; ≠ idle Resume n-hunting under ambiguity.
```

## 1. Asset slot

| Field | Design value |
|-------|----------------|
| `campaign_id` | `CID_013` |
| `working_strategy_id`（provisional） | `STRAT_SMC_OB_LONG_01`（pending Identity Freeze） |
| `class_tags`（provisional） | `["smc","order_block","structure","long_only"]` |
| `lifecycle_start` | Candidate（after Identity Freeze） |
| `parent_asset` | none（**not** working-tree restore of smc package） |

```text
Provisional IDs may change at Identity Freeze.
Do not mint source_hash until freeze.
Honesty: this is beyond-PA · PAAF still requires Detector purity + docs/07.
```

## 2. Preferred seed（inventory / git · not Bindable）

| Seed | Provenance | Why preferred |
|------|------------|---------------|
| **SMC Order Block（bullish）after liquidity sweep** | git `e2bfc0c…` · `strategies/smc_orderflow_vwap/smc_orderflow_vwap_strategy.py` · `_update_smc_structure` + zone long path | SAFIP I008 RECOVERABLE；≠ opp/ PA；single structure axis for first Candidate |

```text
Seed = morphology / structure hypothesis for a NEW PAAF Detector
Recovery mode intent: REWRITE_AS_PAAF_ASSET（SCIDR）
≠ WORKING_TREE_RESTORE of smc_orderflow_vwap package as-is
≠ Bindable claim from legacy hybrid
```

### Declared simplifications（at future rewrite）

```text
Scope IN:  5m · bullish Order Block after liquidity sweep
           · OB zone active（price in/near [ob_low, ob_high]）
           · LONG entry on declared confirmation（Freeze picks ONE:
             close reclaim above ob_high OR quality bullish bar in zone）
           · stop below ob_low − buffer（ticks）
Scope OUT: Setup B pure z-score path · Setup C toggle stack
           · VWAP z-score hard gate · bar-delta hard gate
           · OPP16 two-bar slow channel · scale-out / half-close
           · 60m/15m macro as entry alpha（may remain Context consumer later）
Strip:     embedded multi-strategy resonance theater
Keep defaults（legacy starting points · Freeze may narrow）:
  smc_pool_bars=12 · smc_min_bars=16 · ob_stop_buffer=2 · long-only
Explicit PatternState: IDLE → OB_SET → ZONE/SIGNAL/INVALIDATED
```

### Explicitly NOT preferred as CID_013 mainline

| Object | Reason |
|--------|--------|
| CID_003–012 assets | Alpha CLOSED · PAUSED |
| Chat-invented SMC / FVG / BOS Spec | Violates SAC |
| Full VWAP+Delta+OB triple resonance | Multi-hypothesis · deferred |
| `pa_minimal` multi-OPP restore | Bundle · not this Design |
| Silent SCAP “smc is Bindable” | Forbidden |

## 3. Research question（CID_013）

```text
Primary:
  Can a simplified SMC bullish Order-Block-after-sweep mechanism,
  rewritten as a Context-independent PAAF Detector under docs/07 costs,
  produce an auditable H_MECH AND a pre-registered H_EDGE that survives
  temporal OOS — without parameter shopping and without restoring the
  legacy VWAP/Delta hybrid as one identity?

Secondary（only after H_EDGE structure exists）:
  Multi-symbol portability · capital surface · Context consumption
```

## 4. Planned evidence order（do not skip）

```text
1) Morphology Spec（OB-long only）+ PAAF Detector rewrite + Identity Freeze
2) SEVF Spec bound to that identity
3) H_MECH EXP（auditability · one scope）
4) H_EDGE diagnostic（SAME gates as AERC CID_003–012）
5) H_EDGE OOS / multi-symbol power as needed
6) Alpha Candidate petition OR Negative Alpha close for CID_013
```

```text
FORBIDDEN order:
  Bindable / Production theater before H_EDGE
  Resume CID_003–012 as substitute for this Design
  Restore full smc hybrid “to make n large”
```

## 5. Hard boundaries

```text
❌ Resume CID_003–012 under this Design
❌ PnL optimization / grid search as Design goal
❌ Context→entry alpha inside Detector
❌ Implementation / Identity Freeze under this Design alone
❌ Claim SMC seed is already Alpha / Bindable
```

## 6. Dual-surface note

```text
Capital / scale-out controls are a later RISK surface under a new CC.
Do not merge survival KEEP into H_EDGE.
```

## 7. Inventory honesty

```text
Preferred opp/ PA shelf: EXHAUSTED · residual DT: CONSUMED.
CID_013 is the first beyond-opp NSAD under RPP Option A（smc）.
Further campaigns after this still require inventory/Spec honesty —
not chat invention.
```

## 8. Explicit non-grants

```text
❌ Identity Freeze
❌ Code implementation / working-tree restore
❌ Observation / backtest
❌ Alpha / Bindable / Production
❌ SCAP outcome change declaring smc Bindable
```

## 9. Next（须另授 · pick）

```text
Authorize Identity Freeze · SMC OB-long Detector + orchestrator @0.1.0
  — OR — leave CID_013 at Design-only
NOT: auto-implement · H_EDGE before Freeze · Resume paused · full hybrid restore
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-24 | NSAD_CID_013_V0_1 DESIGNED · smc OB-long seed · Delegation-25BC Option A |
