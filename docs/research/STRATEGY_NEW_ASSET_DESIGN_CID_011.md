# New Strategy Asset Design — CID_011 Path

> **Type**: Strategy Asset Design（≠ Identity Freeze · ≠ Implementation · ≠ Backtest · ≠ Alpha）  
> **Status**: **DESIGNED** ✓  
> **Design ID**: `NSAD_CID_011_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AR（`授权你决定25次` · interpreted as menu **Option B**）  
> **Prior**: `CPD_CID_003`–`CPD_CID_010` PAUSED · AERC_003–010 Alpha NONE  
> **Contracts**: `SAC-v1` · `SAFIP-v1` · `SEVF-v1` · `SCIDR-v1`  
> **Data baseline（future）**: docs/07 · TQ offline · 1m · CbC · unadjusted · real costs

## Design record

```text
================================================
NSAD_CID_011_V0_1

Purpose: Open NEW strategy asset research path after
         CID_003–010 campaign Pause（all Alpha NONE）.

CID_002–010: NOT resumed · NOT reopened for H_EDGE rescue
Alpha:   NONE（new asset starts at zero hypothesis）
Code / Identity Freeze / Observation: NOT AUTHORIZED here
================================================
```

## 0. Why a new asset now

```text
Closed Alpha-NONE campaigns（all PAUSED）:
  CID_003–005  MR / exhaustion（OPP16/12/17）
  CID_006      all-session strong breakout（OPP08）
  CID_007      session opening-drive BREAKOUT（OPP19 OD-Breakout）
  CID_008      EMA pullback continuation（OPP02）
  CID_009      wedge Path-A（OPP15）
  CID_010      day-boundary single-touch（OPP13 · H_EDGE HOLD×2）

Lesson（compound）:
  Eight auditable mechanisms failed to produce H_EDGE KEEP under frozen gates
  （CID_010 could not even clear MIN_N on rb single-year）.
  Last legacy opp/ shelf item called out by prior NSAD: OPP19 OD_REV —
  same session opening microstructure family as CID_007 but OPPOSITE
  hypothesis（fade first drive · not breakout）. Must be a NEW identity,
  not a rescue of SIF_CID_007.
```

## 1. Asset slot

| Field | Design value |
|-------|----------------|
| `campaign_id` | `CID_011` |
| `working_strategy_id`（provisional） | `STRAT_SESS_OPP19_REV_01`（pending Identity Freeze） |
| `class_tags`（provisional） | `["session","opening_drive","reversal"]` |
| `lifecycle_start` | Candidate（after Identity Freeze） |
| `parent_asset` | none（**not** a fork of `STRAT_SESS_OPP19_01` / CID_007 binding bytes） |

```text
Provisional IDs may change at Identity Freeze.
Do not mint source_hash until freeze.
Explicit: ≠ CID_007 parameter transfer · ≠ OD-Breakout reopen
```

## 2. Preferred seed（inventory / git · not Bindable）

| Seed | Provenance | Why preferred |
|------|------------|---------------|
| **OPP19 OD_REV** | git `e2bfc0c…` · `strategies/pa_cta/opp/opp19.py` · opening-drive reversal path | Last declared legacy shelf item；session fade ≠ OD-Breakout（CID_007）· ≠ day-boundary（CID_010） |

```text
Seed = morphology hypothesis material for a NEW PAAF Detector
Recovery mode intent: REWRITE_AS_PAAF_ASSET（SCIDR）
≠ WORKING_TREE_RESTORE · ≠ reopen Closed CID_007 EXPs
```

### Declared simplifications（at future rewrite）

```text
Scope IN:  morning/night opening window · bar1 shape capture
           · reverse bar vs bar1 mid/extreme with body_ratio gate
Scope OUT: OD-Breakout path（already CID_007 · Alpha CLOSED）
Strip:     always_in · effective_context / opp19_rev_contexts
           · opp19_rev_gate stack（when enabling would reintroduce Context）
Keep defaults（legacy）: opening_rev_body_ratio=0.45
                         morning/night cutoff ≈25 min
                         bar1 range ATR band optional（declare at Freeze）
Explicit PatternState FSM: IDLE → BAR1_SET → ARMED/SIGNAL/RESET
```

### Explicitly NOT preferred as CID_011 mainline

| Object | Reason |
|--------|--------|
| CID_003–010 assets | Alpha CLOSED · PAUSED |
| CID_007 OD-Breakout identity | Separate freeze · do not merge |
| OPP16/12/17/08/02/15/13 rewrite | Consumed |
| Chat-invented session fade | Violates SAC · fabrication risk |
| “New Spec from scratch” without seed | Deferred unless user rejects OD_REV |

## 3. Research question（CID_011）

```text
Primary:
  Can an OPP19-class opening-drive REVERSAL mechanism, rewritten as a
  Context-independent PAAF Detector under docs/07 costs, produce an
  auditable H_MECH AND a pre-registered H_EDGE that survives temporal OOS
  — without parameter shopping and without borrowing CID_007 bytes?

Secondary（only after H_EDGE structure exists）:
  Multi-symbol portability · capital surface · Context consumption（Decision 019）
```

## 4. Planned evidence order（do not skip）

```text
1) Morphology Spec（OD_REV only）+ PAAF Detector rewrite + Identity Freeze
2) SEVF Spec bound to that identity
3) H_MECH EXP（auditability · one scope）
4) H_EDGE diagnostic EXP（SAME gates as AERC CID_003–010）
5) H_EDGE OOS / multi-symbol power as needed（esp. if low-n HOLD risk）
6) Only then: Alpha Candidate petition OR Negative Alpha close for CID_011
```

```text
FORBIDDEN order:
  Bindable / Production theater before H_EDGE structure
  Resume CID_003–010 idle KEEP hunting as substitute
  Copy CID_007 OD-Breakout parameters into OD_REV “to make it work”
  Bundle OD-Breakout + OD_REV under one strategy_id
```

## 5. Hard boundaries

```text
❌ Resume CID_003–010 Observations under this Design
❌ Reopen Closed H_EDGE / H_MECH EXPs on prior CIDs
❌ PnL optimization / grid search as Design goal
❌ Context→entry or Context→sizing alpha in detector
❌ Implementation / Identity Freeze under this Design command alone
❌ Treat pa_cta mixin as production strategy
❌ Claim OD_REV is CID_007 repair
```

## 6. SAC readiness checklist（Design target）

| SAC field | Status in this Design |
|-----------|------------------------|
| `strategy_id` / `version` | provisional only |
| `source_manifest` + hashes | **TBD at Freeze** |
| `parameter_manifest` + hash | **TBD at Freeze**（body_ratio · cutoffs · bar1 ATR band · RR） |
| `market_scope` | unbound at asset · bound per EXP |
| `execution_model` | stop/target/sizing class at Freeze |
| `evidence_lineage` | empty at Candidate birth |
| `context_independence` | MUST attest（strip always_in / context lists） |
| `architecture_attestation` | Detector pure · Strategy orchestrates only |

## 7. Dual-surface note

```text
Capital controls, if any, are a later RISK version/surface
under a new CC — do not merge survival KEEP into H_EDGE.
Prior CID RISK / Bindable does not transfer to CID_011.
```

## 8. Inventory honesty

```text
After CID_011 consumes OD_REV, the e2bfc0c strategies/pa_cta/opp/ preferred
shelf is exhausted for mainline NSAD.
Further campaigns require: new morphology Spec（evidence-backed）,
scoped Resume（e.g. multi-symbol H_EDGE power on HOLD/KEEP surfaces）,
or explicit user-directed research posture change — not chat invention.
```

## 9. Explicit non-grants

```text
❌ Identity Freeze
❌ Code implementation / working-tree restore
❌ Observation / backtest
❌ Alpha / Bindable / Production
❌ SCAP outcome change for pa_minimal / pa_cta / smc
❌ Selection of CID_011 as live strategy
```

## 10. Next（须另授 · pick）

```text
Authorize Identity Freeze · OPP19 OD_REV Detector + orchestrator @0.1.0
  — OR — leave CID_011 at Design-only
NOT: auto-implement · H_EDGE before Freeze · Resume paused · merge with CID_007
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | NSAD_CID_011_V0_1 DESIGNED · OPP19 OD_REV preferred · Delegation-25AR |
