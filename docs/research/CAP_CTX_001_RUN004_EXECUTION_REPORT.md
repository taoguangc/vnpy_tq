# CAP_CTX_001_RUN004 — Observation Execution Report

> **Status**: Observation COMPLETE · Evidence artifacts written  
> **Role**: Observation Expansion（Liquidity Structure）· `parent=CAP_CTX_001_RUN003`  
> **Knowledge Decision**: **NONE** — Registered Action only  
> **Gate / RC001 / P4**: UNCHANGED / UNCHANGED / NOT MET  
> **Path**: `docs/research/CAP_CTX_001_RUN004_EXECUTION_REPORT.md`

## Authorization

```text
Command: Authorize Observation Execution for CAP_CTX_001_RUN004
Script: scripts/run_cap_ctx_001_run004.py
Revision: f9e56cd67ec4e4a6bcbbc428ea8671d7aac194b3
Override: Observation Family = Liquidity Structure（M3）only
```

## Artifacts

| Artifact | Path |
|----------|------|
| Manifest | `research/output/evidence/CAP_CTX_001_RUN004/CAP_CTX_001_RUN_MANIFEST.json` |
| Evaluation | `research/output/evidence/CAP_CTX_001_RUN004/evaluation.json` |
| EvidenceRecord | `research/output/evidence/CAP_CTX_001_RUN004/evidence_record.json` |

## Results

| Check | Result |
|-------|--------|
| Coverage rb/i/MA/TA | OK |
| E1_core rb/i/MA/TA | **PASS**（SMD_M1） |
| E1_family rb | **PASS** — SMD_M3=0.528 > N1 q95=0.009 |
| E1_family i/MA/TA | **PASS**（披露；TA SMD_M3=0.081 仍 > q95） |
| E2 rb | **PASS** — mean_run=17.47 > N2 q95=15.62 |
| E3 core transfer | **3/3** |

| Field | Value |
|-------|-------|
| `cross_evidence_result` | `SUPPORTED` |
| `registered_knowledge_action` | **STRENGTHEN** |
| `knowledge_decision` | null |

## Methodological note

E1_core 定义耦合保留。E1_family 使用 **同一 M1 标签** 下的 SMD_M3 → supporting only。  
**P3 ≠ P4**：Family PASS ≠ Independence Evidence。

## Claim boundary

允许：Observation Family robustness evidence。  
禁止：Capability Candidate · Gate PASS · P4 MET · Alpha · 换 Family。

## Next

```text
Evidence Review → K001 Review（另授 / 本轮可续）
```

---

## 修订记录

| 日期 | 说明 |
|------|------|
| 2026-07-21 | Observation COMPLETE；SUPPORTED → STRENGTHEN（Action only） |
