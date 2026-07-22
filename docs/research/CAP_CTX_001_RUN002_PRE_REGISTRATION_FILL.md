# CAP_CTX_001_RUN002 — Pre-Registration Fill Proposal v0.2

> **Type**: Governance Completion Document（Cross Evidence Fill）  
> **Status**: **Confirmation PASS** ✓ — Pre-Registration COMPLETE  
> **Version**: 0.2  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CAP_CTX_001_RUN002_PRE_REGISTRATION_FILL.md`  
> **Parent Spec**: [`CAP_CTX_001_RUN002_RUN_SPEC.md`](CAP_CTX_001_RUN002_RUN_SPEC.md) v0.2 **Review PASS**  
> **Parent Knowledge**: K001 (Qualified)  
> **Lineage**: `parent=CAP_CTX_001_RUN001`  
> **Prior Review**: v0.1 Fill Review PASS → v0.2 Confirmation PASS

### Review / Auth Boundary

```text
Fill v0.1 Review: PASS ✓
Fill v0.2 Confirmation: PASS ✓
O1–O5: CLOSED ✓
Pre-Registration: COMPLETE ✓
Execution Authorization: GRANTED WITH CONDITIONS ✓（见 Auth）
CP3: OPEN
Observation: NOT EXECUTED
K001 / Gate / RC001: unchanged by this document
```

**Auth**: [`CAP_CTX_001_RUN002_EXECUTION_AUTHORIZATION.md`](CAP_CTX_001_RUN002_EXECUTION_AUTHORIZATION.md) v1.0

### Boundary

```text
❌ Observation / Auth GRANTED
❌ Gate / RC001 / Alpha
❌ Discovery experiment framing
❌ Methodological tuning to favor K001 support
✅ Freeze RUN002 instance for Temporal OOS Cross Evidence
```

```text
RUN002 is not an independent discovery experiment.
It is a registered cross-evidence evaluation of K001.
```

### Cross Evidence Integrity Constraint（institutional）

```text
RUN002 shall not introduce any post-RUN001
methodological modification intended to improve
the probability of supporting K001.
```

Applies to RUN002 and subsequent Cross Evidence Runs: duty is to **test** Knowledge, not optimize design for confirmation.

---

## Review Response（相对 v0.1）

| Item | v0.2 |
|------|------|
| Single-variable (time only) | Confirmed |
| Protocol inheritance | Confirmed + citation string frozen |
| Open Items O1–O5 | CLOSED |
| Decision Mapping R2 | Frozen |
| Warmup | Excluded from all evaluation statistics |
| Integrity constraint | Added（above） |

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

### 1.1 Fingerprints（ceremony 2026-07-21 — existence only）

Same artifact identity files as RUN001 freeze（dataset unchanged on disk）：

| Symbol | manifest.json SHA256 | dominant_windows.json SHA256 | rollover_map.parquet SHA256 |
|--------|----------------------|------------------------------|-----------------------------|
| rb | `bc62c8b606bf5c5018448e54aad841aa14a58f60482042f561e80f99ba8ed0fa` | `051e5b48154a2228ec4e06ed361d8ebed40ba20f2fccec8fc8c953f9a169929b` | `170102046bdbe339aad14de20a9f95463838da18b077fab10e54381102e92a8e` |
| i | `ea0c1aeeb40902a17beb9ae86ebb2f3313fd7199f546cea9ab05c4219ed46239` | `72302ce316c97de9b0448725180743fe7b21cfb66a6c8815f7f89f1567f2ced8` | `3eeedfcaa143ba6a1a698ccb033cae147a696446f1ecd1df2cdb9c293b9bf5ba` |
| MA | `04de9c86cfba8f2a18a3f908d2a5fa748d788dbc8f84a38129b878164321012f` | `9d448d120da2e7bd98cc0ae0a0faf7f3418c6985a58f23c032b1b7f412389109` | `e16a32be6565989629151f12ed1cd5706f6de4eb9d54c0c5809803bf3bbbe64d` |

路径：`data/tq/rb` · `data/tq/i` · `data/tq/MA`。  
哈希变化 → 新 `run_id`。

---

## 2. Frozen Evaluation Universe

```text
rb, i, MA
```

（与 RUN001 相同；时间为主变量。）

### Coverage 2022-01 … 2023-12（dominant_windows month-starts）

| Symbol | Missing months | Status |
|--------|----------------|--------|
| rb | none | OK |
| i | none | OK |
| MA | none | OK |

**STOP rule（执行时）**：日历月零 bar → STOP + 新 run_id；禁止静默缩宇宙。长假 gap 仅披露。

---

## 3. Time Scope

| Item | Freeze |
|------|--------|
| Full | `2022-01-01` … `2023-12-31` |
| Period A | `2022-01-01` … `2022-12-31` |
| Period B | `2023-01-01` … `2023-12-31` |
| Warmup start | `2021-10-01` |
| vs RUN001 | Non-overlapping（RUN001 = 2024–2025） |

**Warmup rule**：`2021-10-01` … Full start 之前仅用于因果窗预热；**不进入** E1/E2/E3 或任何 Null 对照统计。

---

## 4. Observation / Evaluation / Null

**Protocol inheritance citation（Evidence 必须引用）**：

> Protocol inherited from CAP_CTX_001_RUN001 unless explicitly overridden by registered temporal scope.

| Item | Freeze |
|------|--------|
| M1 / M2 / W | realized vol / directional efficiency / 20 |
| Partition | causal_rolling_median_threshold，L=240 |
| E1 / E2 / E3 | same thresholds & order |
| N1 / N2 | iid_label_permutation / block_label_permutation(60)；200；seed 20240721 |

E1 = supporting only（definition coupling）。

唯一显式覆盖：temporal scope（§3）。

---

## 5. Decision Mapping（R2 — Frozen）

| Result | K001 Action |
|--------|-------------|
| Supported | Strengthen qualification |
| Partial | Narrow scope |
| Not supported | Downgrade |
| Infeasible | No upgrade |

`RUN002 PASS ≠ Gate PASS`。

---

## 6. Run Identity

| Field | Value |
|-------|-------|
| `run_id` | `CAP_CTX_001_RUN002` |
| `parent` | `CAP_CTX_001_RUN001` |
| `eq` | `EQ-CTX-002` |
| `spec_version` | `0.2` |
| `fill_version` | `0.2` |

---

## 7. Appendix A — Frozen Pre-Registration Record

| 项 | 值 |
|----|-----|
| Universe | rb, i, MA |
| Full window | 2022-01-01 … 2023-12-31 |
| Period A/B | 2022 / 2023 |
| Warmup | 2021-10-01（excluded from stats） |
| Protocol | Inherited from RUN001；override = temporal scope only |
| Integrity | No post-RUN001 methodological modification to favor K001 |
| Fingerprints | §1.1 |
| Coverage 2022–2023 | OK（§2） |
| K001 mapping | §5 |

Environment / Manifest：Auth 后、Observation 前写入（同 RUN001 C-ENV）。

---

## 8. Open Items

| ID | Item | Status |
|----|------|--------|
| O1 | Fingerprints | **CLOSED**（§1.1） |
| O2 | 2022–2023 coverage | **CLOSED**（§2） |
| O3 | Session / ns_utc | **CLOSED**（继承） |
| O4–O5 | E1/N2 strings | **CLOSED**（继承 RUN001） |

**无新增开放项。**

---

## 9. Next

```text
Fill Confirmation PASS ✓
  → Execution Authorization Review（另授；本文件不自动打开）
  →（另授）Observation
  → Evidence Review
  → K001 Strengthen / Narrow / Downgrade
```

**本 Fill ≠ Auth ≠ Observation。**

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | Draft Fill：2022–2023 OOS；指纹/覆盖；协议继承；R2 映射 |
| 2026-07-21 | 0.2 | Fill Review PASS → Confirmation PASS；Integrity Constraint；Warmup 排除统计；协议引用串 |
