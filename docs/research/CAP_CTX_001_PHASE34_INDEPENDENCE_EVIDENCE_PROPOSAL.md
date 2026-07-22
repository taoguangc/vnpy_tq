# CAP-CTX-001 — Phase 3.4 Independence Evidence Proposal

> **Type**: Proposal Review Document（非 Independence Run 执行授权）  
> **Status**: **Confirmation PASS** ✓ — Eligible for Independence Evidence Spec  
> **Version**: 0.2  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CAP_CTX_001_PHASE34_INDEPENDENCE_EVIDENCE_PROPOSAL.md`  
> **Input**:  
> - [`CAPABILITY_PORTFOLIO_BAR_REVIEW.md`](CAPABILITY_PORTFOLIO_BAR_REVIEW.md) v0.2（BAR NOT MET；P3 MET；**P4 NOT MET**）  
> - [`CAP_CTX_001_RUN004_CLOSURE_REVIEW.md`](CAP_CTX_001_RUN004_CLOSURE_REVIEW.md)（CLOSED ✓）  
> - [`K001_KNOWLEDGE_REVIEW.md`](K001_KNOWLEDGE_REVIEW.md)（Strengthened Qualified + Family）  
> **Goal**: 设计如何严格验证 Portfolio Bar **P4（Independence）**；不执行 Observation；不触发 Gate / RC001 / Alpha  
> **Phase map note**: 原 EPOCH「3.4 Gate v2」顺延为 **Phase 3.5**；本 Phase 专责 P4  
> **Prior**: Draft v0.1 → Review **PASS WITH REVISION** → v0.2 → **Confirmation PASS**（2026-07-21）

### Confirmation（binding）

```text
================================================
CAP_CTX_001_PHASE34_INDEPENDENCE_EVIDENCE_PROPOSAL v0.2

Confirmation: PASS ✓

Review chain:
  v0.1 Draft → PASS WITH REVISION → v0.2 → Confirmation PASS

Proposal Purpose:
  P4 Independence Validation Design

Proposal Status:
  CONFIRMED — Eligible for Independence Evidence Spec

P4A1–P4A6 / Taxonomy / Claim Boundary: PASS ✓
Mode: NOT SELECTED（Spec 阶段按 §7 治理表填写）
Independence Observation: NOT AUTHORIZED
Capability Candidate: NO
Gate v2: DEFERRED
RC001: UNCHANGED
K001: Strengthened Qualified（unchanged）
Portfolio Bar: NOT MET（P4 open）
================================================
```

### Confirmation Checklist

| ID | Check | Verdict |
|----|-------|---------|
| C1 | Independence ≠ more samples / window / symbol / var / param | **PASS** |
| C2 | Definition = separated assumptions / choices / ownership；self-confirmation risk | **PASS** |
| C3 | Taxonomy I1–I5 present；Mode not selected | **PASS** |
| C4 | Governance Table includes Removed Dependencies + Residual Bias | **PASS** |
| C5 | Controlled Independence preferred over External Replication | **PASS** |
| C6 | Claim Boundary：no auto Knowledge upgrade / Capability Candidate | **PASS** |
| C7 | No Spec / Observation / Gate / RC001 authorization in this doc | **PASS** |

### Proposal Boundary

```text
Confirmation PASS =
  governance for Phase 3.4 Independence Evidence is locked
  ≠ Mode frozen
  ≠ Spec Confirmation
  ≠ Independence Observation / Auth
  ≠ Gate v2 / Capability Candidate / RC001 / K001 change
```

### 本文不是

```text
❌ RUN005 another expansion（universe / time / family）
❌ Gate v2 Review
❌ Capability Candidate designation
❌ 改写 RUN001–004 Closed 产物
❌ 为提高 K001 置信度而堆同质 Evidence
❌ 强制外部第三方复现作为默认路径
❌ Mode 已选定 / Spec 已确认
```

---

## Claim Boundary（binding · R5）

> **Phase 3.4 may evaluate whether K001 evidence has sufficient independence support; it cannot upgrade Knowledge status or designate Capability Candidate automatically.**

```text
Independence Evidence SUPPORTED
        ≠
K001 tier upgrade（automatic）
        ≠
Capability Candidate
        ≠
Gate v2 PASS
        ≠
RC001 Accepted
```

错误跳跃（禁止）：

```text
P4 PASS → Capability Candidate
```

Knowledge / Portfolio / Gate 变更均须**另授** Review。

---

## Confirmation archive

```text
================================================
Confirmation Review 2026-07-21

Decision: PASS ✓
Object: PHASE34 Independence Evidence Proposal v0.2
Eligible next: Independence Spec Draft
  — Mode via §7 table + I-axis
  — Controlled Independence default
Execution: NONE
================================================
```
---

## 1. Why Phase 3.4 now（P4A1）

### Evidence Portfolio（after RUN004）

| Run | Evidence Type | Question answered | Status |
|-----|---------------|-------------------|--------|
| RUN001 | Discovery | 是否存在描述结构？ | 支持 |
| RUN002 | Temporal OOS | 是否跨时间保持？ | 支持 |
| RUN003 | Cross-sectional | 是否跨 Universe 保持？ | 支持 |
| RUN004 | Observation Family | 是否依赖单一观察域？ | 支持 |

```text
Existence ✓ · Temporal ✓ · Cross-sectional ✓ · Observation Family ✓
```

剩余缺口不是「再证明一次」，而是 **Evidence independence**。

### Portfolio Bar

```text
P1 Temporal              MET ✓
P2 Cross-sectional       MET ✓
P3 Observation Family    MET ✓
P4 Independence          NOT MET  ← Phase 3.4 hard gap
P5 Falsification         PARTIAL
P6 Scope Stability       MET ✓
E1 Engineering           NOT READY
```

```text
Robustness（P1–P3）
        ≠
Independent Validation（P4）
```

继续 RUN005 式扩展只提高同管道置信度，**不推动** Capability Portfolio Bar。

---

## 2. Core Research Question

**禁止问法**：

> 再做一个 Run 是否也 SUPPORTED？  
> 换个指标 / Family / 品种 / 参数能否“更强”？

**正确问法**：

> 在保持 CAP-CTX-001 Research Question 与 Claim Boundary 不变的前提下，  
> K001 的支持是否可在**充分分离的假设 / 选择 / 验证归属**下被复现或证伪——  
> 从而降低仅由原研究路径产生的 self-confirmation risk？

### Allowed claim if future Independence Evidence SUPPORTED（preview）

> Under registered Independence protocol, descriptive condition structure associated with K001 is not solely an artifact of a single shared research path / evidence-generation process.

### Forbidden claim even if SUPPORTED

```text
❌ Context capability proven
❌ Gate PASS / Capability Candidate automatic
❌ Alpha / trading value
❌ Independence = mandatory external institutional audit
❌ K001 unconditional / Qualification removed
```

---

## 3. What Independence means（P4A2 · R1）

### Binding definition

```text
Independence =
  Evidence generation under sufficiently separated assumptions,
  choices,
  or validation ownership,
  such that confirmation is not solely produced by the original research path.
```

> 目标是 **减少 self-confirmation risk**，不是要求“别人重复整条研究”。

### Independence 明确不是（仍属 same evidence generation process）

| 不是 Independence | 仍属于 |
|-------------------|--------|
| 新时间窗 | P1 类扩展 / 同管道 Robustness |
| 新品种 / Universe | P2 类扩展 |
| 新 Observation Family / 新变量 | P3 或 Feature drift |
| 新参数 / 调参 | 同管道优化 |
| 同一 Spec 再跑一遍 | 复现性 ≠ Independence |

```text
new window / symbol / variable / parameter
        ≠
Independence
```

因上述变化通常仍共享 **同一证据生成过程**。

### Shared process factors（why P1–P3 ≠ P4）

RUN001–RUN004 即使维度不同，仍共享：

| Factor | Shared across RUN001–004 |
|--------|--------------------------|
| Research framework | CAP-CTX-001 / PRM / Governance |
| Research team / analyst path | 同一决策链 |
| Evaluation definition | E1 → E2 → E3 结构 |
| Evidence pipeline | Manifest → Evaluation → EvidenceRecord |
| Dataset lineage | TQ offline · CbC · 同指纹家族 |
| Label / partition coupling | M1-driven labels（已披露；仍耦合） |

---

## 4. Independence Taxonomy（P4A2b · R2）

**先 Taxonomy，后 Mode。** 本 Proposal **不选定** Mode。

| Axis | Question |
|------|----------|
| **I1** Method Independence | 是否依赖同一计算流程？ |
| **I2** Data Handling Independence | 是否依赖同一数据处理假设？ |
| **I3** Evaluation Independence | 是否存在独立评价视角？ |
| **I4** Research Path Independence | 是否避免仅由原假设驱动确认？ |
| **I5** Reviewer Independence | 是否存在独立审查归属？ |

### Taxonomy 用途

```text
Independence Mode（未来 Spec）
  must declare which I1–I5 axis（或组合）it targets
  must NOT equate “换一个数据集” with Independence
```

| 误判 | 正确 |
|------|------|
| 换数据集 = Independence | 须说明解除了哪条 I-axis，以及 **Residual Bias** |
| 覆盖全部 I1–I5 才算 P4 | 预注册至少一条充分分离轴；披露仍共享部分 |
| I5 强制外部机构 | I5 可为 Controlled Reviewer 分离；外部复现非默认 |

---

## 5. Controlled Independence（优先 · R4）

### Prefer

```text
Controlled Independence Evidence
```

保持：

- Research Question  
- Knowledge Claim Boundary  

改变：

- **产生证据的路径**（针对预注册 I-axis）

### Deprioritize as default

```text
External institutional replication
```

第三方复现在个人研究系统中成本过高；可作为 **可选增强**（illustrative），**不是** Phase 3.4 默认入口。

```text
Controlled Independence（默认优先）
        >
External Replication（可选；非默认；非 Confirmation 前提）
```

§7 illustrative 占位中的 “External Protocol Replay” **降级为非优先选项**。

---

## 6. Single-variable / freeze discipline（P4A3）

Independence Evidence **不是**“放开一切重做 Discovery”。

### Frozen（default）

| Item | Freeze |
|------|--------|
| Research Question | CAP-CTX-001 descriptive condition structure |
| Claim Boundary | § Claim Boundary；Knowledge ≠ Capability ≠ Gate ≠ Alpha |
| Closed Runs | RUN001–004 不可改写 |
| K001 tier | **不因本 Phase 自动升级** |
| Data baseline | TQ offline · 1m · CbC · 无复权 · 真实成本口径（若执行） |

### Change（exactly the Independence override）

```text
Single design variable = Independence Mode（预注册）
  targeting ≥1 Taxonomy axis I1–I5
```

具体 Mode 须经 §7 Governance Table 选定后写入 **Independence Spec**；本 v0.2 **不冻结** Mode。

### Failure interpretation（binding preview）

| Outcome | Knowledge implication（须预注册映射） |
|---------|--------------------------------------|
| Independence SUPPORTED | 可触发 STRENGTHEN / P4-facing evidence；**≠** Capability Candidate；**≠** K001 auto-upgrade |
| Independence NOT SUPPORTED / 被挑战 | Narrow / Downgrade / retain Qualification；Negative Evidence 一等公民 |
| INFEASIBLE | 新 `run_id`；禁止静默换 Mode 凑 PASS |

---

## 7. Independence Mode Candidate Governance（P4A4 · R3）

**不急于选定**具体 Mode。先固化选择规则，再进入 Spec。

### 7.1 Selection Criteria（must answer before Spec）

| # | Question |
|---|----------|
| 1 | 针对哪条 **Taxonomy axis（I1–I5）**？ |
| 2 | **Removed Dependencies** 是什么？**Residual Bias** 仍是什么？ |
| 3 | 为什么不是新时间 / 品种 / Family / 参数（同管道）？ |
| 4 | Research Question 与 Claim Boundary 是否保持？ |
| 5 | 失败解释是否预注册？ |
| 6 | 为什么不是“为更容易 PASS”的管道变体？ |
| 7 | 是否优先 Controlled Independence（而非默认外部复现）？ |

### 7.2 Forbidden selection bases

```text
❌ 预期更容易 SUPPORTED
❌ 为提高 K001 叙事强度
❌ 未声明的 Feature / Family / Universe / 参数漂移
❌ 用 Gate 工程改造冒充 Independence Evidence
❌ 以 PnL / Alpha 作为 Independence 判据
❌ 将“换数据集 / 再跑一遍”标为 Independence 而不填 Residual Bias
```

### 7.3 Candidate Mode Governance Table（Spec 前必填）

| 项 | 目的 |
|----|------|
| **Candidate Mode** | Independence 验证模式名称 |
| **Independence Dimension** | 测什么（映射 I1–I5） |
| **Shared Components** | 哪些保持共享（诚实披露） |
| **Removed Dependencies** | 去掉 / 分离了什么依赖 |
| **Residual Bias** | 仍可能存在的偏差 / 共享路径 |
| **Independence Argument** | 为何足以降低 self-confirmation risk |
| **Protocol delta** | 相对冻结基线的唯一可审计变化 |
| **Exclusion Criteria** | 为什么不是 P1/P2/P3 扩展 / Feature / 重复跑数 |
| **Failure Interpretation** | 失败说明什么（证伪 / Narrow / Downgrade / …） |
| **Non-claim list** | 即使 SUPPORTED 也不得声称的内容 |

> P4 的核心不是“通过”，而是明确：**哪些依赖被解除，哪些仍存在。**

未填完上表 → **不得**进入 Independence Spec Confirmation。

### 7.4 Illustrative modes only（non-binding）

以下仅作讨论占位，**不是**已选 Mode：

| Placeholder | Illustrative I-axis | Priority note |
|-------------|---------------------|---------------|
| **Alternate Evaluation Chain** | I3 | Controlled — 优先候选讨论 |
| **Proxy-Challenge Protocol** | I1 / I3 | Controlled — 优先候选讨论 |
| **Blind / Sealed Re-analysis** | I4 / I5 | Controlled — 优先候选讨论 |
| **External Protocol Replay** | I5 | **非默认**；可选增强；Confirmation 不要求 |

```text
Illustrative name
        ≠
Selected Independence Mode
        ≠
Authorized Observation
```

---

## 8. Layer boundaries（P4A5）

### P4 ≠ P3 / P1 / P2

```text
new Family / universe / window / parameter
        ≠
Independence Evidence（P4）
```

### P4 ≠ Gate v2 / G7 automatic

```text
Independence Evidence SUPPORTED
        ≠
Gate v2 PASS
        ≠
G7 satisfied by decree
```

### P4 ≠ Capability Candidate / K001 auto-upgrade

见 **Claim Boundary**。错误跳跃禁止。

### Knowledge claim ceiling

> Context descriptive structure appears to have independence support under a registered Controlled Independence protocol.

仍**不**支持：

> Context capability has been proven.

---

## 9. Non-goals（P4A6）

```text
❌ RUN005 universe / time / family / parameter expansion as default next
❌ Alpha / Signal / Trading / PnL optimization
❌ Feature ranking / Model selection
❌ Gate PASS / Capability Candidate / RC001 Accepted
❌ 改写 Closed Runs 或静默换 Mode 凑 PASS
❌ 将 Engineering signal readiness（E1）并入本 Phase 冒充完成
❌ 以强制外部复现作为 Confirmation / Spec 前提
```

---

## 10. Relation to Epoch map

| Phase | Theme | Status |
|-------|-------|--------|
| 3.1 | Governance Consolidation | COMPLETE ✓ |
| 3.2 | Cross-sectional（RUN003） | CLOSED ✓ |
| 3.3 | Observation Family（RUN004） | CLOSED ✓ |
| **3.4** | **Independence Evidence** | **Proposal Confirmation PASS** · Spec eligible |
| **3.5** | Capability Gate v2 Review | DEFERRED |

```text
Phase 3.4 designs how to test P4（definition first）.
Phase 3.5 (Gate v2) remains deferred.
```

---

## 11. Proposal acceptance checklist（v0.2）

| ID | Check | Verdict |
|----|-------|---------|
| P4A1 | Motivation = P4 gap；拒绝堆同质 Run | **PASS** |
| P4A2 | Independence definition；≠ new window/symbol/var/param | **PASS** |
| P4A2b | Independence Taxonomy I1–I5 | **PASS** |
| P4A3 | Freeze / single override / failure mapping | **PASS** |
| P4A4 | Governance Table（含 Removed Dependencies / Residual Bias） | **PASS** |
| P4A4b | Controlled Independence 优先于 External Replication | **PASS** |
| P4A5 | Claim Boundary；P4 ≠ Capability Candidate / K001 auto-upgrade | **PASS** |
| P4A6 | Non-goals / no expansion drift | **PASS** |

> Checklist used for Confirmation；见文首 Confirmation Checklist C1–C7。

---

## 12. Deliverables（Confirmation PASS → Spec）

```text
Proposal Confirmation PASS ✓
        ↓
Independence Evidence Spec（Draft；Mode via §7 table + I-axis）
        ↓
Fill → Auth（各另授）
        ↓
（另授）Controlled Independence execution
        ↓
Evidence Review → K001 / Portfolio Bar update（另授）
```

仍不执行 Observation，直至显式 Auth + 执行指令。Mode 仍须在 Spec 中按 §7 填写，**本 Confirmation 不选定 Mode**。

---

## 13. Next

```text
Confirmation PASS ✓
        ↓
Independence Spec Draft v0.1 — [`CAP_CTX_001_INDEPENDENCE_SPECIFICATION.md`](CAP_CTX_001_INDEPENDENCE_SPECIFICATION.md)
        ≠
Mode frozen here
        ≠
Observation / Gate v2 / Capability Candidate
```

当前：**Confirmation COMPLETE**；**Spec Draft opened**；Mode **未冻结**；Observation **未授权**。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | 首版：Phase 3.4 Independence Proposal；P4 gap；Mode governance；Gate v2 → 3.5 |
| 2026-07-21 | 0.2 | PASS WITH REVISION：Taxonomy I1–I5；Governance 扩字段；Controlled Independence；Claim Boundary |
| 2026-07-21 | 0.2.1 | **Confirmation PASS**；Eligible for Independence Spec；Mode 仍未选 |
