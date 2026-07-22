# CAP-CTX-001 — Phase 3.3 Observation Expansion Proposal

> **Type**: Proposal Review Document（非 RUN004 执行授权）  
> **Status**: **Confirmation PASS** ✓ — Eligible for Observation Family Expansion Spec  
> **Version**: 0.2  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CAP_CTX_001_PHASE33_OBSERVATION_EXPANSION_PROPOSAL.md`  
> **Input**: [`CAPABILITY_PORTFOLIO_BAR_REVIEW.md`](CAPABILITY_PORTFOLIO_BAR_REVIEW.md)（BAR NOT MET）  
> **Goal**: 补齐 Portfolio Bar **P3**（Observation Family）缺口；不触发 Gate / RC001 / Alpha  
> **Prior**: Draft v0.1 → Review **PASS WITH REVISION** → v0.2 → **Confirmation PASS**（2026-07-21）

### Confirmation（binding）

```text
================================================
CAP_CTX_001_PHASE33_OBSERVATION_EXPANSION_PROPOSAL

Confirmation: PASS ✓

Review chain:
  v0.1 Draft → PASS WITH REVISION → v0.2 → Confirmation PASS

Proposal Status:
  CONFIRMED — Eligible for Observation Family Expansion Spec

P3A1–P3A6: PASS ✓
Family selection: NOT FROZEN（Spec 阶段按 §5 治理表填写）
RUN004: NOT AUTHORIZED
Observation: NONE
K001: Strengthened Qualified（unchanged）
Gate: BLOCKED
RC001: UNCHANGED
================================================
```

### Proposal Boundary

```text
Confirmation PASS =
  governance for Phase 3.3 Observation Family Expansion is locked
  ≠ RUN004 Auth / Observation / Family pick frozen

This document does NOT authorize:
  RUN004 execution
  concrete Family selection / implementation（须 Spec + §5 table）
  Gate v2 review
  Capability Candidate designation
  K001 / RC001 change
```

---

## 1. Why Phase 3.3 now（P3A1 — PASS）

Portfolio Bar 结论：

```text
P1 Temporal          MET
P2 Cross-sectional   MET
P3 Observation Family NOT MET  ← Phase 3.3 hard gap
P4 Independence      NOT MET  ← separate track（§6）
```

Phase 3.3 目标不是「寻找更好的 Context」，而是：

> 检验 Context 描述能力是否依赖当前 Observation Family。

不增加同族证据数量；补 Capability 证据维度。

---

## 2. Core Research Question

**禁止问法**：

> 新 Observation 是否也“有效”？

**正确问法**：

> 在保持 RUN001–RUN003 注册框架不变的前提下，K001 的描述结构是否依赖当前 Observation Family（Volatility + Price），还是可在新增 Observation Family 下保持？

---

## 3. Single-variable constraint（P3A2 — PASS）

```text
Single Variable = Observation Family only
```

### Frozen

| Item | Freeze |
|------|--------|
| Universe | `{rb, i, MA, TA}` |
| Time protocol | 已注册窗口与 warmup |
| Evaluation | E1 → E2 → E3 |
| Null | N1/N2（seed / n_perm / block_size） |
| Governance | Spec → Fill → Auth → Manifest → Observation → Review |

### Change（only one）

- Observation Family（须经 §5 Candidate Governance 选定后写入 Spec）

---

## 4. Observation Family Boundary（P3A3 — Revision）

### Binding Boundary Statement

> **Observation Family** represents a **conceptual measurement domain**, not an individual feature set or optimized feature combination.

| 是 Observation Family | 不是（Feature / Drift） |
|----------------------|-------------------------|
| Volatility Structure | ATR20、realized vol 窗口调参 |
| Price Structure | EMA20、slope、directional efficiency 单点优化 |
| Liquidity Structure（候选概念） | Volume ratio、OI 差分的特征堆叠 |
| Market Geometry（候选概念） | 任意几何“指标配方” |

```text
Observation Family
        ≠
Feature
        ≠
Feature Catalog expansion
        ≠
“加几个指标看看有没有效果”
```

**禁止**：用 Feature Engineering / Feature Ranking / Model Selection 冒充 Family Expansion。

---

## 5. Observation Family Candidate Governance（P3A4 — Revision）

**不急于选定** Liquidity / Geometry 等具体 Family。先固化选择规则，再进入 Spec。

### 5.1 Selection Criteria（must answer before Spec）

| # | Question |
|---|----------|
| 1 | 该 Family 是否提供**独立市场描述维度**（相对 Volatility + Price）？ |
| 2 | 为什么它能测试当前 Capability **边界**（而非重复 P1/P2 结论）？ |
| 3 | 为什么这是 Family 扩展，**不是** Feature 扩展？ |

### 5.2 Forbidden selection bases

```text
❌ 预期效果 / 历史表现
❌ 与 K001 相似程度（结果导向）
❌ 便于通过 Null / 易于 PASS
```

### 5.3 Candidate Family Governance Table（Spec 前必填）

| 项 | 目的 |
|----|------|
| **Candidate Family** | 研究对象（概念域名） |
| **Conceptual Motivation** | 为什么选择该描述域 |
| **Independence Argument** | 与现有 Family（Vol/Price）的概念区别 |
| **Exclusion Criteria** | 为什么不是 Feature / Feature 组合 |
| **Failure Interpretation** | 若失败：说明依赖当前 Family / Narrow / Downgrade |

未填完上表 → **不得**进入 RUN004 Spec Confirmation。

### 5.4 Illustrative names only（non-binding）

以下名称仅作讨论占位，**不是**已选 Family：

- Liquidity Structure  
- Market Geometry  

选定须经 §5.1–§5.3 + Proposal Confirmation 后另文冻结。

---

## 6. P3 ≠ P4（P3A5 — Revision）

```text
Phase 3.3 addresses P3 only.
P4 requires separate governance review.
```

| Dimension | Phase 3.3 能提供 | 不能自动声称 |
|-----------|------------------|--------------|
| **P3** | Observation Robustness Evidence（跨 Family） | — |
| **P4** Independence | 最多弱提示 | Independent Evidence / Gate G7 满足 |

```text
不同 Observation Family
        ≠
Independent Evidence
```

共享 dataset lineage、evaluation framework、research pipeline 时，跨 Family **不**等于 Independence。

---

## 7. Non-goals（P3A6 — PASS）

```text
❌ Alpha / Signal / Trading
❌ Feature ranking / Model selection
❌ Gate PASS / Capability Candidate
❌ 为提高支持概率而选 Family
```

---

## 8. Proposal acceptance checklist（v0.2）

| ID | Check | Verdict |
|----|-------|---------|
| P3A1 | Research motivation = P3 gap | **PASS** |
| P3A2 | Single variable = Family only | **PASS** |
| P3A3 | Family ≠ Feature boundary | **PASS**（§4） |
| P3A4 | Selection governance + criteria | **PASS**（§5） |
| P3A5 | P3 ≠ P4 clarified | **PASS**（§6） |
| P3A6 | Non-goals / no Alpha drift | **PASS** |

---

## 9. Deliverables（Confirmation PASS → Spec）

```text
Proposal Confirmation PASS ✓
        ↓
Observation Family Expansion Spec（RUN004 Spec Draft）
        ↓
Fill → Auth（各另授）
        ↓
（另授）Observation
```

仍不执行 Observation，直至显式 Auth + Observation 指令。

---

## 10. Next

```text
Proposal Confirmation PASS ✓
        ↓
RUN004 Spec Draft v0.1 — [`CAP_CTX_001_RUN004_RUN_SPEC.md`](CAP_CTX_001_RUN004_RUN_SPEC.md)
        ↓
Spec Review → Fill（§5 Family）→ Confirmation → Auth（另授）
```

当前：**Confirmation COMPLETE**；Spec Draft 已开；**不**选定具体 Family；**不**授权 RUN004 Observation。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | 首版：Phase 3.3 Proposal；聚焦 P3 |
| 2026-07-21 | 0.2 | Review PASS WITH REVISION：Family boundary；Candidate Governance；P3≠P4；勿急选具体 Family |
| 2026-07-21 | 0.2.1 | **Confirmation PASS**；Eligible for Family Expansion Spec |
| 2026-07-21 | 0.2.2 | Pointer：RUN004 Spec Draft v0.1 opened |
