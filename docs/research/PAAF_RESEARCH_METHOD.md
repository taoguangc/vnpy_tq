# PAAF Scientific Method（PRM v1.0）

> **PAAF Scientific Method (PRM v1.0)**  
> This document serves as the **research playbook** for all Research Campaigns.

> **Status**: Accepted  
> **Version**: 1.0.0  
> **Date**: 2026-07-20  
> **Kind**: Scientific Method（哲学层）+ Playbook（操作层）  
> **Epoch**: 1.5 — Research Methodology；**Epoch 1 最后一个值得沉淀的文档**  
> **Authority**: `AGENTS.md` > Accepted Decisions & Specs > **本 Method** > 临时话术  
> **Path**: `docs/research/PAAF_RESEARCH_METHOD.md`

**不变的核心循环**：

```text
Question → Hypothesis → Evidence → Validation → Knowledge
```

Profit 是 Knowledge 的 downstream consumer，不是第一层输出。

---

## Chapter 0 — Research Philosophy

> 以下句子均来自 Epoch 1 已 Accepted 的治理与实践；此处第一次并置为哲学。

```text
Research exists to produce trustworthy knowledge.

Profit is downstream of knowledge.

Evidence is the only source of truth.

Architecture serves research, never the opposite.

Negative Evidence has equal archival value as Positive Evidence.

Every detector is guilty until proven innocent.
```

**Method**（本文件）描述**永远不变**的研究科学方法。  
**Playbook**（下文 Step、模板、引用）描述**当前版本**如何执行；可随工具演进，但不得违背 Method。

---

## 1. 四层模型

```text
Layer 1  Research Governance     Decision / ADR / Contract / ABR / PBR
Layer 2  Research OS             Evidence / Repository / Projection / Validation
Layer 3  Research Campaign       RC001, RC002, …（须遵守 PRM）
Layer 4  Experiment              RC001 下的 EXP001, EXP002, …
```

**Repository 层次**（推荐命名）：

```text
Campaign (RC001)
    ├── Experiment (RC001_EXP001 / EXP001)
    ├── Experiment (RC001_EXP002 / EXP002)
    └── Experiment (RC001_EXP003 / EXP003)
            └── Evidence → Evaluation → Repository
```

- **RC-xxx**：研究战役；同一 Question 下的实验编排与叙事容器。  
- **EXP-xxx**：可审计实验单元；每个 EXP **一个**主要假设。  
- 新 Campaign **不要**从孤立的 `EXP001` 开始编号；先定 `RC001`，再在其下挂 EXP。

PRM 是 Layer 3 的**母协议（Meta Protocol）**；**不是**新 Contract。

**当前状态**：Layer 1–2 就绪；PRM v1.0 **Accepted**；RC-001 **未启动**。

---

## 2. Scientific Method — 七步（Playbook）

每一步映射**已有**规范；只回答「顺序与何时停」。

### Step 0 — Question

可证伪的研究问题，不是功能愿望。

| 好 | 差 |
|----|-----|
| Compression 是否提高 Breakout 条件期望？ | 做一个 VWAP Dashboard |

不可证伪 → 重写 Question，不开 Campaign。

### Step 1 — Hypothesis

单句、可检验、与 Question 对应。OPP / Feature / Detector 只是载体。

### Step 2 — Campaign（RC-xxx）

见 §4 Research Campaign 模板。Campaign 结束：实验矩阵完成 / Negative 足以关闭 Question / 用户授权关闭并写入 Evidence。

### Step 3 — Experiment Design

每 EXP 满足 `experiments/schema.yaml` 与 `docs/06_RESEARCH_WORKFLOW.md` §3。Closed 不可复活；跨品种用新 `experiment_id`（可 `parent=`）。

### Step 4 — Evidence

```text
Experiment → Artifact → Evaluation → EvidenceRecord → Repository
```

Append-only；Negative / HOLD / REVERT 同等归档；无 CSV 不得称已证实。

### Step 5 — Evaluation

KEEP / REVERT / HOLD。KEEP ≠ Production。

### Step 6 — Cross Validation

新 experiment_id；Validation Projection 只读比较；不重算 Evidence。

### Step 7 — Promotion（可见性）

`PromotionReadinessView`：`may_auto_promote=False`。可描述状态，不可决定上线。Production：Decision 011 + E4 + 用户确认。

---

## 3. 端到端流程

```text
Question → Hypothesis → Campaign (RC) → Experiments (EXP) × N
    → Run → Evidence → Repository → Validation View → Knowledge → Next Question
```

**禁止**：

```text
Idea → Backtest profit → Production
```

---

## 4. Research Campaign 模板

复制以下块开启 **RC-xxx**（首个授权 Campaign 可建 `docs/campaigns/RC001.md`）：

```markdown
# RC-xxx — <Campaign Title>

## Research Question

<可证伪问题>

## Background

<为何现在问；与既有 Evidence 的关系>

## Hypothesis

<单句或假设族；每 EXP 一个主要假设>

## Evidence Needed

<须进入 Repository 的产物：Artifact / Evaluation / Evidence 字段>

## Experiment Design

| ID | Symbol / Scope | 主要变量 | 停止条件 |
|----|----------------|----------|----------|
| RCxxx_EXP001 | rb | … | … |
| RCxxx_EXP002 | hc | … | … |

## Acceptance Criteria

<Campaign 何时算完成；HOLD/REVERT 是否足以关闭>

## Promotion Boundary

<明确：本 Campaign 不自动晋级；Production 门槛引用 Decision 011>

## Expected Outputs

- docs/experiments/<EXP>.md
- research/output/evidence/<experiment_id>/
- Validation Comparison（若多 EXP）
```

---

## 5. AI Agent 开场（强制习惯）

研究任务**先**填，再写代码：

```text
Research Question:
Hypothesis:
Campaign ID (RC-xxx):
Experiment ID(s):
Evidence Needed:
Modifies Baseline? (default: No)
```

默认第一句**不是** `Implement…`。

Pre-Merge / Sprint：`docs/development/REVIEW_CHECKLIST.md`。

---

## 6. 权威细则索引（Playbook 引用）

| PRM Step | 权威 |
|----------|------|
| 0–1 | `01_CONSTITUTION.md`、`AGENTS.md` |
| 3–5 | `docs/06_RESEARCH_WORKFLOW.md`、`experiments/schema.yaml` |
| Evidence | `EVIDENCE_DOMAIN_SPEC`、`APPEND_ONLY_STORAGE_SPEC` |
| Validation | `PROJECTION_LAYER_SPEC`、Validation Projection |
| Promotion | Decision 011、015；`docs/03_DETECTOR_SPEC.md` |
| 路线图 | Decision 017、018 |

冲突时以 Decision / Spec 为准；Method 不变，Playbook 可增补。

---

## 7. 什么不是 PRM

- ❌ 新 Contract / Domain / Repository 语义  
- ❌ 新 Decision（除非真实架构变更）  
- ❌ Sprint / RC-001 自动授权  

---

## Chapter Last — Failure

研究何时算**失败**？

**不是**亏钱。

```text
Hypothesis rejected
        ↓
Negative Evidence
        ↓
Archived in Repository
        ↓
Knowledge increased
        ↓
Research successful
```

| 失败（真） | 成功（含 Negative） |
|------------|---------------------|
| 无 Evidence 就下结论 | REVERT / HOLD 写入 Repository |
| 删除或淡化 Negative | Validation 可引用、可比较 |
| 重复投入已证伪假设 | Campaign 明确关闭并记录 blocking |
| 为 PnL 改结论 | 下一 Question 来自 Knowledge |

**PAAF 与多数量化项目的分野**：系统性积累 Negative Evidence，避免重复犯错——长期价值常高于偶然 Alpha。

---

## 8. 下一阶段门禁

```text
PRM v1.0 Accepted ✓
        ↓
Research Question（证据驱动）
        ↓
RC-001（第一个按 PRM 执行的 Campaign）
```

**Stable Window**：Architecture Frozen；Research First。

**Epoch 1 结束条件**（愿景）：第一个候选在完整遵守 PRM 下走完  
`Hypothesis → Experiment → Evidence → Validation → Promotion → Production Candidate`  
——不以赚钱为结束条件。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-20 | 1.0.0 | Accepted：Scientific Method + Playbook；Chapter 0 / Failure / RC 模板 |
