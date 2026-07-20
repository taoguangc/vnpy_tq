# Platform Construction Phase

**Announced:** 2026-07-20  
**Anchor:** `architecture-baseline-v1`  
**Status:** Active（infrastructure design **closed**）  
**Epoch:** 1 — Evidence-driven Architecture  
**Epoch summary:** [`../releases/EPOCH_1_SUMMARY.md`](../releases/EPOCH_1_SUMMARY.md)

## Positioning

```text
Architecture Phase     — Ended
Platform Construction  — Started
Research (Alpha)       — Remains frozen until Research track resumes
Infrastructure design  — Closed（只建设、不扩地基）
```

This is **not** a new numbered product Phase replacing v0.3.  
It is the engineering posture after Architecture Baseline v1:

| Layer | Maturity |
|-------|----------|
| Governance | Stable |
| Contracts | Frozen |
| Capabilities | Building |

> New code should **consume existing capabilities**, not invent new foundations.

## Epoch（世界观，非 Version）

| Concept | Means |
|---------|--------|
| **Version**（如 v0.3.0） | 能力发布 |
| **Epoch** | 世界观 / 契约宇宙 |

| Epoch | Goal | Status |
|-------|------|--------|
| 0 | 寻找 Alpha（AFF → 证伪） | Ended |
| 1 | Evidence-driven Architecture | **Current** |
| 2 | 仅当核心契约必须重写 | Not authorized |

## Team culture（非 Decision / 非 Spec）

> **Every Sprint should leave the Architecture Baseline unchanged.**

## Two tracks

```text
Platform  ←→  Evidence Repository  ←→  Research
```

Do not couple Research modules directly into Platform modules.

## Development discipline

```text
Need → Existing Decision? → Existing Contract? → Implementation → Contract Tests → ABR
```

Pre-merge gate: [`REVIEW_CHECKLIST.md`](REVIEW_CHECKLIST.md).

## ABR series

| Review | Role |
|--------|------|
| ABR-001 | Architecture Baseline |
| ABR-002 | First Infrastructure Compliance Review |
| ABR-003（future） | Capability Compliance |

### ABR-002 checklist（预登记）

```text
Storage Compliance
Projection Compliance
Dependency Compliance
Contract Compliance
Knowledge Duplication
```

## Sprint 1 start line（when authorized — do not alter）

> **Start Platform Construction Sprint 1：Projection Layer consumes Evidence Repository under Architecture Baseline v1.**

Gates: Contract Tests + **Zero Knowledge Duplication**（organize knowledge only; never recompute Evidence）.

## Architecture Metrics（每 Sprint 结束）

```text
Decision Added:        0
Contract Added:        0
Domain Changed:        No
Baseline Changed:      No
Knowledge Duplicated:  No
ABR Required:          No
```

Frequent non-zeros → reassess whether a true architecture-level problem exists.

## Push policy

Local `architecture-baseline-v1` remains RC until Projection + ABR-002; then one coordinated push.
