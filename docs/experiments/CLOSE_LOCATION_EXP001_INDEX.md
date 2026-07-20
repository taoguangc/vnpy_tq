# CLOSE_LOCATION_EXP001 — Artifact Index

> **Status**: Completed（Evidence closed；no promotion）
> **Indexed date**: 2026-07-20
> **Experiment Spec**: `docs/experiments/CLOSE_LOCATION_EXP001.md`
> **Local artifact root**（gitignored）: `research/output/evidence/CLOSE_LOCATION_EXP001/`

## Lifecycle Result

| Stage | Status |
|-------|--------|
| Feature Artifact | Completed |
| Evaluation | Completed（`full` + `ex_roll`） |
| Evidence | Completed |
| Promotion / Trading | **none** |
| Sensor | `close_location@1.0` remains **EXPERIMENT** |

| Evidence field | Value |
|----------------|-------|
| `evidence_id` | `EV-CLOSE-LOCATION-EXP001-001` |
| conclusion | `inconclusive` |
| governance | `HOLD` |
| primary `ρ_ex_roll` | `-0.004569`（n=2747） |
| 95% CI | `[-0.041961, 0.032836]` |
| sensitivity `ρ_full` | `-0.004706`（n=2761） |
| roll-excluded | `14`（0.507%） |

主样本效应接近 0，95% CI 跨 0，未达预注册门槛 `|ρ_ex|≥0.10`。结论为
**inconclusive / HOLD**，不得晋级。符合 Decision 016：本实验 Outcome 为
SR_60（signed return），不是 RV_60 同构搜索。

## Provenance

| Field | Value |
|-------|-------|
| run | `CLOSE_LOCATION_EXP001_RUN001` |
| code revision（Artifact） | `7d20f7c7d2e7970e5e177bc13bd73d6f30d77396` |
| data fingerprint | `sha256:0c084a8cec91686dc6a7105f9b1e411412c243566810d3842391af8e2a617044` |
| artifact hash | `sha256:bad324df10e16b8080b5aa47bf5ad9d9ac410ba08172f22a30da87f3ff47508d` |
| rows | `165765`（ready=165659；null=106；roll=726） |
| period | `2024-01-01` … `2025-12-31` |
| outcome | `SR_60` = `sum(log_return[t+1:t+60])` |

## Freeze

本实验已关闭。禁止改写产物、阈值或结论。后续 Close Location 研究必须使用新
`experiment_id`。不得把本结论与 ATR/Volume/OI 拼成联合「特征无效」叙事；仅说明
本预注册设定下未检出关联。
