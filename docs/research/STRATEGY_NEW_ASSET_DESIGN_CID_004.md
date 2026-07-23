# New Strategy Asset Design — CID_004 Path

> **Type**: Strategy Asset Design（≠ Identity Freeze · ≠ Implementation · ≠ Backtest · ≠ Alpha）  
> **Status**: **DESIGNED** ✓  
> **Design ID**: `NSAD_CID_004_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25N（`授权你决定25次` · interpreted as menu **Option B**）  
> **Prior**: `CPD_CID_003_V0_1` PAUSED · `CPD_CID_003_V0_1_R1` · `AERC_CID_003_V0_1` · `SCAP-v1`  
> **Contracts**: `SAC-v1` · `SAFIP-v1` · `SEVF-v1` · `SCIDR-v1`  
> **Data baseline（future）**: docs/07 · TQ offline · 1m · CbC · unadjusted · real costs

## Design record

```text
================================================
NSAD_CID_004_V0_1

Purpose: Open NEW strategy asset research path after CID_003
         campaign Pause（Alpha NONE · research stack complete）.

CID_002 / CID_003: NOT resumed · NOT reopened for H_EDGE rescue
Alpha:   NONE（new asset starts at zero hypothesis）
Code / Identity Freeze / Observation: NOT AUTHORIZED here
================================================
```

## 0. Why a new asset now

```text
CID_003 delivered:
  H_MECH Verified · RISK Verified · Research Bindable
  H_CTX_FILTER / H_CTX_RISK_COMP KEEP stacks
  H_EDGE REVERT×2 · Alpha NONE · Production WITHHELD
  Campaign PAUSED（idle KEEP / Production theater blocked）

Lesson（same as CID_002→003）:
  Auditable mechanism + Context filter activity ≠ convertible edge.
  Next asset must plan H_EDGE falsification EARLY.
```

## 1. Asset slot

| Field | Design value |
|-------|----------------|
| `campaign_id` | `CID_004` |
| `working_strategy_id`（provisional） | `STRAT_REV_OPP12_01`（pending Identity Freeze） |
| `class_tags`（provisional） | `["mean_reversion","exhaustion","overshoot"]` |
| `lifecycle_start` | Candidate（after Identity Freeze） |
| `parent_asset` | none（not a fork of CID_002/003 binding bytes） |

```text
Provisional IDs may change at Identity Freeze.
Do not mint source_hash until freeze.
```

## 2. Preferred seed（inventory / git · not Bindable）

| Seed | Provenance | Why preferred |
|------|------------|---------------|
| **OPP12 Overshoot Fail morphology** | git `e2bfc0c…` · `strategies/pa_cta/opp/opp12.py` · `Opp12Mixin._try_overshoot_fail` | Single-hypothesis extractable；mixin body has **no** `effective_context` gate；family ≠ OPP16 two-bar · ≠ Brooks scalp FP |

```text
Seed = morphology hypothesis material for a NEW PAAF Detector
Recovery mode intent: REWRITE_AS_PAAF_ASSET（SCIDR）
≠ WORKING_TREE_RESTORE of pa_cta / pa_minimal packages
≠ SCAP ADMIT of multi-OPP bundles（pa_minimal HOLD · pa_cta REJECT retained）
```

### Explicitly NOT preferred as CID_004 mainline

| Object | Reason |
|--------|--------|
| `STRAT_REV_OPP16_01` / OPP16 | CID_003 campaign · Alpha CLOSED |
| `STRAT_TREND_BROOKS_SCALP_*` / BROOKS_SCALP_FP | CID_002 Alpha CLOSED |
| `DEMO_MINIMAL` | Pipeline demo only · no research Alpha path |
| Whole `pa_cta` / `pa_minimal` strategies | SCAP REJECT / HOLD · multi-OPP · Context embedding risks |
| Chat-invented “new Brooks variant” | Violates SAC · fabrication risk |

## 3. Research question（CID_004）

```text
Primary:
  Can an OPP12-class overshoot-exhaustion mechanism, rewritten as a
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
6) Only then: Alpha Candidate petition OR Negative Alpha close for CID_004
```

```text
FORBIDDEN order:
  Bindable / Production theater before H_EDGE structure
  Resume CID_003 idle Context multi-symbol as substitute for new edge work
```

## 5. Hard boundaries

```text
❌ Resume CID_003 Observations under this Design
❌ Reopen Closed H_EDGE EXPs on CID_002 / CID_003
❌ Copy CID_003 parameters into OPP12 “to make it work”
❌ PnL optimization / grid search as Design goal
❌ Context→entry or Context→sizing alpha in detector
❌ Implementation / Identity Freeze under this Design command alone
❌ Treat pa_cta mixin as production strategy
```

## 6. SAC readiness checklist（Design target）

| SAC field | Status in this Design |
|-----------|------------------------|
| `strategy_id` / `version` | provisional only |
| `source_manifest` + hashes | **TBD at Freeze**（new detector + orchestrator files） |
| `parameter_manifest` + hash | **TBD at Freeze**（declare ATR multiples · confirm style） |
| `market_scope` | unbound at asset · bound per EXP |
| `execution_model` | stop/target/sizing class at Freeze |
| `evidence_lineage` | empty at Candidate birth |
| `context_independence` | MUST attest（OPP12 mixin extract is Context-free；do not re-add legacy channel gates into detect()） |
| `architecture_attestation` | Detector pure · Strategy orchestrates only |

## 7. Dual-surface note

```text
Capital controls, if any, are a later RISK version/surface
under a new CC — do not merge survival KEEP into H_EDGE.
CID_003 RISK Verified does not transfer to CID_004.
```

## 8. Explicit non-grants

```text
❌ Identity Freeze
❌ Code implementation / working-tree restore
❌ Observation / backtest
❌ Alpha / Bindable / Production
❌ SCAP outcome change for pa_minimal / pa_cta / smc
❌ Selection of CID_004 as live strategy
```

## 9. Next（须另授 · pick）

```text
DONE: Identity Freeze · OPP12 Detector + orchestrator @0.1.0（Delegation-25O）
Next: Authorize SEVF Spec + Fill for STRAT_RO12_EXP001（H_MECH）
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | NSAD_CID_004_V0_1 DESIGNED · OPP12 preferred seed · Delegation-25N |
| 2026-07-23 | Identity FROZEN · STRAT_REV_OPP12_01@0.1.0 · Delegation-25O |
