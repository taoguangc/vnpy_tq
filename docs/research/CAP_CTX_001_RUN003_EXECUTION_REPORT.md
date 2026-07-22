# CAP_CTX_001_RUN003 — Observation Execution Report

> **Status**: Observation COMPLETE · Evidence artifacts written  
> **Role**: Cross-sectional Cross Evidence（`parent=CAP_CTX_001_RUN002`）  
> **Knowledge Decision**: **NONE** — Registered Knowledge Action only  
> **Gate / RC001**: UNCHANGED  
> **Path**: `docs/research/CAP_CTX_001_RUN003_EXECUTION_REPORT.md`

## Authorization

```text
Command: Authorize Observation Execution for CAP_CTX_001_RUN003
Script: scripts/run_cap_ctx_001_run003.py
Revision at start: f9e56cd67ec4e4a6bcbbc428ea8671d7aac194b3
Protocol: inherited from RUN001; override = registered universe scope only
Integrity: C-XEV + C-UNIV binding
```

## Artifacts

| Artifact | Path |
|----------|------|
| Run Manifest | `research/output/evidence/CAP_CTX_001_RUN003/CAP_CTX_001_RUN_MANIFEST.json` |
| Evaluation | `research/output/evidence/CAP_CTX_001_RUN003/evaluation.json` |
| EvidenceRecord draft | `research/output/evidence/CAP_CTX_001_RUN003/evidence_record.json` |

## Scope

| Item | Value |
|------|-------|
| Full window | 2024-01-01 … 2025-12-31 |
| Warmup | 2023-10-01（excluded from stats） |
| Initial universe | rb / i / MA |
| Expansion instrument | **TA** |
| Expanded universe | rb / i / MA / TA |

## Results (registered metrics)

| Check | Result |
|-------|--------|
| Coverage (monthly presence rb/i/MA/TA) | OK（长假 gap 仅披露；max_gap≈258h） |
| E1 rb | **PASS** — SMD_M1=0.832 > N1 q95=0.010；SMD_M2=0.177 |
| E1 i | **PASS** — SMD_M1=0.886 > N1 q95=0.009；SMD_M2=0.114 |
| E1 MA | **PASS** — SMD_M1=0.927 > N1 q95=0.009；SMD_M2=0.135 |
| E1 TA | **PASS** — SMD_M1=0.749 > N1 q95=0.009；SMD_M2=0.096 |
| E2 rb | **PASS** — mean_run_length=17.47 > N2 q95=15.62；n_runs=9490 |
| E3 | **supported** — transfer E1 Pass 3/3（i, MA, TA）；n3_isolated=false |

## Cross Evidence fields（not Knowledge Decision）

| Field | Value |
|-------|-------|
| `cross_evidence_result` | `SUPPORTED` |
| `decision` | `SUPPORTED` |
| `registered_knowledge_action` | **STRENGTHEN** |
| `knowledge_decision` | **null**（须另授 Review） |
| `accepted_knowledge` | **false** |
| `review_required` | **true** |
| Gate implication | NONE_AUTOMATIC |
| RC001 implication | NONE_AUTOMATIC |

## Methodological note（必须进入 Review）

E1 主度量 `SMD_M1` 的标签来自 **M1 因果中位数分割**，因此 SMD_M1 相对 iid 标签 Null 偏大，**部分属定义使然**（与 RUN001/RUN002 相同限制）。  
解释权重：**E2 + E3 + SMD_M2** ≥ 孤立 E1。  
E3 为 expanded-universe transfer（i, MA, TA），**不是** TA-only 评估。

## Claim boundary

允许：在 RUN003 cross-sectional 注册条件下，Evidence 与 K001 descriptive structure **一致/不一致**；仅触发预注册 Registered Knowledge Action。  
禁止：无条件 K001 升级；Capability Candidate；未经 Review 的 Knowledge Decision；Regime / Alpha；Gate 自动 PASS；RC001 Accepted。

## Next

```text
Evidence / Cross Evidence Review
        ↓
K001 Knowledge Review（依据预注册 Action；另授）
        ↓
（later）Capability Portfolio / Gate v2（独立；DEFERRED）
```

Evidence Review 文档：[`CAP_CTX_001_RUN003_EVIDENCE_REVIEW.md`](CAP_CTX_001_RUN003_EVIDENCE_REVIEW.md)

---

## 修订记录

| 日期 | 说明 |
|------|------|
| 2026-07-21 | Observation 完成；SUPPORTED → STRENGTHEN（Registered Action only） |
