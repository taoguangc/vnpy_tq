# Context eXecution Safety Definition — Design（CID_002）

> **Type**: Design（≠ Implementation · ≠ Observation · ≠ Alpha）  
> **Status**: **DESIGNED** ✓ · **Contract FROZEN**（`CXSD-CID_002-v0.1`）· **NOT IMPLEMENTED**  
> **Design ID**: `CXSD_CID_002_V0_1`  
> **Date**: 2026-07-22  
> **Authorization**: `Authorize Context Safety Definition Design`  
> **Charter**: [`STRATEGY_CONTEXT_SAFETY_DEFINITION_CHARTER_CID_002.md`](STRATEGY_CONTEXT_SAFETY_DEFINITION_CHARTER_CID_002.md) · `CXSDC_CID_002_V0_1`  
> **Contract**: [`STRATEGY_CONTEXT_EXECUTION_SAFETY_CONTRACT_CID_002.md`](STRATEGY_CONTEXT_EXECUTION_SAFETY_CONTRACT_CID_002.md) · **`CXSD-CID_002-v0.1` FROZEN**  
> **Parents**: `LCF_CID_002_V0_1` · `ACL_CID_002_V0_1` · `CC-CID_002-v1` · `CCED_CID_002_V0_1` · Decision 019 · CAP-CTX-001 CLOSED

## Design record

```text
================================================
CXSD_CID_002_V0_1

Name:     Context eXecution Safety Definition（消费安全定义）
Purpose:  Consumption-constraint contract ONLY
Delivered: Design + frozen contract
Frozen:   YES（CXSD-CID_002-v0.1）
Implemented: NO
Observation / backtest: NONE

≠ Strategy Upgrade
≠ Risk Alpha
≠ Production Approval
≠ Context Capability Upgrade
≠ CSD_CID_002（Component Split）
================================================
```

## 1. Problem statement

```text
Without CXSD, future consumers may treat Context as:
  · implicit Alpha
  · signal generator
  · sizing oracle
  · silent black-box merge with Strategy + Risk

CXSD defines how Context MAY be executed/consumed safely
in research — not whether Context predicts returns.
```

## 2. Six-layer design

### 2.1 Consumer Identity — who may read ContextState

| Consumer ID | May read ContextState | Notes |
|-------------|----------------------|-------|
| `CI_FILTER_ADAPTER` | YES | Research filter adapter only（outside G5 bytes） |
| `CI_MONITOR` | YES | Logging / evidence / dashboards · no trading effect |
| `CI_ORCH_MECH` | NO direct | May receive ALLOW/BLOCK decision from Filter only |
| `CI_ORCH_RISK` | NO direct | Same · no Context→sizing |
| `CI_DETECTOR` | NO | `detect()` must ignore Context（attested） |
| `CI_ENGINE` | NO | Fills only |
| `CI_HARNESS` | YES（setup/replay） | Must not inject Context into Detector |

```text
Read ≠ Write.
No consumer may write ContextState except the Context publisher
（P_CTX_ENGINE / A1 publisher）.
```

### 2.2 Permission Model

| Permission | Meaning | Effect on existing DetectionResult path |
|------------|---------|----------------------------------------|
| `ALLOW` | Permit stop-entry proposal unchanged | Proceed |
| `BLOCK` | Deny proposal | No order · emit `permission_denial` |
| `MONITOR` | Observe only | No change to entry path · audit only |

```text
Default for unknown/unsupported permission tag: BLOCK
（fail closed for trading path · MONITOR may still log）
```

Mapped to Decision 019 / CC roles:

| Role | Primary permission |
|------|-------------------|
| Filter | ALLOW / BLOCK |
| Permission | ALLOW / BLOCK |
| Monitoring | MONITOR |
| Risk Modifier | OUT OF CXSD v0.1 scope（requires separate contract） |

### 2.3 Forbidden Actions

```text
Context / Filter / Monitor MUST NOT:

  F1  generate DetectionResult / Signal
  F2  call buy / sell / cancel / cover
  F3  modify entry / stop / target
  F4  modify fixed_size / lots / risk_fraction / kill thresholds
  F5  invent Alpha score / expected return / rank
  F6  mutate G5 binding strategy or detector bytes
  F7  reopen RC001-B or reuse Closed experiment_id
  F8  collapse MECH + RISK + Context into one unlabeled PnL claim
```

### 2.4 Interface Boundary

```text
Publisher（Context）
  publish_state(bar_window) → ContextState
        │
        ▼  read-only
Filter Adapter
  decide(DetectionResult?, ContextState) → ALLOW|BLOCK + audit
        │
        ▼  gate only
Strategy Orchestrator（MECH or RISK surface）
  if ALLOW → existing submit path
  if BLOCK → no submit
        │
        ▼
Risk（RISK surface only）· unchanged by Context in CXSD v0.1
        │
        ▼
Execution Engine
```

```text
Monitor taps ContextState and/or permission events read-only.
Monitor never sits on the order path.
```

Pseudocode（normative intent · not implementation）:

```text
# ALLOWED
state = context.get_state()           # read
decision = filter.decide(signal, state)  # ALLOW|BLOCK|MONITOR

# FORBIDDEN
context.modify_signal(signal)
context.modify_position(pos)
context.generate_order(...)
context.set_size(...)
```

### 2.5 Failure Policy

| Context condition | Consumer behavior |
|-------------------|-------------------|
| `invalid` | **BLOCK** entry proposals · audit `context_state=invalid` |
| `missing` / timeout / schema fail | treat as **DEGRADED** → **BLOCK** trading path · MONITOR may continue |
| `DEGRADED` publisher flag | **BLOCK** · do not invent substitute state |
| Unsupported tag | **BLOCK** |
| Hash / identity mismatch on strategy | **ABORT** run（VMP）· no KEEP evaluation |

```text
Fail closed on the trading path.
Fail open only for MONITOR audit streams（may record gaps）.
```

### 2.6 Audit

Every Context-affecting decision MUST emit lineage fields:

| Field | Required |
|-------|----------|
| `experiment_id` | YES |
| `surface_id`（CC MECH\|RISK） | YES |
| `cxsd_version` | YES（e.g. `CXSD-CID_002-v0.1` when frozen） |
| `context_version` / engine_id | YES |
| `context_state` | YES |
| `permission`（ALLOW\|BLOCK\|MONITOR） | YES |
| `detector_binding` | YES |
| `strategy freeze_id` / hashes | YES |
| `signal_reason`（if any） | if DetectionResult present |
| `event`（PERMISSION_DENIAL \| PERMISSION_ALLOW \| MONITOR_NOTE） | YES |

```text
Evidence without these fields cannot support CXSD-compliance KEEP.
PnL fields remain descriptive only · never CXSD primary gates.
```

## 3. Relationship to existing freezes

| Artifact | Relation |
|----------|----------|
| `ACL_CID_002_V0_1` | Call ACL retained · CXSD specializes Context consumption |
| `CC-CID_002-v1` | Surface citation retained · CXSD adds Context execution safety |
| `EI_CID_002_V0_1` / `VMP_CID_002_V0_1` | Still mandatory for Research Maturity claims |
| CTX EXP001/002 | Capability evidence · not CXSD freeze · F1 unchanged |
| `CSD_CID_002_V0_1` | Component Split · orthogonal · deferred |

## 4. Explicit non-deliverables（this authorization）

```text
❌ Code / adapter changes
❌ Modify BROOKS_SCALP_FP
❌ Modify F1 Filter parameters or rule
❌ Alpha score
❌ Parameter search / backtest
❌ Production Bindable / deployment
❌ Contract FREEZE（needs separate auth）
```

## 5. Next gates（须另授）

```text
Contract Freeze: DONE → CXSD-CID_002-v0.1

Optional:
  Pause / Epoch 5 closure
  CXSD implementation charter（conformance only · no Alpha）
  Production Bindable Re-review（still WITHHELD residuals）
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | CXSD_CID_002_V0_1 DESIGNED · contract draft only |
| 2026-07-22 | Contract promoted → CXSD-CID_002-v0.1 FROZEN |
