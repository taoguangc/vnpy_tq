# DATA_CONTINUOUS_CONTRACT_EXP001 — Artifact Index

> **Status**: Archived（Evidence closed；Decision 001 unchanged）
> **Indexed date**: 2026-07-19
> **Experiment Spec**: `docs/experiments/DATA_CONTINUOUS_CONTRACT_EXP001.md`
> **Local artifact root**（gitignored）: `research/output/evidence/DATA_CONTINUOUS_CONTRACT_EXP001/`

本文件是工程闭环索引。大产物不进 Git；以 content hash 核验本地文件。

---

## 1. Lifecycle Result

| Stage | Status |
|-------|--------|
| Method A Roll Audit Artifact | Completed（**RUN002**） |
| Evaluation | Completed |
| Evidence | Completed |
| RUN001 | **INVALID**（gap 口径错误；保留不覆盖） |
| Decision 001 baseline | **Unchanged** |
| Production loader | **Unchanged** |
| Trading / Promotion | **None** |

| Evidence field | Value |
|----------------|-------|
| `evidence_id` | `EV-DATA-CONTINUOUS-CONTRACT-EXP001-RUN002` |
| `hypothesis_conclusion` | `roll_effect_material_annotate` |
| governance `decision` | `HOLD` |
| gap_abs_mean | `44.17`（n=6） |
| vol_ratio | `2.56` |
| abs_return_p95_ratio | `1.36` |

**含义**：换月邻域对无复权序列有实质结构影响，Feature 研究须预注册换月标注/过滤；**不得**因此改用复权主连。

---

## 2. Runners（in repo）

| Script | Role |
|--------|------|
| `scripts/run_data_continuous_contract_exp001.py` | Method A Artifact + run-scoped manifest（RUN002） |
| `scripts/run_data_continuous_contract_exp001_evaluation.py` | Outcome/Metric + EvaluationResult |
| `scripts/run_data_continuous_contract_exp001_evidence.py` | EvidenceRecord + evidence_summary |

Core metrics：`strategies/paaf/data_audit/roll_audit.py`（old close → new open）。

---

## 3. Provenance Snapshot（RUN002）

| Field | Value |
|-------|-------|
| `experiment_id` | `DATA_CONTINUOUS_CONTRACT_EXP001` |
| `run_id` | `DATA_CONTINUOUS_CONTRACT_EXP001_RUN002` |
| Artifact `content_hash` | `sha256:36a0fff62ceb270e7588174af19f5ae73b6e97ab798c0e9508ae899e5ff5ea3f` |
| gap definition | old_close → new_open |
| Period | `2024-01-01` … `2025-12-31` |
| W | `60` |
| Universe | `rb` / `1m` / CbC unadjusted |
| Invalid predecessor | `DATA_CONTINUOUS_CONTRACT_EXP001_RUN001` + `RUN001_INVALID.json` |

---

## 4. Local Layout（not committed）

```text
research/output/evidence/DATA_CONTINUOUS_CONTRACT_EXP001/
├── RUN001_INVALID.json
├── manifest.json                    # RUN001 root（保留）
├── run_metadata.json                # RUN001 root（保留）
├── artifacts/
│   ├── ..._RUN001.../               # INVALID artifact retained
│   └── ..._RUN002_ROLL_AUDIT/roll_audit.json
├── definitions/...
├── evaluation/EVAL-...-RUN002.json
└── runs/
    └── DATA_CONTINUOUS_CONTRACT_EXP001_RUN002/
        ├── manifest.json
        ├── run_metadata.json
        ├── evaluation_report.json
        └── evidence_summary.json
```

---

## 5. Freeze

DATA EXP001 已关闭。后续若扩展（多品种 / B/C 负对照 / 更长区间）必须新 `experiment_id`，禁止改写本实验产物或 Decision 001。
