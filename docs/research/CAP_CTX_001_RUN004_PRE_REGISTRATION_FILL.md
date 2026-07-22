# CAP_CTX_001_RUN004 — Pre-Registration Fill Proposal v0.2

> **Type**: Governance Completion Document（Observation Expansion Fill）  
> **Status**: **Confirmation PASS** ✓ — Pre-Registration COMPLETE  
> **Version**: 0.2  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CAP_CTX_001_RUN004_PRE_REGISTRATION_FILL.md`  
> **Parent Spec**: [`CAP_CTX_001_RUN004_RUN_SPEC.md`](CAP_CTX_001_RUN004_RUN_SPEC.md) v0.2 **Confirmation PASS**  
> **Parent Proposal**: [`CAP_CTX_001_PHASE33_OBSERVATION_EXPANSION_PROPOSAL.md`](CAP_CTX_001_PHASE33_OBSERVATION_EXPANSION_PROPOSAL.md)  
> **Parent Knowledge**: K001 (Strengthened Qualified)  
> **Governance**: [`CROSS_EVIDENCE_GOVERNANCE.md`](CROSS_EVIDENCE_GOVERNANCE.md) v1.2  
> **Lineage**: `parent=CAP_CTX_001_RUN003`  
> **Prior**: Draft v0.1 → Fill Review PASS → **Confirmation PASS**

### Review / Auth Boundary

```text
Spec: Confirmation PASS ✓
Fill Review: PASS ✓
Fill Confirmation: PASS ✓
F1–F6: PASS
O1–O5: CLOSED ✓
Pre-Registration: COMPLETE ✓
Execution Authorization: **GRANTED WITH CONDITIONS** ✓（CP3 OPEN）
Observation: NOT EXECUTED（见 Execution）
Family: Liquidity Structure FROZEN
K001 / Gate / RC001: unchanged
```

### Boundary

```text
❌ Observation executed
❌ Capability Candidate / Gate / RC001 / Alpha
❌ 失败后替换 Family 或改 M3 定义
✅ Freeze RUN004 Observation Expansion instance
```

### Claim Boundary（binding）

> RUN004 may provide Observation Family robustness evidence; it does **not** establish Capability Candidate status.

### Dataset Identity Statement

> Dataset fingerprint verifies identity of the registered universe and inherited protocol; **it does not constitute evaluation evidence.**

---

## Fill Review（2026-07-21）

| ID | Check | Verdict |
|----|-------|---------|
| F1 | §5 Governance Table 全字段 | PASS |
| F2 | Family = Liquidity Structure；非结果导向 | PASS |
| F3 | M3 定义可审计、固定 L=240 | PASS |
| F4 | E1_core / E1_family / E2 / E3 映射清晰 | PASS |
| F5 | Partition / Null / Universe / Time 冻结 | PASS |
| F6 | P3≠P4；失败不换 Family；Non-goals | PASS |

**Aggregate: PASS ✓ → Confirmation PASS ✓**

---

## 1. §5 Family Governance Table（frozen）

| 字段 | Fill |
|------|------|
| **Family** | **Liquidity Structure** |
| **Conceptual domain** | 市场参与强度 / 流动性供给相对水平（activity intensity），非价格路径波动、非方向效率 |
| **Difference from existing family** | Volatility = 收益波动幅度；Price = 价格路径几何效率；Liquidity = **成交活跃度相对近期基线** |
| **Why suitable for P3** | 检验描述结构是否依赖 Vol+Price 观察域；同冻结协议下加入独立描述域 |
| **Exclusion** | 单 Family + 单观测 M3；禁止调参 / 多指标竞赛 |
| **Failure interpretation** | Family 失败 → Narrow/Downgrade；**禁止**换 Family 重跑 |

### Selection criteria answers

| # | Answer |
|---|--------|
| 1 | Liquidity 相对 Vol/Price 独立（参与强度） |
| 2 | 测边界：失败暴露 Family 依赖，服务 Narrow |
| 3 | 概念域 + 单条注册观测；非特征堆叠 |

**Rejected**：Market Geometry；Order Flow（见 v0.1）。

---

## 2. Dataset Instance

| Item | Freeze |
|------|--------|
| Source | TQSDK Offline |
| Bar | 1m |
| Continuous | CbC |
| Adjustment | Unadjusted |
| Timezone | Asia/Shanghai |
| Universe | `rb`, `i`, `MA`, `TA` |
| Primary | `rb` |
| Transfer | `i`, `MA`, `TA` |

### 2.1 Fingerprints（RUN003 ceremony）

| Symbol | manifest.json | dominant_windows.json | rollover_map.parquet |
|--------|---------------|----------------------|----------------------|
| rb | `bc62c8b606bf5c5018448e54aad841aa14a58f60482042f561e80f99ba8ed0fa` | `051e5b48154a2228ec4e06ed361d8ebed40ba20f2fccec8fc8c953f9a169929b` | `170102046bdbe339aad14de20a9f95463838da18b077fab10e54381102e92a8e` |
| i | `ea0c1aeeb40902a17beb9ae86ebb2f3313fd7199f546cea9ab05c4219ed46239` | `72302ce316c97de9b0448725180743fe7b21cfb66a6c8815f7f89f1567f2ced8` | `3eeedfcaa143ba6a1a698ccb033cae147a696446f1ecd1df2cdb9c293b9bf5ba` |
| MA | `04de9c86cfba8f2a18a3f908d2a5fa748d788dbc8f84a38129b878164321012f` | `9d448d120da2e7bd98cc0ae0a0faf7f3418c6985a58f23c032b1b7f412389109` | `e16a32be6565989629151f12ed1cd5706f6de4eb9d54c0c5809803bf3bbbe64d` |
| TA | `bff7e60648be96dc07671468e567aff6fc179b20dae820f2cc704c302f53867d` | `17ebac8a4e085b910fe07f50fb1fbe89c5e7f0d6ac6da0a362976f3766ed075e` | `86dff2a71b7a8226812d9c3b9932f53273579429b310034485849e46cb7466e7` |

---

## 3. Registered Observations

| ID | Family | Definition |
|----|--------|------------|
| M1 | Volatility | realized vol，W=20，ddof=1 |
| M2 | Price | directional efficiency，W=20 |
| **M3** | **Liquidity Structure** | `volume_t / median(volume[t−L:t])`，L=240；prior 不含 t |

**Infeasible**：volume 不可用 / M3 样本不足 → INFEASIBLE；禁止改定义。

---

## 4. Time / Protocol

| Item | Freeze |
|------|--------|
| Full | 2024-01-01 … 2025-12-31 |
| Warmup | 2023-10-01（excluded） |
| Partition | causal_rolling_median_threshold on **M1**，L=240 |
| N1/N2 | seed 20240721；n_perm 200；block 60 |
| min_sample / min_runs | 5000 / 100 |

---

## 5. E1 / E2 / E3 Mapping

| Check | Mapping |
|-------|---------|
| E1_core | SMD_M1 vs N1 q95 |
| E1_family | SMD_M3 vs 同 N1 协议 |
| E2 | mean_run_length vs N2；`rb` |
| E3 | E1_core PASS on i ∧ MA ∧ TA；披露 E1_family |

| Result | Rule | Action |
|--------|------|--------|
| Supported | E1_core(rb) ∧ E2 ∧ E3 ∧ E1_family(rb) | STRENGTHEN |
| Partial | core 链过但 Family/transfer 不全 | NARROW |
| Not supported | E1_core(rb) 失败 | DOWNGRADE |
| Infeasible | coverage / M3 HOLD | NO_UPGRADE |

```text
P3 ≠ P4 · E1_family PASS ≠ Independence
```

---

## 6. Run Identity / Appendix A

| Field | Value |
|-------|--------|
| `run_id` | `CAP_CTX_001_RUN004` |
| `parent` | `CAP_CTX_001_RUN003` |
| `eq` | `EQ-CTX-004` |
| `expansion_family` | Liquidity Structure |
| `fill_version` | `0.2` |

| Appendix A | 值 |
|------------|-----|
| Universe | rb, i, MA, TA |
| Expansion | Liquidity Structure（M3） |
| Protocol | Inherited RUN001；override = Family only |
| Infeasible | no Family / metric substitution |

Evidence path：`research/output/evidence/CAP_CTX_001_RUN004/`

---

## 7. Next

```text
Fill Confirmation PASS ✓
        ↓
Execution Authorization
        ↓
Manifest + C-ENV →（显式指令）Observation
```

**Auth**: [`CAP_CTX_001_RUN004_EXECUTION_AUTHORIZATION.md`](CAP_CTX_001_RUN004_EXECUTION_AUTHORIZATION.md)

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | Draft：Liquidity Structure；M3；§5；E1_family |
| 2026-07-21 | 0.2 | Fill Review PASS + Confirmation PASS；Pre-Registration COMPLETE |
