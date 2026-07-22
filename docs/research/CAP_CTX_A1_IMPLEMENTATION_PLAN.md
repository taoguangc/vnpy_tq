# CAP_CTX_A1 — Implementation Plan（v0.1 · Authorized）

> **Type**: Implementation Scope Freeze（≠ Observation · ≠ A1 validated）  
> **Status**: **Authorized** — Implementation Authorization **GRANTED** · code present · Obs **NOT GRANTED**  
> **Version**: 0.1  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CAP_CTX_A1_IMPLEMENTATION_PLAN.md`  
> **Auth**: [`CAP_CTX_A1_EXECUTION_AUTHORIZATION.md`](CAP_CTX_A1_EXECUTION_AUTHORIZATION.md) — Confirmation PASS · CP3 **OPEN** · Impl Auth **GRANTED**  
> **Manifest**: `research/output/evidence/CAP_CTX_A1/CAP_CTX_A1_RUN_MANIFEST.json` — **C-ENV SATISFIED** · `implementation_authorized=true`  
> **Fill**: [`CAP_CTX_A1_PRE_REGISTRATION_FILL.md`](CAP_CTX_A1_PRE_REGISTRATION_FILL.md) Confirmation PASS  
> **ADR**: Decision 019

### Status（binding）

```text
================================================
CAP_CTX_A1_IMPLEMENTATION_PLAN v0.1

CP3: OPEN ✓
Manifest + C-ENV: SATISFIED ✓

Implementation Authorization: GRANTED ✓
Observation Authorization: NOT GRANTED
Code: PRESENT（context_engine/）
Smoke: PASS（synthetic batch==streaming）

Purpose: freeze directories + module boundaries; realize frozen Spec/Fill only
================================================
```

```text
Code creation ≠ Experiment execution
Implementation complete ≠ A1 validated
```

---

## 1. Deliverables（Implementation Authorization GRANTED）

| Deliverable | Path / entry | Status |
|-------------|--------------|--------|
| Validate CLI | `python -m context_engine.validate_a1 --manifest <path>` | **Present**（writes Evidence only if Obs Auth） |
| Publisher core | `context_engine/` | **Present** |
| Batch + streaming publish | same `context_version` | **Present** · smoke parity OK |
| Fault harness | F-MISS … F-SESS | **Present** |
| Latency probe | bar_close → publish only | **Present** |
| Evidence writers | `research/output/evidence/CAP_CTX_A1/` 六件套 + C-LINEAGE | **Wired** · **not run**（Obs blocked） |
| Smoke | `scripts/test_context_engine_a1_smoke.py` | **PASS** |

### Directory（realized）

```text
context_engine/
  __init__.py
  __main__.py              # → validate_a1
  validate_a1.py
  schema.py                # ContextState.v1
  publisher.py             # batch + streaming
  faults.py
  latency.py
  evidence_io.py

research/output/evidence/CAP_CTX_A1/
  CAP_CTX_A1_RUN_MANIFEST.json   # exists · impl authorized
  context_schema.json            # Auth Obs 后
  parity_report.json
  fault_test_report.json
  latency_report.json
  evidence_record.json
```

**禁止**新建策略 / OPP detector / 回测入口作为 A1 交付物。

---

## 2. C-IMPL / C-NO-SEMANTIC-UPGRADE（binding）

```text
Implementation may realize only frozen A1 Spec + Fill.

Forbidden:
  changing ContextState semantics
  adding trading-oriented fields
  forward-looking features
  changing detector definitions beyond Fill publish rules
  upgrading compression|expansion|invalid → regime|alpha|signal
```

主标签发布规则（Fill）：

```text
invalid | compression | expansion
```

---

## 3. Two authorization gates（must remain separate）

| Gate | Allows | Does not allow |
|------|--------|----------------|
| **Implementation Authorization** | Write engineering code per this Plan | Observation / Evidence PASS claim |
| **Observation Authorization** | Run validate_a1 · produce Evaluation/Evidence | Claiming A1 PASS without Review |

```text
Implementation Authorization ✓
        ↓
code exists ✓
        ≠
A1 validated
        ↓
Observation Authorization ← CURRENT WAIT
        ↓
artifacts
        ↓
Evidence Review
```

---

## 4. Out of scope until A1 Evidence Review PASS + 另授

```text
❌ RC001
❌ Context Filter Backtest
❌ Strategy / Alpha 优化
❌ Gate auto PASS / Candidate auto
❌ CONTEXT_ENGINE_SPEC silent MarketState expansion
```

---

## 5. Next

```text
Explicit Observation Authorization
        ↓
python -m context_engine.validate_a1 --manifest <path>
        ↓
Evidence Review
```

当前：**Implementation GRANTED + code present**；**Observation NOT AUTHORIZED**。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | Draft：目录冻结；双授权点；C-IMPL 重申 |
| 2026-07-21 | 0.1 | Impl Auth **GRANTED**；`context_engine/` 落地；smoke PASS；Obs 另授 |
