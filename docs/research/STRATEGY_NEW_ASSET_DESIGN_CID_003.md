# New Strategy Asset Design — CID_003 Path

> **Type**: Strategy Asset Design（≠ Identity Freeze · ≠ Implementation · ≠ Backtest · ≠ Alpha）  
> **Status**: **DESIGNED** ✓  
> **Design ID**: `NSAD_CID_003_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: `Authorize New Strategy Asset Design`  
> **Prior**: [`STRATEGY_ALPHA_EVIDENCE_RESEARCH_CLOSURE_CID_002.md`](STRATEGY_ALPHA_EVIDENCE_RESEARCH_CLOSURE_CID_002.md) · `AERC_CID_002_V0_1`  
> **Contracts**: `SAC-v1` · `SAFIP-v1` · `SEVF-v1` · `CC-CID_002-v1`（citation pattern；new asset gets own CC if needed）  
> **Data baseline（future）**: docs/07 · TQ offline · 1m · CbC · unadjusted · real costs

## Design record

```text
================================================
NSAD_CID_003_V0_1

Purpose: Open a NEW strategy asset research path after
         CID_002 Alpha Evidence CLOSED without edge.

CID_002: NOT reopened for H_EDGE rescue / retune
Alpha:   NONE（new asset starts at zero hypothesis）
Code / Identity Freeze / Observation: NOT AUTHORIZED here
================================================
```

## 0. Why a new asset（binding lesson from CID_002）

```text
CID_002 delivered:
  H_MECH Verified · RISK Verified · Research Bindable（mechanism）
  H_EDGE REVERT on rb/2024 and rb/2025
  Alpha Candidate NOT ESTABLISHED

Lesson:
  Auditable mechanism ≠ convertible edge.
  New asset must plan H_EDGE falsification EARLY,
  and must NOT inherit Brooks Scalp First-Pullback as “default Alpha hope”.
```

## 1. Asset slot

| Field | Design value |
|-------|----------------|
| `campaign_id` | `CID_003` |
| `working_strategy_id`（provisional） | `STRAT_REV_OPP16_01`（pending Identity Freeze） |
| `class_tags`（provisional） | `["mean_reversion"]` or `["other","reversal"]` |
| `lifecycle_start` | Candidate（after Identity Freeze） |
| `parent_asset` | none（not a fork of CID_002 bytes） |

```text
Provisional IDs may change at Identity Freeze.
Do not mint source_hash until freeze.
```

## 2. Preferred seed（from inventory · not selected as Bindable yet）

| Seed | Path | Why preferred |
|------|------|----------------|
| **OPP16 Two-Bar Reversal Detector** | `strategies/paaf/detectors/opp16_two_bar_reversal.py` | AVAILABLE · different family from BROOKS_SCALP_FP · already Candidate E0 · Detector≠Strategy（correct layering） |

```text
Seed = detector hypothesis material
≠ frozen strategy asset
≠ permission to trade / backtest under this Design alone
```

### Explicitly NOT preferred as CID_003 mainline

| Object | Reason |
|--------|--------|
| `STRAT_TREND_BROOKS_SCALP_02` / BROOKS_SCALP_FP | Alpha path CLOSED · no silent reopen |
| `BrooksScalpPaafStrategy*` RISK/MECH wrappers | Same morphology family |
| `TemplateStrategy` / `PaafStrategy` | Orchestration skeleton only |
| Chat-invented “new Brooks variant” | Violates SAC · fabrication risk |

## 3. Research question（CID_003）

```text
Primary:
  Can a two-bar reversal（OPP16）mechanism, under docs/07 costs,
  produce an auditable H_MECH AND a pre-registered H_EDGE that
  survives temporal OOS — without parameter shopping?

Secondary（only after H_EDGE structure exists）:
  Multi-symbol portability · cost stress · Context consumption（capability only）
```

## 4. Planned evidence order（do not skip）

```text
1) Identity Freeze（new SIF · new strategy module wrapping OPP16）
2) SEVF Spec bound to that identity
3) H_MECH EXP（auditability · one scope）
4) H_EDGE diagnostic EXP（structure+expectancy · SAME gates discipline as AERD）
5) H_EDGE OOS EXP（temporal completeness · not rescue）
6) Only then: Alpha Candidate petition OR Negative close of CID_003 Alpha path
```

```text
FORBIDDEN order:
  Bindable maturity theater → Production residuals → then ask about edge
```

## 5. Hard boundaries

```text
❌ Reopen CID_002 H_EDGE Closed EXPs
❌ Copy CID_002 parameters into OPP16 “to make it work”
❌ PnL optimization / grid search as Design goal
❌ Context→Alpha smuggling
❌ Epoch 7 / Production Bindable for CID_003 before edge evidence
❌ Implementation under this Design command alone
```

## 6. SAC readiness checklist（Design target）

Before any future Identity Freeze for CID_003, Design requires a draft of:

| SAC field | Status in this Design |
|-----------|------------------------|
| `strategy_id` / `version` | provisional only |
| `source_manifest` + hashes | **TBD at Freeze** |
| `parameter_manifest` + hash | **TBD at Freeze** |
| `market_scope` | unbound at asset · bound per EXP |
| `execution_model` | must declare stop/target/sizing class at Freeze |
| `evidence_lineage` | empty at Candidate birth |
| `context_independence` | MUST attest（OPP16 already Context-free signal） |
| `architecture_attestation` | Detector pure · Strategy orchestrates only |

## 7. Dual-surface note

```text
If capital controls are added later, use a NEW version/surface
and CC-style citation — do not merge survival KEEP into H_EDGE.
CID_002 RISK Verified does not transfer to CID_003.
```

## 8. Explicit non-grants

```text
❌ Identity Freeze
❌ Code implementation / detector behavior change
❌ Observation / backtest
❌ Alpha / Bindable / Production
❌ Selection of CID_003 as “the” production strategy
```

## 9. Next（须另授 · pick）

```text
DONE: Strategy Identity Freeze SIF_CID_003_V0_1
Next: Authorize SEVF Specification for CID_003
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | NSAD_CID_003_V0_1 DESIGNED · OPP16 preferred seed |
| 2026-07-23 | Identity FROZEN · STRAT_REV_OPP16_01@0.1.0 |
