# New Strategy Asset Design — CID_012 Path

> **Type**: Strategy Asset Design（≠ Identity Freeze · ≠ Implementation · ≠ Backtest · ≠ Alpha）  
> **Status**: **DESIGNED** ✓  
> **Design ID**: `NSAD_CID_012_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AU（`授权你决定25次` · interpreted as menu **Option B**）  
> **Prior**: `CPD_CID_003`–`CPD_CID_011` PAUSED · AERC_003–011 Alpha NONE  
> **Contracts**: `SAC-v1` · `SAFIP-v1` · `SEVF-v1` · `SCIDR-v1`  
> **Data baseline（future）**: docs/07 · TQ offline · 1m · CbC · unadjusted · real costs

## Design record

```text
================================================
NSAD_CID_012_V0_1

Purpose: Open NEW strategy asset research path after
         CID_003–011 campaign Pause（all Alpha NONE）.

CID_002–011: NOT resumed · NOT reopened for H_EDGE rescue
Alpha:   NONE（new asset starts at zero hypothesis）
Code / Identity Freeze / Observation: NOT AUTHORIZED here
================================================
```

## 0. Why a new asset now

```text
Closed Alpha-NONE campaigns（all PAUSED）:
  CID_003–005  MR / exhaustion（OPP16/12/17）
  CID_006      all-session strong breakout（OPP08）
  CID_007      session opening-drive BREAKOUT（OPP19）
  CID_008      EMA pullback continuation（OPP02）
  CID_009      wedge Path-A（OPP15）
  CID_010      day-boundary SINGLE-TOUCH（OPP13 Path A · H_EDGE HOLD×2）
  CID_011      session opening-drive REVERSAL（OPP19 OD_REV）

Lesson（compound）:
  Nine auditable mechanisms failed frozen H_EDGE gates（or could not clear MIN_N）.
  Preferred e2bfc0c strategies/pa_cta/opp/ mainline shelf is EXHAUSTED.
  CID_010 NSAD explicitly deferred day_high double-top / FIRST_TEST as a
  separate hypothesis — that residual is the last pre-declared PA git seed
  before true beyond-opp Spec or non-PA recovery（smc）would be required.
```

## 1. Asset slot

| Field | Design value |
|-------|----------------|
| `campaign_id` | `CID_012` |
| `working_strategy_id`（provisional） | `STRAT_REV_OPP13_DT_01`（pending Identity Freeze） |
| `class_tags`（provisional） | `["mean_reversion","day_boundary","double_top"]` |
| `lifecycle_start` | Candidate（after Identity Freeze） |
| `parent_asset` | none（**not** a fork of `STRAT_REV_OPP13_01` / CID_010 binding bytes） |

```text
Provisional IDs may change at Identity Freeze.
Do not mint source_hash until freeze.
Explicit: ≠ CID_010 parameter transfer · ≠ single-touch reopen · ≠ rescue H_EDGE HOLD
```

## 2. Preferred seed（inventory / git · not Bindable）

| Seed | Provenance | Why preferred |
|------|------------|---------------|
| **OPP13 day-high double-top / FIRST_TEST** | git `e2bfc0c…` · `strategies/pa_cta/opp/opp13.py` · `_try_day_high_double_top` | Pre-declared residual after preferred shelf exhaustion；two-touch LH fail ≠ CID_010 single-touch |

```text
Seed = morphology hypothesis material for a NEW PAAF Detector
Recovery mode intent: REWRITE_AS_PAAF_ASSET（SCIDR）
≠ WORKING_TREE_RESTORE of pa_cta / pa_minimal packages
≠ Expand double-top under SIF_CID_010 / Closed EXP ids
```

### Declared simplifications（at future rewrite）

```text
Scope IN:  5m · day-high FIRST_TEST → second LH test · quality short bar
           · explicit PatternState FSM: IDLE → FIRST_TEST → SIGNAL/RESET
Scope OUT: day-boundary single-touch Path A（already CID_010 · Alpha CLOSED）
           · day-low mirror（unless declared at Freeze as separate Spec）
           · opp13 volume filter stack · climax volume
Strip:     always_in · market_context / effective_context · late_phase · pd_blocks · is_oo
Keep:      day_high_touch_tol · lh_max_drop · day_high_second_test_max_bars
           · quality day-high short bar gate（extracted morphology helper）
Day levels: PatternState / Strategy-injected session-day OHLC（no hidden globals）
```

### Explicit differentiation vs CID_010

```text
CID_010: single completed bar · touch day high/low + shadow/close gates
CID_012: multi-bar FSM · first touch arms FIRST_TEST · second LH + quality bar arms entry
≠ same identity · ≠ parameter transfer · ≠ HOLD rescue
```

### Explicitly NOT preferred as CID_012 mainline

| Object | Reason |
|--------|--------|
| CID_003–011 assets | Alpha CLOSED · PAUSED |
| CID_010 single-touch identity | Separate freeze · do not merge / rescue |
| OPP16/12/17/08/02/15/19 rewrite | Consumed |
| Chat-invented double-top / Spec | Violates SAC · fabrication risk |
| `smc_orderflow_vwap` / `pa_minimal` | Beyond-PA hybrid or multi-OPP bundle · deferred unless user rejects DT |
| Scoped Resume of HOLD surfaces | Separate wake · not this Design |

## 3. Research question（CID_012）

```text
Primary:
  Can an OPP13-class day-high double-top / FIRST_TEST mechanism, rewritten as a
  Context-independent PAAF Detector under docs/07 costs, produce an
  auditable H_MECH AND a pre-registered H_EDGE that survives temporal OOS
  — without parameter shopping and without borrowing CID_010 bytes?

Secondary（only after H_EDGE structure exists）:
  Multi-symbol portability · capital surface · Context consumption（Decision 019）
```

## 4. Planned evidence order（do not skip）

```text
1) Morphology Spec（double-top only）+ PAAF Detector rewrite + Identity Freeze
2) SEVF Spec bound to that identity
3) H_MECH EXP（auditability · one scope）
4) H_EDGE diagnostic EXP（SAME gates as AERC CID_003–011）
5) H_EDGE OOS / multi-symbol power as needed（esp. if low-n HOLD risk）
6) Only then: Alpha Candidate petition OR Negative Alpha close for CID_012
```

```text
FORBIDDEN order:
  Bindable / Production theater before H_EDGE structure
  Resume CID_003–011 idle KEEP hunting as substitute
  Copy CID_010 single-touch parameters into double-top “to make it work”
  Bundle single-touch + double-top under one strategy_id
```

## 5. Hard boundaries

```text
❌ Resume CID_003–011 Observations under this Design
❌ Reopen Closed H_EDGE EXPs on prior CIDs
❌ PnL optimization / grid search as Design goal
❌ Context→entry or Context→sizing alpha in detector
❌ Implementation / Identity Freeze under this Design command alone
❌ Treat pa_cta mixin as production strategy
❌ Claim double-top is CID_010 rewrite / rescue
```

## 6. Identity package fields（to mint at Freeze）

| Field | Note |
|-------|------|
| `strategy_id` / `version` | provisional → frozen |
| `source_manifest` | Detector + orchestrator paths |
| `source_hash` / `parameter_hash` | mint at Freeze only |
| `morphology_spec_id` | OPP13_DT_MS_V0_1（at Freeze） |
| `execution_model` | stop/target/sizing class at Freeze |
| `evidence_lineage` | empty at Candidate birth |
| `context_independence` | MUST attest（strip always_in / context / late） |
| `architecture_attestation` | Detector pure · Strategy orchestrates only |

## 7. Dual-surface note

```text
Capital controls, if any, are a later RISK version/surface
under a new CC — do not merge survival KEEP into H_EDGE.
Prior CID RISK / Bindable does not transfer to CID_012.
```

## 8. Inventory honesty

```text
Preferred e2bfc0c strategies/pa_cta/opp/ mainline shelf: EXHAUSTED（CID_011）.
CID_012 consumes the last pre-declared residual PA path in that tree
（OPP13 double-top / FIRST_TEST · deferred by NSAD_CID_010）.

After CID_012 consumes this residual:
  Further NSAD requires evidence-backed new morphology Spec（not chat）,
  scoped Resume（e.g. multi-symbol H_EDGE power on HOLD/KEEP surfaces）,
  or explicit non-PA recovery（e.g. smc rewrite）— not Alpha theater.
```

## 9. Explicit non-grants

```text
❌ Identity Freeze
❌ Code implementation / working-tree restore
❌ Observation / backtest
❌ Alpha / Bindable / Production
❌ SCAP outcome change for pa_minimal / pa_cta / smc
❌ Selection of CID_012 as live strategy
```

## 10. Next（须另授 · pick）

```text
Authorize Identity Freeze · OPP13 double-top Detector + orchestrator @0.1.0
  — OR — leave CID_012 at Design-only
NOT: auto-implement · H_EDGE before Freeze · Resume paused · merge with CID_010
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | NSAD_CID_012_V0_1 DESIGNED · OPP13 double-top residual · Delegation-25AU |
