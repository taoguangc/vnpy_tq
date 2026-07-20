# ABR-003 — First Research Capability Compliance Review

> **Review ID**: ABR-003  
> **Title**: First Research Capability Compliance Review（第一次研究能力合规审计）  
> **Date**: 2026-07-20  
> **Status**: Completed  
> **Kind**: Compliance Audit（not Architecture Redesign；not refactor）  
> **Baseline**: `architecture-baseline-v1`  
> **Under review**: Platform Construction Sprint 2（Validation Projection）  
> **Path**: `docs/reviews/ABR-003_CAPABILITY_COMPLIANCE.md`

**一句话**：Validation Projection 是否真正提升了 Evidence 使用质量，而没有偷偷变成 Analysis Engine？

**ABR 系列定位**：

| Review | Role |
|--------|------|
| ABR-001 | Architecture Baseline |
| ABR-002 | Infrastructure Compliance |
| ABR-003 | **Research Capability Compliance**（Projection 研究能力） |

```text
Spec → Implementation → Contract Tests → ABR（Compliance）→ Close Sprint
```

---

## Overall Verdict

```text
PASS WITH BACKLOG
```

Sprint 2 实现符合 Architecture Baseline v1。未发现 Compliance Failure。  
既有治理 Backlog（REPO-001、CLEANUP-001/002、ABR-001 VOC-*）保留，不在本轮修复。

| Verdict | 含义 |
|---------|------|
| FAIL | 违反 Contract/Baseline → 不得关闭 Sprint |
| **PASS WITH BACKLOG** | 符合基线；延期治理项 → **可关闭 Sprint** |
| PASS | 符合且无待治理项（少见） |

---

## Executive Summary

| 检查项 | 结论 |
|--------|------|
| Projection Compliance | **Pass** |
| Evidence Integrity | **Pass** |
| Comparison Neutrality | **Pass** |
| Promotion Boundary | **Pass** |
| Baseline Integrity | **Pass** |

**Evidence**：`tests/contracts/test_validation_projection_contract.py` + prior projection/storage contracts（本审查时 34 相关测试 OK）。  
**Contract Review**：`docs/development/SPRINT_2_CONTRACT_REVIEW.md` → PASS（无 Contract 扩展）。

---

## 1. Projection Compliance

**问题**：Validation 是否只是 Projection？是否只消费已有 Evidence？

| 检查 | 结果 |
|------|------|
| 实现位于 `strategies/paaf/projection/` | Pass |
| 经 `EvidenceReadView` 只读加载 | Pass |
| 未创建 Evaluation / Evidence Domain 对象 | Pass |
| Sprint Contract Review：无需扩展 foundation Contract | Pass |

**Findings**：无 Compliance Failure。

---

## 2. Evidence Integrity

**问题**：是否存在 Validation → 修改原 Evidence？

| 检查 | 结果 |
|------|------|
| 路径保持 `Evidence → Validation View` | Pass |
| `save_*` / update / replace / delete 经 ReadView 拒绝 | Pass |
| 构建前后 `list_evidence_ids` 不变（契约测试） | Pass |
| metrics / decision 原样复制 | Pass |

**Findings**：无 Compliance Failure。

---

## 3. Comparison Neutrality

**问题**：Comparison 是否并列展示，而未滑向 Ranking？

| 允许 | 结果 |
|------|------|
| 并列展示 entries | Pass |
| 聚合已有 decision / status 计数 | Pass |
| 引用 classification（`subject_kind`） | Pass |
| 稳定排序 `(experiment_id, evidence_id)`（非优劣排序） | Pass |

| 禁止 | 结果 |
|------|------|
| 自动优劣排序 / Alpha Ranking | Pass（未实现） |
| 隐含评分 / `score` 字段 | Pass（测试断言无 invented score） |

**Findings**：无 Compliance Failure。  
**Note（非失败）**：`KEEP→ACCEPTED` / `REVERT→REJECTED` 为展示别名，Domain decision 仍保留在快照中。

---

## 4. Promotion Boundary

**问题**：是否仍只回答“条件可见性”，而不回答“应该上线”？

| 检查 | 结果 |
|------|------|
| `may_auto_promote=False`（硬编码） | Pass |
| Readiness 输出 blocking / suggested_next 为可见性描述 | Pass |
| 无 auto-promote / Decision Engine 语义 | Pass |
| KEEP 亦声明非自动晋级 | Pass |

**Findings**：无 Compliance Failure。

---

## 5. Baseline Integrity

```text
Decision Added:        0
Contract Added:        0
Domain Changed:        No
Baseline Changed:      No
Knowledge Duplicated:  No
```

**Findings**：无 Compliance Failure。

---

## Backlog（不修；非 Failure）

| ID | Item | Severity |
|----|------|----------|
| REPO-001 | `save_*` naming deferred | Low |
| CLEANUP-001/002 | Legacy Signal / adapter | Medium |
| ABR-001 VOC-* | Documentation vocabulary drift | Low |

---

## Explicitly out of scope

- 重构 / 性能 / UI  
- 扩展 Contract / 新 Domain  
- v0.4 Validation Protocol 启动  
- 更多 Projection 产品化  

---

## Gate decision

| Gate | Decision |
|------|----------|
| Close Sprint 2 | **Authorized** |
| Commit Sprint 2 + this ABR + Sprint Report | **Authorized** |
| Push accumulated history | **Authorized** |
| Start v0.4 / more Projections | **Not authorized**（空窗期继续） |

---

## 修订记录

| 日期 | 说明 |
|------|------|
| 2026-07-20 | Completed：PASS WITH BACKLOG |
