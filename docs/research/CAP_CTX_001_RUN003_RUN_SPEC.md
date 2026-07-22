# CAP_CTX_001_RUN003 — Cross-sectional Evidence Run Specification（v0.2）

> **Type**: Cross Evidence Run Specification（Cross-sectional）  
> **Status**: **CLOSED** ✓ — Fill / Auth / Observation / Evidence / K001 Review complete  
> **Version**: 0.2  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CAP_CTX_001_RUN003_RUN_SPEC.md`  
> **Campaign**: CAP-CTX-001（PROMOTED）  
> **Parent Knowledge**: K001 (**Strengthened Qualified**) — [`K001_KNOWLEDGE_REVIEW.md`](K001_KNOWLEDGE_REVIEW.md)  
> **Governance**: [`CROSS_EVIDENCE_GOVERNANCE.md`](CROSS_EVIDENCE_GOVERNANCE.md) v1.2 Baseline  
> **Lineage**: `parent=CAP_CTX_001_RUN002`（Closed；不可改写）  
> **Evidence Type**: **Cross-sectional**（G-CX-001 / A.2）  
> **Purpose**: Cross-sectional stress-test K001 — **not** Gate · **not** RC001 · **not** Alpha

### Review

```text
v0.2 Spec Review: PASS WITH REVISION ✓
v0.2 Spec Confirmation: PASS ✓
Fill: Confirmation PASS ✓
Auth: GRANTED · Run: **CLOSED** ✓
```

### Single-variable declaration（R2）

```text
RUN003 changes Universe only.

Time window 2024–2025 is a registered execution condition
inherited from RUN001 protocol,
not an experimental variable of RUN003.
```

### Boundary

```text
✅ Spec Review PASS WITH REVISION
❌ Fill / Auth / Observation
❌ 最终 Universe 冻结（Fill 阶段）
❌ K001 Knowledge Decision
❌ Gate v2 / RC001 / Alpha
```

```text
RUN003 is not an independent discovery experiment.

It is a registered cross-sectional evidence evaluation
of K001 strengthened qualified knowledge.
```

---

## Review Response（v0.1 → v0.2）

| Item | Revision |
|------|----------|
| R2 Time non-variable | §3.3 升格为显式声明 |
| R3 Universe intent | §3.1：expansion = 初始宇宙外预注册品种；非优化选择 |
| R4 E3 | §3.2：Expanded Universe transfer evaluation |

---

## 1. Research Question

### EQ-CTX-003

```text
Under the same registered observation and evaluation protocol
as CAP_CTX_001_RUN001,

does the descriptive condition structure persist across
an expanded instrument universe?
```

中文：

> 在与 RUN001 **相同**的注册观测与评价协议下，descriptive condition structure 是否在**扩展品种宇宙**上仍然成立？

### 1.1 Cross Evidence Relationship

主问题：

> Does the registered descriptive structure remain supported when the evaluated universe is expanded under a single registered cross-sectional change?

**不是**：发现新结构 · 换时间窗 · 换 Observation Family · Capability 已证实 · 策略/交易研究。

| Run | Evidence Type | 唯一主变量 |
|-----|---------------|------------|
| RUN001 | Discovery | — |
| RUN002 | Temporal | Time window |
| RUN003 | **Cross-sectional** | **Universe** |

---

## 2. Protocol Inheritance

> Protocol inherited from CAP_CTX_001_RUN001 unless explicitly overridden by registered universe scope.

| Item | Value（继承） |
|------|----------------|
| Families | Volatility + Price only |
| M1 / M2 / W | realized vol / directional efficiency / 20 |
| Partition | `causal_rolling_median_threshold`, L=240 |
| Eval order | E1 → E2 → E3 |
| E1 | `SMD_M1` vs N1 q95；min 5000/label；SMD_M2 secondary |
| E2 | mean_run_length vs N2 q95；min_runs 100（primary `rb`） |
| E3 | **Expanded Universe transfer evaluation**（§3.2） |
| N1 / N2 | 同 RUN001（seed **20240721**） |
| Data | TQ offline / 1m / CbC / 无复权 |

### Carried methodological limitation

```text
E1 = supporting only（definition coupling）
Interpretation weight: E2 + E3 + SMD_M2 ≥ isolated E1
```

### Integrity Constraint（C-XEV）

```text
No methodological modification shall be introduced
for the purpose of increasing support for existing knowledge.
```

---

## 3. What Changes（唯一主变量：Universe）

```text
RUN003 changes Universe only.
```

### 3.1 Universe — Cross-sectional expansion only（R3）

**Baseline（initial evaluation universe；frozen）：**

| Role | Symbol |
|------|--------|
| Primary | `rb` |
| Transfer | `i`, `MA` |

**Expansion intent（须在 Fill 冻结具体品种）：**

> Add **one pre-registered instrument outside the initial evaluation universe** `{rb, i, MA}`.

研究目的：

```text
未知品种加入后的结构稳定性
        ≠
「第四个品种」或结果导向的品种优化选择
```

**Draft 候选（非最终冻结）：** `TA` — 作为 initial universe 外的 +1 验证对象；Fill 须确认数据可用性与指纹，**不得**因预期结果挑选品种。

```text
Evaluated universe (draft): rb, i, MA, +1 expansion instrument
唯一主变量 = expansion instrument（单选）
不得同时：换时间 / 换 Family / 改指标 / 改 Null
```

**Fill 前未冻结 expansion instrument → 不得 Observation。**

### 3.2 E3 — Expanded Universe transfer evaluation（R4）

E3 评价**扩展后宇宙整体**的 transfer，而非仅新增品种：

```text
E3 evaluates whether the registered condition structure
remains supported across the expanded universe.
```

**Operational rule（draft；Fill 随 expansion instrument 冻结列表）：**

| Check | Rule |
|-------|------|
| Universe | initial transfer `{i, MA}` **plus** expansion instrument |
| E3 supported | E1 PASS on **every** registered transfer symbol in expanded universe |
| Partial path | primary E1 Pass but not all transfer Pass → `n3_isolated` / Partial |

```text
E3 is NOT "TA evaluation only".
E3 is expanded-universe transfer evaluation:
  initial members + new member must be considered together.
```

失败模式须可区分：

* 仅 expansion instrument 失败 → Partial / Narrow 路径  
* initial transfer 亦失败 → 更强 Not supported / Downgrade 信号  

### 3.3 Time Scope — execution condition, NOT experimental variable（R2）

```text
Time window 2024–2025 is a registered execution condition
inherited from RUN001 protocol,
not an experimental variable of RUN003.
```

| Item | Freeze（execution condition） |
|------|-------------------------------|
| Full | `2024-01-01` … `2025-12-31` |
| Period A / B | 2024 / 2025 |
| Warmup start | `2023-10-01` |

```text
Temporal OOS was addressed by RUN002.
RUN003 does NOT re-test time as a hypothesis variable.
```

---

## 4. Cross Evidence Decision Framework（R2 — Frozen）

| RUN003 Result (after Evidence Review) | Registered K001 Action |
|---------------------------------------|------------------------|
| **Supported** — E2+E3 与 RUN001/002 方向一致；expanded universe 覆盖完整 | **Strengthen**（Knowledge Review 另授；非自动） |
| **Partial** — 仅部分 transfer / E2 或 E3 一弱一强 | **Narrow scope** |
| **Not supported** — expanded universe 上 E2/E3 系统性失败 | **Downgrade** |
| **Infeasible** — coverage STOP / sample HOLD / 连续性不足 | **No upgrade**（≠ Negative Evidence） |

```text
INFEASIBLE ≠ NOT SUPPORTED
NOT SUPPORTED = Valid Knowledge Boundary Evidence
RUN003 PASS ≠ Gate PASS ≠ Capability Candidate
```

---

## 5. Dataset / Fingerprint Requirements

Fill 阶段冻结；本 Spec 不冻结最终 Universe。

| Item | Requirement |
|------|-------------|
| Expansion instrument | 单选 + 须在 initial universe 外 + SHA256 |
| Baseline | rb / i / MA 指纹与 RUN001 一致 |
| Coverage | 2024–2025 月度 presence |
| Manifest + C-ENV | Auth 后、Observation 前 |

---

## 6. Artifacts（执行后）

| Artifact | Path pattern |
|----------|----------------|
| Manifest | `research/output/evidence/CAP_CTX_001_RUN003/CAP_CTX_001_RUN_MANIFEST.json` |
| Evaluation | `.../evaluation.json` |
| EvidenceRecord | `.../evidence_record.json` |

---

## 7. Claim Boundary

允许：RUN003 cross-sectional 条件下，expanded universe 上与 K001 一致/不一致的 Evidence。  
禁止：universal capability · Gate · RC001 · Alpha · Capability Candidate · 无条件 K001 升级。

---

## 8. Run Identity

| Field | Value |
|-------|-------|
| `run_id` | `CAP_CTX_001_RUN003` |
| `parent` | `CAP_CTX_001_RUN002` |
| `eq` | `EQ-CTX-003` |
| `evidence_type` | Cross-sectional |
| `knowledge_link` | K001 (Strengthened Qualified) |

---

## 9. Open Items

| ID | Item | Status |
|----|------|--------|
| O1–O5 | Fill 关闭 | **CLOSED**（见 Fill v0.2） |

---

## 10. Phasing

| Phase | Status |
|-------|--------|
| Spec Confirmation | **PASS** ✓ |
| Fill | **Confirmation PASS** ✓ |
| Execution Auth | **GRANTED** · Run **CLOSED** ✓ |
| Closure | [`CAP_CTX_001_RUN003_CLOSURE_REVIEW.md`](CAP_CTX_001_RUN003_CLOSURE_REVIEW.md) |
| Observation | NONE |

---

## 11. Next

```text
RUN003 CLOSED ✓
  → Capability Portfolio Bar Review（suggested；非授权）
```

**Closure**: [`CAP_CTX_001_RUN003_CLOSURE_REVIEW.md`](CAP_CTX_001_RUN003_CLOSURE_REVIEW.md)

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | Draft：Cross-sectional；Universe +TA draft |
| 2026-07-21 | 0.2 | Review PASS WITH REVISION；Universe only；E3 expanded universe；time non-variable |
| 2026-07-21 | 0.2.1 | Spec Confirmation PASS |
| 2026-07-21 | 0.2.2 | Fill Confirmation PASS |
