# SEVF Specification — CID_002 / STRAT_TREND_BROOKS_SCALP_02

> **Type**: Asset-bound SEVF Specification（≠ Fill · ≠ Pre-registration · ≠ Authorization · ≠ Observation · ≠ Backtest）  
> **Status**: **SPECIFIED** ✓  
> **Spec ID**: `SEVF_SPEC_CID_002_V0_1`  
> **Date**: 2026-07-22  
> **Authorization**: User path **A** — `Authorize SEVF Specification`  
> **Framework**: [`SEVF-v1`](STRATEGY_EVIDENCE_VALIDATION_FRAMEWORK_FREEZE.md)  
> **Identity**: [`SIF_CID_002_V0_1`](STRATEGY_IDENTITY_FREEZE_CID_002.md) — **FROZEN** · Candidate  
> **Data baseline**: [`docs/07_DATA_SPEC.md`](../07_DATA_SPEC.md) v1.0.0

## Spec record

```text
================================================
SEVF_SPEC_CID_002_V0_1

Status: SPECIFIED ✓
Bound identity: STRAT_TREND_BROOKS_SCALP_02@0.1.0
Fill / Pre-registration: DONE → STRAT_BS02_EXP001（see STRATEGY_SEVF_FILL_CID_002_EXP001.md）
SEVF Authorization: NOT GRANTED
Observation / Backtest: NOT AUTHORIZED
Alpha claim: NONE
================================================
```

## 1. Purpose

Define **how** CID_002 may generate Strategy Asset Evidence under `SEVF-v1`,
before any concrete experiment is filled or run.

```text
Answers:   What must be true of every EXP on this identity?
Does not:  Pick symbols · run backtests · claim edge · designate Bindable
```

## 2. Bound test object（immutable for this Spec）

Every EXP under this Spec must bind exactly:

| Field | Required value |
|-------|----------------|
| `strategy_id` | `STRAT_TREND_BROOKS_SCALP_02` |
| `version` | `0.1.0` |
| `source_hash` | `3ba12893e43db6805e5af2012d811a7f0034143dbedb102637afd7a5819b9589` |
| `parameter_hash` | `3ff061891488a9d9f5641cf147efc1e70c8d4cb8410540858d8b727bd485d1ab` |
| `freeze_id` | `SIF_CID_002_V0_1` |
| `detector_binding` | `BROOKS_SCALP_FP@0.1.0` |
| `class_tags` | `["trend"]` |

```text
Any source_hash / parameter_hash drift
  → this Spec does not apply
  → require new identity version + new Spec（or Spec amendment under new ID）
```

`source_revision` at Fill time:

```text
• Prefer full git commit SHA if binding bytes are committed and hash-match
• Else retain CONTENT_ADDRESSED:<source_hash> with git_anchor note
• Never invent a revision that does not contain the frozen bytes
```

## 3. Hypothesis class policy

### 3.1 Allowed primary-hypothesis families（first Testing EXP）

Exactly **one** primary hypothesis per EXP. Allowed families for CID_002:

| Family ID | Intent | Example shape（not a filled hypothesis） |
|-----------|--------|------------------------------------------|
| `H_MECH` | Mechanism / auditability | Under declared scope, the frozen identity produces auditable signal→entry→exit events with stop/target/time reasons attributable to `BROOKS_SCALP_FP` |
| `H_NULL` | Null / no-edge orientation | Under declared scope and frozen costs, mean closed-trade expectancy is not distinguishable from the pre-registered null（default: zero after costs） |
| `H_ROBUST` | Declared robustness（only after a Closed prior EXP） | Same identity; one validation dimension per `SEVF-v1` §6 |

### 3.2 Forbidden hypothesis shapes

```text
❌ Maximize return / Sharpe / PF / win-rate
❌ “Prove Brooks / PA works”
❌ Rescue via Context routing / Context Alpha
❌ Multi-OPP or multi-detector bundles in one EXP
❌ Parameter search framed as a single hypothesis
```

## 4. Market scope（must be filled at EXP · not invented here）

Asset freeze has `market_scope = UNBOUND_AT_ASSET`.

Every Fill / Pre-registration **must** declare:

```text
symbols / universe
session（day / night / both · as applicable）
period（start · end · timezone convention）
data_protocol_version → docs/07_DATA_SPEC.md v1.0.0（or approved independent data EXP）
```

```text
This Spec does NOT select a preferred symbol list.
Inventing “best” symbols for positive results: FORBIDDEN
```

## 5. Data / cost / execution contract

| Binding | Frozen requirement |
|---------|-------------------|
| Data | TQ offline · 1m · CbC · unadjusted · real costs（`docs/07` v1.0.0） unless a separately labeled independent data EXP |
| `cost_binding` | `PROJECT_FROZEN_DATA_PROTOCOL` |
| `fill_binding` | `VNPY_CTA_BACKTEST_ENGINE_DEFAULTS_AT_EXP_REGISTRATION` |
| Fee/slippage numbers | Resolved at EXP registration from project symbol tables / harness — not invented in Spec |
| Signal TF | 1m（identity execution_model） |
| Order style | Stop entry after DetectionResult；structural stop + 1R target；`max_hold_bars` time stop |
| Sizing | `fixed_size` from frozen parameter_manifest |

Zero-cost or adjusted-price runs are **independent data EXPs**, not substitutes for the baseline.

## 6. Single-variable rule

Each EXP changes **exactly one** primary variable relative to its declared baseline.

For the **first** Testing EXP on CID_002, the recommended primary variable is:

```text
VARIABLE_0 = “execute Observation under frozen identity + newly declared market_scope”
Baseline   = null / no-trade expectation OR explicit no-strategy comparator
```

Subsequent EXPs may vary **one** of:

```text
temporal window · symbol（within a predeclared universe policy）
cost sensitivity · fill assumption stress · reproducibility replay
```

Never in the same EXP:

```text
detector logic + exit + sizing + filter + Context gate
```

## 7. Metrics and stop rules（Spec-level policy）

`SEVF-v1` freezes **no** universal profit thresholds. For CID_002:

### 7.1 Mandatory audit metrics（every EXP）

```text
• trade/event count
• exit_reason distribution（STOP / TARGET / TIME_STOP / other）
• identity fingerprint echo（strategy_id · version · source_hash · parameter_hash）
• cost_binding / fill_binding / data_protocol echoed in artifact metadata
```

### 7.2 Optional hypothesis metrics（must be named in Fill）

```text
May be declared only if relevant to the primary hypothesis, e.g.:
  mean PnL after costs · expectancy · MFE/MAE summaries · hold-time distribution
Must include a pre-registered decision rule for KEEP / HOLD / REVERT
```

### 7.3 Forbidden as silent success criteria

```text
❌ Post-hoc Sharpe / annual-return targets
❌ “Looks good enough” without pre-registered rule
❌ Dropping symbols after seeing results
```

## 8. Outcome classification（bound to SEVF-v1）

| Outcome | Meaning for CID_002 |
|---------|---------------------|
| `KEEP` | Supports retaining the stated hypothesis in its declared scope；eligible for independent validation EXP；**≠** Bindable / Alpha |
| `HOLD` | Insufficient, conflicting, or scope-limited；no promotion |
| `REVERT` | Contradicts primary hypothesis or fails a pre-registered gate；close/revert tested claim for that EXP scope；retain negative evidence |

```text
KEEP ≠ Alpha proven ≠ Bindable ≠ Production
HOLD / REVERT ≠ delete artifacts
```

## 9. Evidence contract

An EXP yields **evidence** only if all hold:

```text
1. Pre-registration complete under this Spec（Fill + Authorization）
2. Identity snapshot matches §2 hashes
3. Auditable output exists（CSV or equivalent trade/event-level）
4. Evaluation records KEEP | HOLD | REVERT + uncertainty
5. Artifact is immutable after Close（Decision 017）
```

```text
No CSV / equivalent → no evidence claim → no Testing→Verified promotion
```

Evidence units remain Strategy Asset Evidence only — not Context Consumer Evidence,
not Portfolio Evidence.

## 10. Lifecycle gates under this Spec

| From → To | Minimum under this Spec |
|-----------|-------------------------|
| Candidate → Testing | This Spec + completed Fill/Pre-registration + SEVF Authorization for a named EXP |
| Testing → Verified | ≥1 Closed EXP with Evidence Review supporting the stated hypothesis；identity match |
| → Bindable | Outside this Spec alone；requires full `SAC-v1` Bindable conditions + separate approval |
| → Deprecated | Predeclared or replicated negative evidence；archive immutable |

## 11. Explicit non-authorizations（this Spec）

```text
❌ Fill concrete symbols/dates（requires Authorize SEVF Fill / Pre-registration）
❌ SEVF Authorization to run
❌ Observation / Backtest execution
❌ Parameter or PnL optimization
❌ Context Consumer experiment
❌ Portfolio construction
❌ RC001-B reopen
❌ Claim Bindable / Verified / Alpha
```

## 12. Next gate

```text
Authorize SEVF Observation for STRAT_BS02_EXP001
  （Fill complete 2026-07-22）
```

Or:

```text
Pause Epoch 5 Strategy Research
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | `SEVF_SPEC_CID_002_V0_1` specified under user path A |
| 2026-07-22 | Fill/Pre-reg `STRAT_BS02_EXP001` completed（run still NO） |
