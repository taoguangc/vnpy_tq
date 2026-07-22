# Cross Evidence Governance v1.2 — Governance Baseline

> **Kind**: Research Methodology（研究治理规范）  
> **Status**: **Governance Baseline** ✓（Review PASS WITH REVISION · 2026-07-21）  
> **Not**: System Contract / Spec / Decision / ADR  
> **Path**: `docs/research/CROSS_EVIDENCE_GOVERNANCE.md`  
> **Review**: [`CROSS_EVIDENCE_GOVERNANCE_REVIEW.md`](CROSS_EVIDENCE_GOVERNANCE_REVIEW.md)  
> **Authority**: PRM > 本文件；冲突时以 Accepted Spec / Decision 为准  
> **Derived from**: CAP-CTX-001 RUN001 + RUN002  
> **Date**: 2026-07-21 · **Version**: 1.2

---

## 0. Purpose

Cross Evidence 用于在 **已有 Qualified Knowledge** 之上，通过**独立注册的 Run** 检验、强化、收窄或降级该 Knowledge——**不是**重新发现、**不是** Gate PASS、**不是** RC001 / Alpha。

```text
Qualified Knowledge
        ↓
Cross Evidence Run（registered）
        ↓
Support / Narrow / Downgrade
        ↓
Knowledge Review（另授）
```

本文件抽象 RUN001/RUN002 已验证有效的治理规则，供 RUN003+ 及未来 CAP 研究复用。

---

## 0.1 What Cross Evidence Is Not

| 不是 | 说明 |
|------|------|
| Discovery Run | 不验证新 Hypothesis 作为首要目标 |
| Gate PASS | Strengthen / SUPPORTED ≠ Capability Proven |
| RC001 / Alpha | 不产生交易或 Opportunity 结论 |
| 结果导向调参 | 禁止为提高支持概率而改方法（见 §5） |
| 自动 Knowledge Decision | Registered Action ≠ Decision |

---

## 1. Run Types（对照）

| Type | 典型 | 首要问题 | Knowledge 影响 |
|------|------|----------|----------------|
| **Discovery** | RUN001 | Does descriptive structure exist? | 创建 Candidate → Qualified Knowledge |
| **Cross Evidence** | RUN002+ | Does qualified structure remain supported under new registered conditions? | Strengthen / Narrow / Downgrade |

```text
Discovery:
  RUN001 → K001 Qualified

Cross Evidence:
  RUN002 → SUPPORTED → STRENGTHEN → K001 Strengthened Qualified
```

两种类型共享同一套 **Evidence → Review → Knowledge** 分层；**不**共享「自动晋级」语义。

---

## 2. When to Use Cross Evidence

在以下情况启动 Cross Evidence（须新 `run_id`、完整 Spec/Fill/Auth）：

| 动机 | 示例（CAP-CTX-001） |
|------|---------------------|
| Temporal reproducibility | RUN002：2022–2023 vs RUN001 2024–2025 |
| Cross-sectional stress（未来） | RUN003+：新品种（单变量） |
| Family / Null robustness（未来） | 须单独立项；非默认 |

**不在** Cross Evidence 中同时变更多个主变量（见 §3）。

---

## 3. Single-Variable Principle

每个 Cross Evidence Run **仅允许一个主变量**：

| 可变更（一次一个） | 冻结（除非新 Run） |
|--------------------|-------------------|
| Time window | Observation families |
| Universe（截面扩展时） | Partition / metrics 定义 |
| Observation family（须单独立项） | Evaluation order / Null 协议 |
| | Data construction（CbC / 1m / 无复权） |

```text
RUN002 主变量 = Time Window only
RUN003 主变量 = Universe only（proposed；未授权）
```

**禁止同 Run 多维度同变**（示例）：

```text
时间 + 品种 + 指标 + 算法 + Null  → 禁止
```

若同时换时间 + 加品种 → 无法解释失败原因 → **禁止**。

---

## 4. Protocol Inheritance

Cross Evidence 为保持可比性，**默认继承** Parent Run 的完整协议：

> Protocol inherited from `<parent_run_id>` unless explicitly overridden by registered temporal scope (or other single registered override).

| 继承项 | 说明 |
|--------|------|
| M1/M2 / W / L | 观测与分割 |
| E1→E2→E3 顺序与阈值 | 评价链 |
| N1/N2 Null | 算法与 seed |
| Universe | 除非本 Run 主变量即为 universe |

**唯一显式覆盖**须在 Spec/Fill 中冻结（如 RUN002 的 temporal scope）。

---

## 5. Integrity Constraint（C-XEV）

**Purpose rule**（绑定所有 Cross Evidence Run）：

```text
No methodological modification shall be introduced
for the purpose of increasing support for existing knowledge.
```

强调 **purpose**，而非禁止一切方法学修改：

| 允许 | 禁止 |
|------|------|
| 治理、复现、基础设施所需且经注册的变更 | 为提高支持 K001/K00x 概率而改阈值、改 Null、改 E 顺序 |
| 新 `run_id` 下的合规协议升级 | 看到结果后再决定如何解释 |

```text
The purpose of Cross Evidence is to evaluate
previously qualified knowledge,
not to improve the likelihood of supporting it.
```

---

## 6. Lifecycle（无自动触发）

每一步须**显式 Review / Authorization**；上一步完成 **不**自动打开下一步。

```text
Cross Evidence Run Spec
        ↓ Review PASS
Pre-Registration Fill
        ↓ Confirmation PASS
Execution Authorization Review
        ↓ GRANTED WITH CONDITIONS · CP3 OPEN
Run Manifest（Identity Artifact）+ C-ENV
        ↓
Authorize Observation Execution for <run_id>
        ↓
Observation → Evaluation → EvidenceRecord
        ↓
Evidence / Cross Evidence Review
        ↓
Registered Knowledge Action（预映射）
        ↓
Knowledge Review（另授）→ Knowledge Decision
```

### Run Manifest

- **Role**: Run Identity Artifact  
- **≠** Execution Result  
- **C-ENV**: `code_revision` + `environment_identity` 须在首条 Observation bar 前写入

### Observation 入口

唯一显式指令模板：

```text
Authorize Observation Execution for <run_id>
```

---

## 7. Registered Knowledge Actions vs Knowledge Decision（C-K001）

```text
Observation
        ↓
Evaluation
        ↓
Evidence
        ↓
Registered Knowledge Action    ← 预注册映射
        ↓
Knowledge Review               ← 另授
        ↓
Knowledge Decision
```

### Pre-registered mapping（设计先于结果）

| Cross Evidence Result | Registered Action |
|-----------------------|-------------------|
| **Supported** | Strengthen qualification |
| **Partial** | Narrow scope |
| **Not supported** | Downgrade |
| **Infeasible** | No upgrade |

```text
SUPPORTED ≠ PROVEN
STRENGTHEN ≠ Knowledge Decision
RUN00x PASS ≠ Gate PASS
```

### Knowledge Review Decision vocabulary

避免简单 PASS/FAIL：

```text
ACCEPT STRENGTHENED QUALIFIED KNOWLEDGE
STRENGTHEN WITH ADDITIONAL QUALIFICATION
REMAIN QUALIFIED (NO STATUS CHANGE)
DOWNGRADE
ACCEPT WITH QUALIFICATION（Discovery 路径）
REJECT
```

---

## 8. Strengthen Semantics（KR-S 摘要）

Knowledge Strengthen Review 须审查：

| ID | 问题 |
|----|------|
| **KR-S1** | 累计 Evidence 是否强于单次 Run？ |
| **KR-S2** | Scope：same scope / higher confidence，还是 Expand？（默认前者） |
| **KR-S3** | Qualification 是否保留？（Strengthen **不得**消除 Qualification） |
| **KR-S4** | 强化后是否仍可被未来 Evidence 推翻？ |

**Strengthened ≠ Unqualified ≠ Gate PASS.**

---

## 9. Authorization Conditions（绑定 GRANTED）

自 RUN002 起，Cross Evidence Authorization 继承并扩展 RUN001 条件：

| ID | Condition |
|----|-----------|
| **C-ENV** | Manifest 含 environment identity；Observation 前满足 |
| **C-SCOPE** | 严格遵守 Fill Appendix A；改冻结字段 → 新 `run_id` |
| **C-CLAIM** | 禁止 Capability 已证实 / Regime / Alpha / Gate PASS |
| **C-GATE** | 不自动 PASS Gate；不 ACCEPT RC001 |
| **C-NO-DRIFT** | 禁止选优、静默缩 universe、未注册扩参 |
| **C-XEV** | §5 Integrity Constraint |
| **C-K001** | §7 Action ≠ Decision |

### EA7 — Cross Evidence Integrity（Auth 审查项）

除 EA1–EA6（与 Discovery 同族）外，Cross Evidence 须通过 **EA7**：非 Discovery 定位、协议引用冻结、Integrity Constraint、K001 预映射、Gate 不自动打开。

---

## 10. Evidence Interpretation（继承限制）

Cross Evidence **不**消除 Parent Run 的方法学限制，除非未来 Run 显式验证并修订：

| 限制 | 持续含义 |
|------|----------|
| E1 definition coupling | E1 = supporting；E2/E3/SMD_M2 权重更高 |
| Universe boundary | `{rb, i, MA}` 等 frozen universe；非 all markets |
| Family boundary | Volatility + Price only（除非新 Run 主变量为 family） |
| Descriptive ≠ Predictive | 无 Alpha / 无交易宣称 |

---

## 11. Relation to Gate / RC001

```text
Cross Evidence SUPPORTED
        ≠
Context Capability Gate PASS
        ≠
RC001 Accepted
```

Gate 输入应为 **成熟的 Knowledge Portfolio** + **Engineering Signal 就绪**；单条 Knowledge Strengthen **不**自动打开 Gate。

当前（as-of 2026-07-21）：[`CONTEXT_CAPABILITY_GATE.md`](CONTEXT_CAPABILITY_GATE.md) — **BLOCKED**（K001 Strengthened Qualified；Engine 仍 UNKNOWN）。

---

## 12. Reference Cases（CAP-CTX-001）

| Run | Type | 主变量 | 结果 | Knowledge |
|-----|------|--------|------|-----------|
| RUN001 | Discovery | — | E1/E2/E3 PASS | K001 Qualified |
| RUN002 | Temporal OOS | Time 2022–2023 | SUPPORTED | K001 **Strengthened Qualified** |

文档链：

| 阶段 | RUN002 示例 |
|------|-------------|
| Spec | [`CAP_CTX_001_RUN002_RUN_SPEC.md`](CAP_CTX_001_RUN002_RUN_SPEC.md) |
| Fill | [`CAP_CTX_001_RUN002_PRE_REGISTRATION_FILL.md`](CAP_CTX_001_RUN002_PRE_REGISTRATION_FILL.md) |
| Auth | [`CAP_CTX_001_RUN002_EXECUTION_AUTHORIZATION.md`](CAP_CTX_001_RUN002_EXECUTION_AUTHORIZATION.md) |
| Evidence Review | [`CAP_CTX_001_RUN002_EVIDENCE_REVIEW.md`](CAP_CTX_001_RUN002_EVIDENCE_REVIEW.md) |
| Knowledge | [`K001_KNOWLEDGE_REVIEW.md`](K001_KNOWLEDGE_REVIEW.md) |

---

## 13. Starting RUN003+

新 Cross Evidence Run 须：

1. 引用本文件 + 指定 parent run / knowledge id  
2. Spec 中声明 **单一主变量** 与 **协议继承串**  
3. 预注册 Decision Mapping（§7）  
4. 不修改 Closed Run 产物  
5. 完整走 §6 生命周期（无跳过）

**RUN003 未授权**；须用户单独立项。

---

## 14. Negative Evidence（一等公民）

Cross Evidence **必须**将非支持结果视为有效研究产物。

| Outcome | Registered Action | Evidence status |
|---------|-------------------|-----------------|
| SUPPORTED | Strengthen | **Valid** |
| PARTIAL | Narrow | **Valid** |
| NOT SUPPORTED | Downgrade | **Valid** |
| INFEASIBLE | No upgrade | **Valid** |

```text
Negative Evidence ≠ Failed Experiment
Negative Evidence ≠ Delete Run / Revise Question / Retrofit Scope
```

**禁止（结果导向）：**

* 因 NOT SUPPORTED / PARTIAL 删除 Run 或改写 Closed 产物  
* Observation 后修改 Spec/Fill 以「挽回」支持  
* 静默缩小 universe 或改主变量解释  
* 用 Governance 修订**追溯性**重释 RUN001/RUN002（Closed 不可变；治理变更仅约束**未来** Run）

Governance 修订须新版本号；**不** retroactively 改变已 Closed Run 的 Evidence 含义。

---

## A. Evidence Types Taxonomy（Epoch 3.1）

**G-CX-001 原则**：每种 Evidence Type 对应 **唯一目的** 与 **唯一典型主变量**；禁止一 Run 承担多种 Cross Evidence 目的。

| Type | 唯一目的 | 典型主变量（仅此） | 不得同时承担 | CAP-CTX 案例 |
|------|----------|-------------------|--------------|----------------|
| **Discovery** | 发现现象 / 初始结构 | —（新 EQ；非 Cross Evidence） | Cross Evidence 链 | RUN001 |
| **Temporal** | 时间外稳定性 | Time window | 品种 / family / 指标 | RUN002 |
| **Cross-sectional** | 品种/截面稳定性 | Universe | 时间 / family / 指标 | RUN003（proposed） |
| **Observation Expansion** | 观测族稳定性 | Observation family | 时间 / universe / 指标 | RUN004（Spec Draft v0.1） |
| **Stress** | 边界/压力/失效模式 | 注册的 stress 条件（单维） | 其他主变量 | 未来 |

### Type boundary

```text
Discovery Evidence     → 创建 Qualified Knowledge（独立路径）
Cross Evidence Types   → 仅作用于已有 Qualified+ Knowledge
```

Temporal Evidence **不得**用于证明品种稳定；Cross-sectional **不得**用于证明时间稳定。

### A.2 Run mapping（G-CX-005）

| Run | Evidence Type | 唯一主变量 | Status |
|-----|---------------|------------|--------|
| RUN001 | Discovery | — | Closed |
| RUN002 | Temporal | Time window | Closed |
| RUN003 | Cross-sectional | Universe only | Closed |
| RUN004 | Observation Expansion | Family only | Spec Confirmation PASS · Fill pending · **NOT AUTHORIZED** |

### Accumulation chain（非自动晋级）

```text
Discovery → Qualified Knowledge
        ↓
Temporal / Cross-sectional / Family / Stress Evidence（each = registered Run）
        ↓
Strengthen / Narrow / Downgrade（per Run）
        ↓
Capability Candidate（portfolio + Gate review；非单 Run 自动）
```

---

## B. Knowledge State Machine（documented）

```text
Candidate
   ↓  Knowledge Review
Qualified
   ↓  Cross Evidence + Strengthen Review
Strengthened Qualified          ← K001 (current)
   ↓  Portfolio + Gate v2（future）
Capability Candidate
   ↓  Gate / formal acceptance
Accepted Capability
```

| Transition | Requires |
|------------|----------|
| → Qualified | Discovery Evidence Review + Knowledge Review |
| → Strengthened Qualified | Cross Evidence SUPPORTED + Strengthen Review |
| → Capability Candidate | **Not automatic**；须满足下方 Portfolio Bar |
| → Accepted Capability | Gate PASS + explicit acceptance |

### Strengthened Qualified → Capability Candidate（G-CX-002 / B.1）

```text
Strengthened Qualified
        ≠
Capability proven
        ≠
Capability Candidate（automatic）
```

晋级 **Capability Candidate** 须另授 Gate / Portfolio Review；证据组合通常须覆盖：

| Dimension | 含义 | CAP-CTX 现状 |
|-----------|------|----------------|
| **Temporal** | 多非重叠时间窗 Cross Evidence | RUN002 ✓ |
| **Cross-sectional** | Universe 扩展下仍成立 | RUN003 ✓ |
| **Observation Family** | 注册族扩展下仍成立 | RUN004 ✓（**Portfolio Bar P3 MET**） |
| **Independence** | 非仅重复 vol/trend/liquidity 代理；独立验证链 | Phase 3.4 Proposal Draft（**Portfolio Bar P4 缺口**） |
| **Engineering signal** | 研究可用的一级状态信号 | Gate v1 BLOCKED（**E1 并行轨道**） |

**Portfolio Bar Review（2026-07-21）**：[`CAPABILITY_PORTFOLIO_BAR_REVIEW.md`](CAPABILITY_PORTFOLIO_BAR_REVIEW.md) v0.2 — **BAR NOT MET**；P3 MET；**P4 未满足**。

**单次 SUPPORTED Run 不足以晋级 Capability Candidate。**

**Strengthened Qualified ≠ Capability Candidate ≠ Gate PASS.**

Epoch 3 roadmap：[`EPOCH_3_POSITIONING.md`](../releases/EPOCH_3_POSITIONING.md).

---

## C. Layer separation（G-CX-003 — baseline）

```text
Evidence Result（artifact + Review PASS）
        ≠
Registered Knowledge Action（pre-mapped）
        ≠
Knowledge Decision（另授 Review）
        ≠
Gate PASS / RC001 / Alpha
```

此为 PAAF Cross Evidence 核心治理优势；**不得**在 Run Spec、Fill 或事后解释中合并层级。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 1.0 | 初稿：RUN001/RUN002 抽象 |
| 2026-07-21 | 1.1 | Appendix A/B：Evidence types、state machine |
| 2026-07-21 | 1.2 | **Governance Baseline**：G-CX Review；§14 Negative Evidence；A.1/A.2；B.1；§C |
