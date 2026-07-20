# DATA_CONTINUOUS_CONTRACT_EXP001 — Experiment Run Specification

> **Status**: Archived（Evidence closed 2026-07-19；Decision 001 unchanged）
> **Accepted date**: 2026-07-19
> **Experiment ID**: `DATA_CONTINUOUS_CONTRACT_EXP001`
> **Parent RFC**: `docs/specs/DATA_CONTINUOUS_CONTRACT_EXPERIMENT_RFC.md`（Accepted）
> **Artifact Index**: `docs/experiments/DATA_CONTINUOUS_CONTRACT_EXP001_INDEX.md`
> **规则优先级**: `AGENTS.md` > Parent RFC > 本 Run Spec > 脚本
> **运行门禁**: 本实验线已闭环。有效结果以 **RUN002** 为准；RUN001 为 INVALID。禁止改写产物；禁止改 Decision 001。

---

## 0. Identity

| 字段 | 冻结值 |
|------|--------|
| `experiment_id` | `DATA_CONTINUOUS_CONTRACT_EXP001` |
| `run_id`（有效） | `DATA_CONTINUOUS_CONTRACT_EXP001_RUN002`（RUN001 INVALID） |
| `subject_kind` | `dataset` |
| `subject_id` | `rb_cbc_unadjusted` |
| `subject_version` | `1.0` |
| method | Method A only：`CbC_unadjusted` |
| symbol / timeframe | `rb` / `1m` |
| period | `2024-01-01` … `2025-12-31` |
| neighborhood W | `60`（换月前 60 + 后 60 根 1m bar） |

---

## 1. Hypothesis

```text
H0:
  换月邻域的跳空/波动对全样本收益与 Feature 观测无实质扭曲。

H1:
  换月邻域存在可度量的实质结构差异（相对非换月时段）。
```

结论词汇：`roll_effect_immaterial` | `roll_effect_material_annotate` | `inconclusive`。
Governance：预期 `HOLD` 或保持基线；**禁止**改复权基线。

---

## 2. Data

| 项 | 值 |
|----|-----|
| Source | TQ offline |
| Construction | CbC unadjusted（`tq_rollover_data`） |
| Roll map | `data/tq/rb/rollover_map.parquet` |
| Adjustment | none |

`data_fingerprint` = source_id + file_manifest + file_hashes + construction_metadata
（construction_metadata 必须含 `continuous_contract=CbC`，`adjustment=unadjusted`，period，W）。

---

## 3. Primary Metrics（预注册）

1. **Roll gap size**：每个换月点的绝对/相对跳空。
2. **Roll-neighborhood vol**：邻域实现波动 vs 非换月。
3. **Roll-neighborhood return**：邻域 log-return 尾部 vs 非换月。

## 4. Secondary

- `atr_compression@1.0`（atr_period=14, baseline_window=100）
- 比较换月邻域 vs 非换月的 `atr_ratio` 分布
- 标注 `secondary`；不得替代 Primary 结论

## 5. Out of Scope

```text
B/C/D 复权构造
改 Decision 001
改默认 loader
Trading / PnL
覆盖 ATR EXP001
```

## 6. Artifacts（授权跑数后）

```text
research/output/evidence/DATA_CONTINUOUS_CONTRACT_EXP001/
├── manifest.json
├── run_metadata.json
├── artifacts/...
├── evaluation/...
└── evidence/...
```

## 7. Execution Gate

| Step | 状态 |
|------|------|
| RFC + Run Spec Accepted | ✅ |
| RUN001 Artifact | ❌ INVALID（gap 口径错误；保留） |
| RUN002 Artifact | ✅ |
| Evaluation（RUN002） | ✅ HOLD |
| Evidence（RUN002） | ✅ `roll_effect_material_annotate` / HOLD |
| Decision 001 / loader | ✅ unchanged |

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-19 | 1.0.0 | Accepted：与 Parent RFC DQ 决议对齐；W=60；仅 Method A |
| 2026-07-19 | 1.1.0 | Lifecycle Completed：RUN002 Evidence；见 Artifact Index |
