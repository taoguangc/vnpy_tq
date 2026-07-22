# Context Consumer Experiment Fill — CTX_CID002_EXP001

> **Type**: Experiment Fill / Pre-registration（Observation CLOSED）  
> **Status**: **CLOSED** ✓ · Observation **COMPLETE** · Outcome **KEEP**  
> **Experiment ID**: `CTX_CID002_EXP001`  
> **Date**: 2026-07-22  
> **Authorization**: Fill · then `Authorize Context Consumer Experiment Observation`  
> **Design**: [`STRATEGY_CONTEXT_CONSUMER_EXPERIMENT_DESIGN_CID_002.md`](STRATEGY_CONTEXT_CONSUMER_EXPERIMENT_DESIGN_CID_002.md) · `CCED_CID_002_V0_1`  
> **Eval**: [`STRATEGY_CONTEXT_CONSUMER_EVALUATION_CTX_CID002_EXP001.md`](STRATEGY_CONTEXT_CONSUMER_EVALUATION_CTX_CID002_EXP001.md)  
> **ER**: [`STRATEGY_CONTEXT_CONSUMER_EVIDENCE_REVIEW_CTX_CID002_EXP001.md`](STRATEGY_CONTEXT_CONSUMER_EVIDENCE_REVIEW_CTX_CID002_EXP001.md)  
> **Parents**: `BDR_CID_002_V0_1` · `CC-CID_002-v1` · `SIF_CID_002_V0_1_1` · CAP-CTX A1 · Decision 019  
> **RC001-B**: **NOT REOPENED**（new `experiment_id`）  
> **Machine**: `research/output/evidence/CTX_CID002_EXP001/`

## Record

```text
================================================
CTX_CID002_EXP001 — CLOSED · KEEP

Hypothesis:     H_CTX_FILTER ADMITTED（filter active）
Strategy:       MECH @0.1.1 only（RISK wrapper OUT）
Context role:   Filter / Permission only（Decision 019）
N0 / N1 / D:    1303 / 919 / 563
Observation:    COMPLETE
Alpha claim:    NONE
================================================
```

## 1. Identity bindings（must match at run）

### 1.1 Strategy（MECH surface）

| Field | Pre-registered value |
|-------|----------------------|
| `consumer_surface` | `MECH` |
| `strategy_id` | `STRAT_TREND_BROOKS_SCALP_02` |
| `version` | `0.1.1` |
| `freeze_id` | `SIF_CID_002_V0_1_1` |
| `source_hash` | `1877dffe2108ba4237469b52bccc589d479811d4aea82c2764900cf74ad1d4c8` |
| `parameter_hash` | `3ff061891488a9d9f5641cf147efc1e70c8d4cb8410540858d8b727bd485d1ab` |
| `source_revision` | `833ae4740e6da3e2e3a42899d2bd4229f61785d6` |
| `detector_binding` | `BROOKS_SCALP_FP@0.1.0` |
| `strategy_class` | `strategies.paaf.brooks_scalp_paaf_strategy_v011.BrooksScalpPaafStrategyV011` |
| `consumer_contract` | `CC-CID_002-v1` |

At run: recompute hashes；mismatch → **abort**（do not evaluate）.

### 1.2 Context artifact（A1 Published State）

| Field | Pre-registered value |
|-------|----------------------|
| `context_engine_id` | `paaf.context_published_state` |
| `schema_version` | `ContextState.v1` |
| `context_version` | `A1-CTX-PS-v1.0.0` |
| `a1_spec` | `CAP_CTX_A1_ENGINEERING_PUBLISHED_STATE_SPECIFICATION` v0.2 |
| `a1_fill` | `CAP_CTX_A1_PRE_REGISTRATION_FILL` v0.2 |
| `a1_evidence_anchor` | `CAP_CTX_A1_RUN001` Evidence Review **PASS** |
| `consumption_role` | `filter`（Decision 019） |

```text
PAAF ContextEngine v0.1.1（always UNKNOWN）is NOT the filter source for this EXP.
Filter reads A1 ContextState.context_state only.
```

## 2. Primary hypothesis（one）

**Family**: `H_CTX_FILTER`

**Primary hypothesis（falsifiable）**:

> Under the declared scope and frozen MECH `@0.1.1` identity, applying the
> pre-registered Context Filter F1（§3）changes the auditable allowed-entry /
> closed-trade set relative to the unfiltered MECH baseline in a
> non-PnL-primary, pre-registered way — while Context never generates entries
> and never supplies sizing alpha.

**Null / baseline**:

```text
Baseline B0 = same MECH @0.1.1 run with Filter F1 DISABLED
  （detector→entry path identical to STRAT_BS02_EXP005-class orchestration）

Filtered B1 = identical identity/data/costs with Filter F1 ENABLED
```

**Not claimed**:

```text
❌ Context improves return / Sharpe / drawdown
❌ Alpha / Production
❌ RISK @0.2.0 interaction
❌ RC001-B continuity
```

## 3. Single variable + Filter F1（frozen）

```text
VARIABLE_0: Context Filter F1 on/off
  OFF = B0 baseline
  ON  = B1 filtered

No detector / exit / sizing / RISK wrapper changes.
```

### Filter F1（Permission gate）

```text
On each MECH signal intent（DetectionResult ≠ None）at bar t:
  read A1 ContextState at t（causal · closed bars ≤ t）

  if context_state == "expansion":
      PERMIT → allow stop-entry proposal（unchanged MECH execution）
  elif context_state in {"compression", "invalid"}:
      DENY → no order；record permission_denial audit row
  else:
      DENY → treat as unknown/unsupported tag；permission_denial

Context MUST NOT:
  invent DetectionResult
  modify stop/target/size
  write buy/sell directly
```

A1 primary publish rule（bound from A1 Fill v0.2）:

```text
if warmup fail or non-finite: context_state = invalid
else if range_ratio < 1: context_state = compression
else: context_state = expansion
```

## 4. Market scope package（CEMB）

| Item | Value |
|------|-------|
| Symbol | `rb.SHFE` |
| size / pricetick | `10` / `1.0` |
| Period | `2024-01-01` … `2024-12-31` |
| Warmup | `2023-12-01` |
| Data | docs/07 · TQ offline · 1m · CbC · unadjusted |
| rate / slippage / capital | `0.00003` / `1.0` / `200000` |
| fill_binding | `VNPY_CTA_BACKTEST_ENGINE_DEFAULTS_AT_EXP_REGISTRATION` |

```text
Single symbol · single year — first Context Consumer EXP.
Universe expansion requires a new experiment_id.
```

## 5. Decision rule（pre-registered · non-PnL primary）

Let:

```text
N0 = B0 auditable closed exits with reason ∈ {STOP,TARGET,TIME_STOP}
     and detector_binding = BROOKS_SCALP_FP@0.1.0
N1 = same for B1
D  = count of permission_denial audit rows in B1
```

| Outcome | Rule |
|---------|------|
| **REVERT** | Hash mismatch · OR Context writes entries · OR sizing alpha from Context · OR decision uses PnL/Sharpe as primary gate |
| **HOLD** | Run completes but `N0 < 1` · OR (`N1 == N0` AND `D == 0`)（filter inert） |
| **KEEP** | `N0 ≥ 1` AND (`N1 ≠ N0` OR `D ≥ 1`) AND all B1 exits still detector-attributed AND no Context entry generation |

```text
PnL / Sharpe / PF may be logged as descriptive only.
They MUST NOT decide KEEP/HOLD/REVERT.
```

## 6. Required artifacts（at Observation）

```text
research/output/evidence/CTX_CID002_EXP001/
  run_metadata.json          # hashes · surface · filter version · outcomes
  baseline_trades_audit.csv  # B0
  filtered_trades_audit.csv  # B1
  permission_denials.csv     # B1 denials
  context_state_sample.json  # optional echo of A1 tags used
```

## 7. Implementation（delivered at Observation）

```text
Adapter: strategies/paaf/context_consumer/
  a1_published_state.py
  brooks_scalp_ctx_filter_v011.py
Harness: scripts/run_ctx_cid002_exp001.py
G5 binding bytes: NOT mutated（source_hash MATCH）
```

## 8. Explicit non-claims（still）

```text
❌ Parameter search / PnL optimization
❌ RISK @0.2.0 in this EXP
❌ Mutate Bindable binding bytes
❌ Reopen RC001-B
❌ Claim Context trading value / Alpha
```

## 9. Closed

```text
Observation COMPLETE · KEEP · ER PASS
Further Context EXPs require new experiment_id + authorization
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | PRE-REGISTERED under Fill authorization |
| 2026-07-22 | Observation KEEP · CLOSED |
