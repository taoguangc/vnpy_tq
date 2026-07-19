# OI_CHANGE_EXP001 — Artifact Index

> **Status**: Completed（Evidence closed；no promotion）
> **Indexed date**: 2026-07-19
> **Experiment Spec**: `docs/experiments/OI_CHANGE_EXP001.md`
> **Local artifact root**（gitignored）: `research/output/evidence/OI_CHANGE_EXP001/`

## Lifecycle Result

| Stage | Status |
|-------|--------|
| Feature Artifact | Completed |
| Evaluation | Completed（`full` + `ex_roll`） |
| Evidence | Completed |
| Promotion / Trading | **none** |
| Sensor | `oi_change@1.0` remains **EXPERIMENT** |

| Evidence field | Value |
|----------------|-------|
| `evidence_id` | `EV-OI-CHANGE-EXP001-001` |
| conclusion | `inconclusive` |
| governance | `HOLD` |
| primary `ρ_ex_roll` | `-0.019848`（n=2749） |
| 95% CI | `[-0.057191, 0.017550]` |
| sensitivity `ρ_full` | `-0.019185`（n=2763） |
| roll-excluded | `14`（0.507%） |

效应很小，且主样本 CI 跨 0；不满足预注册的 `|ρ| >= 0.10`
与 CI 门槛，因此为 **inconclusive / HOLD**，不得晋级。

## Provenance

| Field | Value |
|-------|-------|
| run | `OI_CHANGE_EXP001_RUN001` |
| code revision（Artifact） | `17ccabecfdbea216d850e731a55635aa2745d2f8` |
| data fingerprint | `sha256:0c084a8cec91686dc6a7105f9b1e411412c243566810d3842391af8e2a617044` |
| artifact hash | `sha256:b6df1abdfcd56a9d91fb4731434e8e1797c894226a8b7bd4356a7ec185df4132` |
| rows | `165765` |
| period | `2024-01-01` … `2025-12-31` |

## Freeze

本实验已关闭。禁止改写产物、阈值或结论。后续 OI 研究必须使用新
`experiment_id`；不得与 Volume EXP001 合并成联合结论。
