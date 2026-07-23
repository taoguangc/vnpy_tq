# SEVF Specification — CID_003 / STRAT_REV_OPP16_01

> **Type**: Asset-bound SEVF Specification（≠ Fill · ≠ Observation · ≠ Alpha）  
> **Status**: **SPECIFIED** ✓  
> **Spec ID**: `SEVF_SPEC_CID_003_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: `Authorize SEVF Specification for CID_003`  
> **Framework**: [`SEVF-v1`](STRATEGY_EVIDENCE_VALIDATION_FRAMEWORK_FREEZE.md)  
> **Identity**: [`STRATEGY_IDENTITY_FREEZE_CID_003.md`](STRATEGY_IDENTITY_FREEZE_CID_003.md) — `SIF_CID_003_V0_1` **FROZEN** · Candidate  
> **Design**: [`STRATEGY_NEW_ASSET_DESIGN_CID_003.md`](STRATEGY_NEW_ASSET_DESIGN_CID_003.md)  
> **Data baseline**: [`docs/07_DATA_SPEC.md`](../07_DATA_SPEC.md) v1.0.0  
> **Lesson parent**: CID_002 Alpha Evidence **CLOSED**（H_MECH ≠ H_EDGE）— do not reopen

## Spec record

```text
================================================
SEVF_SPEC_CID_003_V0_1

Status: SPECIFIED ✓
Bound identity: STRAT_REV_OPP16_01@0.1.0
Fill / Observation: NOT AUTHORIZED
Alpha claim: NONE
CID_002 H_EDGE: NOT transferable · remains CLOSED
================================================
```

## 1. Purpose

Define **how** CID_003 may generate Strategy Asset Evidence under `SEVF-v1`,
before any concrete experiment is filled or run.

```text
Answers:   What must be true of every EXP on this identity?
Does not:  Pick symbols · run backtests · claim edge · designate Bindable
```

## 2. Bound test object（immutable for this Spec）

Every EXP under this Spec must bind exactly:

| Field | Required value |
|-------|----------------|
| `strategy_id` | `STRAT_REV_OPP16_01` |
| `version` | `0.1.0` |
| `source_hash` | `f87cdcc43e74060f23c08fa06364f0be90c538a1576566a0034ba096f0adc220` |
| `parameter_hash` | `76b124f47414af2da2e0cdfdc6afcd5025d2cca8ae3a5583ba667cc7e1e31c57` |
| `freeze_id` | `SIF_CID_003_V0_1` |
| `detector_binding` | `OPP16@1.0.0` |
| `class_tags` | `["mean_reversion","reversal"]` |
| `source_revision` | `966d7cab0d11c3f835b39533872cb8ead6f26e62`（or later tip **only if** hash-match） |

```text
Any source_hash / parameter_hash drift
  → this Spec does not apply
  → require new identity version + new Spec ID
```

## 3. Hypothesis class policy

### 3.1 Allowed primary-hypothesis families

Exactly **one** primary hypothesis per EXP.

| Family ID | Intent | Notes |
|-----------|--------|-------|
| `H_MECH` | Mechanism / auditability | Auditable signal→entry→exit with STOP/TARGET/TIME_STOP attributable to OPP16 |
| `H_EDGE` | Edge / expectancy structure | Pre-registered structure+expectancy gates（plan early；lesson from CID_002） |
| `H_NULL` | Null / no-edge orientation | Mean net after costs not distinguishable from pre-registered null |
| `H_ROBUST` | Declared robustness | Only after a Closed prior EXP；one validation dimension |

### 3.2 Recommended evidence order（NSAD）

```text
1) H_MECH（first Testing EXP）
2) H_EDGE diagnostic（do not defer indefinitely）
3) H_EDGE OOS（temporal completeness · not rescue）
4) Alpha Candidate petition OR Negative close of CID_003 Alpha path
```

### 3.3 Forbidden hypothesis shapes

```text
❌ Maximize return / Sharpe / PF / win-rate
❌ “Prove OPP16 / reversal works”
❌ Rescue via Context routing / Context Alpha
❌ Import CID_002 KEEP as CID_003 edge proof
❌ Parameter search framed as a single hypothesis
❌ Multi-detector bundles in one EXP
```

## 4. Market scope（Fill-time · not selected here）

Asset freeze has `market_scope = UNBOUND_AT_ASSET`.

Every Fill **must** declare:

```text
symbols / universe
session
period（start · end）
data_protocol_version → docs/07_DATA_SPEC.md v1.0.0
```

```text
Inventing “best” symbols after seeing results: FORBIDDEN
Continuity scopes preferred when comparing EXPs（declare why）
```

## 5. Data / cost / execution contract

| Binding | Frozen requirement |
|---------|-------------------|
| Data | TQ offline · 1m feed · CbC · unadjusted · real costs（docs/07） |
| Signal | 5m via BarGenerator（identity execution_model） |
| Risk | 1m stop / target / time-stop |
| `cost_binding` | `PROJECT_FROZEN_DATA_PROTOCOL` |
| `fill_binding` | `VNPY_CTA_BACKTEST_ENGINE_DEFAULTS_AT_EXP_REGISTRATION` |
| Fee/slippage | Resolved at EXP registration from project tables |
| Sizing | `fixed_size` from frozen parameter_manifest |
| Rollover | `on_rollover_adjust` present（identity） |

Zero-cost / adjusted-price runs = independent data EXPs only.

## 6. Single-variable rule

Each EXP changes **exactly one** primary variable vs its declared baseline.

First Testing EXP recommended variable:

```text
VARIABLE_0 = execute Observation under frozen identity + newly declared market_scope
Baseline   = no auditable closed round-trip attributable to OPP16
```

Later EXPs may vary **one** of: temporal window · symbol（predeclared universe）· cost stress · reproducibility replay.

Never in one EXP: detector logic + exit + sizing + Context gate.

## 7. Metrics and stop rules（Spec-level policy）

### 7.1 Mandatory audit metrics（every EXP）

```text
• trade/event count
• exit_reason distribution（STOP / TARGET / TIME_STOP / other）
• identity fingerprint echo（strategy_id · version · source_hash · parameter_hash）
• cost_binding / fill_binding / data_protocol in artifact metadata
• detector_binding echo（OPP16@1.0.0）
```

### 7.2 Optional hypothesis metrics（must be named in Fill）

```text
H_MECH: attributed exit count / reason set
H_EDGE: median MFE/MAE · share(MFE>MAE) · mean net_pnl · pre-registered tests
Must include KEEP/HOLD/REVERT rule before Observation
```

### 7.3 Forbidden as silent success criteria

```text
❌ Post-hoc Sharpe / annual-return targets
❌ “Looks good enough” without pre-registered rule
❌ Dropping symbols after seeing results
❌ Retuning body_ratio / risk_reward to flip KEEP
```

## 8. Outcome classification

| Outcome | Meaning for CID_003 |
|---------|---------------------|
| `KEEP` | Supports hypothesis in declared scope；≠ Bindable / Alpha |
| `HOLD` | Insufficient / inapplicable；no promotion |
| `REVERT` | Fails pre-registered gate；retain as Negative Evidence |

```text
KEEP ≠ Alpha proven ≠ Bindable ≠ Production
H_MECH KEEP ≠ H_EDGE KEEP
```

## 9. Evidence contract

An EXP yields **evidence** only if:

```text
1. Pre-registration complete under this Spec（Fill + Observation auth）
2. Identity snapshot matches §2 hashes
3. Auditable CSV / equivalent exists
4. Evaluation records KEEP|HOLD|REVERT + uncertainty
5. Artifact immutable after Close（Decision 017）
```

```text
No CSV / equivalent → no evidence claim → no Testing→Verified promotion
```

## 10. Lifecycle gates under this Spec

| From → To | Minimum |
|-----------|---------|
| Candidate → Testing | This Spec + Fill/Pre-registration + Observation auth for a named EXP |
| Testing → Verified | ≥1 Closed EXP + Evidence Review；identity match；hypothesis-scoped |
| → Bindable | Outside this Spec；full SAC-v1 + separate approval |
| Alpha Candidate | Separate multi-gate petition after H_EDGE (+ OOS) package — not automatic from H_MECH |

## 11. Experiment ID convention

```text
STRAT_RO16_EXP001, STRAT_RO16_EXP002, …
（RO16 = REV_OPP16 shorthand）
New experiment_id for every Observation；never reuse Closed IDs
```

## 12. Explicit non-authorizations（this Spec）

```text
❌ Fill concrete symbols/dates
❌ Observation / backtest execution
❌ Parameter or PnL optimization
❌ Context Consumer experiment
❌ Portfolio / Production / Epoch 7
❌ Claim Bindable / Verified / Alpha
❌ Reopen CID_002 H_EDGE Closed EXPs
```

## 13. Next gate

```text
DONE: STRAT_RO16_EXP001 Observation → HOLD
DONE: Engineering Review + @0.1.1 repair（see SEVF_SPEC_CID_003_V0_1_1）
@0.1.0 Spec: remains binding for Closed EXP001 only
New EXPs on repair identity: use SEVF_SPEC_CID_003_V0_1_1
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | `SEVF_SPEC_CID_003_V0_1` SPECIFIED |
| 2026-07-23 | Next pointer · repair Spec V0_1_1 / EXP002 |
