# CLOSE_LOCATION_EXP001 — Experiment Run Specification

> **Status**: Accepted（Frozen；实现完成后跑数仍须另授权）
> **Accepted date**: 2026-07-19
> **Experiment ID**: `CLOSE_LOCATION_EXP001`
> **Parent RFC**: `docs/specs/CLOSE_LOCATION_SENSOR_EXPERIMENT_RFC.md`
> **规则优先级**: `AGENTS.md` > Parent RFC > 本 Run Spec > 脚本
> **运行门禁**: Accepted ≠ 自动跑数。须先实现 Sensor + 单测，再明确授权「跑 CLOSE_LOCATION EXP001」。

**一句话**：登记 bar 内收盘位置的第一次可审计 Run；Outcome 为 signed return；强制换月双报。

---

## 0. Identity

| 字段 | 冻结值 |
|------|--------|
| `experiment_id` | `CLOSE_LOCATION_EXP001` |
| `run_id` | `CLOSE_LOCATION_EXP001_RUN001` |
| `subject_kind` | `feature_sensor` |
| `sensor_id` | `close_location` |
| `sensor_version` | `1.0` |
| output key | `close_location` |
| governance | `EXPERIMENT`（本 Run 不晋级） |

---

## 1. Hypothesis

```text
H0: close_location 与 SR_N 无关联
H1: close_location 与 SR_N 存在可检出关联
SR_N = sum(log_return[t+1:t+N])
```

唯一改动变量：本 Sensor 观测本身。

---

## 2. Universe

| 项 | 值 |
|----|-----|
| symbol | `rb` |
| timeframe | `1m` |
| Continuous / Price | CbC / 无复权 |
| period | `2024-01-01` … `2025-12-31` |
| Feature | `(close-low)/(high-low)` |
| N（outcome） | `60` |
| sampling interval | `60`（非重叠） |
| Primary Metric | Spearman ρ |
| Roll | 标注 + **双报** `full` / `ex_roll`；W_roll=`60` |

主结论样本：主=`ex_roll`，次=`full`；必须双报。

### 2.1 Evidence 结论规则（跑数前冻结）

与 Volume/OI 同尺：`|ρ_ex|≥0.10` 且 CI 不跨 0 且同号且 `|Δρ|≤0.05` → `association_detected`；否则 `inconclusive` / `HOLD`。

---

## 3. Out of Scope

交易、PnL、RV_60、参数搜索、改 Decision 001、改写已 Closed 实验。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-19 | 1.0.0 | Accepted：CQ1–CQ4 按建议冻结；跑数须另授权 |
