# RC001-A — Contract Review

> **Type**: Experiment Contract Review（≠ Spec · ≠ Execution · ≠ Backtest）  
> **Status**: **PASS** ✓ — Eligible for Controlled Experiment Spec（另授）  
> **Version**: 0.1  
> **Date**: 2026-07-21  
> **Path**: `docs/research/RC001_A_CONTRACT_REVIEW.md`  
> **Authorization**: [`RC001_A_CONTRACT_REVIEW_AUTHORIZATION.md`](RC001_A_CONTRACT_REVIEW_AUTHORIZATION.md) — **GRANTED**  
> **Design**: [`RC001_A_CONTEXT_FILTER_DESIGN.md`](RC001_A_CONTEXT_FILTER_DESIGN.md) v0.1  
> **Candidate**: NARROW Infrastructure · Decision 019  
> **Baseline lineage**: `OPP16_EXP001` Closed（immutable）

### Review Record（binding）

```text
================================================
RC001-A CONTRACT REVIEW v0.1

Verdict: PASS ✓

Locks:
  Baseline OPP16          LOCKED
  Filter mapping          LOCKED（single path）
  Dual-arm identity       LOCKED
  Evaluation Contract     LOCKED

Eligible next:
  Authorize RC001-A Controlled Experiment Spec

NOT authorized:
  Backtest · Param search · OPP16 modification · Alpha claim
================================================
```

```text
Contract Review PASS
        ≠
Experiment success
        ≠
Context improves returns
        ≠
RC001 Accepted
```

---

## 1. Baseline Strategy Lock（OPP16）

### 1.1 Identity

| Field | Locked value |
|-------|----------------|
| `detector_id` | `OPP16` |
| `detector_version` | `1.0.0` |
| `opportunity_id` | `OPP16` |
| Source file | `strategies/paaf/detectors/opp16_two_bar_reversal.py` |
| File SHA256（Contract freeze） | `ddb8378defa95ed1e2f3ccdd3cfd2ee3fbc25816a576524c21b6a42284ae9954` |
| Code revision（git HEAD at Review） | `f9e56cd67ec4e4a6bcbbc428ea8671d7aac194b3` |
| Lineage parent | `OPP16_EXP001` / `OPP16_EXP001_RUN001` — **Closed** · inconclusive/HOLD |
| RFC | `docs/specs/OPP16_TWO_BAR_REVERSAL_EXPERIMENT_RFC.md` — Accepted / Frozen |

```text
RC001-A consumes OPP16 as external signal source
        ≠
re-opens or rewrites OPP16_EXP001
        ≠
promotes OPP16 to Production / Alpha
```

### 1.2 Parameter freeze

| Parameter | Locked |
|-----------|--------|
| `body_ratio` | `0.5` |
| Timeframe | **5m**（from frozen 1m synthesis） |
| Context inside detector | **None**（`del context` · EXP001 semantics） |
| Symmetry | Long/Short shared OPP16 |
| Cross-bar state | None（single completed-bar detect） |

### 1.3 Signal logic freeze（entry/stop **references** from detector）

From RFC §2.1 / detector `1.0.0`（unchanged）：

| Direction | Conditions |
|-----------|------------|
| LONG | prev bearish；`prev_body_ratio ≥ 0.5`；`bar.close > prev mid` |
| SHORT | mirror |

| Field | Locked reference |
|-------|------------------|
| `entry` | signal bar `close` |
| `stop`（structure ref） | LONG=`bar.low`；SHORT=`bar.high` |
| Output | `DetectionResult \| None` only |

**Contract rule**: RC001-A **must not** edit `opp16_two_bar_reversal.py` or Closed EXP001 artifacts. Any detector behavior change → new `detector_version` + **new** Contract Review（out of Phase A）。

### 1.4 RC001-A execution wrapper（shared by CTRL & FILT · not OPP16）

OPP16 is observation detector；RC001-A needs an **identical** trade wrapper on both arms:

| Rule | Locked for Phase A |
|------|---------------------|
| Signal source | OPP16 `1.0.0` only |
| When to consider entry | New `DetectionResult` on completed 5m bar |
| CTRL path | signal → trade wrapper（no ContextFilter） |
| FILT path | signal → ContextFilter → trade wrapper iff permission allows execution |
| Stop | Use detector `stop` reference；**same** on both arms |
| Exit / target / time-stop | **Deferred to Controlled Experiment Spec** — must be identical on both arms；**one** pre-registered exit family only |
| Sizing | Fixed / identical on both arms；**no** confidence→size alpha |
| Forbidden | Change stop relative to OPP16；add confirm bars；change period |

```text
Trade wrapper ∈ RC001-A experiment layer
OPP16 detector ∈ frozen external baseline
FILT − CTRL = ContextFilter only
```

### 1.5 Data & cost freeze（Decision 001）

| Item | Locked |
|------|--------|
| Data | TQSDK offline · **1m** · CbC · unadjusted |
| Synthesis | 1m → 5m for OPP16 |
| Cost model | **Real commission + real slippage** on **both** arms（same schedule） |
| Universe / window | Frozen in Controlled Experiment Spec（must match both arms） |

---

## 2. Dual-Arm Identity Lock

### Required topology

```text
CTRL:
  Market Data → OPP16 → Trade Wrapper → Trade

FILT:
  Market Data → OPP16 → Context Filter → Trade Wrapper → Trade
```

### Forbidden topology

```text
❌ OPP16+Context fused inside detector
❌ Different OPP16 params / period / stop / symbols per arm
❌ FILT retunes after seeing CTRL results
```

### Identity checklist

| Check | Verdict |
|-------|---------|
| Same OPP16 version + body_ratio | **PASS** |
| Same data / cost / universe / window | **PASS**（Spec must restate） |
| Differ only by ContextFilter | **PASS** |
| No silent OPP16 edit | **PASS**（file hash locked） |

---

## 3. Filter Mapping Lock（single path）

### Input

```text
ContextState.v1 · A1-CTX-PS-v1.0.0
context_state ∈ {compression, expansion, invalid}
validity ∈ {VALID, DEGRADED, INVALID}
```

### Timestamp rule

```text
Filter uses ContextState published for the same decision bar boundary
（bar close → publish → filter）
No future ContextState
```

### Locked mapping **FP-RC001-A-v1**（single path · pre-registered）

| Condition | Permission | Trade effect | Attribution |
|-----------|------------|--------------|-------------|
| `validity == INVALID` OR `context_state == invalid` | **BLOCK** | no new entry | `filtered_invalid` |
| `validity == DEGRADED` | **BLOCK** | no new entry | `filtered_degraded` |
| `context_state == compression` AND `validity == VALID` | **ALLOW** | execute via wrapper | `allowed_compression` |
| `context_state == expansion` AND `validity == VALID` | **MONITOR_ONLY** | **no** new entry | `monitored_expansion_skip` |

```text
REDUCE: NOT USED in Phase A（avoids size-alpha channel）
```

### Hard rules

```text
✓ Pre-registered before any backtest
✓ Single path — no grid of mappings
❌ If results look bad → change mapping → re-run（forbidden without new experiment_id + new Contract）
❌ permission invents direction / expected_return
❌ confidence drives size
```

### Semantic note

```text
MONITOR_ONLY ≠ ALLOW
MONITOR_ONLY = skip execution + record for missed-trade / tail analysis
```

---

## 4. Evaluation Contract Lock

### Purpose

Evaluate **trade selection quality under Filter** — not “does Context make money?”

### Primary（must report · decision-relevant）

| ID | Metric | Role |
|----|--------|------|
| E1 | Trade count（CTRL vs FILT）+ % change | Over-filter detection |
| E2 | Selection stability（Spec-defined dispersion of per-trade outcomes） | Core quality |
| E3 | Drawdown impact（FILT vs CTRL） | Risk |

### Required attribution counters

| ID | Counter |
|----|---------|
| A1 | `#` blocked / monitored-skipped signals |
| A2 | Missed large winners（Spec: top-k CTRL winners blocked by FILT） |
| A3 | Tail-risk change（e.g. worst-N trade PnL or left-tail quantile — Spec freezes one） |

### Secondary（report only · **not** success sole criterion）

| ID | Metric |
|----|--------|
| S1 | Return change |
| S2 | Sharpe change |
| S3 | Profit factor |

### Explicit anti-conclusion

```text
❌ Context 增加收益 = 成功
❌ Maximize S1/S2 via mapping/param search
```

### Outcome classes（Spec will attach numeric gates）

| Class | Meaning |
|-------|---------|
| FILTER_HELPFUL | E1–E3 support improved selection / risk without catastrophic under-sample |
| FILTER_HARMFUL | Over-filter or risk/stability worsens materially |
| FILTER_INCONCLUSIVE | No stable separation / insufficient sample |
| CONTRACT_INVALID | P1–P3 / Decision 019 / arm identity violated |

**Contract Review does not decide** FILTER_HELPFUL — only that metrics/classes are frozen for Spec.

---

## 5. Success Standard of *this* Review

| Question | Answer |
|----------|--------|
| Is baseline locked? | **YES** |
| Is Filter single-path locked? | **YES**（FP-RC001-A-v1） |
| Are arms identical except Filter? | **YES** |
| Is Evaluation non-return-centric? | **YES** |
| Allow Controlled Experiment Spec? | **YES** |

```text
Contract Review PASS
        ↓
Eligible: Authorize RC001-A Controlled Experiment Spec
        ≠
Authorize Backtest
```

---

## 6. Residual qualifications（carry forward）

| Residual | Binding |
|----------|---------|
| NARROW Candidate | Infrastructure consumption only |
| P5 PARTIAL | Falsification gap remains |
| Price Family residual | Independence qualification remains |
| OPP16_EXP001 inconclusive | Baseline ≠ proven Alpha |
| Gate CONDITIONAL | ≠ Gate PASS |

---

## 7. Next

```text
Authorize RC001-A Controlled Experiment Spec → Spec WRITTEN
        ↓
Authorize RC001-A Spec Review / Confirmation（另授）
        ↓
Execution Authorization（另授）
        ↓
Backtest
```

Spec: [`RC001_A_CONTROLLED_EXPERIMENT_SPEC.md`](RC001_A_CONTROLLED_EXPERIMENT_SPEC.md) v0.1 — Confirmation **PENDING**.

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | **PASS** — OPP16 lock + FP-RC001-A-v1 + Evaluation Contract；Eligible for Spec |
