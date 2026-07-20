# OPP16_EXP001 — Artifact Index

> **Status**: Completed（Evidence closed；no promotion）
> **Indexed date**: 2026-07-20
> **Experiment Spec**: `docs/experiments/OPP16_EXP001.md`
> **Local artifact root**（gitignored）: `research/output/evidence/OPP16_EXP001/`

## Lifecycle Result

| Stage | Status |
|-------|--------|
| Detection Artifact | Completed |
| Evaluation | Completed（`full` + `ex_roll`） |
| Evidence | Completed |
| Promotion / Trading | **none** |
| Detector | `OPP16@1.0.0` remains **Candidate / EXPERIMENT** |

| Evidence field | Value |
|----------------|-------|
| `evidence_id` | `EV-OPP16-EXP001-001` |
| conclusion | `inconclusive` |
| governance | `HOLD` |
| primary `mean(aligned)_ex_roll` | `-0.000134`（n=4557） |
| 95% CI | `[-0.000423, 0.000141]` |
| sensitivity `mean_full` | `-0.000124`（n=4572） |
| hit_rate_ex_roll | `0.4753` |
| roll-excluded events | artifact `roll=15`；评价样本差约 15 |

主样本均值略负，95% CI 下界不大于 0，未达预注册门槛。结论为
**inconclusive / HOLD**，不得晋级；不得继承遗留 E2 叙事。

## Provenance

| Field | Value |
|-------|-------|
| run | `OPP16_EXP001_RUN001` |
| code revision（Artifact） | 见 `run_metadata.json` |
| artifact hash | `sha256:24d7915a136aeec8c1b502482527f9e7bc567c0fd981293fa5589e3d66fd7c26` |
| events | `4580`（roll 邻域 15） |
| period | `2024-01-01` … `2025-12-31` |
| outcome | aligned `SR_60` on 5m |

## Freeze

本实验已关闭。禁止改写产物、门槛或结论。后续 OPP16 研究必须使用新
`experiment_id` / 新 `detector_version`。
