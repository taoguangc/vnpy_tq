# OPP16_EXP001 — Experiment Run Specification

> **Status**: Accepted / **Lifecycle Completed**（Evidence closed；no promotion）
> **Accepted date**: 2026-07-20
> **Closed date**: 2026-07-20
> **Experiment ID**: `OPP16_EXP001`
> **Parent RFC**: `docs/specs/OPP16_TWO_BAR_REVERSAL_EXPERIMENT_RFC.md`
> **Artifact Index**: `docs/experiments/OPP16_EXP001_INDEX.md`
> **规则优先级**: `AGENTS.md` > Parent RFC > 本 Run Spec > 脚本
> **运行门禁**: 本实验已关闭；禁止覆盖产物。继续研究须新 `experiment_id`。

**一句话**：登记 OPP16 两棒反转的第一次可审计事件研究 Run；只验证裸形态边沿。

---

## 0. Identity

| 字段 | 冻结值 |
|------|--------|
| `experiment_id` | `OPP16_EXP001` |
| `run_id` | `OPP16_EXP001_RUN001` |
| `subject_kind` | `opportunity_detector` |
| `detector_id` | `OPP16` |
| `detector_version` | `1.0.0` |
| `opportunity_id` | `OPP16` |
| lifecycle | `Candidate` |
| evidence_level | `E0` → 跑通后最高宣称 `E1`（单品种）；本 Run **不**宣称 E2+ |
| governance | `EXPERIMENT`（不晋级 Production） |

---

## 1. Hypothesis

```text
H0: OPP16 事件后 aligned SR_N 无实质正边沿
H1: OPP16 事件后 aligned SR_N 可检出正边沿
```

唯一改动变量：OPP16 最小形态定义（Parent §2.1）。

---

## 2. Universe

| 项 | 值 |
|----|-----|
| symbol | `rb` |
| bar | 1m → 合成 **5m** |
| Continuous / Price | CbC / 无复权 |
| period | `2024-01-01` … `2025-12-31` |
| `body_ratio` | `0.5` |
| Context 过滤 | 无 |
| N | `60`（5m） |
| Roll | 双报 `full` / `ex_roll`；主=`ex_roll`；W_roll=`60`（1m） |
| Primary Metric | `mean(direction * SR_N)` + 95% CI |
| 成本 | 主结论不含交易成本；附录可报含成本敏感 |

### 2.1 事件去重

同一根 5m 完成棒至多一条 OPP16 事件（LONG 与 SHORT 互斥；若逻辑上不可能双触发则返回至多一个 `DetectionResult`）。跨棒不合并。

### 2.2 Evidence 结论规则（已冻结）

| 条件 | 要求 |
|------|------|
| 主样本 | `ex_roll` |
| CI | `mean(aligned)` 的 95% CI **下界 > 0** |
| 最小效应 | `min_effect = 0`（硬门为 CI 下界；不另加幅度门槛） |
| 稳健 | `full` 与 `ex_roll` **同号**；`|mean_full − mean_ex| ≤ 0.0005` |
| 样本 | `n_ex_roll ≥ 100` |

全过 → `association_detected` / 决策 `KEEP`（仍 Candidate，证据最高 E1）；否则 `inconclusive` 或 `REVERT` → `HOLD`，无晋级。

---

## 3. Out of Scope

交易、PnL 优化、参数搜索、多品种、遗留 context 过滤、改 Decision 001、改写已 Closed Feature 实验。

---

## 4. Lifecycle Result（Closed）

| 项 | 值 |
|----|-----|
| conclusion | `inconclusive` |
| governance | `HOLD` |
| `mean(aligned)_ex_roll` | `-0.000134`（n=4557） |
| 95% CI | `[-0.000423, 0.000141]` |
| `mean_full` | `-0.000124`（n=4572） |
| promotion | none |

详见 `OPP16_EXP001_INDEX.md`。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-20 | 0.1.0-draft | 首稿；待 Parent OQ1–OQ6 Accept |
| 2026-07-20 | 1.0.0 | Accepted：与 Parent 同步冻结；门槛写入 §2.2 |
| 2026-07-20 | 1.1.0 | Lifecycle Completed：inconclusive / HOLD；无晋级 |
