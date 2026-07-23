# New Strategy Asset Design — CID_005 Path

> **Type**: Strategy Asset Design（≠ Identity Freeze · ≠ Implementation · ≠ Backtest · ≠ Alpha）  
> **Status**: **DESIGNED** ✓  
> **Design ID**: `NSAD_CID_005_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25S（`授权你决定25次` · interpreted as menu **Option B**）  
> **Prior**: `CPD_CID_003_V0_1` PAUSED · `CPD_CID_004_V0_1` PAUSED · `AERC_CID_003_V0_1` · `AERC_CID_004_V0_1`  
> **Contracts**: `SAC-v1` · `SAFIP-v1` · `SEVF-v1` · `SCIDR-v1`  
> **Data baseline（future）**: docs/07 · TQ offline · 1m · CbC · unadjusted · real costs

## Design record

```text
================================================
NSAD_CID_005_V0_1

Purpose: Open NEW strategy asset research path after
         CID_003 + CID_004 campaign Pause（both Alpha NONE）.

CID_002 / CID_003 / CID_004: NOT resumed · NOT reopened for H_EDGE rescue
Alpha:   NONE（new asset starts at zero hypothesis）
Code / Identity Freeze / Observation: NOT AUTHORIZED here
================================================
```

## 0. Why a new asset now

```text
CID_003 delivered:
  OPP16 MECH+RISK Research Bindable · H_EDGE REVERT×2 · Alpha NONE · PAUSED

CID_004 delivered:
  OPP12 H_MECH KEEP · H_EDGE REVERT×2 · Alpha NONE · PAUSED

Lesson（compound）:
  Auditable mechanism ≠ convertible edge.
  Exhaustion / overshoot families failed H_EDGE early screens twice.
  Next asset must stay single-hypothesis, Context-independent at detect(),
  and plan H_EDGE falsification EARLY — without retuning Closed campaigns.
```

## 1. Asset slot

| Field | Design value |
|-------|----------------|
| `campaign_id` | `CID_005` |
| `working_strategy_id`（provisional） | `STRAT_REV_OPP17_01`（pending Identity Freeze） |
| `class_tags`（provisional） | `["mean_reversion","climax","exhaustion"]` |
| `lifecycle_start` | Candidate（after Identity Freeze） |
| `parent_asset` | none（not a fork of CID_002/003/004 binding bytes） |

```text
Provisional IDs may change at Identity Freeze.
Do not mint source_hash until freeze.
```

## 2. Preferred seed（inventory / git · not Bindable）

| Seed | Provenance | Why preferred |
|------|------------|---------------|
| **OPP17 Climax Reversal morphology** | git `e2bfc0c…` · `strategies/pa_cta/opp/opp17.py` · `Opp17Mixin._process_climax_reversal` | Compact single-hypothesis：prior bar range climax + next-bar mid reclaim；family ≠ OPP16 two-bar · ≠ OPP12 overshoot-fail · ≠ BROOKS scalp FP |

```text
Seed = morphology hypothesis material for a NEW PAAF Detector
Recovery mode intent: REWRITE_AS_PAAF_ASSET（SCIDR）
≠ WORKING_TREE_RESTORE of pa_cta / pa_minimal packages
≠ SCAP ADMIT of multi-OPP bundles
```

### Declared simplifications（at future rewrite）

```text
Strip legacy effective_context allow-list from detect()
  → Context independence attestation required at Freeze
Strip pending-confirm / stop-cap / pd_blocks from Detector
  → Strategy / Risk own execution geometry
Keep: prior-bar range vs ATR gate · mid reclaim · long/short symmetry
```

### Explicitly NOT preferred as CID_005 mainline

| Object | Reason |
|--------|--------|
| `STRAT_REV_OPP16_01` / OPP16 | CID_003 · Alpha CLOSED · PAUSED |
| `STRAT_REV_OPP12_01` / OPP12 | CID_004 · Alpha CLOSED · PAUSED |
| `STRAT_TREND_BROOKS_SCALP_*` | CID_002 · Alpha CLOSED |
| OPP02 EMA pullback | Overlaps continuation / pullback family with BROOKS path |
| OPP08 strong breakout | Heavy `effective_context` embedding · not clean extract |
| OPP13 day-boundary | Multi-path FSM + day state · high complexity budget |
| OPP15 wedge | Multi-TF scan + arm FSM · deferred |
| OPP19 opening drive | Session FSM · deferred |
| `DEMO_MINIMAL` | Pipeline demo only |
| Chat-invented “new Brooks variant” | Violates SAC · fabrication risk |

## 3. Research question（CID_005）

```text
Primary:
  Can an OPP17-class climax-reversal mechanism, rewritten as a
  Context-independent PAAF Detector under docs/07 costs, produce an
  auditable H_MECH AND a pre-registered H_EDGE that survives temporal OOS
  — without parameter shopping?

Secondary（only after H_EDGE structure exists）:
  Multi-symbol portability · capital surface · Context consumption（Decision 019）
```

## 4. Planned evidence order（do not skip）

```text
1) PAAF Detector rewrite design + Identity Freeze（new SIF · new strategy_id）
2) SEVF Spec bound to that identity
3) H_MECH EXP（auditability · one scope）
4) H_EDGE diagnostic EXP（SAME gates discipline as prior AERC）
5) H_EDGE OOS EXP（temporal · not rescue）
6) Only then: Alpha Candidate petition OR Negative Alpha close for CID_005
```

```text
FORBIDDEN order:
  Bindable / Production theater before H_EDGE structure
  Resume CID_003/004 idle KEEP hunting as substitute for new edge work
  Copy OPP12/OPP16 parameters into OPP17 “to make it work”
```

## 5. Hard boundaries

```text
❌ Resume CID_003 / CID_004 Observations under this Design
❌ Reopen Closed H_EDGE EXPs on CID_002 / CID_003 / CID_004
❌ PnL optimization / grid search as Design goal
❌ Context→entry or Context→sizing alpha in detector
❌ Implementation / Identity Freeze under this Design command alone
❌ Treat pa_cta mixin as production strategy
```

## 6. SAC readiness checklist（Design target）

| SAC field | Status in this Design |
|-----------|------------------------|
| `strategy_id` / `version` | provisional only |
| `source_manifest` + hashes | **TBD at Freeze** |
| `parameter_manifest` + hash | **TBD at Freeze**（declare climax range ATR · mid reclaim） |
| `market_scope` | unbound at asset · bound per EXP |
| `execution_model` | stop/target/sizing class at Freeze |
| `evidence_lineage` | empty at Candidate birth |
| `context_independence` | MUST attest（strip legacy context allow-list from detect()） |
| `architecture_attestation` | Detector pure · Strategy orchestrates only |

## 7. Dual-surface note

```text
Capital controls, if any, are a later RISK version/surface
under a new CC — do not merge survival KEEP into H_EDGE.
Prior CID RISK / Bindable does not transfer to CID_005.
```

## 8. Explicit non-grants

```text
❌ Identity Freeze
❌ Code implementation / working-tree restore
❌ Observation / backtest
❌ Alpha / Bindable / Production
❌ SCAP outcome change for pa_minimal / pa_cta / smc
❌ Selection of CID_005 as live strategy
```

## 9. Next（须另授 · pick）

```text
DONE: Identity Freeze · OPP17 Detector + orchestrator @0.1.0（Delegation-25T）
Next: Authorize SEVF Spec + Fill for STRAT_RO17_EXP001（H_MECH）
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | NSAD_CID_005_V0_1 DESIGNED · OPP17 preferred seed · Delegation-25S |
| 2026-07-23 | Identity FROZEN · STRAT_REV_OPP17_01@0.1.0 · Delegation-25T |
