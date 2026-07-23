# New Strategy Asset Design — CID_007 Path

> **Type**: Strategy Asset Design（≠ Identity Freeze · ≠ Implementation · ≠ Backtest · ≠ Alpha）  
> **Status**: **DESIGNED** ✓  
> **Design ID**: `NSAD_CID_007_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AD（`授权你决定25次` · interpreted as menu **Option B**）  
> **Prior**: `CPD_CID_003`–`CPD_CID_006` PAUSED · AERC_003–006 Alpha NONE  
> **Contracts**: `SAC-v1` · `SAFIP-v1` · `SEVF-v1` · `SCIDR-v1`  
> **Data baseline（future）**: docs/07 · TQ offline · 1m · CbC · unadjusted · real costs

## Design record

```text
================================================
NSAD_CID_007_V0_1

Purpose: Open NEW strategy asset research path after
         CID_003–006 campaign Pause（all Alpha NONE）.

CID_002–006: NOT resumed · NOT reopened for H_EDGE rescue
Alpha:   NONE（new asset starts at zero hypothesis）
Code / Identity Freeze / Observation: NOT AUTHORIZED here
================================================
```

## 0. Why a new asset now

```text
Closed Alpha-NONE campaigns（all PAUSED）:
  CID_003 OPP16 two-bar · MR/exhaustion
  CID_004 OPP12 overshoot · MR/exhaustion
  CID_005 OPP17 climax · MR/exhaustion
  CID_006 OPP08 strong-breakout · trend/breakout（H_MECH KEEP · H_EDGE REVERT×2）

Lesson（compound）:
  Auditable MR and generic breakout mechanisms ≠ convertible edge.
  Next asset should change family again（session opening microstructure）,
  stay single-hypothesis + Context-independent at detect(), and plan
  H_EDGE falsification EARLY — without retuning Closed campaigns.
```

## 1. Asset slot

| Field | Design value |
|-------|----------------|
| `campaign_id` | `CID_007` |
| `working_strategy_id`（provisional） | `STRAT_SESS_OPP19_01`（pending Identity Freeze） |
| `class_tags`（provisional） | `["session","opening","breakout"]` |
| `lifecycle_start` | Candidate（after Identity Freeze） |
| `parent_asset` | none（not a fork of CID_002–006 binding bytes） |

```text
Provisional IDs may change at Identity Freeze.
Do not mint source_hash until freeze.
```

## 2. Preferred seed（inventory / git · not Bindable）

| Seed | Provenance | Why preferred |
|------|------------|---------------|
| **OPP19 Opening Drive Breakout morphology** | git `e2bfc0c…` · `strategies/pa_cta/opp/opp19.py` · `Opp19Mixin._process_opening_drive` | Session-scoped OR-range break after opening bars；family ≠ MR stack · ≠ OPP08 all-day breakout · ≠ BROOKS pullback |

```text
Seed = morphology hypothesis material for a NEW PAAF Detector
Recovery mode intent: REWRITE_AS_PAAF_ASSET（SCIDR）
≠ WORKING_TREE_RESTORE of pa_cta / pa_minimal packages
```

### Declared scope & simplifications（at future rewrite）

```text
IN SCOPE（single hypothesis）:
  Opening-drive BREAKOUT only
  — collect first N session bars → OR high/low → breakout arm

OUT OF SCOPE for @0.1.0 Candidate:
  OD_REV / opening reversal path（separate later identity if ever）
  effective_context soft bans / always_in / AFF / R² gates
  climax / tick pad / stop_cap inside Detector

Keep defaults（legacy）as Freeze starting point:
  opening_drive_bars=6 · opening_drive_min_body=0.50
  opening_drive_range_atr_min=0.2
```

### Explicitly NOT preferred as CID_007 mainline

| Object | Reason |
|--------|--------|
| OPP16 / 12 / 17 / 08 assets | CID_003–006 · Alpha CLOSED · PAUSED |
| BROOKS_SCALP_FP | CID_002 · Alpha CLOSED |
| OPP02 EMA pullback | Overlaps BROOKS continuation family |
| OPP13 / OPP15 | Higher complexity · deferred |
| Full OPP19 dual-path（breakout+rev） | Violates one-hypothesis rule at Candidate birth |
| Chat-invented session variant | Violates SAC · fabrication risk |

## 3. Research question（CID_007）

```text
Primary:
  Can an OPP19-class opening-drive breakout mechanism, rewritten as a
  Context-independent PAAF Detector under docs/07 costs, produce an
  auditable H_MECH AND a pre-registered H_EDGE that survives temporal OOS
  — without parameter shopping?

Secondary（only after H_EDGE structure exists）:
  Multi-symbol / session calendar robustness · capital surface · Context（D019）
```

## 4. Planned evidence order（do not skip）

```text
1) PAAF Detector rewrite design + Identity Freeze（new SIF · new strategy_id）
2) SEVF Spec bound to that identity
3) H_MECH EXP（auditability · one scope）
4) H_EDGE diagnostic EXP（SAME gates discipline as prior AERC）
5) H_EDGE OOS / multi-year as needed
6) Only then: Alpha Candidate petition OR Negative Alpha close for CID_007
```

```text
FORBIDDEN order:
  Bindable / Production theater before H_EDGE structure
  Resume CID_003–006 idle KEEP hunting as substitute for new edge work
  Copy prior CID parameters into OPP19 “to make it work”
```

## 5. Hard boundaries

```text
❌ Resume CID_003–006 Observations under this Design
❌ Reopen Closed H_EDGE EXPs on prior CIDs
❌ PnL optimization / grid search as Design goal
❌ Context→entry or Context→sizing alpha in detector
❌ Implementation / Identity Freeze under this Design command alone
❌ Treat pa_cta mixin as production strategy
❌ Bundle OD_REV into the same @0.1.0 identity
```

## 6. SAC readiness checklist（Design target）

| SAC field | Status in this Design |
|-----------|------------------------|
| `strategy_id` / `version` | provisional only |
| `source_manifest` + hashes | **TBD at Freeze** |
| `parameter_manifest` + hash | **TBD at Freeze**（N bars · body · range ATR · RR） |
| `market_scope` | unbound at asset · bound per EXP |
| `execution_model` | stop/target/sizing class at Freeze |
| `evidence_lineage` | empty at Candidate birth |
| `context_independence` | MUST attest（strip legacy context / always_in gates） |
| `architecture_attestation` | Detector pure · Strategy orchestrates only |

## 7. Dual-surface note

```text
Capital controls, if any, are a later RISK version/surface
under a new CC — do not merge survival KEEP into H_EDGE.
Prior CID RISK / Bindable does not transfer to CID_007.
```

## 8. Explicit non-grants

```text
❌ Identity Freeze
❌ Code implementation / working-tree restore
❌ Observation / backtest
❌ Alpha / Bindable / Production
❌ SCAP outcome change for pa_minimal / pa_cta / smc
❌ Selection of CID_007 as live strategy
```

## 9. Next（须另授 · pick）

```text
Authorize Identity Freeze · OPP19 OD-Breakout Detector + orchestrator @0.1.0
  — OR — leave CID_007 at Design-only
NOT: auto-implement · H_EDGE before Freeze · Resume paused campaigns
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | NSAD_CID_007_V0_1 DESIGNED · OPP19 OD-Breakout preferred seed · Delegation-25AD |
