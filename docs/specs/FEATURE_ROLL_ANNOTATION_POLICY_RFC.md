# Feature Roll Neighborhood Annotation Policy RFC

> **Status**: Accepted（Frozen for new Feature experiments）
> **Accepted date**: 2026-07-19
> **Doc id**: `FEATURE_ROLL_ANNOTATION_POLICY`
> **Path**: `docs/specs/FEATURE_ROLL_ANNOTATION_POLICY_RFC.md`
> **Parent Evidence**: `EV-DATA-CONTINUOUS-CONTRACT-EXP001-RUN002`
> **Parent conclusion**: `roll_effect_material_annotate` / governance `HOLD`
> **规则优先级**: `AGENTS.md` > Decision 001 / `docs/07_DATA_SPEC.md` > 本 RFC > Feature Run Spec > 代码
> **实现门禁**: Accepted 后约束**新** Feature 实验。不改默认 loader；本 RFC **不**授权跑数 / 交易。共享标注工具须另开实现切片。

**一句话**：无复权基线不变；换月邻域必须先标清楚，再谈 Feature 结论。

---

## 0. Why（为什么需要）

DATA EXP001（RUN002）在 `rb` / 1m / CbC 无复权上发现：换月邻域相对非换月时段存在可度量结构差异（如 `vol_ratio≈2.56`，`gap_abs_mean≈44`）。

结论是 **annotate / filter for research**，不是改复权：

| 允许 | 禁止 |
|------|------|
| 标注换月邻域 | 用复权替换 Decision 001 基线 |
| Evaluation 预注册并**双报** `full` + `ex_roll` | 静默丢掉换月 bar 却不写进 Spec |
| 主次结论在 Run Spec 标明 | 把换月跳空当 Alpha 晋级依据 |
| 多品种扩展审计（另开实验） | 改写 DATA/ATR EXP001 产物 |

---

## 1. Scope

### 1.1 In Scope（Accepted）

适用于 **新** Feature Sensor 实验（新 `experiment_id`），在正式 Evaluation / Evidence 阶段：

1. 必须定义换月邻域与标注字段；
2. 必须预注册并报告 `full` 与 `ex_roll`（主次在 Run Spec 标明）；
3. 结论表述须区分「含换月」与「剔换月」。

### 1.2 Out of Scope

```text
改 Decision 001 / 默认 tq_data_loader
复权主连作为正式研究基线
交易信号 / 策略回测验收
回溯改写 ATR EXP001 / DATA EXP001
强制改写已 Closed 实验的 Evidence
```

ATR EXP001 已 Closed：其 `rollover_flag` 诊断口径保留为历史；**新实验**对齐本 RFC，不得原地改 EXP001。

---

## 2. Frozen Defaults（已冻结）

| 项 | 冻结值 | 来源 / RQ |
|----|--------|-----------|
| 价格序列 | CbC **无复权** | Decision 001 |
| 邻域宽度 `W` | **60**（换月前 60 + 后 60 根 **1m** bar） | DATA EXP001 DQ8；**RQ2** |
| 偏离 `W` | 允许，但须在 Run Spec 写理由 | RQ2 |
| 换月时刻 | `rollover_map` / 合约 `yymm` 切换对齐 | DATA EXP001 Method A |
| gap 口径（若引用） | old close → **new open** | DATA EXP001 RUN002 |
| 合成 K 邻域 | 任一成分 **1m** 落在邻域内 → 该合成 bar 标为邻域 | **RQ3**（保守） |

---

## 3. Layer Rules（分层责任）

| 层 | 必须 | 禁止 |
|----|------|------|
| **Sensor / Artifact** | 写出可审计标注（见 §4） | 因换月静默 `drop` 观测 |
| **Evaluation** | 预注册并计算 `full` 与 `ex_roll`（见 §5） | 跑完后再决定是否剔换月 |
| **Evidence** | 写明主次样本口径与换月处理 | 用剔换月后的好看结果假装全样本 |
| **Loader / Baseline** | 保持无复权 | 为「曲线好看」切换复权 |

---

## 4. Annotation Contract（标注契约）

每个 Feature Artifact 行（或等价审计表）至少满足其一：

**A. 行级诊断（推荐）**

| diagnostics / 字段 | 类型 | 含义 |
|--------------------|------|------|
| `roll_neighborhood` | `"true"` / `"false"` | 该 bar 是否落在任一换月邻域（W）内 |
| `roll_event_id`（可选） | string | 所属换月事件 id；非邻域可空 |

**B. 实验级掩码 Artifact（允许）**

单独产出 `roll_mask` / 事件清单 Artifact，Manifest 引用；Evaluation 用同一 `content_hash` 对齐。

Sensor **不**因 `roll_neighborhood=true` 删除行；过滤只发生在预注册的 Evaluation。

---

## 5. Evaluation Reporting Minimum（报告下限 · RQ1）

新 Feature 实验的 Evaluation / Evidence **必须双报**：

| 样本 | 定义 |
|------|------|
| `full` | 含换月邻域 |
| `ex_roll` | 剔除 `roll_neighborhood=true`（或等价掩码） |

并满足：

1. Run Spec **标明主结论**用 `full` 还是 `ex_roll`（另一套为敏感性 / 对照）；
2. 报告换月邻域样本占比（或被 `ex_roll` 排除的占比）；
3. 声明 `W` 与事件来源；
4. **禁止**仅在叙事中写「已考虑换月」而无字段 / 掩码 / 预注册 Metric。

本 RFC **不**规定具体相关 / 效应量阈值；那属于各 Feature 实验自己的 Outcome/Metric。

---

## 6. Relationship to DATA EXP001

| 项 | 状态 |
|----|------|
| DATA EXP001 | **Closed**；不得改写 |
| 本 RFC | 落实其 `roll_effect_material_annotate` 建议 |
| Decision 001 | **Unchanged** |
| 多品种是否同脏 | **未证实**；扩展须新 `DATA_*` 实验 |

---

## 7. Closed Questions（RQ1–RQ5）

| ID | 决议 | 日期 |
|----|------|------|
| RQ1 | **强制双报** `full` + `ex_roll`；主次在 Run Spec 标明 | 2026-07-19 |
| RQ2 | **`W=60` 全局默认**；偏离须在 Run Spec 写理由 | 2026-07-19 |
| RQ3 | 合成 K：**任一成分 1m 落邻域即标**（保守） | 2026-07-19 |
| RQ4 | **写入** `docs/07_DATA_SPEC.md` §3.1 指针 | 2026-07-19 |
| RQ5 | **不回溯** Closed 实验；仅约束新 `experiment_id` | 2026-07-19 |

---

## 8. Enforcement

Accepted 之后：

- 新 Feature Run Spec 缺换月标注预注册或缺双报计划 → **不得**进入 Evaluation 授权；
- 共享工具位于 `strategies/paaf/data_audit/roll_annotation.py`；仅生成标注 / 合成 K 聚合，不过滤样本；
- 本 RFC **不**授权跑数、不改变 Decision 001、不授权交易。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-19 | 0.1.0-draft | 首稿：落实 DATA EXP001 annotate 建议；RQ1–RQ5 待关 |
| 2026-07-19 | 1.0.0 | Accepted：RQ 全按建议关闭；约束新 Feature 实验 |
| 2026-07-19 | 1.0.1 | 记录共享标注工具实现位置；政策语义不变 |
