# CAP-CTX-001 Execution Authorization Review

> **Type**: Execution Authorization Review（Research Governance）  
> **Date**: 2026-07-21  
> **Object**: CAP-CTX-001 / Run Spec v0.2  
> **Prerequisite**: Run Spec **Confirmation PASS**  
> **Path**: `docs/research/CAP_CTX_001_EXECUTION_AUTHORIZATION.md`  
> **Scope**: 审查是否满足进入 **CP3 Observation Authorization** 的条件 — **不是**自动批准执行、**不是**生成 Observation

### Authorization 含义

```text
Execution Authorization Review
        ≠
「Capability 存在」
        ≠
自动 Observation
        ≠
Knowledge / Gate / RC001 变更

若 GRANTED:
  仅允许进入 CP3 → 受治理 Observation Generation
```

---

## Checklist（六项）

### EA1 — Dataset Fingerprint 是否实际存在并冻结？

| 项 | 状态 |
|----|------|
| Fingerprint **schema**（§2.3） | ✓ Accepted（Confirmation） |
| `data_source_id` / continuous / adjustment | ✓ 协议级约定存在 |
| `timestamp_convention` / `missing_data_rule` | ❌ **实例未填**（`_TBD_`） |
| `file_checksum_or_version` | ❌ **未采集** |
| Time Scope start/end / session | ❌ **`_TBD_`** |

**Verdict EA1: FAIL（incomplete freeze）**

结构通过 ≠ 实例冻结。CP3 前必须填死并可复现。

---

### EA2 — Run Manifest 是否可生成？

| 项 | 状态 |
|----|------|
| Manifest 字段定义 | ✓（Run Spec §9.1） |
| 建议文件名 | ✓ `CAP_CTX_001_RUN_MANIFEST.json` |
| 实际文件已写出 | ❌ 未生成（正确：Auth 前可不写） |
| 生成能力（模板完备） | ✓ **可生成**（待 Auth + 填值后） |

**Verdict EA2: PASS（capability）** — 模板就绪；实例文件非本审查前置写出。

---

### EA3 — Pre-Registration 是否锁定？

| 项 | 状态 |
|----|------|
| Appendix A **结构** | ✓ Accepted |
| Evaluation order E1→E2→E3 | ✓ 冻结 |
| Falsification mapping | ✓ 冻结 |
| Universe 名单 | ✓ 结构确认（rb/i/ma） |
| M1/M2 定义 + 窗长 | ❌ **`_TBD_`** |
| Partition rule / 数值门槛 / Null 重复次数 | ❌ **`_TBD_`** |
| `run_id` 最终冻结 | ❌ **`_TBD_`** |

**Verdict EA3: FAIL（values not locked）**

设计先于结果要求：**具体预注册值**锁定后才可 Auth。

---

### EA4 — Environment 是否记录？

| 项 | 状态 |
|----|------|
| Environment 字段位（A.7） | ✓ 已预留 |
| `code_revision` / `environment_identity` | ❌ 执行时补齐（可接受在 **Auth 授予后、Observation 开始前** 写入 Manifest） |

**Verdict EA4: CONDITIONAL PASS**

允许：Auth GRANTED 后、CP3 触发前写入环境身份。  
不允许：Observation 之后补写环境。

---

### EA5 — Execution Scope 是否不会扩大？

| 边界 | 状态 |
|------|------|
| Families 仅 Volatility + Price | ✓ |
| 无 Feature Catalog / 选优 | ✓ |
| 无 Engine / Classifier / Strategy / PnL | ✓ |
| 无 Gate/RC001 自动联动 | ✓ |
| Initial evaluation universe（非全市场） | ✓ |

**Verdict EA5: PASS**

---

### EA6 — Evidence Artifact 输出路径是否明确？

| 项 | 状态 |
|----|------|
| `research/output/evidence/<experiment_id>/` | ✓ |
| Run Manifest 文件名 | ✓ |
| EvidenceRecord → Manifest → Fingerprint → Evaluation | ✓ |

**Verdict EA6: PASS**

---

## Aggregate Decision

```text
================================================

CAP-CTX-001 EXECUTION AUTHORIZATION REVIEW

Result:
NOT GRANTED

Reason:
Precondition incomplete — instance freeze missing

EA1 Dataset Fingerprint instance:  FAIL
EA2 Run Manifest generable:        PASS
EA3 Pre-Registration values lock:  FAIL
EA4 Environment recording:         CONDITIONAL PASS
EA5 Scope non-expansion:           PASS
EA6 Evidence path clarity:         PASS

Observation: NOT AUTHORIZED
CP3: CLOSED

Gate: UNCHANGED (BLOCKED)
RC001: UNCHANGED
Scientific claim: NONE

================================================
```

### Blocking Preconditions（须全部清除后才能重新申请 Auth）

| ID | Required action |
|----|-----------------|
| B1 | 填死 Time Scope Fingerprint（start/end/timezone/session） |
| B2 | 填死 Dataset Fingerprint 实例（含 checksum/version） |
| B3 | 填死 Appendix A：`run_id`、M1/M2、partition、门槛、Null 重复次数 |
| B4 | 确认 Initial evaluation universe 最终名单（rb/i/ma 或审定替换） |

清除 B1–B4 后 → **重新提交** Execution Authorization Review（可简表复审）。  
**不**在 TBD 状态下授予 CP3。

---

## What This Review Is Not

```text
❌ 批准 Observation Generation
❌ 批准写 Detector / Feature Pipeline / 跑批
❌ 解释任何结果
❌ 产生 Knowledge
❌ 变更 Gate / RC001
```

---

## Recommended Next Step

```text
Pre-Registration Fill Proposal
  → docs/research/CAP_CTX_001_PRE_REGISTRATION_FILL_PROPOSAL.md
        ↓
Review → close O1–O5 → write Appendix A instances
        ↓
Re-submit Execution Authorization Review
        ↓
（若 GRANTED）CP3 Observation Authorization
```

**不要**在 TBD 状态下修改本文件为 GRANTED。

---

## Epoch Snapshot

```text
Proposal v0.3                 ✓ Review PASS
Capability Experiment Spec    ✓ Confirmation PASS
CAP-CTX-001                   ✓ PROMOTED
Run Spec v0.2                 ✓ Confirmation PASS
Execution Authorization       NOT GRANTED（precondition incomplete）
Observation                   NONE
Evidence                      NONE
Context Capability Gate       BLOCKED
RC001                         Review Passed / Not Accepted
```

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 1.0 | Execution Authorization Review：NOT GRANTED；B1–B4 blocking |
