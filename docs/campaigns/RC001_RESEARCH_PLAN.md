# RC-001 — Context-conditioned Opportunity Validation

> **Campaign ID**: RC001  
> **Plan Version**: v0.2  
> **Status**: Review Passed  
> **Accepted**: No（Not Accepted Yet）  
> **Type**: Scientific Investigation  
> **Parent**: Epoch 2.0 — Evidence-driven Knowledge Growth  
> **Method**: [`PAAF_RESEARCH_METHOD.md`](../research/PAAF_RESEARCH_METHOD.md)（PRM v1.0 + Campaign Lifecycle）  
> **P0 Gate**: [`CONTEXT_CAPABILITY_GATE.md`](../research/CONTEXT_CAPABILITY_GATE.md)（v1；Current = **BLOCKED**）  
> **Upstream**: CAP-CTX-001 PROMOTED · Run Spec Confirmation PASS · Execution Auth **NOT GRANTED**；Gate **BLOCKED**  
> **Path**: `docs/campaigns/RC001_RESEARCH_PLAN.md`  
> **Implementation**: ⏸ 未授权（Gate 非 PASS 前不 Ready / Accepted、不写 Run Spec、不写代码、不跑回测）

---

## Research Campaign

| 字段 | 值 |
|------|-----|
| Title | Context-conditioned Opportunity Validation |
| Plan Version | v0.2 |
| Status | **Review Passed** |
| Accepted | **No** |
| Type | Scientific Investigation |
| Parent | Epoch 2.0 — Evidence-driven Knowledge Growth |

### Lifecycle Position（PRM Campaign Lifecycle）

```text
Draft → Review Passed → Ready → Accepted → Running → Completed → Archived
              ▲
           (here)
```

科学问题审查已通过；**尚未**达到可执行 Campaign（Ready / Accepted）。

---

## 1. Research Question

### RQ-001

> **Market Context 是否能够提升 Opportunity 的质量评价能力？**

English:

> Does Market Context provide measurable improvement in Opportunity evaluation?

### 问题边界

本研究**不是**：

- 寻找交易策略
- 优化 Entry / Exit
- 最大化收益
- 调参寻找最佳参数

本研究**只回答**：

> 当一个 Opportunity 出现时，加入 Market Context 后，我们是否获得了**额外的、可审计的**预测信息？

**Operationalization（Campaign 层）**：比较 Context 条件化前后，Opportunity 结果分布是否出现可解释分离。具体 metric / HOLD 门槛在各 EXP Run Spec 预注册——**不在本 Campaign Plan 冻结**。

---

## 2. Background

### 已有 Evidence

**E-OPP16-001** — `OPP16_EXP001`（Closed / Archived）

```text
裸两棒反转（无 Context 过滤）→ inconclusive / HOLD
```

Knowledge：单一 Price Pattern 在当前协议下**未证明**稳定 Alpha。

**E-AFF-CTX** — AFF 历史研究

大量 Context 相关探索，但尚未在 PAAF 下完成正式链路：

```text
Context → Opportunity Quality → Evidence → Repository
```

### Evidence Gap

> Context 是否能**解释** Opportunity 的质量差异？

---

## 3. Hypothesis

### H0（Null）

```text
Market Context does not improve Opportunity evaluation.
```

### H1（Alternative）

```text
Certain Market Context states improve Opportunity expectancy discrimination.
```

存在 Context 状态（Spec 基线 `TREND` / `RANGE`，非临时 Feature）能够提高质量判断的可分性。

---

## 4. Expected Knowledge

RC-001 **不预设** H1 成立。

### If H1 holds — Knowledge K001

```text
Context-conditioned Opportunity evaluation has measurable, auditable evidence.
```

### If H0 holds — Knowledge K002

```text
Current Context representation does not improve OPP16 evaluation.
```

（含：Context Capability 不可用时的 Process Evidence / early close，仍为有效 Knowledge。）

---

## 5. Research Preconditions

Campaign 可执行前必须同时满足。排序（优先级）：

| Pri | Precondition | 说明 |
|-----|----------------|------|
| **P0** | **Context Capability Gate** | 唯一真正阻塞；权威清单见 [`CONTEXT_CAPABILITY_GATE.md`](../research/CONTEXT_CAPABILITY_GATE.md) |
| **P1** | **Research Lifecycle State** | 本 Plan ≥ Review Passed；Ready 须 P0；Accepted 须用户明确授权 |
| **P2** | **Run Spec 定义** | 每 EXP 执行前预注册 metric / 门槛 / 配置（不下沉到 Campaign 冻结） |

展开为三项研究前置：

```text
P1 Opportunity baseline exists
P2 Context capability available
P3 Evaluation protocol preregistered per EXP
```

| 映射 | 含义 |
|------|------|
| Opportunity baseline | OPP16 + Closed `OPP16_EXP001` 作为 Evidence Lineage 父节点 |
| Context capability | Context Capability Gate v1 **Pass** |
| Evaluation protocol | 每个 EXP Run Spec 内预注册；Campaign 只要求「必须预注册」 |

### 5.1 Context Capability Gate v1（P0）

权威定义与验收条文：**[`docs/research/CONTEXT_CAPABILITY_GATE.md`](../research/CONTEXT_CAPABILITY_GATE.md)**（G0–G4）。

本 Plan 只保留边界摘要：

```text
Gate ≠ Context Spec v2
Gate ≠ Market State Engine
Gate =「Context 能否作为 Research Variable？」
```

**Current Gate Verdict（引用）**：`BLOCKED` — `market_state` 恒 `UNKNOWN`。  
**PASS / PASS WITH LIMITATION** → 才可申请 RC001 Ready；**BLOCKED** → 不得 Accepted / EXP002。  
可选 early close（K002-process）须用户授权。

上游（研究问题层，非 RC）：[`CONTEXT_CAPABILITY_RESEARCH_PROPOSAL.md`](../research/CONTEXT_CAPABILITY_RESEARCH_PROPOSAL.md) — 先验证 Context 作为描述变量是否成立，再谈 Gate / RC001。

### 5.2 Evidence Lineage（非 Gate）

`OPP16_EXP001` **不是** Accepted 条件，也**不是**「复用旧结果继续跑」。

```text
RC001
 └── RC001_EXP001
       parent: OPP16_EXP001
```

含义：Closed Evidence 是新研究的**父节点**（Lineage）。Closed 不可变；协议或条件变化必须新 `experiment_id`（Decision 017）。

### 5.3 Metric Policy（非 Campaign Gate）

```text
Research Question → Hypothesis → Experiment Design → Metric
```

Metric 属于 **Experiment**，不属于 Campaign Accepted Gate。

Campaign 只冻结：

> Evaluation metrics must be preregistered before each EXP execution.

各 EXP 可有不同 metric（例如 EXP001=A，EXP002=B），只要在该 EXP 执行前写入 Run Spec。

---

## 6. Research Scope

### Opportunity（Phase 1）

**OPP16** — 两棒反转；Lineage 父节点 `OPP16_EXP001`。

### Context（Phase 1）

- 不重新发明 Context；不临时创造 Feature / Indicator。
- 只使用 **Accepted** `CONTEXT_ENGINE_SPEC` v0.1.1：`MarketState` ∈ {UNKNOWN, TREND, RANGE}；Compression 等仅在约定 `extras`，不膨胀主枚举。
- 能力以 **Context Capability Gate v1** 为准（非完整 Market State Framework）。

---

## 7. Experiment Design

```text
RC001
├── RC001_EXP001 — OPP16 rb，Context-off；parent=OPP16_EXP001
├── RC001_EXP002 — OPP16 rb，Context-on（须 Gate Pass）
└── RC001_EXP003 — OPP16 跨品种（hc, i 或预注册矩阵）
```

| ID | 范围 | 目的 | 主要变量 |
|----|------|------|----------|
| RC001_EXP001 | rb | Control：无 Context 过滤 | Lineage：`parent=OPP16_EXP001` |
| RC001_EXP002 | rb | Treatment：Context 条件化 | `market_state`（TREND/RANGE） |
| RC001_EXP003 | hc, i | Cross-symbol | 同协议；非 rb 特例 |

**One Question**：三条 EXP 服务 RQ-001；每 EXP 仍一个主要假设。

**数据协议**：Decision 001 — TQ 离线 / 1m / CbC / 无复权 / 真实成本。

---

## 8. Evidence Required

| 产物 | 要求 |
|------|------|
| **Artifact** | 数据版本、参数、配置、代码 revision |
| **Evaluation** | **该 EXP** 预注册的 outcome/metric、sample、CI、稳健性 |
| **EvidenceRecord** | decision ∈ {KEEP, REVERT, HOLD}；metadata 含 `campaign=RC001`、symbol、context 条件、lineage |

**Classification（展示层）**：Positive / Negative / Inconclusive / Hold — 映射 Domain `decision`。

---

## 9. Evaluation Criteria（Campaign 层）

**禁止**以「赚钱 / 亏钱」为唯一标准。

### Primary（方向，非冻结数值）

Context **增量**信息：outcome separation / conditional expectancy difference（具体定义与门槛 → 各 EXP Run Spec）。

### Secondary

Cross symbol（EXP003）；roll 邻域等按 Spec 约定。

---

## 10. Promotion Boundary

本 RC **不**自动晋级 Production。

| 层级 | 条件 |
|------|------|
| **Campaign Knowledge Accepted** | 多 EXP 完成 + Validation 只读比较 + 明确 K001 或 K002 |
| **Detector Candidate** | 仅当 K001 + 独立 Validation；非本 RC 默认产出 |
| **Production Candidate** | Decision 011 + E4 + 用户确认；**不在 RC-001 范围** |

单品种 rb 仅 positive → 默认 **HOLD**。  
`PromotionReadinessView.may_auto_promote` 恒为 False。

---

## 11. Exit Criteria

RC-001 完成 = 产生明确 Knowledge（四选一）：

```text
Accepted Knowledge（K001）
Negative Evidence（K002）
Inconclusive
Research Hold
```

**不是**「找到 Alpha」。

---

## 12. Out of Scope

- 新 Feature / Indicator / Strategy
- 参数搜索与 PnL 优化
- 自动交易 / Execution / ML
- Dashboard / UI
- 修改 Architecture Baseline / Domain / 基础 Contract
- 复活或改写 Closed `OPP16_EXP001` 产物
- 为通过 Gate 而造实验专用 Context 逻辑（违反 G4）

---

## 13. Expected Outputs（Accepted 之后）

- `docs/experiments/RC001_EXP00N.md`（每 EXP Run Spec；含预注册 metric）
- `research/output/evidence/<experiment_id>/`
- Validation Comparison View（Campaign 级，只读）
- Campaign Close Note（K001 或 K002）

---

## 14. Execution Prerequisites（进入 Accepted / Running 之前）

取代 v0.1「Accepted conditions: metric freeze」。

```text
Execution prerequisites:
  1. Context Capability Gate v1 ∈ {PASS, PASS WITH LIMITATION}
     （见 docs/research/CONTEXT_CAPABILITY_GATE.md）
  2. Lifecycle: Ready → 用户明确 Accepted
  3. 目标 EXP 的 Run Spec 已定义且 metric 已预注册
```

**当前禁止**：

- ❌ RC001 Ready / Accepted  
- ❌ EXP001 Run Spec  
- ❌ 写代码 / 跑回测 / 改 Context Spec / 新 Decision  

**当前允许**：

- ✅ 保持 Review Passed  
- ✅ Gate 清单审阅与 Capability 研究立项（用户另授）  
- ✅ Gate PASS 后申请 Ready → Accepted  

### Future start path

```text
Context Capability Gate PASS | PASS WITH LIMITATION
          ↓
RC001 Ready → Accepted（用户授权）
          ↓
RC001_EXP001 Run Spec
          ↓
Experiment → Evidence → Evaluation → Knowledge
```

---

## 15. Research Plan Review

### v0.1 Verdict（历史）

```text
ACCEPT WITH CONDITIONS — Draft v0.1
```

条件曾把 metric 冻结与 EXP001 引用策略列入 Accepted Gate——**v0.2 已修正**。

### v0.2 Method Refinement Verdict

| 审查项 | 结论 |
|--------|------|
| Q1 RQ 单一清晰 | **Pass**（科学问题成立） |
| Q2 Experiment 可解释 | **Pass as design**；执行依赖 P0 Gate |
| Q3 Promotion 足够严 | **Pass** |

```text
Review Passed — Plan v0.2
Not Accepted Yet

Scientific question: cleared
Executable campaign: blocked on Context Capability Gate (P0)
```

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-20 | 0.1 | Draft：Epoch 2 首个 RC；含 Plan Review |
| 2026-07-20 | 0.2 | Method Refinement：Status→Review Passed；P0 Gate；Preconditions；Metric 下沉 EXP；Lineage；Lifecycle |
| 2026-07-20 | 0.2.1 | 引用 `CONTEXT_CAPABILITY_GATE.md`；§5.1 改为摘要；Verdict 量表对齐 |
| 2026-07-20 | 0.2.2 | 链接 Capability Research Proposal；明确 Proposal → Gate → RC001 |
| 2026-07-20 | 0.2.3 | Upstream → Proposal v0.2 Review Passed；CAP-CTX-001 Candidate |
| 2026-07-21 | 0.2.4 | Upstream → Proposal v0.3（Observation Space + Falsification） |
| 2026-07-21 | 0.2.5 | Proposal PASS；链接 Capability Experiment Spec Draft |
