# Context Capability Research Proposal v0.3

> **Type**: Research Proposal  
> **Status**: Review Passed（after revision）  
> **Version**: 0.3  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CONTEXT_CAPABILITY_RESEARCH_PROPOSAL.md`  
> **Method**: [`PAAF_RESEARCH_METHOD.md`](PAAF_RESEARCH_METHOD.md)  
> **Gate**: [`CONTEXT_CAPABILITY_GATE.md`](CONTEXT_CAPABILITY_GATE.md)（Current = BLOCKED）  
> **Downstream（未授权）**: RC001 — 仅在 Gate PASS 之后  
> **Future candidate（未 Promote）**: **CAP-CTX-001** — Context Capability Research（Foundation / Capability Validation，非 Alpha RC）

### Review Verdict（v0.3）

```text
CONTEXT CAPABILITY RESEARCH PROPOSAL v0.3

Review Result: PASS
Scientific Scope / RQ / Observation Boundary / Falsification: Accepted

Status: Review Passed
Ready for: Capability Experiment Specification

CAP-CTX-001: Candidate only — Not promoted
Gate: BLOCKED — awaiting Spec Review + Promote + Evidence
```

下游 Spec：[`CAPABILITY_EXPERIMENT_SPECIFICATION_CAP_CTX_001.md`](CAPABILITY_EXPERIMENT_SPECIFICATION_CAP_CTX_001.md)（v0.2 **Confirmation PASS**）  
Promote Decision：[`CAP_CTX_001_PROMOTE_DECISION.md`](CAP_CTX_001_PROMOTE_DECISION.md)（**CONFIRM PROMOTE**）  
Run Spec：[`CAP_CTX_001_RUN_SPEC.md`](CAP_CTX_001_RUN_SPEC.md)（v0.2 **Confirmation PASS**）  
Execution Auth：[`CAP_CTX_001_EXECUTION_AUTHORIZATION.md`](CAP_CTX_001_EXECUTION_AUTHORIZATION.md)（**NOT GRANTED**）
### 本文不是

| 不是 | 说明 |
|------|------|
| Decision / ADR | 不改变治理结论 |
| Contract / Spec | 不修改 `CONTEXT_ENGINE_SPEC` |
| Architecture Spec | 不设计 Market State Engine / Context Engine |
| Alpha Research Campaign（RC-xxx） | 不开启 Alpha RC；亦不 Promote CAP |
| Experiment Run Spec | 不预注册数值门槛、不跑数 |
| 技术设计文档 | v0.3 = **研究边界补全**，非实现蓝图 |

### 三个“不做”（本阶段强制）

```text
❌ 不写 Context Engine
❌ 不定义 Market State 算法
❌ 不跑回测
❌ 不 Promote 为 CAP-CTX-001（须另授）
```

本阶段只回答：

> **Context 值不值得被研究**——描述能力是否成立，而非是否赚钱。

---

## 1. Purpose

在 RC001（Context-conditioned Opportunity）使用 Context **之前**，先验证该隐含前提：

> Context 是否是一个有效的研究变量？

科学链条（正确）：

```text
Context 是否存在有效描述能力？
        ↓
如果成立
        ↓
Context 是否改善 Opportunity Evaluation？（RC001）
```

禁止的逻辑漏洞：

```text
假设 Context 存在
        ↓
测试 Context 是否有效
```

**不是**：是否赚钱 / 提高收益 / 产生 Alpha / 改善 Opportunity 评价（后者属 RC001）。  
**是**：Context 作为研究对象是否存在可观测、可审计的**市场条件描述能力**。

---

## 2. Research Question

### RQ-CTX-001

```text
Can a Context representation
capture persistent and distinguishable
market conditions across instruments?
```

中文：

> Context 表示是否能够跨品种捕获**持续且可区分的市场条件**？

本 RQ 问的是 **Capability 是否存在**，不是 **如何构建 Context Engine**。  
不升级为「Do Context Regimes exist？」；不加入 regime / feature vector / classifier。

### 用词：Condition vs State

| 用语 | 倾向 | 本 Proposal |
|------|------|-------------|
| **market state** | 易联想到牛熊 / Regime / 策略域 | **避免**作为 RQ 主词（Gate G1 讨论除外） |
| **market condition** | 偏观察事实、Evidence First | **采用** |
| **regime** | 易滑向分类器 / 策略叙事 | **不作为核心研究对象** |

`MarketState` 仍是 Domain 枚举名（工程标识）；研究叙述优先用 **condition**。

### 问题边界

| 本问题问 | 本问题不问 |
|----------|------------|
| 条件是否可观测、可分、可跨品种 | 条件能否过滤 OPP / 提高 expectancy |
| **描述能力**是否成立 | **预测能力** / 交易信号是否有效 |

---

## 2.1 Critical Boundary — Descriptive ≠ Predictive

> **This research evaluates descriptive capability, not predictive power.**

| 评价 | 含义 | 本阶段 |
|------|------|--------|
| **Descriptive capability** | 不同 Context 对应不同可观测条件 | **In scope** |
| **Predictive power** | 方向命中率、能否赚钱 | **Out of scope** |

误解示例（禁止据此判失败）：

```text
Context label = TREND
未来上涨概率 ≈ 52%
→ 「没用」  ← 错误：第一阶段任务不是预测方向
```

---

## 3. Hypothesis

### H0 — Null

```text
Context label is not associated
with observable market behavior differences.
```

### H1 — Alternative（General capability）

```text
Context label corresponds to
different observable market conditions.
```

**H1 成立 ≠ Alpha**；仅表示有可区分的描述。

### H2 — Limited Capability（Boundary）

```text
Context shows separation,
but only under specific conditions.
```

**不是失败** → **K004 Boundary Knowledge**；Gate 或为 `PASS WITH LIMITATION`。

---

## 4. Scope Boundary

### Included

```text
Context Representation
        ↓
Market Conditions
        ↓
Existence → Stability → Transfer
```

### Excluded

```text
Context → Signal → Trading
Context → Direction prediction → “edge”
```

**禁止**：策略收益、胜率优化、参数搜索、ML 分类器、Alpha 挖掘、Opportunity 条件化（RC001）、实验专用 Context（Gate G4）。

### Non-Goals（v0.3 强化 — 不进入本 Proposal）

| 内容 | 状态 |
|------|------|
| Feature normalization | ❌ |
| Clustering algorithm | ❌ |
| HMM / XGBoost | ❌ |
| State label definition（工程实现） | ❌ |
| Context Engine architecture | ❌ |
| Context Vector `C(t)` 作为预设架构 | ❌ |
| Backtest | ❌ |
| Alpha evaluation | ❌ |

---

## 5. Observation Space

> 什么类型的可观测信息可以用于验证 Context Capability？  
> **不是**：如何实现 Context Representation？

本研究**不假设**预先给定的 Context 表示。  
候选观测按 **observable families** 分组，供后续（若 Promote）CAP 实验从中选取证据来源。

### Candidate Observation Families

#### 1. Price Structure

Examples（候选，非冻结清单）：

- directional efficiency  
- return persistence  
- candle overlap  
- range structure  

#### 2. Volatility Structure

Examples：

- realized volatility  
- volatility percentile  
- compression / expansion characteristics  

#### 3. Liquidity Structure

Examples：

- volume participation  
- turnover behavior  
- liquidity variation  

#### 4. Market Geometry

Examples：

- structural persistence  
- price path characteristics  

### Boundary Statement（强制）

```text
Observation Space defines candidate evidence sources.

It does not define:
- a Context Engine
- a Market State Model
- a classifier
- a trading signal
- an alpha model
- a mandatory Context Vector C(t)
```

| 概念 | 角色 |
|------|------|
| Observation Space | 研究输入**候选族** |
| Domain `MarketState` / Gate G1 | 发布**资格**（工程契约） |
| CAP Experiment Spec（未来） | 从候选族中**预注册**具体度量 |

三者不可混成「先实现完整特征向量再谈科学问题」。

---

## 6. Capability Questions

顺序：**Existence → Reliability → Generalization**。  
本层只定义问题，不冻结 metric 数值（数值门槛属未来 Experiment Spec）。

### CQ1 — Existence

不同 Context 是否产生**任何**可观察差异？（可对照 Observation Space 中的候选族）

无差异 → 支持 H0；不必再谈稳定与跨品种。

### CQ2 — Stability

若存在差异：是否持续、而非一次性偶然？

### CQ3 — Transferability

是否跨品种 / 跨市场成立？

```text
定义 / 观察示例：rb → i, ma, ta, …
```

仅单品种「看起来不同」→ 可能落入 H2 / K004。

---

## 7. Falsification / Rejection Criteria

定位：**否定 Capability Hypothesis 的方向性条件**。  
**不是** Experiment Threshold（数值门槛另授 CAP Experiment Spec 冻结）。

Context Capability 视为 **unsupported**，若证据表明：

1. **No distinguishable conditions** exist beyond a random-partition baseline.  
2. Observed conditions **lack temporal persistence** beyond random-switching expectation.  
3. **Cross-instrument consistency** is absent.  
4. Results **depend only on isolated** instruments or periods（无法构成可迁移描述能力）。

映射：

| 失败方向 | 主要对照 | 典型知识 |
|----------|----------|----------|
| (1) | CQ1 Existence | H0 / K002 |
| (2) | CQ2 Stability | H0 或 K003 |
| (3)(4) | CQ3 Transfer | H0 / K002 或 H2 / K004 |

### Predictive failure ≠ Capability failure

```text
Failure of predictive performance
does not invalidate Context Capability.

Context research is descriptive,
not predictive.
```

方向命中率弱、无法交易获利 → **不得**单独作为拒绝 Context Capability 的理由。

---

## 8. Evidence Required

### 只接受

```text
Context Output（或候选表示输出）
+ Market Data（冻结数据协议）
+ Evaluation Result（可审计、可复现）
```

```text
Artifact → Evaluation → EvidenceRecord
```

（本 Proposal **不**启动写入。）

### 不接受

```text
Chart examples alone
Manual interpretation
Single trade screenshots
Backtest PnL / hit-rate narratives as primary evidence
```

---

## 9. Possible Outcomes（知识四类）

| ID | 名称 | 含义 | 典型假设 | 对 Gate / RC001 |
|----|------|------|----------|-----------------|
| **K001** | Positive Evidence | 稳定、可迁移的描述能力 | H1 | 支持 Gate → PASS* |
| **K002** | Negative Evidence | 无稳定区分能力 | H0 | Gate 可保持 BLOCKED |
| **K003** | Process Knowledge | 方法有效，当前表示不足 | — | 修订表示；非 Spec 膨胀 |
| **K004** | Boundary Knowledge | 仅部分条件 / 品种成立 | H2 | Gate 或 PASS WITH LIMITATION |

不预设 K001。默认零假设至有 Evidence。

---

## 10. Relationship（依赖图）

```text
Context Capability Research Proposal  ← 本文（v0.3 Review Passed）
        ↓
CAP-CTX-001 Candidate（未 Promote）
        ↓
Capability Experiment Specification（未授权）
        ↓
Context Capability Gate v1
  PASS | PASS WITH LIMITATION | BLOCKED
        ↓
RC001 Ready → Accepted
```

| 层级 | 问题 | 类型 |
|------|------|------|
| **本 Proposal** | Context 描述能力是否成立？ | Foundation 问题 + 边界 |
| **CAP-CTX-001**（候选） | 同上，正式 Capability Validation | **非** Alpha RC |
| **Gate** | Context 是否具备被 RC 使用的资格？ | Methodology checklist |
| **RC001** | Context 是否改善 Opportunity **评价**？ | Scientific Investigation RC |

**禁止跳跃**：不得在 Gate BLOCKED 时用 RC001 反推 Context「有用」。

---

## 11. Current Placement in Epoch 2.0

```text
Epoch 2.0
PRM ✓
RC001 Review Passed ✓
Context Gate v1 ✓（BLOCKED）
        ↓
CTX Capability Research Proposal v0.3
        ↓
Review PASS
        ↓
Capability Experiment Spec Draft
        ↓
CAP-CTX-001 Candidate（Not promoted）
        ↓
（另授）Spec Review PASS → Promote → Execution → Gate
```

### 本阶段授权边界

| 允许 | 禁止 |
|------|------|
| 审阅 Capability Experiment Spec Draft | Promote CAP-CTX-001 / 开启执行 |
| 修订 Spec Draft | 写 ContextEngine / 算法 / 分类器 |
| 明确与 Gate / RC001 边界 | 改 RC001 Accepted；跑回测 |

---

## 12. Exit from Proposal Stage

须用户确认（四选一）：

1. **Withdraw** — 暂不研究 Context Capability  
2. **Further Refine** — 仍为 Proposal  
3. **Promote to CAP-CTX-001** — 用户授权后写 Capability Experiment Spec，再正式 Campaign  
4. **Close as Knowledge** — 仅文档层结论（无跑数不得伪称 K001）

**当前默认**：停留 **Review Passed**；**不** Promote。  
Gate 保持 **BLOCKED**，理由：Awaiting Capability Experiment Specification。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-20 | 0.1 | Draft：RQ-CTX-001；H0/H1；CQ；四类 Knowledge |
| 2026-07-20 | 0.2 | Review Passed：condition；H2；CQ Existence→Stability→Transfer；Descriptive≠Predictive |
| 2026-07-21 | 0.3 | Review Passed after revision：Observation Space；Falsification；Non-Goals 强化；仍不 Promote |
| 2026-07-21 | 0.3.1 | Proposal Review PASS 归档；链接 Capability Experiment Spec Draft |
