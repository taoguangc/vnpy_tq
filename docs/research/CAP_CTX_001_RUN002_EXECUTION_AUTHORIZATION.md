# CAP_CTX_001_RUN002 — Execution Authorization Review（Draft）

> **Type**: Execution Authorization Review（Cross Evidence Governance）  
> **Status**: **Draft** — awaiting Review / Confirmation  
> **Version**: 0.1  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CAP_CTX_001_RUN002_EXECUTION_AUTHORIZATION.md`  
> **Object**: CAP-CTX-001 / `CAP_CTX_001_RUN002`  
> **Parent Knowledge**: K001 (Qualified)  
> **Lineage**: `parent=CAP_CTX_001_RUN001`（Closed；不可改写）  
> **Prerequisite**: Spec v0.2 Review PASS · Fill v0.2 **Confirmation PASS**

### Authorization 含义

```text
Execution Authorization GRANTED
        ≠
K001 Strengthen
        ≠
Gate PASS / RC001 Accepted / Alpha

GRANTED =
  CP3 OPEN（Observation Generation Authorized under conditions）
  ≠ automatic Observation start

Observation start still requires:
  Run Manifest (C-ENV) → validation → explicit execution instruction
```

### 本文不是

```text
❌ Observation executed
❌ Evidence / Knowledge update
❌ Gate / RC001 变更
❌ 自动 GRANTED（须 Review Confirmation）
```

---

## Proposed Aggregate Decision（Draft）

```text
================================================

CAP_CTX_001_RUN002 EXECUTION AUTHORIZATION

Proposed Result:
GRANTED WITH CONDITIONS

Actual Authorization:
NOT GRANTED（awaiting Review Confirmation）

EA1 Dataset Fingerprint:     PASS（proposed）
EA2 Run Manifest:            PASS（proposed）
EA3 Pre-Registration lock:   PASS（proposed）
EA4 Environment:             PASS WITH CONDITION (C-ENV)
EA5 Scope non-expansion:     PASS（proposed）
EA6 Evidence path:           PASS（proposed）
EA7 Cross Evidence integrity: PASS（proposed）

Fill Confirmation: PASS ✓
CP3: CLOSED until Confirmation
Observation: NONE
Evidence: NONE
K001 / Gate / RC001: unchanged

================================================
```

---

## Checklist EA1–EA7

### EA1 — Dataset Fingerprint 实例冻结？

| 项 | 状态 |
|----|------|
| source / CbC / 无复权 / timezone / session | ✓ Fill §1 |
| Time Scope **2022-01-01…2023-12-31**（Temporal OOS） | ✓ Fill §3 |
| Warmup `2021-10-01`；不进入评价统计 | ✓ Fill §3 |
| SHA256：manifest / dominant_windows / rollover_map（rb, i, MA） | ✓ Fill §1.1 |
| Coverage 2022–2023 OK；Incomplete-coverage STOP | ✓ Fill §2 |

**Verdict EA1: PASS（proposed）**

---

### EA2 — Run Manifest 可生成？

| 项 | 状态 |
|----|------|
| Path | `research/output/evidence/CAP_CTX_001_RUN002/CAP_CTX_001_RUN_MANIFEST.json` |
| Role | RUN002 identity artifact（非结果文件） |
| 实例文件 | 允许在 Observation **开始前**写出 |
| `parent` | `CAP_CTX_001_RUN001` |
| `eq` | `EQ-CTX-002` |

**Verdict EA2: PASS（proposed）**

---

### EA3 — Pre-Registration 最终锁定？

| 项 | 状态 |
|----|------|
| `run_id` = `CAP_CTX_001_RUN002` | ✓ |
| Universe `rb`, `i`, `MA`（不变） | ✓ Frozen |
| Protocol = RUN001 inheritance；唯一覆盖 = temporal scope | ✓ |
| M1/M2 / partition / E1–E3 / N1–N2 | ✓ identical to RUN001 |
| Decision Mapping R2 | ✓ Frozen |
| Fill Confirmation PASS | ✓ |

**Verdict EA3: PASS（proposed）**

---

### EA4 — Environment Identity？

| 项 | 状态 |
|----|------|
| `code_revision` / `environment_identity` | ⚠ 允许 **GRANTED 后、首条 Observation 处理前** 写入 Manifest |

**Verdict EA4: PASS WITH CONDITION（C-ENV）**

---

### EA5 — Execution Scope 无漂移？

| 边界 | 状态 |
|------|------|
| Cross Evidence / Temporal OOS only | ✓ |
| Families = Volatility + Price only | ✓ |
| 无新品种 / 新 Family / 新阈值 / 改 Null | ✓ |
| 无 Feature Catalog / Engine / Classifier / Strategy / PnL | ✓ |
| 无自动 Gate / RC001 / unconditional Knowledge | ✓ |
| descriptive observations only | ✓ |

**Verdict EA5: PASS（proposed）**

---

### EA6 — Evidence 输出路径明确？

| 项 | 状态 |
|----|------|
| `research/output/evidence/CAP_CTX_001_RUN002/` | ✓ |
| Manifest → Evaluation → EvidenceRecord | ✓ |
| Cross note（另授） | `docs/research/CAP_CTX_001_RUN001_RUN002_CROSS_EVIDENCE.md` |
| 不改写 RUN001 Closed 产物 | ✓ |

**Verdict EA6: PASS（proposed）**

---

### EA7 — Cross Evidence Integrity？

| 项 | 状态 |
|----|------|
| Not a discovery experiment | ✓ Spec R1 / Fill |
| Protocol citation frozen | ✓ |
| Integrity Constraint frozen | ✓ |
| K001 mapping pre-registered（Supported/Partial/Not supported） | ✓ |
| `RUN002 PASS ≠ Gate PASS` | ✓ |

**Integrity Constraint（binding）**：

```text
RUN002 shall not introduce any post-RUN001
methodological modification intended to improve
the probability of supporting K001.
```

**Verdict EA7: PASS（proposed）**

---

## Proposed Conditions（若 Confirmation → GRANTED）

| ID | Condition |
|----|-----------|
| **C-ENV** | 处理任何 Observation bar **之前**，Run Manifest 必须写入 `code_revision` 与 `environment_identity` |
| **C-SCOPE** | 严格遵守 Fill v0.2 Appendix A；改任何冻结字段 → 新 `run_id`，本 Auth 作废 |
| **C-CLAIM** | 禁止宣称 Capability 已证实 / Regime / Alpha / Gate PASS；仅允许 Artifact → Evaluation → Cross Evidence → K001 Review |
| **C-GATE** | 不自动 PASS Context Capability Gate；不 ACCEPT RC001 |
| **C-NO-DRIFT** | 禁止 Feature 选优、换 M1/M2、改 Null、改 E 顺序、静默缩 universe、加品种 |
| **C-XEV** | Protocol inherited from RUN001 unless overridden by registered temporal scope；禁止为支持 K001 做方法学修改 |
| **C-K001** | 结果仅可触发预注册 K001 Action（Strengthen / Narrow / Downgrade / No upgrade）；须另授 Knowledge Review |

### What GRANTED would / would not

| 允许 | 禁止（仍） |
|------|------------|
| 打开 CP3 | 自动 Strengthen K001 |
| 按 Appendix A 生成 Observation | 扩大 Family / 改协议 |
| 写出 Manifest + Evaluation | 未满足 C-ENV 即开跑 |
| Cross Evidence vs RUN001 | 修改 Gate / RC001 / RUN001 artifacts |

---

## Controlled Observation Window（Confirmation 后）

```text
Run Manifest Generation
        ↓
C-ENV validation
        ↓
（explicit instruction）Observation Execution
        ↓
Evaluation → EvidenceRecord
        ↓
Cross Evidence note（另授）
        ↓
K001 Update Review（另授）
```

**显式指令模板**（尚未发出；Confirmation 后仍须单独发出）：

```text
Authorize Observation Execution for CAP_CTX_001_RUN002
```

---

## CP3 Status（Draft）

```text
CP3 = CLOSED（Authorization not Confirmed）

After Confirmation GRANTED WITH CONDITIONS:
  CP3 OPEN = Observation Generation authorized under C-ENV…C-K001
  ≠ Observation has been run
  ≠ K001 strengthened
  ≠ Gate PASS
```

---

## Epoch Snapshot（Draft Auth 时）

```text
K001                          Qualified（ACCEPT WITH QUALIFICATION）
RUN001                        Completed / Closed
RUN002 Spec                   ✓ Review PASS
RUN002 Fill                   ✓ Confirmation PASS
Pre-Registration              ✓ COMPLETE
Execution Authorization       Draft — NOT GRANTED
CP3                           CLOSED
Observation                   NONE
Evidence                      NONE
Context Capability Gate       BLOCKED
RC001                         unchanged
```

---

## Next

```text
Authorization Review
  → Confirmation（GRANTED WITH CONDITIONS / NOT GRANTED / REVISE）
  →（若 GRANTED）Manifest + C-ENV
  →（另授显式指令）Observation
```

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | Draft：EA1–EA7；proposed GRANTED WITH CONDITIONS；含 C-XEV / C-K001；Auth 未授予 |
