# SEVF Specification — CID_003 / STRAT_REV_OPP16_01@0.2.0（RISK surface）

> **Type**: Asset-bound SEVF Specification（capital / positioning lineage）  
> **Status**: **SPECIFIED** ✓  
> **Spec ID**: `SEVF_SPEC_CID_003_V0_2_0`  
> **Date**: 2026-07-23  
> **Authorization**: bundled with Fill `STRAT_RO16_EXP007`  
> **Identity**: [`SIF_CID_003_V0_2_0`](STRATEGY_IDENTITY_FREEZE_CID_003_V020.md)  
> **Parent MECH Spec**: `SEVF_SPEC_CID_003_V0_1_1`（@0.1.1 · H_MECH only · immutable）

## Spec record

```text
================================================
SEVF_SPEC_CID_003_V0_2_0

Bound identity: STRAT_REV_OPP16_01@0.2.0
Surface:        RISK / capital（≠ MECH Verified citation）
Primary family: H_CAPITAL_GATE
Alpha:          NONE
================================================
```

## 1. Bound test object

| Field | Required value |
|-------|----------------|
| `strategy_id` | `STRAT_REV_OPP16_01` |
| `version` | `0.2.0` |
| `source_hash` | `0e796e226b5906f22bdc4ce622f522788985a05525d2f65ae05e40fb2c474012` |
| `parameter_hash` | `fce3f995d1421ada2152e591362700ed2a24d93c7ff3259394261f254cd7aa22` |
| `freeze_id` | `SIF_CID_003_V0_2_0` |
| `detector_binding` | `OPP16@1.0.0` |
| `strategy_class` | `StratRevOpp1601StrategyV020` |
| `consumer_surface` | `RISK` |

## 2. Hypothesis policy

```text
Allowed primary: H_CAPITAL_GATE（capital survivability under @0.2.0 controls）
Forbidden as primary under this Spec:
  · H_MECH rewrite of @0.1.1 Verified package
  · H_EDGE / Alpha reopen
  · PnL maximize
```

## 3. Citation rule

```text
Cite capital results only against @0.2.0 hashes.
Cite H_MECH Verified only against @0.1.1 hashes.
Never collapse surfaces.
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | SPECIFIED with EXP007 Fill |
