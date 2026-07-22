# CAP_CTX_001_RUN003 — Pre-Registration Fill Proposal v0.2

> **Type**: Governance Completion Document（Cross-sectional Fill）  
> **Status**: **Confirmation PASS** ✓ — Pre-Registration COMPLETE  
> **Version**: 0.2  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CAP_CTX_001_RUN003_PRE_REGISTRATION_FILL.md`  
> **Parent Spec**: [`CAP_CTX_001_RUN003_RUN_SPEC.md`](CAP_CTX_001_RUN003_RUN_SPEC.md) v0.2 **Confirmation PASS**  
> **Parent Knowledge**: K001 (Strengthened Qualified)  
> **Governance**: [`CROSS_EVIDENCE_GOVERNANCE.md`](CROSS_EVIDENCE_GOVERNANCE.md) v1.2  
> **Lineage**: `parent=CAP_CTX_001_RUN002`  
> **Prior Review**: v0.1 Fill Review PASS → v0.2 **Confirmation PASS**

### Review / Auth Boundary

```text
Fill v0.1 Review: PASS ✓
Fill v0.2 Confirmation: PASS ✓
F1–F5: PASS
O1–O5: CLOSED ✓
Pre-Registration: COMPLETE ✓
Execution Authorization: **GRANTED WITH CONDITIONS** ✓（CP3 OPEN）
Observation: NOT EXECUTED
K001 / Gate / RC001: unchanged
```

### Boundary

```text
❌ Observation executed
❌ Gate / RC001 / Alpha / K001 Decision
❌ 替换 expansion instrument（若不可行 → Infeasible，非换品种）
✅ Freeze RUN003 Cross-sectional instance
```

```text
RUN003 changes Universe only.
Expansion instrument = pre-registered validation object, not optimization pick.
```

### Infeasibility rule（Confirmation 绑定）

若 ceremony 或执行时 expansion instrument（`TA`）不满足 coverage / 连续性：

```text
Result = INFEASIBLE
        ≠
replace TA with another symbol
```

换品种须新 `run_id` + 新 Spec/Fill。

### Dataset Identity Statement（Review 建议；绑定 Fill）

> Dataset fingerprint verifies identity of the registered expanded universe and inherited protocol; **it does not constitute evaluation evidence.**

RUN003 为首次 Universe 扩展；指纹/覆盖 ceremony 仅确认**数据身份与注册实例**，不是实验结果。

---

## Review Response（Fill Review 2026-07-21）

| ID | Check | Verdict |
|----|-------|---------|
| F1 | Expansion instrument `TA` frozen | PASS |
| F2 | Expanded universe = initial + expansion | PASS |
| F3 | E3 transfer: i, MA, TA | PASS |
| F4 | Time = execution condition 2024–2025 | PASS |
| F5 | Coverage failure → INFEASIBLE；禁止换品种 | PASS |

---

## 1. Dataset Instance

| Item | Freeze |
|------|--------|
| Source | TQSDK Offline |
| Bar | 1m |
| Continuous | CbC |
| Adjustment | Unadjusted |
| Timezone calendar | Asia/Shanghai |
| Storage datetime | ns_utc（manifest `_meta`） |
| Session | all bars in CbC 1m stream |

### 1.1 Fingerprints（ceremony 2026-07-21）

| Symbol | Role | manifest.json | dominant_windows.json | rollover_map.parquet |
|--------|------|---------------|----------------------|----------------------|
| rb | primary | `bc62c8b6…ed0fa` | `051e5b48…9929b` | `17010204…2a8e` |
| i | transfer | `ea0c1aee…6239` | `72302ce3…ced8` | `3eeedfcaa…f5ba` |
| MA | transfer | `04de9c86…012f` | `9d448d12…9109` | `e16a32be…be64d` |
| **TA** | **expansion** | `bff7e606…867d` | `17ebac8a…075e` | `86dff2a7…66e7` |

完整 SHA256：

| Symbol | manifest.json | dominant_windows.json | rollover_map.parquet |
|--------|---------------|----------------------|----------------------|
| rb | `bc62c8b606bf5c5018448e54aad841aa14a58f60482042f561e80f99ba8ed0fa` | `051e5b48154a2228ec4e06ed361d8ebed40ba20f2fccec8fc8c953f9a169929b` | `170102046bdbe339aad14de20a9f95463838da18b077fab10e54381102e92a8e` |
| i | `ea0c1aeeb40902a17beb9ae86ebb2f3313fd7199f546cea9ab05c4219ed46239` | `72302ce316c97de9b0448725180743fe7b21cfb66a6c8815f7f89f1567f2ced8` | `3eeedfcaa143ba6a1a698ccb033cae147a696446f1ecd1df2cdb9c293b9bf5ba` |
| MA | `04de9c86cfba8f2a18a3f908d2a5fa748d788dbc8f84a38129b878164321012f` | `9d448d120da2e7bd98cc0ae0a0faf7f3418c6985a58f23c032b1b7f412389109` | `e16a32be6565989629151f12ed1cd5706f6de4eb9d54c0c5809803bf3bbbe64d` |
| TA | `bff7e60648be96dc07671468e567aff6fc179b20dae820f2cc704c302f53867d` | `17ebac8a4e085b910fe07f50fb1fbe89c5e7f0d6ac6da0a362976f3766ed075e` | `86dff2a71b7a8226812d9c3b9932f53273579429b310034485849e46cb7466e7` |

路径：`data/tq/rb` · `data/tq/i` · `data/tq/MA` · `data/tq/TA`。  
rb/i/MA 与 RUN001 Fill 一致；TA 为 expansion 新增指纹。

---

## 2. Frozen Evaluation Universe（O1）

### Initial evaluation universe（frozen baseline）

```text
rb (primary), i, MA (transfer)
```

### Expansion instrument（frozen）

```text
TA
```

> One pre-registered instrument **outside** initial universe `{rb, i, MA}`.

### Expanded evaluated universe

```text
rb, i, MA, TA
```

**唯一主变量**：+1 expansion instrument（`TA`）。  
**禁止**：执行时替换为其他品种。

### Coverage 2024-01 … 2025-12

| Symbol | Missing months | n_bars_full | Status |
|--------|----------------|-------------|--------|
| rb | none | 165765 | OK |
| i | none | 165765 | OK |
| MA | none | 165765 | OK |
| TA | none | 165765 | OK |

**STOP rule**：日历月零 bar → STOP / INFEASIBLE + 新 `run_id`；**禁止**静默换品种。

---

## 3. Time Scope（O4 — execution condition）

```text
Time window 2024–2025 is a registered execution condition
inherited from RUN001 protocol,
not an experimental variable of RUN003.
```

| Item | Freeze |
|------|--------|
| Full | `2024-01-01` … `2025-12-31` |
| Period A / B | 2024 / 2025 |
| Warmup start | `2023-10-01` |
| Warmup | excluded from E1/E2/E3 and Null stats |

Temporal OOS：**不由本 Run 复测**（RUN002 已覆盖）。

---

## 4. Observation / Evaluation / Null（protocol identity）

> Protocol inherited from CAP_CTX_001_RUN001 unless explicitly overridden by registered universe scope.

| Item | Freeze |
|------|--------|
| M1 / M2 / W | realized vol / directional efficiency / 20 |
| Partition | causal_rolling_median_threshold，L=240 |
| E1 | all symbols in expanded universe |
| E2 | primary `rb` only |
| E3 | **Expanded Universe transfer evaluation**（§5） |
| N1 / N2 | iid_label_permutation / block_label_permutation(60)；200；seed 20240721 |

E1 = supporting only（definition coupling）。

---

## 5. E3 Expanded Universe Transfer List（O3）

```text
E3 evaluates whether the registered condition structure
remains supported across the expanded universe.
```

| Role | Symbols | E3 requirement |
|------|---------|----------------|
| Primary | `rb` | E1 Pass required for E2/E3 chain |
| Transfer（initial） | `i`, `MA` | E1 Pass |
| Transfer（expansion） | `TA` | E1 Pass |

**E3 supported** iff E1 PASS on **every** transfer symbol: `i`, `MA`, `TA`.

```text
E3 is NOT "TA-only evaluation".
Failure on any transfer member → Partial / Not supported per pre-registered mapping.
```

---

## 6. Decision Mapping（O5 — frozen）

| Result | K001 Action |
|--------|-------------|
| Supported | Strengthen（Knowledge Review 另授） |
| Partial | Narrow scope |
| Not supported | Downgrade |
| Infeasible | No upgrade |

`RUN003 PASS ≠ Gate PASS ≠ Capability Candidate`

---

## 7. Run Identity

| Field | Value |
|-------|-------|
| `run_id` | `CAP_CTX_001_RUN003` |
| `parent` | `CAP_CTX_001_RUN002` |
| `eq` | `EQ-CTX-003` |
| `evidence_type` | Cross-sectional |
| `spec_version` | `0.2` |
| `fill_version` | `0.2` |

---

## 8. Appendix A — Frozen Pre-Registration Record（Proposed）

| 项 | 值 |
|----|-----|
| Initial universe | rb, i, MA |
| Expansion instrument | **TA** |
| Expanded universe | rb, i, MA, TA |
| Full window | 2024-01-01 … 2025-12-31 |
| Warmup | 2023-10-01（excluded from stats） |
| Protocol | Inherited RUN001；override = universe only |
| E3 transfer list | i, MA, TA |
| Fingerprints | §1.1 |
| Coverage 2024–2025 | OK（§2） |
| Infeasible policy | no symbol substitution |
| K001 mapping | §6 |

Manifest + C-ENV：Auth 后、Observation 前。

---

## 9. Open Items

| ID | Item | Status |
|----|------|--------|
| O1 | Expansion instrument `TA` | **CLOSED**（§2） |
| O2 | Fingerprints + coverage | **CLOSED**（§1.1 / §2） |
| O3 | E3 expanded-universe list | **CLOSED**（§5） |
| O4 | Time = execution condition | **CLOSED**（§3） |
| O5 | Decision mapping / Appendix A | **CLOSED**（§6 / §8） |

**无新增开放项。**

---

## 10. Next

```text
Fill Confirmation PASS ✓
Execution Authorization: GRANTED WITH CONDITIONS ✓
  → Run Manifest + C-ENV
  →（另授）Authorize Observation Execution for CAP_CTX_001_RUN003
```

**Auth**: [`CAP_CTX_001_RUN003_EXECUTION_AUTHORIZATION.md`](CAP_CTX_001_RUN003_EXECUTION_AUTHORIZATION.md)

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | Draft Fill：TA frozen；指纹/覆盖；E3；Infeasible 不换品种 |
| 2026-07-21 | 0.1.1 | Fill Review PASS；Dataset Identity Statement |
| 2026-07-21 | 0.2 | Fill Confirmation PASS；Pre-Registration COMPLETE |
