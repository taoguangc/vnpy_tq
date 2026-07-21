# CAP-CTX-001 Execution Authorization Review

> **Type**: Execution Authorization Review（Research Governance）  
> **Path**: `docs/research/CAP_CTX_001_EXECUTION_AUTHORIZATION.md`  
> **Object**: CAP-CTX-001 / `CAP_CTX_001_RUN001`  
> **Prerequisite**: Run Spec v0.2 Confirmation PASS · Fill Proposal v0.2 **Confirmation PASS**

### Authorization 含义

```text
Execution Authorization GRANTED
        ≠
Capability exists
        ≠
Knowledge / Gate PASS / RC001 Accepted

GRANTED =
  CP3 OPEN（Observation Generation Authorized under conditions）
  ≠ automatic Observation start

Observation start still requires:
  Run Manifest (C-ENV) → validation → explicit execution instruction
```

---

## Review #1 — Initial（2026-07-21）

```text
Result: NOT GRANTED
Reason: Precondition incomplete — instance freeze missing
EA1 FAIL | EA3 FAIL | EA2/EA5/EA6 PASS | EA4 CONDITIONAL
Blocking: B1–B4
CP3: CLOSED
```

历史详情保留在 git 历史；本文件以 **Re-review** 为当前权威。

---

## Review #2 — Re-review（2026-07-21）

**Trigger**: Fill Proposal v0.2 Confirmation PASS；O1–O5 CLOSED；Appendix A Frozen.

### Checklist EA1–EA6

### EA1 — Dataset Fingerprint 实例冻结？

| 项 | 状态 |
|----|------|
| source / CbC / 无复权 / timezone / session | ✓ Fill §1 |
| Time Scope 2024-01-01…2025-12-31 | ✓ |
| SHA256：manifest / dominant_windows / rollover_map（rb, i, MA） | ✓ Fill §1.2 |
| Incomplete-coverage STOP rule | ✓ Fill §2 |

**Verdict EA1: PASS**

---

### EA2 — Run Manifest 可生成？

| 项 | 状态 |
|----|------|
| 字段定义（Run Spec §9.1） | ✓ |
| 文件名 `CAP_CTX_001_RUN_MANIFEST.json` | ✓ |
| 实例文件 | 允许在 Observation **开始前**写出 |

**Verdict EA2: PASS**

---

### EA3 — Pre-Registration 最终锁定？

| 项 | 状态 |
|----|------|
| `run_id` = `CAP_CTX_001_RUN001` | ✓ |
| Universe `rb`, `i`, `MA` | ✓ Frozen |
| M1/M2 / partition / E1–E3 / N1–N2 公式与算法串 | ✓ Fill §4–§6 / Appendix A |
| Fill Confirmation PASS | ✓ |

**Verdict EA3: PASS**

---

### EA4 — Environment Identity？

| 项 | 状态 |
|----|------|
| 字段位 A.7 | ✓ |
| `code_revision` / `environment_identity` 实例 | ⚠ 允许 **GRANTED 后、首条 Observation 处理前** 写入 Manifest |

**Verdict EA4: PASS WITH CONDITION（C-ENV）**

---

### EA5 — Execution Scope 无漂移？

| 边界 | 状态 |
|------|------|
| Families = Volatility + Price only | ✓ |
| 无 Feature Catalog / 选优 / Engine / Classifier / Strategy / PnL | ✓ |
| 无自动 Gate / RC001 | ✓ |
| Frozen evaluation universe（非全市场） | ✓ |
| descriptive observations only | ✓ |

**Verdict EA5: PASS**

---

### EA6 — Evidence 输出路径明确？

| 项 | 状态 |
|----|------|
| `research/output/evidence/CAP_CTX_001_RUN001/` | ✓ |
| EvidenceRecord → Run Manifest → Dataset Fingerprint → Evaluation | ✓ |

**Verdict EA6: PASS**

---

## Aggregate Decision — Re-review

```text
================================================

CAP-CTX-001 EXECUTION AUTHORIZATION RE-REVIEW

Result:
GRANTED WITH CONDITIONS

EA1 Dataset Fingerprint:     PASS
EA2 Run Manifest:            PASS
EA3 Pre-Registration lock:   PASS
EA4 Environment:             PASS WITH CONDITION (C-ENV)
EA5 Scope non-expansion:     PASS
EA6 Evidence path:           PASS

Fill Confirmation: PASS ✓
Blocking B1–B4: CLEARED

CP3: OPEN
Observation Generation: AUTHORIZED（未执行）
Observation executed: NO
Evidence produced: NONE

Gate: UNCHANGED (BLOCKED)
RC001: UNCHANGED
Scientific claim: NONE

================================================
```

### Conditions（绑定 GRANTED）

| ID | Condition |
|----|-----------|
| **C-ENV** | 在处理任何 Observation bar **之前**，Run Manifest 必须写入 `code_revision` 与 `environment_identity` |
| **C-SCOPE** | 执行严格遵守 Fill v0.2 Appendix A；改任何冻结字段 → 新 `run_id`，本 Auth 作废 |
| **C-CLAIM** | 禁止宣称 Capability 已证实 / Regime / Alpha；仅允许产出 Artifact → Evaluation → Knowledge Candidate → Review |
| **C-GATE** | 不自动 PASS Context Capability Gate；不 ACCEPT RC001 |
| **C-NO-DRIFT** | 禁止 Feature 选优、换 M1/M2、改 Null、改 E 顺序、静默缩 universe |

### What GRANTED does / does not

| 允许 | 禁止（仍） |
|------|------------|
| 打开 CP3 | 自动解释为 Knowledge |
| 按 Appendix A 生成 Observation | 扩大 Observation Family |
| 写出 Run Manifest + Evaluation Artifact | 未满足 C-ENV 即开跑 |
| | 修改 Gate / RC001 |

---

## Confirmation — Authorization Status（2026-07-21）

```text
================================================
CAP_CTX_001_RUN001
Execution Authorization: GRANTED WITH CONDITIONS ✓
CP3: OPEN (Authorized)
Observation: NOT EXECUTED
Observation start: AWAITING Run Manifest + explicit execution instruction
Evidence: NONE
Gate / RC001: unchanged
================================================
```

Conditions **accepted**: C-ENV · C-SCOPE · C-CLAIM · C-GATE · C-NO-DRIFT

### Controlled Observation Execution Window

当前阶段：

```text
Run Manifest Generation
        ↓
C-ENV validation
        ↓
（explicit instruction）Observation Execution
        ↓
Evaluation → EvidenceRecord
```

**Run Manifest 不是结果文件**；是 `CAP_CTX_001_RUN001` **identity artifact**。

### Manifest status

| 项 | 状态 |
|----|------|
| Path | `research/output/evidence/CAP_CTX_001_RUN001/CAP_CTX_001_RUN_MANIFEST.json` |
| Role | run identity artifact |
| Manifest Confirmation | **CONFIRMED** ✓ |
| C-ENV | **SATISFIED** ✓ |
| Chain closed | Run Spec + Pre-Registration + Manifest |
| `observation_status` | `NOT_EXECUTED` |
| `observation_start_authorized` | `false` |
| `execution_state` | `WAITING_FOR_EXPLICIT_COMMAND` |

**显式指令模板**（尚未发出）：

```text
Authorize Observation Execution for CAP_CTX_001_RUN001
```

---

## CP3 Status

```text
CP3 = Observation Authorization Point — OPEN

Meaning:
  Observation Generation is authorized under C-ENV…C-NO-DRIFT.

Does NOT mean:
  Observation has been run
  Results exist
  Capability is proven
```

**下一动作（须另授实现方式）**：创建 Manifest（含 C-ENV）→ 按 Appendix A 执行 Observation → Evaluation → EvidenceRecord → Knowledge Candidate → Review。

---

## Epoch Snapshot（Re-review 后）

```text
Proposal v0.3                 ✓ Review PASS
Capability Experiment Spec    ✓ Confirmation PASS
CAP-CTX-001                   ✓ PROMOTED
Run Spec v0.2                 ✓ Confirmation PASS
Fill Proposal v0.2            ✓ Confirmation PASS
Pre-Registration              ✓ COMPLETE
Execution Authorization       GRANTED WITH CONDITIONS
CP3                           OPEN
Observation executed          NO
Evidence                      NONE
Context Capability Gate       BLOCKED
RC001                         Review Passed / Not Accepted
```

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 1.0 | Initial Review：NOT GRANTED；B1–B4 |
| 2026-07-21 | 2.0 | Re-review：GRANTED WITH CONDITIONS；CP3 OPEN；C-ENV…C-NO-DRIFT |
| 2026-07-21 | 2.1 | Authorization Confirmation；Manifest 路径；Observation start 仍待显式指令 |
| 2026-07-21 | 2.2 | Run Manifest Confirmation；C-ENV SATISFIED；WAITING_FOR_EXPLICIT_COMMAND |
| 2026-07-21 | 2.3 | Observation executed；see CAP_CTX_001_RUN001_EXECUTION_REPORT.md |
