# PAAF 路线图

> 版本：3.3.0 · 更新日期：2026-07-20  
> 路线图**可变**；宪章与规格冻结后，改路线图不等于改哲学。  
> **研究顺序以 Decision 017 为准**；基础设施契约以 Decision 018 为准。  
> **架构基线**：ABR-001；**Contract Freeze**：Storage + Projection Specs Accepted。

---

## 阶段总览

```text
Phase 0  Research Chaos（AFF）                 — 已结束
Phase 1  Architecture Foundation（v0.1）       — 已结束
Phase 2  Evidence Foundation                   — Completed（≠ v0.3 Completed）
Phase 3  Evidence Platform（v0.3）             — In Progress（Contract Freeze 已完成）
Phase 4  Validation Protocol（v0.4）           — 下一
Phase 5+ Market State → Opportunity → …      — 其后
```

大版本进入下一阶段前须通过 **ABR**。

---

## PAAF Phase 2 — Evidence Foundation

```text
✓ Detector Framework Frozen
✓ Evidence Domain Frozen
✓ Research Governance Frozen
Status: Completed
```

> **Completed ≠ v0.3 Completed。**

---

## PAAF v0.3 — Evidence Platform / Contract Freeze

```text
PAAF v0.3

✓ Evidence Domain Frozen
✓ ABR-001（Architecture Baseline v1）
✓ Storage Contract Frozen（APPEND_ONLY_STORAGE_SPEC）
✓ Projection Contract Frozen（PROJECTION_LAYER_SPEC）
✓ Decision 018（Stable Contracts, Replaceable Infrastructure）

□ Repository Append-only（实现对齐 Contract；不急 rename）
□ Portfolio Projection（只读实现）
□ ABR-002

Status:
In Progress
```

**Contract Freeze（本节点）**：语言 / 契约 / 治理三条线中，**基础设施契约**已齐。  
下一重心：利用契约构建能力（Repository refinement → Portfolio Projection → ABR-002），
而非继续改地基。

| Backlog | 说明 |
|---------|------|
| REPO-001 | `save_*` → 未来倾向 `record_*`；**不为命名改 API** |
| CLEANUP-001/002 | Legacy Adapter + Signal 表述 → **v0.3 Cleanup Sprint** |
| DOC-001 | Status 四态统一 → **本轮已处理主要项** |

**明确不做（v0.3）**：新 OPP / Market State / Alpha；Projection 回写 Domain；为 rename 大改 API。

---

## PAAF v0.4 — Validation Protocol

进入前：v0.3 Done Definition + **ABR-002**。

```text
Every Candidate Detector → Multi-Symbol → Roll-aware → Evidence Generated
```

---

## 已关闭研究快照

Closed 实验 Run Spec **Status = Archived**（DOC-001）。产物不可变。

| ADR / Spec | 状态 |
|------------|------|
| Decision 017 / 018 | **Accepted** |
| ABR-001 | **Completed** |
| EVIDENCE_DOMAIN / APPEND_ONLY_STORAGE / PROJECTION_LAYER | **Accepted** |

---

## Release

| 版本 | 含义 |
|------|------|
| v0.2.x | Detector Framework |
| **v0.3.x** | Evidence Platform + Contract Freeze（当前） |
| **v0.4.x** | Validation Protocol |
| v0.5+ | Market State → Opportunity → Decision → Execution |

---

## 明确不做

- 未经立项 OPP/Alpha；覆盖 Closed 实验；Projection 改 Domain  
- 无 Replaceability Checklist 的「换存储」宣称  

## 后续

| 项 | 状态 |
|----|------|
| Architecture Whitepaper v1.0 | 后置（ABR-002 后） |
| Cleanup Sprint | Signal + `_adapt_legacy` |

---

## 变更方式

哲学级变更走新 ADR；契约变更先改 Spec。
