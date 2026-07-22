# RC001_A_EXP001 — Execution Report

> **Type**: Controlled Experiment Execution Report（≠ Evidence Review final claim alone）  
> **Status**: **COMPLETE** · machine outcome **PARTIAL**  
> **Date**: 2026-07-21  
> **Auth**: [`RC001_A_EXECUTION_AUTHORIZATION.md`](RC001_A_EXECUTION_AUTHORIZATION.md) — **GRANTED**  
> **Spec**: [`RC001_A_CONTROLLED_EXPERIMENT_SPEC.md`](RC001_A_CONTROLLED_EXPERIMENT_SPEC.md) v0.1 **CONFIRMED**  
> **Artifacts**: `research/output/evidence/RC001_A_EXP001/`  
> **Command**: `.\.venv\Scripts\python.exe scripts\run_rc001_a_exp001.py`

### Execution Record

```text
================================================
RC001_A_EXP001_RUN001

Execution: COMPLETE ✓
Integrity: PASS ✓
Machine Outcome: PARTIAL

Universe: rb · 2024–2025 · warmup 2023-10-01
Baseline: OPP16@1.0.0（hash match）
Filter: FP-RC001-A-v1
Exit: EF-RC001-A-v1
================================================
```

---

## 1. Execution Integrity

| Check | Result |
|-------|--------|
| OPP16 SHA256 | **MATCH** locked |
| rb fingerprints | **MATCH** A1 / Spec |
| Single variable = Filter | **YES** |
| No Filter remap / param search | **YES** |

---

## 2. Primary metrics（E1–E4）

| ID | Value | Note |
|----|-------|------|
| n_CTRL | 2224 | ≥100 ✓ |
| n_FILT | 1643 | ≥30 ✓ |
| **E1** | 0.7388 | in [0.30, 0.95] ✓ |
| **E2** mean R CTRL | -1.3984 | |
| **E2** mean R FILT | -1.3977 | FILT ≥ CTRL（marginal） |
| **E3** maxDD Δ（FILT−CTRL） | +34931.30 | FILT DD **worse** → blocks PASS |
| **E4** skipped mean R | -1.4004 | ≤0 ✓（skipped set not positively valuable） |

---

## 3. Attribution（A1–A3）

| ID | Value |
|----|-------|
| A1 ALLOW / BLOCK / MONITOR_ONLY | 2585 / 0 / 1995 |
| A2 missed top-decile | 83 / 223（ratio ≈ 0.372 ≤ 0.50） |
| A3 tail5 R Δ | -0.0053（见 `evaluation.json`） |

---

## 4. Outcome（Spec §5.2）

```text
PASS:    NO（E3 > 0）
PARTIAL: YES（E1 in band · E4 ≤ 0 · E2_FILT ≥ E2_CTRL · sample OK）
FAIL:    NO
INVALID: NO
```

```text
Machine Outcome = PARTIAL
```

### Binding non-claims

```text
PARTIAL ≠ Alpha
PARTIAL ≠ Gate PASS
PARTIAL ≠ RC001 Accepted
PARTIAL ≠ multi-symbol capability
FAIL/PARTIAL ≠ K001 false
```

---

## 5. Secondary（report only）

See `evaluation.json` → `secondary`（S1–S3）. **Not** used as sole success criterion.

---

## 6. Artifacts

| File | Role |
|------|------|
| `RC001_A_EXP001_RUN_MANIFEST.json` | Run identity |
| `trades_CTRL.json` / `trades_FILT.json` | Round-trips |
| `filter_decisions.json` | FILT decisions |
| `evaluation.json` | E1–E4 / A1–A3 / outcome |
| `evidence_record.json` | Evidence shell + lineage |

---

## 7. Next

```text
Evidence Review → COMPLETE · PARTIAL confirmed
        ↓（另授）
RC001 Decision（Route A / B）
```

Evidence Review: [`RC001_A_EXP001_EVIDENCE_REVIEW.md`](RC001_A_EXP001_EVIDENCE_REVIEW.md)
