# CAP_CTX_001_RUN002 — Observation Execution Report

> **Status**: Observation COMPLETE · Evidence artifacts written  
> **Role**: Temporal OOS Cross Evidence（`parent=CAP_CTX_001_RUN001`）  
> **Knowledge Decision**: **NONE** — Registered Knowledge Action only  
> **Gate / RC001**: UNCHANGED  
> **Path**: `docs/research/CAP_CTX_001_RUN002_EXECUTION_REPORT.md`

## Authorization

```text
Command: Authorize Observation Execution for CAP_CTX_001_RUN002
Script: scripts/run_cap_ctx_001_run002.py
Revision at start: f9e56cd67ec4e4a6bcbbc428ea8671d7aac194b3
Protocol: inherited from RUN001; override = temporal scope only
Integrity: C-XEV purpose constraint binding
```

## Artifacts

| Artifact | Path |
|----------|------|
| Run Manifest | `research/output/evidence/CAP_CTX_001_RUN002/CAP_CTX_001_RUN_MANIFEST.json` |
| Evaluation | `research/output/evidence/CAP_CTX_001_RUN002/evaluation.json` |
| EvidenceRecord draft | `research/output/evidence/CAP_CTX_001_RUN002/evidence_record.json` |

## Scope

| Item | Value |
|------|-------|
| Full window | 2022-01-01 … 2023-12-31 |
| Warmup | 2021-10-01（excluded from stats） |
| Universe | rb / i / MA |

## Results (registered metrics)

| Check | Result |
|-------|--------|
| Coverage (monthly presence rb/i/MA) | OK（长假 gap 仅披露；max_gap≈258h） |
| E1 rb | **PASS** — SMD_M1=0.961 > N1 q95=0.010；SMD_M2=0.119（secondary） |
| E1 i | **PASS** — SMD_M1=0.748 > N1 q95=0.009；SMD_M2=0.153 |
| E1 MA | **PASS** — SMD_M1=1.053 > N1 q95=0.009；SMD_M2=0.216 |
| E2 rb | **PASS** — mean_run_length=16.30 > N2 q95=14.75；n_runs=10127 |
| E3 | **supported** — transfer E1 Pass 2/2；n3_isolated=false |

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

E1 主度量 `SMD_M1` 的标签来自 **M1 因果中位数分割**，因此 SMD_M1 相对 iid 标签 Null 偏大，**部分属定义使然**（与 RUN001 相同限制）。  
解释权重：**E2 + E3 + SMD_M2** ≥ 孤立 E1。

## Claim boundary

允许：在 RUN002 OOS 注册条件下，Evidence 与 RUN001 descriptive structure **一致/不一致**；仅触发预注册 Registered Knowledge Action。  
禁止：无条件 K001 升级；未经 Review 的 Knowledge Decision；Regime / Alpha；Gate 自动 PASS；RC001 Accepted。

## Next

```text
Evidence / Cross Evidence Review PASS ✓
        ↓
K001 Strengthen Knowledge Review（另授）
        ↓
（later）Gate 复评（独立）
```

Evidence Review 文档：[`CAP_CTX_001_RUN002_EVIDENCE_REVIEW.md`](CAP_CTX_001_RUN002_EVIDENCE_REVIEW.md)

---

## 修订记录

| 日期 | 说明 |
|------|------|
| 2026-07-21 | Observation 完成；SUPPORTED → STRENGTHEN（Registered Action only） |
| 2026-07-21 | Evidence Review PASS；K001 Decision 未执行 |
