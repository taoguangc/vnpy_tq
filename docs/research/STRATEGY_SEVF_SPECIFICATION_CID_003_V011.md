# SEVF Specification — CID_003 / STRAT_REV_OPP16_01@0.1.1

> **Type**: Asset-bound SEVF Specification（repair lineage）  
> **Status**: **SPECIFIED** ✓  
> **Spec ID**: `SEVF_SPEC_CID_003_V0_1_1`  
> **Date**: 2026-07-23  
> **Authorization**: bundled with `Authorize SEVF Fill / Pre-registration for STRAT_RO16_EXP002（H_MECH @0.1.1）`  
> **Parent Spec**: [`SEVF_SPEC_CID_003_V0_1`](STRATEGY_SEVF_SPECIFICATION_CID_003.md)（@0.1.0 · immutable）  
> **Identity**: [`SIF_CID_003_V0_1_1`](STRATEGY_IDENTITY_FREEZE_CID_003_V011.md)  
> **Reason**: `SEVF_SPEC_CID_003_V0_1` §2 does not apply after `source_hash` drift；new Spec required

## Spec record

```text
================================================
SEVF_SPEC_CID_003_V0_1_1

Status: SPECIFIED ✓
Bound identity: STRAT_REV_OPP16_01@0.1.1
Inherits: hypothesis / metrics / outcome / evidence policy from V0_1 §§3–10
Fill / Observation: Fill authorized for EXP002；Observation NOT by this Spec alone
Alpha: NONE
================================================
```

## 1. Bound test object（immutable for this Spec）

| Field | Required value |
|-------|----------------|
| `strategy_id` | `STRAT_REV_OPP16_01` |
| `version` | `0.1.1` |
| `source_hash` | `6dee22fe6c1eaf5958defa3f94db614ece5991bdbc58abc93d281bbd7b1164b5` |
| `parameter_hash` | `76b124f47414af2da2e0cdfdc6afcd5025d2cca8ae3a5583ba667cc7e1e31c57` |
| `freeze_id` | `SIF_CID_003_V0_1_1` |
| `detector_binding` | `OPP16@1.0.0` |
| `source_revision` | `7706213fe997189eeb9e1c9c6cfa9a4aecfd4f05`（or later tip **only if** hash-match） |
| `strategy_class` | `StratRevOpp1601StrategyV011` |

```text
Any further source_hash / parameter_hash drift
  → this Spec does not apply
  → require new identity version + new Spec ID
```

## 2. Inherited policy

```text
Hypothesis families · forbidden shapes · market-scope Fill rules ·
data/cost/execution contract · single-variable rule · metrics ·
outcomes · evidence contract · lifecycle gates:
  → identical to SEVF_SPEC_CID_003_V0_1 §§3–10
  except every EXP must bind §1 of THIS Spec（not V0_1 §2）
```

## 3. Relation to EXP001

```text
STRAT_RO16_EXP001 @0.1.0 HOLD: IMMUTABLE · under V0_1 only
EXP002 is NOT a rewrite of EXP001
EXP002 single variable = repaired identity under same rb/2024 continuity scope
```

## 4. Explicit non-authorizations（this Spec alone）

```text
❌ Observation / backtest execution
❌ Parameter or PnL optimization
❌ Flip Closed EXP001
❌ Alpha / Bindable / Verified / Production
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | `SEVF_SPEC_CID_003_V0_1_1` SPECIFIED with EXP002 Fill |
