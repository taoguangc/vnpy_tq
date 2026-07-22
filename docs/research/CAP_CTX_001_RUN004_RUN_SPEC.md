# CAP_CTX_001_RUN004 — Observation Family Expansion Run Specification（v0.2）

> **Type**: Cross Evidence Run Specification（Observation Expansion）  
> **Status**: **Confirmation PASS** ✓ — Eligible for Pre-registration Fill  
> **Version**: 0.2  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CAP_CTX_001_RUN004_RUN_SPEC.md`  
> **Campaign**: CAP-CTX-001（PROMOTED）  
> **Parent Knowledge**: K001 (**Strengthened Qualified**) — [`K001_KNOWLEDGE_REVIEW.md`](K001_KNOWLEDGE_REVIEW.md)  
> **Parent Proposal**: [`CAP_CTX_001_PHASE33_OBSERVATION_EXPANSION_PROPOSAL.md`](CAP_CTX_001_PHASE33_OBSERVATION_EXPANSION_PROPOSAL.md) — **Confirmation PASS**  
> **Governance**: [`CROSS_EVIDENCE_GOVERNANCE.md`](CROSS_EVIDENCE_GOVERNANCE.md) v1.2 Baseline  
> **Lineage**: `parent=CAP_CTX_001_RUN003`（Closed；不可改写）  
> **Evidence Type**: **Observation Expansion**（G-CX-001 / A.2）  
> **Purpose**: Observation Family robustness evidence for Portfolio Bar **P3** — **not** Gate · **not** RC001 · **not** Alpha · **not** P4

### Spec Confirmation（2026-07-21）

```text
================================================
CAP_CTX_001_RUN004_RUN_SPEC v0.2

Confirmation: PASS ✓

Review chain:
  v0.1 Draft → PASS WITH REVISION → v0.2 → Confirmation PASS

Eligible for: Pre-registration Fill Draft

Family: NOT FROZEN（Fill §5）
Fill / Auth / Observation: NOT STARTED / NONE / NONE
K001 / Gate / RC001: unchanged
================================================
```

### Spec Review（historical）

```text
v0.1 Review: PASS WITH REVISION ✓
R1–R3 / R5: PASS
R4 / R6: addressed in v0.2
```

### Claim Boundary（binding）

> RUN004 may provide **Observation Family robustness evidence**; it does **not** establish Capability Candidate status.

```text
RUN004 SUPPORTED
        ≠
Capability Candidate
        ≠
Gate PASS
        ≠
P4 Independence MET
        ≠
“寻找另一个有效变量”
```

### Single-variable declaration（binding）

```text
RUN004 changes Observation Family only.

Universe {rb, i, MA, TA} and time window 2024–2025
are registered execution conditions inherited from
RUN001/RUN003 protocol — not experimental variables of RUN004.
```

### Boundary

```text
✅ Spec Confirmation PASS ✓
❌ Fill / Auth / Observation
❌ Concrete Family frozen（须 Fill §5）
❌ Feature Engineering / Ranking / Selection / Tuning
❌ Alpha / Trading / Model comparison
```

```text
Capability Question
        ↓
Observation Domain Robustness（P3）
```

---

## Review Response（v0.1 → v0.2）

| ID | Item | Revision |
|----|------|----------|
| R1 | EQ wording | §1：remain supported / 注册条件下支持（非“成立”） |
| R4 | Family Governance Table | §5：扩展字段（domain / P3 suitability / exclusion / failure） |
| R6 | Non-goals + Claim Boundary | §0 Claim Boundary · §10 Non-goals 强化 |

---

## 1. Research Question（R1）

### EQ-CTX-004

```text
Under the same registered universe, time, evaluation order, and null protocol
as CAP_CTX_001_RUN001 (with universe scope as closed in RUN003),

under a registered additional Observation Family,
does the descriptive condition structure remain supported?
```

中文：

> 在 Universe / 时间 / Evaluation / Null 冻结不变的前提下，在**新增一个注册 Observation Family** 后，descriptive condition structure 是否在**注册条件下仍获得支持**？

**禁止过强措辞**：不说「Capability 成立 / 已证实」。

### 1.1 What this answers / does not

| Answers（P3） | Does not answer |
|---------------|-----------------|
| Observation Family robustness | Independence（**P4** — 另授） |
| Whether K001 depends only on Vol+Price domain | Gate / Capability Candidate |
| Narrow/Downgrade if expanded Family unsupported | Alpha / trading value |

```text
Phase 3.3 / RUN004 addresses P3 only.
P4 requires separate governance review.
Different Family ≠ Independent Evidence.
```

---

## 2. Protocol Inheritance（R2）

> Protocol inherited from CAP_CTX_001_RUN001 unless explicitly overridden by registered Observation Family scope.

| Item | Value |
|------|--------|
| Universe | **Frozen** `{rb, i, MA, TA}` |
| Time Full | **Execution condition** `2024-01-01` … `2025-12-31` |
| Warmup | `2023-10-01`（excluded from stats） |
| Baseline Families | Volatility Structure + Price Structure |
| **Override** | **+1 registered Observation Family**（Fill 冻结） |
| Partition | `causal_rolling_median_threshold`, L=240 |
| Eval order | E1 → E2 → E3 |
| Null N1 / N2 | seed **20240721**；n_perm 200；block 60 |
| Data | TQ offline / 1m / CbC / 无复权 |

### Integrity Constraint（C-XEV）

```text
No methodological modification shall be introduced
for the purpose of increasing support for existing knowledge.
```

### Carried methodological limitation

```text
E1 = supporting only when labels couple to partition metric
Interpretation weight: E2 + E3 + secondary metrics ≥ isolated E1
```

---

## 3. Observation Family Boundary

> Observation Family = conceptual measurement domain, **not** a feature set or optimized feature combination.

| Allowed | Forbidden |
|---------|-----------|
| Register one new **Family** domain | ATR/EMA/volume-ratio shopping |
| Define registered observation(s) inside that Family | Feature Catalog as “Family” |
| Keep Evaluation/Null frozen | Change Null / E order to fit signals |

```text
Observation Family ≠ Feature ≠ “加几个指标看看有没有效果”
```

---

## 4. Candidate Family — NOT FROZEN（R3）

本 Spec **不选定** Liquidity / Geometry / Order Flow / Volume 等具体 Family。

提前指定会产生 Selection Bias（选预期更易通过的 Family）→ **禁止**。

---

## 5. Family Governance Table（R4 — required before Confirmation）

Fill 必须完整填写下表；**不仅** Family name。

| 字段 | 目的 |
|------|------|
| **Family** | 观察域名称 |
| **Conceptual domain** | 描述什么市场属性 |
| **Difference from existing family** | 相对 Vol/Price 的概念独立性 |
| **Why suitable for P3** | 为何补 Capability Portfolio Bar P3 缺口 |
| **Exclusion** | 为何不是 Feature / Feature Engineering |
| **Failure interpretation** | 失败意味着什么（Narrow / Downgrade / No upgrade） |

### Selection criteria（must answer）

1. 是否提供独立市场描述维度（相对 Volatility + Price）？  
2. 为何能测试 Capability **边界**（而非重复 P1/P2）？  
3. 为何是 Family 扩展而非 Feature 扩展？

### Forbidden selection bases

```text
❌ 预期效果 / 历史表现
❌ 与 K001 相似程度
❌ 便于通过 Null / 易于 PASS
```

```text
RUN004 value
  =
test whether K001 depends on existing observation domains
  ≠
find a Family that passes
```

**未填完上表 → 不得 Spec Confirmation → 不得进入 Fill Confirmation。**

---

## 6. Evaluation Scope（frozen skeleton；Family 映射在 Fill）

| Check | Role | Freeze |
|-------|------|--------|
| E1 | Separability supporting | 协议同 RUN001；新 Family 观测接口由 Fill 注册，**不得**改 Null |
| E2 | Persistence（primary `rb`） | mean_run_length vs N2；min_runs 100 |
| E3 | Transfer on `{i, MA, TA}` | E1 Pass on each transfer under expanded Family set |

Primary：`rb`。Transfer：`i`, `MA`, `TA`。

Fill 须注册：新 Family 下至少一条 **registered observation definition**（可审计、可复现）及 E1/E2/E3 接口。

---

## 7. Decision Mapping（pre-registered）

| Result | Registered Knowledge Action |
|--------|----------------------------|
| Supported | Strengthen（Knowledge Review 另授） |
| Partial | Narrow scope（e.g. Family-dependent claim） |
| Not supported | Downgrade |
| Infeasible | No upgrade |

```text
RUN004 PASS ≠ Gate PASS ≠ Capability Candidate ≠ P4 MET
```

---

## 8. Run Identity（proposed）

| Field | Value |
|-------|--------|
| `run_id` | `CAP_CTX_001_RUN004` |
| `parent` | `CAP_CTX_001_RUN003` |
| `eq` | `EQ-CTX-004` |
| `evidence_type` | Observation Expansion |
| `spec_version` | `0.2` |

Evidence path（若执行）：`research/output/evidence/CAP_CTX_001_RUN004/`

---

## 9. Open Items

| ID | Item | Status |
|----|------|--------|
| O1 | Candidate Family + §5 Governance Table（全字段） | **OPEN**（Fill） |
| O2 | Registered observation definition(s) | **OPEN**（Fill） |
| O3 | E1/E2/E3 interface mapping | **OPEN**（Fill） |
| O4 | Fingerprints / coverage（universe frozen） | **OPEN**（Fill；可复用 RUN003） |
| O5 | Decision mapping strings / Appendix A | **OPEN**（Fill） |

---

## 10. Non-goals（R6 — binding）

RUN004 **不允许**：

```text
❌ Feature ranking
❌ Feature selection
❌ Model comparison
❌ Parameter tuning
❌ Alpha evaluation
❌ Trading performance evaluation
❌ Universe / time co-variables
❌ Claiming P4 from Family expansion alone
❌ Gate v2 / Capability Candidate designation
```

---

## 11. Next

```text
Spec Confirmation PASS ✓
        ↓
Fill Draft v0.1 — [`CAP_CTX_001_RUN004_PRE_REGISTRATION_FILL.md`](CAP_CTX_001_RUN004_PRE_REGISTRATION_FILL.md)
  Family proposed: Liquidity Structure（§5 complete）
        ↓
Fill Review → Confirmation → Auth（另授）
```

当前：**Spec CONFIRMED**；Fill **Draft**；**不**授权 Observation。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | Draft：Observation Expansion；Family only；未冻结 Family |
| 2026-07-21 | 0.2 | Review PASS WITH REVISION：EQ wording；§5 Governance 字段；Claim Boundary；Non-goals |
| 2026-07-21 | 0.2.1 | **Spec Confirmation PASS**；Eligible for Pre-registration Fill |
| 2026-07-21 | 0.2.2 | Pointer：Fill Draft v0.1（Liquidity Structure proposed） |
