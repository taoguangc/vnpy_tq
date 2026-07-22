# Strategy Research Phase — Authorization

> **Type**: Phase Authorization（≠ Strategy Implementation · ≠ Backtest · ≠ RC001-B reopen）  
> **Status**: **GRANTED** ✓  
> **Date**: 2026-07-22  
> **Command**: `Authorize Strategy Research Phase`  
> **Prior**: [`EPOCH_4_CLOSURE.md`](../releases/EPOCH_4_CLOSURE.md) — CAP-CTX-001 **CLOSED** · was NO ACTIVE PHASE  
> **Positioning**: [`EPOCH_5_POSITIONING.md`](../releases/EPOCH_5_POSITIONING.md)  
> **First sub-phase**: Strategy Asset Contract Design（authorized below）

### Authorization Record（binding）

```text
================================================
Authorize Strategy Research Phase

Decision: GRANTED ✓

Active Phase: Strategy Research（Epoch 5）
CAP-CTX-001: remains CLOSED（not reopened）
RC001-B: remains PERMANENTLY CLOSED（not reopened）

Gate v2: UNCHANGED（CONDITIONAL）
Capability: UNCHANGED（Narrow Candidate · Infrastructure only）
K001: UNCHANGED
Trading Value of Context: still NOT PROVEN
================================================
```

---

## 1. What this authorizes

```text
Allows:
  - Epoch 5 Strategy Research Phase start
  - Strategy Asset Layer framing
  - Strategy Identity / Asset Contract Design
  - Strategy Evidence Chain Design
  - Strategy Validation Framework Design（governance only）
  - Inventory of candidate strategy families under Contract rules
  - Documentation of entry criteria for later bindable assets

Does NOT authorize（this command alone）:
  - Writing / shipping new CTA strategy code
  - Parameter search / PnL optimization
  - Backtest / Observation runs
  - Portfolio Construction execution
  - Live / simulation trading
  - Reopen RC001-B or mutate RP/SR-RC001-B
  - Context Capability upgrade claims
  - “Context → Alpha” experiments
```

---

## 2. Core research question（Epoch 5）

Closed（Epoch 4）:

```text
Context 是否值得作为受限基础设施候选？
```

Open（Epoch 5）:

```text
什么样的策略资产才值得被 Context 安全消费？
```

```text
Strategy Asset Layer
        ↓
Context Consumer Layer（future · separate auth）
        ↓
Portfolio Layer（future · separate auth）
```

Primary objective now: **bindable, auditable strategy assets** — not immediate return hunting.

---

## 3. First authorized sub-phase

| Sub-phase | Status | Next gate |
|-----------|--------|-----------|
| **5.0 Phase Authorization** | **GRANTED** ✓ | — |
| **5.1 Strategy Asset Contract Design** | **CONFIRMED** ✓ | Contract Freeze（另授） |
| **5.1b Strategy Asset Contract** | `SAC-v1` **FROZEN** ✓ | Validation Framework Design（另授） |
| **5.2 Evidence / Validation Framework** | `SEVF-v1` **FROZEN** ✓ | Family Inventory Protocol Design（另授） |
| **5.3 Family Inventory Protocol** | `SAFIP-v1` **FROZEN** ✓ | Bounded Inventory Review |
| **5.3a Family Inventory Review** | **COMPLETE** ✓ · no Testing-eligible asset | Candidate Admission Protocol Design（另授） |
| **5.3b Candidate Source Admission** | **COMPLETE** ✓ · one source admitted | Identity Draft / Source Recovery Design |
| **5.3c Candidate Identity Draft / SCIDR** | `SCIDR-v1` **FROZEN** · CID_001 **DRAFT** · recovery **REFERENCE_ONLY_IN_GIT** | Identity Freeze / Restore / PAAF Rewrite（另授） |
| 5.4 Strategy implementation / OOS | NOT AUTHORIZED | after Identity Freeze |
| 5.5 Context Consumer Experiment | NOT AUTHORIZED | after bindable pair exists |
| 5.6 Portfolio Construction | NOT AUTHORIZED | later |

```text
Authorize Strategy Research Phase
        =
authorize Phase + Contract Design start
        ≠
authorize coding / backtest / portfolio
```

---

## 4. Hard boundaries

```text
❌ Reopen RC001_B_EXP001
❌ Fabricate strategies solely to unblock historical C-BIND
❌ Optimize for backtest PnL
❌ Treat Narrow Candidate as FULL / mature Context Capability
❌ Claim Context trading edge from this Phase start
❌ Skip Strategy Identity Contract before implementation
❌ Mix Context routing experiment into Strategy Asset Design
```

Data freeze（when Observation later authorized）remains:

```text
TQ offline · 1m · CbC · unadjusted · real costs
```

---

## 5. Immediate next action

```text
Completed: Strategy Asset Contract Design → Confirmation PASS → SAC-v1 Freeze
Completed: Evidence / Validation Framework → Confirmation PASS → SEVF-v1 Freeze
Completed: Family Inventory Protocol → Confirmation PASS → SAFIP-v1 Freeze → Review
Completed: Candidate Admission → SCAP-v1 → SCIDR-v1 → CID_001 Identity Draft
Stop:      REFERENCE_ONLY_IN_GIT; no working-tree restore; no Identity Freeze; no backtest
```

Until later scoped authorization: **no restore · no rewrite · no Identity Freeze · no backtest**.

---

## 修订记录

| 日期 | 说明 |
|------|------|
| 2026-07-22 | Strategy Research Phase **GRANTED**；sub-phase 5.1 Contract Design authorized |
| 2026-07-22 | 5.1 Contract Design Confirmation **PASS**; Freeze remains separately authorized |
| 2026-07-22 | `SAC-v1` Contract Freeze **FROZEN**; no asset selected or identity frozen |
| 2026-07-22 | Delegated decision: 5.2 Framework Design authorized; Draft created |
| 2026-07-22 | Three-round delegation: Framework Confirmation PASS → `SEVF-v1` FROZEN → Family Inventory Protocol DRAFT |
| 2026-07-22 | Ten-round delegation: `SAFIP-v1` FROZEN; bounded inventory COMPLETE; no Testing-eligible asset and no selection |
| 2026-07-22 | Five-round delegation: `SCAP-v1` FROZEN; `brooks_scalp` admitted as Candidate Source only |
| 2026-07-22 | Five-round delegation: `SCIDR-v1` FROZEN; CID_001 draft complete; recovery REFERENCE_ONLY_IN_GIT |
| 2026-07-22 | Twenty-round delegation: ADAP/CEMB frozen; Freeze readiness NOT READY; Rewrite charter design-only; STOP 16/20 |
