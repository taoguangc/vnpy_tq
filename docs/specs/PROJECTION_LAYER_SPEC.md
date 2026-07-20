# Projection Layer Specification

> **Status**: Accepted  
> **Accepted date**: 2026-07-20  
> **Version**: 1.0.0  
> **Decision**: 018（Principle 4）；亦服从 017  
> **Path**: `docs/specs/PROJECTION_LAYER_SPEC.md`  
> **规则优先级**: `AGENTS.md` > Decision 018 > 本 Spec > 任何 Dashboard/UI 实现  
> **实现门禁**: 本 Spec **只冻结概念**。不授权实现 Portfolio/Timeline/Dashboard UI；不改 Domain。

**一句话**：Projection 是 Domain 的只读投影；Domain 才是权威。

---

## 1. Purpose

本 Spec 回答：

- 什么是 Projection？
- Portfolio / Timeline / Dashboard 属于哪一层？
- Projection 能否写回 Repository？

本 Spec **不**回答：图表样式、Web 框架、查询优化、具体 SQL。

---

## 2. Core Principle

> **Projection is Derived; Domain is Authoritative.**（Decision 018 Principle 4）

```text
Evidence Repository（及 Domain 记录）
        │
        ▼
Projection Builder（只读派生）
        │
        ▼
Projection（Portfolio / Timeline / Dashboard / …）
```

**Forbidden**：

```text
Projection
      │
      ▼
Modify Repository / Domain
```

---

## 3. Frozen Projections（v1）

本 Spec 冻结下列三类为 **Projection**（均可后实现）：

| Projection | 含义（概念） |
|------------|--------------|
| **Portfolio** | 按 DATA / FEATURE / PATTERN / DETECTOR / EXECUTION 等桶汇总研究资产状态 |
| **Timeline** | 按时间排列 Experiment / Evaluation / Evidence 事件 |
| **Dashboard** | 只读监视面板（状态计数、门槛提示等） |

未来同属 Projection、本 Spec 预留但不冻结细节：

```text
Knowledge Graph
Analytics
Statistics
```

它们 **不是** Domain，不得获得写权限。

---

## 4. What Projection May Do

- 读取 Manifest / Evaluation / Evidence / ArtifactReference  
- 聚合、过滤、计数、分组  
- 缓存派生视图（缓存失效不得改写源记录）  
- 展示 Classification / decision / Closed 状态  

## 5. What Projection Must Not Do

- `update` / `replace` / `overwrite` / `delete` 权威记录  
- 为「面板好看」改 Domain 字段或门槛  
- 把 Projection 状态写回当作新的权威真相  
- 引入交易下单语义  

存储行为仍服从 `APPEND_ONLY_STORAGE_SPEC.md`。

---

## 6. Relation to Research Portfolio（Decision 017）

Decision 017 的五个 Portfolio 桶：

```text
DATA | FEATURE | PATTERN | DETECTOR | EXECUTION
```

是 **Portfolio Projection** 的分类维度，不是第五个 Domain 对象。  
Negative / Inconclusive / Archived 证据必须可被投影统计，不得因「不好看」省略。

---

## 7. Lifecycle of a Projection Build

```text
1. Read Domain records（exists/load/list/find）
2. Derive view model（纯函数优先）
3. Publish Projection snapshot（可选；若持久化则自身亦 append-only 或可丢弃缓存）
```

若 Projection 快照被持久化：它是 **派生品**，重建应从 Domain 重算；冲突时以 Domain 为准。

---

## 8. Freeze Gate

- [x] 明确 Projection ≠ Domain  
- [x] 冻结 Portfolio / Timeline / Dashboard 三类  
- [x] Forbidden：Projection → Modify Repository  
- [x] 无 UI / 无实现绑定  

下一实现：Portfolio Projection（只读），须另授权；完成后进入 ABR-002 候选范围。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-20 | 1.0.0 | Accepted：Projection Layer 概念冻结 |
