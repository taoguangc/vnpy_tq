# CAP-CTX-001 Pre-Registration Fill Proposal v0.1

> **Type**: Governance Completion Document（非执行、非选优）  
> **Status**: Draft — awaiting Review  
> **Version**: 0.1  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CAP_CTX_001_PRE_REGISTRATION_FILL_PROPOSAL.md`  
> **Parent**: Run Spec v0.2 Confirmation PASS · Execution Auth **NOT GRANTED**  
> **Purpose**: 将 Template → **Frozen Run Instance** 建议值，清除 B1–B4；**不**打开 CP3

### 本文不是

```text
❌ Execution / Observation Generation
❌ 按结果选日期 / 选品种
❌ 调参 / 换 M1·M2 / 改 Null / 改 E 顺序
❌ Capability 结论 / Gate / RC001 变更
```

### 允许

```text
✅ 建议冻结值
✅ 检查完整性与歧义
✅ 标出 Open Items（须用户确认或冻结仪式采集）
```

### 选用原则（反选优）

| 原则 | 应用 |
|------|------|
| Lineage over curiosity | 时间窗优先对齐已有 Closed Evidence 区间，而非「找好看区间」 |
| Fixed over searched | 窗长/分位一次选定，不网格 |
| Causal over hindsight | 分区规则避免用全样本未来中位数贴历史标签 |
| Open over invented | checksum / 数据覆盖以实测为准，不编造 |

---

## 0. Mapping to Blocking Items

| Blocking | 本 Proposal 覆盖 |
|----------|------------------|
| B1 | §1 Dataset + §3 Time Scope |
| B2 | §1.2 Checksum（Open Item：冻结仪式采集） |
| B3 | §4–§7 Observation / Eval / Null / run_id |
| B4 | §2 Frozen evaluation universe |

---

## 1. Dataset Instance Proposal

### 1.1 Data source

| 项 | Proposed freeze |
|----|-----------------|
| `data_source_id` | TQSDK Offline（Decision 001 / `docs/07_DATA_SPEC.md`） |
| Bar | 1m |
| Path pattern | `data/tq/{prefix}/`（rb / i / ma） |

### 1.2 Contract construction

| 项 | Proposed freeze |
|----|-----------------|
| Continuous method | CbC 自动换月（`rollover_map` 驱动） |
| Adjustment policy | **无复权** Unadjusted |
| Roll awareness | 评价披露 full；若 M1/M2 受跳空影响则双报 `ex_roll`（Feature 换月政策指针） |

### 1.3 Timestamp convention

| 项 | Proposed freeze |
|----|-----------------|
| Timezone | `Asia/Shanghai`（交易所本地日历） |
| Bar clock | 1m bar 的 `datetime` = 该分钟区间标识（与现有 TQ parquet / vn.py 加载约定一致；冻结仪式写明所用 loader） |
| Missing data rule | **不**前向填充跨 session；缺失分钟不参与 M1/M2 更新；不跨日虚构 bar |

### 1.4 Checksum / version（B2）

| 项 | Proposed freeze |
|----|-----------------|
| `file_checksum_or_version` | **Open Item O1** — 冻结仪式对各品种 `manifest.json`（及所用 parquet 集合）记录版本号或内容哈希 |
| 禁止 | 用「文件名相同」代替 checksum |

> Checksum 在 **Fill Proposal Review PASS 后、Execution Auth 重新申请前** 采集；采集过程**不得**计算 E1/E2/E3 或查看 Capability 结果。

---

## 2. Evaluation Universe Proposal（B4）

升级用语：

```text
Initial evaluation universe  →  Frozen evaluation universe（本 Run）
```

| 角色 | Symbol | 状态 |
|------|--------|------|
| Primary | `rb` | **Proposed frozen** |
| Transfer-1 | `i` | **Proposed frozen** |
| Transfer-2 | `ma` | **Proposed frozen** |
| Hold-out | — | none（本 Run） |

**声明**：本宇宙仅为本 Run 的 Frozen evaluation universe，**不**代表「全市场」。  
替换 `ma`→`ta` 仅允许在本 Proposal Review 阶段；一旦写入 Appendix A 并 Auth，不得因结果更换。

**Open Item O2**：冻结仪式确认 `data/tq/rb|i|ma` 在拟时间窗内数据可用（存在性检查，非评价）。

---

## 3. Time Scope Proposal（B1）

### 3.1 Full window

| 项 | Proposed freeze | 理由（非选优） |
|----|-----------------|----------------|
| `start` | `2024-01-01` | 与 Closed `OPP16_EXP001` 区间对齐（Evidence Lineage），非因回报挑选 |
| `end` | `2025-12-31` | 同上 |
| Calendar | 三品种使用**同一日历窗** | Transfer 可比 |

> 若 O2 发现某品种覆盖不足 → **缩短至三品种交集**并记录于 Manifest；禁止只对「表现好」的品种加长窗。

### 3.2 Period A / B（Stability）

| 切片 | Proposed freeze |
|------|-----------------|
| Period A | `2024-01-01` … `2024-12-31` |
| Period B | `2025-01-01` … `2025-12-31` |

### 3.3 Session

| 项 | Proposed freeze |
|----|-----------------|
| `session_filter` | **全部可用 session**（日盘+夜盘，凡 1m CbC 流中存在的 bar） |
| 理由 | 避免事后剔除「不利 session」；与 Domain `Session` 枚举兼容但不按 session 分层本 Run |

**Open Item O3**：若 loader 默认丢弃夜盘，须在 Manifest 显式记录实际 session 集合（仍不得按结果裁剪）。

---

## 4. Observation Registration（B3）

### 4.1 Families（本 Run）

| Family | Status |
|--------|--------|
| Volatility Structure | **registered (in)** |
| Price Structure | **registered (in)** |
| Liquidity Structure | out |
| Market Geometry | out |

### 4.2 M1 — registered

| 字段 | Proposed freeze |
|------|-----------------|
| Name | `M1_realized_volatility` |
| Family | Volatility Structure |
| Definition | 对 log return \(r_t=\ln(C_t/C_{t-1})\)，在窗 \(W\) 内样本标准差 |
| Window \(W\) | **20**（1m bars） |
| Update | 每 bar 因果更新；不足 \(W\) 有效 return → 不产出 M1（不填充） |

### 4.3 M2 — registered

| 字段 | Proposed freeze |
|------|-----------------|
| Name | `M2_directional_efficiency` |
| Family | Price Structure |
| Definition | \( \mathrm{DE}_t = \lvert C_t - C_{t-W}\rvert / \sum_{i=0}^{W-1}\lvert C_{t-i}-C_{t-i-1}\rvert \)（分母为 0 则不产出） |
| Window \(W\) | **20**（与 M1 同窗，减少自由度，非联合优化） |
| Update | 因果；不足窗 → 不产出 |

**禁止**本阶段改 M1/M2 定义或窗长。若发现定义歧义 → Open Item，不静默改写。

### 4.4 Partition rule — registered

| 字段 | Proposed freeze |
|------|-----------------|
| Rule | 因果尾部中位数：令 \(m_t=\mathrm{median}(M1_{t-L},\ldots,M1_{t-1})\)；若 \(M1_t > m_t\) → 标签 `HIGH_VOL`，否则 `LOW_VOL` |
| Lookback \(L\) | **240**（1m bars） |
| 不足 \(L\) 个有效 M1 | 不贴标签（不参与 E1/E2） |
| 命名 | 事后标签 only；**不是**预测方向 |

选用因果中位数而非全窗中位数，避免用未来样本定义过去状态。

---

## 5. Evaluation Registration（B3）

顺序冻结（不可改）：

```text
E1 → E2 → E3
```

### 5.1 E1 Separability — registered

| 项 | Proposed freeze |
|----|-----------------|
| Sample | Primary `rb`；有标签 bar |
| Statistic | 两标签下 M1 与 M2 的分布差异（预注册：对 M1、M2 分别计算；主报告以 **M1** 为准，M2 为并列披露） |
| 建议度量 | 标准化均值差 \(\lvert\mu_H-\mu_L\rvert/s_{\mathrm{pool}}\)（或等价可复算统计量；实现时写入 Manifest 精确公式） |
| Pass vs N1 | 观测统计量 > N1 零分布的 **95%** 分位（单侧「更大可分」） |
| min sample | 每标签至少 **5000** 个有效 1m bar（不足 → HOLD / 不宣称 E1） |

### 5.2 E2 Persistence — registered

| 项 | Proposed freeze |
|----|-----------------|
| Gate | **仅当 E1 vs N1 支持可分** 才执行正式 E2 结论；否则 E2 记为 `skipped` |
| Statistic | 标签 run length（连续同标签 bar 数）的均值 |
| Pass vs N2 | 观测均值 > N2 零分布 **95%** 分位 |
| min runs | 至少 **100** 段 run（不足 → HOLD） |

### 5.3 E3 Transfer — registered

| 项 | Proposed freeze |
|----|-----------------|
| Apply | 同一 M1/M2/分区规则于 `i`、`ma` |
| Criterion | 在 Transfer 品种上，E1 vs N1 至少 **2/2** 品种同向支持可分；否则不得宣称 general capability（→ K004/K002 路径） |
| Persistence on transfer | 披露性；不额外放宽阈值 |

Secondary：Period A/B 分别披露 E1 统计量（不改变主结论阈值）。

---

## 6. Null Baseline Registration（B3）

| ID | Proposed freeze |
|----|-----------------|
| N1 | 保标签随机重贴 `HIGH_VOL`/`LOW_VOL` 标签（打乱标签、保持计数）；重复 **200** 次；固定种子写入 Manifest |
| N2 | 时间块打乱或整段标签序列循环移位（预注册实现名写入 Manifest）；重复 **200** 次；固定种子 |
| N3 | 若仅 `rb` 过 E1 而 `i`/`ma` 未过 → isolated；不得 general claim |

```text
Null = 是否超过简单随机结构
≠ 市场是否随机
```

**禁止**本阶段改重复次数或 Null 方法以「更容易过」。

---

## 7. Run Identity Proposal

| 项 | Proposed freeze |
|----|-----------------|
| `run_id` | `CAP_CTX_001_RUN001` |
| `campaign_id` | `CAP-CTX-001` |
| `spec_version` | `0.2` |
| `fill_proposal_version` | `0.1` |
| `experiment_id`（入库） | `CAP_CTX_001_RUN001`（一对一） |

一旦 Auth GRANTED 并开始 Observation，`run_id` 不可改；变更 → 新 run。

---

## 8. Open Items

| ID | Item | 关闭条件 |
|----|------|----------|
| O1 | Dataset checksum / manifest version | 冻结仪式采集，写入 Appendix A / Manifest |
| O2 | 三品种时间窗数据存在性 | 仅覆盖检查；不足则缩窗至交集并记录 |
| O3 | Loader 实际 session 集合 | Manifest 如实记录 |
| O4 | E1 精确统计量公式字符串 | Review 钉死一种可复算定义 |
| O5 | N2 精确打乱算法名 | Review 钉死 |

O1–O5 **关闭前**不得申请 Execution Authorization GRANTED。  
关闭 O1–O5 **不等于**自动 Auth — 须重新提交 Execution Authorization Review。

---

## 9. Completeness Checklist（相对 B1–B4）

| Blocking | Proposal 状态 |
|----------|----------------|
| B1 Dataset/Time Fingerprint | 值已建议；O1/O3 待采集 |
| B2 Checksum | **Open — O1** |
| B3 Run/Eval freeze | 值已建议；O4/O5 待钉公式字符串 |
| B4 Universe | **Proposed frozen** rb/i/ma；O2 待存在性 |

---

## 10. Next Governance Path

```text
Pre-Registration Fill Proposal v0.1
        ↓
Review（PASS / PASS WITH REVISION / REJECT）
        ↓
（PASS 后）关闭 O1–O5（冻结仪式，无 Evaluation）
        ↓
写入 Run Spec Appendix A（实例）
        ↓
Re-submit Execution Authorization Review
        ↓
（若 GRANTED）CP3 Observation Authorization
```

**本文件通过 ≠ Execution Authorized ≠ Observation。**

---

## 11. Current Status Snapshot

```text
CAP-CTX-001          PROMOTED ✓
Run Spec             Confirmation PASS ✓
Execution Auth       NOT GRANTED
CP3                  CLOSED
Blocking             B1–B4（本 Proposal 建议填值中）
Observation          NONE
Evidence             NONE
```

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | Draft：B1–B4 建议冻结值；Lineage 时间窗；因果分区；Open Items O1–O5 |
