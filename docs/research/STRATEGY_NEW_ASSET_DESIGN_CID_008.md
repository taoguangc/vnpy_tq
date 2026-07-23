# New Strategy Asset Design — CID_008 Path

> **Type**: Strategy Asset Design（≠ Identity Freeze · ≠ Implementation · ≠ Backtest · ≠ Alpha）  
> **Status**: **DESIGNED** ✓  
> **Design ID**: `NSAD_CID_008_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AI（`授权你决定25次` · interpreted as menu **Option B**）  
> **Prior**: `CPD_CID_003`–`CPD_CID_007` PAUSED · AERC_003–007 Alpha NONE  
> **Contracts**: `SAC-v1` · `SAFIP-v1` · `SEVF-v1` · `SCIDR-v1`  
> **Data baseline（future）**: docs/07 · TQ offline · 1m · CbC · unadjusted · real costs

## Design record

```text
================================================
NSAD_CID_008_V0_1

Purpose: Open NEW strategy asset research path after
         CID_003–007 campaign Pause（all Alpha NONE）.

CID_002–007: NOT resumed · NOT reopened for H_EDGE rescue
Alpha:   NONE（new asset starts at zero hypothesis）
Code / Identity Freeze / Observation: NOT AUTHORIZED here
================================================
```

## 0. Why a new asset now

```text
Closed Alpha-NONE campaigns（all PAUSED）:
  CID_003–005  MR / exhaustion（OPP16/12/17）
  CID_006      all-session strong breakout（OPP08）
  CID_007      session opening-drive breakout（OPP19）

Lesson（compound）:
  Auditable mechanisms across MR, breakout, and session families
  still failed H_EDGE screens.
  Next asset: EMA pullback continuation（trend-with-touch）,
  distinct from OPP08 breakout and BROOKS first-pullback FSM,
  Context-independent at detect(), H_EDGE falsification EARLY.
```

## 1. Asset slot

| Field | Design value |
|-------|----------------|
| `campaign_id` | `CID_008` |
| `working_strategy_id`（provisional） | `STRAT_TREND_OPP02_01`（pending Identity Freeze） |
| `class_tags`（provisional） | `["trend","pullback","ema"]` |
| `lifecycle_start` | Candidate（after Identity Freeze） |
| `parent_asset` | none（not a fork of CID_002–007 binding bytes） |

```text
Provisional IDs may change at Identity Freeze.
Do not mint source_hash until freeze.
```

## 2. Preferred seed（inventory / git · not Bindable）

| Seed | Provenance | Why preferred |
|------|------------|---------------|
| **OPP02 EMA Pullback morphology** | git `e2bfc0c…` · `strategies/pa_cta/opp/opp02.py` · `Opp02Mixin._process_ema_pullback` | Compact continuation-after-EMA-touch；≠ OPP08 breakout · ≠ OPP19 session OR · ≠ BROOKS multi-state first-pullback FSM |

```text
Seed = morphology hypothesis material for a NEW PAAF Detector
Recovery mode intent: REWRITE_AS_PAAF_ASSET（SCIDR）
≠ WORKING_TREE_RESTORE of pa_cta / pa_minimal packages
```

### Declared simplifications（at future rewrite）

```text
Strip always_in LONG/SHORT gate
  → replace with explicit EMA-side proxy（close vs EMA）declared at Freeze
Strip AFF / R² gates · pd_blocks · is_oo · stop_cap · tick pad · pending-confirm
Keep: EMA touch band（atr × touch）· min body ratio · upper/lower wick bound
Defaults（legacy）: ema_pullback_touch_atr=1.0 · ema_pullback_min_body_ratio=0.35
                   ema_period=20 · atr_period=14
```

### Explicit differentiation vs BROOKS_SCALP_FP

```text
BROOKS: multi-bar trend-leg → pullback FSM → stop beyond pullback extreme
OPP02:  single completed bar · EMA touch + directional body · no trend-leg FSM
≠ same identity · ≠ parameter transfer
```

### Explicitly NOT preferred as CID_008 mainline

| Object | Reason |
|--------|--------|
| OPP16/12/17/08/19 assets | CID_003–007 · Alpha CLOSED · PAUSED |
| BROOKS_SCALP_FP | CID_002 · Alpha CLOSED · different FSM |
| OPP13 / OPP15 | Higher complexity · deferred |
| OPP19 OD_REV | Separate hypothesis · not this campaign |
| Chat-invented EMA variant | Violates SAC · fabrication risk |

## 3. Research question（CID_008）

```text
Primary:
  Can an OPP02-class EMA-pullback continuation mechanism, rewritten as a
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
5) H_EDGE OOS as needed
6) Only then: Alpha Candidate petition OR Negative Alpha close for CID_008
```

```text
FORBIDDEN order:
  Bindable / Production theater before H_EDGE structure
  Resume CID_003–007 idle KEEP hunting as substitute for new edge work
  Copy prior CID / BROOKS parameters into OPP02 “to make it work”
```

## 5. Hard boundaries

```text
❌ Resume CID_003–007 Observations under this Design
❌ Reopen Closed H_EDGE EXPs on prior CIDs
❌ PnL optimization / grid search as Design goal
❌ Context→entry or Context→sizing alpha in detector
❌ Implementation / Identity Freeze under this Design command alone
❌ Treat pa_cta mixin as production strategy
❌ Claim OPP02 is BROOKS_SCALP rewrite
```

## 6. SAC readiness checklist（Design target）

| SAC field | Status in this Design |
|-----------|------------------------|
| `strategy_id` / `version` | provisional only |
| `source_manifest` + hashes | **TBD at Freeze** |
| `parameter_manifest` + hash | **TBD at Freeze**（EMA · touch ATR · body ratio · RR） |
| `market_scope` | unbound at asset · bound per EXP |
| `execution_model` | stop/target/sizing class at Freeze |
| `evidence_lineage` | empty at Candidate birth |
| `context_independence` | MUST attest（strip always_in / AFF / R²） |
| `architecture_attestation` | Detector pure · Strategy orchestrates only |

## 7. Dual-surface note

```text
Capital controls, if any, are a later RISK version/surface
under a new CC — do not merge survival KEEP into H_EDGE.
Prior CID RISK / Bindable does not transfer to CID_008.
```

## 8. Explicit non-grants

```text
❌ Identity Freeze
❌ Code implementation / working-tree restore
❌ Observation / backtest
❌ Alpha / Bindable / Production
❌ SCAP outcome change for pa_minimal / pa_cta / smc
❌ Selection of CID_008 as live strategy
```

## 9. Next（须另授 · pick）

```text
Authorize Identity Freeze · OPP02 Detector + orchestrator @0.1.0
  — OR — leave CID_008 at Design-only
NOT: auto-implement · H_EDGE before Freeze · Resume paused campaigns
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | NSAD_CID_008_V0_1 DESIGNED · OPP02 preferred seed · Delegation-25AI |
