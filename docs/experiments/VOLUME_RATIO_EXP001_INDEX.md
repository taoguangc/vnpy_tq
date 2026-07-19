# VOLUME_RATIO_EXP001 — Artifact Index

> **Status**: Completed（Evidence closed；no promotion）
> **Indexed date**: 2026-07-19
> **Experiment Spec**: `docs/experiments/VOLUME_RATIO_EXP001.md`
> **Local artifact root**（gitignored）: `research/output/evidence/VOLUME_RATIO_EXP001/`

## Lifecycle Result

| Stage | Status |
|-------|--------|
| Feature Artifact | Completed |
| Evaluation | Completed（`full` + `ex_roll`） |
| Evidence | Completed |
| Promotion / Trading | **none** |
| Sensor | `volume_ratio@1.0` remains **EXPERIMENT** |

| Evidence field | Value |
|----------------|-------|
| `evidence_id` | `EV-VOLUME-RATIO-EXP001-001` |
| conclusion | `inconclusive` |
| governance | `HOLD` |
| primary `ρ_ex_roll` | `0.064631`（n=2749） |
| 95% CI | `[0.027311, 0.101770]` |
| sensitivity `ρ_full` | `0.064146`（n=2763） |
| roll-excluded | `14`（0.507%） |

相关方向在两套样本中稳定且 CI 不跨 0，但预注册效应门槛要求
`|ρ_ex_roll| >= 0.10`；实际效应未达门槛，因此结论为
**inconclusive / HOLD**，不得晋级。

## Provenance

| Field | Value |
|-------|-------|
| run | `VOLUME_RATIO_EXP001_RUN001` |
| code revision（Artifact） | `3e9e8bb6fb4c83da23a68534d3e860f5fa20fac0` |
| data fingerprint | `sha256:0c084a8cec91686dc6a7105f9b1e411412c243566810d3842391af8e2a617044` |
| artifact hash | `sha256:40bc7337fe92fb979492ed05d1aee668ba18b3e01f67231f4899ff86859d49ee` |
| rows | `165765` |
| period | `2024-01-01` … `2025-12-31` |

## Freeze

本实验已关闭。禁止改写产物、阈值或结论。后续 Volume 研究必须使用新
`experiment_id`。OI 实验保持独立，不得把两者拼成联合结论。
