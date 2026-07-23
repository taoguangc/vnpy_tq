# CID_003 Engineering Review — Zero-Trade Path

> **Type**: Engineering Review（≠ Bindable · ≠ Alpha · ≠ parameter search · ≠ Observation）  
> **Status**: **COMPLETE** ✓  
> **Review ID**: `ENG_REV_CID_003_ZERO_TRADE_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: `Authorize Engineering Review for CID_003 zero-trade path`  
> **Parents**: `SAR_CID_003_V0_5` · `SIF_CID_003_V0_1`（@0.1.0）· `STRAT_RO16_EXP001` HOLD  
> **Implementation**: **AUTHORIZED + DONE** under user option **A**（2026-07-23）· see [`STRATEGY_IMPLEMENTATION_CID_003_ADAPTER_REPAIR_V011.md`](STRATEGY_IMPLEMENTATION_CID_003_ADAPTER_REPAIR_V011.md) · Identity `SIF_CID_003_V0_1_1`

## Review record

```text
================================================
ENG_REV_CID_003_ZERO_TRADE_V0_1

EXP001 HOLD (0 trades): EXPLAINED
Primary class:        ENGINEERING DEFECT（adapter window length）
Secondary:            entry/fill path NOT reached after AM warm-up
@0.1.0 binding bytes: NOT MUTATED
Closed EXP001:        IMMUTABLE（HOLD retained）
Repair lineage:       IMPLEMENTED @0.1.1（adapter + SIF_CID_003_V0_1_1）
Bindable / Alpha:     NOT GRANTED
================================================
```

## 1. Problem separation（mandatory）

| Problem | Question | EXP001 status |
|---------|----------|---------------|
| H_MECH / morphology | Does OPP16 two-bar reversal produce auditable exits under docs/07? | **Unresolved**（HOLD）— blocked by engineering |
| Engineering integrity | Can detector see real OHLC after ArrayManager warm-up? | **FAIL** |
| Stop-entry / fill path | Do stop orders fill when a live signal exists? | **Not reached** after warm-up（no live signals） |
| Parameter / edge | Is `body_ratio=0.5` “too sparse”? | **Not decidable** under broken window |

```text
Zero trades ≠ H_MECH REVERT
Zero trades ≠ “OPP16 has no Alpha”
Zero trades = mechanism chain not observable under current adapter bug
```

## 2. Findings

### 2.1 Primary defect — `bars_from_am` / `_series_len`

```text
File: strategies/paaf/adapters/vnpy_adapter.py
_series_len(am) returns am.count unconditionally when count is int ≥ 0.

vn.py ArrayManager:
  · open/high/low/close arrays have fixed length = size（CID_003 uses 200）
  · count increments without bound（≫ size after warm-up）
  · valid indices for series[i]: 0 .. size-1（or negative −size .. −1）

bars_from_am(am, 2):
  n = count（e.g. 17910）
  start = n - 2
  reads series[start:n] → IndexError → _bar_at returns OHLC = 0.0

OPP16TwoBarReversalDetector.detect → bars_from_am(am, 2)
  → prev_range ≈ 0 → always None after count > size
```

**Reproduced（unit ArrayManager size=10, count=25）:**

| Access | Result |
|--------|--------|
| `last_bar(am)`（index −1） | correct close |
| `bars_from_am(am, 2)` | closes `[0.0, 0.0]` |
| true `am.close[-2], am.close[-1]` | non-zero |

**Why EXP001 still saw hash match + AM inited:**  
Identity hashes only pin detector + orchestrator paths（not adapter）. Engine warmed 5m AM (~17910 bars) correctly; detector path was silent after warm-up.

**Why offline diagnostics saw ~1 hit:**  
While `count ≤ size`, positive indices still land inside the array. After warm-up, hits drop to zero for the rest of the year. That “extreme sparsity” is largely an **artifact of the defect**, not a settled morphology claim.

### 2.2 Secondary path（not root cause of year-long zero）

| Layer | Observation |
|-------|-------------|
| BarGenerator 5m | Present；`on_5min_bar` updates AM then detects |
| Stop entry | `_submit_stop_entry` only runs when `detect` ≠ None |
| Rollover hook | Present on @0.1.0；EXP001 had no missing-hook WARN |
| 1m risk / exits | Never exercised（no fills） |

Stop-entry / fill integrity remains a **residual** question for post-repair smoke — not the explanation of EXP001’s full-year silence.

### 2.3 Test gap

```text
tests/test_paaf_adapter.py uses _FakeAM with count == len(close).
Never asserts ArrayManager count > size.
Bug invisible to current suite.
```

### 2.4 Identity / evidence governance

```text
SIF_CID_003_V0_1 source_manifest:
  · opp16_two_bar_reversal.py
  · strat_rev_opp16_01.py
  · adapter NOT included

⇒ Adapter fix changes runtime evidence without changing frozen @0.1.0 source_hash.
⇒ Must NOT silently re-run EXP001 under same experiment_id / version claim.
⇒ Repair = new version + new experiment_id；expand source_manifest to include adapter.
```

## 3. Decision

```text
DO NOT edit STRAT_REV_OPP16_01@0.1.0 binding bytes to flip EXP001
DO NOT reopen / rewrite Closed STRAT_RO16_EXP001
DO NOT parameter-search body_ratio / RR to “create trades”
DO NOT grant H_MECH KEEP / Verified / Bindable / Alpha from this review

RECOMMEND repair lineage（implementation 须另授）:

  strategy_id:   STRAT_REV_OPP16_01
  version:       0.1.1
  change class:  engineering — ArrayManager window length in bars_from_am
  adapter fix:   _series_len = min(count, len(close series)) when both known
                 （or equivalent: index via negative lookback only）
  tests:         real ArrayManager count > size regression
  identity:      new SIF；source_manifest MUST include
                 strategies/paaf/adapters/vnpy_adapter.py
  detector:      OPP16@1.0.0 morphology bytes unchanged unless hash forced by
                 packaging；prefer adapter-only diff
  next EXP:      new id（e.g. STRAT_RO16_EXP002）H_MECH smoke rb/2024
                 under @0.1.1 — pre-register before Observation
```

## 4. Recommended repair sketch（design only）

```python
# Conceptual — not applied under this review
def _series_len(am: Any) -> int:
    close = getattr(am, "close", None)
    array_len = len(close) if isinstance(close, Sequence) else 0
    count = getattr(am, "count", None)
    if isinstance(count, int) and count >= 0:
        if array_len > 0:
            return min(count, array_len)
        return count
    return array_len
```

Optional hardening: `bars_from_am` may prefer negative indices (`-lookback .. -1`) so length math cannot walk past the buffer.

## 5. Non-goals

```text
❌ PnL improvement claim
❌ body_ratio / fixed_size / risk_reward search
❌ Alternate-symbol EXP as substitute for fixing the adapter
❌ Treat EXP001 HOLD as morphology failure
❌ Production / Epoch 7 / CID_002 H_EDGE reopen
```

## 6. Next（须新授权 · pick）

```text
DONE: A. Authorize Implementation of CID_003 adapter repair lineage @0.1.1
A'. Authorize SEVF Fill for STRAT_RO16_EXP002（H_MECH @0.1.1）
C.  Pause CID_003 Testing
NOT: retune @0.1.0 · flip Closed EXP001 · Alpha claim
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | Engineering Review COMPLETE · root cause documented · repair design-only |
| 2026-07-23 | Implementation A DONE · @0.1.1 FROZEN |
