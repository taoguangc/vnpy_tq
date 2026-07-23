# Bindable Designation — CID_003

> **Type**: Bindable Designation Review（≠ Alpha · ≠ Production · ≠ Context routing permission）  
> **Status**: **COMPLETE** ✓ · **DESIGNATION GRANTED**（dual-surface · scoped）  
> **Review ID**: `BDR_CID_003_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-50D（`授权你决定50次`）  
> **Contracts**: `SAC-v1` · `SEVF-v1` · `CC-CID_003-v1` · `CPA_CID_003_V0_1`  
> **Parents**: `VR_CID_003_MECH_V0_1_1` · `VR_CID_003_RISK_V0_2_0` · `BPR_CID_003_V0_1` · `AERC_CID_003_V0_1`

## Designation record

```text
================================================
BDR_CID_003_V0_1

Bindable:     GRANTED（dual-surface · research consumption）
Alpha:        NONE（path CLOSED）
Production:   NO
Context routing permission: NOT GRANTED
                （eligible to *design* a future Context Consumer EXP）

Mandatory:    CC-CID_003-v1 · cite Surface ID before every claim
================================================
```

## 1. Objects designated（must not collapse）

| Surface | Identity | Freeze | Bindable class |
|---------|----------|--------|----------------|
| **MECH** | `STRAT_REV_OPP16_01@0.1.1` | `SIF_CID_003_V0_1_1` | **Bindable Research Mechanism Asset** |
| **RISK** | `STRAT_REV_OPP16_01@0.2.0` | `SIF_CID_003_V0_2_0` | **Bindable Capital-Gated Research Consumer** |

```text
Detector binding（both）: OPP16@1.0.0
```

| Field check | MECH `@0.1.1` | RISK `@0.2.0` |
|-------------|---------------|---------------|
| `source_hash` | `6dee22fe…1164b5` ✓ | `0e796e22…4012` ✓ |
| `parameter_hash` | `76b124f4…1c57` ✓ | `fce3f995…aa22` ✓ |
| Lifecycle | Verified H_MECH · E3 | Verified H_CAPITAL_GATE · E3 |
| Consumer Contract | Surface=`MECH` | Surface=`RISK` |

## 2. Intake checklist

| # | Item | Status |
|---|------|--------|
| 1 | MECH Verified E3 | ✓ `VR_CID_003_MECH_V0_1_1` |
| 2 | RISK Verified E3 | ✓ `VR_CID_003_RISK_V0_2_0`（EXP007–009） |
| 3 | Consumer Contract | ✓ `CC-CID_003-v1` |
| 4 | Pipeline attestation | ✓ `CPA_CID_003_V0_1` |
| 5 | SAC freezes | ✓ `@0.1.1` / `@0.2.0` |
| 6 | BPR gaps G1/G2 | ✓ closed（RISK exists · CC frozen） |
| 7 | G3 Standalone Trading | **mitigated**：research Bindable only；not Standalone Trading Asset |
| 8 | Alpha path | ✓ CLOSED · NONE（not a blocker for research Bindable） |
| 9 | Explicit designation auth | ✓ Delegation-50D |

## 3. Accepted deviations（declared · not blockers）

```text
• Detector constructed directly（no Registry catalog wiring）
• ContextEngine.update for orchestration；OPP16 detect ignores Context
• RISK equity_est ≈ engine path（kill uses equity_est）
• Dual-surface version-coupled on one strategy_id
• EXP001 @0.1.0 HOLD retained（engineering parent · not Bindable object）
```

## 4. What Bindable means here

```text
MAY:
  • Be cited as frozen, hash-locked research consumption assets
  • Be selected as StrategyIdentity in a *future* Context Consumer
    experiment design（new experiment_id · separate auth）
  • Be composed only under CC-CID_003-v1 surface rules

MUST NOT be read as:
  • Alpha / edge proven（H_EDGE REVERT×2 retained）
  • Production / live default / E4
  • Permission to route Context into entries or sizing alpha
  • Portfolio weights or capital allocation advice
  • License to merge MECH + RISK into one PnL story
```

## 5. Explicit non-grants

```text
❌ Alpha claim / H_EDGE reopen
❌ Production Bindable / Epoch 7
❌ Automatic Context Consumer Experiment authorization
❌ Standalone Trading Asset / live-safe stamp
❌ Single collapsed “OPP16 Bindable” erasing surfaces
```

## 6. Decisions

```text
GRANT:  Research Bindable on MECH @0.1.1 and RISK @0.2.0
        under CC-CID_003-v1
WITHHOLD: Production · Alpha · Context routing permission
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | BDR_CID_003_V0_1 COMPLETE · GRANTED（scoped） |
