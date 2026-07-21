# Context Capability Gate v1

> **Kind**: Research Methodology（研究验收清单）  
> **Not**: System Contract / Spec / Decision / ADR  
> **Path**: `docs/research/CONTEXT_CAPABILITY_GATE.md`  
> **Authority**: PRM > 本 Gate；冲突时以 Accepted Spec / Decision 为准  
> **Related**: [`PAAF_RESEARCH_METHOD.md`](PAAF_RESEARCH_METHOD.md) · [`RC001_RESEARCH_PLAN.md`](../campaigns/RC001_RESEARCH_PLAN.md) · [`CONTEXT_ENGINE_SPEC.md`](../specs/CONTEXT_ENGINE_SPEC.md)（引用边界，不修订）

---

## 0. Purpose

> Define minimum conditions for Context to become an **observable research variable**.

本 Gate **只回答**：

> 当前 Context 是否具备作为 Research Variable 被使用的资格？

本 Gate **不回答**：

- 如何设计完整 Market State Engine  
- Context Spec 是否升版  
- RC001 / OPP16 是否有 Alpha  
- 是否该写新 Contract / Decision  

**定位**：

```text
docs/research/     ← 本文件（Methodology）
docs/specs/        ← Contract（本 Gate 不进入）
```

---

## 0.1 What This Gate Is Not

| 不是 | 说明 |
|------|------|
| Context Engine Spec v2 | 不改接口、不扩枚举、不新 ADR |
| Market State Framework | Market State 只是 Context Capability 的**一个**实现面 |
| 实验实现授权 | Gate Pass ≠ RC001 Accepted ≠ 可跑回测 |
| 为 RC001 补变量 | 禁止「为实验创造 Context」 |

正确关系：

```text
Context Capability
        |
        +---- Market State      （当前候选实现）
        |
        +---- Volatility State  （未来）
        |
        +---- Liquidity State   （未来）
```

---

## Current Verdict（as-of 2026-07-20）

```text
Context Capability Gate v1

Status: BLOCKED

Reason:
  ContextEngine publishes market_state = UNKNOWN only
  → Context Signal does not yet exist as a research variable
```

此 Verdict 本身可作为 **Process Evidence**：Framework 存在、Signal 未就绪。  
**不**因此自动关闭 RC001；RC001 保持 Review Passed，等待 Capability 或 early-close 授权。

---

## Gate Criteria

### G0 — Ownership

Context 必须来自正式 Context 管线，不得由实验脚本临时造特征。

**Required chain**:

```text
ContextEngine
      ↓
Context（Domain snapshot）
      ↓
Evidence（可关联字段 / provenance）
```

**Forbidden chain**:

```text
Experiment Script
      ↓
temporary feature / ad-hoc label
      ↓
「当作 Context」写入结果
```

| PASS | FAIL |
|------|------|
| 状态由 `ContextEngine.update(...)`（或等价正式发布路径）产生 | OPP / EXP 脚本自行计算并冒充 Context |
| Domain `Context` / `MarketState` 类型 | 实验局部 dict / 私有枚举 |

---

### G1 — Published State

必须存在**至少一个**非 `UNKNOWN` 的一级状态，由 Context 发布。

**允许示例**（来自 Accepted Spec 基线或未来经 Spec 晋级的一级状态）：

```text
MarketState.TREND
MarketState.RANGE
```

未来若 Spec 将 Compression 提升为一级状态，亦可；**当前** Compression 在 `extras` 不算 G1 的一级 Published State（除非用户另立 Gate 修订）。

**必须**：状态来自 Context。  
**禁止**：状态来自 EXP / Detector「自带 context」。

| PASS | FAIL |
|------|------|
| 对约定输入窗口，可观测到非 UNKNOWN | 恒 UNKNOWN |
| 同输入 → 同 ContextState（与 G2 衔接） | Detector 为 OPP16 自生成 context 标签 |

---

### G2 — Reproducibility

Context 必须可重建；Evidence 方可审计。

**最小 provenance（概念字段，不发明新 Contract）**：

```text
symbol
timestamp（或 bar datetime）
data_version（或等价数据指纹）
context_version（引擎/规则版本标识）
```

给定上述输入，应得到相同 `ContextState`（一级 `market_state`；约定 extras 若参与研究须同样可重建）。

| PASS | FAIL |
|------|------|
| 同 provenance → 同状态 | 隐藏参数、不可复现随机、无版本标识 |
| 可在 Evidence / Artifact 中追溯 provenance | 仅有口头描述或不可复跑截图 |

---

### G3 — Evidence Traceability

Context 输出必须能进入 Evidence 链路，而非事后叙事。

**Required chain**:

```text
Context
  → Experiment
  → Evaluation
  → EvidenceRecord
```

| PASS | FAIL |
|------|------|
| Evidence / Artifact 可关联当时 Context（或等价可重建快照） | 仅有 backtest PnL + 截图 + 人工解释 |
| 条件化实验能声明「在何 Context 下」 | Context 只存在于分析笔记 |

---

### G4 — Experiment Independence

**最关键一条。** Context 不得知道具体 Campaign / Opportunity。

Context **不得**编码或依赖：

```text
OPP16
RC001
EXP002
```

| 允许（通用能力） | 禁止（实验专用） |
|------------------|------------------|
| ATR / 波动压缩类 **通用** Context 表示（若经 Spec / 约定 extras） | `OPP16_reversal_context` |
| Trend / Range 市场状态 | `compression_state_for_OPP16` |
| 与任何 Detector 无关的发布规则 | 仅服务 RC001 EXP002 的分支逻辑 |

**原则**：Context 是研究基础设施变量；Opportunity 是被评价对象。二者方向不可反转。

---

## Verdict Scale

不使用二元「随便过/不过」叙事；采用：

```text
PASS
PASS WITH LIMITATION
BLOCKED
```

| Verdict | 含义 | 对 RC001 |
|---------|------|----------|
| **PASS** | G0–G4 均满足 | 可申请 **Ready**（仍须用户 Accepted） |
| **PASS WITH LIMITATION** | 可用，但范围受限（须写明限制，例如仅 TREND/RANGE、仅单品种可测） | 可申请 Ready；EXP 设计须遵守限制 |
| **BLOCKED** | 尚不具备 Research Variable 资格 | **不得** Ready / Accepted / EXP002 |

**Limitation 示例写法**：

```text
PASS WITH LIMITATION
Limitation: only TREND|RANGE; Compression not first-level; single-symbol smoke only
```

---

## Assessment Procedure（清单用法）

1. 对照 G0–G4 逐条记录证据（代码路径、测试、Spec 条款引用——**不**要求本文件触发实现）。  
2. 给出 Verdict + Reason（一句话）。  
3. 若 BLOCKED：可选择推进 Context Capability（Spec **内**实现）或 RC early-close（K002-process）——须用户授权。  
4. 若 PASS / PASS WITH LIMITATION：更新本文件 Current Verdict，再由 RC001 申请 Ready。

**禁止**：为凑 Gate 而改 Detector、为 RC001 加专用 Context、升 Spec 版本却不经既有治理。

---

## Relationship to Capability Research & RC001

```text
Context Capability Research Proposal（Review Passed）
        ↓
CAP-CTX-001 Candidate（未 Promote）
        ↓
Context Capability Gate   ← 本文件
        ↓
RC001 Ready → Accepted → EXP001 …
```

- Gate **BLOCKED** → 先完成 Capability 研究（Proposal / 未来 CAP-CTX-001），或授权 early-close。  
- Gate **PASS / PASS WITH LIMITATION** → 才讨论 RC001 Ready。  
- **禁止**用 RC001 实验反推 Context「有资格」。  
- Proposal 权威：[`CONTEXT_CAPABILITY_RESEARCH_PROPOSAL.md`](CONTEXT_CAPABILITY_RESEARCH_PROPOSAL.md)。

---

## Out of Scope（本文件）

- 实现 Context 算法  
- 修改 `CONTEXT_ENGINE_SPEC`  
- 新 Decision / Domain 枚举  
- 回测、Run Spec、Commit  

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-20 | 1.0 | 初稿：G0–G4；Verdict 量表；Current = BLOCKED；非 Spec |
