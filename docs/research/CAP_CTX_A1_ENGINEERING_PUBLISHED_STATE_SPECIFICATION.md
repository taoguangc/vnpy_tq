# CAP-CTX A1 — Engineering Published State Specification（v0.2）

> **Type**: Engineering Specification（Published State Reliability · Gate **G2** / Bar **E1**）  
> **Status**: **Confirmation PASS** ✓ — Eligible for Pre-registration Fill  
> **Version**: 0.2  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CAP_CTX_A1_ENGINEERING_PUBLISHED_STATE_SPECIFICATION.md`  
> **Parent Proposal**: [`PHASE_A1_ENGINEERING_PUBLISHED_STATE_PROPOSAL.md`](PHASE_A1_ENGINEERING_PUBLISHED_STATE_PROPOSAL.md) v0.2 **Confirmation PASS**  
> **Fill**: [`CAP_CTX_A1_PRE_REGISTRATION_FILL.md`](CAP_CTX_A1_PRE_REGISTRATION_FILL.md) — **Confirmation PASS**  
> **Auth**: [`CAP_CTX_A1_EXECUTION_AUTHORIZATION.md`](CAP_CTX_A1_EXECUTION_AUTHORIZATION.md) — **Draft v0.1** · Auth **NONE**
> **Campaign / Track**: CAP-CTX · Phase A1  
> **Possible evidence path**: `research/output/evidence/CAP_CTX_A1/`（仅 Auth 后）  
> **Spec boundary**: [`CONTEXT_ENGINE_SPEC.md`](../specs/CONTEXT_ENGINE_SPEC.md) v0.1.1 — **本文件不修改 Accepted Spec**  
> **Prior**: Draft v0.1 → PASS WITH REVISION → v0.2 → **Confirmation PASS**  
> **Purpose**: Freeze **Context Capability Runtime Contract** — reliability only · **not** Alpha · **not** RC001 · **not** Strategy

### Spec Confirmation（binding）

```text
================================================
CAP_CTX_A1_ENGINEERING_PUBLISHED_STATE_SPECIFICATION v0.2

Confirmation: PASS ✓

R1–R5: COMPLETE ✓
Scope: Engineering Published State Validation

Excluded:
  Implementation · Strategy · Backtest · RC001 · Candidate Decision

Eligible next: A1 Pre-registration Fill Draft

K001 / Gate CONDITIONAL / Candidate NO / RC001 / Strategy: unchanged
================================================
```

### Claim Boundary（binding）

```text
A1 = Context Capability Runtime Contract（reliability）
        ≠
Capability Validation / Effectiveness / Alpha

Published State = technical projection
        ≠
market truth · predictive probability · trading recommendation

confidence = computation confidence ≠ win_probability
A1 PASS ≠ Capability PASS ≠ RC001 ≠ Strategy
```

---

## Structure（frozen）

```text
1. ContextState Contract
        ↓
2. Version Compatibility
        ↓
3. Publication Boundary
        ↓
4. Deterministic Rule
        ↓
5. Batch / Streaming Parity
        ↓
6. Fault Handling
        ↓
7. Latency Measurement
        ↓
8. Evidence & Reproduction
        ≠
Capability / RC001 / Strategy
```

---

## 1. Experiment Question（frozen）

```text
Can the Context Engine deterministically publish a failure-aware
Published State (ContextState) with batch/streaming parity and
no future-data leakage under a frozen Runtime Contract?
```

下游策略（未来）只应消费 **Published State**，不应直接耦合 raw detector 内部——三层隔离：

```text
Research Layer → Capability Layer（Published State）→ Strategy Layer
```

本 Spec **不**授权任何策略接入。

---

## 2. ContextState Schema Contract

```text
ContextState {
  timestamp,
  instrument,
  context_version,

  validity,              # VALID | DEGRADED | INVALID
  descriptive_state,
  confidence,            # computation confidence ONLY
  diagnostics            # §2.4 allow/forbid
}
```

### 2.1 `validity`

| Value | Meaning |
|-------|---------|
| **VALID** | 契约满足；可只读消费（≠ 交易建议） |
| **DEGRADED** | 可发布但不完整/边界受损 |
| **INVALID** | 不得作为可信 Published State 消费 |

### 2.2 `descriptive_state`

**Allowed**: `compression_state` · `volatility_condition` · `structure_tag`（tags only）  

**Forbidden**: `direction_prediction` · `expected_return` · `trade_bias` · `buy_signal` · `sell_signal`

### 2.3 `confidence`

```text
computation confidence ONLY
FORBIDDEN: prediction / trade confidence / probability of profit
```

### 2.4 `diagnostics`（R3 · binding）

**Allowed**（工程可观测性）：

```text
{
  "missing_bars": 0,
  "data_quality": "good",
  "calculation_time_ms": 12,
  "warmup_complete": true,
  "fault_reason_code": "..."
}
```

**Forbidden**（隐藏 Alpha / 预测通道）：

```text
{
  "expected_direction": "long",
  "future_volatility": "high",
  "trade_quality": "good",
  "edge_score": 0.9
}
```

违反 → 该发布 **INVALID** 或整次 Observation **INVALID**（Fill 写死）。

### 2.5 Relation to Accepted Spec

不静默修改 `CONTEXT_ENGINE_SPEC`；`MarketState` 基线不变；映射 → Fill / 必要时 ADR。

---

## 3. Version Compatibility（R1 · binding）

| Rule | Requirement |
|------|-------------|
| Same `context_version` | 必须产生 **兼容** 契约字段（字段名/语义/validity 枚举） |
| Schema breaking change | **必须**新 `context_version`（及 schema 版本记录） |
| Closed Evidence | **不得**因新版本覆盖或改写 |

```text
RUN_A ContextState v1
RUN_B ContextState v2
        ≠
同一 Capability 静默混用
```

Evidence / RC001（未来）必须按 `context_version` 分隔引用。

---

## 4. Publication Boundary（R2 · binding）

### Publication Timestamp Rule

```text
Published State(t) MAY use only information with
  bar_timestamp <= t

FORBIDDEN:
  future bar
  future session information
  rollover future mapping（t 之后才可知的换月信息）
```

这是 future-data-leakage 的工程落地。违反 → `validity=INVALID` 且 Fault 记录。

---

## 5. Deterministic Publish Rule

```text
same input bars
same timestamp boundary
same context_version
        →
same Published State（per Equality Policy §6.2）
```

隐藏全局状态 / 未注册随机源 → **INVALID** 执行。

---

## 6. Batch / Streaming Parity Protocol

### 6.1 Processes

| Process | Path |
|---------|------|
| **A Batch** | historical bars → `batch_publish()` → `ContextState[t]` |
| **B Streaming** | 1m incremental → `update()` per bar → `ContextState[t]` |

### 6.2 Comparison object

```text
ContextState equality（§6.3 Policy）
        ≠
PnL · trades · strategy metrics · Sharpe / PF
```

### 6.3 Floating Point / Equality Policy（R4 · binding）

**Exact equality**（必须 bit/字面 identical）：

```text
timestamp
instrument
context_version
validity
descriptive_state tags（枚举/字符串）
diagnostics allow-list 中的离散字段
```

**Tolerance**（仅连续量；ε 在 Fill 冻结）：

```text
confidence（若连续）
diagnostics 中显式标为 continuous 的数值（若有）
```

```text
禁止用 0.7000001 vs 0.7 造成未定义假失败
禁止用宽松 ε 掩盖泄漏或非确定性
```

默认：无 Fill ε 时，连续字段也须在约定量化/舍入后 exact。

---

## 7. Fault Matrix

| Scenario | Expected `validity` |
|----------|---------------------|
| missing bar | **DEGRADED** |
| duplicate timestamp | **INVALID** |
| future data leakage / Publication Boundary 违反 | **INVALID** |
| rollover mismatch | **INVALID** |
| session boundary mismatch | **DEGRADED** or **INVALID**（Fill 写死） |
| insufficient warmup | **INVALID** / no publish |
| diagnostics 含 forbidden 预测字段 | **INVALID** |
| symbol switch without contract | **INVALID** or **DEGRADED**（Fill 写死） |

---

## 8. Latency（engineering-only）

```text
1m bar close → update → publish
  < 100ms p99（单品种；环境 Fill 冻结）

Engineering requirement only ≠ Production readiness
```

---

## 9. Evidence & Reproduction（R5）

### 9.1 Path

`research/output/evidence/CAP_CTX_A1/`（Auth 后）

| Artifact | Role |
|----------|------|
| `manifest.json` | identity + **reproduction entry**（§9.2） |
| `context_schema.json` | frozen schema dump + `context_version` |
| `parity_report.json` | equality policy results |
| `fault_test_report.json` | Fault Matrix |
| `latency_report.json` | engineering-only latency |
| `evidence_record.json` | outcome · non-claims |

### 9.2 Reproduction Entry Point（manifest 必填）

```text
reproduction_command      # exact CLI / entry to regenerate
environment_hash          # env identity（packages / OS / interpreter）
input_fingerprint         # dataset / bar window fingerprints
context_version           # must match schema
code_revision             # git SHA
```

A1 必须能回答：

> 六个月后是否仍能重新生成同一 Published State？

不能仅依赖不可复现的工程日志。

---

## 10. Outcome mapping

| Outcome | Meaning | Next preview |
|---------|---------|--------------|
| **PASS** | Contract + parity + faults + no leakage + reproducible | 另授 Gate Re-review（G2） |
| **PARTIAL** | 部分限制可披露 | G2 仍 CONDITIONAL |
| **FAIL** | 可靠性不足 | ≠ K001 Downgrade |
| **INVALID** | 协议/泄漏/diagnostics Alpha / 比较了交易结果 | No Capability Action |

```text
A1 Evidence PASS → Gate Re-eval → Candidate Review →（若 YES）RC001-A
        ≠
A1 PASS → 马上策略
```

---

## 11. Forbidden

```text
❌ Code / Backtest / RC001 / Strategy without Auth
❌ Gate Unlock / Candidate auto
❌ Spec silent change / Closed Evidence overwrite
❌ Version-incompatible silent mix
❌ diagnostics 预测通道
❌ Parity via PnL
```

---

## 12. Open Items（→ Fill）

| ID | Item | Status |
|----|------|--------|
| O1 | JSON types / enum literals | OPEN |
| O2 | Universe / window / fingerprints | OPEN |
| O3 | Tolerance ε + quantization rules | OPEN |
| O4 | Session mismatch branch | OPEN |
| O5 | Latency environment | OPEN |
| O6 | `context_version` / `reproduction_command` 格式 | OPEN |
| O7 | ADR need（Published State vs MarketState） | OPEN |

---

## 13. Spec checklist（v0.2）

| ID | Check | Verdict |
|----|-------|---------|
| AS1 | Reliability ≠ money / effectiveness | **PASS** |
| AS2 | Schema + diagnostics allow/forbid | **PASS** |
| AS3 | Version Compatibility | **PASS** |
| AS4 | Publication Timestamp Rule | **PASS** |
| AS5 | Equality Policy exact/tolerance | **PASS** |
| AS6 | Reproduction Entry Point | **PASS** |
| AS7 | No Code/RC001 | **PASS** |

> Checklist PASS ≠ Confirmation PASS。

---

## 14. Next

```text
Confirmation PASS ✓
        ↓
A1 Fill（Draft）
        ≠
Code / Backtest / RC001
```

当前：**Confirmation PASS**；Fill = Draft v0.1。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | Draft：Schema · Determinism · Parity · Fault · Latency · Evidence |
| 2026-07-21 | 0.2 | PASS WITH REVISION：R1–R5；Runtime Contract 结构 1–8 |
| 2026-07-21 | 0.2 | **Confirmation PASS** — Eligible for Fill |
