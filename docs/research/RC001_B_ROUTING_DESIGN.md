# RC001-B — Context Routing Design

> **Type**: Controlled Experiment Design（Phase B · Context as Routing / Permission）  
> **Status**: **Contract FROZEN** ✓ — Design **CONFIRMED** · Execution **NOT AUTHORIZED**
> **Version**: 0.1  
> **Date**: 2026-07-21  
> **Path**: `docs/research/RC001_B_ROUTING_DESIGN.md`  
> **Contract**: [RC001_B_CONTRACT_FREEZE.md](RC001_B_CONTRACT_FREEZE.md) — **FROZEN**  
> **Confirmation**: [`RC001_B_DESIGN_CONFIRMATION.md`](RC001_B_DESIGN_CONFIRMATION.md) — **PASS**  
> **Authorization**: [`RC001_B_DESIGN_AUTHORIZATION.md`](RC001_B_DESIGN_AUTHORIZATION.md) — **GRANTED**  
> **Parent Decision**: [`RC001_DECISION_REVIEW.md`](RC001_DECISION_REVIEW.md) — CLOSE A · Route A  
> **Prior**: RC001-A EXP001 **CLOSED** · PARTIAL · NOT ACCEPTED  
> **Context**: A1 `ContextState.v1` · Decision 019  
> **Capability**: NARROW Infrastructure Candidate  
> **experiment_id（proposed）**: `RC001_B_EXP001`

### Design Record（binding）

```text
================================================
RC001-B ROUTING DESIGN v0.1

Status: CONFIRMED ✓
Contract: FROZEN ✓
Confirmation: PASS

Object: Context → Strategy Routing / Permission
NOT: Signal · Alpha · Position sizing · Filter remap of FP-RC001-A-v1

Next: Contract Freeze（另授）→ Execution Auth（另授）→ Backtest
================================================
```

```text
Design CONFIRMED ≠ Contract Frozen ≠ Execution ≠ Backtest
FAIL ≠ K001 false ≠ Context useless
PASS ≠ Alpha ≠ Gate PASS ≠ RC001 Accepted
```

---

## 1. Research Question（frozen）

### RQ-RC001-B

> ContextState 是否能够改善已有策略之间的环境匹配（strategy routing quality），而不是作为预测信号或收益来源？

### Formal

```text
RQ-RC001-B:

Given fixed strategies S1/S2 and fixed ContextState.v1,
does Context-based routing reduce strategy-context mismatch
compared with static routing?
```

### Not the question

```text
❌ Context → 预测收益 / 预测方向
❌ Context → 产生交易信号
❌ Context → 直接提高年化 / Sharpe（sole claim）
❌ Context manufactures Alpha
```

---

## 2. Hypotheses

### H1（allowed）

```text
ContextState
      ↓
Strategy compatibility
      ↓
Routing decision
```

Context provides environment description that improves **match** between active strategy and environment versus static allocation.

### H0（Null）

Context routing does not materially differ from static routing on pre-registered routing-quality metrics.

### Forbidden hypotheses

```text
❌ Context predicts price direction
❌ Context creates alpha
❌ Context improves returns directly（as primary H1）
```

---

## 3. Strategy Pair Selection Criteria（frozen）

### Principle

Do **not** pick two “strong / profitable” strategies. Prefer **orthogonal environment assumptions** so Context contribution is attributable.

| Role | Class | Environment assumption |
|------|-------|------------------------|
| **S1（Strategy A）** | Breakout / Trend Following | Benefits from sustained directional movement / expansion-like conditions |
| **S2（Strategy B）** | Mean Reversion / Range | Benefits from oscillatory / compression-like conditions |

### Mandatory selection gates

| Condition | Required |
|-----------|----------|
| Already exists in repo / Closed evidence lineage | ✓ |
| Independent of Context（no Context inside strategy） | ✓ |
| Parameters frozen before Execution | ✓ |
| Not newly designed for this experiment | ✓ |
| Explicit environment suitability hypothesis | ✓ |
| Not selected for historical PnL ranking | ✓ |

### Concrete lock

```text
S1/S2 identity → Contract Review / Spec Confirmation
Design freezes CLASS + CRITERIA only
```

Candidate search space（illustrative · not locked IDs）:

```text
S1 class: Trend / Breakout family（existing CTA / PA trend modules）
S2 class: Mean-reversion / Range family（existing mean-reversion / range modules）
```

If no qualifying pair exists at Contract time → **BLOCK Execution**（Design remains；do not invent strategies inside RC001-B）.

---

## 4. Routing Contract（Design freeze）

### Input

```text
ContextState.v1 / A1-CTX-PS-v1.0.0
context_state ∈ {compression, expansion, invalid}
validity ∈ {VALID, DEGRADED, INVALID}
```

### Output vocabulary（only）

```text
ROUTE_S1 | ROUTE_S2 | MONITOR_ONLY
```

Equivalently per strategy:

```text
ALLOW(S1) / BLOCK(S1)
ALLOW(S2) / BLOCK(S2)
```

with at most one `ALLOW` active strategy at a time（Phase B default），or MONITOR_ONLY（flat / no new risk）.

### Proposed single-path mapping **RP-RC001-B-v1**（pre-register · Contract locks）

| Condition | Route |
|-----------|-------|
| `validity ∈ {INVALID, DEGRADED}` OR `context_state == invalid` | **MONITOR_ONLY** |
| `compression` + VALID | **ROUTE_S2**（mean-reversion / range） |
| `expansion` + VALID | **ROUTE_S1**（trend / breakout） |

```text
Mapping frozen before any backtest
❌ Remap after peeking
❌ confidence × position
❌ context score / edge ranking / future return estimate
```

### Consumption boundary（Decision 019）

```text
Context: Infrastructure
Consumption: Routing / Permission
Not: Signal
Not: Alpha
Not: Position sizing
```

---

## 5. Dual-arm design（concept）

### Unique variable

```text
Change = Context-based routing policy
Everything else = frozen（S1, S2, params, data, costs, exits per strategy）
```

### CTRL — Static routing

**SR-RC001-B-v1**（proposed · Contract locks one）:

```text
Alternate or fixed split without Context:
  Default proposal: time-sliced 50/50
  - Even calendar days → S1 only
  - Odd calendar days → S2 only
OR equal-capital parallel with independent signals（if Spec prefers）
```

Design default for attribution clarity:

```text
CTRL = calendar 50/50 exclusive activation（one strategy live at a time）
```

### ROUTE — Context routing

```text
ContextState → RP-RC001-B-v1 → exclusive ROUTE_S1 | ROUTE_S2 | MONITOR_ONLY
```

### Topology

```text
        Market Data
             |
     +-------+-------+
     |               |
    S1              S2
     |               |
     +-------┼-------+
             |
      CTRL: static rule
      ROUTE: Context router
             |
           Trades
```

```text
Context does not enter S1/S2 signal engines
```

---

## 6. Evaluation Matrix

### Primary（decision-relevant）

| ID | Name | Question |
|----|------|----------|
| **E1** | Routing Quality | Does ROUTE reduce strategy–context mismatch vs CTRL? |
| **E2** | Stability | Is routing stable（switch rate, concentration, pathological stickiness）? |
| **E3** | Attribution | Is any improvement attributable to routing vs S1/S2 standalone edges? |

#### E1 operationalization（Design direction · Spec freezes numbers）

```text
Mismatch proxy（illustrative）:
  S1 active under compression → mismatch++
  S2 active under expansion → mismatch++
  MONITOR_ONLY / aligned pairs → not mismatch
Report: mismatch rate CTRL vs ROUTE
```

#### E2 operationalization

```text
switch_frequency
time_share(S1), time_share(S2), time_share(MONITOR)
flag pathological: >95% one route or flip every bar
```

#### E3 operationalization

```text
Compare:
  ROUTE vs CTRL on E1
  + S1-only / S2-only baselines（optional arms or counterfactual）
Must not credit Context for S1/S2 raw edge
```

### Secondary（auxiliary only）

| ID | Metric |
|----|--------|
| S1 | PnL / return Δ |
| S2 | Sharpe Δ |
| S3 | Drawdown Δ |

```text
Secondary ≠ sole success criterion
❌ Maximize return / Sharpe as search objective
```

---

## 7. Outcome labels

| Outcome | Meaning |
|---------|---------|
| **PASS** | Routing evidence supports H1 under frozen metrics |
| **PARTIAL** | Routing effect observable but limited / mixed value |
| **FAIL** | No material routing improvement vs static |
| **INVALID** | Protocol / identity / Decision 019 violation |

### Non-interpretations

```text
FAIL ≠ K001 false
FAIL ≠ Context has no research value
PASS ≠ Alpha
PASS ≠ Gate PASS / FULL Candidate / RC001 Accepted
PASS ≠ license live trading
rb-only（if Spec chooses）≠ multi-symbol capability
```

---

## 8. Relation to RC001-A

| RC001-A | RC001-B |
|---------|---------|
| Consumption = **Filter** on one baseline（OPP16） | Consumption = **Routing** across two strategies |
| Outcome PARTIAL · CLOSED · NOT ACCEPTED | New `experiment_id` |
| FP-RC001-A-v1 immutable Closed evidence | **RP-RC001-B-v1** new policy（not a silent remap of A） |

```text
Do not “fix A Filter and re-run”
B is a new consumption pattern under new identity
```

---

## 9. Deliverables of this Design phase

| # | Deliverable | Status |
|---|-------------|--------|
| 1 | Design Proposal（this doc） | ✓ |
| 2 | Routing Contract（§4 · RP-RC001-B-v1 draft） | ✓ |
| 3 | Strategy Pair Selection Criteria（§3） | ✓ |
| 4 | Evaluation Matrix（§6–7） | ✓ |
| — | Code / Backtest | **OUT OF SCOPE** |

---

## 10. Lifecycle / next gates

```text
RC001-B Design COMPLETE（this doc）
        ↓
Design Review → Confirmation（另授）
        ↓
Contract Freeze（S1/S2 IDs · RP lock · CTRL static rule · numeric E*）
        ↓
Execution Authorization（另授）
        ↓
Backtest
        ↓
Evidence Review
```

### Current position

```text
RC001-B Design: AUTHORIZED ✓ · COMPLETE ✓
Confirmation: PASS ✓
Execution: NONE
Code: NONE
Backtest: NONE
Strategy Research: NOT STARTED
```

### Next authorization entry

```text
Authorize RC001-B Execution Authorization
```

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | Design COMPLETE：RQ/H0-H1；S1/S2 正交准则；RP-RC001-B-v1；E1–E3 主评价；Confirmation PENDING |
| 2026-07-22 | 0.1 | **Confirmation PASS** — Contract Freeze 另授 |
| 2026-07-22 | 0.1 | **Contract FROZEN** — Execution 另授 |
