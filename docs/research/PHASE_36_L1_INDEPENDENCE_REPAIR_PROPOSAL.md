# Phase 3.6 L1 — Independence Repair Proposal

> **Type**: Exit Criteria L1 Proposal（≠ Experiment Auth · ≠ Spec Confirmation · ≠ Observation）  
> **Status**: **Confirmation PASS** ✓ — Eligible for L1 Independence Specification  
> **Version**: 0.2  
> **Date**: 2026-07-21  
> **Path**: `docs/research/PHASE_36_L1_INDEPENDENCE_REPAIR_PROPOSAL.md`  
> **Parent**: [`PHASE_36_EXIT_CRITERIA_RESOLUTION.md`](PHASE_36_EXIT_CRITERIA_RESOLUTION.md)  
> **Gate**: [`CONTEXT_CAPABILITY_GATE_V2_REVIEW.md`](CONTEXT_CAPABILITY_GATE_V2_REVIEW.md) — CONDITIONAL · Exit Criterion **L1**  
> **Knowledge**: K001 Strengthened Qualified + Independence Narrow（**unchanged**）  
> **Prior**: Draft v0.1 → PASS WITH REVISION → v0.2 → **Confirmation PASS**  
> **Spec**: [`CAP_CTX_001_L1_INDEPENDENCE_SPECIFICATION.md`](CAP_CTX_001_L1_INDEPENDENCE_SPECIFICATION.md) — **Confirmation PASS**  
> **Fill**: [`CAP_CTX_001_L1_PRE_REGISTRATION_FILL.md`](CAP_CTX_001_L1_PRE_REGISTRATION_FILL.md) — **Draft v0.1**

### Confirmation（binding）

```text
================================================
PHASE 3.6 L1 INDEPENDENCE REPAIR PROPOSAL v0.2

Confirmation: PASS ✓

C1 Research Object Stability: PASS ✓
C2 Frozen Object Rule: PASS ✓
C3 Independence Target I2+I3: PASS ✓
C4 Generation ≠ Evaluation: PASS ✓
C5 Outcome Matrix（FAIL ≠ K001 false）: PASS ✓
C6 L1 ≠ Gate Unlock: PASS ✓

Eligible next: L1 Independence Specification Draft

Spec / Fill / Auth / Observation: NOT STARTED / NONE
K001: unchanged
Gate v2: CONDITIONAL / CLOSED
RC001 / Strategy: deferred / not started
================================================
```

---

## 1. Why L1 now（watershed）

| Question | Status |
|----------|--------|
| Context 是否可能含跨品种/时间/可重复描述结构？ | **有证据支持** |
| Context 是否可作为交易系统稳定输入？ | **尚未回答** |

Gate v2 = **CONDITIONAL** 主因是 **P4 Independence PARTIAL**。  
L1 修复**评价独立性 / 定义耦合**，不是继续证明 K001，也不是重新寻找更好的 Context 定义。

```text
挑战已有 Knowledge 的证据生成过程
        ≠
重新探索 Alpha / Feature Engineering
```

---

## 2. Research Question（R1 · binding）

### EQ framing（keep）

```text
Can K001-supported descriptive structure survive under a
less definition-coupled evidence generation process?
```

中文：

> 在降低定义耦合的证据生成过程下，K001 所支持的 descriptive structure 是否仍能成立？

### Forbidden reformulation

```text
❌ Can we find a better independent Context representation?
❌ 换一个更有效的 Context / 指标 / Family
```

前者 = 挑战已有 Knowledge；后者 = 失焦到 Alpha / Feature Engineering。

---

## 3. Frozen Object Rule（R2 · binding）

```text
Change HOW evidence is produced
NOT
Change WHAT is being claimed
```

### Must NOT change（Frozen）

| 项 | Status |
|----|--------|
| K001 Claim / Claim Boundary | **Frozen** |
| Research Question（上节 EQ） | **Frozen** |
| Universe | **Frozen**（除非未来 Spec **显式**单变量并另授；默认冻结） |
| Temporal / Cross Evidence lineage（RUN001–005 Closed） | **Frozen** |
| Governance Contract（Evidence≠Knowledge≠Gate≠Alpha） | **Frozen** |

### May change（Allowed）

| 项 | Status |
|----|--------|
| Evidence generation dependency | **Allowed** |
| Evaluation dependency | **Allowed** |
| Measurement independence（相对原耦合路径） | **Allowed** |

违反 Frozen Object Rule → **Execution Invalid**（≠ Independence FAIL）。

---

## 4. M1 definition coupling — core risk（R3）

### Risk chain

```text
M1 volatility
        ↓
partition by M1
        ↓
evaluate M1 separation
```

→ measurement → label → proof 风险。

### Forbidden “fix”

```text
❌ M1 → 换 M3 → 重新跑
```

这只是换指标，不是修独立性。

### Required separation

| Layer | Role |
|-------|------|
| **Generation** | 产生 Context observation（e.g. volatility / price / liquidity **condition**） |
| **Evaluation** | 使用**不与 Observation 恒等**的外部度量（e.g. future realized behavior、holding stability、distribution shift、cross-condition consistency） |

```text
Evaluation must not be the Observation itself
```

具体 Generation/Evaluation 配方 **不在本 Proposal 冻结**；须在 Spec 按 Frozen Object Rule + I2/I3 填写。

---

## 5. Primary Independence Target（R4 · binding）

沿用 Phase 3.4 Taxonomy I1–I5。

### Frozen for L1 instance

```text
Primary Target: I2 Measurement Independence
              + I3 Evaluation Independence
```

| Axis | L1 role |
|------|---------|
| **I2** | 降低 measurement / partition 与被证对象的耦合 |
| **I3** | Evaluation 与 Observation 分离 |
| I1 Dataset | **非本阶段主目标**（P1–P3 扩样已完成） |
| I4 / I5 | 可披露 Residual；非 Primary unless Spec 另授 |

```text
I2 + I3 frozen as Primary Target
        ≠
concrete metrics frozen（→ Spec）
```

---

## 6. Outcome Interpretation Matrix（R5 · binding）

```text
PASS ≠ “K001 forever true”
FAIL ≠ “K001 false”
```

| Result | Meaning |
|--------|---------|
| **PASS** | K001 robustness strengthened under less-coupled evidence generation（P4-facing） |
| **PARTIAL** | Claim narrowing required（Independence / scope） |
| **FAIL** | Current evidence generation insufficiently independent / too coupled |
| **INVALID** | Process violation（Frozen Object / protocol）— 非 Knowledge 结果 |

```text
FAIL
  =
evidence-generation path inadequate for Independence claim
  ≠
descriptive structure does not exist
  ≠
K001 false
```

Registered Actions 预览（Fill 冻结）：PASS→STRENGTHEN（Independence）；PARTIAL→NARROW；FAIL→NARROW/DOWNGRADE；INVALID→无 Knowledge Action。

---

## 7. Relation to Gate v2（R6 · binding）

```text
L1 = Capability Evidence Preparation
L1 ≠ Gate Unlock Experiment
```

```text
L1
        ↓
Evidence update（K001 / P4 另授 Review）
        ↓
Gate v2 Re-Review（另授）
        ├─ remain CONDITIONAL / BLOCK
        └─ Candidate evaluation path（若达标）
```

**禁止**：

```text
“做 L1 是为了过 Gate”
→ confirmation bias
```

L1 成功 ≠ Gate PASS；须独立 Re-Review。

---

## 8. Strategy Entry Gate（unchanged intent · clarified）

见 Phase 3.6 主文档 SE-G1…G3。摘要：

| ID | Requirement |
|----|-------------|
| **SE-G1** | Capability Candidate（**不是**仅 K001 Qualified） |
| **SE-G2** | Context Interface Defined：decision variable（filter/risk/selection）≠ entry signal |
| **SE-G3** | RC001：Strategy vs Strategy+Context — 非直接开发 PAAF Strategy |

本 L1 **不**启动 Strategy / Backtest。

---

## 9. Non-goals

```text
❌ 寻找更好的 Context 表示 / Feature Engineering
❌ M1→M3 换皮重跑
❌ P1–P3 样本堆叠（RUN006-style）
❌ Gate Unlock / Candidate / RC001 / PnL
❌ 改写 Closed RUN001–005
❌ 改变 K001 Claim 内容（仅允许另授 Narrow 结果）
```

---

## 10. Deliverables if Confirmation PASS

```text
L1 Proposal Confirmation
        ↓
L1 Experiment Specification（Generation≠Evaluation；I2+I3；Frozen Object）
        ↓
Fill → Auth（各另授）
        ↓
Observation → Evidence → Reviews（另授）
        ↓
Gate Re-Review（另授；非自动）
```

---

## 11. Checklist（v0.2）

| ID | Check | Verdict |
|----|-------|---------|
| L1P1 | RQ = survive under less coupling；≠ better Context | **PASS** |
| L1P2 | Frozen Object Rule | **PASS** |
| L1P3 | Generation ≠ Evaluation；禁止 M1→Mx 换皮 | **PASS** |
| L1P4 | Primary Target I2+I3 frozen | **PASS** |
| L1P5 | Outcome Matrix；FAIL ≠ K001 false | **PASS** |
| L1P6 | L1 ≠ Gate Unlock Experiment | **PASS** |
| L1P7 | No Spec/Obs/Strategy authorized | **PASS** |

> Checklist PASS ≠ Proposal Confirmation PASS。

---

## 12. Next

```text
Confirmation PASS ✓
        ↓
L1 Spec Draft v0.1 — [`CAP_CTX_001_L1_INDEPENDENCE_SPECIFICATION.md`](CAP_CTX_001_L1_INDEPENDENCE_SPECIFICATION.md)
        ≠
Fill / Auth / Observation / Strategy
```

当前：**Confirmation COMPLETE**；Spec Draft opened；Experiment **NOT AUTHORIZED**。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | 首版：L1 Independence Repair；挑战耦合；非扩样本 |
| 2026-07-21 | 0.2 | PASS WITH REVISION：Frozen Object；I2+I3；Gen≠Eval；Outcome Matrix；≠Gate Unlock |
| 2026-07-21 | 0.2.1 | **Confirmation PASS**；Eligible for L1 Spec |
