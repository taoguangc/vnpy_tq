# Strategy Identity Freeze — CID_010 / STRAT_REV_OPP13_01@0.1.0

> **Type**: Candidate Identity Freeze（≠ Bindable · ≠ Testing evidence · ≠ Alpha）  
> **Status**: **FROZEN** ✓  
> **Freeze ID**: `SIF_CID_010_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AP  
> **Design**: `NSAD_CID_010_V0_1` · `OPP13_MS_V0_1`  
> **Contracts**: `SAC-v1` · `CEMB-v1` · docs/07  
> **Implementation**: `strategies/paaf/strat_rev_opp13_01.py`

## Freeze record

```text
================================================
SIF_CID_010_V0_1

strategy_id: STRAT_REV_OPP13_01
version:     0.1.0
lifecycle:   Candidate
Identity:    FROZEN ✓

Bindable:    NO
Testing:     NOT STARTED（needs SEVF Spec + Fill + Observation）
Verified:    NO
Alpha:       NONE
CID_002–009: NOT forks · Alpha paths remain CLOSED / PAUSED
================================================
```

## 1. Frozen StrategyIdentity

| Field | Frozen value |
|-------|--------------|
| `strategy_id` | `STRAT_REV_OPP13_01` |
| `version` | `0.1.0` |
| `source_revision` | `445b5a7ee0d61e9abd85d4560f32247312e4cea7`（binding bytes first committed） |
| `git_anchor_head` | `445b5a7ee0d61e9abd85d4560f32247312e4cea7` |
| `source_manifest` | §2 |
| `source_hash` | `d20147d23918edac9d94cdea5572155dacc8375218b62c0aa4a822eac303d1de` |
| `parameter_manifest` | §3 |
| `parameter_hash` | `1f95584dfc3a17c18ad41210a53e53fbe050988850d656f881686d80e7c11405` |
| `market_scope` | `UNBOUND_AT_ASSET` |
| `execution_model` | §4 |
| `evidence_lineage` | `[]` |
| `class_tags` | `["mean_reversion","day_boundary","range_fail"]` |
| `context_independence` | `true` |
| `not_fabricated_for_context` | `true`（seed from legacy OPP13 Path A） |
| `detector_binding` | `OPP13@1.0.0` |
| `campaign_id` | `CID_010` |
| `morphology_spec` | `OPP13_MS_V0_1` |

## 2. Frozen `source_manifest`

```json
[
  {
    "path": "strategies/paaf/detectors/opp13_day_boundary_touch.py",
    "sha256": "ee710e3c63d3be45734a3dc9436c72439f95041562e1573b48863afa17576411"
  },
  {
    "path": "strategies/paaf/strat_rev_opp13_01.py",
    "sha256": "37a2b0d9e431719c6bf39acd7b14ddb412e3906bf575de3fc3cf8cb8d05969f2"
  }
]
```

## 3. Frozen `parameter_manifest`

```json
{
  "boundary_reversal_close_ratio": {"type": "float", "unit": "fraction", "value": 0.3},
  "boundary_reversal_shadow_ratio": {"type": "float", "unit": "fraction", "value": 0.45},
  "day_boundary_tolerance": {"type": "float", "unit": "ticks", "value": 5.0},
  "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
  "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
  "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0}
}
```

## 4. Frozen `execution_model`

```text
signal_timeframe:     5m
risk_timeframe:       1m
order_entry:          stop order at detector entry（high/low）
stop:                 from OPP13 DetectionResult.stop
target:               entry ± risk_reward × |entry−stop|
sizing:               fixed_size
max_hold:             max_hold_bars on 1m
rollover:             on_rollover_adjust + detector.adjust_levels
```

## 5. Explicit non-grants

```text
❌ Observation / KEEP / Verified / Bindable / Alpha / Production by Freeze alone
❌ Resume CID_003–009
❌ Double-top path under this identity
```

## 6. Next（须另授）

```text
DONE: STRAT_RO13_EXP001 H_MECH KEEP（rb/2024 · attributed=41）
Next: H_EDGE diagnostic Fill · OR · H_MECH OOS/multi-symbol · OR · Pause
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | SIF_CID_010_V0_1 FROZEN · Delegation-25AP |
| 2026-07-23 | `source_revision` → `445b5a7ee0d61e9abd85d4560f32247312e4cea7` |
| 2026-07-23 | Lifecycle note · EXP001 KEEP · Delegation-25AP |
