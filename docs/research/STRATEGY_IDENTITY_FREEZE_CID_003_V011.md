# Strategy Identity Freeze — STRAT_REV_OPP16_01@0.1.1

> **Type**: Candidate Identity Freeze（adapter repair lineage）  
> **Status**: **FROZEN** ✓  
> **Freeze ID**: `SIF_CID_003_V0_1_1`  
> **Date**: 2026-07-23  
> **Authorization**: `Authorize Implementation of CID_003 adapter repair lineage @0.1.1`（user: **A**）  
> **Parent**: `SIF_CID_003_V0_1` / `@0.1.0`（immutable）  
> **Engineering**: [`STRATEGY_ENGINEERING_REVIEW_CID_003_ZERO_TRADE.md`](STRATEGY_ENGINEERING_REVIEW_CID_003_ZERO_TRADE.md)

## Freeze record

```text
================================================
SIF_CID_003_V0_1_1

strategy_id: STRAT_REV_OPP16_01
version:     0.1.1
lifecycle:   Testing（H_MECH · rb/2024 KEEP via EXP002）
change:      adapter window length（_series_len / bars_from_am）
detector:    OPP16@1.0.0（morphology unchanged）
Bindable:    NO
Verified:    NO
Alpha:       NONE
EXP001@0.1.0 HOLD: IMMUTABLE（not reopened）
================================================
```

## 1. Frozen StrategyIdentity

| Field | Frozen value |
|-------|--------------|
| `strategy_id` | `STRAT_REV_OPP16_01` |
| `version` | `0.1.1` |
| `source_revision` | `7706213fe997189eeb9e1c9c6cfa9a4aecfd4f05`（@0.1.1 binding + adapter repair commit） |
| `git_anchor_head` | `7706213fe997189eeb9e1c9c6cfa9a4aecfd4f05` |
| `source_manifest` | §2 |
| `source_hash` | `6dee22fe6c1eaf5958defa3f94db614ece5991bdbc58abc93d281bbd7b1164b5` |
| `parameter_manifest` | §3（unchanged vs @0.1.0） |
| `parameter_hash` | `76b124f47414af2da2e0cdfdc6afcd5025d2cca8ae3a5583ba667cc7e1e31c57` |
| `market_scope` | `UNBOUND_AT_ASSET` |
| `execution_model` | same as `SIF_CID_003_V0_1` §4 |
| `evidence_lineage` | `["STRAT_RO16_EXP002"]` |
| `class_tags` | `["mean_reversion","reversal"]` |
| `context_independence` | `true` |
| `not_fabricated_for_context` | `true` |
| `detector_binding` | `OPP16@1.0.0` |
| `lineage_parent` | `SIF_CID_003_V0_1` |
| `campaign_id` | `CID_003` |

## 2. Frozen `source_manifest`

```json
[
  {
    "path": "strategies/paaf/adapters/vnpy_adapter.py",
    "sha256": "76d0257d457882f6076a75ea7c9ffb095d214c5b7d924d1a5b2a77f8da46e9d7"
  },
  {
    "path": "strategies/paaf/detectors/opp16_two_bar_reversal.py",
    "sha256": "ddb8378defa95ed1e2f3ccdd3cfd2ee3fbc25816a576524c21b6a42284ae9954"
  },
  {
    "path": "strategies/paaf/strat_rev_opp16_01.py",
    "sha256": "1a67cc5188514ef39e0db819a556b6c5435624b745b5f77e8aa9cd483d2c24d8"
  },
  {
    "path": "strategies/paaf/strat_rev_opp16_01_v011.py",
    "sha256": "8736f7ffc980b82d5e7d33e8bd7368c42e6457fc330f90b615f6185c2dc6b2c2"
  }
]
```

```text
Adapter is now in the identity surface（governance fix vs @0.1.0）.
@0.1.0 file bytes unchanged；v011 stamps strategy_version only.
```

## 3. Frozen `parameter_manifest`

```json
{
  "body_ratio": {"type": "float", "unit": "fraction", "value": 0.5},
  "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
  "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
  "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0}
}
```

## 4. What this is / is not

```text
IS: Candidate repair identity after ENG_REV_CID_003_ZERO_TRADE_V0_1
IS: Adapter fix so OPP16 can read real OHLC after ArrayManager warm-up
IS NOT: Observation / KEEP / Verified / Bindable / Alpha
IS NOT: rewrite of Closed STRAT_RO16_EXP001
IS NOT: parameter search
```

## 5. Explicit non-grants

```text
❌ SEVF Fill / Observation（须另授）
❌ H_MECH KEEP claim
❌ Bindable / Production / Epoch 7
❌ CID_002 H_EDGE reopen
```

## 6. Next（须另授）

```text
DONE: SEVF Spec V0_1_1 + Fill + Observation STRAT_RO16_EXP002 → KEEP
Next: further SEVF Fill（OOS / H_EDGE / H_ROBUST）· or Pause CID_003
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | @0.1.1 Candidate Identity Freeze |
| 2026-07-23 | `source_revision` → `7706213fe997189eeb9e1c9c6cfa9a4aecfd4f05` |
| 2026-07-23 | Next updated · EXP002 Fill PRE-REGISTERED |
| 2026-07-23 | Lifecycle → Testing · evidence_lineage EXP002 KEEP |
