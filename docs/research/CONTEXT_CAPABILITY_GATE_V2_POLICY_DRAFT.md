# Context Capability Gate v2 — Policy Preparation Draft

> **Type**: Gate Policy Preparation（≠ Gate Review · ≠ Gate PASS · ≠ RC001 Accepted）  
> **Status**: **Confirmation PASS** ✓ — Eligible for Gate v2 Review Preparation  
> **Version**: 0.2  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CONTEXT_CAPABILITY_GATE_V2_POLICY_DRAFT.md`  
> **Input**:  
> - [`CAPABILITY_PORTFOLIO_BAR_REVIEW.md`](CAPABILITY_PORTFOLIO_BAR_REVIEW.md) v0.3（BAR NOT MET；P4 PARTIAL）  
> - [`CAP_CTX_001_RUN005_CLOSURE_REVIEW.md`](CAP_CTX_001_RUN005_CLOSURE_REVIEW.md)（CLOSED · Partial）  
> - [`CONTEXT_CAPABILITY_GATE.md`](CONTEXT_CAPABILITY_GATE.md)（v1 BLOCKED）  
> - [`K001_KNOWLEDGE_REVIEW.md`](K001_KNOWLEDGE_REVIEW.md)（Strengthened Qualified + Independence Narrow）  
> **Epoch**: Phase **3.5** preparation  
> **Prior**: Draft v0.1 → PASS WITH REVISION → v0.2 → **Confirmation PASS**

### Confirmation（binding）

```text
================================================
CONTEXT_CAPABILITY_GATE_V2_POLICY_DRAFT v0.2

Confirmation: PASS ✓

G1–G4 / G5–G10 layering: PASS ✓
Capability Readiness ≠ K001 strength: PASS ✓
P4 PARTIAL = Conditional Block（PARTIAL ≠ FAILURE）: PASS ✓
Gate ≠ Alpha ≠ Trading ≠ Strategy Approval: PASS ✓
Capability Candidate conditions: PASS ✓

Policy Status: CONFIRMED
Eligible next: Gate v2 Review Preparation / Evidence Package Assembly

Gate Review: NOT STARTED
Capability Candidate: NOT DESIGNATED
RC001: UNCHANGED
K001: UNCHANGED
Trading: NOT STARTED
Gate operational status: BLOCKED
================================================
```

### Boundary

```text
Policy Confirmation PASS
        ≠
Gate Review
        ≠
Gate PASS
        ≠
RC001 Accepted
        ≠
Trading / Strategy / Alpha authorization
        ≠
Capability Candidate designation
```
---

## 1. Why Gate v2 preparation now

Epoch 3 Evidence 闭环已完成；问题已从「Context 是否存在？」转为：

> 一个经过 Evidence 验证的 Context Capability，需要满足什么条件，才允许进入策略研究域？

这一步必须**独立于 K001 强度叙事**。

---

## 2. Judgment object（R1 · binding）

```text
Gate v2 judges: Capability Readiness
Gate v2 does NOT judge: K001 strength / narrative reward
```

| 允许作为输入 | 禁止作为自动 PASS 理由 |
|--------------|------------------------|
| Portfolio Bar dimensions | K001 = Strengthened Qualified |
| Independence Narrow / Residual Bias | “知识很强所以开 Gate” |
| Engineering signal readiness | 单次 RUN SUPPORTED |
| Claim / Scope bindings | PnL / Alpha |

示例（当前事实）：

```text
K001 = Strengthened Qualified
P4 Independence = PARTIAL
→ Gate may remain BLOCKED
```

高强度 Knowledge **≠** 自动 Gate PASS。

---

## 3. Core policy question

**禁止问法**：

> Gate 是否可以因为 K001 Strengthened 而打开？

**正确问法**：

> Given Portfolio Bar gaps and qualifications（e.g. P4 PARTIAL · Independence Narrow · E1 NOT READY）, what minimum Gate v2 criteria must hold before Capability may serve subsequent research domains（including RC001 consideration）?

---

## 4. Gate v2 structure — layered（R2 · binding）

### 4.1 Base governance layer — G1–G4

| ID | Name | Question |
|----|------|----------|
| **G1** Ownership | Capability / Context 是否有明确 ownership 与变更纪律？ |
| **G2** Published State | 是否发布可观察、可引用的研究状态（非仅内部叙事）？ |
| **G3** Reproducibility | 协议 / 产物是否可复现、可审计？ |
| **G4** Evidence Traceability | Knowledge / Evidence / Run 是否可追溯且层分离？ |

### 4.2 Capability layer — G5–G10

| ID | Name | Question | Portfolio / Evidence link |
|----|------|----------|---------------------------|
| **G5** Evidence Sufficiency | 证据是否足以支撑“可服务后续研究”的 Capability 声明？ | P1–P3 material + scoped claim |
| **G6** Independence | 独立证据是否达 Gate 允许档？ | **P4**（见 §5） |
| **G7** Falsification Coverage | Null / 负面证据 / Stress 覆盖是否达最低要求？ | **P5** |
| **G8** Scope Stability | 范围 / qualification 是否稳定可强制？ | **P6** + Narrow addenda |
| **G9** Claim Boundary | Knowledge ≠ Capability ≠ Gate ≠ Alpha 是否可执行？ | Claim docs |
| **G10** Transition Safety | 进入策略研究域的过渡是否安全（无静默升格）？ | RC001 / strategy entry policy |

```text
G1–G4 = 基础治理（不得跳过）
G5–G10 = Capability 层
不得混合成单一“分数”
```

> 相对 v0.1：原 G5 Robustness / G6 Incremental Value / G7 Independence 等已重组进上表；Incremental Value 若需要，可作为 G5 子检查，**不以 PnL 定义**。

---

## 5. P4 PARTIAL → Gate mapping（R3 · binding）

**禁止**简单二元：

```text
❌ P4 PASS → Gate OK
❌ P4 FAIL → Gate Fail（仅此）
```

**采用**（冻结为政策草案映射）：

| P4 status | Gate v2 impact |
|-----------|----------------|
| **MET** | 可继续评估其余 G 项（非自动 Gate PASS） |
| **PARTIAL** | **条件阻塞（Conditional Block）** — 可保留 Partial Evidence 价值；须显式 Narrow / 使用边界；**不得**当作 P4 MET |
| **FAIL** / Execution-Invalid 未修复 | **Block** |

理由：RUN005 证明 Partial Evidence 有研究价值；若 Gate 不允许 Partial 存在，会反向鼓励隐藏负面结果。

```text
PARTIAL
  =
Conditional Block + mandatory qualification binding
  ≠
silent PASS
  ≠
“K001 false”
```

当前事实输入：P4 = **PARTIAL** → Gate v2 路径默认 **Conditional Block**，直至 Policy Confirmation / Gate Review 另裁。

---

## 6. Gate ≠ Alpha ≠ Trading（R4 · binding）

```text
Gate v2 ≠ Strategy Approval
Gate v2 ≠ Trading Authorization
Gate v2 ≠ Alpha Validation
```

Gate v2 **可以**回答：

> Context Capability 是否成熟到可以服务后续研究？

Gate v2 **不能**回答：

> 是否赚钱？

滑回 AFF / 收益优化即政策失败。

---

## 7. Capability Candidate designation（R5 · binding）

```text
Capability Candidate
  ≠
K001 Strengthened
  ≠
Gate PASS
  ≠
Portfolio Bar almost-MET
```

**最低条件草案**（须全部；Confirmation 可修订，不可削弱层分离）：

| # | Condition |
|---|-----------|
| 1 | 显式 Portfolio Bar Review：**BAR MET**（本政策不将 P4 PARTIAL 计为 MET） |
| 2 | G1–G4 基础治理：**PASS** |
| 3 | G5–G10 按 Confirmation 冻结的通过规则：**PASS**（含 P4 映射） |
| 4 | 显式 **Capability Candidate Designation Review** 授权 |
| 5 | Claim Boundary / Narrow qualifications 写入可强制使用边界 |

**当前**：条件未满足 → **NOT DESIGNATED**。

---

## 8. Hard exclusions

```text
❌ K001 Strengthened Qualified → auto Gate PASS
❌ P4 PARTIAL → Capability Candidate / silent Gate PASS
❌ RUN005 Partial → “K001 false” or forced PASS rewrite
❌ Gate PASS → RC001 Accepted automatic
❌ PnL / Alpha as Gate criterion
❌ 修改 Closed RUN001–005 以凑 Gate
❌ Gate v2 Policy Draft = Gate Review
```

---

## 9. Relation to RC001

```text
Gate v2 PASS（future）
        ≠
RC001 Accepted
        ≠
Opportunity / trading experiments authorized
```

RC001 仍保持既有状态，直至**另授**。

---

## 10. Recommended path（non-authorizing）

```text
Policy Draft v0.2
        ↓
Policy Confirmation Review
        ↓
（另授）Gate v2 Review
        ↓
Decide RC001 wait / proceed / early-close
        ≠
RUN006 by default
```

---

## 11. Checklist（v0.2）

| ID | Check | Verdict |
|----|-------|---------|
| GV1 | Judgment object = Capability Readiness ≠ K001 strength | **PASS** |
| GV2 | G1–G4 vs G5–G10 layered | **PASS** |
| GV3 | P4 MET/PARTIAL/FAIL → continue / conditional block / block | **PASS** |
| GV4 | Gate ≠ Alpha ≠ Trading ≠ Strategy Approval | **PASS** |
| GV5 | Capability Candidate designation conditions | **PASS** |
| GV6 | No Gate Review / RC001 / RUN006 / K001 edit authorized | **PASS** |

> Checklist PASS ≠ Policy Confirmation PASS。

---

## 12. Next

```text
Confirmation PASS ✓
        ↓
Gate v2 Review Preparation / Evidence Package Assembly
        ↓
（另授）Gate Review → PASS / CONDITIONAL / BLOCK
        ≠
auto Gate PASS / RC001 / Candidate / Trading
```

当前：**Confirmation COMPLETE**；Gate Review **NOT STARTED**；Gate **BLOCKED**；RC001 **UNCHANGED**。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | 首版：Phase 3.5 Gate v2 Policy Preparation；G5–G10 初稿；P4 options |
| 2026-07-21 | 0.2 | PASS WITH REVISION：Readiness≠K001；G1–G4/G5–G10；P4 PARTIAL conditional block；≠Alpha；Candidate 条件 |
| 2026-07-21 | 0.2.1 | **Confirmation PASS**；Eligible for Gate v2 Review Preparation |
