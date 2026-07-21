# Capability Experiment Specification — CAP-CTX-001

> **Type**: Capability Experiment Specification  
> **Status**: **Confirmation PASS** ✓  
> **Version**: 0.2  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CAPABILITY_EXPERIMENT_SPECIFICATION_CAP_CTX_001.md`  
> **Parent Proposal**: [`CONTEXT_CAPABILITY_RESEARCH_PROPOSAL.md`](CONTEXT_CAPABILITY_RESEARCH_PROPOSAL.md) v0.3（**Review PASS**)  
> **Gate**: [`CONTEXT_CAPABILITY_GATE.md`](CONTEXT_CAPABILITY_GATE.md)（Current = **BLOCKED**)  
> **Campaign**: **CAP-CTX-001 — PROMOTED**（Controlled Research Object）  
> **Promote Decision**: [`CAP_CTX_001_PROMOTE_DECISION.md`](CAP_CTX_001_PROMOTE_DECISION.md) — **CONFIRM PROMOTE**  
> **Run Spec**: [`CAP_CTX_001_RUN_SPEC.md`](CAP_CTX_001_RUN_SPEC.md)（Draft）  
> **Gate**: [`CONTEXT_CAPABILITY_GATE.md`](CONTEXT_CAPABILITY_GATE.md)（Current = **BLOCKED**)

### Review History

```text
v0.1 Review: PASS WITH MINOR REVISION
v0.2: R1–R3 applied
v0.2 Confirmation Review: PASS ✓
  R1 Dataset Freeze: Accepted
  R2 Null Baseline Boundary: Accepted
  R3 Evidence Interpretation Boundary: Accepted
  Blocking Issues: None

Promotion: NOT AUTHORIZED（见 Promote Decision Review）
```

### Positioning

```text
Proposal v0.3 Review PASS
        ↓
Capability Experiment Spec v0.2 Confirmation PASS ✓
        ↓
CAP-CTX-001 Promote Decision Review
        ↓
（若 PROMOTE*）Run Specification → Execution → Evidence
```

### 本文不是

| 不是 | 说明 |
|------|------|
| Experiment 代码 / Run Script | 不实现 |
| Detector / Feature Pipeline | 不实现 |
| Context / Market State Engine | 不实现 |
| Alpha RC / RC001 EXP | 不启动 |
| Feature Catalog / 最优表示搜索 | **明确禁止**（见 §4.1） |
| Contract / Decision / Spec 升版 | 不产生 |

### 三个“不做”

```text
❌ 不写 Detector / Feature Pipeline / State Engine
❌ 不跑回测 / 不评价 Alpha
❌ 不 Promote CAP-CTX-001（须 Spec Confirmation PASS + 用户另授）
```

---

## 1. Experiment Question

继承 RQ-CTX-001，操作化为实验问句：

```text
EQ-CTX-001

Given candidate observations from the Observation Space,
does the information support existence of persistent and
distinguishable market conditions across instruments?
```

中文：

> 在 Observation Space 候选观测下，信息是否支持「跨品种、持续、可区分的市场条件」存在？

### 问什么 / 不问什么

| 问 | 不问 |
|----|------|
| 候选观测中是否含有支持 Condition **存在性**的信息 | 哪组 feature 组合「最好」 |
| 相对 **Null Baseline** 是否可区分 / 可持续 / 可迁移 | 方向预测力 / 交易收益 |
| Descriptive capability | Predictive / Alpha usefulness |

**核心反漂移句**：

```text
Does information contained in candidate observations
support existence of persistent conditions?

≠

Which feature combination creates the best Context model?
```

---

## 2. Linkage to CQ / Hypotheses

| CQ | 实验焦点 | 主要对照假设 |
|----|----------|--------------|
| CQ1 Existence | 相对随机划分，条件是否可区分 | H0 vs H1 |
| CQ2 Stability | 相对随机切换，是否有时间持续性 | H0 / K003 |
| CQ3 Transfer | 跨品种是否一致（非孤立样本） | H1 vs H2 / K004 |

Knowledge 出口仍为 Proposal：K001–K004。  
**Experiment 不自动产生 Knowledge**（见 §8.0）。

---

## 3. Dataset Scope

### 3.0 Dataset Scope Freeze（R1 — 强制）

```text
Dataset Scope Freeze

Dataset universe, instruments,
and evaluation periods must be frozen
before observation generation.
```

冻结时间点必须**早于**：

- observation extraction  
- feature / metric calculation（若有）  
- evaluation  

```text
Freeze dataset scope
        ↓
（仅此后）Observation generation
        ↓
Evaluation
```

**禁止**：先看结果再选品种/区间；禁止在 observation 或 evaluation 开始后改写 universe。

> Dataset scope must be frozen before any observation generation or evaluation.

### 3.1 Frozen data protocol

正式 Capability 证据必须使用 Decision 001 / `docs/07_DATA_SPEC.md` 基线：

| 项 | 值 |
|----|-----|
| Source | TQSDK Offline |
| Bar | 1m |
| Continuous | CbC 自动换月 |
| Price | 无复权 |
| Cost | 真实手续费 + 滑点（本 CAP **不**以 PnL 为评价；成本字段仅作数据完整性/换月意识） |

偏离须标为**独立数据实验**，不得替代本 Spec 基线结论。

### 3.2 Instrument scope（执行前冻结；见 §3.0）

建议最小矩阵（Promote / Run Spec 时锁定，不可事后替换）：

| 角色 | 品种（示例） | 目的 |
|------|--------------|------|
| Primary | rb | Existence + Stability |
| Transfer | i, ma 或 ta（选定 ≥2） | CQ3 |
| Hold-out（可选） | 另授 | 防叙事性挑品种 |

本 Spec **不**在此页写死最终名单；写入 Run Spec 即进入 Freeze。

### 3.3 Period scope（执行前冻结；见 §3.0）

- 至少一个足够长的连续区间用于 Existence / Stability  
- 至少一个时间切分（Period A / Period B）用于稳定性对照  
- 换月邻域：若使用 Feature 类派生量，遵循 Feature 换月标注政策；Capability 报告须披露是否含 roll 邻域  

具体起止日期：Run Spec 预注册并 Freeze。

### 3.4 Cost / trading

本 CAP **不**产生交易、不评价 expectancy / hit-rate / PnL。

---

## 4. Observation Input Boundary

### 4.1 Source

仅允许 Proposal v0.3 **Observation Space** 四族中的候选观测：

1. Price Structure  
2. Volatility Structure  
3. Liquidity Structure  
4. Market Geometry  

### 4.2 Critical anti-drift rule（强制）

**禁止**将 Observation Family 展开为可优化的 Feature Catalog。

| 允许 | 禁止 |
|------|------|
| 预注册**少量**代表度量（每族或跨族，Freeze 后写死） | ATR / HV / Boll / … 长列表后做 selection |
| 检验「信息是否支持 condition 存在」 | 「哪组组合 Context 模型最优」 |
| 固定表示、一次评估 | 网格搜索 / stepwise / ML feature importance 选优 |

若研究漂移为 Feature Engineering Research → **本 Spec 下的实验无效**，须新 Proposal / 新 experiment_id。

### 4.3 Representation stance

```text
本 Spec 不假设、不定义、不实现：
- Context Engine
- Market State Model
- Context Vector C(t)
- 人类标签（trend/range）作为观测输入
```

标签若出现，只能作为**事后分区结果**的命名，不得作为输入特征来「拟合」自己。

### 4.4 Phase recommendation（非强制算法）

执行设计时可先限制输入宽度，例如 Phase 1 仅从 **Volatility + Price Structure** 取预注册度量——目的是控制复杂度，**不是**声明另两族无效。

---

## 5. Evaluation Framework

评价对象：**描述能力**（Existence / Stability / Transfer），不是预测能力。

### 5.1 Primary evaluations（框架冻结；数值门槛执行前预注册）

| ID | 名称 | 问题 | 对照 |
|----|------|------|------|
| E1 | Separability | 分区后观测分布是否可分？ | vs 随机划分 baseline |
| E2 | Persistence | 分区持续性是否高于随机切换？ | vs 随机切换 / 打乱标签 |
| E3 | Transfer | 跨品种是否呈现同向可分/可持续模式？ | 预注册品种矩阵 |

### 5.2 Secondary（可选）

- Period A vs B 分布结构是否 qualitatively 一致  
- 换月邻域敏感度披露（full vs ex_roll，若适用）  

### 5.3 Explicitly out of evaluation

```text
❌ next-bar / next-horizon return predictability
❌ hit-rate / Sharpe / PnL
❌ OPP / Detector 条件期望
❌ 「最优」超参或特征子集竞赛
```

### 5.4 Threshold policy

本 Spec **冻结评价问题与对照逻辑**。  
具体显著性水平、效应量、最小样本、持续 bar 数等 **数值门槛** 在：

```text
CAP-CTX-001 Promote 之后、首次执行之前
→ 写入该次 Run Spec 并预注册（Dataset 已 Freeze）
```

禁止跑数后补门槛。

---

## 6. Null Baseline

Capability 证据必须相对 **Null** 解释，禁止「看起来有簇」叙事。

### 6.0 Purpose of Null（R2 — 强制澄清）

```text
Null baselines evaluate whether observed
structure exceeds simple random expectations.

They do not test whether markets are random.
```

Null **不是**为了证明「市场随机」；  
而是回答：

> observed capability 是否超过简单随机结构。

### N1 — Random partition baseline（→ E1 / Falsification-1）

在相同样本上，用随机划分（或保边际的随机标签）产生「伪条件」；  
真表示若不能显著优于该 baseline 的可分性 → Existence unsupported。

### N2 — Random switching / shuffled persistence（→ E2 / Falsification-2）

打乱时间顺序或随机重排标签后的持续期分布为对照；  
真表示持续期若不能显著长于对照 → Stability unsupported。

### N3 — Isolated-sample check（→ E3 / Falsification-3/4）

仅单品种或单时段成立、预注册矩阵其余不成立 → 不得声称 general capability（至多 H2 / K004）。

### Null 原则

```text
No Null Baseline comparison → No Capability claim
```

---

## 7. Falsification Mapping

映射 Proposal v0.3 Falsification：

| # | Falsification（Proposal） | 本 Spec 评价 | 典型出口 |
|---|---------------------------|--------------|----------|
| F1 | 无不优于随机划分的可区分条件 | E1 vs N1 | H0 / K002 |
| F2 | 持续不低于随机切换期望 | E2 vs N2 | H0 / K003 |
| F3 | 无跨品种一致性 | E3 | H0 / K002 或 H2 / K004 |
| F4 | 仅孤立样本/时段成立 | E3 + period 切分 | H2 / K004 或 K002 |

### Predictive failure clause（强制保留）

```text
Failure of predictive performance
does not invalidate Context Capability.

Example:
  Condition A: higher volatility
  Condition B: lower volatility
  but A does not predict next return
→ Descriptive capability may still hold;
   predictive capability unsupported (out of scope).
```

---

## 8. Evidence Output Contract

### 8.0 Interpretation Boundary（R3 — 强制）

```text
Experiment Result
        ≠
Evidence Interpretation
        ≠
Knowledge Promotion
```

正确流程：

```text
Experiment Output
        ↓
EvidenceRecord（可审计事实层）
        ↓
Evaluation（对照 Null / Falsification）
        ↓
Knowledge Candidate（K001–K004 陈述草案）
        ↓
Review（人工确认）
        ↓
Knowledge（仅 Review 后可称 Accepted Knowledge）
```

| 层级 | 允许 | 禁止 |
|------|------|------|
| Experiment Result | 表、统计量、vs Null 数值 | 直接宣布「Capability 成立」 |
| EvidenceRecord | 归档 Artifact + decision 字段 | 自动晋级 Knowledge |
| Knowledge Candidate | 基于 Evaluation 的候选陈述 | 未经 Review 写入「已证实」 |
| Knowledge Promotion | 用户 / Review 确认后 | 脚本自动 Promote |

**Experiment 不直接产生 Knowledge。**

### 8.1 Artifact

至少包含：

- `experiment_id`（新 ID；Closed 不可改）  
- `parent` / lineage：Proposal v0.3；本 Spec 版本  
- data：已 Freeze 的 symbol 列表、区间、data/manifest 版本指纹  
- 预注册：观测度量列表、Null 方法、数值门槛、代码 revision  
- 原始评价表（可复算）  

### 8.2 Evaluation

- E1 / E2 / E3 结果 vs Null  
- 样本量为证  
- 明确声明：**未评价** predictive / PnL  

### 8.3 EvidenceRecord

- decision ∈ {KEEP, REVERT, HOLD}（Domain）  
- 展示层可映射 Positive / Negative / Inconclusive / Hold  
- metadata：`campaign=CAP-CTX-001`（Promote 后）、CQ 覆盖、Falsification 触碰项  

### 8.4 Knowledge Candidate → Review

收尾可产出 Knowledge **Candidate**（K001–K004）；  
经 Review 后方可称 Accepted Knowledge。  
无 Artifact → 不得称已证实。

### 8.5 Gate implication（非自动）

| Knowledge（经 Review） | Gate 含义（人工） |
|------------------------|-------------------|
| K001 | 可申请 Gate PASS 或 PASS WITH LIMITATION 复评 |
| K002 | Gate 可保持 BLOCKED |
| K003 | 表示不足；非自动改 Spec/Engine |
| K004 | 可能 Gate PASS WITH LIMITATION |

本 Spec **不**自动改写 Gate Verdict；**不**自动 Promote CAP 或 RC001。

---

## 9. Phasing（文档层，非排期承诺）

| Phase | 焦点 | 备注 |
|-------|------|------|
| P0 | Spec Review | v0.1 → PASS WITH MINOR REVISION → v0.2 |
| P0b | Confirmation Review PASS | 待用户确认 |
| P1 | Promote CAP-CTX-001 | **单独决策**；Spec PASS ≠ 自动 Promote |
| P2 | Run Spec（Dataset Freeze + 门槛） | 另授 |
| P3 | Execution → Evidence | 配额与执行另授 |
| P4 | Knowledge Review → Gate 复评 | 基于 Evidence |

### Promotion note（强制）

```text
Proposal Validity
+ Experiment Design Validity
≠ Research Object Promotion

Spec Review PASS ≠ CAP-CTX-001 Promote
```

---

## 10. Relationship to RC001

```text
本 Spec / CAP-CTX-001
        ↓
Evidence → Review → Knowledge → Gate Verdict
        ↓
（仅 PASS*）RC001 Ready
```

RC001 的 RQ（Context 是否改善 Opportunity **评价**）**不在**本 Spec 范围。

---

## 11. Current Status Snapshot

```text
Proposal v0.3: Review PASS ✓
Capability Experiment Spec: v0.2 Confirmation PASS ✓
CAP-CTX-001: PROMOTED（Controlled Research Object）
Run Spec: Draft — CAP_CTX_001_RUN_SPEC.md
Gate: BLOCKED
RC001: Review Passed / Not Accepted
```

---

## 12. Exit from Spec Stage

须用户确认：

1. **Further Revise** — 继续改 Spec  
2. **Confirmation Review PASS** — ✓ 已达成（2026-07-21）  
3. **Promote CAP-CTX-001** — 见 [`CAP_CTX_001_PROMOTE_DECISION.md`](CAP_CTX_001_PROMOTE_DECISION.md)；须用户确认执行 Promote  
4. **Park** — 暂停 Capability 线  

**当前默认**：Spec Confirmation PASS；**不**自动 Promote；**不**写 Run Spec / 代码。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | Draft：EQ；Dataset；Observation；Null；Falsification；Evidence；反 Feature Catalog |
| 2026-07-21 | 0.2 | R1 Dataset Freeze；R2 Null 澄清；R3 Evidence≠Knowledge |
| 2026-07-21 | 0.2.1 | Confirmation PASS 归档；链接 Promote Decision Review |
