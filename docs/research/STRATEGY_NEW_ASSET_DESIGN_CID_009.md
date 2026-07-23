# New Strategy Asset Design — CID_009 Path

> **Type**: Strategy Asset Design（≠ Identity Freeze · ≠ Implementation · ≠ Backtest · ≠ Alpha）  
> **Status**: **DESIGNED** ✓  
> **Design ID**: `NSAD_CID_009_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AL（`授权你决定25次` · interpreted as menu **Option B**）  
> **Prior**: `CPD_CID_003`–`CPD_CID_008` PAUSED · AERC_003–008 Alpha NONE  
> **Contracts**: `SAC-v1` · `SAFIP-v1` · `SEVF-v1` · `SCIDR-v1`  
> **Data baseline（future）**: docs/07 · TQ offline · 1m · CbC · unadjusted · real costs

## Design record

```text
================================================
NSAD_CID_009_V0_1

Purpose: Open NEW strategy asset research path after
         CID_003–008 campaign Pause（all Alpha NONE）.

CID_002–008: NOT resumed · NOT reopened for H_EDGE rescue
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
  CID_008      EMA pullback continuation（OPP02）

Lesson（compound）:
  Auditable mechanisms across MR, breakout, session, and EMA-pullback
  still failed the same frozen H_EDGE gates.
  Next asset: multi-pivot WEDGE exhaustion（OPP15 Path A only）,
  morphologically distinct from single-bar climax（OPP17）and from
  day-boundary range-fail（OPP13 deferred）, Context-independent at
  detect(), H_EDGE falsification EARLY.
```

## 1. Asset slot

| Field | Design value |
|-------|----------------|
| `campaign_id` | `CID_009` |
| `working_strategy_id`（provisional） | `STRAT_REV_OPP15_01`（pending Identity Freeze） |
| `class_tags`（provisional） | `["exhaustion","wedge","reversal"]` |
| `lifecycle_start` | Candidate（after Identity Freeze） |
| `parent_asset` | none（not a fork of CID_002–008 binding bytes） |

```text
Provisional IDs may change at Identity Freeze.
Do not mint source_hash until freeze.
```

## 2. Preferred seed（inventory / git · not Bindable）

| Seed | Provenance | Why preferred |
|------|------------|---------------|
| **OPP15 Wedge Path A** | git `e2bfc0c…` · `strategies/pa_cta/opp/opp15.py` · HH3/LL3 arm → strong-bar reverse break | Multi-pivot exhaustion geometry；≠ OPP17 climax bar · ≠ OPP13 day-boundary · ≠ OPP08/19 breakout |

```text
Seed = morphology hypothesis material for a NEW PAAF Detector
Recovery mode intent: REWRITE_AS_PAAF_ASSET（SCIDR）
≠ WORKING_TREE_RESTORE of pa_cta / pa_minimal packages
```

### Declared simplifications（at future rewrite）

```text
Scope IN:  5m wedge scan · Path A only（strong bar reverse through trigger_line）
Scope OUT: MTF 15m exhaustion zone · Path B' alpha-decay · direct-entry gate stack
Strip:     always_in / market_context / pd_blocks / tick pad / stop_cap / AFF
Keep defaults（legacy）: wedge_n_min_5m=3 · wedge_alpha_threshold=0.85
Explicit PatternState FSM: IDLE → ARMED → SIGNAL/RESET（serialize pivots + arm_time）
Complexity budget: wedge scanner must be pure / auditable; no ML
```

### Explicitly NOT preferred as CID_009 mainline

| Object | Reason |
|--------|--------|
| OPP16/12/17/08/19/02 assets | CID_003–008 · Alpha CLOSED · PAUSED |
| BROOKS_SCALP_FP | CID_002 · Alpha CLOSED · different FSM |
| OPP13 day-boundary | Still range-fail / MR-adjacent after MR×3 · deferred |
| OPP15 Path B' / MTF | Extra hypothesis surface · not this campaign |
| Chat-invented wedge variant | Violates SAC · fabrication risk |

## 3. Research question（CID_009）

```text
Primary:
  Can an OPP15-class 5m wedge Path-A reversal mechanism, rewritten as a
  Context-independent PAAF Detector under docs/07 costs, produce an
  auditable H_MECH AND a pre-registered H_EDGE that survives temporal OOS
  — without parameter shopping?

Secondary（only after H_EDGE structure exists）:
  Multi-symbol portability · capital surface · Context consumption（Decision 019）
```

## 4. Planned evidence order（do not skip）

```text
1) Morphology Spec + PAAF Detector rewrite + Identity Freeze
2) SEVF Spec bound to that identity
3) H_MECH EXP（auditability · one scope）
4) H_EDGE diagnostic EXP（SAME gates as AERC CID_003–008）
5) H_EDGE OOS as needed
6) Only then: Alpha Candidate petition OR Negative Alpha close for CID_009
```

```text
FORBIDDEN order:
  Bindable / Production theater before H_EDGE structure
  Resume CID_003–008 idle KEEP hunting as substitute for new edge work
  Copy prior CID parameters into OPP15 “to make it work”
  Expand to Path B'/MTF under the same experiment_id
```

## 5. Hard boundaries

```text
❌ Resume CID_003–008 Observations under this Design
❌ Reopen Closed H_EDGE EXPs on prior CIDs
❌ PnL optimization / grid search as Design goal
❌ Context→entry or Context→sizing alpha in detector
❌ Implementation / Identity Freeze under this Design command alone
❌ Treat pa_cta mixin as production strategy
❌ Claim OPP15 Path A is OPP17 climax rewrite
```

## 6. SAC readiness checklist（Design target）

| SAC field | Status in this Design |
|-----------|------------------------|
| `strategy_id` / `version` | provisional only |
| `source_manifest` + hashes | **TBD at Freeze** |
| `parameter_manifest` + hash | **TBD at Freeze**（n_min · alpha · strong-bar · RR） |
| `market_scope` | unbound at asset · bound per EXP |
| `execution_model` | stop/target/sizing class at Freeze |
| `evidence_lineage` | empty at Candidate birth |
| `context_independence` | MUST attest（strip always_in / context gates） |
| `architecture_attestation` | Detector pure · Strategy orchestrates only |

## 7. Dual-surface note

```text
Capital controls, if any, are a later RISK version/surface
under a new CC — do not merge survival KEEP into H_EDGE.
Prior CID RISK / Bindable does not transfer to CID_009.
```

## 8. Inventory honesty

```text
After CID_009 consumes OPP15 Path A, remaining legacy opp/ mainline seeds
are thin: OPP13（deferred）· OPP19 OD_REV（separate identity if ever）.
Further NSAD may require new morphology Spec（not chat invention）
or scoped Resume of paused H_MECH surfaces — not Alpha theater.
```

## 9. Explicit non-grants

```text
❌ Identity Freeze
❌ Code implementation / working-tree restore
❌ Observation / backtest
❌ Alpha / Bindable / Production
❌ SCAP outcome change for pa_minimal / pa_cta / smc
❌ Selection of CID_009 as live strategy
```

## 10. Next（须另授 · pick）

```text
Authorize Identity Freeze · OPP15 Path-A Detector + orchestrator @0.1.0
  — OR — leave CID_009 at Design-only
NOT: auto-implement · H_EDGE before Freeze · Resume paused campaigns
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | NSAD_CID_009_V0_1 DESIGNED · OPP15 Path A preferred · Delegation-25AL |
