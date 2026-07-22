# CAP-CTX-001 L1 — Independence Repair Specification（v0.2）

> **Type**: Independence Repair Experiment Specification（Exit Criteria **L1** · I2+I3）  
> **Status**: **Confirmation PASS** ✓ — Eligible for Pre-registration Fill  
> **Version**: 0.2  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CAP_CTX_001_L1_INDEPENDENCE_SPECIFICATION.md`  
> **Parent Proposal**: [`PHASE_36_L1_INDEPENDENCE_REPAIR_PROPOSAL.md`](PHASE_36_L1_INDEPENDENCE_REPAIR_PROPOSAL.md) v0.2 **Confirmation PASS**  
> **Fill**: [`CAP_CTX_001_L1_PRE_REGISTRATION_FILL.md`](CAP_CTX_001_L1_PRE_REGISTRATION_FILL.md) — **Confirmation PASS**  
> **Auth**: [`CAP_CTX_001_L1_EXECUTION_AUTHORIZATION.md`](CAP_CTX_001_L1_EXECUTION_AUTHORIZATION.md) — **Draft v0.1** · Auth **NONE**  
> **Campaign**: CAP-CTX-001  
> **Parent Knowledge**: K001（Strengthened Qualified + Independence Narrow）— **Claim Frozen**  
> **Possible future run_id**: `CAP_CTX_001_L1_RUN001`（仅 Auth 后）  
> **Purpose**: Capability Evidence Preparation — reduce definition coupling — **not** Gate Unlock · **not** Alpha · **not** Strategy  
> **Prior**: Draft v0.1 → Review **PASS WITH REVISION** → v0.2 → **Confirmation PASS**

### Spec Confirmation（binding）

```text
================================================
CAP_CTX_001_L1_INDEPENDENCE_SPECIFICATION v0.2

Confirmation: PASS ✓

C1 Research Object Freeze: PASS ✓
C2 Dependency Boundary（Process vs Context）: PASS ✓
C3 I2 Replacement ≠ Optimization: PASS ✓
C4 I3 EVAL-1/2/3: PASS ✓
C5 Evaluator Access Boundary: PASS ✓
C6 Claim Migration Control: PASS ✓
C7 Outcome Mapping（FAIL ≠ K001 false）: PASS ✓

Eligible next: Execution Authorization Review

Fill: Confirmation PASS ✓
Auth / Observation: Draft started / NONE
K001 / Gate CONDITIONAL / RC001 / Strategy: unchanged / deferred / not started
================================================
```

### Claim Boundary（binding）

```text
L1 designs HOW evidence is produced with less coupling
        ≠
changing WHAT K001 claims（during Spec/execution）
        ≠
Gate Unlock / better Context search / Feature optimization
```

```text
FAIL ≠ K001 false
L1 success ≠ Gate PASS
Claim migration during execution = INVALID
```

---

## 1. Experiment Question（frozen）

```text
Can K001-supported descriptive structure survive under a
less definition-coupled evidence generation process?
```

---

## 2. Frozen Object Rule（inherited）

| Frozen | Mutable（L1 only） |
|--------|-------------------|
| K001 Claim / RQ / Universe `{rb,i,MA,TA}` / RUN001–005 lineage / Governance | Evidence generation · Measurement dependency（I2） · Evaluation dependency（I3） |
| Primary Target **I2 + I3** | Concrete Generation/Evaluation recipes → **Fill** |

```text
Change HOW ≠ Change WHAT
```

---

## 3. Independence Protocol — Original vs Independent

### 3.1 Original Process（reference）

```text
M1 → partition/labels from M1 → evaluate M1-linked separation（+ E2/E3）
```

Coupling: measurement → label → proof。

### 3.2 Independent Process（L1）

```text
Generation（observation/condition）
        ≠
Evaluation（EVAL-1/2/3；not Observation identity）
        ↓
Create → Seal → Hash → Evaluate
```

### 3.3 Difference Matrix（expanded · R1）

| Dimension | Original | Independent（L1） | Dependency Removed | Dependency Retained | Bias Risk | Expected Effect |
|-----------|----------|------------------|--------------------|---------------------|-----------|-----------------|
| Claim / RQ | K001 descriptive structure | **Same** | — | Claim Boundary | Low if frozen | Scope stable |
| Universe / lineage | Closed chain | **Same** | — | Dataset identity | Medium（shared data） | Not re-tested |
| Measurement→Label | M1 defines partition | **I2**: labels **not** from measure under eval | M1→label→proof loop | Shared data contract | Medium if residual | Coupling ↓ |
| Evaluation object | M1-linked SMD etc. | **I3**: metrics ≠ Generation identity | Eval≡Observation | Human Controlled evaluator | Medium | Independence ↑ |
| Protocol timing | Historical pipeline | Seal-before-eval | Post-hoc protocol edit | Same org | Medium | Self-confirm ↓ |
| Purpose | Discovery/robustness/family | Reduce definition coupling | Sample-stack incentive | Gate as later input | High if “unlock Gate” | Honest P4 signal |

**L1 目标**：明确**哪些依赖被解除**，以及解除后支持是否仍成立——不是创造“更好系统”。

Fill 须用实例填满本表各列。

---

## 4. I2 Measurement Independence

### 4.1 Goal

```text
降低 Measurement → Label → Evaluation 循环
```

### 4.2 Fill must answer

| Item | |
|------|--|
| Removed dependencies | 解除的 measurement→label / →proof |
| Retained observations | 保留的 observation 域（非新 Family 搜索） |
| Residual measurement bias | 仍共享测量假设 |

### 4.3 Forbidden Substitution Principle（R2 · binding）

```text
Replacement Measurement ≠ Optimization Target
```

**禁止**：

```text
M1 → 发现耦合 → 换 M2/M3 → 重新证明（选更容易 PASS 的 measurement）
```

替换若发生，须论证：**为解除耦合**，不是为提高通过率；且须满足 Generation ≠ Evaluation。

---

## 5. I3 Evaluation Independence（R3 · three layers）

```text
Observation
        ↓
Evaluation（EVAL-1 / EVAL-2）
        ↓
Interpretation（EVAL-3 · posterior）
```

**禁止**：

```text
Observation → Interpretation expectation → Evaluation
```

### EVAL-1 — Metric Independence

评价指标**不直接复用** Context 定义变量（不与 Generation observation 恒等）。

### EVAL-2 — Decision Independence

评分规则在**看到结果之前**冻结（Seal + Hash）。

### EVAL-3 — Interpretation Independence

Knowledge / preferred outcome / prior conclusion **不参与评分**；解释仅在评分后。

| Fill must answer | |
|----------------|--|
| EVAL-1 metrics list + why ≠ Generation | |
| EVAL-2 sealed scoring rules + seal timing | |
| EVAL-3 ban on Knowledge-in-scoring | |

Illustrative Evaluation families（non-binding）：future realized behavior · holding/condition stability · distribution shift · cross-condition consistency。

---

## 6. Artifact Governance + Access Boundary（R4）

### 6.1 Sequence（inherit RUN005）

```text
Create → Seal → Hash / version →（explicit Auth）→ Evaluate → Evidence Review
```

### 6.2 Access Boundary（binding）

**Before Seal / before Evaluate**，Evaluator **cannot access**：

| Blocked | Reason |
|---------|--------|
| Prior conclusion / preferred Gate or K001 outcome | Outcome bias |
| K001 Knowledge Decision body as scoring input | EVAL-3 |
| Previous Interpretation narratives as eval premise | Narrative inheritance |
| Unsealed result tables for protocol editing | Post-hoc design |

**After Seal**：Governed read-only per Fill Access Level；Closed RUN001–005 read-only immutable。

Silent protocol amendment → **INVALID** / 新 `run_id`。

---

## 7. Forbidden List（+ Claim Migration · R5）

```text
❌ 新 Universe / Time Window / Family 搜索
❌ 参数优化 / Feature Engineering / “更好 Context”
❌ M1→Mx 换皮重跑（Replacement = Optimization）
❌ 重新定义 K001 Claim
❌ Gate Unlock / Candidate / RC001 / Strategy / Backtest / PnL
❌ 改写 Closed Evidence
❌ 为过 Gate 设计协议
```

### Forbidden: Claim Migration（during Spec/Fill/Execution）

```text
❌ Because L1 looks weak → rewrite K001 claim mid-flight
   e.g. “persistent transferable descriptive structure”
        → “weaker local pattern” inside Spec/execution
```

Claim 变更**仅**能经**另授 Knowledge Review**（Outcome PARTIAL/FAIL → NARROW/DOWNGRADE），**不得**在 Spec 执行过程中迁移 Claim。

---

## 8. L1 Outcome Mapping（R6）

| Outcome | Meaning | Action preview |
|---------|---------|----------------|
| **PASS** | Independence strengthens K001 robustness under less-coupled process | STRENGTHEN（Independence / P4-facing） |
| **PARTIAL** | Qualification refinement / claim narrowing required | NARROW |
| **FAIL** | Evidence generation limitation（too coupled / independent process unsupported） | NARROW / DOWNGRADE |
| **INVALID** | Process / Access / Frozen Object / Claim Migration violation | No Knowledge Action |

```text
FAIL ≠ K001 false
INVALID ≠ Independence FAIL
PASS ≠ Gate PASS
```

---

## 9. Relation to Gate

```text
L1 = Capability Evidence Preparation
        ↓
Evidence update（另授）
        ↓
Gate v2 Re-Review（另授）
```

L1 ≠ Gate Unlock Experiment。

---

## 10. Spec acceptance checklist（v0.2）

| ID | Check | Verdict |
|----|-------|---------|
| LS1 | EQ frozen；≠ better Context | **PASS** |
| LS2 | Difference Matrix with Removed/Retained/Bias/Effect | **PASS** |
| LS3 | Replacement ≠ Optimization | **PASS** |
| LS4 | I3 = EVAL-1/2/3 | **PASS** |
| LS5 | Access Boundary + Seal chain | **PASS** |
| LS6 | Claim Migration forbidden | **PASS** |
| LS7 | Outcome Mapping；FAIL ≠ K001 false | **PASS** |
| LS8 | No Fill/Auth/Obs | **PASS** |

> Checklist PASS ≠ Spec Confirmation PASS。

---

## 11. Next

```text
Confirmation PASS ✓
        ↓
Pre-registration Fill（Draft）
        ≠
Auth / Observation / Strategy / Code
```

当前：**Confirmation PASS**；Fill = Draft（另文）。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | 首版 Draft：Difference Matrix；I2/I3；Seal 链；Forbidden |
| 2026-07-21 | 0.2 | PASS WITH REVISION：Matrix 扩列；Replacement≠Opt；EVAL-1/2/3；Access Boundary；Claim Migration |
| 2026-07-21 | 0.2 | **Confirmation PASS** — Eligible for Fill |
