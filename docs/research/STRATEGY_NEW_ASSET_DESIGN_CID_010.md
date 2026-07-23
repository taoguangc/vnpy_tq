# New Strategy Asset Design — CID_010 Path

> **Type**: Strategy Asset Design（≠ Identity Freeze · ≠ Implementation · ≠ Backtest · ≠ Alpha）  
> **Status**: **DESIGNED** ✓  
> **Design ID**: `NSAD_CID_010_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AO（`授权你决定25次` · interpreted as menu **Option B**）  
> **Prior**: `CPD_CID_003`–`CPD_CID_009` PAUSED · AERC_003–009 Alpha NONE  
> **Contracts**: `SAC-v1` · `SAFIP-v1` · `SEVF-v1` · `SCIDR-v1`  
> **Data baseline（future）**: docs/07 · TQ offline · 1m · CbC · unadjusted · real costs

## Design record

```text
================================================
NSAD_CID_010_V0_1

Purpose: Open NEW strategy asset research path after
         CID_003–009 campaign Pause（all Alpha NONE）.

CID_002–009: NOT resumed · NOT reopened for H_EDGE rescue
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
  CID_009      wedge Path-A exhaustion（OPP15）

Lesson（compound）:
  Seven auditable mechanisms across MR, breakout, session, pullback,
  and wedge families failed the same frozen H_EDGE gates.
  Remaining legacy opp/ mainline seed: OPP13 day-boundary single-touch
  fail（deferred earlier as MR-adjacent; now last shelf item before OD_REV）.
  Distinct axis: calendar day high/low structure ≠ session OR（OPP19）
  ≠ multi-pivot wedge（OPP15）≠ single-bar climax（OPP17）.
```

## 1. Asset slot

| Field | Design value |
|-------|----------------|
| `campaign_id` | `CID_010` |
| `working_strategy_id`（provisional） | `STRAT_REV_OPP13_01`（pending Identity Freeze） |
| `class_tags`（provisional） | `["mean_reversion","day_boundary","range_fail"]` |
| `lifecycle_start` | Candidate（after Identity Freeze） |
| `parent_asset` | none（not a fork of CID_002–009 binding bytes） |

```text
Provisional IDs may change at Identity Freeze.
Do not mint source_hash until freeze.
Honesty: class_tags include mean_reversion after MR×3 Alpha NONE —
  this is NOT a reason to skip H_EDGE; it is a reason to falsify EARLY.
```

## 2. Preferred seed（inventory / git · not Bindable）

| Seed | Provenance | Why preferred |
|------|------------|---------------|
| **OPP13 day-boundary single-touch** | git `e2bfc0c…` · `strategies/pa_cta/opp/opp13.py` · 日高/日低单触反转 | Last compact legacy mainline seed；day-structure axis；≠ OPP19 OD · ≠ OPP15 wedge |

```text
Seed = morphology hypothesis material for a NEW PAAF Detector
Recovery mode intent: REWRITE_AS_PAAF_ASSET（SCIDR）
≠ WORKING_TREE_RESTORE of pa_cta / pa_minimal packages
```

### Declared simplifications（at future rewrite）

```text
Scope IN:  5m · single-touch day-high short / day-low long
           · upper/lower shadow ≥ 0.4 × range · directional close
Scope OUT: day_high double-top / FIRST_TEST FSM path
           · opp13 volume filter stack · climax volume
Strip:     always_in · market_context · late_phase · pd_blocks · is_oo
Keep:      day_boundary_tolerance（ticks）· explicit day_high/day_low state
Defaults（legacy）: day_boundary_tolerance=5.0（× pricetick）
Day levels: PatternState / Strategy-injected session-day OHLC（no hidden globals）
```

### Explicitly NOT preferred as CID_010 mainline

| Object | Reason |
|--------|--------|
| OPP16/12/17/08/19/02/15 assets | CID_003–009 · Alpha CLOSED · PAUSED |
| BROOKS_SCALP_FP | CID_002 · Alpha CLOSED |
| OPP13 double-top / FIRST_TEST path | Separate hypothesis · not this campaign |
| OPP19 OD_REV | Separate identity if ever · not this Design |
| Chat-invented day-boundary variant | Violates SAC · fabrication risk |

## 3. Research question（CID_010）

```text
Primary:
  Can an OPP13-class day-boundary single-touch fail mechanism, rewritten as a
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
4) H_EDGE diagnostic EXP（SAME gates as AERC CID_003–009）
5) H_EDGE OOS as needed
6) Only then: Alpha Candidate petition OR Negative Alpha close for CID_010
```

```text
FORBIDDEN order:
  Bindable / Production theater before H_EDGE structure
  Resume CID_003–009 idle KEEP hunting as substitute for new edge work
  Copy prior CID parameters into OPP13 “to make it work”
  Expand double-top path under the same experiment_id
```

## 5. Hard boundaries

```text
❌ Resume CID_003–009 Observations under this Design
❌ Reopen Closed H_EDGE EXPs on prior CIDs
❌ PnL optimization / grid search as Design goal
❌ Context→entry or Context→sizing alpha in detector
❌ Implementation / Identity Freeze under this Design command alone
❌ Treat pa_cta mixin as production strategy
❌ Claim OPP13 is OPP19 / OPP15 rewrite
```

## 6. SAC readiness checklist（Design target）

| SAC field | Status in this Design |
|-----------|------------------------|
| `strategy_id` / `version` | provisional only |
| `source_manifest` + hashes | **TBD at Freeze** |
| `parameter_manifest` + hash | **TBD at Freeze**（tolerance · shadow · RR） |
| `market_scope` | unbound at asset · bound per EXP |
| `execution_model` | stop/target/sizing class at Freeze |
| `evidence_lineage` | empty at Candidate birth |
| `context_independence` | MUST attest（strip always_in / context / late） |
| `architecture_attestation` | Detector pure · Strategy orchestrates only |

## 7. Dual-surface note

```text
Capital controls, if any, are a later RISK version/surface
under a new CC — do not merge survival KEEP into H_EDGE.
Prior CID RISK / Bindable does not transfer to CID_010.
```

## 8. Inventory honesty

```text
After CID_010 consumes OPP13 single-touch, legacy opp/ mainline shelf is
exhausted for preferred seeds. Remaining: OPP19 OD_REV（if authorized as
new identity）or new morphology Spec（not chat invention）or scoped Resume
of paused H_MECH surfaces — not Alpha theater.
```

## 9. Explicit non-grants

```text
❌ Identity Freeze
❌ Code implementation / working-tree restore
❌ Observation / backtest
❌ Alpha / Bindable / Production
❌ SCAP outcome change for pa_minimal / pa_cta / smc
❌ Selection of CID_010 as live strategy
```

## 10. Next（须另授 · pick）

```text
Authorize Identity Freeze · OPP13 single-touch Detector + orchestrator @0.1.0
  — OR — leave CID_010 at Design-only
NOT: auto-implement · H_EDGE before Freeze · Resume paused campaigns
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | NSAD_CID_010_V0_1 DESIGNED · OPP13 single-touch preferred · Delegation-25AO |
