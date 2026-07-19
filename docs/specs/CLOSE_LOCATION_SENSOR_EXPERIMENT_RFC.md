# Close Location Sensor Experiment RFC

> **Status**: Draft（待 Review / Accept）
> **Draft date**: 2026-07-19
> **Experiment family**: `CLOSE_LOCATION`
> **First run id**: `CLOSE_LOCATION_EXP001`
> **Path**: `docs/specs/CLOSE_LOCATION_SENSOR_EXPERIMENT_RFC.md`
> **Parent**: `FEATURE_SENSOR_SPEC.md`、`FEATURE_ROLL_ANNOTATION_POLICY_RFC.md`、Decision 016
> **规则优先级**: `AGENTS.md` > Parent Spec > 本 RFC > 代码
> **实现门禁**: Draft ≠ 实现 / 跑数。本草案满足 Decision 016 条件 3（结构特征）。

**一句话**：测 bar 内收盘位置是否与后续短窗收益分布有关；不是买卖信号。

---

## 0. 为何不是 Volume/OI 同构

Decision 016 禁止再在 `rb` 上开「另一标量 ↔ RV_60」同构实验。  
本草案改用：

1. **结构特征**：`(close-low)/(high-low)`（bar 内位置）
2. **可选新 Outcome（Accept 时二选一冻结）**：
   - A：未来 60 根 **signed** log-return（方向延续）
   - B：未来 60 根 abs log-return（幅度）

默认建议：**A（signed return）**，与 RV_60 波动关联线区分。

---

## 1. 建议假设

```text
H0: close_location 与未来 N 根 signed log-return 无关联
H1: 存在可检出关联
```

Primary Metric：Spearman ρ；强制换月双报；默认 `W_roll=60`。

---

## 2. Open Questions

| ID | 问题 | 建议 |
|----|------|------|
| CQ1 | Outcome 用 signed return 还是 abs return？ | **signed** |
| CQ2 | N=60？ | **是** |
| CQ3 | 首跑仍 `rb` 单品种？ | **是**（结构特征首跑允许；非 RV_60 同构） |
| CQ4 | 主样本？ | 双报；主=`ex_roll` |

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-19 | 0.1.0-draft | 首稿：Decision 016 条件 3 候选 |
