# Context Capability Research Proposal v0.2

> **Type**: Research Proposal  
> **Status**: Review Passed  
> **Version**: 0.2  
> **Date**: 2026-07-20  
> **Path**: `docs/research/CONTEXT_CAPABILITY_RESEARCH_PROPOSAL.md`  
> **Method**: [`PAAF_RESEARCH_METHOD.md`](PAAF_RESEARCH_METHOD.md)  
> **Gate**: [`CONTEXT_CAPABILITY_GATE.md`](CONTEXT_CAPABILITY_GATE.md)（Current = BLOCKED）  
> **Downstream（未授权）**: RC001 — 仅在 Gate PASS 之后  
> **Future candidate（未 Promote）**: **CAP-CTX-001** — Context Capability Research（Foundation / Capability Validation，非 Alpha RC）

### Review Verdict（v0.2）

```text
CONTEXT CAPABILITY RESEARCH PROPOSAL v0.2

Status: Review Passed ✓

Recommendation: Refine complete → decide later whether to Promote to CAP-CTX-001

Not RC yet
Not CAP-CTX-001 yet
```

### 本文不是

| 不是 | 说明 |
|------|------|
| Decision / ADR | 不改变治理结论 |
| Contract / Spec | 不修改 `CONTEXT_ENGINE_SPEC` |
| Architecture Spec | 不设计 Market State Engine |
| Alpha Research Campaign（RC-xxx） | 不开启 RC001 以外的 Alpha RC；亦不 Promote CAP |
| Experiment Run Spec | 不预注册回测参数、不跑数 |

### 三个“不做”（本阶段强制）

```text
❌ 不写 Context Engine
❌ 不定义 Market State 算法
❌ 不跑回测
❌ 不 Promote 为 RC / CAP-CTX-001（须另授）
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

### 用词：Condition vs State

| 用语 | 倾向 | 本 Proposal |
|------|------|-------------|
| **market state** | 易联想到牛熊 / Regime / 策略域模型 | **避免**作为 RQ 主词 |
| **market condition** | 偏观察事实、Evidence First | **采用** |

`MarketState` 仍是 Domain 枚举名（工程标识）；研究叙述优先用 **condition**，避免把模型假设当成已知事实。

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
| **Descriptive capability** | 不同 Context 对应不同可观测条件（波动、持续、分布形状等） | **In scope** |
| **Predictive power** | 例如 TREND 后上涨概率 52%、「能否赚钱」 | **Out of scope** |

误解示例（禁止据此判失败）：

```text
Context = TREND
未来上涨概率 ≈ 52%
→ 「没用」  ← 错误：第一阶段任务不是预测方向
```

Context 可以只描述：波动环境、持续性、交易条件——**不等于**方向预测器。

---

## 3. Hypothesis

### H0 — Null

```text
Context label is not associated
with observable market behavior differences.
```

不同 Context 下，市场行为分布无预注册意义上的显著差异。

### H1 — Alternative（General capability）

```text
Context label corresponds to
different observable market conditions.
```

存在可观测差异（波动、持续性、后续分布形状等）。  
**H1 成立 ≠ Alpha**；仅表示有可区分的描述。

### H2 — Limited Capability（Boundary）

```text
Context shows separation,
but only under specific conditions.
```

示例（非已证实）：

- 某品种有效、另一品种无效  
- 高波动段可分、低波动段不可分  

**不是失败** → 对应 **K004 Boundary Knowledge**；Gate 或为 `PASS WITH LIMITATION`。

---

## 4. Scope Boundary

### Included

```text
Context
  ↓
Market Description（conditions）
  ↓
Evidence: Existence → Stability → Transferability
```

### Excluded

```text
Context → Signal → Trading
Context → Direction prediction → “edge”
```

**禁止**：策略收益、胜率优化、参数搜索、ML 分类器、Alpha 挖掘、Opportunity 条件化（RC001）、实验专用 Context（Gate G4）。

---

## 5. Capability Questions

顺序：**Existence → Reliability → Generalization**。  
本层只定义问题，不冻结 metric 数值。

### CQ1 — Existence

不同 Context 是否产生**任何**可观察差异？

示例方向（非 Run Spec）：volatility / range / persistence 等分布差异。

无差异 → 支持 H0；不必再谈稳定与跨品种。

### CQ2 — Stability

若存在差异：是否持续、而非一次性偶然？

示例探询：

```text
某 condition 标签平均持续多少 bar？
标签切换是否过于频繁以致近似噪声？
```

### CQ3 — Transferability

是否跨品种 / 跨市场成立？

```text
定义 / 观察示例：rb → i, ma, ta, …
```

仅单品种「看起来不同」→ 不足以声称跨品种描述能力；可能落入 H2 / K004。

---

## 6. Evidence Required

### 只接受

```text
Context Output
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

## 7. Possible Outcomes（知识四类）

| ID | 名称 | 含义 | 典型假设 | 对 Gate / RC001 |
|----|------|------|----------|-----------------|
| **K001** | Positive Evidence | 稳定、可迁移的描述能力 | H1 | 支持 Gate → PASS* |
| **K002** | Negative Evidence | 无稳定区分能力 | H0 | Gate 可保持 BLOCKED |
| **K003** | Process Knowledge | 方法有效，当前表示不足 | — | 修订表示；非 Spec 膨胀 |
| **K004** | Boundary Knowledge | 仅部分条件 / 品种成立 | H2 | Gate 或 PASS WITH LIMITATION |

不预设 K001。默认零假设至有 Evidence。

---

## 8. Relationship（依赖图）

```text
Context Capability Research Proposal  ← 本文（Review Passed）
        ↓
CAP-CTX-001 Candidate（未 Promote）
        ↓
Context Capability Gate v1
  PASS | PASS WITH LIMITATION | BLOCKED
        ↓
RC001 Ready → Accepted
  （RQ: Context improves Opportunity evaluation）
```

| 层级 | 问题 | 类型 |
|------|------|------|
| **本 Proposal** | Context 描述能力是否成立？ | Foundation 问题定义 |
| **CAP-CTX-001**（候选） | 同上，正式 Capability Validation | **非** Alpha RC |
| **Gate** | Context 是否具备被 RC 使用的资格？ | Methodology checklist |
| **RC001** | Context 是否改善 Opportunity **评价**？ | Scientific Investigation RC |

**命名说明**：未来若 Promote，建议 **CAP-CTX-001**（或 CAP-001），**不要**占用 RC002 作为 Alpha 序号——本项是 Capability Validation，不是 Alpha Campaign。

**禁止跳跃**：不得在 Gate BLOCKED 时用 RC001 反推 Context「有用」。

---

## 9. Current Placement in Epoch 2.0

```text
Epoch 2.0
PRM ✓
RC001 Review Passed ✓
Context Gate v1 ✓（BLOCKED）
        ↓
CTX Capability Research Proposal
        ↓
Review Passed ← here（v0.2）
        ↓
CAP-CTX-001 Candidate（Not promoted）
```

### 本阶段授权边界

| 允许 | 禁止 |
|------|------|
| 审阅本 v0.2 | Promote CAP-CTX-001 / 开启 EXP |
| 讨论 CQ 操作化（文档） | 写 ContextEngine / Market State 算法 |
| 明确与 Gate / RC001 边界 | 改 RC001 Accepted；跑回测 |

---

## 10. Exit from Proposal Stage

须用户确认（四选一）：

1. **Withdraw** — 暂不研究 Context Capability  
2. **Further Refine** — 仍为 Proposal  
3. **Promote to CAP-CTX-001** — 用户授权开启 Capability Validation Campaign（非 Alpha RC），再写 Experiment Design  
4. **Close as Knowledge** — 仅文档层结论（无跑数不得伪称 K001）

**当前默认**：停留 **Review Passed**；**不** Promote。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-20 | 0.1 | Draft：RQ-CTX-001；H0/H1；CQ；四类 Knowledge |
| 2026-07-20 | 0.2 | Review Passed：condition 用语；H2；CQ Existence→Stability→Transfer；Descriptive≠Predictive；CAP-CTX-001 Candidate |
