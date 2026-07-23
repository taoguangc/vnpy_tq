# Strategy Identity Freeze — CID_004 / STRAT_REV_OPP12_01@0.1.0

> **Type**: Candidate Identity Freeze（≠ Bindable · ≠ Testing evidence · ≠ Alpha）  
> **Status**: **FROZEN** ✓  
> **Freeze ID**: `SIF_CID_004_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25O  
> **Design**: `NSAD_CID_004_V0_1` · `OPP12_MS_V0_1` · `OID_CID_004_OPP12_V0_1`  
> **Contracts**: `SAC-v1` · `CEMB-v1` · docs/07  
> **Implementation**: `strategies/paaf/strat_rev_opp12_01.py`

## Freeze record

```text
================================================
SIF_CID_004_V0_1

strategy_id: STRAT_REV_OPP12_01
version:     0.1.0
lifecycle:   Candidate
Identity:    FROZEN ✓

Bindable:    NO
Testing:     NOT STARTED（needs SEVF Spec + Fill + Observation）
Verified:    NO
Alpha:       NONE
CID_002/003: NOT forks · Alpha paths remain CLOSED / PAUSED
================================================
```

## 1. Frozen StrategyIdentity

| Field | Frozen value |
|-------|--------------|
| `strategy_id` | `STRAT_REV_OPP12_01` |
| `version` | `0.1.0` |
| `source_revision` | `80e26f111d0009535ef8fa6268dda2a779036399`（binding bytes first committed） |
| `git_anchor_head` | `80e26f111d0009535ef8fa6268dda2a779036399` |
| `source_manifest` | §2 |
| `source_hash` | `2efd2112a7ffd6eae70ac2761c0ba3559a07a3e0f6ef7f13ae4e35caba42de4d` |
| `parameter_manifest` | §3 |
| `parameter_hash` | `b6c767a8bf8afde7e5bba56a2777a036ab21f06b7b807ec630d9bd6edb9e1418` |
| `market_scope` | `UNBOUND_AT_ASSET` |
| `execution_model` | §4 |
| `evidence_lineage` | `[]` |
| `class_tags` | `["mean_reversion","exhaustion","overshoot"]` |
| `context_independence` | `true` |
| `not_fabricated_for_context` | `true`（seed from legacy OPP12 mixin extract） |
| `detector_binding` | `OPP12@1.0.0` |
| `campaign_id` | `CID_004` |
| `morphology_spec` | `OPP12_MS_V0_1` |

## 2. Frozen `source_manifest`

```json
[
  {
    "path": "strategies/paaf/detectors/opp12_overshoot_fail.py",
    "sha256": "becbd0868669f11cf9c7ad602addd388a0d9572821ec3735a0124df1ba3f90eb"
  },
  {
    "path": "strategies/paaf/strat_rev_opp12_01.py",
    "sha256": "5d8524871b51358eb53f4869ea1bd93baaa251f2edd027e034629b7f6e8059f9"
  }
]
```

## 3. Frozen `parameter_manifest`

```json
{
  "atr_period": {"type": "int", "unit": "bars", "value": 14},
  "ema_period": {"type": "int", "unit": "bars", "value": 20},
  "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
  "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
  "overshoot_atr_mult": {"type": "float", "unit": "atr_multiple", "value": 1.2},
  "overshoot_max_atr_mult": {"type": "float", "unit": "atr_multiple", "value": 2.5},
  "reversal_close_quarter": {"type": "float", "unit": "fraction", "value": 0.25},
  "reversal_min_body_ratio": {"type": "float", "unit": "fraction", "value": 0.15},
  "reversal_shadow_min_ratio": {"type": "float", "unit": "fraction", "value": 0.4},
  "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0}
}
```

## 4. Frozen `execution_model`

```text
signal_timeframe:     5m
risk_timeframe:       1m
order_entry:          stop order at detector entry（high/low trigger）
stop:                 from OPP12 DetectionResult.stop
target:               entry ± risk_reward × |entry−stop| when detector target absent
sizing:               fixed_size
max_hold:             max_hold_bars on 1m
rollover:             on_rollover_adjust
```

## 5. Explicit non-grants

```text
❌ Observation / KEEP / Verified / Bindable / Alpha / Production
❌ Resume CID_003
❌ Bit-identical pa_cta OPP12 claim
```

## 6. Next（须另授）

```text
DONE: STRAT_RO12_EXP001 H_MECH KEEP（rb/2024）
Next: H_MECH OOS/multi-symbol · OR · H_EDGE diagnostic Fill · OR · Pause
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | SIF_CID_004_V0_1 FROZEN · Delegation-25O |
| 2026-07-23 | `source_revision` → `80e26f111d0009535ef8fa6268dda2a779036399` |
| 2026-07-23 | Lifecycle note · EXP001 KEEP · Delegation-25P |
