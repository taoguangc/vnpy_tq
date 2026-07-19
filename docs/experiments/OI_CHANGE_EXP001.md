# OI_CHANGE_EXP001 — Experiment Run Specification

> **Status**: Accepted（Frozen；按 OQ5 等待 `VOLUME_RATIO_EXP001` 闭环）
> **Accepted date**: 2026-07-19
> **Experiment ID**: `OI_CHANGE_EXP001`
> **Parent RFC**: `docs/specs/OI_CHANGE_SENSOR_EXPERIMENT_RFC.md`
> **规则优先级**: `AGENTS.md` > Parent RFC > 本 Run Spec > 脚本
> **运行门禁**: Accepted ≠ 自动实现 / 跑数。须 `VOLUME_RATIO_EXP001` 先闭环，再明确授权后续工作。

**一句话**：登记持仓相对变化的第一次可审计 Run；与成交量实验完全独立。

---

## 0. Identity

| 字段 | 冻结值 |
|------|--------|
| `experiment_id` | `OI_CHANGE_EXP001` |
| `run_id` | `OI_CHANGE_EXP001_RUN001` |
| `subject_kind` | `feature_sensor` |
| `sensor_id` | `oi_change` |
| `sensor_version` | `1.0` |
| output key | `oi_rel_change` |
| governance | `EXPERIMENT`（本 Run 不晋级） |

---

## 1. Hypothesis

```text
H0: oi_rel_change 与 RV_N 无关联
H1: oi_rel_change 与 RV_N 存在可检出关联
```

唯一改动变量：本 Sensor 观测本身。禁止顺带引入 volume_ratio。

---

## 2. Universe

| 项 | 值 |
|----|-----|
| symbol | `rb` |
| timeframe | `1m` |
| Continuous / Price | CbC / 无复权 |
| period | `2024-01-01` … `2025-12-31` |
| Feature | `(oi[t]-oi[t-1])/oi[t-1]` |
| N（outcome） | `60` |
| sampling interval | `60`（非重叠 Outcome） |
| Primary Metric | Spearman ρ |
| Roll | 标注 + **双报** `full` / `ex_roll`；默认 W_roll=`60` |

主结论样本：主=`ex_roll`，次=`full`；必须双报。

`oi` 字段：与 `tq_data_loader` 一致（`close_oi` 优先，否则 `open_oi` → `open_interest`）。

### 2.1 Evidence 结论规则（跑数前冻结）

与 Volume 使用相同门槛，避免为 B 事后改尺子。`association_detected` 当且仅当：

1. `ex_roll` 的 `|ρ| >= 0.10`；
2. `ex_roll` 的 95% CI 不跨 0；
3. `full` 与 `ex_roll` 的 ρ 同号；
4. `|ρ_full - ρ_ex_roll| <= 0.05`。

否则为 `inconclusive` / `HOLD`；不以显著性单独晋级，不声明普遍无关联。

---

## 3. Sequencing

`VOLUME_RATIO_EXP001` Evidence 关闭后，再授权本实验实现 / Artifact。  
实现与跑数必须串行。

---

## 4. Out of Scope

交易、PnL、参数搜索、与 Volume 合并结论、改 Decision 001。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-19 | 0.1.0-draft | 与 Parent 同步首稿 |
| 2026-07-19 | 1.0.0 | Accepted：OQ1–OQ5 按建议冻结；等待 Volume 闭环 |
| 2026-07-19 | 1.0.1 | 跑数前冻结与 Volume 相同的 Evidence 门槛 |
