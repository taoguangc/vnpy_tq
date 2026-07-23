# Bindable Pre-Review — CID_003（consumption interface only）

> **Type**: Bindable Pre-Review（≠ Bindable designation · ≠ Alpha · ≠ Production · ≠ new Observation）  
> **Status**: **COMPLETE** ✓  
> **Review ID**: `BPR_CID_003_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-50B（`授权你决定50次`）  
> **Parents**: `SAR_CID_003_V1_1` · `SIF_CID_003_V0_1_1` · `VR_CID_003_MECH_V0_1_1` · `AERC_CID_003_V0_1`  
> **Contracts**: `SAC-v1` · `SEVF-v1` · `CEMB-v1`

## Review record

```text
================================================
BPR_CID_003_V0_1

Bindable designation:     WITHHELD
Verified（H_MECH）:       RETAINED（E3 · unchanged）
Alpha:                    NONE（path CLOSED）

Asset classification:     Verified Mechanism Asset
                          with Open Capital Risk

Bindable Candidate:       NO（gaps · see §5）
Production Bindable:      NO
================================================
```

## 1. Scope

```text
✓ Name how CID_003 may be consumed without polluting surfaces
✓ Whether Bindable designation is warranted now
✗ Does NOT grant Bindable / Production / Alpha
✗ Does NOT run backtests or retune
✗ Does NOT reopen H_EDGE
```

## 2. Surface map（today）

| Surface | Identity | Status | Answers | Does not answer |
|---------|----------|--------|---------|-----------------|
| **Mechanism** | `STRAT_REV_OPP16_01@0.1.1` · `SIF_CID_003_V0_1_1` | **Verified H_MECH · E3** | Auditable OPP16→entry→exit | Capital survival · edge |
| **Risk wrapper** | *none* | **ABSENT** | — | — |

```text
OPP16@1.0.0                 ← morphology
        |
        +-- @0.1.0          ← broken adapter era（EXP001 HOLD · immutable）
        |
        +-- @0.1.1          ← mechanism Verified（adapter repair）
        |
        +-- @0.2.0          ← NOT CREATED（positioning design only below）
```

**Hard citation rule:**

```text
Cite H_MECH only against @0.1.1 hashes（Verified package EXP002/005/006）.
Never cite H_MECH KEEP as capital safety.
Never cite H_EDGE REVERT as deleting H_MECH.
Never treat Alpha NONE as “unverified mechanism”.
```

## 3. Identity completeness（SAC-v1 · @0.1.1）

| Field | Status | Note |
|-------|--------|------|
| strategy_id / version | ✓ | `STRAT_REV_OPP16_01` / `0.1.1` |
| source_manifest / hash | ✓ | includes adapter |
| parameter_manifest / hash | ✓ | frozen |
| market_scope | `UNBOUND_AT_ASSET` | CEMB-ok；Bindable consumer still needs EXP scope |
| execution_model | ✓ | 5m signal / 1m risk / fixed_size |
| evidence_lineage | ✓ | EXP002/005/006（+ edge REVERTs separate） |
| context_independence | ✓ | OPP16 ignores Context |
| architecture_attestation | ✓ | SIF § |

**Verdict:** sufficient to cite as **Verified Mechanism Asset**；**not** sufficient for Bindable lock without capital surface + consumer contract closure.

## 4. Interface map

### Morphology

```text
Detector: OPP16@1.0.0 · two-bar reversal · pure detect
```

### Orchestration

```text
StratRevOpp1601StrategyV011
ContextEngine → detect → stop entry → 1m STOP|TARGET|TIME_STOP → trade_log
on_rollover_adjust present
```

### Capital（gap）

```text
sizing: fixed_size=1 only
no risk fraction · no hard_max_lots · no equity kill-switch
EXP005 i: 爆仓 under size=100 × 1 lot × 200k（OPEN RISK）
```

## 5. Gaps blocking Bindable designation

| ID | Gap | Severity |
|----|-----|----------|
| G1 | No RISK / positioning lineage（@0.2.0 absent） | **Blocker** for dual-surface Bindable |
| G2 | No Consumer Contract `CC-CID_003-v*` | Blocker |
| G3 | Open Capital Risk on continuity universe（i） | Blocker for Standalone Trading language |
| G4 | Alpha NONE（expected · not a mech gap） | Blocks Alpha-flavored Bindable only |
| G5 | Registry wiring（direct detector construct） | Accepted deviation（declare） |

## 6. Interim consumption language（authorized wording）

```text
MAY cite as:
  “Verified Research Mechanism Asset（H_MECH · E3 · @0.1.1）
   with Open Capital Risk”

MUST NOT cite as:
  Bindable trading strategy
  Alpha asset
  capital-safe / Production-ready
  portfolio default component
```

## 7. Decision

```text
Bindable designation: WITHHELD
Next engineering:     Positioning lineage design（@0.2.0）— separate review
Implementation:       NOT authorized by this Pre-Review
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | BPR_CID_003_V0_1 COMPLETE · WITHHOLD |
