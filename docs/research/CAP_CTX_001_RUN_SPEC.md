# CAP-CTX-001 Run Specification — v0.2

> **Type**: Capability Run Specification  
> **Status**: **Confirmation PASS** ✓ — Execution NOT AUTHORIZED  
> **Version**: 0.2  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CAP_CTX_001_RUN_SPEC.md`  
> **Campaign**: **CAP-CTX-001 — Promoted**（Controlled Research Object）  
> **Parent Spec**: [`CAPABILITY_EXPERIMENT_SPECIFICATION_CAP_CTX_001.md`](CAPABILITY_EXPERIMENT_SPECIFICATION_CAP_CTX_001.md) v0.2 Confirmation PASS  
> **Promote Decision**: [`CAP_CTX_001_PROMOTE_DECISION.md`](CAP_CTX_001_PROMOTE_DECISION.md) — **CONFIRM PROMOTE**（C1–C5 binding）  
> **Execution Auth**: [`CAP_CTX_001_EXECUTION_AUTHORIZATION.md`](CAP_CTX_001_EXECUTION_AUTHORIZATION.md)  
> **Gate**: BLOCKED（unchanged） · **RC001**: Review Passed / Not Accepted（unchanged）

### Review History

```text
v0.1 Review: PASS WITH REVISION
v0.2: R1–R2 applied
v0.2 Confirmation Review: PASS ✓
  R1 Dataset Fingerprint: Accepted
  R2 Pre-Registration Appendix: Accepted
  Time Scope Fingerprint / Run Manifest / CP3: Accepted
  Execution: NOT AUTHORIZED
  Observation: NOT GENERATED
```

### Positioning

```text
CAP-CTX-001 Promoted ✓
        ↓
Run Spec v0.2 Confirmation PASS ✓
        ↓
Execution Authorization Review
        ↓
（仅当 Auth GRANTED）CP3 Observation Authorization → Observation
```

### 本文不是

```text
❌ Detector / Feature Pipeline / 算法选型
❌ Context Engine / State Classifier / Signal / Strategy
❌ 跑数据 / 生成结果表
❌ Capability 已证实 / Gate PASS / RC001 Accepted
❌ 「最佳特征 / 核心变量 / 有效指标」叙事
```

### Binding Conditions（C1–C5）

| ID | 约束 |
|----|------|
| C1 | 只评估 Capability 是否存在；禁止宣称 Regime/Alpha/「市场状态已证明」 |
| C2 | Run Spec Confirmation PASS + Dataset Fingerprint 填死 + Pre-Registration 冻结后，才允许 Observation |
| C3 | Non-Goals 绑定（无 Engine / Classifier / Strategy / Optimization） |
| C4 | Evidence → Evaluation → Knowledge Candidate → Review；无自动 Knowledge |
| C5 | 不自动 Gate PASS / RC001 Accept / Alpha Research |

---

## 1. Run Identity

| 字段 | 值 |
|------|-----|
| `campaign_id` | `CAP-CTX-001` |
| `run_id`（执行前锁定） | 建议 `CAP_CTX_001_RUN001`（Confirmation PASS 时冻结） |
| `experiment_id`（入库时） | 与 `run_id` 对齐或一对一映射；Closed 不可改 |
| `parent` | Proposal v0.3 · Experiment Spec v0.2 · Promote Decision · 本 Run Spec 版本 |
| `eq` | EQ-CTX-001 |

### Run Objective

```text
Evaluate whether information in a pre-registered,
narrow observation set supports existence of persistent
and distinguishable market conditions across a frozen
initial evaluation universe — relative to Null baselines.
```

保持 **Capability Evaluation**，不是 Model Construction。  
**不是**：最优表示、建模型、交易、证明 Capability 为真。

---

## 2. Dataset Lock

### 2.1 Protocol（冻结基线）

| 项 | Lock |
|----|------|
| Source | TQSDK Offline |
| Bar | 1m |
| Continuous | CbC 自动换月 |
| Price | 无复权 |
| Cost fields | 存在性/换月意识 only；**不**评价 PnL |

权威：`docs/07_DATA_SPEC.md` / Decision 001。

### 2.2 Freeze Point（C2）

```text
Run Spec Confirmation PASS
        ↓
Dataset Fingerprint + Time Scope Fingerprint filled
        ↓
Pre-Registration Appendix frozen
        ↓
（仅此后）Observation Generation
        ↓
Evaluation
```

> Dataset scope must be frozen before any observation generation or evaluation.

Lock 后禁止改品种、区间、预注册度量。变更 → **新 `run_id`**。

### 2.3 Dataset Fingerprint（R1 — 强制）

执行前必须记录以下身份项；写入 Run Manifest 与 Evidence Artifact。

```text
Dataset Fingerprint

The following items must be recorded before execution:

- data source identifier
- contract universe definition
- continuous contract construction method
- adjustment policy
- timestamp convention
- missing data handling rule
- file checksum / version（manifest / parquet 指纹）
```

| Fingerprint 字段 | 本 Run 约定 / 填值时机 |
|------------------|------------------------|
| `data_source_id` | TQSDK Offline（Confirmation 确认） |
| `contract_universe` | 见 §3 Initial evaluation universe |
| `continuous_method` | CbC 自动换月（`docs/07_DATA_SPEC.md`） |
| `adjustment_policy` | 无复权 Unadjusted |
| `timestamp_convention` | Confirmation PASS 钉死（交易所本地 / bar 结束约定） |
| `missing_data_rule` | Confirmation PASS 钉死（跳过 / 前向限制等；禁止隐式填未来） |
| `file_checksum_or_version` | Execution 前写入；来自 `manifest.json` / 等价指纹 |

**原则**：`same research question + same data identity` 才可比较。  
Fingerprint 是 Evidence Artifact 的一部分，不是可选注释。

---

## 3. Instrument Universe — Initial Evaluation Universe

> **Initial evaluation universe** — 非「代表市场 / 全景结论」。

本 Run 目标是验证 Capability 是否存在，**不是**建立市场全景归纳。

| 角色 | Symbol | 目的 |
|------|--------|------|
| Primary | `rb` | E1 Separability + E2 Persistence |
| Transfer-1 | `i` | E3 Transfer |
| Transfer-2 | `ma` | E3 Transfer |

**Hold-out**：本 Run **不启用**。  
Confirmation 可改为 `ta` 替换 `ma`，必须在 Observation **之前**锁定。

禁止表述：本宇宙「代表中国商品期货市场」。

---

## 4. Time Scope Fingerprint

```text
Time Scope Fingerprint

Execution requires:

- start date
- end date
- timezone convention
- session filtering rule

After freeze:
no modification permitted.
```

| 切片 | 用途 | 状态 |
|------|------|------|
| Full window | 主评价样本 | Confirmation PASS 钉死 `start`/`end` |
| Period A | Stability | 预注册切分（前半或日历） |
| Period B | Stability | 预注册切分（后半或日历） |

### Lock 表（Confirmation PASS / Execution Auth 前填死）

| 字段 | 值 |
|------|-----|
| `timezone_convention` | _TBD_ |
| `session_filter` | _TBD_（日盘/夜盘/全时段） |
| `rb_start` / `rb_end` | _TBD_ |
| `i_start` / `i_end` | _TBD_（同日历窗策略） |
| `ma_start` / `ma_end` | _TBD_ |
| `period_A` | _TBD_ |
| `period_B` | _TBD_ |
| `roll_policy` | 披露 full；若度量受换月影响则双报 ex_roll |
| `dataset_fingerprint_ref` | 指向 §2.3 / Run Manifest |

日期与指纹在 **Observation 前**冻结；Draft/v0.2 修订阶段可留 `_TBD_`，但 **Execution Authorization 不得在 TBD 状态下授予**。

---

## 5. Observation Extraction Boundary

### 5.1 Candidate Observation Families（本 Run）

用语保持：**Candidate Observation Family**（禁止「最佳特征 / 核心变量 / 有效指标」）。

| Family | 本 Run |
|--------|--------|
| Volatility Structure | **In**（candidate） |
| Price Structure | **In**（candidate） |
| Liquidity Structure | **Out**（本 Run） |
| Market Geometry | **Out**（本 Run） |

收窄目的：控制复杂度，**不是**否定其他族。

### 5.2 Pre-registered candidate metrics（Confirmation 钉死）

少量、固定、**不可选优**。

| ID | Family | Metric（概念） | 用途 |
|----|--------|----------------|------|
| M1 | Volatility Structure | Realized volatility（固定窗长） | E1 分布对照 |
| M2 | Price Structure | Directional efficiency **或** return persistence（二选一钉死） | E1 分布对照 |

**禁止**：目录式展开后 selection；禁止根据结果更换 M1/M2。

### 5.3 Partition rule（概念）

```text
Pre-registered threshold partition on M1
（分位数 / 阈值 Confirmation 钉死）
```

- 分区标签仅为事后命名  
- **禁止**聚类搜索、HMM、分类器、多阈值网格  

---

## 6. Evaluation Procedure

顺序固定（不可反转）：

```text
E1 Separability（Existence）
        ↓
E2 Persistence（Stability）— 仅当 E1 相对 N1 支持可分
        ↓
E3 Transfer
```

| ID | 程序摘要 |
|----|----------|
| E1 | condition 分区下 M1/M2 分布 vs **N1** |
| E2 | 分区持续期 vs **N2** |
| E3 | Transfer 品种重复预注册规则；非孤立样本 |
| Secondary | Period A vs B；roll 邻域披露（若适用） |

### Out of evaluation

```text
❌ return predictability / hit-rate / PnL / Sharpe
❌ OPP / Detector / RC001
❌ 窗长/分位数/度量选优竞赛
```

数值门槛：见 Appendix A；早于 Observation；禁止跑后补。

---

## 7. Null Baseline Execution

| ID | 执行要点 |
|----|----------|
| N1 | 随机划分 / 保边际随机标签；重复次数预注册 |
| N2 | 时间打乱或标签重排持续期 |
| N3 | 仅 Primary 可分而 Transfer 不可分 → 不得宣称 general capability |

```text
Null baselines evaluate whether observed structure
exceeds simple random expectations.
They do not test whether markets are random.
```

`No Null comparison → No Capability claim`。

---

## 8. Falsification Mapping

| F | 触发（方向） | 出口候选 |
|---|--------------|----------|
| F1 | E1 不优于 N1 | K002 Candidate |
| F2 | E2 不优于 N2 | K002 / K003 Candidate |
| F3 | E3 无跨品种一致性 | K002 或 K004 Candidate |
| F4 | 仅孤立品种/时段 | K004 或 K002 Candidate |

Predictive failure ≠ Capability failure（C1）。

---

## 9. Evidence Artifacts

### 9.1 Run Manifest（强制产物）

```text
EvidenceRecord
        ↓
Run Manifest
        ↓
Dataset Fingerprint
        ↓
Evaluation Artifact
```

建议文件名：`CAP_CTX_001_RUN_MANIFEST.json`（或等价）

至少包含：

| 字段 | 说明 |
|------|------|
| `run_id` | |
| `spec_version` | 本 Run Spec 版本 |
| `dataset_fingerprint` | §2.3 全项 |
| `time_scope_fingerprint` | §4 |
| `pre_registration` | Appendix A 快照 |
| `parameters` | 预注册度量与门槛 |
| `execution_timestamp` | 执行开始时间（若已执行） |
| `environment_identity` | OS / Python / 关键库版本（若有脚本） |
| `code_revision` | git revision（若有） |

### 9.2 其他产物

| 产物 | 要求 |
|------|------|
| Evaluation | E1/E2/E3 vs Null；样本量；声明未做 predictive/PnL |
| EvidenceRecord | decision ∈ {KEEP, REVERT, HOLD}；引用 Run Manifest |
| Knowledge Candidate | K001–K004 草案 **仅** |
| Review | 人工后才可 Accepted Knowledge |

路径：`research/output/evidence/<experiment_id>/`（不在本阶段创建）。

---

## 10. Review Checkpoints

| CP | 名称 | 问题 |
|----|------|------|
| CP0 | Run Spec Review | 治理是否完整？（v0.1→v0.2） |
| CP1 | Dataset Lock | Fingerprint + Time Scope 是否填死？ |
| CP2 | Pre-Registration | Appendix A 是否冻结？ |
| **CP3** | **Observation Authorization Point** | 用户是否授权 **Observation Generation**？（≠「开始随便分析」） |
| CP4 | Post-Eval Review | Knowledge Candidate？Gate 复评？ |

```text
CP3 = Observation Authorization Point
（不是模糊的「开始分析」）
```

**CP3 之前禁止 Observation Generation。**

即使 Run Spec Confirmation PASS，也只表示：

```text
Experiment can be authorized for execution
≠
Capability exists
```

---

## 11. Scientific Claim Boundary（C1）

| 允许 | 禁止 |
|------|------|
| 评估 Context Capability 是否存在 | 证明市场存在状态 / 有效 Regime |
| vs Null 的可分/持续/迁移 Evidence | 发现 Alpha / 最佳特征 / 核心变量 |
| K002 Negative Evidence 有效 | Experiment → 自动 Conclusion |

---

## 12. Current Status

```text
Promote: ✓
Run Spec v0.2: Confirmation PASS ✓
Fill Proposal v0.2: Confirmation PASS ✓ · Pre-Registration COMPLETE
Execution Authorization: GRANTED WITH CONDITIONS
CP3: OPEN（Authorized）
Run Manifest: research/output/evidence/CAP_CTX_001_RUN001/CAP_CTX_001_RUN_MANIFEST.json
Observation executed: NO（待显式执行指令）
Evidence: NONE
Gate: BLOCKED
RC001: Review Passed / Not Accepted
```

---

## 13. Exit from Run Spec Stage

1. **Further Revise** — 改 Run Spec  
2. **Confirmation Review PASS** — ✓ 已达成（2026-07-21）  
3. **Fill Proposal Confirmation** — ✓ 已达成（v0.2）  
4. **Execution Authorization** — **GRANTED WITH CONDITIONS** — [`CAP_CTX_001_EXECUTION_AUTHORIZATION.md`](CAP_CTX_001_EXECUTION_AUTHORIZATION.md)  
5. **Observation** — CP3 OPEN；须满足 C-ENV 后另授实现  
6. **Park**

**当前默认**：Execution **GRANTED WITH CONDITIONS**；CP3 **OPEN**；Observation **未**执行；Gate/RC001 不变。

---

## Appendix A — Pre-Registration Record（Synced from Fill Proposal v0.2）

> 权威实例以 [`CAP_CTX_001_PRE_REGISTRATION_FILL_PROPOSAL.md`](CAP_CTX_001_PRE_REGISTRATION_FILL_PROPOSAL.md) **v0.2 §9** 为准（**Confirmation PASS**）。  
> 下表为同步副本。改字段 → 新 `run_id`。

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
| Period A / B | `2024` / `2025` |
| Timezone / storage | Asia/Shanghai calendar；`ns_utc` |
| Session | all bars in CbC 1m stream |
| Dataset fingerprints | Fill Proposal §1.2（SHA256 ceremony 2026-07-21） |
| Lineage | OPP16_EXP001 period = provenance reference only |

### A.3 Observation Families & Metrics

| 项 | 值 |
|----|-----|
| Families in | Volatility Structure, Price Structure |
| Families out | Liquidity, Market Geometry |
| M1 | `M1_realized_volatility`, W=20（descriptive only） |
| M2 | `M2_directional_efficiency`, W=20（descriptive only） |
| Partition | `causal_rolling_median_threshold`, L=240 |

### A.4 Evaluation Order（冻结）

```text
E1 → E2 → E3
```

| 项 | 值 |
|----|-----|
| E1 | `SMD_M1` > N1 q95；min 5000/label |
| E2 | mean_run_length > N2 q95；min_runs 100 |
| E3 | E1 Pass on i and MA |

### A.5 Null Baselines（冻结）

| 项 | 值 |
|----|-----|
| N1 | iid_label_permutation；200；seed 20240721 |
| N2 | block_label_permutation；block=60；200；seed 20240721 |
| N3 | isolated-sample check |

### A.6 Falsification Mapping（冻结引用）

| F | → Knowledge Candidate path |
|---|------------------------------|
| F1 | K002 |
| F2 | K002 / K003 |
| F3 | K002 / K004 |
| F4 | K004 / K002 |

### A.7 Environment（Auth 后、Observation 前补齐）

| 项 | 值 |
|----|-----|
| `code_revision` | _TBD until Auth GRANTED_ |
| `environment_identity` | _TBD until Auth GRANTED_ |
| Run Manifest path | `CAP_CTX_001_RUN_MANIFEST.json` |

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | Draft：Run Objective；Dataset Lock；Universe；Eval/Null；Checkpoints |
| 2026-07-21 | 0.2 | R1 Dataset Fingerprint；R2 Pre-Registration；Time Scope；Run Manifest；CP3 |
| 2026-07-21 | 0.2.1 | Confirmation PASS 归档；链接 Execution Authorization Review |
| 2026-07-21 | 0.2.2 | Sync Appendix A from Fill Proposal v0.2 |
| 2026-07-21 | 0.2.3 | Fill Confirmation PASS；Execution Auth GRANTED WITH CONDITIONS；CP3 OPEN |
