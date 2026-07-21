# CAP-CTX-001 Promote Decision Review

> **Type**: Promote Decision Review（Research Governance）  
> **Date**: 2026-07-21  
> **Object**: CAP-CTX-001 — Context Capability Research  
> **Prerequisite**: Proposal v0.3 Review PASS · Experiment Spec v0.2 Confirmation PASS  
> **Path**: `docs/research/CAP_CTX_001_PROMOTE_DECISION.md`

### Promote 含义（强制）

```text
Promote ≠ Context Capability 已被证明存在
Promote ≠ Truth

Promote =
  Candidate Research Object
        ↓
  Controlled Research Object
  （获得正式 Experiment Identity，允许生成受治理的 Evidence）
```

---

## Decision Questions

### P1 — Research Object 是否足够明确？

| 是 | 不是 |
|----|------|
| **Context Capability**（描述能力是否存在） | Context Engine |
| RQ-CTX-001 / EQ-CTX-001 | Market State Model |
| Descriptive conditions | Trading Model / Alpha / Signal |

**Verdict P1: PASS**

研究对象边界与 Proposal / Spec Non-Goals 一致。

---

### P2 — Experiment Governance 是否完整？

已具备：

| 项 | 权威文档 |
|----|----------|
| Question | EQ-CTX-001（Spec §1） |
| Scope | Dataset + Freeze Point（Spec §3） |
| Boundary | Observation Space；反 Feature Catalog（Spec §4） |
| Evaluation | E1 / E2 / E3（Spec §5） |
| Null Baseline | N1 / N2 / N3 + 意义澄清（Spec §6） |
| Falsification | F1–F4 映射（Spec §7） |
| Evidence Contract | Artifact → Evaluation → Knowledge Candidate → Review（Spec §8） |

数值门槛与最终品种/区间名单属 **Run Spec**（Promote 后、观察生成前冻结）——不构成 Governance 缺口。

**Verdict P2: PASS**

---

### P3 — Promote 是否会导致研究漂移？

Promote **后仍禁止**（继承 Spec / Proposal）：

```text
❌ 策略化
❌ Alpha 化
❌ 分类器化
❌ 参数优化化 / Feature Catalog 选优
❌ 自动 Knowledge / 自动 Gate PASS
❌ 无 Run Spec 即 observation generation
```

若漂移发生 → 该次实验在本 CAP 下无效，须新 experiment_id / 新 Proposal。

**Verdict P3: PASS WITH CONDITIONS**（条件见下）

---

## Promote Decision

```text
================================================

CAP-CTX-001 PROMOTE DECISION REVIEW

Result:
PROMOTE WITH CONDITIONS

P1 Research Object Clarity: PASS
P2 Experiment Governance: PASS
P3 Drift Risk Control: PASS WITH CONDITIONS

Blocking Issues: None

================================================
```

### Conditions（绑定 Promote，若用户确认执行）

| ID | Condition |
|----|-----------|
| C1 | Promote 仅授予 Controlled Research Object 身份；**不**声称 Capability 已证实 |
| C2 | 任何 observation generation **之前**必须完成 Run Spec（含 Dataset Freeze + 预注册度量与数值门槛） |
| C3 | 执行阶段仍遵守 Spec Non-Goals（无 Engine / 分类器 / 回测 Alpha / Feature 选优） |
| C4 | Experiment Result → EvidenceRecord → Evaluation → Knowledge Candidate → **Review**；禁止自动 Knowledge |
| C5 | Gate 保持 BLOCKED 直至 Evidence + Review 后人工复评；RC001 不自动 Ready |

### Promote Decision Confirmation（执行记录）

```text
================================================
CAP-CTX-001 Promote Decision
Decision: CONFIRM PROMOTE ✓
Date: 2026-07-21
Promotion Type: Candidate → Controlled Research Object
Conditions: C1–C5 accepted
Scientific Claim: NOT established
Capability Existence: NOT proven
Gate Status: UNCHANGED (BLOCKED)
RC001 Status: UNCHANGED
================================================
```

### Current object status

```text
CAP-CTX-001: PROMOTED（Controlled Research Object）
Next: Run Spec — docs/research/CAP_CTX_001_RUN_SPEC.md（Draft）
```

---

## Epoch Snapshot（Promote 确认后）

```text
Epoch 2.0 — Evidence-driven Discovery

Architecture Baseline v1          ✓
Evidence Foundation               ✓
PRM v1.0                          ✓
Context Capability Proposal v0.3  ✓ Review PASS
Capability Experiment Spec v0.2   ✓ Confirmation PASS
CAP-CTX-001                       ✓ PROMOTED（Controlled Research Object）
Run Spec                          v0.2 Confirmation PASS ✓
Execution Authorization           NOT GRANTED（见 CAP_CTX_001_EXECUTION_AUTHORIZATION.md）
Context Capability Gate           BLOCKED
RC001                             Review Passed / Not Accepted
```

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 1.0 | Promote Decision Review：PROMOTE WITH CONDITIONS（C1–C5） |
| 2026-07-21 | 1.1 | CONFIRM PROMOTE 执行记录；链接 Run Spec Draft |
