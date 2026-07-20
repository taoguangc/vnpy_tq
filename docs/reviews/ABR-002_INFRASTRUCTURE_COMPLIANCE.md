# ABR-002 — First Infrastructure Compliance Review

> **Review ID**: ABR-002  
> **Title**: First Infrastructure Compliance Review（第一次基础设施合规审计）  
> **Date**: 2026-07-20  
> **Status**: Completed  
> **Kind**: Compliance Audit（not Architecture Redesign）  
> **Baseline**: `architecture-baseline-v1`（commit `3bc810a`）  
> **Under review**: Platform Construction Sprint 1（Projection / Portfolio）  
> **Path**: `docs/reviews/ABR-002_INFRASTRUCTURE_COMPLIANCE.md`

**一句话**：回答唯一问题——Sprint 1 实现是否仍然符合 Architecture Baseline v1？

**制度**：ABR-001 建立基线；ABR-002 起审查**实现是否遵守基线**。不审功能美观、不提重构建议；超出范围记 Backlog。

```text
Spec → Implementation → Contract Tests → ABR（Compliance）→ Next
```

---

## Overall Verdict

```text
PASS WITH BACKLOG
```

Sprint 1 实现符合 Architecture Baseline v1 与 Accepted Contracts。  
未发现 Compliance Failure。既有治理 Backlog（REPO-001、CLEANUP-001/002 等）保留，不在本轮修复。

| Verdict | 含义 |
|---------|------|
| FAIL | 违反 Contract/Baseline → 不得继续 |
| **PASS WITH BACKLOG** | 符合基线；存在延期治理项 → **可继续** |
| PASS | 符合且无待治理项（少见） |

---

## Executive Summary

| 检查项 | 结论 |
|--------|------|
| Storage Compliance | **Pass** |
| Projection Compliance | **Pass** |
| Dependency Compliance | **Pass** |
| Contract Compliance | **Pass** |
| Knowledge Duplication | **Pass** |

**Evidence**：`tests/contracts/test_storage_contract.py` + `tests/contracts/test_projection_contract.py`（本审查时合计 32 相关测试 OK）。

---

## 1. Storage Compliance

**问题**：Repository 是否仍符合 Append-only Storage Contract？

| 检查 | 结果 |
|------|------|
| Create-only writes（`open("x")` / duplicate → `FileExistsError`） | Pass |
| `save_*` 语义为 create-once（未 rename；符合 Spec 允许） | Pass |
| `update` / `replace` / `overwrite` / `delete` 显式拒绝 | Pass |
| 只读扩展 `list_evidence_ids` / `list_experiment_ids` | Pass（Storage Spec 允许 list_*） |
| Contract Tests 覆盖 FS + Memory | Pass |

**Findings**：无 Compliance Failure。

---

## 2. Projection Compliance

**问题**：Projection 是否只是消费 Evidence，而不是新的 Domain？

| 检查 | 结果 |
|------|------|
| Portfolio 为 Projection（Decision 017 五桶为分类维度） | Pass |
| 视图模型在 `strategies/paaf/projection/`，未写入 Domain Spec/models | Pass |
| `EvidenceReadView` 拒绝对 Repository 回写 | Pass |
| 无 Timeline / Dashboard UI / Query Engine 越界实现 | Pass |
| HOLD / REVERT 证据被计入（Negative Evidence 一等公民） | Pass |

**Findings**：无 Compliance Failure。

---

## 3. Dependency Compliance

**问题**：是否新增了违反 Baseline 的依赖关系？

| 检查 | 结果 |
|------|------|
| Projection → 只读消费 Evidence 记录类型 | Pass |
| Projection ↛ 修改 Repository / Domain | Pass |
| Projection ↛ 交易下单 / Strategy 编排 | Pass |
| 未引入新的「权威写入口」 | Pass |

**Findings**：无 Compliance Failure。

---

## 4. Contract Compliance

**问题**：是否有任何实现偏离 Accepted Contract？

| Contract | 结果 |
|----------|------|
| `APPEND_ONLY_STORAGE_SPEC` | Pass |
| `PROJECTION_LAYER_SPEC` | Pass（实现授权来自 Sprint 1；未扩展 Spec） |
| `EVIDENCE_DOMAIN_SPEC` | Pass（未改 Domain） |
| Decision 017 / 018 | Pass（无新 Decision） |

**Findings**：无 Compliance Failure。  
**Note（非失败）**：`subject_kind` → Portfolio 桶映射为 Projection 层分类，未改 Domain `SUBJECT_KINDS`。

---

## 5. Knowledge Duplication

**问题**：是否重新计算、推导、复制了 Evidence？

| 检查 | 结果 |
|------|------|
| metrics 从 Evidence 原样复制 | Pass |
| decision 计数为聚合，非 re-score | Pass |
| 未发明 `score` / `portfolio_score` | Pass |
| 未重算 Evaluation / 未改 Provenance | Pass |
| Contract Tests 断言 Zero Knowledge Duplication | Pass |

**Findings**：无 Compliance Failure。  
允许的聚合（count / group / sort / filter / reference）符合 Sprint 原则：  
*Projection may aggregate knowledge, but never derive new evidence.*

---

## Architecture Metrics（Sprint 1）

```text
Decision Added:        0
Contract Added:        0
Domain Changed:        No
Baseline Changed:      No
Knowledge Duplicated:  No
ABR Required:          Completed（this review）
```

---

## Backlog（不修；非 Failure）

| ID | Item | Severity |
|----|------|----------|
| REPO-001 | `save_*` → 未来倾向 `record_*`；不为命名改 API | Low — deferred |
| CLEANUP-001/002 | Legacy Adapter + Signal 表述 | Medium — Cleanup Sprint |
| ABR-001 VOC-* | 文档词汇滞后项 | Low — 文档治理 |

---

## Explicitly out of scope

- 功能完整度 / UX / 性能  
- 重构建议  
- Timeline / Dashboard / Analytics 实现  
- Push 策略以外的发布流程变更  

---

## Gate decision

| Gate | Decision |
|------|----------|
| Close Sprint 1 | **Authorized**（after docs + push） |
| Push commits + `architecture-baseline-v1` tag | **Authorized** |
| Continue Platform Construction | **Authorized** under Baseline |

---

## 修订记录

| 日期 | 说明 |
|------|------|
| 2026-07-20 | Completed：PASS WITH BACKLOG |
