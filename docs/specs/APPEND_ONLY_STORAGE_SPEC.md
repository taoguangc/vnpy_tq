# Append-only Storage Specification

> **Status**: Accepted  
> **Accepted date**: 2026-07-20  
> **Version**: 1.0.0  
> **Decision**: 018（Stable Contracts, Replaceable Infrastructure）；亦服从 017  
> **Path**: `docs/specs/APPEND_ONLY_STORAGE_SPEC.md`  
> **规则优先级**: `AGENTS.md` > Decision 018 > 本 Spec > Repository 实现  
> **实现门禁**: 本 Spec **只冻结存储行为合同**。不授权改 Python API 名、不规定 JSON/DuckDB/SQLite/Parquet。

**一句话**：持久化实现可替换；写入语义必须永远是 create-only / append-only。

**不是**：Repository 实现文档、数据库选型指南、Dashboard。

---

## 1. Purpose

本 Spec 回答：

- 研究资产如何进入存储？
- 读路径能否改写历史？
- 修正错误结论时如何处理？

本 Spec **不**回答：文件格式、SQL 方言、对象存储厂商、函数字面名。

适用对象：Evidence / Evaluation / Experiment Manifest / Artifact 元数据等 **Domain 权威记录** 的持久化边界。

---

## 2. Invariants

```text
Storage Contract

Invariant 1 — Record is immutable.
  已存储记录的字段不得原地修改。

Invariant 2 — Create-only.
  首次持久化成功后，同一主键不得再次写入。

Invariant 3 — Read never mutates.
  load / find / list / exists 不得产生副作用写入。

Invariant 4 — History is append-only.
  时间线上的记录只增不改；纠错靠新记录。

Invariant 5 — Replacement creates a new record with provenance.
  「替换」= 新 ID + 指向旧记录的 parent/provenance；不是 overwrite。
```

违反任一不变式即违反本 Contract，无论底层是 JSON 文件还是数据库。

---

## 3. Lifecycle（唯一合法）

```text
Create
    │
    ▼
Stored
    │
    ▼
Referenced（被 Evidence / Evaluation / Projection 引用）
```

**禁止**：

```text
Create → Update → Replace
Create → Overwrite
Stored → Delete（正式研究主路径）
```

软禁 / 废弃叙事通过 **新记录** 或 **Archived 状态文档** 表达，不通过物理删除权威字节（除非用户单独立项的灾难恢复程序，且须留审计）。

---

## 4. API Semantics（语义合同）

允许的**语义**（名称可映射，见下）：

| 语义 | 含义 |
|------|------|
| `record` | 创建并持久化一条新不可变记录；冲突则失败 |
| `load` | 按 ID 读取 |
| `find` | 按谓词查询 |
| `list` | 列举 |
| `exists` | 是否存在 |

禁止的**语义**：

| 语义 | 含义 |
|------|------|
| `update` | 原地改字段 |
| `replace` | 同 ID 换内容 |
| `overwrite` | 覆盖写 |
| `delete` | 删除权威记录（主路径） |

### 关于现有 `save_*` 命名

`save_evidence` / `save_manifest` 等若实现为 **create-only**（例如 `open("x")` 失败于已存在），则 **符合** 本 Contract。  
本 Spec **不要求**本轮改名为 `record_*`（REPO-001 保持 Backlog；倾向未来领域名 `record`）。

判断合规看语义，不看函数名。

---

## 5. Identity & Conflict

- 每条记录须有稳定 ID（如 `evidence_id` / `evaluation_id` / `experiment_id`）。
- 同 ID 第二次 `record` **必须失败**（显式错误），不得静默覆盖。
- 新结论 / 新评估 → 新 ID；可用 provenance 声明 `parent=<old_id>`。

---

## 6. Relation to Domain

| Domain 对象 | 存储角色 |
|-------------|----------|
| ExperimentManifest | 条件身份；create-once |
| ArtifactReference | 引用；产物字节另存且 hash 固定 |
| EvaluationResult | Assessment 快照；create-once |
| EvidenceRecord | 结论归档；create-once |

Projection（Portfolio 等）**不得**成为权威写入口；见 `PROJECTION_LAYER_SPEC.md`。

---

## 7. Forbidden Behaviors

- 原地改 Evidence / Evaluation / Manifest 字段  
- 同 ID overwrite  
- 读路径触发写回  
- 为 Dashboard「好看」改写历史记录  
- 把存储方言（SQL/ORM）泄漏进 Domain Spec  

---

## 8. Replaceability Checklist

未来若 Repository 从 JSON 文件迁到 DuckDB / SQLite / PostgreSQL / Object Storage，**必须同时满足**：

```text
✓ No Domain Change
✓ No Spec Change（本 Contract 与 Evidence Domain）
✓ No ADR Change（除非新 ADR 明确覆盖）
✓ Tests Continue Passing（契约测试语义不变）
```

任一不满足 → 迁移失败，不得宣称「仅换存储」。

---

## 9. Freeze Gate

- [x] 不含具体存储引擎选型  
- [x] 不含 Dashboard / UI  
- [x] 明确 create-only / append-only 不变式  
- [x] 允许 `save_*` 若语义合规  
- [x] Replaceability Checklist 可验收  

下一工程：Repository Refinement **对齐**本 Contract（测试与文档），不急着 rename API。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-20 | 1.0.0 | Accepted：Append-only Storage Contract |
