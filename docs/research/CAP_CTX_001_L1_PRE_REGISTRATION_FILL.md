# CAP-CTX-001 L1 — Independence Repair Pre-Registration Fill（v0.2）

> **Type**: Governance Completion Document（L1 Fill · Exit Criteria **L1** · I2+I3）  
> **Status**: **Confirmation PASS** ✓ — Pre-Registration COMPLETE · Eligible for Execution Authorization  
> **Version**: 0.2  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CAP_CTX_001_L1_PRE_REGISTRATION_FILL.md`  
> **Parent Spec**: [`CAP_CTX_001_L1_INDEPENDENCE_SPECIFICATION.md`](CAP_CTX_001_L1_INDEPENDENCE_SPECIFICATION.md) v0.2 **Confirmation PASS**  
> **Parent Proposal**: [`PHASE_36_L1_INDEPENDENCE_REPAIR_PROPOSAL.md`](PHASE_36_L1_INDEPENDENCE_REPAIR_PROPOSAL.md) — Confirmation PASS  
> **Auth**: [`CAP_CTX_001_L1_EXECUTION_AUTHORIZATION.md`](CAP_CTX_001_L1_EXECUTION_AUTHORIZATION.md) — **Confirmation PASS** · CP3 **OPEN** · Obs **NOT AUTHORIZED**  
> **LER Seal**: [`CAP_CTX_001_L1_LER_FREEZE_CEREMONY.md`](CAP_CTX_001_L1_LER_FREEZE_CEREMONY.md) — **SEALED**  
> **Manifest**: `research/output/evidence/CAP_CTX_001_L1_RUN001/`
  
> **Parent Knowledge**: K001（Strengthened Qualified + Independence Narrow）— **Claim Frozen**  
> **Lineage**: Closed RUN001–005 read-only · future `run_id=CAP_CTX_001_L1_RUN001`（仅 Auth 后）  
> **Purpose**: Freeze Independent Process instance — **not** Auth · **not** Observation · **not** Gate Unlock · **not** Strategy  
> **Prior**: Draft v0.1 → Fill Review **PASS WITH REVISION** → v0.2 → **Confirmation PASS**

### Fill Confirmation（binding）

```text
================================================
CAP_CTX_001_L1_PRE_REGISTRATION_FILL v0.2

Confirmation: PASS ✓

F1 Process Independence: PASS ✓
F2 M2 / Price Family Freeze: PASS ✓
F3 L1-E1/E2/E3 metrics: PASS ✓
F4 N1 primary / N2 diagnostic: PASS ✓
F5 Anti-Optimization: PASS ✓
EFI-1…5: CLOSED ✓

Pre-Registration: COMPLETE ✓

Eligible next: Execution Authorization Review

Auth: GRANTED WITH CONDITIONS · Confirmation PASS · CP3 OPEN
Observation: NOT AUTHORIZED
Evidence generation: NOT AUTHORIZED（awaiting explicit Obs Auth）
Knowledge update: NOT AUTHORIZED

K001: UNCHANGED
Gate v2: CONDITIONAL / CLOSED
Capability Candidate: NO
RC001: DEFERRED
Strategy: NOT STARTED
================================================
```

### Claim Boundary（binding）

```text
Fill freezes HOW the less-coupled process is instantiated
        ≠
changing WHAT K001 claims
        ≠
Auth / Observation / Gate Unlock / better Context
```

```text
Measurement change = dependency repair
        ≠
performance improvement / better Context discovery

FAIL ≠ K001 false
Claim Migration during Fill/execution = INVALID
```

### Anti-Optimization Clause（R5 · binding）

```text
Independent process design is fixed before outcome observation
and cannot be modified based on observed results.
```

```text
禁止：为了“证明独立性”而在看到结果后改写 Independent Process
（含 GEN / LER / Null / Partition / Horizon / Seed）

违反 → INVALID · 须新 run_id
精神对齐 RUN005：Seal-before-eval · 无事后协议漂移
```

---

## 1. Experiment Object（frozen from Spec）

```text
Can K001-supported descriptive structure survive under a
less definition-coupled evidence generation process?
```

Primary comparison:

```text
Original Evidence Process
        vs
Independent Evidence Process
```

**不是** Old Context vs New Context。

---

## 2. Process Architecture

### 2.1 Original Process（reference only）

```text
M1（volatility）
  → partition / labels from M1
  → evaluate M1-linked separation（SMD_M1 等）
```

### 2.2 Independent Process（L1 primary）

```text
GEN-L1-v0.2（Price Family labels）
        ≠
LER-CTX-L1 v0.2（EVAL-1/2/3）
        ↓
Create → Seal LER + Hash →（Auth）→ Observe → Evaluate → Interpret
```

### 2.3 Process Difference Table（R1 · binding）

| Dependency | Original | Independent（L1） | Removed? |
|------------|----------|------------------|----------|
| **Label generation** | Partition on **M1**（realized vol） | Partition on **M2**（Price / directional efficiency） | M1→label |
| **Evaluation metric** | **SMD_M1**（与 label 同源） | **L1-E1/E2/E3**（后续路径 / persistence / transfer；**≠ M2**） | Eval≡M1 identity |
| **Evaluator access** | 历史管线；无 L1 Seal 边界 | Seal-before-eval；评分前禁 preferred outcome / K001 Decision | Post-hoc protocol + outcome bias path |
| **Interpretation access** | 易与评价交织 | **仅 Decision 之后**；Artifact→Metric→Decision→Interpretation | Interpretation→Metric 路径 |

执行后必须能回答：

> 到底哪一项 dependency 被解除？（上表 Removed? = Yes 的行）

### 2.4 Difference Matrix（Spec §3.3 · retained）

| Dimension | Original | Independent | Dependency Removed | Dependency Retained | Bias Risk | Expected Effect |
|-----------|----------|-------------|--------------------|---------------------|-----------|-----------------|
| Claim / RQ | K001 descriptive | **Same** | — | Claim Boundary | Low | Scope stable |
| Universe / lineage | `{rb,i,MA,TA}` | **Same** | — | Dataset fingerprints | Medium | Not re-P1–P3 |
| Measurement→Label | M1 partition | **M2 partition** | M1→label→M1-proof | TQ/1m/CbC；Family 清单 | Medium | Coupling ↓ |
| Evaluation object | SMD_M1 | L1-E1…E3 ≠ M2 | Eval≡label measure | Controlled evaluator | Medium | Independence ↑ |
| Protocol timing | Historical | Seal-before-eval | Post-hoc edit | Same org | Medium | Self-confirm ↓ |
| Purpose | Discovery/P4 | Dependency repair | Unlock Gate incentive | Gate later input | High if misread | Honest P4 signal |

---

## 3. I2 — Generation Recipe `GEN-L1-v0.2`

### 3.1 Intent

```text
解除：同一 measurement 既做 label 又做 proof（M1 循环）
保留：Universe / 数据契约 / Claim / 已注册 Price Family 身份
```

### 3.2 Price Family Freeze Rule（R2 · binding）

冻结（Confirmation 后不可因结果修改）：

| Frozen element | Binding value |
|----------------|---------------|
| Price observation | `M2_directional_efficiency`（Closed 定义，见 §3.3） |
| Sampling | TQ offline · 1m · CbC · 无复权 · 无跨 session 前向填充 |
| Partition method | `causal_rolling_median_threshold`（§3.4） |
| Threshold source | 因果窗 `S_t` 的 sample median；**禁止** full-sample / expanding / 事后选阈 |

**禁止**：

```text
Observation 结果
  → 调整 Price 定义 / W / L / 阈值算法
  → 重新执行求 PASS
```

违反 → **INVALID** / 新 `run_id`。

### 3.3 Price observation definition（frozen string）

| 字段 | Freeze |
|------|--------|
| `id` | `M2_directional_efficiency` |
| Definition | `M2_t = abs(C_t - C_{t-W}) / sum_{i=0..W-1} abs(C_{t-i} - C_{t-i-1})`；分母为 0 → 缺失 |
| `W` | `20` |
| Warmup | 价格点不足 → 缺失（不填充） |
| Role in L1 | **Generation only** — **不得**作为 L1-E1 评价对象 |

### 3.4 Partition（frozen string）

```text
Algorithm: causal_rolling_median_threshold
Input measure: M2_t（NOT M1）

For each bar t with valid M2_t:
  S_t = { M2_{t-L}, ..., M2_{t-1} }  # finite only; no impute
  If |S_t| < L: emit NO label
  Else:
    m_t = median(S_t)
    if M2_t > m_t: label = HIGH_EFF
    else:            label = LOW_EFF

L = 240
expanding / full-sample median: FORBIDDEN
Bars without label: excluded from L1-E1/E2/E3 samples
```

标签 = descriptive condition 命名，**不是**交易方向。

### 3.5 Recipe summary

| Item | Freeze |
|------|--------|
| Recipe ID | `GEN-L1-v0.2` |
| Universe | `{rb, i, MA, TA}` — no expansion |
| Time / fingerprint | Appendix A（EFI-1/2） |
| Replacement argument | Dependency repair only；**Replacement ≠ Optimization** |
| If metrics “look better” | **不得**解释为更好 Context |

---

## 4. I3 — Evaluation Rubric `LER-CTX-L1` v0.2

### 4.0 Evaluator output order（binding）

```text
Artifact
  → Metric（EVAL-1）
  → Decision（EVAL-2）
  → Interpretation（EVAL-3）
```

**禁止**：

```text
Interpretation expectation → Metric selection / band 调整
```

### 4.0.1 Freeze Checklist（before Observation）

| Item | Binding |
|------|---------|
| Evaluator | `L1 Independent Evaluator (Controlled)` |
| Rubric | `LER-CTX-L1 v0.2` |
| Metrics / bands / Access | §4.1–4.3 · §5 |
| Anti-Optimization | § header Clause |

未完成 → **禁止** Observation。

### 4.1 L1-E1 — Subsequent separation（operational freeze）

**评价问题（冻结）**：

> 在 Independent Process 下，由 GEN labels 划分的条件，其**后续路径分离**是否仍超过 Primary Null（N1）？

**不是**抽象地问「结构是否存在」，也**不是**复测 `SMD_M2`。

```text
L1-E1_metric_id = SMD_FWD_ABSRET

Horizon H = 20 bars（1m）
Forward measure at labeled bar t:
  F_t = mean( abs(ln(C_{t+j}/C_{t+j-1})) for j=1..H )
  # require H finite positive returns; else exclude t

On Primary symbol rb, labels H=HIGH_EFF, L=LOW_EFF:
  nH, nL = counts
  muH, muL = mean(F | H), mean(F | L)
  sH2, sL2 = var(F | H), var(F | L)  # ddof=1
  pooled = sqrt( ((nH-1)*sH2 + (nL-1)*sL2) / (nH+nL-2) )
  SMD_FWD_ABSRET = abs(muH - muL) / pooled
  If nH+nL-2 < 1 or pooled == 0: L1-E1 = Infeasible

Pass / Retain vs N1（primary）:
  SMD_FWD_ABSRET > quantile_95(SMD_FWD_ABSRET under N1)

min_sample_per_label = 5000
Why ≠ Generation: F_t 不使用 M2 定义变量；label 来自 M2，metric 来自后续 |return|
```

### 4.2 L1-E2 — Persistence（operational freeze）

**评价问题**：

> Independent Process 产生的 condition labels，其 **run-length persistence** 是否仍超过 N1？

| Field | Freeze |
|-------|--------|
| Measurement | `mean_run_length` of `{HIGH_EFF, LOW_EFF}` sequence on **rb** |
| Run definition | Maximal consecutive equal-label segment；NO-label bars break runs |
| Horizon | Full registered evaluation window（Appendix A）；warmup excluded |
| Pass / Retain | `mean_run_length > quantile_95(N1 null mean_run_length)` |
| Gate | Formal L1-E2 仅当 L1-E1 ∈ {Retain}；否则 `skipped`（不升格 PASS） |
| `min_runs` | `100` |

### 4.3 L1-E3 — Transfer（operational freeze）

**评价问题**：

> 同一 Independent Process 下，分离是否在冻结宇宙上可迁移？

| Field | Freeze |
|-------|--------|
| Universe | `{rb, i, MA, TA}` |
| Primary | `rb` |
| Transfer direction | `rb → {i, MA, TA}`（单向登记；禁止事后改列表） |
| Per-symbol test | 对每个 transfer symbol 重复 **L1-E1** 公式（同一 H、同一 N1 协议） |
| Aggregation | **E3 Retain** iff L1-E1 Pass/Retain on **every** transfer symbol：`i` ∧ `MA` ∧ `TA`（3/3） |
| Else | Narrow / Reject per aggregate 表；**禁止**删品种凑过 |

### 4.4 EVAL-2 — Decision bands + Aggregate

| Band | Meaning |
|------|---------|
| Retain | 独立过程下仍支持 descriptive condition structure（Claim 内） |
| Narrow | 更窄限定下支持（列收窄项；**禁止**改 Claim 正文） |
| Reject | 不支持 |
| Infeasible | 缺口不足以裁决 |
| Invalid | Seal / Access / Anti-Optimization / Claim Migration / Replacement=Opt 违规 |

| Aggregate | Result |
|-----------|--------|
| L1-E1 Retain，L1-E2 非 Reject，L1-E3 Retain，且 N1 按预期（E1 超 N1 q95） | **PASS** |
| L1-E1 Retain，但 E2/E3 Narrow 或须收窄 | **PARTIAL** |
| L1-E1 Reject，或 E3 关键 Reject，或 N1 不降级（不可辨伪） | **FAIL** |
| 过程违规 | **INVALID** |

```text
Create LER → Seal + Hash → Auth → Observation → Score
Silent amendment after results = INVALID
```

### 4.5 EVAL-3 — Interpretation Independence

评分前 **不可用**：prior conclusion · preferred Gate/K001 outcome · K001 Decision body · 原 Interpretation 叙事作前提 · 未密封结果改协议。

评分后：Claim Boundary 对照 → Interpretation →（另授）Knowledge Review。

---

## 5. Artifact Access Level

| Artifact | Access | Rule |
|----------|--------|------|
| Closed RUN001–005 | read-only | 不改写；不作调参源 |
| K001 Decision / Original interpretation | unavailable until after scoring draft | EVAL-3 |
| LER-CTX-L1 | sealed before Observation | EVAL-2 |
| Observation tables | after Seal only | |
| Raw Parquet | restricted | 仅 Auth 下身份/覆盖核验 |

---

## 6. Null / Comparison Framework（R4）

### 6.1 Primary vs Diagnostic

| ID | Role | Design | May decide L1 Outcome? |
|----|------|--------|-------------------------|
| **N1** | **Primary statistical null** | `iid_label_permutation`；保持 HIGH/LOW **计数不变**；`n_perm=200`；`rng_seed=20240721`（继承 Closed null 身份，非新优化） | **YES** — L1-E1/E2 Pass 规则唯一对照 |
| **N2** | **Diagnostic only** | Coupling diagnostic：在 **同一 GEN labels** 上计算 `SMD_M2`（Generation-identity 伪评价）并与 `SMD_FWD_ABSRET` 并列表披露 | **NO** — 不计入 PASS/FAIL；解释残余耦合 |

```text
N1 = primary statistical null
N2 = diagnostic only
N2 ≠ Capability / L1 Outcome 判定输入
```

若 `SMD_M2 ≫ SMD_FWD_ABSRET`：披露残余 Price 耦合；**不得**因此改 GEN 求好看。

### 6.2 Comparison object

Independent Outcome vs Original Process（reference）= 结构是否仍支持；**≠** 谁更好 / 更赚。

---

## 7. Outcome → Knowledge Action（preview）

| Outcome | Interpretation | Action preview |
|---------|----------------|----------------|
| PASS | Independence strengthens K001 | STRENGTHEN（P4-facing） |
| PARTIAL | Qualification refinement | NARROW |
| FAIL | Evidence generation limitation | NARROW / DOWNGRADE |
| INVALID | Process violation | No Knowledge Action |

```text
FAIL ≠ K001 false
PASS ≠ Gate PASS ≠ Capability Candidate
```

---

## 8. Forbidden

```text
❌ Universe / Time / Family expansion
❌ Feature / parameter search / better Context
❌ 事后改 Price Family / LER / Null（Anti-Optimization）
❌ M1→Mx 换皮重跑（Replacement = Optimization）
❌ Claim Migration
❌ 用 N2 决定 Outcome
❌ Gate Unlock / Candidate / RC001 / Strategy / Backtest / PnL
❌ Code / Observation without Auth
```

---

## 9. Execution Freeze Items（R6）

| ID | Item | Status |
|----|------|--------|
| **EFI-1** | Dataset fingerprint（Appendix A） | **CLOSED** |
| **EFI-2** | Time window / warmup（Appendix A） | **CLOSED** |
| **EFI-3** | Price partition（§3.3–3.4） | **CLOSED** |
| **EFI-4** | Evaluation formulas L1-E1/E2/E3（§4.1–4.3） | **CLOSED** |
| **EFI-5** | Null seed / n_perm / N1–N2 roles（§6） | **CLOSED** |

> EFI 全 CLOSED ≠ Confirmation PASS（须另授 Confirmation Review）。

---

## Appendix A — Execution Freeze Detail

### A.1 Dataset fingerprint（EFI-1）

继承 Closed RUN003 expansion 指纹身份（路径 `data/tq/{sym}`）：

| Symbol | `manifest.json` sha256 | `dominant_windows.json` | `rollover_map.parquet` |
|--------|------------------------|-------------------------|------------------------|
| rb | `bc62c8b606bf5c5018448e54aad841aa14a58f60482042f561e80f99ba8ed0fa` | `051e5b48154a2228ec4e06ed361d8ebed40ba20f2fccec8fc8c953f9a169929b` | `170102046bdbe339aad14de20a9f95463838da18b077fab10e54381102e92a8e` |
| i | `ea0c1aeeb40902a17beb9ae86ebb2f3313fd7199f546cea9ab05c4219ed46239` | `72302ce316c97de9b0448725180743fe7b21cfb66a6c8815f7f89f1567f2ced8` | `3eeedfcaa143ba6a1a698ccb033cae147a696446f1ecd1df2cdb9c293b9bf5ba` |
| MA | `04de9c86cfba8f2a18a3f908d2a5fa748d788dbc8f84a38129b878164321012f` | `9d448d120da2e7bd98cc0ae0a0faf7f3418c6985a58f23c032b1b7f412389109` | `e16a32be6565989629151f12ed1cd5706f6de4eb9d54c0c5809803bf3bbbe64d` |
| TA | `bff7e60648be96dc07671468e567aff6fc179b20dae820f2cc704c302f53867d` | `17ebac8a4e085b910fe07f50fb1fbe89c5e7f0d6ac6da0a362976f3766ed075e` | `86dff2a71b7a8226812d9c3b9932f53273579429b310034485849e46cb7466e7` |

```text
Fingerprint = identity check ≠ evaluation evidence
Mismatch at Auth/Obs → INVALID / HOLD（不换品种凑过）
```

### A.2 Time window（EFI-2）

| Field | Freeze |
|-------|--------|
| Full | `2024-01-01` … `2025-12-31` |
| Period A / B | `2024` / `2025` calendar years |
| Warmup start | `2023-10-01`（excluded from L1-E1/E2/E3 / N1 stats） |
| Data contract | TQ offline / 1m / CbC / unadjusted / real costs N/A（非交易实验） |

继承 RUN001/003/004 执行窗；**禁止**扩窗。

### A.3 Manifest field names（L1_RUN001 · preview）

| Field | Value |
|-------|-------|
| `schema` | `CAP_CTX_001_L1_RunManifest_v1` |
| `run_id` | `CAP_CTX_001_L1_RUN001` |
| `parent_knowledge` | `K001` |
| `gen_recipe` | `GEN-L1-v0.2` |
| `ler_version` | `LER-CTX-L1 v0.2` |
| `primary_null` | `N1` |
| `diagnostic_null` | `N2` |

---

## 10. Fill acceptance checklist（v0.2）

| ID | Check | Verdict |
|----|-------|---------|
| LF1 | Process Difference Table | **PASS** |
| LF2 | Price Family Freeze + Anti-Optimization | **PASS** |
| LF3 | L1-E1/E2/E3 operational strings | **PASS** |
| LF4 | N1 primary / N2 diagnostic | **PASS** |
| LF5 | Evaluator order Artifact→…→Interpretation | **PASS** |
| LF6 | EFI-1…5 CLOSED | **PASS** |
| LF7 | No Auth/Obs/Code | **PASS** |

> Checklist PASS ≠ Confirmation PASS。

---

## 11. Next

```text
Confirmation PASS ✓
        ↓
Execution Authorization Review（Draft）
        ≠
Observation / Strategy / Code（未经 Auth Confirmation + 显式指令）
```

当前：**Confirmation PASS**；Auth = Draft / **NONE**。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | Draft：GEN-L1 / LER / Access / Null；O1–O5 OPEN |
| 2026-07-21 | 0.2 | PASS WITH REVISION：Difference Table；Price Freeze；E1–E3 公式；N1/N2 分离；Anti-Optimization；EFI CLOSED |
| 2026-07-21 | 0.2 | **Confirmation PASS** — Eligible for Execution Authorization |
