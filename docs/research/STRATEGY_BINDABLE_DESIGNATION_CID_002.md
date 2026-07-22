# Bindable Designation — CID_002

> **Type**: Bindable Designation Review（≠ Alpha · ≠ Production · ≠ Context routing permission）  
> **Status**: **COMPLETE** ✓ · **DESIGNATION GRANTED**（dual-surface · scoped）  
> **Review ID**: `BDR_CID_002_V0_1`  
> **Date**: 2026-07-22  
> **Authorization**: `Authorize Bindable Designation Review`  
> **Docket**: [`STRATEGY_BINDABLE_DESIGNATION_DOCKET_CID_002.md`](STRATEGY_BINDABLE_DESIGNATION_DOCKET_CID_002.md) · `BDD_CID_002_V0_1`  
> **Contracts**: `SAC-v1` · `SEVF-v1` · `CC-CID_002-v1` · `CPA_CID_002_V0_1`  
> **G5 revision**: `833ae4740e6da3e2e3a42899d2bd4229f61785d6`

## Designation record

```text
================================================
BDR_CID_002_V0_1

Bindable:     GRANTED（dual-surface · research consumption）
Alpha:        NONE
Production:   NO
Context routing permission: NOT GRANTED by this designation
                （eligible to *design* a future Context Consumer EXP）

Mandatory:    CC-CID_002-v1 · cite Surface ID before every claim
================================================
```

## 1. Objects designated（must not collapse）

| Surface | Identity | Freeze | Bindable class |
|---------|----------|--------|----------------|
| **MECH** | `STRAT_TREND_BROOKS_SCALP_02@0.1.1` | `SIF_CID_002_V0_1_1` | **Bindable Research Mechanism Asset** |
| **RISK** | `STRAT_TREND_BROOKS_SCALP_02@0.2.0` | `SIF_CID_002_V0_2_0` | **Bindable Capital-Gated Research Consumer** |

```text
Detector binding（both）: BROOKS_SCALP_FP@0.1.0
source_revision（both）: 833ae4740e6da3e2e3a42899d2bd4229f61785d6
```

| Field check | MECH `@0.1.1` | RISK `@0.2.0` |
|-------------|---------------|---------------|
| `source_hash` vs G5 blobs | `1877dffe…` ✓ | `5c089251…` ✓ |
| `parameter_hash` | `3ff06189…` ✓ | `7ff1fe99…` ✓ |
| Lifecycle evidence | Verified H_MECH · **E3** | H_CAPITAL_GATE portable KEEP |
| Architecture / Context independence | attested（detect ignores Context） | inherits + risk wrapper |
| Consumer Contract | Surface=`MECH` | Surface=`RISK` |

## 2. Intake checklist（at designation time）

| # | Item | Status |
|---|------|--------|
| 1 | MECH Verified | ✓ `VR_CID_002_MECH_V0_1_1` + E3 A1 |
| 2 | RISK capital portable | ✓ EXP009 · EXP010 |
| 3 | Consumer Contract | ✓ `CC-CID_002-v1` |
| 4 | Pipeline attestation | ✓ `CPA_CID_002_V0_1` |
| 5 | SAC fields | ✓ freezes complete |
| 6 | Gaps G0–G4/G6/G7 | ✓ closed / mitigated |
| 7 | G5 commit + source_revision | ✓ `833ae47…` |
| 8 | Explicit designation auth | ✓ this review |

## 3. Accepted deviations（declared · not blockers）

```text
• Detector constructed directly（no Registry catalog wiring）
• ContextEngine.update for orchestration；detect() discards Context
• RISK equity_est ≈ engine balance（kill uses equity_est）
• Dual-surface still version-coupled on one strategy_id
  （future Strategy vs Risk Controller split = CSD design only）
```

## 4. What Bindable means here

```text
MAY:
  • Be cited as a frozen, hash-locked research consumption asset
  • Be selected as the StrategyIdentity in a *future* Context Consumer
    experiment design（new experiment_id · separate auth）
  • Be composed only under CC-CID_002-v1 surface rules

MUST NOT be read as:
  • Alpha / edge proven
  • Production / live default
  • Permission to route Context into entries or sizing alpha
  • Portfolio weights or capital allocation advice
  • License to merge MECH KEEP with RISK KEEP into one PnL story
```

## 5. Explicit non-grants

```text
❌ Alpha claim
❌ Production / E4
❌ Automatic Context Consumer Experiment authorization
❌ RC001-B reopen
❌ Single collapsed “Brooks Scalp Bindable” identity erasing surfaces
```

## 6. Decisions

```text
1. Bindable Designation Review COMPLETE.
2. GRANTED for MECH @0.1.1 and RISK @0.2.0 as separate Bindable classes.
3. CC-CID_002-v1 is mandatory for all consumers.
4. Context Consumer Experiment Design is now *eligible* but NOT authorized.
```

## 7. Next（须另授）

```text
P. Authorize Context Consumer Experiment Design
   （first time CAP-CTX-era Context may meet a Bindable strategy asset）

D. Commit remaining Epoch 5 docs/scripts/tests（optional hygiene）

C. Keep Epoch 5 research pause otherwise
```

## Hard guarantees

```text
✓ No Alpha / Production stamp
✓ No new Observation under this authorization
✓ Dual-surface separation preserved
✓ G5 hash lock re-verified at review time
```

## Machine record

`research/output/evidence/STRATEGY_BINDABLE_DESIGNATION_CID_002/designation.json`

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | BDR_CID_002_V0_1 · Bindable GRANTED（dual-surface） |
