# CAP_CTX_001_RUN005 — Independence Execution Authorization（v0.2）

> **Type**: Execution Authorization Review（Independence Evidence · Portfolio Bar **P4**）  
> **Status**: **GRANTED WITH CONDITIONS** ✓ — Confirmation **PASS** ✓ · Observation **COMPLETE** · Run **CLOSED** · Outcome **Partial**  
> **Version**: 0.2  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CAP_CTX_001_RUN005_EXECUTION_AUTHORIZATION.md`  
> **Object**: CAP-CTX-001 / `run_id=CAP_CTX_001_RUN005`  
> **EQ**: EQ-CTX-005  
> **Parent Knowledge**: K001 (**Strengthened Qualified**)  
> **Lineage**: Original chain RUN001–004 Closed（Access Level 约束）  
> **Prerequisite**: Spec v0.2 Confirmation PASS · Fill v0.2 **Confirmation PASS**  
> **Prior**: Draft v0.1 → Authorization Review GRANTED WITH CONDITIONS → v0.2（R1/R2）→ **Confirmation PASS**

### Authorization Confirmation（binding）

```text
================================================
CAP_CTX_001_RUN005_EXECUTION_AUTHORIZATION v0.2

Authorization Confirmation: PASS ✓

Authorization: GRANTED WITH CONDITIONS ✓
CP3: OPEN（Authorized）

C-IER:        PASS ✓（Create→Seal→Hash before artifact access）
C-ART:        PASS ✓
C-ORDER:      PASS ✓
C-BIAS:       PASS ✓
C-INTEGRITY:  PASS ✓（Execution Invalid ≠ Independence FAIL ≠ K001 Downgrade）

Manifest: NOT CREATED
Observation: NOT EXECUTED · NOT STARTED
Evidence: NONE
Knowledge update: NOT AUTHORIZED

Required before Observation:
  1. Create Run Manifest
  2. Complete C-ENV identity
  3. Explicit Observation authorization instruction

K001: UNCHANGED
Gate: BLOCKED
RC001: UNCHANGED
Capability Candidate: NO
================================================
```

### Authorization 含义

```text
GRANTED WITH CONDITIONS + Confirmation PASS
  =
CP3 OPEN（execution window authorized）
  ≠ automatic Observation
  ≠ Manifest created
  ≠ Capability Candidate / Gate PASS
  ≠ K001 auto-update
  ≠ “维护 / 证明 K001”

Observation / Phase C→B still requires:
  Run Manifest + C-ENV
  → IER Freeze（Artifact Access = NONE）
  → explicit execution instruction
```

### Success criterion（binding）

```text
RUN005 success ≠ Independence PASS

Weakening / challenging K001 packaging
  = valuable Negative / Partial Evidence

True failure =
  modifying the experiment to protect prior conclusions
```

### Research Objective Integrity（EA1 · binding）

RUN005 **不是**：

```text
❌ 证明 K001
❌ 维护 K001
❌ 寻找支持证据
```

RUN005 **是**：

> Evaluate whether K001 remains supported under a controlled independent evidence generation process.

价值在于 **P4 判别能力**（可挑战既有包装），不在于追求 PASS。

### Claim Boundary（binding）

```text
Independence Outcome PASS/Partial/FAIL
        ≠
Capability Candidate
        ≠
Gate PASS
```

```text
Independence FAIL ≠ K001 false
Execution Invalid ≠ Independence FAIL ≠ K001 Downgrade
```

正确 PASS 表述上限：

> Independence support increased under registered residual bias conditions.

**禁止**：宣称“完全独立”。

---

## Aggregate Decision（Authorization Review）

```text
================================================
CAP_CTX_001_RUN005 EXECUTION AUTHORIZATION

Decision: GRANTED WITH CONDITIONS ✓

EA1 Research Objective Integrity:    PASS
EA2 C→B Protocol Freeze:             PASS
EA3 IER Control:                     PASS WITH CONDITION（C-IER）
EA4 Artifact Access Control:         PASS WITH CONDITION（C-ART）
EA5 Order Constraint:                PASS（C-ORDER）
EA6 Bias Disclosure:                 PASS（C-BIAS）
EA7 Evidence path / Manifest:        PASS
EA8 Scope / Non-drift:               PASS

Conditions:
  C-ENV · C-IER · C-ART · C-ORDER · C-SCOPE
  · C-CLAIM · C-GATE · C-NO-DRIFT · C-K001 · C-BIAS · C-XEV
  · C-INTEGRITY（R1）

CP3: OPEN（Authorized · Confirmation PASS）
Observation: NOT EXECUTED
Manifest: NOT CREATED
================================================
```

---

## Checklist（Authorization Review）

### EA1 — Research Objective Integrity — PASS

目标保持 EQ-CTX-005；禁止为维护 K001 设计流程（C-XEV）。

### EA2 — C→B Protocol Freeze — PASS

```text
C Independent Specification
        ↓
B Independent Evaluation
```

禁止：Result observed → Change specification。

### EA3 — IER Control — PASS WITH CONDITION（C-IER）

**必须**在 `Artifact Access = NONE` 下完成 IER：

```text
Create IER
        ↓
Seal IER
        ↓
Record hash/version（IER-CTX-005 v1.0）
        ↓
Open permitted artifacts
```

**禁止**：Look artifact → Write IER。

### EA4 — Artifact Access Control — PASS WITH CONDITION（C-ART）

| Artifact | Permission |
|----------|------------|
| Original interpretation | **sealed**（Phase B 至多 cite-sparingly） |
| Evidence artifacts | **read-only**（仅 IER sealed 后） |
| Knowledge decision | **unavailable** until after IER scoring draft |
| Raw source | **governed / restricted** |

Original narrative 不得成为 independent evaluator 的隐性先验。

### EA5 — Order Constraint — PASS（C-ORDER）

```text
IER Freeze
        ↓
Artifact Access
        ↓
Evaluation / Scoring
        ↓
Interpretation
```

### EA6 — Bias Disclosure — PASS（C-BIAS）

Residual Bias Matrix 必须披露；即使 Independence PASS 也不得声称完全独立。

### EA7 — Evidence path / Manifest — PASS

Path：`research/output/evidence/CAP_CTX_001_RUN005/`  
Manifest → IER Freeze record → Scoring → EvidenceRecord → Report  
不改写 Closed RUN001–004。

### EA8 — Scope / Non-drift — PASS

仅 Independence Mode；≠ Universe/Time/Family/参数扩展；≠ Mode A/D；≠ B→C。

---

## Conditions（binding on Grant）

| ID | Condition |
|----|-----------|
| **C-ENV** | Manifest 含 `code_revision` + `environment_identity`，先于 Phase C |
| **C-IER** | IER 在 **Artifact Access = NONE** 下 Create→Seal→Record hash/version；再开放 artifact |
| **C-ART** | Access Level 表；Original interpretation sealed；Knowledge decision delayed |
| **C-ORDER** | C→B 与 IER→Access→Eval→Interpretation；禁止颠倒 |
| **C-SCOPE** | 仅 Independence Mode；改 Mode/IER/Access → 新 `run_id`，本 Auth 作废 |
| **C-CLAIM** | 禁止 Capability Candidate / Gate PASS / “K001 为假” / “完全独立” / Alpha |
| **C-GATE** | 不自动 PASS Gate；不 ACCEPT RC001 |
| **C-NO-DRIFT** | 禁止为 PASS 改 IER、换 Mode、用 sealed 叙事重写判据 |
| **C-K001** | Registered Actions only；Knowledge Decision 另授 |
| **C-BIAS** | Residual Bias Matrix + runtime notes 必披露 |
| **C-XEV** | No modification for the purpose of increasing support for existing knowledge |
| **C-INTEGRITY** | 见 § Failure Type Separation（R1） |

### What Grant allows / forbids

| 允许（Confirmation 后） | 禁止（仍） |
|-------------------------|------------|
| CP3 OPEN；Manifest + IER Freeze | 无显式指令即 Observation |
| Phase B read-only scoring | 改写 Closed artifacts |
| 写出 RUN005 Evidence 产物 | Gate / RC001 / Capability Candidate |
| 触发 Registered Action 映射 | 将 Execution Invalid 记为 Independence FAIL |

---

## Failure Type Separation（R1 / R2 · binding）

### R1 — Execution Integrity Failure Trigger

若发生任一：

- IER protocol deviation（未 Freeze / artifact 已打开后写 IER / 事后改 IER）  
- Artifact leakage（违反 Access Level；过早打开 Original interpretation / Knowledge decision）  
- Order violation（B→C 或 Access→IER）  

则：

```text
RUN005 execution INVALID
```

**不是**：

```text
RUN005 Independence FAIL
```

治理失败 ≠ Knowledge 失败。Invalid → 停止计分；须新 `run_id` 或修复后重开 Auth；**不**映射 NARROW/DOWNGRADE。

### R2 — Three-way separation

| 类型 | 含义 | 进入 Knowledge Action？ |
|------|------|-------------------------|
| **Execution Invalid** | 实验链污染 / 协议破坏 | **No** — 无 Independence Outcome |
| **Independence FAIL** | 独立证据不足（IER 合法完成后的 Outcome） | Yes — NARROW 或 DOWNGRADE（另授 Review） |
| **K001 Downgrade** | 知识层决定 | Yes — 仅另授 Knowledge Review 可作出 |

```text
Execution Invalid
        ≠
Independence FAIL
        ≠
K001 Downgrade
```

---

## Controlled execution window（Confirmation PASS · not started）

```text
Authorization Confirmation PASS ✓
        ↓
Run Manifest + C-ENV          ← NEXT（not done）
        ↓
Phase C: Create → Seal → Record IER（Access = NONE）
        ↓
（explicit）Authorize Independence Observation / Scoring for CAP_CTX_001_RUN005
        ↓
Phase B: Access Level → Scoring → Interpretation
        ↓
EvidenceRecord → Report（含 Bias Matrix；若 Invalid 则标 INVALID）
        ↓
Evidence Review
        ↓
K001 Independence Review（另授）
        ↓
Portfolio Bar update（另授）
```

**关键观察点**：独立路径是否**挑战**既有 K001 包装（非追求 PASS）。

---

## Manifest status

| 项 | 状态 |
|----|------|
| Path | `research/output/evidence/CAP_CTX_001_RUN005/CAP_CTX_001_RUN_MANIFEST.json` |
| Status | **CONFIRMED** · IER **FROZEN** · identity + freeze recorded |
| C-ENV | **SATISFIED** |
| IER Freeze | **SEALED** · [`CAP_CTX_001_RUN005_IER_FREEZE.md`](CAP_CTX_001_RUN005_IER_FREEZE.md) |
| Observation | **NOT EXECUTED** · **NOT AUTHORIZED** |

---

## Next

```text
Authorization Confirmation PASS ✓
IER SEALED ✓
        ↓
Explicit Observation Authorization
        ≠
auto Observation / Evidence / Knowledge update
```

当前：**Confirmation COMPLETE**；CP3 **OPEN**；Manifest **CONFIRMED**；IER **SEALED**；Observation **NOT AUTHORIZED**。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | Draft：EA1–EA8；proposed GRANTED WITH CONDITIONS；NOT GRANTED |
| 2026-07-21 | 0.2 | Review GRANTED WITH CONDITIONS；C-IER Access=NONE；R1/R2；Confirmation PENDING |
| 2026-07-21 | 0.2.1 | **Authorization Confirmation PASS**；CP3 OPEN；Manifest/Observation still none |
| 2026-07-21 | 0.2.2 | Manifest + C-ENV Draft written；IER Freeze still PENDING；Observation NONE |
| 2026-07-21 | 0.2.3 | IER Freeze Ceremony COMPLETE；Obs still NOT AUTHORIZED |
