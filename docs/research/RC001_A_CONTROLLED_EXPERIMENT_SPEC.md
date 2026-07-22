# RC001-A — Controlled Experiment Spec

> **Type**: Controlled Experiment Specification（Phase A · Context Filter consumption）  
> **Status**: **Confirmation PASS** ✓ — Spec v0.1 **CONFIRMED** · Execution **NOT AUTHORIZED** · Backtest **NOT STARTED**
> **Version**: 0.1  
> **Date**: 2026-07-21  
> **Path**: `docs/research/RC001_A_CONTROLLED_EXPERIMENT_SPEC.md`  
> **Confirmation**: [`RC001_A_SPEC_CONFIRMATION.md`](RC001_A_SPEC_CONFIRMATION.md) — **PASS**  
> **Spec Auth**: [`RC001_A_SPEC_AUTHORIZATION.md`](RC001_A_SPEC_AUTHORIZATION.md) — **GRANTED**  
> **Contract**: [`RC001_A_CONTRACT_REVIEW.md`](RC001_A_CONTRACT_REVIEW.md) — **PASS**  
> **Design**: [`RC001_A_CONTEXT_FILTER_DESIGN.md`](RC001_A_CONTEXT_FILTER_DESIGN.md) v0.1  
> **Filter policy**: **FP-RC001-A-v1**（immutable this Spec）  
> **Baseline**: OPP16 `1.0.0`（immutable this Spec）  
> **Capability**: NARROW Infrastructure Candidate · Decision 019  
> **experiment_id（proposed）**: `RC001_A_EXP001`  
> **run_id（proposed）**: `RC001_A_EXP001_RUN001`

### Spec Record（binding）

```text
================================================
RC001-A CONTROLLED EXPERIMENT SPEC v0.1

Status: CONFIRMED ✓ · Confirmation PASS

Unique variable: Context Filter（FP-RC001-A-v1）
CTRL: OPP16 → Trade Wrapper
FILT: OPP16 → Filter → Trade Wrapper

NOT: Execution · Backtest · Param search · Filter remapping
================================================
```

```text
Spec CONFIRMED ≠ Execution Auth ≠ Backtest authorized
FAIL ≠ K001 false ≠ Context worthless
```

---

## 0. Identity

| Field | Value |
|-------|-------|
| `campaign` | RC001-A |
| `experiment_id` | `RC001_A_EXP001` |
| `run_id` | `RC001_A_EXP001_RUN001` |
| `eq` | `EQ-RC001-A-CONTEXT-FILTER-SELECTION` |
| Parent lineage | `OPP16_EXP001`（Closed · immutable） |
| Arms | `RC001-A-CTRL` · `RC001-A-FILT` |
| Filter policy | `FP-RC001-A-v1` |
| Exit family | `EF-RC001-A-v1` |
| Context | `ContextState.v1` / `A1-CTX-PS-v1.0.0` |

---

## 1. Research Question（frozen）

### RQ-RC001-A-EXP001

> Under frozen Decision 001 data and identical OPP16 `1.0.0` signals, does applying **FP-RC001-A-v1** Context Filter improve **trade selection quality** versus Context-off control, without violating Decision 019 / NARROW consumption constraints?

### Not in scope

```text
❌ Does Context make money?
❌ Is OPP16 Alpha?
❌ Which Filter mapping maximizes Sharpe?
❌ Multi-symbol / multi-strategy horse race
```

### Unique experimental variable

```text
Change = Context consumption（Filter on vs off）
Everything else = frozen
```

---

## 2. Dataset / Universe / Window（frozen）

### 2.1 Universe

| Item | Locked |
|------|--------|
| Symbol | **`rb` only**（Phase A；matches OPP16_EXP001 lineage） |
| Multi-symbol | **OUT OF SCOPE**（requires new Spec / experiment_id） |

### 2.2 Time windows

| Window | Locked |
|--------|--------|
| Warmup（Context SMA / publisher） | `2023-10-01` → evaluation start（inclusive load；**no** evaluation trades before eval start） |
| Evaluation window | `2024-01-01` … `2025-12-31`（Asia/Shanghai calendar bounds） |
| Aligns with | OPP16_EXP001 period · A1 full window |

### 2.3 Data protocol（Decision 001）

| Item | Locked |
|------|--------|
| Source | TQSDK **offline** |
| Bar | **1m** raw · OPP16 on synthesized **5m** |
| Continuous | **CbC** automatic rollover |
| Adjustment | **Unadjusted** |
| Session | As present in stitched TQ dominant series（no ad-hoc session rewrite） |
| Dataset path | `data/tq/rb` |
| Fingerprints（must match at Execution） | See §2.4 |

### 2.4 Dataset fingerprints（rb · from A1 Manifest）

| Artifact | SHA256 |
|----------|--------|
| `manifest.json` | `bc62c8b606bf5c5018448e54aad841aa14a58f60482042f561e80f99ba8ed0fa` |
| `dominant_windows.json` | `051e5b48154a2228ec4e06ed361d8ebed40ba20f2fccec8fc8c953f9a169929b` |
| `rollover_map.parquet` | `170102046bdbe339aad14de20a9f95463838da18b077fab10e54381102e92a8e` |

Mismatch at Execution → **CONTRACT_INVALID / run abort**（no silent continue）.

### 2.5 Cost model（both arms identical）

| Item | Locked |
|------|--------|
| Commission | **Real** schedule for `rb` via project SYMBOL / TQ cost path（same loader both arms） |
| Slippage | **Real** slippage model（same both arms） |
| Zero-cost | **Forbidden** as primary arm |
| Compare zero-cost | Optional appendix only；**not** primary outcome |

### 2.6 Capital / sizing（both arms identical）

| Item | Locked |
|------|--------|
| Position size | **1 lot** fixed |
| Confidence → size | **Forbidden** |
| Pyramid / scale-in | **Forbidden** |

---

## 3. Arms & execution protocol

### 3.1 Topology（unchanged from Contract）

```text
CTRL (RC001-A-CTRL):
  Market Data → OPP16@1.0.0 → EF-RC001-A-v1 Trade Wrapper → Trade

FILT (RC001-A-FILT):
  Market Data → OPP16@1.0.0 → FP-RC001-A-v1 → EF-RC001-A-v1 Trade Wrapper → Trade
```

### 3.2 OPP16 lock（restate）

| Field | Value |
|-------|-------|
| File | `strategies/paaf/detectors/opp16_two_bar_reversal.py` |
| SHA256 | `ddb8378defa95ed1e2f3ccdd3cfd2ee3fbc25816a576524c21b6a42284ae9954` |
| `body_ratio` | `0.5` |
| Version | `1.0.0` |
| Edit in this experiment | **Forbidden** |

### 3.3 Filter lock（restate FP-RC001-A-v1）

| Condition | Permission |
|-----------|------------|
| INVALID validity OR `invalid` state | **BLOCK** |
| DEGRADED | **BLOCK** |
| `compression` + VALID | **ALLOW** |
| `expansion` + VALID | **MONITOR_ONLY**（no entry；attribution only） |
| REDUCE | **Not used** |

Context publish: bar-close causal A1 publisher；Filter consumes state for the **same** 5m decision bar（no future bars）.

### 3.4 Exit family **EF-RC001-A-v1**（single · both arms）

| Rule | Locked |
|------|--------|
| Signal | New OPP16 `DetectionResult` on completed **5m** bar |
| Entry | At signal bar `entry`（detector close reference）；1m engine may fill per project stop/entry conventions — **identical** both arms |
| Stop | Detector `stop`；evaluated on **1m**；**stop priority** same bar vs other exits |
| Take-profit | **None**（no RR grid） |
| Time stop | **60** completed **5m** bars after entry（aligns OPP16_EXP001 horizon N=60；**not** a tuned optimum claim） |
| Opposite signal | Flatten then allow new signal only if arm rules permit（identical both arms） |
| Session / flat | End-of-available-data flatten；no discretionary early exit |

```text
EF-RC001-A-v1 chosen for identity & auditability
        ≠
claim that N=60 is optimal
```

### 3.5 Position / concurrency

| Rule | Locked |
|------|--------|
| Max positions | **1**（flat or one direction） |
| Signal while in position | Ignore new entries until flat（both arms） |

---

## 4. Evaluation Contract

### 4.1 Primary metrics（decision-relevant）

| ID | Metric | Definition |
|----|--------|------------|
| **E1** | Trade count ratio | `n_FILT / n_CTRL` |
| **E2** | Retained-trade quality | Mean per-trade PnL（or R-multiple）of **executed** FILT trades vs CTRL trades；Spec uses **mean R** where R = PnL / |entry−stop| at entry |
| **E3** | Drawdown impact | `max_DD_FILT − max_DD_CTRL`（currency；lower/better for FILT） |
| **E4** | Filtered outcome attribution | For signals BLOCK/MONITOR_ONLY on FILT：forward outcome under CTRL path counterfactual（same EF wrapper） — mean R of skipped set |

### 4.2 Required counters

| ID | Counter |
|----|---------|
| A1 | `#` ALLOW / BLOCK / MONITOR_ONLY decisions on FILT signal stream |
| A2 | Missed large winners：count of CTRL top-decile R trades that FILT skipped |
| A3 | Tail：5% worst trade R（FILT vs CTRL）；report Δ |

### 4.3 Secondary（report only · not sole success）

| ID | Metric |
|----|--------|
| S1 | Total return / annualized return Δ |
| S2 | Sharpe Δ |
| S3 | Profit factor Δ |

### 4.4 Sample adequacy（gates before PASS/PARTIAL）

| Gate | Threshold |
|------|-----------|
| `n_CTRL` | **≥ 100** round-trips in evaluation window |
| `n_FILT` | **≥ 30**（else cannot claim FILTER_HELPFUL；may be FAIL or PARTIAL only if E3 strong — see §5） |
| Fingerprint match | Required |
| Arm identity audit | Required（hash / params / EF / cost） |

### 4.5 Anti-objectives

```text
❌ Maximize S1/S2
❌ Remap FP-RC001-A-v1 after peeking
❌ Drop costs to improve PASS rate
```

---

## 5. Outcome Mapping

### 5.1 Labels

| Outcome | Meaning |
|---------|---------|
| **PASS** | Filter improves selection quality without constraint violation |
| **PARTIAL** | Risk/structure improvement signals present；evidence incomplete or mixed |
| **FAIL** | No material selection-quality improvement under frozen rules |
| **INVALID** | Protocol / identity / Decision 019 violation |

### 5.2 Pre-registered decision rules

**INVALID** if any:

```text
OPP16 / Filter / EF / cost / fingerprint / future-leak / arm asymmetry detected
OR confidence used as size alpha
OR Filter remapped mid-run
```

**PASS** if all:

```text
NOT INVALID
AND n_CTRL ≥ 100 AND n_FILT ≥ 30
AND E1 ∈ [0.30, 0.95]          # not collapsed；some filtering occurred
AND E3 ≤ 0                     # FILT max DD not worse than CTRL
AND (E2_FILT ≥ E2_CTRL OR E4_skipped_mean_R ≤ 0)
AND A2 / n_CTRL_top_decile ≤ 0.50   # did not miss >50% of CTRL top-decile winners
```

**PARTIAL** if:

```text
NOT INVALID
AND n_CTRL ≥ 100
AND NOT PASS
AND (
      E3 < 0                                    # DD improved
   OR (E1 ∈ [0.30, 0.95] AND E4_skipped_mean_R ≤ 0)
   OR (n_FILT ≥ 30 AND E2_FILT ≥ E2_CTRL)
)
AND not clearly catastrophic over-filter (E1 ≥ 0.15)
```

**FAIL** otherwise（including clear over-filter E1 < 0.15 with no E3 improvement, or no primary improvement）.

### 5.3 Binding non-interpretations

```text
FAIL ≠ K001 false
FAIL ≠ Context has no research value
FAIL ≠ revoke A1 / NARROW Candidate automatically
PASS ≠ OPP16 is Alpha
PASS ≠ Gate PASS / FULL Candidate / RC001 Accepted
PASS ≠ license live trading
```

---

## 6. Negative Evidence handling

| Case | Handling |
|------|----------|
| FAIL / PARTIAL | First-class EvidenceRecord；append-only under `RC001_A_EXP001` |
| INVALID | Abort claim；fix contract；new experiment_id if redesign |
| Skipped winners (A2) | Must appear in report even if PASS |
| Over-filter | Prefer FAIL or PARTIAL — never hide via metric shopping |
| Closed OPP16_EXP001 inconclusive | Remains parent lineage；**not** rewritten |

```text
Negative Evidence = equal citizen（Decision 017 / Governance）
```

---

## 7. Artifacts（Execution phase · not now）

| Artifact | Path（planned） |
|----------|----------------|
| Manifest | `research/output/evidence/RC001_A_EXP001/` |
| CTRL / FILT trade CSVs | same |
| Evaluation JSON | `evaluation.json` |
| EvidenceRecord | `evidence_record.json` |
| Filter decision log | `filter_decisions.parquet` or CSV |

Must include lineage: `manifest_id` · `runtime_hash` · dataset fingerprints · `schema_version` · OPP16 hash · FP id · EF id.

---

## 8. Governance bindings

| Binding | Effect |
|---------|--------|
| NARROW Candidate | Filter / permission only |
| Decision 019 | No signal / sizing alpha from Context |
| P5 PARTIAL residual | Carry qualification on claims |
| Gate CONDITIONAL | Unchanged by this Spec |
| Contract PASS | Required precursor — satisfied |

---

## 9. Lifecycle / next gates

```text
Spec WRITTEN → Spec Review → Confirmation PASS ✓
        ↓
Execution Authorization（另授）
        ↓
Backtest（first legal offline strategy-consumption run）
        ↓
Evidence Review
```

### Current position

```text
Controlled Experiment Spec: CONFIRMED ✓
Confirmation: PASS ✓
Execution Authorization: NOT GRANTED
Backtest: NOT STARTED
```

### Next authorization entry

```text
Authorize RC001-A Execution
```

Confirmation doc: [`RC001_A_SPEC_CONFIRMATION.md`](RC001_A_SPEC_CONFIRMATION.md)

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | Spec WRITTEN：rb 2024–2025；EF-RC001-A-v1；门槛冻结 |
| 2026-07-21 | 0.1 | **Confirmation PASS** — Spec frozen；Execution 另授 |
