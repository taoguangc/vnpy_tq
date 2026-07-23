# Strategy Identity Freeze — CID_013 / STRAT_SMC_OB_LONG_01@0.1.0

> **Type**: Candidate Identity Freeze（≠ Bindable · ≠ Testing evidence · ≠ Alpha）  
> **Status**: **FROZEN** ✓  
> **Freeze ID**: `SIF_CID_013_V0_1`  
> **Date**: 2026-07-24  
> **Authorization**: Delegation-25BD  
> **Design**: `NSAD_CID_013_V0_1` · `SMC_OB_LONG_MS_V0_1`  
> **Contracts**: `SAC-v1` · docs/07  
> **Implementation**: `strategies/paaf/strat_smc_ob_long_01.py`

## Freeze record

```text
================================================
SIF_CID_013_V0_1

strategy_id: STRAT_SMC_OB_LONG_01
version:     0.1.0
lifecycle:   Candidate
Identity:    FROZEN ✓

Bindable:    NO
Verified:    NO
Alpha:       NONE
Family:      beyond-PA SMC structure（≠ opp/ PA shelf）
CID_002–012: NOT forks · Alpha paths remain CLOSED / PAUSED
================================================
```

## 1. Frozen StrategyIdentity

| Field | Frozen value |
|-------|--------------|
| `strategy_id` | `STRAT_SMC_OB_LONG_01` |
| `version` | `0.1.0` |
| `source_revision` | c0fb19f8297f6d885f575f432044b0ea5bfc5f61 |
| `source_hash` | `a835a8bb8c1dfa6a18e610e323351cd4620070ce1b8ac4f410e72c5de833d42d` |
| `parameter_hash` | `8ea775b14b6f4a44eaaf494aa39aa650f6da4d44ff408e3dedb6f762a4e06214` |
| `class_tags` | `["smc","order_block","structure","long_only"]` |
| `context_independence` | `true` |
| `detector_binding` | `SMC_OB_LONG@1.0.0` |
| `campaign_id` | `CID_013` |
| `morphology_spec` | `SMC_OB_LONG_MS_V0_1` |

## 2. Frozen `source_manifest`

```json
[
  {
    "path": "strategies/paaf/detectors/smc_order_block_long.py",
    "sha256": "d37de32e70c288e18cfbd1cc43573041c59831659c299dd30898dae9888e523f"
  },
  {
    "path": "strategies/paaf/strat_smc_ob_long_01.py",
    "sha256": "4e9e6c2d1c245674da61cfa2b3e80328ee41543bf4ea1b095127f3395a572f49"
  }
]
```

## 3. Frozen `parameter_manifest`

```json
{
  "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
  "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
  "ob_stop_buffer": {"type": "float", "unit": "ticks", "value": 2.0},
  "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
  "smc_min_bars": {"type": "int", "unit": "bars_5m", "value": 16},
  "smc_pool_bars": {"type": "int", "unit": "bars_5m", "value": 12}
}
```

## 4. Frozen `execution_model`

```text
signal_timeframe: 5m
risk_timeframe:   1m
order_entry:      stop at detector entry（high）
stop:             ob_low − ob_stop_buffer × tick
target:           entry ± risk_reward × |entry−stop|
rollover:         on_rollover_adjust + detector.adjust_levels
```

## 5. Explicit non-grants

```text
❌ Observation / KEEP / Bindable / Alpha by Freeze alone
❌ Resume CID_003–012
❌ VWAP/Delta hybrid restore under this identity
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-24 | SIF_CID_013_V0_1 FROZEN · Delegation-25BD |
