# Multi-Symbol Continuous Contract Roll Audit RFC（DATA_EXP002）

> **Status**: Accepted（Frozen for `DATA_CONTINUOUS_CONTRACT_EXP002`）
> **Accepted date**: 2026-07-19
> **Experiment family**: `DATA_CONTINUOUS_CONTRACT`
> **Run id**: `DATA_CONTINUOUS_CONTRACT_EXP002`
> **Path**: `docs/specs/DATA_MULTI_SYMBOL_ROLL_EXPERIMENT_RFC.md`
> **Parent**: `docs/07_DATA_SPEC.md`、Decision 001、`DATA_CONTINUOUS_CONTRACT_EXPERIMENT_RFC.md`
> **Prior Evidence**: `EV-DATA-CONTINUOUS-CONTRACT-EXP001-RUN002`（rb；`roll_effect_material_annotate`）
> **规则优先级**: `AGENTS.md` > Decision 001 > Parent RFC > 本 RFC > 代码
> **实现门禁**: Accepted 授权 Method A 多品种审计；**禁止**改 Decision 001 / 默认 loader / 交易。

**一句话**：检验「换月邻域脏」是否在预注册多品种上普遍成立；仍保持无复权基线。

---

## 0. 零假设

> H0：在预注册品种集合上，换月邻域相对非换月**多数不呈现**可度量实质结构差异。

目的：把 DATA EXP001（仅 `rb`）的 annotate 建议，扩展为可审计的多品种威胁等级；**不是**选复权法。

---

## 1. 单一假设

```text
H1:
  预注册品种中，至少一半品种的换月邻域满足预注册「实质」门槛。

结论词汇:
  roll_effect_material_annotate_multi
  | roll_effect_immaterial_multi
  | inconclusive
```

禁止与 ATR / Volume / OI Feature 结论合并。

---

## 2. Frozen Universe

| 项 | 冻结值 |
|----|--------|
| symbols | `hc`, `i`, `m`, `au`（**不含** `rb`；rb 已由 EXP001 覆盖） |
| timeframe | `1m` |
| method | Method A：CbC **无复权** |
| period | `2024-01-01` … `2025-12-31` |
| W | `60` |
| gap | old close → **new open** |

品种选择理由（预注册，不可因结果更换）：黑色相关 `hc`、黑色上游 `i`、农产品 `m`、贵金属 `au`。

---

## 3. Primary Metrics（每品种）

与 EXP001 对齐：

1. `gap_abs_mean`
2. `vol_ratio`（邻域 / 非换月 log-return std）
3. `abs_return_p95_ratio`

不做 ATR secondary（`atr_compression@1.0` 仅允许 rb）。

---

## 4. Evidence Gates（跑数前冻结）

**单品种实质（material）**当且仅当：

1. `roll_count >= 1`
2. 指标有限（非 NaN）
3. `vol_ratio >= 1.50` **或** `abs_return_p95_ratio >= 1.20`

**实验结论**：

| 条件 | conclusion |
|------|------------|
| material 品种数 / 4 ≥ 0.5 | `roll_effect_material_annotate_multi` |
| material 品种数 = 0 | `roll_effect_immaterial_multi` |
| 其它 | `inconclusive` |

Governance：**HOLD**；Decision 001 **不变**。

---

## 5. Out of Scope

```text
复权主连 / Panama / 改 loader
交易 / PnL
改写 EXP001
参数搜索 / 事后换品种
Feature Sensor 晋级
```

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-19 | 1.0.0 | Accepted：多品种 Method A；门槛与品种冻结 |
