# CAP-CTX A1 — Engineering Published State Pre-Registration Fill（v0.2）

> **Type**: Governance Completion Document（A1 Fill · G2 / E1 Engineering）  
> **Status**: **Confirmation PASS** ✓ — Pre-Registration COMPLETE · Eligible for Execution Authorization  
> **Version**: 0.2  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CAP_CTX_A1_PRE_REGISTRATION_FILL.md`  
> **Parent Spec**: [`CAP_CTX_A1_ENGINEERING_PUBLISHED_STATE_SPECIFICATION.md`](CAP_CTX_A1_ENGINEERING_PUBLISHED_STATE_SPECIFICATION.md) v0.2 **Confirmation PASS**  
> **Parent Proposal**: [`PHASE_A1_ENGINEERING_PUBLISHED_STATE_PROPOSAL.md`](PHASE_A1_ENGINEERING_PUBLISHED_STATE_PROPOSAL.md) — Confirmation PASS  
> **Auth**: [`CAP_CTX_A1_EXECUTION_AUTHORIZATION.md`](CAP_CTX_A1_EXECUTION_AUTHORIZATION.md) — **Confirmation PASS** · CP3 **OPEN**  
> **Impl Plan**: [`CAP_CTX_A1_IMPLEMENTATION_PLAN.md`](CAP_CTX_A1_IMPLEMENTATION_PLAN.md) — Impl Auth **GRANTED** · code present  
> **Manifest**: `research/output/evidence/CAP_CTX_A1/` — C-ENV **SATISFIED** · Obs **NOT AUTHORIZED**
> **ADR**: [`DECISIONS.md`](../../DECISIONS.md) — **Decision 019**  
> **Evidence path（Auth 后）**: `research/output/evidence/CAP_CTX_A1/`  
> **Possible run_id**: `CAP_CTX_A1_RUN001`（仅 Auth 后）  
> **Prior**: Draft v0.1 → PASS WITH REVISION → v0.2 → **Confirmation PASS**

### Fill Confirmation（binding）

```text
================================================
CAP_CTX_A1_PRE_REGISTRATION_FILL v0.2

Confirmation: PASS ✓

O-TAG / O-CONF / O-CLI / O-LAT / O-ADR: CLOSED ✓
F1–F6: FROZEN ✓
Decision 019: Accepted ✓

Pre-Registration: COMPLETE ✓

Eligible next: Execution Authorization Draft

Auth: NONE（Draft started）
Observation / Implementation / Backtest: NONE
RC001: NOT STARTED

K001: UNCHANGED
Gate v2: CONDITIONAL
Capability Candidate: NO
================================================
```

### Claim Boundary（binding）

```text
A1 PASS = Engine can stably publish Published State
        ≠
Context makes money / K001 rewrite / Gate PASS / Candidate
```

---

## 1. Object

```text
Can the Context Engine deterministically publish a failure-aware
Published State with batch/streaming parity and no future-data leakage?
```

---

## 2. F1 — Runtime Identity（frozen）

| Field | Value |
|-------|-------|
| `engine_id` | `paaf.context_published_state` |
| `schema_version` | `ContextState.v1` |
| `context_version` | `A1-CTX-PS-v1.0.0` |
| `spec_version` | `0.2` |
| `fill_version` | `0.2` |
| `code_revision` | Manifest 时 `git rev-parse HEAD` |
| `environment_hash` | python + platform + packages + requirements sha256 |
| `dependency_hash` | `requirements.txt` sha256 |
| `reproduction_command` | §5 O-CLI（冻结） |

Breaking schema → 新 `context_version` / `schema_version`；Closed Evidence 不覆盖。

---

## 3. F2 — Evaluation Dataset（frozen）

| Item | Value |
|------|-------|
| Universe | `{rb, i, MA, TA}` |
| Source | TQ offline · 1m · CbC · 无复权 |
| Full window | `2024-01-01` … `2025-12-31` |
| Warmup | `2023-10-01`（excluded if unpublished） |
| Session | 不跨 session 前向填充；不虚构 bar |
| Rollover | CbC；`bar_timestamp <= t` only |
| Fingerprints | Appendix A |

数据选择 **不是** 优化变量。

---

## 4. O-TAG — Tag taxonomy（R1 · CLOSED）

`descriptive_state` 使用冻结枚举键 **`context_state`**（单主标签）+ 可选并列条件：

### Allowed

```text
context_state ∈ {
  compression,
  expansion,
  volatility_condition,
  liquidity_condition,
  invalid
}
```

说明：

- 以上为 **Published State descriptive tags**（A1 Runtime Contract）。  
- **不是** Accepted Spec `MarketState` ∈ {UNKNOWN, TREND, RANGE} 的静默扩展。  
- `compression` / `expansion` 在此仅为工程可发布标签，**≠** Spec 基线事实升格（Decision 002 / CONTEXT_ENGINE_SPEC 仍约束）。  
- `invalid` = 描述层标记数据/契约不可用（可与 `validity=INVALID` 对齐，但二者语义分列记录）。

### Forbidden

```text
trade_signal
long_bias
short_bias
expected_return
edge_score
direction_prediction
buy_signal
sell_signal
```

A1 验证 Published State，**不**验证交易含义。

### Operational definitions（audit strings · frozen）

| Tag | Definition string（A1） |
|-----|-------------------------|
| `compression` | `range(high-low)/SMA(range,20) < 1` on closed bars ≤ t；else not this tag |
| `expansion` | `range(high-low)/SMA(range,20) >= 1` on closed bars ≤ t |
| `volatility_condition` | label from M1-style realized vol vs causal median L=240（High/Low as subtag in diagnostics only if needed）；主 `context_state` 仍取 compression/expansion/liquidity/invalid 之一 |
| `liquidity_condition` | volume_t / median(volume[t-L:t]) vs 1.0（active/quiet subtag optional in diagnostics） |
| `invalid` | insufficient warmup / non-finite inputs / Publication Boundary fail |

**Primary publish rule（frozen）**：每 `t` 恰好一个主 `context_state` ∈ 上表；优先级：`invalid` >（若同时触发）`liquidity_condition` 不覆盖 compression/expansion — 主标签取 compression **或** expansion 二选一（由 range ratio）；liquidity/volatility 仅作 `diagnostics` allow-list 子键，**不**另开交易语义。

简化主规则（绑定）：

```text
if warmup fail or non-finite: context_state = invalid
else if range_ratio < 1: context_state = compression
else: context_state = expansion
```

`volatility_condition` / `liquidity_condition` 保留在 **允许枚举** 中供后续版本/子字段使用；**本 Fill v0.2 主路径仅发布 compression | expansion | invalid**，以免 taxonomy 漂移。并列条件若写入，仅进 `diagnostics` 的 allow-list 键：`vol_regime_subtag` · `liq_regime_subtag`（∈ {high,low,active,quiet,unknown}）。

---

## 5. O-CONF — confidence（R2 · CLOSED）

```text
confidence_semantics: computational_confidence_only
```

### Formula（frozen）

```text
confidence = mean([
  1.0 if warmup_complete else 0.0,
  finite_input_ratio,          # fraction of required inputs finite at t
  1.0 if publication_boundary_ok else 0.0,
  1.0 if validity != INVALID else 0.0
]) ∈ [0, 1]
rounded half-even to 6 decimal places
```

### Allowed sources

- data completeness  
- detector/engine validity（工程有效，非 alpha）  
- calculation consistency / boundary OK  

### Forbidden sources

- future outcome · forward return · PnL · strategy performance  

`confidence ≠ win_probability`。

---

## 6. O-CLI — Reproduction entrypoint（R3 · CLOSED）

```text
reproduction_command (Windows / repo root):

.\.venv\Scripts\python.exe -m context_engine.validate_a1 --manifest <manifest_path>
```

| Input | Required |
|-------|----------|
| `--manifest` | path to `manifest.json` |
| dataset fingerprint | inside manifest |
| runtime / environment hash | inside manifest |

| Output | Required |
|--------|----------|
| ContextState artifact(s) | under evidence dir |
| evaluation / report artifacts | parity · fault · latency · evidence_record |

Implementation Auth 后必须提供该模块入口（或薄包装）；**不得**改命令字符串凑过复现。

---

## 7. O-LAT — Latency（R4 · CLOSED）

```text
Measurement:
  bar_close_timestamp  →  ContextState_published_timestamp

Metric: publish_latency_ms
Threshold: p99 < 100ms（单品种；环境写入 Manifest）

INCLUDED: Context Engine publish path only
EXCLUDED: strategy decision · order routing · exchange latency · broker feed
```

```text
Engineering publish latency ≠ Production trading performance
```

---

## 8. O-ADR — Decision 019（R5 · CLOSED）

见 `DECISIONS.md` **Decision 019 — Published State consumption boundary**。

摘要：

| Context Engine 输出 | 允许消费者 | 禁止 |
|---------------------|------------|------|
| `ContextState` | filter · risk modifier · monitoring | signal generation · position sizing alpha |

支撑未来 RC001-A 边界；本 Fill **不**授权 RC001。

---

## 9. F3 — Parity Protocol（unchanged · restated）

Batch historical replay vs streaming bar-by-bar；比较 **ContextState** only（Exact + confidence 6dp）。  
禁止：trade / PnL / strategy metrics。

---

## 10. F4 — Fault Injection（frozen）

| Fault ID | Expected |
|----------|----------|
| F-MISS missing bar | DEGRADED |
| F-DUP duplicate timestamp | INVALID |
| F-FUT future data | INVALID |
| F-ROLL rollover mismatch | INVALID |
| F-SESS session mismatch / cross-session fill | INVALID |

---

## 11. F5 — Evidence Mapping

| ID | Focus | Artifact |
|----|-------|----------|
| A1-E1 | Deterministic publish | parity / determinism |
| A1-E2 | Batch/Streaming parity | `parity_report.json` |
| A1-E3 | Fault handling | `fault_test_report.json` |
| A1-E4 | Publish latency | `latency_report.json` |
| A1-E5 | Reproduction | manifest + re-run |

---

## 12. F6 — Outcome Boundary

影响：**Engineering Readiness** only。  
不影响：K001 · Alpha · Trading · Candidate（须另授）。

---

## Appendix A — Fingerprints

| Symbol | manifest.json | dominant_windows.json | rollover_map.parquet |
|--------|---------------|----------------------|----------------------|
| rb | `bc62c8b606bf5c5018448e54aad841aa14a58f60482042f561e80f99ba8ed0fa` | `051e5b48154a2228ec4e06ed361d8ebed40ba20f2fccec8fc8c953f9a169929b` | `170102046bdbe339aad14de20a9f95463838da18b077fab10e54381102e92a8e` |
| i | `ea0c1aeeb40902a17beb9ae86ebb2f3313fd7199f546cea9ab05c4219ed46239` | `72302ce316c97de9b0448725180743fe7b21cfb66a6c8815f7f89f1567f2ced8` | `3eeedfcaa143ba6a1a698ccb033cae147a696446f1ecd1df2cdb9c293b9bf5ba` |
| MA | `04de9c86cfba8f2a18a3f908d2a5fa748d788dbc8f84a38129b878164321012f` | `9d448d120da2e7bd98cc0ae0a0faf7f3418c6985a58f23c032b1b7f412389109` | `e16a32be6565989629151f12ed1cd5706f6de4eb9d54c0c5809803bf3bbbe64d` |
| TA | `bff7e60648be96dc07671468e567aff6fc179b20dae820f2cc704c302f53867d` | `17ebac8a4e085b910fe07f50fb1fbe89c5e7f0d6ac6da0a362976f3766ed075e` | `86dff2a71b7a8226812d9c3b9932f53273579429b310034485849e46cb7466e7` |

---

## 13. Open Items

| ID | Status |
|----|--------|
| O-TAG | **CLOSED**（§4） |
| O-CONF | **CLOSED**（§5） |
| O-CLI | **CLOSED**（§6） |
| O-LAT | **CLOSED**（§7） |
| O-ADR | **CLOSED**（Decision 019） |

---

## 14. Fill checklist（v0.2）

| ID | Check | Verdict |
|----|-------|---------|
| AF1–AF6 | F1–F6 | **PASS** |
| AF7 | O-* closed | **PASS** |
| AF8 | Decision 019 referenced | **PASS** |
| AF9 | No Code/RC001 | **PASS** |

> Checklist PASS ≠ Confirmation PASS。

---

## 15. Next

```text
Confirmation PASS ✓
        ↓
Execution Authorization Review（Draft）
        ≠
Code / Observation / RC001（未经 Auth Confirmation + 显式指令）
```

当前：**Confirmation PASS**；Auth = Draft / **NONE**。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | Draft：F1–F6；O-* OPEN |
| 2026-07-21 | 0.2 | PASS WITH REVISION：O-* CLOSED；Decision 019 |
| 2026-07-21 | 0.2 | **Confirmation PASS** — Eligible for Execution Authorization |
