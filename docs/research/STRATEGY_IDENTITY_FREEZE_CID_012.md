# Strategy Identity Freeze — CID_012 / STRAT_REV_OPP13_DT_01@0.1.0

> **Type**: Candidate Identity Freeze（≠ Bindable · ≠ Testing evidence · ≠ Alpha）  
> **Status**: **FROZEN** ✓  
> **Freeze ID**: `SIF_CID_012_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AV  
> **Design**: `NSAD_CID_012_V0_1` · `OPP13_DT_MS_V0_1`  
> **Contracts**: `SAC-v1` · `CEMB-v1` · docs/07  
> **Implementation**: `strategies/paaf/strat_rev_opp13_dt_01.py`

## Freeze record

```text
================================================
SIF_CID_012_V0_1

strategy_id: STRAT_REV_OPP13_DT_01
version:     0.1.0
lifecycle:   Candidate
Identity:    FROZEN ✓

Bindable:    NO
Testing:     NOT STARTED（needs SEVF Spec + Fill + Observation）
Verified:    NO
Alpha:       NONE
CID_002–011: NOT forks · Alpha paths remain CLOSED / PAUSED
================================================
```

## 1. Frozen StrategyIdentity

| Field | Frozen value |
|-------|--------------|
| `strategy_id` | `STRAT_REV_OPP13_DT_01` |
| `version` | `0.1.0` |
| `source_revision` | c47d4c39027f9b07181343f032903985449cd913 |
| `git_anchor_head` | c47d4c39027f9b07181343f032903985449cd913 |
| `source_manifest` | §2 |
| `source_hash` | `b01715d8e4ff68e0fb15b228dfcd9f263651b070362bf83f301961859fa24207` |
| `parameter_manifest` | §3 |
| `parameter_hash` | `910989850b1620d4db2c9fa99d539b039c316b834216b25ad0dc7ef155dc1f8b` |
| `market_scope` | `UNBOUND_AT_ASSET` |
| `execution_model` | §4 |
| `evidence_lineage` | `[]` |
| `class_tags` | `["mean_reversion","day_boundary","double_top"]` |
| `context_independence` | `true` |
| `not_fabricated_for_context` | `true`（seed from legacy OPP13 double-top） |
| `detector_binding` | `OPP13_DT@1.0.0` |
| `campaign_id` | `CID_012` |
| `morphology_spec` | `OPP13_DT_MS_V0_1` |

## 2. Frozen `source_manifest`

```json
[
  {
    "path": "strategies/paaf/detectors/opp13_day_high_double_top.py",
    "sha256": "20293b3a242674587ade9e4b205f22b87be72cdc6d3444266ca3e1cbe1d47f3b"
  },
  {
    "path": "strategies/paaf/strat_rev_opp13_dt_01.py",
    "sha256": "c5f83ed919afeb5d092490cc132a2f13b0b468b47b421f33f5814a06a143549e"
  }
]
```

## 3. Frozen `parameter_manifest`

```json
{
  "boundary_reversal_close_ratio": {"type": "float", "unit": "fraction", "value": 0.3},
  "boundary_reversal_shadow_ratio": {"type": "float", "unit": "fraction", "value": 0.45},
  "day_high_lh_max_ticks": {"type": "float", "unit": "ticks", "value": 10.0},
  "day_high_second_test_max_bars": {"type": "int", "unit": "bars_5m", "value": 12},
  "day_high_second_test_ticks": {"type": "float", "unit": "ticks", "value": 3.0},
  "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
  "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
  "quality_close_from_high_ratio": {"type": "float", "unit": "fraction", "value": 0.35},
  "quality_shadow_ratio": {"type": "float", "unit": "fraction", "value": 0.4},
  "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0}
}
```

## 4. Frozen `execution_model`

```text
signal_timeframe:     5m
risk_timeframe:       1m
order_entry:          stop order at detector entry（low）
stop:                 from OPP13_DT DetectionResult.stop
target:               entry ± risk_reward × |entry−stop|
sizing:               fixed_size
max_hold:             max_hold_bars on 1m
rollover:             on_rollover_adjust + detector.adjust_levels
```

## 5. Explicit non-grants

```text
❌ Observation / KEEP / Verified / Bindable / Alpha / Production by Freeze alone
❌ Resume CID_003–011
❌ Single-touch Path A under this identity（CID_010）
❌ Day-low double-bottom expand under this identity
```

## 6. Differentiation

```text
≠ SIF_CID_010 / STRAT_REV_OPP13_01（single-touch）
≠ parameter transfer from CID_010 HOLD surface
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | SIF_CID_012_V0_1 FROZEN · Delegation-25AV |
