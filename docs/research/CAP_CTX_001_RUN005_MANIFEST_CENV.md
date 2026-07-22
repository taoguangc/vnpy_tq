# CAP_CTX_001_RUN005 — Run Manifest + C-ENV Draft

> **Type**: Run Identity Artifact Review（≠ Observation / Evidence Result）  
> **Status**: **Manifest CONFIRMED** · C-ENV **SATISFIED** · IER **SEALED** · Observation **NOT AUTHORIZED**  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CAP_CTX_001_RUN005_MANIFEST_CENV.md`  
> **Artifact**: [`research/output/evidence/CAP_CTX_001_RUN005/CAP_CTX_001_RUN_MANIFEST.json`](../../research/output/evidence/CAP_CTX_001_RUN005/CAP_CTX_001_RUN_MANIFEST.json)  
> **Auth**: [`CAP_CTX_001_RUN005_EXECUTION_AUTHORIZATION.md`](CAP_CTX_001_RUN005_EXECUTION_AUTHORIZATION.md) Confirmation PASS · CP3 OPEN

### Boundary

```text
Manifest = identity artifact
        ≠
result artifact

Contains: run identity / EQ / IER version / env / hashes / access policy / protocol fingerprint
Does NOT contain: Observation results / Interpretation / K001 conclusion bias
```

```text
Authorized ≠ Executed
Executed ≠ Evidence Accepted
Evidence Accepted ≠ Knowledge Decision
```

---

## C-ENV Capture

| Item | Status |
|------|--------|
| `code_revision` | `f9e56cd67ec4e4a6bcbbc428ea8671d7aac194b3` |
| Python | 3.13.13 |
| Platform | recorded in Manifest |
| Package versions | numpy / pandas / pyarrow / vnpy |
| `requirements_txt_sha256` | recorded |
| Dataset fingerprints | inherited identity continuity（Raw still restricted） |
| Dependency hashes | Spec / Fill / Auth / Proposal docs |

**C-ENV validation: SATISFIED**（identity checks only）

---

## Manifest contents（identity）

| Field | Value |
|-------|-------|
| `run_id` | `CAP_CTX_001_RUN005` |
| `eq` | `EQ-CTX-005` |
| `evidence_type` | `independence_evidence` |
| `mode` / `order` | `B+C` / `C→B` |
| `ier_protocol` / `ier_version` | `IER-CTX-005` / `1.0` |
| `ier_freeze_status` | **PENDING** |
| `artifact_access_policy.before_ier_freeze` | **NONE** |
| `protocol_fingerprint_sha256` | recorded |
| `observation_status` | **NONE** |
| `observation_start_authorized` | **false** |
| `execution_state` | `MANIFEST_DRAFT_C_ENV_CAPTURED` |
| `manifest_confirmation` | **DRAFT** |

---

## Explicit exclusions

```text
❌ observation_results
❌ interpretation
❌ k001_conclusion_bias
❌ independence_outcome
❌ registered_knowledge_action
```

---

## Next

```text
Manifest Draft + C-ENV ✓
        ↓
Manifest Confirmation（可选轻量）
        ↓
IER Freeze Ceremony / Review
        ↓
（explicit）Observation Authorization
        ≠
auto Observation
```

当前：**Identity frozen draft**；IER **PENDING**；Observation **NONE**。

---

## 修订记录

| 日期 | 说明 |
|------|------|
| 2026-07-21 | Manifest + C-ENV Draft；identity only；IER/Observation pending |
