# Strategy Identity Freeze — CID_007 / STRAT_SESS_OPP19_01@0.1.0

> **Type**: Candidate Identity Freeze（≠ Bindable · ≠ Testing evidence · ≠ Alpha）  
> **Status**: **FROZEN** ✓  
> **Freeze ID**: `SIF_CID_007_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AE  
> **Design**: `NSAD_CID_007_V0_1` · `OPP19_MS_V0_1` · `OID_CID_007_OPP19_V0_1`  
> **Contracts**: `SAC-v1` · `CEMB-v1` · docs/07  
> **Implementation**: `strategies/paaf/strat_sess_opp19_01.py`

## Freeze record

```text
================================================
SIF_CID_007_V0_1

strategy_id: STRAT_SESS_OPP19_01
version:     0.1.0
lifecycle:   Candidate
Identity:    FROZEN ✓
Scope:       OD-Breakout only（OD_REV NOT INCLUDED）

Bindable:    NO
Testing:     NOT STARTED
Verified:    NO
Alpha:       NONE
CID_002–006: NOT forks · Alpha paths remain CLOSED / PAUSED
================================================
```

## 1. Frozen StrategyIdentity

| Field | Frozen value |
|-------|--------------|
| `strategy_id` | `STRAT_SESS_OPP19_01` |
| `version` | `0.1.0` |
| `source_revision` | `PENDING_FIRST_BINDING_COMMIT` |
| `git_anchor_head` | `PENDING_FIRST_BINDING_COMMIT` |
| `source_manifest` | §2 |
| `source_hash` | `f7cbcb3f9b556af5478d7f88fa9d7f51627887250273b4bd4c153e38e43d90d6` |
| `parameter_manifest` | §3 |
| `parameter_hash` | `3f9793feda3d0ca20ba238197acbf120a469a486620b0f23a002dcceb5762a05` |
| `market_scope` | `UNBOUND_AT_ASSET` |
| `execution_model` | §4 |
| `evidence_lineage` | `[]` |
| `class_tags` | `["session","opening","breakout"]` |
| `context_independence` | `true` |
| `not_fabricated_for_context` | `true` |
| `detector_binding` | `OPP19@1.0.0` |
| `campaign_id` | `CID_007` |
| `morphology_spec` | `OPP19_MS_V0_1` |

## 2. Frozen `source_manifest`

```json
[
  {
    "path": "strategies/paaf/detectors/opp19_opening_drive_breakout.py",
    "sha256": "cdbcaf4bdc85ab7b318901a9396476324432fef33677ce70b27e97443f752d58"
  },
  {
    "path": "strategies/paaf/strat_sess_opp19_01.py",
    "sha256": "5ecbd12ea9a49d683bcf3965baf06aacde16af5e1359bba6b3b517e6514e9ffe"
  }
]
```

## 3. Frozen `parameter_manifest`

```json
{
  "atr_period": {"type": "int", "unit": "bars", "value": 14},
  "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
  "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
  "opening_drive_bars": {"type": "int", "unit": "bars", "value": 6},
  "opening_drive_min_body": {"type": "float", "unit": "fraction", "value": 0.5},
  "opening_drive_range_atr_min": {"type": "float", "unit": "atr_multiple", "value": 0.2},
  "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
  "strong_bar_atr_mult": {"type": "float", "unit": "atr_multiple", "value": 1.0},
  "strong_bar_body_ratio": {"type": "float", "unit": "fraction", "value": 0.6}
}
```

## 4. Frozen `execution_model`

```text
signal_timeframe:     5m
risk_timeframe:       1m
order_entry:          stop order at detector entry
stop:                 from OPP19 DetectionResult.stop
target:               entry ± risk_reward × |entry−stop|
sizing:               fixed_size
max_hold:             max_hold_bars on 1m
rollover:             on_rollover_adjust + detector.adjust_or_levels
```

## 5. Explicit non-grants

```text
❌ Observation / KEEP / Verified / Bindable / Alpha / Production
❌ Resume CID_003–006
❌ OD_REV in this identity
❌ Bit-identical pa_cta OPP19 claim
```

## 6. Next（须另授）

```text
Authorize SEVF Spec + Fill for H_MECH EXP001
  — OR — leave Candidate idle
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | SIF_CID_007_V0_1 FROZEN · Delegation-25AE |
| 2026-07-23 | `source_revision` → pending first binding commit |
