# CAP-CTX-001 — Independence Evidence Specification（v0.1）

> **Type**: Independence Evidence Run Specification（Controlled Independence · Portfolio Bar **P4**）  
> **Status**: **Confirmation PASS** ✓ — Eligible for Pre-registration Fill  
> **Version**: 0.2  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CAP_CTX_001_INDEPENDENCE_SPECIFICATION.md`  
> **Campaign**: CAP-CTX-001（PROMOTED）  
> **Parent Knowledge**: K001 (**Strengthened Qualified**) — [`K001_KNOWLEDGE_REVIEW.md`](K001_KNOWLEDGE_REVIEW.md)  
> **Parent Proposal**: [`CAP_CTX_001_PHASE34_INDEPENDENCE_EVIDENCE_PROPOSAL.md`](CAP_CTX_001_PHASE34_INDEPENDENCE_EVIDENCE_PROPOSAL.md) — **Confirmation PASS**  
> **Governance**: [`CROSS_EVIDENCE_GOVERNANCE.md`](CROSS_EVIDENCE_GOVERNANCE.md) v1.2 Baseline  
> **Lineage**: Original chain `RUN001 → RUN002 → RUN003 → RUN004`（Closed；不可改写）  
> **Evidence Type**: **Independence Evidence**（Portfolio Bar **P4**）  
> **Possible future run_id**: `CAP_CTX_001_RUN005`（仅 Auth 后；本 Spec **不**授权）  
> **Purpose**: Design controlled independent evidence generation for K001 — **not** Gate · **not** RC001 · **not** Alpha · **not** Capability Candidate  
> **Prior**: Draft v0.1 → Review **PASS WITH REVISION** → v0.2 → **Confirmation PASS**

### Spec Confirmation（2026-07-21）

```text
================================================
CAP_CTX_001_INDEPENDENCE_SPECIFICATION v0.2

Confirmation: PASS ✓

Review chain:
  v0.1 Draft → PASS WITH REVISION → v0.2 → Confirmation PASS

Eligible for: Pre-registration Fill Draft

Mode: NOT FROZEN in Spec（Fill §5.2 冻结）
Fill / Auth / Observation: NOT STARTED / NONE / NONE
Execution: NOT AUTHORIZED

K001: Strengthened Qualified（unchanged）
Portfolio Bar: NOT MET（P4 open）
Capability Candidate: NO
Gate: BLOCKED
RC001: UNCHANGED
================================================
```

### Spec Review（v0.1 → v0.2）

```text
Decision: PASS WITH REVISION ✓

R1 Mode B+C operational protocol（phased）— added §4.2
R2 Operational PASS/Partial/FAIL criteria — added §6.5
R3 Artifact lock for Mode B — added §3.5
R4 EQ / Claim / Non-goals — PASS（unchanged）
```

### Claim Boundary（binding）

> This Spec may define how to evaluate whether K001 evidence has sufficient **independence support**; it does **not** prove K001 is “true”, and it cannot upgrade Knowledge or designate Capability Candidate automatically.

```text
Independence Evidence SUPPORTED
        ≠
K001 proven / unconditional
        ≠
Capability Candidate
        ≠
Gate PASS
        ≠
RC001 Accepted
        ≠
External replication completed
```

错误跳跃（禁止）：

```text
P4 PASS → Capability Candidate
```

须另授 Portfolio Bar / Gate Review。

### What this Spec is not answering

```text
❌ “Can K001 be reproduced?”（过早接近外部复现）
❌ “Is K001 true?”
❌ “Does another Family / universe / window also work?”（P1–P3；已覆盖）
```

**Target EQ framing**：

```text
Does K001 retain support under a controlled independent
evidence generation process?
```

### Boundary

```text
✅ Spec Confirmation PASS ✓
❌ Fill Mode freeze / Auth / Observation
❌ Mode A/D required
❌ Capability Candidate / Gate / RC001
```
---

## 1. Experiment Question — EQ-CTX-005

### EQ-CTX-005

```text
Does K001 retain support under a controlled independent
evidence generation process?
```

中文：

> 在保持 Research Question 与 Knowledge Claim Boundary 不变的前提下，  
> K001 是否在**受控的独立证据生成过程**下仍获得支持——  
> 从而降低仅依赖原始研究路径的 self-confirmation risk？

### 1.1 Answers / does not

| Answers（P4） | Does not answer |
|---------------|-----------------|
| Independence support for current evidence chain | Capability proven |
| Whether support is solely an artifact of original path | Gate / Capability Candidate |
| Narrower qualification if independence weak | Alpha / trading |
| Residual Bias disclosure | External institutional audit as requirement |

```text
Robustness（RUN001–004）
        ≠
Independence（this Spec）
```

---

## 2. Independence Objective

### 2.1 Process diagram

```text
Original Evidence Chain（Closed）

  RUN001 Discovery
  RUN002 Temporal OOS
  RUN003 Cross-sectional
  RUN004 Observation Family

        ↓

Independent Evidence Process
  （Controlled Independence；预注册 Mode）

        ↓

Compare Support / Failure
  vs pre-registered criteria
```

### 2.2 Objective statement

> Compare K001’s support under the **original evidence chain** with support under a **pre-registered independent evidence-generation path**, and interpret outcomes per §6 — without redesigning the Research Question to inflate confirmation.

### 2.3 Taxonomy reference（from Proposal）

Mode 必须声明针对的 Independence Axis（≥1）：

| Axis | Question |
|------|----------|
| **I1** Method | 是否依赖同一计算流程？ |
| **I2** Data Handling | 是否依赖同一数据处理假设？ |
| **I3** Evaluation | 是否存在独立评价视角？ |
| **I4** Research Path | 是否避免仅由原假设驱动确认？ |
| **I5** Reviewer | 是否存在独立审查归属？ |

```text
换数据集 / 新窗 / 新品种 / 新参数
        ≠
Independence（除非填清 Removed Dependencies + Residual Bias）
```

---

## 3. Independence Boundary

### 3.1 Held constant（frozen）

| Item | Freeze |
|------|--------|
| Research Question | CAP-CTX-001 descriptive condition structure |
| K001 Claim Boundary | Strengthened Qualified · Qualification retained unless Narrow/Downgrade via Review |
| Evidence Contract | Manifest → Evaluation → EvidenceRecord · layer separation |
| Governance Rules | CROSS_EVIDENCE_GOVERNANCE v1.2；Negative Evidence 一等公民 |
| Closed Runs | RUN001–004 不可改写 |
| Data baseline（若执行） | TQ offline · 1m · CbC · 无复权 · 真实成本口径 |

### 3.2 Changed（exactly one design override）

```text
Change ≥1 Evidence Generation Dependency
  via pre-registered Independence Mode
  targeting ≥1 Taxonomy axis I1–I5
```

### 3.3 Single-variable discipline

```text
Independence Spec changes the evidence-generation path only
（Mode / dependency separation）.

It does not reopen P1/P2/P3 as experimental variables.
Universe / time / Family expansion are not default overrides.
```

### 3.4 Controlled Independence preference

```text
Controlled Independence（默认）
        >
External Replication（Mode D；非默认；非本 Spec Confirmation 前提）
```

保持 RQ + Claim；改变**产生证据的路径**。

### 3.5 Artifact lock（Mode B binding）

若选定含 Mode B 的路径：

```text
Closed Run artifacts（RUN001–004）
  = read-only inputs for independent evaluation
  ≠ editable to improve Independence PASS
  ≠ Discovery re-run disguised as Independence
```

允许：按 Fill 冻结的 Independent Evaluation Rubric（IER）**重新解释 / 重新评分**。  
禁止：改写 Closed Evaluation 数值、改 Fingerprint、追加未注册品种/窗/Family。

---

## 4. Candidate Modes（not frozen in Spec）

本 § 仅列候选与讨论优先级；**Spec Confirmation 不冻结 Mode**。Mode 在 Fill §5.2 冻结。

### Mode A — Independent Implementation Path

| | |
|--|--|
| Meaning | 重新实现 observation / evaluation pipeline |
| Change | same data · same question · **different implementation path** |
| Targets（illustrative） | I1 Method |
| Tests | pipeline dependency · implementation bias |
| Cost | 工程成本较高 |
| Priority | 次优先（非默认首选） |

### Mode B — Independent Evaluation Path

| | |
|--|--|
| Meaning | 保持 Closed Evidence Artifacts；**独立评价 / 重新解释** |
| Change | Evidence ≠ Evaluation 分离 |
| Targets（illustrative） | I3 Evaluation（可及 I5） |
| Tests | 评价视角独立性；符合 PAAF Evidence 分层 |
| Priority | **Primary candidate component** |

### Mode C — Independent Research Specification

| | |
|--|--|
| Meaning | 从 Research Question 重新规格化评价标准；**起草 IER 时不打开**原始 intermediate choice 细节 |
| Change | researcher degrees of freedom 路径分离 |
| Targets（illustrative） | I4 Research Path |
| Tests | 研究路径选择偏误（Family → Eval → Knowledge 解释链） |
| Priority | **Primary candidate component** |

### Mode D — External Replication

| | |
|--|--|
| Meaning | 第三方按冻结 Spec 复现 |
| Targets（illustrative） | I5 Reviewer（最强） |
| Priority | **Not recommended for this stage**；可选增强，非 Confirmation/Fill 前提 |

### 4.1 Suggested primary candidate（non-binding in Spec）

```text
Primary candidate for Fill:
  Mode B + Mode C combination
```

**理由（非预选结果）**：当前最大风险更可能是 **researcher choice bias**，而非单纯代码错误。

### 4.2 Mode B+C operational protocol（if Fill selects B+C）

```text
Phase C — Independent Research Specification
  1. Draft Independent Evaluation Rubric (IER) from EQ-CTX-005 / RQ
  2. During IER drafting: do NOT open RUN001–004 intermediate design
     choices (Family pick rationale, metric recipes, threshold tuning notes)
  3. May open: Claim Boundary, EQ text, Governance, Closed status labels only
  4. Output: sealed IER（Fill 冻结）

Phase B — Independent Evaluation Path
  1. Unlock Closed artifacts（read-only）
  2. Apply sealed IER to original chain support claims
  3. Record PASS / Partial / FAIL per §6.5
  4. Disclose Shared Components + Residual Bias
```

```text
Phase C before Phase B
        =
reduce research-path contamination of the rubric
```

Mode A / D 不在 B+C 默认路径内；另选须新填 Governance Table。

```text
Primary candidate
        ≠
Mode frozen by Spec
        ≠
Auth / Observation
```
---

## 5. Governance（Spec-level）

### 5.1 Integrity Constraint（C-XEV style）

```text
No methodological modification shall be introduced
for the purpose of increasing support for existing knowledge.

Independence Mode shall reduce self-confirmation risk,
not optimize for PASS.
```

### 5.2 Candidate Mode Governance Table（Fill 前必填 · 冻结 Mode 用）

| 项 | 目的 |
|----|------|
| **Candidate Mode** | 名称（可含 B+C 组合） |
| **Independence Dimension** | 映射 I1–I5 |
| **Shared Components** | 仍共享什么 |
| **Removed Dependencies** | 解除什么 |
| **Residual Bias** | 仍可能偏差 |
| **Independence Argument** | 为何降低 self-confirmation risk |
| **Protocol delta** | 唯一可审计变化 |
| **Exclusion Criteria** | 为何不是 P1/P2/P3 / Feature / 重跑 |
| **Failure Interpretation** | 见 §6 映射 |
| **Non-claim list** | 即使 SUPPORTED 也不得声称 |

> P4 核心不是“通过”，而是：**哪些依赖被解除，哪些仍存在。**

未填完 → **不得** Fill Confirmation / Auth。

### 5.3 Forbidden bases for Mode selection

```text
❌ 预期更容易 SUPPORTED
❌ 为提高 K001 叙事
❌ 未声明的 Family / Universe / 参数漂移
❌ 以 PnL / Alpha 为判据
❌ 默认强制 External Replication
❌ “换数据集 = Independence” 且不填 Residual Bias
```

---

## 6. Null / Failure Interpretation

### 6.1 Design principle

```text
Independence FAIL
        ≠
automatic “K001 is false”
```

更准确：当前证据链的**独立性支持不足**，或范围需收窄——须另授 Knowledge Review。

### 6.2 Result → Interpretation（binding preview）

| Result | Interpretation |
|--------|----------------|
| **PASS** | Independence support increases（P4-facing evidence）；可映射 STRENGTHEN / P4 update 候选；**≠** Capability Candidate |
| **Partial** | K001 scope may need **narrower qualification**；Qualification retained or Narrow |
| **FAIL** | Current evidence chain **insufficiently independent**；Narrow / Downgrade / retain per Review；Negative Evidence 一等公民 |
| **INFEASIBLE** | Mode 不可行 → 新 `run_id`；禁止静默换 Mode 凑 PASS |

### 6.3 Registered Knowledge Action mapping（Fill 冻结）

| Outcome | Action（预览；Fill 锁定） |
|---------|---------------------------|
| PASS | STRENGTHEN（Independence）或等价 P4-facing action |
| Partial | NARROW（qualification） |
| FAIL | NARROW 或 DOWNGRADE |
| INFEASIBLE | 无 Knowledge Decision；新 Run |

```text
Registered Action
        ≠
Knowledge Decision
        ≠
Portfolio Bar MET automatic
        ≠
Capability Candidate
```

### 6.4 Null / challenge posture

Independence protocol 须使 **NOT SUPPORTED / FAIL 可被诚实记录**；禁止事后改 Mode / 改判据以提高 PASS 概率。具体 Null 细节（若需要独立于 RUN001 N1/N2）在 Fill 中预注册。

### 6.5 Operational decision rules（Fill 可细化，不可削弱）

针对 K001 核心主张（在注册条件下 descriptive condition structure 获得支持）：

| Result | Operational meaning |
|--------|---------------------|
| **PASS** | Sealed IER concludes **retain support** on the same Claim Boundary scope as current K001 citation（universe + families as already registered），with Residual Bias disclosed |
| **Partial** | IER retains support **only under narrower scope** than current K001 citation（须列出收窄项） |
| **FAIL** | IER does **not** retain support for the core claim；or finds support contingent on undisclosed original-path choices that IER rejects |
| **INFEASIBLE** | Phase C/B 无法按 Fill 执行（例如 artifact 缺失）→ 新 `run_id`；禁止换 Mode 凑 PASS |

```text
FAIL
  =
insufficient independence support for current claim packaging
  ≠
automatic “descriptive structure does not exist”
```

---

## 7. Mode Selection Table（candidates only · Spec 不冻结）

| ID | Mode | I-axis（illustrative） | Stage priority | Frozen in Spec? |
|----|------|------------------------|----------------|-----------------|
| A | Independent Implementation Path | I1 | Secondary | **No** |
| B | Independent Evaluation Path | I3（±I5） | **Primary component** | **No** |
| C | Independent Research Specification | I4 | **Primary component** | **No** |
| B+C | Evaluation + Research Path combo | I3+I4 | **Suggested primary** | **No** |
| D | External Replication | I5 | Deprioritized | **No** |

Fill 阶段从本表选出并完成 §5.2 全表后，方可冻结 Mode。

---

## 8. Non-goals

```text
❌ 证明 K001 “为真”
❌ 外部机构复现作为本阶段必选项
❌ RUN005 式 Universe / Time / Family / 参数扩展冒充 P4
❌ Feature ranking / Model selection / PnL
❌ Gate PASS / Capability Candidate / RC001 Accepted
❌ 本 Spec 内授权 Observation / 选定并冻结 Mode
❌ 将 Engineering signal readiness（E1）并入冒充 P4 完成
❌ P4 PASS → 自动 Capability Candidate
```

---

## 9. Deliverables path（Confirmation PASS →）

```text
Independence Spec Confirmation PASS ✓
        ↓
Fill（§5.2 Mode 冻结）
        ↓
Authorization
        ↓
RUN005（可能；另授 Observation）
        ↓
Evidence Review
        ↓
K001 Review（另授）
        ↓
Portfolio Bar Update（另授）
        ≠
Capability Candidate automatic
```

---

## 10. Spec acceptance checklist（v0.2 Confirmation）

| ID | Check | Verdict |
|----|-------|---------|
| IS1 | EQ-CTX-005 = controlled independent process；≠ “reproduced” | **PASS** |
| IS2 | Objective diagram + compare support/failure | **PASS** |
| IS3 | Boundary + Artifact lock §3.5 | **PASS** |
| IS4 | Modes A–D；D deprioritized；B+C suggested only | **PASS** |
| IS4b | Mode B+C operational protocol §4.2 | **PASS** |
| IS5 | Governance Table + Residual Bias | **PASS** |
| IS6 | Failure ≠ K001 false；§6.5 operational rules | **PASS** |
| IS7 | Mode Selection Table not frozen in Spec | **PASS** |
| IS8 | Non-goals + Claim Boundary | **PASS** |

---

## 11. Next

```text
Confirmation PASS ✓
        ↓
Independence Fill Draft（Mode via §5.2；建议 B+C）
        ≠
Observation / Gate / Capability Candidate
```

当前：**Confirmation COMPLETE**；**Eligible for Fill**；Mode **由 Fill 冻结**；Observation **NONE**；Execution **NOT AUTHORIZED**。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | 首版 Draft：EQ-CTX-005；Objective；Boundary；Modes A–D；B+C 建议候选；Failure mapping；Non-goals |
| 2026-07-21 | 0.2 | PASS WITH REVISION：§4.2 B+C protocol；§3.5 Artifact lock；§6.5 operational rules |
| 2026-07-21 | 0.2.1 | **Confirmation PASS**；Eligible for Fill |
