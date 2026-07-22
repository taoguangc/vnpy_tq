# Context Capability Gate v2 — Re-evaluation（v3.0 · post A1）

> **Type**: Gate v2 Re-evaluation（Capability Readiness · post A1 Engineering Evidence）  
> **Status**: **COMPLETE** ✓ — Decision **CONDITIONAL**（retained · **G2 Engineering block lifted**）  
> **Version**: 3.0  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CONTEXT_CAPABILITY_GATE_V2_REEVALUATION.md`  
> **Authorization**: [`GATE_V2_REEVALUATION_AUTHORIZATION_POST_A1.md`](GATE_V2_REEVALUATION_AUTHORIZATION_POST_A1.md) — **GRANTED**  
> **Prior Re-eval**: v2.0 — CONDITIONAL · G6 lift · G2 FAIL/BLOCK  
> **Prior Review**: [`CONTEXT_CAPABILITY_GATE_V2_REVIEW.md`](CONTEXT_CAPABILITY_GATE_V2_REVIEW.md) v1.1 — CONDITIONAL · CLOSED  
> **Policy**: [`CONTEXT_CAPABILITY_GATE_V2_POLICY_DRAFT.md`](CONTEXT_CAPABILITY_GATE_V2_POLICY_DRAFT.md) v0.2  
> **Knowledge**: [`K001_KNOWLEDGE_REVIEW.md`](K001_KNOWLEDGE_REVIEW.md) — Strengthened Qualified + Independence Qualified  
> **L1 Evidence**: [`CAP_CTX_001_L1_RUN001_EVIDENCE_REVIEW.md`](CAP_CTX_001_L1_RUN001_EVIDENCE_REVIEW.md)  
> **A1 Evidence**: [`CAP_CTX_A1_RUN001_EVIDENCE_REVIEW.md`](CAP_CTX_A1_RUN001_EVIDENCE_REVIEW.md) — **PASS**  
> **Portfolio Bar**: [`CAPABILITY_PORTFOLIO_BAR_REVIEW.md`](CAPABILITY_PORTFOLIO_BAR_REVIEW.md) v0.5  
> **ADR**: Decision 019

### Judgment object（binding）

```text
Gate v2 judges: Capability Readiness for consumption as a system component
Gate v2 does NOT judge: K001 Alpha / PnL / “是否值得交易”
```

```text
A1 PASS = engineering publication reliability
        ≠ statistical independence
        ≠ Alpha
        ≠ Strategy approval
```

### Frozen inputs（this re-eval）

```text
K001: Strengthened Qualified + Independence Qualified + Residual Price Family
A1:   Engineering Published State PASS（E1–E5）
Gate prior: CONDITIONAL（v2.0）
Capability Candidate: NO
RC001: NOT STARTED
```

---

## Aggregate Decision

```text
================================================
CONTEXT CAPABILITY GATE v2 RE-EVALUATION v3.0

Decision: CONDITIONAL ✓（retained）

Change vs v2.0:
  G2 Published State / Engineering: FAIL/BLOCK → PASS
  E1 Engineering: NOT READY → MET
  G2 Engineering Conditional Block → LIFTED

Unchanged:
  G6 Independence: PASS WITH QUALIFICATION
  G7 Falsification: PARTIAL
  G10 Transition Safety: BLOCK pressure（Candidate / RC001 unmet）
  Portfolio Bar: NOT MET（P5 PARTIAL remains）
  Capability Candidate: NO（≠ auto from G2 PASS）
  RC001: UNCHANGED / NOT STARTED
  Trading / Strategy / Backtest: NOT AUTHORIZED
  K001: UNCHANGED

Still blocking full Gate PASS:
  G7 PARTIAL（Stress）
  G10 BLOCK pressure
  Portfolio Bar P5
  Explicit Candidate Designation（not authorized this round）
================================================
```

```text
CONDITIONAL ≠ FAILURE
G2 PASS ≠ Gate PASS
A1 PASS ≠ Independence upgrade
Gate PASS ≠ Candidate ≠ RC001 ≠ Strategy
```

---

## Criterion scorecard（Policy G1–G10）

### Governance foundation

| ID | Name | v2.0 | v3.0 | Note |
|----|------|------|------|------|
| **G1** Ownership | PASS | **PASS** | unchanged |
| **G2** Published State | FAIL / BLOCK | **PASS** | A1 Evidence-backed ContextState publish（see §G2） |
| **G3** Reproducibility | PASS | **PASS** | + A1 CLI / lineage / fingerprints |
| **G4** Evidence Traceability | PASS | **PASS** | RUN001–005 + L1 + **A1** layer separation |

### Capability readiness

| ID | Name | v2.0 | v3.0 | Note |
|----|------|------|------|------|
| **G5** Evidence Sufficiency | PASS | **PASS** | Research + Engineering evidence now both present |
| **G6** Independence | PASS WITH QUALIFICATION | **PASS WITH QUALIFICATION** | **unchanged** — A1 ≠ independence evidence |
| **G7** Falsification Coverage | PARTIAL | **PARTIAL** | **unchanged** — Stress still absent；A1 does not cover |
| **G8** Scope Stability | PASS WITH BINDING | **PASS WITH BINDING** | + Decision 019 / A1 C-NO-SEMANTIC-UPGRADE |
| **G9** Claim Boundary | PASS | **PASS** | A1 PASS explicitly non-Alpha |
| **G10** Transition Safety | BLOCK pressure | **BLOCK pressure** | Candidate not designated；RC001 not Accepted |

### Informal ↔ Policy map

| User label | Policy ID |
|------------|-----------|
| Knowledge Boundary | **G9** |
| Evidence Sufficiency | **G5** |
| Independence | **G6** |
| Engineering | **G2**（+ E1） |
| Consumption | **G8/G9** + Decision 019 |

---

## §G2 — Published State（primary change）

### Prior（v2.0）

```text
FAIL / BLOCK
ContextEngine UNKNOWN-only
no evidence-backed published primary state
```

### New evidence（A1）

| Criterion | Review |
|-----------|--------|
| A1-E1 Deterministic Publish | PASS |
| A1-E2 Batch/Streaming Parity | PASS |
| A1-E3 Fault Handling | PASS |
| A1-E4 Latency（publish path） | PASS |
| A1-E5 Reproduction | PASS |

### Verdict

```text
G2: PASS ✓

UNKNOWN-only narrative
        →
Evidence-backed Published State（ContextState.v1）
```

Supports:

```text
stable publish · engineering consumption eligibility（Decision 019）
batch ≈ streaming · explicit INVALID/DEGRADED
```

Does **not** support:

```text
Alpha · trade signal · PnL improvement · full MarketState TREND/RANGE expansion claim
```

Binding scope:

```text
Primary tags: compression | expansion | invalid
confidence = computational only
≠ market_regime / alpha_state / trade_bias
```

---

## G6 / G7 — explicitly unchanged by A1

```text
A1 proves: engineering publication reliability
A1 does not prove: statistical independence or falsification stress
```

| ID | Verdict | Rationale |
|----|---------|-----------|
| G6 | PASS WITH QUALIFICATION | L1 residual Price Family retained |
| G7 | PARTIAL | Null/N1 present；material Stress still missing |

---

## Consumption Boundary（G8/G9 · binding while CONDITIONAL）

### Allowed（design / future RC001 only — **not authorized now**）

```text
Context Layer → Strategy Layer（filter / risk / selection）

  - descriptive context_state tag
  - computational confidence
  - risk_multiplier / allow-block on pre-existing signals
  - monitoring / diagnostics
```

### Forbidden（until RC001 Accepted + explicit Auth）

```text
❌ if compression: buy()/sell()
❌ Context as sole alpha / signal engine
❌ PnL-optimized Context tuning
❌ Claiming market regime detector / Brooks clone
```

---

## Portfolio Bar impact（v0.5）

| Dimension | v0.4 | v0.5 |
|-----------|------|------|
| P1 Temporal | MET | MET |
| P2 Cross-sectional | MET | MET |
| P3 Observation Family | MET | MET |
| P4 Independence | PASS WITH QUALIFICATION | PASS WITH QUALIFICATION |
| P5 Falsification | PARTIAL | PARTIAL |
| P6 Scope | MET | MET |
| **E1 Engineering** | **NOT READY** | **MET** |
| **BAR** | NOT MET | **NOT MET**（P5 remains） |

```text
E1 MET
        ≠
BAR MET
        ≠
Capability Candidate
```

---

## Capability Candidate Criteria（judgment only · **not designated**）

| # | Condition | Status |
|---|-----------|--------|
| 1 | Portfolio Bar **MET** | **NO**（P5 PARTIAL） |
| 2 | G1–G4 PASS | **YES**（G2 now PASS） |
| 3 | G5–G10 PASS（含 P4 映射） | **NO**（G7 PARTIAL；G10 BLOCK pressure） |
| 4 | Explicit Candidate Designation Review | **NOT STARTED**（本轮未授权） |
| 5 | Claim / consumption boundaries enforceable | **IMPROVED**（A1 + Decision 019 engineered）；full RC001 contract still open |

**Capability Candidate: NOT DESIGNATED**

```text
G2 PASS + E1 MET
        ≠
auto Capability Candidate = YES
```

> **Superseded for designation status**: see [`CAPABILITY_CANDIDATE_DESIGNATION_REVIEW.md`](CAPABILITY_CANDIDATE_DESIGNATION_REVIEW.md) — **CONDITIONAL / NARROW CANDIDATE**（Infrastructure only；FULL forbidden）。Gate v3.0 scorecard above unchanged.

---

## What this Re-evaluation does / does not authorize

| Allows | Forbids |
|--------|---------|
| Cite G2 / E1 lift with A1 evidence | Gate full PASS claim |
| Prepare Capability Candidate Review（另授） | Auto Candidate designation |
| Prepare RC001-A **design** docs（另授） | RC001 Accepted / 回测 |
| Cite Engineering consumption eligibility（Decision 019） | Strategy / Detector / Alpha / Trading |

---

## Recommended path（non-authorizing）

```text
Gate CONDITIONAL（G2 lift · G6 qualified · G7/P5 gap · G10 open）
        ↓
Capability Candidate Review（另授 · criteria above）
        ↓
（若 designation YES 或显式 Narrow Candidate）
RC001-A Context Filter Design（filter / risk only）
        ↓
RC001 Auth → experiment
        ↓
Strategy Research（另授）
```

Optional parallel（另授）：A2 Falsification Stress（G7 / P5）

**禁止现在**：

```text
AFF Strategy / Context+EMA / 回测求年化 / if compression: buy()
```

---

## Hard exclusions respected

```text
✓ No Observation / Code / Strategy this round
✓ No Candidate designation
✓ No RC001-A
✓ G6/G7 not silently upgraded by A1
✓ Residual Price coupling retained
✓ Gate ≠ Knowledge rewrite ≠ Alpha ≠ Trading
```

---

## Status after Re-evaluation

```text
Gate v2:                CONDITIONAL · RE-EVALUATED v3.0
G2 Engineering:         PASS（A1 Evidence-backed）
Independence (G6):      PASS WITH QUALIFICATION
Falsification (G7):     PARTIAL
Portfolio Bar:          NOT MET（E1 MET；P5 PARTIAL）
Capability Candidate:   CONDITIONAL / NARROW（Infrastructure）— see Designation Review
RC001:                  NOT STARTED
Trading / Backtest:     NOT STARTED
K001:                   UNCHANGED
Next eligible:          Authorize RC001-A Design（另授）
                        and/or A2 Stress（P5）（另授）
```

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 2.0 | post-L1：CONDITIONAL；G6 lift；G2 FAIL；Candidate NO |
| 2026-07-21 | 3.0 | post-A1：CONDITIONAL retained；**G2 PASS**；E1 MET；Bar still NOT MET（P5）；Candidate NO |
