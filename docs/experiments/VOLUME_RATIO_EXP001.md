# VOLUME_RATIO_EXP001 — Experiment Run Specification

> **Status**: Accepted（Frozen；实现完成后跑数仍须另授权）
> **Accepted date**: 2026-07-19
> **Experiment ID**: `VOLUME_RATIO_EXP001`
> **Parent RFC**: `docs/specs/VOLUME_RATIO_SENSOR_EXPERIMENT_RFC.md`
> **规则优先级**: `AGENTS.md` > Parent RFC > 本 Run Spec > 脚本
> **运行门禁**: Accepted ≠ 自动跑数。须先实现 Sensor + 单测，再明确授权「跑 VOLUME_RATIO EXP001」。

**一句话**：登记成交量相对活跃度的第一次可审计 Run；只验证一条假设；强制换月双报。

---

## 0. Identity

| 字段 | 冻结值 |
|------|--------|
| `experiment_id` | `VOLUME_RATIO_EXP001` |
| `run_id` | `VOLUME_RATIO_EXP001_RUN001` |
| `subject_kind` | `feature_sensor` |
| `sensor_id` | `volume_ratio` |
| `sensor_version` | `1.0` |
| governance | `EXPERIMENT`（本 Run 不晋级） |

---

## 1. Hypothesis

```text
H0: volume_ratio 与 RV_N 无关联
H1: volume_ratio 与 RV_N 存在可检出关联
```

唯一改动变量：本 Sensor 观测本身。禁止顺带改 OI / 出入场 / 成本。

---

## 2. Universe

| 项 | 值 |
|----|-----|
| symbol | `rb` |
| timeframe | `1m` |
| Continuous / Price | CbC / 无复权 |
| period | `2024-01-01` … `2025-12-31` |
| W（baseline） | `100` |
| N（outcome） | `60` |
| sampling interval | `60`（非重叠 Outcome） |
| Primary Metric | Spearman ρ |
| Roll | 标注 + **双报** `full` / `ex_roll`；默认 W_roll=`60` |

主结论样本：主=`ex_roll`，次=`full`；必须双报。

### 2.1 Evidence 结论规则（跑数前冻结）

`association_detected` 当且仅当：

1. `ex_roll` 的 `|ρ| >= 0.10`；
2. `ex_roll` 的 95% CI 不跨 0；
3. `full` 与 `ex_roll` 的 ρ 同号；
4. `|ρ_full - ρ_ex_roll| <= 0.05`。

否则结论为 `inconclusive`，治理决策保持 `HOLD`。  
本 EXP001 不使用显著性单独晋级，也不声明 `no_association`（单品种无法证明普遍无关联）。

---

## 3. Execution sequence（相对 OI）

1. Accept Volume RFC + 本 Run Spec  
2. 实现 `volume_ratio` Sensor + 单测  
3. 授权跑 Artifact → Evaluation → Evidence  
4. **闭环后**再实现 / 跑 `OI_CHANGE_EXP001`

禁止与 OI 实验并行混读、禁止拼一条「量仓都有效」的叙事。

---

## 4. Out of Scope

交易、PnL、参数搜索、多品种结论、改 Decision 001、改写 ATR/DATA。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-19 | 0.1.0-draft | 与 Parent 同步首稿 |
| 2026-07-19 | 1.0.0 | Accepted：VQ1–VQ5 按建议冻结；跑数仍须另授权 |
| 2026-07-19 | 1.0.1 | 跑数前冻结 Evidence 门槛与非重叠采样 |
