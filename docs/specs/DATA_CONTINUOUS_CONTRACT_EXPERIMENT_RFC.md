# Continuous Contract Construction Experiment RFC（DATA_EXP001）

> **Status**: Accepted（Frozen for DATA_CONTINUOUS_CONTRACT_EXP001）
> **Accepted date**: 2026-07-19
> **Experiment family**: `DATA_CONTINUOUS_CONTRACT`
> **First run id**: `DATA_CONTINUOUS_CONTRACT_EXP001`
> **Path**: `docs/specs/DATA_CONTINUOUS_CONTRACT_EXPERIMENT_RFC.md`
> **Parent**: `docs/07_DATA_SPEC.md`、Decision 001
> **规则优先级**: `AGENTS.md` > Data Spec / Decision 001 > 本 RFC > 代码
> **实现门禁**: 本 RFC **已 Accepted**；仍禁止改正式基线 / 默认 loader；跑数须另授权。

本文件登记一次**独立数据实验**：审计冻结基线 **CbC 无复权** 的换月行为，及其对序列统计 / Feature 观测的影响。

**一句话**：实盘就是无复权——先验这把尺子在换月处会怎样；不找“更好的复权法”，更不改写 Decision 001。

**定位**：

```text
主线 = Method A：CbC unadjusted 换月 / 波动审计（实盘对齐）
辅线 = Method B/C：首跑不做（负对照推迟）
禁止 = 用复权替换正式基线，或用 PnL 选数据构造
```

---

## 0. 零假设（Null Hypothesis）

> H0：在冻结 CbC 无复权序列上，换月邻域的跳空 / 波动结构对全样本收益与 Feature 观测**无实质扭曲**（相对非换月时段）。

目的：

1. **刻画**无复权基线在换月处的真实行为（与实盘一致）；
2. **评估**这对 Feature 研究的威胁等级；
3. **保持** Decision 001；必要时强制换月标注 / 过滤，而不是改复权。

---

## 1. Objective

```text
分月 raw + rollover_map
        |
        v
Method A: CbC unadjusted
        |
        +-- roll-gap audit
        +-- return / vol around rolls (window W)
        +-- secondary: atr_ratio roll sensitivity
        |
        v
Artifact → Evaluation → Evidence
        |
        v
威胁等级 + 保持无复权基线的标注建议
```

成功标准（过程）：

1. 冻结基线不被替换。
2. Method A 有可复现 fingerprint 与换月事件清单。
3. Primary 指标只关于 A（换月 vs 非换月）。
4. Evidence 给出威胁等级与 Feature 标注建议。
5. 无交易信号、无策略回测验收。

---

## 2. Scope

### 2.1 In Scope

| 项 | 说明 |
|----|------|
| Method A 审计 | CbC 无复权：换月时刻、价差跳空、邻域收益/波动 |
| 换月事件可追溯 | 对齐 `rollover_map` |
| Feature 敏感性（secondary） | `atr_compression@1.0`：换月邻域 vs 非换月 |
| Artifact / Evidence | 可审计、append-only |

### 2.2 Out of Scope（首跑）

```text
Method B/C/D（后复权 / 比例复权 / Panama）— 推迟
替换 Decision 001 / docs/07_DATA_SPEC 基线
修改 tq_data_loader 默认路径
Trading / PnL / 策略回测
覆盖 ATR_COMPRESSION_EXP001
```

---

## 3. Identity（冻结）

| 字段 | 值 |
|------|-----|
| `experiment_id` | `DATA_CONTINUOUS_CONTRACT_EXP001` |
| Universe | `rb` / `1m` |
| Period | `2024-01-01` … `2025-12-31` |
| Primary method | `CbC_unadjusted` |
| Neighborhood W | `60` 根 1m bar（换月点前 W + 后 W） |
| Evidence subject | `subject_kind=dataset`，`subject_id=rb_cbc_unadjusted`，`subject_version=1.0` |

实现注记（DQ1）：Phase 实现允许 Evidence `SUBJECT_KINDS` 增加 `dataset`；在此之前可用 workflow 写入等价 metadata，但 Run Spec / Evidence 对外身份按上表冻结。

---

## 4. Method A — CbC Unadjusted

```text
分月 raw → rollover_map 切段拼接 → 价格不调整
换月跳空保留
```

路径：现有 `scripts/tq_rollover_data.py`（旁路审计，不改默认 loader 语义）。

---

## 5. Pre-registered Metrics

### 5.1 Primary（Method A only）

| Metric | 定义 |
|--------|------|
| Roll gap size | 每个换月点价格跳空（绝对价差与相对价差） |
| Roll-neighborhood vol | 换月邻域（前 W + 后 W）实现波动 vs 非换月时段 |
| Roll-neighborhood return | 换月邻域 log-return 极值 / 尾部占比 vs 非换月 |

### 5.2 Secondary

| Metric | 定义 |
|--------|------|
| Feature roll sensitivity | 同一 `atr_compression@1.0`（14/100）下，邻域 vs 非换月的 `atr_ratio` 分布距离 |

禁止：PnL 选优；事后改 W / 区间 / Primary。

报告数值与事件数 n；不设“通过则改基线”门禁。

---

## 6. Evidence Outcomes

`hypothesis_conclusion`：

```text
roll_effect_immaterial
roll_effect_material_annotate
inconclusive
```

Governance：`KEEP` / `REVERT` / `HOLD`。

| 结论 | 行动 |
|------|------|
| roll_effect_immaterial | 保持 Decision 001；换月处理可较弱 |
| roll_effect_material_annotate | **保持**无复权；Feature/Evaluation 强制换月标注或过滤 |
| inconclusive | HOLD |

**不存在**“改用复权基线”的晋级路径。

---

## 7. Open Questions — CLOSED

| ID | Accepted 决议 |
|----|---------------|
| DQ1 | Evidence：`subject_kind=dataset`，`subject_id=rb_cbc_unadjusted`，`subject_version=1.0`；实现可扩展 SUBJECT_KINDS |
| DQ2 | 首跑 **不启用** B/C；负对照整段推迟 |
| DQ3 | 随 DQ2 defer |
| DQ4 | Panama **不做** |
| DQ5 | 区间冻结 `2024-01-01`–`2025-12-31` |
| DQ6 | `atr_ratio` 敏感性进首跑，标 **secondary** |
| DQ7 | 仅 **rb** |
| DQ8 | 邻域窗口 **W=60**（1m bar；换月前 60 + 后 60） |

---

## 8. Freeze Criteria

- [x] DQ1–DQ8 关闭
- [x] 主线 Method A；B/C 非首跑
- [x] Primary 只关于 A
- [x] 不替换 Decision 001
- [x] 与实盘无复权语义一致
- [x] `docs/README.md` 已索引

---

## 9. Commit / Run Boundary

| Step | 内容 |
|------|------|
| 1 | 本 RFC Accepted |
| 2 | Run Spec `DATA_CONTINUOUS_CONTRACT_EXP001.md` |
| 3 | Method A 审计实现（不改默认 loader） |
| 4 | 用户明确「跑 DATA EXP001」后才执行 |

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-19 | 0.1.0-draft | 首版多构造对照 |
| 2026-07-19 | 0.2.0-draft | 主线改为 A；B/C 负对照 |
| 2026-07-19 | 1.0.0 | **Accepted**：DQ1–DQ8 关闭；W=60；仅 A；区间对齐 ATR EXP001 |
