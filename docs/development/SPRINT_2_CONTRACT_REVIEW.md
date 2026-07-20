# Sprint 2 — Validation Projection Contract Review

**Status:** Pass — proceed to Implementation  
**Date:** 2026-07-20  
**Sprint start line:** Validation Projection consumes Evidence Repository under Architecture Baseline v1

## Question

Can Validation Projection land entirely inside existing Accepted Contracts without expansion?

## Verdict

```text
PASS — No Contract expansion required
```

| Contract | Fit |
|----------|-----|
| Evidence Domain | Read existing `EvidenceRecord` fields only; no schema change |
| Append-only Storage | Read-only via `EvidenceReadView`; no write semantics change |
| Projection Layer | Same class as Portfolio：derived view；aggregate / filter / reference allowed |

## Mapping（Projection presentation only）

| View field | Source（Domain / metadata） | Invented? |
|------------|----------------------------|-----------|
| decision / status | `EvidenceRecord.decision`（display alias KEEP→ACCEPTED, REVERT→REJECTED） | No（alias only） |
| classification | `subject_kind` | No |
| symbol | `metadata["symbol"]` if present else `""` | No |
| evidence_type | `metadata["evidence_type"]` if present else `""` | No |
| metrics | `EvidenceRecord.metrics` copy | No |
| parent / provenance | `metadata["parent"]` + artifact uri/hash | No |
| blocking / suggested_next | Derived from **existing decision** (+ optional metadata blockers） | Aggregate only |

## Stop conditions（would abort Sprint）

- Need new Domain object for Promotion
- Need to recompute Evaluation / invent scores
- Need foundation Contract change

None triggered.

## Proceed

Implementation → Contract Tests → ABR-003 Prep → Sprint Report.
