# CAP_CTX_001_RUN001 — Observation Execution Report

> **Status**: Observation COMPLETE · Evidence artifacts written  
> **Knowledge**: **Candidate only** — NOT Accepted Knowledge  
> **Gate / RC001**: UNCHANGED  
> **Path**: `docs/research/CAP_CTX_001_RUN001_EXECUTION_REPORT.md`

## Authorization

```text
Command: Authorize Observation Execution for CAP_CTX_001_RUN001
Script: scripts/run_cap_ctx_001_run001.py
Revision at start: 46aa4c308eee095051dba3ff279d9d8acab915ef
```

## Artifacts

| Artifact | Path |
|----------|------|
| Run Manifest | `research/output/evidence/CAP_CTX_001_RUN001/CAP_CTX_001_RUN_MANIFEST.json` |
| Evaluation | `research/output/evidence/CAP_CTX_001_RUN001/evaluation.json` |
| EvidenceRecord draft | `research/output/evidence/CAP_CTX_001_RUN001/evidence_record.json` |

## Results (registered metrics)

| Check | Result |
|-------|--------|
| Coverage (monthly presence rb/i/MA) | OK（长假 gap 仅披露） |
| E1 rb | **PASS** — SMD_M1=0.832 > N1 q95=0.010；SMD_M2=0.177（secondary） |
| E1 i | **PASS** — SMD_M1=0.886 > N1 q95=0.009 |
| E1 MA | **PASS** — SMD_M1=0.927 > N1 q95=0.009 |
| E2 rb | **PASS** — mean_run_length=17.47 > N2 q95=15.62；n_runs=9490 |
| E3 | **supported** — transfer E1 Pass 2/2；n3_isolated=false |

## Decision fields (not Knowledge Promotion)

| Field | Value |
|-------|-------|
| `decision` | `KEEP` |
| `knowledge_candidate` | `K001_CANDIDATE` |
| `accepted_knowledge` | **false** |
| `review_required` | **true** |
| Gate implication | NONE_AUTOMATIC |
| RC001 implication | NONE_AUTOMATIC |

## Methodological note（必须进入 Review）

E1 主度量 `SMD_M1` 的标签来自 **M1 因果中位数分割**，因此 SMD_M1 相对 iid 标签 Null 偏大，**部分属定义使然**。  
解释「超越标签变量本身的描述分离」时，应同时看：

- secondary `SMD_M2`
- E2 persistence vs block null
- E3 transfer

**不得**仅凭 E1 SMD_M1 宣布「市场状态已发现」或 Capability Accepted。

## Claim boundary

允许：在注册条件下，Evidence **支持/不支持** Capability 假设的 **Candidate** 陈述。  
禁止：已发现 Regime / Alpha；Gate 自动 PASS；RC001 Accepted；未经 Review 的 Accepted Knowledge。

## Next

```text
Evidence / Knowledge Candidate Review
        ↓
（另授）Accepted Knowledge 或修订/HOLD
        ↓
Gate 复评（独立）
```

---

## 修订记录

| 日期 | 说明 |
|------|------|
| 2026-07-21 | Observation 完成；K001_CANDIDATE；方法学注记 |
