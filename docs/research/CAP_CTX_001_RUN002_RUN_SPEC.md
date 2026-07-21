# CAP_CTX_001_RUN002 — Cross Evidence Run Specification（v0.2）

> **Type**: Cross Evidence Run Specification  
> **Status**: **Review PASS** ✓ — Fill **Confirmation PASS** ✓  
> **Version**: 0.2  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CAP_CTX_001_RUN002_RUN_SPEC.md`  
> **Campaign**: CAP-CTX-001（PROMOTED）  
> **Parent Knowledge**: K001 (Qualified) — [`K001_KNOWLEDGE_REVIEW.md`](K001_KNOWLEDGE_REVIEW.md)  
> **Lineage**: `parent=CAP_CTX_001_RUN001`（Closed；不可改写）  
> **Fill**: [`CAP_CTX_001_RUN002_PRE_REGISTRATION_FILL.md`](CAP_CTX_001_RUN002_PRE_REGISTRATION_FILL.md) v0.2 **Confirmation PASS**  
> **Purpose**: Strengthen / stress-test K001 — **not** Gate · **not** RC001 · **not** Alpha

### Review

```text
v0.1 Spec Review: PASS ✓
R1 Cross Evidence Boundary: applied
R2 Decision Mapping: applied / frozen
Fill v0.2 Confirmation: PASS ✓
Execution: NOT AUTHORIZED
Observation: NONE
```

### Positioning

```text
K001 Qualified Knowledge
        ↓
RUN002 Spec Review PASS ✓
        ↓
Fill Confirmation PASS ✓
        ↓
Auth → Observation（另授）
        ↓
Cross Evidence vs RUN001 → K001 Update Decision
```

### 本文不是

```text
❌ Observation Execution
❌ Gate Policy / Gate PASS
❌ RC001 / Opportunity / Trading / Alpha
❌ 修改 RUN001 Closed 产物
❌ 无条件 Accepted Knowledge 自动升级
```

---

## 1. Research Question（本 Run）

### EQ-CTX-002

```text
Under the same registered observation and evaluation protocol as RUN001,
does the descriptive condition structure persist on a temporally
out-of-sample window?
```

中文：

> 在与 RUN001 **相同**的注册观测与评价协议下，descriptive condition structure 是否在**时间外样本**窗口上仍然成立？

### 1.1 Cross Evidence Relationship（R1）

```text
RUN002 is not an independent discovery experiment.

It is a registered cross-evidence evaluation
of K001 qualified knowledge.
```

主问题：

> Does the registered descriptive structure remain supported under a temporally separated run?

不是：发现新的结构 / 新 Hypothesis。

### Relation to K001

| | RUN001 | RUN002 |
|--|--------|--------|
| Role | Initial qualified evidence | Temporal Cross Evidence |
| Claim impact | Created K001 (Qualified) | May **strengthen / narrow / downgrade** K001 |

**One primary hypothesis**：Temporal OOS only。品种扩展 → RUN003+。

---

## 2. Protocol Inheritance（Frozen from RUN001）

为保持 Cross Evidence 可比性，**协议不变**：

> Protocol inherited from CAP_CTX_001_RUN001 unless explicitly overridden by registered temporal scope.

| Item | Value（继承） |
|------|----------------|
| Families | Volatility + Price only |
| M1 | `M1_realized_volatility`, W=20 |
| M2 | `M2_directional_efficiency`, W=20 |
| Partition | `causal_rolling_median_threshold`, L=240 |
| Eval order | E1 → E2 → E3 |
| E1 | `SMD_M1` vs N1 q95；min 5000/label；SMD_M2 secondary |
| E2 | mean_run_length vs N2 q95；min_runs 100 |
| E3 | E1 Pass on both transfer symbols |
| N1 | iid_label_permutation；200；seed **20240721** |
| N2 | block_label_permutation；block=60；200；seed **20240721** |
| Data | TQ offline / 1m / CbC / 无复权 |

### Carried methodological limitation

```text
E1 provides supporting descriptive evidence,
not standalone capability confirmation.
(Definition coupling: M1 → partition → SMD_M1)
```

解释权重：**E2 + E3 + SMD_M2** ≥ 孤立 E1。

---

## 3. What Changes（本 Run 唯一主变量）

### 3.1 Time Scope — Temporal OOS

| 切片 | RUN001 | RUN002 |
|------|--------|--------|
| Full | 2024-01-01 … 2025-12-31 | **2022-01-01 … 2023-12-31** |
| Period A / B | 2024 / 2025 | **2022 / 2023** |
| Warmup start（执行） | 2023-10-01 | **2021-10-01** |

非重叠时间段；temporal reproducibility evidence。  
**不是**因该区间「更好看」。

### 3.2 Universe — Unchanged

| Role | Symbol |
|------|--------|
| Primary | `rb` |
| Transfer | `i`, `MA` |

---

## 4. Cross Evidence Decision Framework（R2 — Frozen）

RUN002 结果**只能**影响 `K001 Qualification Status`，**不能**直接影响 Gate / RC001 / Alpha。

### Pre-registered mapping（设计先于结果）

| RUN002 Result (after Evidence Review) | K001 Action |
|---------------------------------------|-------------|
| **Supported** — E2+E3 方向与 RUN001 一致；覆盖完整；无 HOLD/STOP | **Strengthen qualification**（仍非 unconditional ACCEPT；仍非 Gate PASS） |
| **Partial** — E2 或 E3 一弱一强 / 仅部分品种 / 方法学限制主导 | **Narrow scope**（Qualification retained with narrower scope） |
| **Not supported** — E2 或 E3 系统性失败 | **Downgrade** |
| **Infeasible** — coverage STOP / sample HOLD | **No upgrade**；必要时新 `run_id` |

```text
RUN002 PASS ≠ Gate PASS
RUN002 PASS ≠ Unconditional Knowledge
RUN002 Negative ≠ delete RUN001 artifacts
```

### Cross Evidence Integrity Constraint

```text
RUN002 shall not introduce any post-RUN001
methodological modification intended to improve
the probability of supporting K001.
```

（Cross Evidence 检验 Knowledge，不优化实验设计。）

---

## 5. Dataset / Fingerprint Requirements

执行前须：Fingerprint 实例、2022–2023 月度覆盖、Manifest + C-ENV、Fill Appendix、Execution Authorization。  
细节见 Fill 文档。

---

## 6. Artifacts（执行后）

| Artifact | Path pattern |
|----------|----------------|
| Manifest | `research/output/evidence/CAP_CTX_001_RUN002/CAP_CTX_001_RUN_MANIFEST.json` |
| Evaluation | `.../evaluation.json` |
| EvidenceRecord | `.../evidence_record.json` |
| Cross note | `docs/research/CAP_CTX_001_RUN001_RUN002_CROSS_EVIDENCE.md`（另授） |

---

## 7. Claim Boundary

允许：Under RUN002 OOS conditions, evidence consistent / inconsistent with RUN001 descriptive structure.  
禁止：Universal market conditions · unconditional K001 · Gate / RC001 / Alpha。

---

## 8. Run Identity

| Field | Value |
|-------|-------|
| `run_id` | `CAP_CTX_001_RUN002` |
| `parent` | `CAP_CTX_001_RUN001` |
| `eq` | `EQ-CTX-002` |
| `knowledge_link` | K001 (Qualified) |

---

## 9. Phasing

| Phase | Status |
|-------|--------|
| Spec Draft | done |
| Spec Review | **PASS** |
| Fill | **Confirmation PASS**（v0.2） |
| Execution Auth | **Draft** — NOT GRANTED（见 Auth 文档） |
| Observation | NONE |

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | Draft：Temporal OOS；协议继承 |
| 2026-07-21 | 0.2 | Review PASS；R1；R2；Fill Confirmation PASS；Integrity Constraint |
