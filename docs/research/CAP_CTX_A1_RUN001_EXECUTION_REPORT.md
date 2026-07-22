# CAP_CTX_A1_RUN001 — Observation Execution Report

> **Type**: Observation Execution Report（≠ Evidence Review）  
> **Status**: **COMPLETE** · machine `outcome=PASS`  
> **Date**: 2026-07-21  
> **Run**: `CAP_CTX_A1_RUN001`  
> **Obs Auth**: [`CAP_CTX_A1_OBSERVATION_AUTHORIZATION.md`](CAP_CTX_A1_OBSERVATION_AUTHORIZATION.md) — **GRANTED**  
> **Evidence dir**: `research/output/evidence/CAP_CTX_A1/`

### Command

```text
.\.venv\Scripts\python.exe -m context_engine.validate_a1 \
  --manifest research/output/evidence/CAP_CTX_A1/CAP_CTX_A1_RUN_MANIFEST.json \
  --authorize-observation
```

### Results（machine）

| Criterion | Result | Notes |
|-----------|--------|-------|
| A1-E1 Deterministic Publish | **PASS** | n=165765 · exact_mismatches=0（rb full window） |
| A1-E2 Batch/Streaming Parity | **PASS** | ContextState equality only |
| A1-E3 Fault Handling | **PASS** | F-MISS→DEGRADED；F-DUP/F-FUT/F-ROLL/F-SESS→INVALID |
| A1-E4 Latency | **PASS** | p99≈0.18ms ≪ 100ms；publish-path only |
| A1-E5 Reproduction | **PASS** | content sha256 recorded |

```text
evidence_record.outcome = PASS
```

### Artifacts

| File | Role |
|------|------|
| `context_schema.json` | Schema freeze |
| `parity_report.json` | A1-E1 / A1-E2 |
| `fault_test_report.json` | A1-E3 |
| `latency_report.json` | A1-E4 |
| `evidence_record.json` | Aggregate + lineage |
| `CAP_CTX_A1_RUN_MANIFEST.json` | Run identity · OBSERVATION_COMPLETE |

### Non-claims（binding）

```text
Observation COMPLETE ≠ Evidence Review PASS
≠ K001 update
≠ Gate PASS / Candidate
≠ RC001 / Strategy / Alpha / PnL
confidence ≠ win probability
latency ≠ production trading SLA
```

### Next

```text
Evidence Review（另授 / 人工审阅）→ COMPLETE · PASS
        ↓（另授）
Gate v2 Re-evaluation
```
