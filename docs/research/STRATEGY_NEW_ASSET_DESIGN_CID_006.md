# New Strategy Asset Design — CID_006 Path

> **Type**: Strategy Asset Design（≠ Identity Freeze · ≠ Implementation · ≠ Backtest · ≠ Alpha）  
> **Status**: **DESIGNED** ✓  
> **Design ID**: `NSAD_CID_006_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25Y（`授权你决定25次` · interpreted as menu **Option B**）  
> **Prior**: `CPD_CID_003_V0_1` · `CPD_CID_004_V0_1` · `CPD_CID_005_V0_1` PAUSED · AERC_003/004/005 Alpha NONE  
> **Contracts**: `SAC-v1` · `SAFIP-v1` · `SEVF-v1` · `SCIDR-v1`  
> **Data baseline（future）**: docs/07 · TQ offline · 1m · CbC · unadjusted · real costs

## Design record

```text
================================================
NSAD_CID_006_V0_1

Purpose: Open NEW strategy asset research path after
         CID_003 + CID_004 + CID_005 campaign Pause（all Alpha NONE）.

CID_002–005: NOT resumed · NOT reopened for H_EDGE rescue
Alpha:   NONE（new asset starts at zero hypothesis）
Code / Identity Freeze / Observation: NOT AUTHORIZED here
================================================
```

## 0. Why a new asset now

```text
Closed Alpha-NONE campaigns（all PAUSED）:
  CID_003 OPP16 two-bar reversal · MR/exhaustion
  CID_004 OPP12 overshoot-fail · MR/exhaustion
  CID_005 OPP17 climax-reversal · MR/exhaustion

Lesson（compound）:
  Three auditable MR/exhaustion mechanisms ≠ convertible edge.
  Next asset should change family tag（trend/breakout）, stay
  single-hypothesis + Context-independent at detect(), and plan
  H_EDGE falsification EARLY — without retuning Closed campaigns.
```

## 1. Asset slot

| Field | Design value |
|-------|----------------|
| `campaign_id` | `CID_006` |
| `working_strategy_id`（provisional） | `STRAT_TREND_OPP08_01`（pending Identity Freeze） |
| `class_tags`（provisional） | `["trend","breakout","momentum"]` |
| `lifecycle_start` | Candidate（after Identity Freeze） |
| `parent_asset` | none（not a fork of CID_002–005 binding bytes） |

```text
Provisional IDs may change at Identity Freeze.
Do not mint source_hash until freeze.
```

## 2. Preferred seed（inventory / git · not Bindable）

| Seed | Provenance | Why preferred |
|------|------------|---------------|
| **OPP08 Strong Breakout morphology** | git `e2bfc0c…` · `strategies/pa_cta/opp/opp08.py` · `Opp08Mixin._process_strong_breakout` | Compact continuation/breakout hypothesis；family ≠ MR/exhaustion stack（OPP16/12/17）· ≠ BROOKS scalp FP pullback narrative |

```text
Seed = morphology hypothesis material for a NEW PAAF Detector
Recovery mode intent: REWRITE_AS_PAAF_ASSET（SCIDR）
≠ WORKING_TREE_RESTORE of pa_cta / pa_minimal packages
```

### Declared simplifications（at future rewrite）

```text
Strip effective_context labels（STRONG_BULL / STRONG_BEAR / BEAR_CHANNEL）
  → Context independence attestation required at Freeze
Drop BEAR_CHANNEL asymmetric branch（keep long/short breakout symmetry）
Strip climax flags / is_oo / stop_cap / tick pad from Detector
Keep: EMA side · strong-bar definition · close beyond prior extreme
Strong-bar defaults（legacy）: range ≥ atr × 1.0 · body/range ≥ 0.6
```

### Explicitly NOT preferred as CID_006 mainline

| Object | Reason |
|--------|--------|
| OPP16 / OPP12 / OPP17 assets | CID_003–005 · Alpha CLOSED · PAUSED |
| BROOKS_SCALP_FP | CID_002 · Alpha CLOSED · same broad pullback family risk |
| OPP02 EMA pullback | Overlaps continuation-with-touch narrative vs BROOKS path |
| OPP13 / OPP15 / OPP19 | Higher FSM / MTF / session complexity · deferred |
| Chat-invented breakout variant | Violates SAC · fabrication risk |

## 3. Research question（CID_006）

```text
Primary:
  Can an OPP08-class strong-breakout mechanism, rewritten as a
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
5) H_EDGE OOS / multi-year as needed for n adjudication
6) Only then: Alpha Candidate petition OR Negative Alpha close for CID_006
```

```text
FORBIDDEN order:
  Bindable / Production theater before H_EDGE structure
  Resume CID_003–005 idle KEEP hunting as substitute for new edge work
  Copy MR-campaign parameters into OPP08 “to make it work”
```

## 5. Hard boundaries

```text
❌ Resume CID_003 / CID_004 / CID_005 Observations under this Design
❌ Reopen Closed H_EDGE EXPs on prior CIDs
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
| `parameter_manifest` + hash | **TBD at Freeze**（EMA · strong_bar ATR/body · RR） |
| `market_scope` | unbound at asset · bound per EXP |
| `execution_model` | stop/target/sizing class at Freeze |
| `evidence_lineage` | empty at Candidate birth |
| `context_independence` | MUST attest（strip legacy context labels from detect()） |
| `architecture_attestation` | Detector pure · Strategy orchestrates only |

## 7. Dual-surface note

```text
Capital controls, if any, are a later RISK version/surface
under a new CC — do not merge survival KEEP into H_EDGE.
Prior CID RISK / Bindable does not transfer to CID_006.
```

## 8. Explicit non-grants

```text
❌ Identity Freeze
❌ Code implementation / working-tree restore
❌ Observation / backtest
❌ Alpha / Bindable / Production
❌ SCAP outcome change for pa_minimal / pa_cta / smc
❌ Selection of CID_006 as live strategy
```

## 9. Next（须另授 · pick）

```text
Authorize Identity Freeze · OPP08 Detector + orchestrator @0.1.0
  — OR — leave CID_006 at Design-only
NOT: auto-implement · H_EDGE before Freeze · Resume paused campaigns
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | NSAD_CID_006_V0_1 DESIGNED · OPP08 preferred seed · Delegation-25Y |
