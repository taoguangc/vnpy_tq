# PBR-001 — Post-Baseline Gap Review

> **Review ID**: PBR-001  
> **Title**: Post-Baseline Gap Review（基线后缺口审查）  
> **Date**: 2026-07-20  
> **Status**: Completed  
> **Kind**: Internal judgment（not ABR, not Spec, not Decision）  
> **Anchor**: Epoch 1 Stable Checkpoint（`573e31e` / `architecture-baseline-v1`）  
> **Path**: `docs/reviews/PBR-001_POST_BASELINE_GAP_REVIEW.md`

**一句话**：在不改代码、不改 Contract、不启动 Sprint 的前提下，判断 Sprint 2 是否值得被证据驱动地提出。

```text
Stable Checkpoint → Gap Review → Need identified? → Sprint Proposal → Sprint Start
```

---

## 1. What we already have

### 1.1 Evidence production — Capable

```text
Experiment → Artifact → EvidenceRecord → EvaluationResult → Repository
```

研究结果可以按 Append-only 契约沉淀。

### 1.2 Evidence consumption — Capable（Sprint 1）

```text
Repository → ReadView → Projection → Portfolio
```

研究结果可以被只读消费；Zero Knowledge Duplication / ABR-002 已验证。

### 1.3 Governance — Capable

```text
Decision → Contract → Implementation → Contract Test → ABR → Checklist
```

演进路径可约束；Baseline 可审计。

---

## 2. Review questions

| # | Question | Answer |
|---|----------|--------|
| 1 | 当前 Platform 是否存在**阻塞研究**的问题？ | **Partial Yes** — 单实验闭环可用；**跨 Evidence 比较**尚未成为一等能力 |
| 2 | 哪些能力缺失？ | 见 Findings F1–F3 |
| 3 | 哪些能力只是便利功能？ | 见 Non-gaps |
| 4 | 下一 Sprint 是否必要？ | **Not yet authorized** — 候选清晰；须正式 Sprint Start Check 后再启 |

---

## 3. Findings

### F1 — Evidence comparison missing

```text
Finding:     Evidence comparison missing
Impact:      High
Kind:        Capability gap（阻塞“值得相信的证据”运营）
Candidate:   Validation Projection / Validation Infrastructure
             （Evidence Validation — 非策略回测验证）
Decision:    Consider Sprint 2
```

**现象**：单实验 `Experiment → Evidence → Evaluation` 完整；多实验 / 多品种 / 多版本场景缺乏统一的只读比较与晋级判断视图。

**典型研究问题（当前难以一等回答）**：

- 哪个 Evidence 更可靠？
- 哪些实验已被证伪 / HOLD？
- 哪些结果可进入下一阶段？
- 多实验如何关联（parent / subject / symbol）？

**示例期望（说明性，非 Spec）**：

输入：已存 Evidence / Evaluation 字段（decision、metrics、CI 等）  
输出：Validation Summary（Status / Reason / Recommendation）  
约束：**不产生新 Evidence；不重算 Evaluation；只解释已有记录**。

符合：*Projection may aggregate knowledge, but never derive new evidence.*

### F2 — Cross-experiment query surface thin

```text
Finding:     Cross-experiment list/filter is ad hoc
Impact:      Medium
Kind:        Convenience overlapping F1
Candidate:   Minimal query helpers inside Validation Projection
             （不必先做独立 Query Engine）
Decision:    Fold into Sprint 2 candidate scope if opened; else defer
```

Portfolio 按桶汇总，不等于“按 subject / symbol / parent 比较多条 Evidence”。

### F3 — Promotion / do-not-promote is still narrative

```text
Finding:     Promotion recommendation lives in prose / human memory
Impact:      Medium
Kind:        Process gap，可由 F1 输出承载
Candidate:   Validation Report recommendation field（derived only）
Decision:    Consider with F1; do not invent Domain promotion object
```

---

## 4. Non-gaps（便利功能，不阻塞，不启动 Sprint）

| Item | Why not now |
|------|-------------|
| Portfolio Dashboard UI | 功能愿望；Portfolio Projection 已够 First Consumer |
| Timeline / Analytics / Knowledge Graph | Projection Spec 预留；非当前阻塞 |
| Repository rename（REPO-001） | 治理 Backlog；非研究阻塞 |
| CLEANUP Signal 表述 | 文档治理；非能力缺口 |
| Market State / Decision Engine / Execution | 路线图后置；改 Baseline 风险高 |
| New OPP / Alpha sprint | Research 冻结；平台领先于 Alpha 是健康状态 |

---

## 5. Sprint 2 candidate（未启动）

**若**未来通过 Sprint Start Check，建议启动语保持：

> **Start Platform Construction Sprint 2: Validation Infrastructure consumes Evidence Repository under Architecture Baseline v1.**

### Sprint Start Check（预填，非正式授权）

| Question | Draft answer |
|----------|--------------|
| What existing Contract does this consume? | Projection Layer Spec + Evidence Domain + Storage（read-only） |
| What Evidence/Capability gap does it solve? | **F1** — 跨 Evidence 比较与 Evidence Validation 视图 |
| Why cannot this wait? | **尚未强制** — 有空窗期价值；待用户明确“比较多条 Evidence”为当前研究阻塞时再启 |
| Does it modify Baseline? | **No**（目标约束）；若需新基础 Contract → 中止 Sprint，改走 Decision |

### Validation 边界（预登记，非 Spec）

```text
Evidence → Evaluation → Validation（判断证据质量）
```

禁止：

```text
Validation → 重新计算 / 制造 Evidence
```

---

## 6. PBR Decision

```text
PBR-001 Decision

Core gap:     F1 Evidence comparison / Evidence Validation
Sprint 2:     CONSIDER（candidate clear）— NOT STARTED
Authorize:    No implementation, no Spec expansion, no Contract
Next gate:    Explicit user Start line + Sprint Start Check all Yes/No as required
Proposal:     docs/development/SPRINT_2_PROPOSAL.md（Validation Projection；Draft）
```

Epoch 1 Stable Checkpoint **保持成立**。空窗期继续保护 Baseline。

---

## 7. Explicitly out of scope for this review

- 写代码 / 改 Repository 语义  
- 新增或修改 Accepted Contract  
- 开 Sprint 2 / 写 Validation Spec  
- Push 策略变更  

---

## 修订记录

| 日期 | 说明 |
|------|------|
| 2026-07-20 | Completed：F1 High → Consider Sprint 2；当前不启动 |
