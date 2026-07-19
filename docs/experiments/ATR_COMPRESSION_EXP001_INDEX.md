# ATR_COMPRESSION_EXP001 — Artifact Index

> **Status**: Completed（Evidence closed；no promotion）
> **Indexed date**: 2026-07-19
> **Experiment Spec**: `docs/experiments/ATR_COMPRESSION_EXP001.md`
> **Local artifact root**（gitignored）: `research/output/evidence/ATR_COMPRESSION_EXP001/`

本文件是工程闭环索引：记录 runner、指纹与 Evidence 结论。
**不**把 Feature JSONL 大文件纳入 Git；本地产物以 content hash 核验。

---

## 1. Lifecycle Result

| Stage | Status |
|-------|--------|
| Feature Artifact | Completed |
| Evaluation | Completed |
| Evidence | Completed |
| Promotion | **none** |
| Trading | **none** |
| Sensor status | `atr_compression@1.0` remains **EXPERIMENT** |

| Evidence field | Value |
|----------------|-------|
| `evidence_id` | `EV-ATR-COMPRESSION-EXP001-001` |
| `hypothesis_conclusion` | `inconclusive` |
| governance `decision` | `HOLD` |
| Spearman ρ | `0.1082` |
| sample_n | `2761` |

---

## 2. Runners（in repo）

| Script | Role |
|--------|------|
| `scripts/run_atr_compression_exp001.py` | Feature Artifact + Manifest + run_metadata |
| `scripts/run_atr_compression_exp001_evaluation.py` | Outcome/Metric defs + EvaluationResult + evaluation_report |
| `scripts/run_atr_compression_exp001_evidence.py` | EvidenceRecord + evidence_summary |

Authorization order was enforced: Feature → Evaluation → Evidence（separate user gates）.

---

## 3. Provenance Snapshot

| Field | Value |
|-------|-------|
| `experiment_id` | `ATR_COMPRESSION_EXP001` |
| `run_id` | `ATR_COMPRESSION_EXP001_RUN001` |
| `code_revision`（Feature run） | `3886735ebd2852ed2070e410abf8e911162086bf` |
| `data_fingerprint` | `sha256:0c084a8cec91686dc6a7105f9b1e411412c243566810d3842391af8e2a617044` |
| Feature `content_hash` | `sha256:984f525a3b6e2d1d6f389676349c07e978fa8a1c75e45faced80f0c99af6cbfc` |
| Feature rows | `165765` |
| Period | `2024-01-01` … `2025-12-31` |
| Parameters | `atr_period=14`, `baseline_window=100` |

---

## 4. Local Layout（not committed）

```text
research/output/evidence/ATR_COMPRESSION_EXP001/
├── manifest.json
├── run_metadata.json
├── evaluation_report.json
├── evidence_summary.json
├── artifacts/ATR_COMPRESSION_EXP001_FEATURES/feature_results.jsonl
├── definitions/outcomes/OUT-ATR-EXP001-RV60.json
├── definitions/metrics/MET-ATR-EXP001-SPEARMAN.json
├── evaluation/EVAL-ATR-COMPRESSION-EXP001-001.json
└── evidence/EV-ATR-COMPRESSION-EXP001-001.json
```

---

## 5. Freeze

EXP001 is closed. Further ATR research requires a **new** `experiment_id`（e.g. EXP002 OOS / multi-symbol / new hypothesis）. Do not mutate EXP001 artifacts, parameters, period, or conclusions.
