# Capability Candidate Designation Review

> **Type**: Capability Candidate Designation Review（≠ Gate PASS · ≠ RC001 · ≠ Strategy）  
> **Status**: **COMPLETE** ✓ — Decision **CONDITIONAL / NARROW CANDIDATE**  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CAPABILITY_CANDIDATE_DESIGNATION_REVIEW.md`  
> **Authorization**: `Authorize Capability Candidate Review` — **GRANTED**  
> **Inputs**: K001 Strengthened + Independence Qualified · A1 PASS · Gate v2 CONDITIONAL v3.0 · Portfolio Bar v0.5 NOT MET  
> **Policy**: [`CONTEXT_CAPABILITY_GATE_V2_POLICY_DRAFT.md`](CONTEXT_CAPABILITY_GATE_V2_POLICY_DRAFT.md) R5  
> **ADR**: Decision 019  
> **Gate**: [`CONTEXT_CAPABILITY_GATE_V2_REEVALUATION.md`](CONTEXT_CAPABILITY_GATE_V2_REEVALUATION.md) v3.0  
> **Bar**: [`CAPABILITY_PORTFOLIO_BAR_REVIEW.md`](CAPABILITY_PORTFOLIO_BAR_REVIEW.md) v0.5

### Review Record（binding）

```text
================================================
CAPABILITY CANDIDATE DESIGNATION REVIEW

Decision: CONDITIONAL / NARROW CANDIDATE ✓

Object: Context Infrastructure Capability
        ≠ Market Alpha / Signal / Predictive Edge

FULL CANDIDATE: NOT ALLOWED（Bar NOT MET · P5 PARTIAL）
NOT DESIGNATED: rejected as primary（C1/C2 satisfied；Narrow path opened by this Review Auth）

K001 Tier: UNCHANGED
Gate v2: UNCHANGED（CONDITIONAL）
RC001 / Strategy / Backtest: NOT STARTED
================================================
```

---

## 1. Candidate Object Definition（C2）

### Frozen object

```text
Capability Candidate Object =
  Context Infrastructure Capability
```

Meaning:

```text
A validated environment-description and strategy-constraint component
that may be consumed by trading systems only as:
  Filter · Risk Modifier · Monitoring · Permission Layer
```

### Explicit non-objects

```text
❌ Market Alpha Capability
❌ Signal Capability
❌ Predictive Edge Capability
❌ “proven profitable Context”
```

```text
Infrastructure Candidate
        ≠
Alpha Candidate
```

---

## 2. C1 — Consumption Contract

### Sources（auditable）

| Source | Role |
|--------|------|
| Decision 019 | ADR freeze：filter / risk / monitoring · NOT signal / sizing alpha |
| Gate v3.0 §Consumption | Allowed / Forbidden while CONDITIONAL |
| A1 ContextState.v1 | Engineered forbid-list（diagnostics）· descriptive tags only |
| A1 Evidence Review PASS | Publish reliability for engineering consumption |

### Allowed（binding）

```text
Context
 ├── Filter
 ├── Risk Modifier
 ├── Monitoring
 └── Permission Layer（allow/block on pre-existing strategy signals）
```

### Forbidden（binding）

```text
❌ Context → Entry Signal
❌ Context → Expected Return
❌ Context → Position Size Alpha
❌ if context_state == compression: buy()/sell()
❌ edge = context_score / confidence-as-win-probability
```

### Verdict C1

```text
PASS ✓ — Consumption Contract exists and is enforceable in docs + A1 schema
```

Remaining gap（does not fail C1）：RC001 runtime contract not yet implemented — Design only eligible under Narrow（§5）。

---

## 3. Eligibility Check

| # | Policy / Review condition | Status |
|---|---------------------------|--------|
| 1 | Portfolio Bar **MET** | **NO**（P5 PARTIAL） |
| 2 | G1–G4 PASS | **YES**（G2 PASS post-A1） |
| 3 | G5–G10 full PASS | **NO**（G7 PARTIAL；G10 BLOCK pressure） |
| 4 | Explicit Designation Review Auth | **YES**（this Review） |
| 5 | Claim / consumption boundaries enforceable | **YES**（docs + A1；RC001 runtime pending） |
| C1 | Consumption Contract | **PASS** |
| C2 | Infrastructure object freeze | **PASS** |
| C3 | R5 compatibility | **FULL blocked · Narrow allowed by Review matrix** |

```text
Eligible for FULL Candidate: NO
Eligible for NARROW Infrastructure Candidate: YES（under this Auth Decision Matrix）
```

---

## 4. R5 Compatibility（C3）

### Policy R5 path

```text
Portfolio Bar MET
        ↓
Candidate Eligible（full path）
```

### Current fact

```text
Portfolio Bar: NOT MET
Primary block: P5 Falsification = PARTIAL
```

### Ruling

```text
FULL CANDIDATE = NOT ALLOWED ✓
```

Cannot output `Capability Candidate = YES` as unrestricted / full designation.

### Narrow Path（this Review Authorization）

This Review’s Decision Matrix **explicitly** permits:

```text
CONDITIONAL / NARROW CANDIDATE
  = Infrastructure Candidate only
  + P5 residual binding
  + Price Family residual binding（from L1 / G6）
  ≠ silent Policy R5 bypass
  ≠ FULL Candidate
  ≠ Gate PASS
```

```text
NARROW
  =
explicit limited designation under Review Auth
  ≠
Policy R5 BAR MET satisfaction
  ≠
rewrite Portfolio Bar to MET
```

---

## 5. Scope Restriction（binding on NARROW）

While **CONDITIONAL / NARROW CANDIDATE** holds:

| May | Must not |
|-----|----------|
| Cite Infrastructure Candidate for **RC001-A Design** eligibility（另授） | Claim Alpha / Signal Candidate |
| Use Decision 019 consumption verbs | `buy()` / expected return / size alpha from Context |
| Retain P5 PARTIAL + Price residual as **active qualifications** | Treat Bar as MET |
| Keep Gate = CONDITIONAL | Claim Gate PASS |
| Keep K001 tier unchanged | Upgrade K001 via Candidate |

```text
NARROW Candidate
        ≠
Strategy authorized
        ≠
Backtest authorized
        ≠
RC001 Accepted
```

---

## 6. RC001 Entry Condition（define only · **not started**）

### Prerequisite for RC001-A Design Authorization

```text
CONDITIONAL / NARROW CANDIDATE（this Review）
        ↓
Explicit Authorize RC001-A Design
        ↓
RC001-A Contract Test（filter / risk / permission only）
        ↓（另授）
RC001-B Controlled Strategy Integration
        ↓（另授）
Backtest（≠ return optimization objective）
```

### RC001-A Design must freeze

```text
Context as: filter | risk_modifier | allow_block | monitoring
Context must not: generate entry · expected_return · sizing alpha
Success metric: contract compliance / behavior under ContextState
        ≠ Sharpe / PnL / annual return chase
```

### Forbidden sequence

```text
Candidate → 调参 → 找年化
```

---

## 7. Decision Matrix Application

| Option | Applied? | Reason |
|--------|----------|--------|
| **NOT DESIGNATED** | No（as primary） | C1/C2 PASS；blocking only R5 full path / P5；Narrow matrix available |
| **CONDITIONAL / NARROW CANDIDATE** | **YES** | Infrastructure object + consumption contract；P5 residual bound；FULL forbidden |
| **FULL CANDIDATE** | **No** | Bar NOT MET；G7/G10 incomplete |

### Aggregate Decision

```text
Capability Candidate Designation:
  CONDITIONAL / NARROW CANDIDATE

Label for citation:
  “Context Infrastructure Capability Candidate（Narrow）
   — P5 PARTIAL residual binding
   — Price Family residual binding
   — Decision 019 consumption only”
```

---

## 8. What this Review does / does not authorize

| Allows | Forbids |
|--------|---------|
| Cite Narrow Infrastructure Candidate | FULL Candidate / `Candidate = YES` unrestricted |
| Prepare RC001-A Design（**另授**） | RC001-A Design/Execution without new Auth |
| Keep A1 + Decision 019 consumption claims | Strategy / Backtest / Trading |
| | Gate PASS · K001 tier change · Alpha claim |

---

## 9. Status after Review

```text
Capability Candidate:   CONDITIONAL / NARROW（Infrastructure only）
K001:                   UNCHANGED
Gate v2:                CONDITIONAL（unchanged）
Portfolio Bar:          NOT MET（unchanged）
RC001:                  NOT STARTED
Strategy / Backtest:    NOT STARTED

Next eligible:
  Authorize RC001-A Design → **GRANTED** · Design **COMPLETE**
  → Authorize RC001-A Contract Review（另授）
  （optional parallel: A2 Stress to lift P5）
```

---

## 修订记录

| 日期 | 说明 |
|------|------|
| 2026-07-21 | **COMPLETE** — NARROW Infrastructure Candidate；FULL forbidden；RC001 未启动 |
