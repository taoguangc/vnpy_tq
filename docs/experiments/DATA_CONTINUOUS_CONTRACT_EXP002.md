# DATA_CONTINUOUS_CONTRACT_EXP002 — Experiment Run Specification

> **Status**: Accepted（Frozen；跑数由本授权执行）
> **Accepted date**: 2026-07-19
> **Experiment ID**: `DATA_CONTINUOUS_CONTRACT_EXP002`
> **Parent RFC**: `docs/specs/DATA_MULTI_SYMBOL_ROLL_EXPERIMENT_RFC.md`
> **规则优先级**: `AGENTS.md` > Parent RFC > 本 Run Spec > 脚本

**一句话**：对 `hc/i/m/au` 做 Method A 换月邻域审计；双报每品种指标；按冻结门槛写 Evidence。

---

## 0. Identity

| 字段 | 冻结值 |
|------|--------|
| `experiment_id` | `DATA_CONTINUOUS_CONTRACT_EXP002` |
| `run_id` | `DATA_CONTINUOUS_CONTRACT_EXP002_RUN001` |
| `subject_kind` | `dataset` |
| `subject_id` | `multi_cbc_unadjusted_hc_i_m_au` |
| `subject_version` | `1.0` |
| symbols | `hc`, `i`, `m`, `au` |
| W / period | `60` / `2024-01-01`…`2025-12-31` |

---

## 1. Hypothesis

见 Parent RFC §1；Evidence 门槛见 Parent RFC §4。

---

## 2. Artifacts

```text
research/output/evidence/DATA_CONTINUOUS_CONTRACT_EXP002/
├── manifest.json
├── run_metadata.json
├── artifacts/.../roll_audit.json   # per-symbol summaries
├── evaluation_report.json
└── evidence_summary.json
```

---

## 3. Out of Scope

交易、复权、改 Decision 001、改写 EXP001、ATR secondary。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-19 | 1.0.0 | Accepted 并授权本轮 Artifact→Evidence |
