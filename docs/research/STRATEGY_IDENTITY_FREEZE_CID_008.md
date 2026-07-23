# Strategy Identity Freeze — CID_008 / STRAT_TREND_OPP02_01@0.1.0

> **Type**: Candidate Identity Freeze（≠ Bindable · ≠ Testing evidence · ≠ Alpha）  
> **Status**: **FROZEN** ✓  
> **Freeze ID**: `SIF_CID_008_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AJ  
> **Design**: `NSAD_CID_008_V0_1` · `OPP02_MS_V0_1`  
> **Contracts**: `SAC-v1` · `CEMB-v1` · docs/07  
> **Implementation**: `strategies/paaf/strat_trend_opp02_01.py`

## Freeze record

```text
================================================
SIF_CID_008_V0_1

strategy_id: STRAT_TREND_OPP02_01
version:     0.1.0
lifecycle:   Candidate
Identity:    FROZEN ✓

Bindable:    NO
Testing:     NOT STARTED（needs SEVF Spec + Fill + Observation）
Verified:    NO
Alpha:       NONE
CID_002–007: NOT forks · Alpha paths remain CLOSED / PAUSED
================================================
```

## 1. Frozen StrategyIdentity

| Field | Frozen value |
|-------|--------------|
| `strategy_id` | `STRAT_TREND_OPP02_01` |
| `version` | `0.1.0` |
| `source_revision` | `81c90b4d6e20fa560c4b5052cf6af8eeb2b5c8d3`（binding bytes first committed） |
| `git_anchor_head` | `81c90b4d6e20fa560c4b5052cf6af8eeb2b5c8d3` |
| `source_manifest` | §2 |
| `source_hash` | `c6e47760e11290b171aec8d50c7f727606ed5df147ecb6eaa3b660fa62de9f99` |
| `parameter_manifest` | §3 |
| `parameter_hash` | `06b64730fa61b0b1c9411feb332140d5a7b4911339c035ac30f0ede406db7a86` |
| `market_scope` | `UNBOUND_AT_ASSET` |
| `execution_model` | §4 |
| `evidence_lineage` | `[]` |
| `class_tags` | `["trend","pullback","ema"]` |
| `context_independence` | `true` |
| `not_fabricated_for_context` | `true`（seed from legacy OPP02 mixin extract） |
| `detector_binding` | `OPP02@1.0.0` |
| `campaign_id` | `CID_008` |
| `morphology_spec` | `OPP02_MS_V0_1` |

## 2. Frozen `source_manifest`

```json
[
  {
    "path": "strategies/paaf/detectors/opp02_ema_pullback.py",
    "sha256": "bd71de70ac45809677bd618a31969e95ce7d02d3cb1ec5993bc8a64167b089f5"
  },
  {
    "path": "strategies/paaf/strat_trend_opp02_01.py",
    "sha256": "980410358d0d5e4492a64f7e9dd568ae01501f378136f2edfe2af690d460759f"
  }
]
```

## 3. Frozen `parameter_manifest`

```json
{
  "atr_period": {"type": "int", "unit": "bars", "value": 14},
  "ema_period": {"type": "int", "unit": "bars", "value": 20},
  "ema_pullback_min_body_ratio": {"type": "float", "unit": "fraction", "value": 0.35},
  "ema_pullback_touch_atr": {"type": "float", "unit": "atr_multiple", "value": 1.0},
  "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
  "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
  "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
  "wick_max_fraction": {"type": "float", "unit": "fraction", "value": 0.45}
}
```

## 4. Frozen `execution_model`

```text
signal_timeframe:     5m
risk_timeframe:       1m
order_entry:          stop order at detector entry（high/low trigger）
stop:                 from OPP02 DetectionResult.stop
target:               entry ± risk_reward × |entry−stop| when detector target absent
sizing:               fixed_size
max_hold:             max_hold_bars on 1m
rollover:             on_rollover_adjust
```

## 5. Explicit non-grants

```text
❌ Observation / KEEP / Verified / Bindable / Alpha / Production by Freeze alone
❌ Resume CID_003–007
❌ Bit-identical pa_cta OPP02 claim · BROOKS identity merge
```

## 6. Next（须另授）

```text
DONE: STRAT_TO02_EXP001 H_MECH KEEP（rb/2024 · attributed=2834）
Next: H_EDGE diagnostic Fill · OR · H_MECH OOS/multi-symbol · OR · Pause
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | SIF_CID_008_V0_1 FROZEN · Delegation-25AJ |
| 2026-07-23 | `source_revision` → `81c90b4d6e20fa560c4b5052cf6af8eeb2b5c8d3` |
| 2026-07-23 | Lifecycle note · EXP001 KEEP · Delegation-25AJ |
