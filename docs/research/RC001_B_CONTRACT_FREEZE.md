# RC001-B — Contract Freeze

> **Type**: Experiment Contract Freeze（≠ Execution · ≠ Implementation · ≠ Backtest）  
> **Status**: **APPROVED** ✓ · Contract **FROZEN**  
> **Version**: 0.1  
> **Date**: 2026-07-22  
> **Path**: `docs/research/RC001_B_CONTRACT_FREEZE.md`  
> **Authorization**: [`RC001_B_CONTRACT_FREEZE_AUTHORIZATION.md`](RC001_B_CONTRACT_FREEZE_AUTHORIZATION.md) — **GRANTED**  
> **Design**: [`RC001_B_ROUTING_DESIGN.md`](RC001_B_ROUTING_DESIGN.md) v0.1 **CONFIRMED**  
> **Confirmation**: [`RC001_B_DESIGN_CONFIRMATION.md`](RC001_B_DESIGN_CONFIRMATION.md) — **PASS**  
> **experiment_id（proposed）**: `RC001_B_EXP001`  
> **routing_policy**: **RP-RC001-B-v1**  
> **static_rule**: **SR-RC001-B-v1**

### Freeze Record（binding）

```text
================================================
RC001-B CONTRACT FREEZE v0.1

Verdict: APPROVED ✓
Contract: FROZEN ✓

Execution: GRANTED WITH CONDITIONS（Confirmation PENDING · C-BIND PENDING）
Code: NONE
Backtest: NONE

Unique experimental variable: Routing mechanism only
================================================
```

```text
Contract FROZEN
        ≠
Execution Authorization
        ≠
S1/S2 source files already chosen in this doc
（artifact binding = Pre-Execution gate · §1.2）
```

---

## 1. Strategy Identity Contract

### 1.1 Class freeze

| Role | Class | Environment hypothesis |
|------|-------|------------------------|
| **S1** | Trend-oriented（Breakout / Trend Following） | Suited to expansion-like conditions |
| **S2** | Non-trend / Mean-reversion / Range | Suited to compression-like conditions |

### 1.2 Artifact binding gate（FROZEN requirement）

Contract is **FROZEN** with mandatory fields. Concrete values **must be bound before Execution Authorization Confirmation** (Manifest / C-ENV package). Until bound, Execution Auth **cannot** PASS.

| Field | Requirement |
|-------|-------------|
| Strategy ID | frozen at bind |
| Version | frozen at bind |
| Source revision（git） | frozen at bind |
| Parameter set | frozen at bind |
| Content hash（SHA256 of source module(s)） | frozen at bind |
| Independence from Context | attested（no Context inside S1/S2） |
| Not newly designed for RC001-B | attested |
| Not selected by PnL ranking | attested |

```text
Binding package path（planned）:
  research/output/evidence/RC001_B_EXP001/strategy_identity_bind.json
```

### 1.3 Why binding is deferred to Pre-Execution

Current `strategies/` tree lacks a ready orthogonal frozen CTA pair meeting §1.1 without inventing new Alpha. Contract **forbids** inventing S1/S2 inside RC001-B. Binding selects **existing** modules/lineage at Execution prep — still **before** any Observation/Backtest.

```text
Context routing = unique variable
        ≠
Strategy selection experiment
```

---

## 2. Routing Policy Contract — **RP-RC001-B-v1**

### Input

```text
ContextState.v1 / A1-CTX-PS-v1.0.0
context_state ∈ {compression, expansion, invalid}
validity ∈ {VALID, DEGRADED, INVALID}
```

### Frozen mapping

```text
compression + VALID     →  ROUTE_S2（S2 only）
expansion   + VALID     →  ROUTE_S1（S1 only）
invalid OR DEGRADED OR INVALID validity → MONITOR_ONLY
```

### Forbidden remaps（without new experiment_id）

```text
❌ compression → S1
❌ expansion → S2
❌ invalid → auto-trade / ALLOW
❌ confidence × position / context score / edge ranking
```

---

## 3. Experiment Arms

### CTRL — **SR-RC001-B-v1**（static）

```text
Exclusive activation by calendar day（Asia/Shanghai）:
  even calendar day → S1 only
  odd  calendar day → S2 only
≡ Design “50/50 static allocation” without Context
```

### ROUTE

```text
ContextState → RP-RC001-B-v1 → ROUTE_S1 | ROUTE_S2 | MONITOR_ONLY
```

### Unique difference

```text
routing mechanism only
```

S1/S2 engines, parameters, costs, data, exits（per strategy）identical across arms.

---

## 4. Dataset / Cost / Execution assumptions

Aligned with RC001-A lineage for comparability（routing test ≠ data-edge test）.

| Item | Frozen |
|------|--------|
| Universe | **`rb` only**（Phase B；≠ multi-symbol claim） |
| Warmup | `2023-10-01` → eval start |
| Evaluation window | `2024-01-01` … `2025-12-31` |
| Data | TQ offline · 1m · CbC · unadjusted |
| rb fingerprints | Same as A1 / RC001-A Spec（must match at Execution） |
| Cost | Real commission + slippage；defaults locked at bind: `rate=1e-4` · `slippage=1.0` · `size` per strategy contract · capital `200_000` |
| Session | As in stitched TQ series（no ad-hoc rewrite） |
| Zero-cost primary | **Forbidden** |

Fingerprint table（rb）:

| Artifact | SHA256 |
|----------|--------|
| `manifest.json` | `bc62c8b606bf5c5018448e54aad841aa14a58f60482042f561e80f99ba8ed0fa` |
| `dominant_windows.json` | `051e5b48154a2228ec4e06ed361d8ebed40ba20f2fccec8fc8c953f9a169929b` |
| `rollover_map.parquet` | `170102046bdbe339aad14de20a9f95463838da18b077fab10e54381102e92a8e` |

---

## 5. Evaluation Contract

### Primary

| ID | Focus | Frozen intent |
|----|-------|---------------|
| **E1** Routing Quality | strategy–context mismatch / unsuitable activation | Compare mismatch rate CTRL vs ROUTE（Spec/Execution package freezes numeric gates） |
| **E2** Stability | route frequency · concentration · switching | Flag pathological concentration / flip storms |
| **E3** Attribution | improvement from Context routing vs S1/S2 alone | Must separate strategy edge from routing effect |

### Mismatch proxy（frozen definition）

```text
Mismatch event when active route is unsuitable:
  S1 active AND context_state == compression  → mismatch
  S2 active AND context_state == expansion      → mismatch
  MONITOR_ONLY                                 → not mismatch
  aligned pairs                                → not mismatch
```

### Secondary（not sole PASS criterion）

```text
PnL · Sharpe · Drawdown
```

### Anti-objectives

```text
❌ Maximize return/Sharpe as search goal
❌ Remap RP after peeking
❌ Change S1/S2 params mid-run
```

---

## 6. Outcome Boundary

| Outcome | Meaning |
|---------|---------|
| **PASS** | Routing evidence supported under frozen primary metrics |
| **PARTIAL** | Routing behavior observable；value limited / mixed |
| **FAIL** | No material routing benefit vs static |
| **INVALID** | Protocol / identity / Decision 019 / arm asymmetry broken |

```text
FAIL ≠ K001 false
FAIL ≠ Context useless
PASS ≠ Alpha
PASS ≠ Gate PASS / FULL Candidate / RC001 Accepted
rb-only ≠ multi-symbol capability
```

Numeric PASS/PARTIAL thresholds → Execution Manifest / Run Spec package（must not contradict this Contract）.

---

## 7. Attribution risk control（binding）

```text
Largest risk: mistaking S1/S2 differences for Context contribution
```

Therefore Execution package must freeze **together**:

```text
S1 · S2 · parameters · hashes
RP-RC001-B-v1
SR-RC001-B-v1
Dataset · cost · execution assumptions
Evaluation contract
```

---

## 8. Status / next gate

```text
K001: UNCHANGED
Gate: CONDITIONAL
Capability: NARROW
A1: COMPLETE
RC001-A: CLOSED / PARTIAL / NOT ACCEPTED
RC001-B: Contract FROZEN ✓
Execution: NONE
Implementation: NONE
Backtest: NONE
```

### Next legal entry

```text
Authorize RC001-B Execution Authorization
        ↓
GRANTED WITH CONDITIONS（see Execution Auth doc）
        ↓
Authorize RC001-B Execution Authorization Confirmation（另授）
```

Execution Auth: [`RC001_B_EXECUTION_AUTHORIZATION.md`](RC001_B_EXECUTION_AUTHORIZATION.md)

Expected flow after that Auth（still stepwise）:

```text
Execution Auth
      ↓
Manifest + C-ENV + strategy_identity_bind.json
      ↓
Implementation（if needed）
      ↓
Observation Authorization（if dual-gated）
      ↓
Backtest
      ↓
Evidence Review
      ↓
RC001 Decision
```

```text
≠ automatic return optimization
≠ CTA strategy development free-for-all
```

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-22 | 0.1 | **APPROVED / FROZEN** — RP/SR/Dataset/Eval/Outcome；S1/S2 artifact binding = Pre-Execution gate |
