# CAP-CTX-001 Pre-Registration Fill Proposal v0.2

> **Type**: Governance Completion Document（Frozen Run Instance）  
> **Status**: **Confirmation PASS** ✓ — Pre-Registration COMPLETE  
> **Version**: 0.2  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CAP_CTX_001_PRE_REGISTRATION_FILL_PROPOSAL.md`  
> **Parent**: Run Spec v0.2 Confirmation PASS · Execution Auth → 见 Re-review 文档  
> **Prior Review**: v0.1 PASS WITH REVISION → v0.2 O1–O5 closed → **Confirmation PASS**

### Review / Auth Boundary

```text
Fill Proposal v0.2 Confirmation: PASS ✓
O1–O5: CLOSED ✓
Pre-Registration: COMPLETE ✓
Execution Authorization: see CAP_CTX_001_EXECUTION_AUTHORIZATION.md
CP3 / Observation: 见 Auth 结论（本文件不自动打开）
```

### 本文不是

```text
❌ Execution / Observation / E1–E3 计算
❌ 按结果选日期 / 品种 / 窗长
❌ Capability 结论 / Gate / RC001 变更
❌ 自动授予 Execution Authorization
```

---

## Review Response（相对 v0.1）

| 项 | v0.2 处理 |
|----|-----------|
| Dataset / No Adjustment | 保持；Fingerprint 实例写入 §1 / Appendix A |
| Universe | Frozen rb / i / **MA**（路径 `data/tq/MA`）；O2 覆盖关闭 |
| Time Scope | 保持；Lineage = **provenance reference only**（§3） |
| M1/M2 | 强化：descriptive observations only（§4） |
| Partition | 完整因果 / rolling / warmup 冻结串（§4.4） |
| Null N2 | 命名算法冻结（§6，O5） |
| E1 formula | 精确字符串冻结（§5，O4） |
| O1–O5 | §8 **Closed** |

---

## 1. Dataset Instance（Frozen）

| 项 | Freeze |
|----|--------|
| `data_source_id` | TQSDK Offline（Decision 001 / `docs/07_DATA_SPEC.md`） |
| Bar | 1m |
| Continuous | CbC（`rollover_map.parquet`） |
| Adjustment | **Unadjusted / 无复权** |
| Timezone display | `Asia/Shanghai` 日历解释 |
| Storage datetime | `datetime_unit = ns_utc`（manifest `_meta`） |
| Missing data | 不跨 session 前向填充；缺失分钟不更新 M1/M2；不虚构 bar |

### 1.1 Session / loader（O3 Closed）

| 项 | Freeze |
|----|--------|
| Session policy | 使用 CbC 1m 流中**全部存在的 bar**（日盘+夜盘，凡数据中有则纳入） |
| Day-session note（provenance） | TQSDK 1m：日盘最后 bar 为 14:59 CST；无 15:00 bar（manifest `session_note`） |
| Loader identity | 执行时须使用与仓库 TQ parquet 加载一致的 loader；名称与 revision 写入 Run Manifest（Observation 前） |
| 禁止 | 事后按「结果」剔除 session |

### 1.2 Dataset Fingerprint（O1 Closed — ceremony 2026-07-21）

存在性/身份采集；**未**计算 Capability 评价。

| Symbol dir | Resolved path | `manifest.json` SHA256 | `dominant_windows.json` SHA256 | `rollover_map.parquet` SHA256 |
|------------|---------------|------------------------|--------------------------------|-------------------------------|
| rb | `C:\projects\vnpy_tq\data\tq\rb` | `bc62c8b606bf5c5018448e54aad841aa14a58f60482042f561e80f99ba8ed0fa` | `051e5b48154a2228ec4e06ed361d8ebed40ba20f2fccec8fc8c953f9a169929b` | `170102046bdbe339aad14de20a9f95463838da18b077fab10e54381102e92a8e` |
| i | `C:\projects\vnpy_tq\data\tq\i` | `ea0c1aeeb40902a17beb9ae86ebb2f3313fd7199f546cea9ab05c4219ed46239` | `72302ce316c97de9b0448725180743fe7b21cfb66a6c8815f7f89f1567f2ced8` | `3eeedfcaa143ba6a1a698ccb033cae147a696446f1ecd1df2cdb9c293b9bf5ba` |
| MA | `C:\projects\vnpy_tq\data\tq\MA` | `04de9c86cfba8f2a18a3f908d2a5fa748d788dbc8f84a38129b878164321012f` | `9d448d120da2e7bd98cc0ae0a0faf7f3418c6985a58f23c032b1b7f412389109` | `e16a32be6565989629151f12ed1cd5706f6de4eb9d54c0c5809803bf3bbbe64d` |

| Extra | Value |
|-------|-------|
| `fingerprint_ceremony_date` | `2026-07-21` |
| `fingerprint_algo` | SHA256 of listed files |
| Windows path note | `data/tq/ma` 解析到 `data/tq/MA`；冻结目录名为 **`MA`** |

若任一哈希在 Auth/执行前变化 → **新 `run_id`**，禁止静默沿用。

---

## 2. Frozen Evaluation Universe（B4 / O2 Closed）

```text
Frozen evaluation universe（本 Run）:
  rb, i, MA
```

**不是**「代表全市场」。

### Coverage existence（O2）

| Symbol | dominant_windows span | Target `2024-01-01`…`2025-12-31` month-starts missing |
|--------|----------------------|------------------------------------------------------|
| rb | 2020-01-10 → 2026-07-06 | **0** |
| i | 2015-12-29 → 2026-07-07 | **0** |
| MA | 2020-01-11 → 2026-07-06 | **0** |

### Incomplete coverage rule（若执行加载后发现缺口）

```text
IF continuous 1m stream for any frozen symbol lacks bars
   required for the frozen calendar window
   beyond pre-registered tolerance:
THEN
   do NOT silently drop the symbol from universe;
   STOP evaluation for this run_id;
   emit Evidence HOLD / process note;
   require new run_id with revised universe or window.
```

Tolerance（freeze）：日历窗内连续缺口 **> 1 个完整交易日**（按该品种实际交易日历）即触发 STOP。  
**禁止**事后缩减为「rb+i」却仍声称原 universe。

---

## 3. Time Scope（Frozen）

| 项 | Freeze |
|----|--------|
| Full start | `2024-01-01` |
| Full end | `2025-12-31` |
| Period A | `2024-01-01` … `2024-12-31` |
| Period B | `2025-01-01` … `2025-12-31` |
| Calendar alignment | 三品种同一日历窗 |

### Lineage note（强制）

```text
Alignment with OPP16_EXP001 period is a provenance reference only.

It is NOT validation evidence.
It does NOT mean “OPP16 performed well, therefore choose this window.”
```

---

## 4. Observation Registration（Frozen）

### 4.0 Role statement（强制）

```text
M1/M2 are descriptive observations used for
condition characterization only.

They are input measurements — not candidate predictors,
not trading signals, and not alpha features.
```

### 4.1 Families

| Family | Status |
|--------|--------|
| Volatility Structure | in |
| Price Structure | in |
| Liquidity / Market Geometry | out（本 Run） |

### 4.2 M1

| 字段 | Freeze |
|------|--------|
| `id` | `M1_realized_volatility` |
| Definition string | `M1_t = stdev({ln(C_i/C_{i-1}) for i=t-W+1..t})` using sample stdev (ddof=1); require W finite positive returns |
| `W` | `20` |
| Warmup | 有效 return 数 `< W` → M1 缺失（不填充） |

### 4.3 M2

| 字段 | Freeze |
|------|--------|
| `id` | `M2_directional_efficiency` |
| Definition string | `M2_t = abs(C_t - C_{t-W}) / sum_{i=0..W-1} abs(C_{t-i} - C_{t-i-1})`；分母为 0 → 缺失 |
| `W` | `20` |
| Warmup | 价格点不足 → 缺失 |

### 4.4 Partition Definition（Closed — 原技术开放项）

```text
Partition Definition

All partition thresholds must be calculated
using information available before timestamp t.
No future observations are permitted.

Algorithm name: causal_rolling_median_threshold

For each bar t with valid M1_t:
  Let S_t = { M1_{t-L}, M1_{t-L+1}, ..., M1_{t-1} }
       (only finite M1 values; do not impute)
  If |S_t| < L:
       emit NO label (warmup / insufficient history)
  Else:
       m_t = median(S_t)   # rolling window, length L, causal
       if M1_t > m_t: label = HIGH_VOL
       else:            label = LOW_VOL

Parameters:
  L = 240
  median = ordinary sample median of S_t
  expanding median: FORBIDDEN for this run
  full-sample median: FORBIDDEN for this run

Warmup policy:
  Bars without label are excluded from E1/E2/E3 samples.
```

标签仅为 condition 命名，**不是**方向预测。

---

## 5. Evaluation Registration（O4 Closed）

Order（immutable）：`E1 → E2 → E3`

### 5.1 E1 formula string（Frozen）

```text
E1_primary_metric_id = SMD_M1

For labels H=HIGH_VOL, L=LOW_VOL on Primary rb:
  nH, nL = counts of labeled bars
  muH, muL = mean(M1 | H), mean(M1 | L)
  sH2, sL2 = variance(M1 | H), variance(M1 | L)  # ddof=1
  pooled = sqrt( ((nH-1)*sH2 + (nL-1)*sL2) / (nH+nL-2) )
  SMD_M1 = abs(muH - muL) / pooled
  If nH+nL-2 < 1 or pooled == 0: E1 = INFEASIBLE → HOLD

Pass rule vs N1:
  SMD_M1 > quantile_95(SMD_M1 under N1 permutations)

Secondary disclosure (not pass gate):
  Same SMD on M2 (SMD_M2) reported alongside; does not replace SMD_M1.

min_sample_per_label = 5000
```

### 5.2 E2

```text
E2_metric = mean_run_length of label sequence on rb
Pass: mean_run_length > quantile_95(N2 null distribution)
Gate: formal E2 conclusion only if E1 Pass; else E2=skipped
min_runs = 100
```

### 5.3 E3

```text
Apply identical M1/M2/partition to i and MA.
General capability claim requires E1 Pass on both transfer symbols (2/2).
Else → K004/K002 candidate path (isolated / negative).
```

---

## 6. Null Baseline Registration（O5 Closed）

| ID | Freeze string |
|----|----------------|
| N1 | `algorithm=iid_label_permutation`；保持 HIGH/LOW **计数不变**，随机重贴标签；`n_perm=200`；`rng_seed=20240721` |
| N2 | `algorithm=block_label_permutation`；将标签序列切成长度 `block_size_bars=60` 的块（末块可短），随机重排块顺序；`n_perm=200`；`rng_seed=20240721` |
| N3 | isolated-sample check：仅 Primary E1 Pass 而 Transfer 未达 2/2 → 不得 general claim |

```text
Null baselines evaluate whether observed structure
exceeds simple random expectations.
They do not test whether markets are random.
```

**禁止**将 N2 写作含糊的 `shuffle`。  
N1 ≠ N2：N1 打乱标签（破坏持续结构）；N2 块置换（保留块内局部持续、破坏块间位置）。

---

## 7. Run Identity

| 项 | Freeze |
|----|--------|
| `run_id` | `CAP_CTX_001_RUN001` |
| `experiment_id` | `CAP_CTX_001_RUN001` |
| `campaign_id` | `CAP-CTX-001` |
| `spec_version` | `0.2` |
| `fill_proposal_version` | `0.2` |

---

## 8. Open Items — Closure Status

| ID | Status | Closure evidence |
|----|--------|------------------|
| O1 | **CLOSED** | §1.2 SHA256 fingerprints |
| O2 | **CLOSED** | §2 coverage table + incomplete-coverage STOP rule |
| O3 | **CLOSED** | §1.1 session policy + manifest `session_note` / `ns_utc` |
| O4 | **CLOSED** | §5.1 `SMD_M1` formula string |
| O5 | **CLOSED** | §6 `iid_label_permutation` / `block_label_permutation` |

---

## 9. Appendix A — Frozen Pre-Registration Record（Final for RUN001）

> 设计先于结果。写入后改任何字段 → **新 `run_id`**。

### A.1 Identity & Universe

| 项 | 值 |
|----|-----|
| `run_id` | `CAP_CTX_001_RUN001` |
| `campaign_id` | `CAP-CTX-001` |
| `spec_version` | `0.2` |
| `fill_proposal_version` | `0.2` |
| Frozen evaluation universe | `rb`, `i`, `MA` |
| Hold-out | none |

### A.2 Time & Data Identity

| 项 | 值 |
|----|-----|
| Full | `2024-01-01` … `2025-12-31` |
| Period A / B | `2024` / `2025` calendar years |
| Timezone / storage | Asia/Shanghai calendar；store `ns_utc` |
| Session | all bars present in CbC 1m stream |
| Dataset fingerprints | §1.2 table |
| Lineage | OPP16_EXP001 period = **provenance reference only** |

### A.3 Observation

| 项 | 值 |
|----|-----|
| Families in | Volatility, Price |
| M1 | `M1_realized_volatility`, W=20（§4.2） |
| M2 | `M2_directional_efficiency`, W=20（§4.3） |
| Partition | `causal_rolling_median_threshold`, L=240（§4.4） |
| Role | descriptive observations only |

### A.4 Evaluation

| 项 | 值 |
|----|-----|
| Order | E1 → E2 → E3 |
| E1 | `SMD_M1` vs N1 q95；min 5000/label（§5.1） |
| E2 | mean_run_length vs N2 q95；min_runs 100（§5.2） |
| E3 | E1 Pass on i **and** MA（§5.3） |

### A.5 Null

| 项 | 值 |
|----|-----|
| N1 | iid_label_permutation；200；seed 20240721 |
| N2 | block_label_permutation；block=60；200；seed 20240721 |
| N3 | isolated-sample rule |

### A.6 Falsification

| F | Path |
|---|------|
| F1–F4 | 同 Run Spec / Experiment Spec（K002/K003/K004 candidates） |

### A.7 Environment

| 项 | 值 |
|----|-----|
| `code_revision` | _fill at Auth GRANTED, before Observation_ |
| `environment_identity` | _fill at Auth GRANTED, before Observation_ |
| Run Manifest | `CAP_CTX_001_RUN_MANIFEST.json` |

---

## 10. Next Governance Path

```text
Fill Proposal v0.2
        ↓
Confirmation Review（本文件）
        ↓
Sync Appendix A into Run Spec（若 Confirmation PASS）
        ↓
Execution Authorization Re-review
        ↓
（仅当 GRANTED）CP3 Observation Authorization
```

**Fill v0.2 ≠ Execution Authorized ≠ Observation。**

---

## 11. Status Snapshot

```text
CAP-CTX-001 PROMOTED ✓
Run Spec v0.2 Confirmation PASS ✓
Fill Proposal v0.2 Confirmation PASS ✓
Pre-Registration COMPLETE ✓
Execution Auth → see CAP_CTX_001_EXECUTION_AUTHORIZATION.md
```

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | Draft：B1–B4 建议值；Open Items O1–O5 |
| 2026-07-21 | 0.2 | 关闭 O1–O5；指纹/覆盖；因果分区；E1/N2 冻结串；Appendix A Final |
| 2026-07-21 | 0.2.1 | Confirmation PASS 归档；Pre-Registration COMPLETE |
