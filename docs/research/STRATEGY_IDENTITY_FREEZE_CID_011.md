# Strategy Identity Freeze — CID_011 / STRAT_SESS_OPP19_REV_01@0.1.0

> **Type**: Candidate Identity Freeze（≠ Bindable · ≠ Testing evidence · ≠ Alpha）  
> **Status**: **FROZEN** ✓  
> **Freeze ID**: `SIF_CID_011_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AS  
> **Design**: `NSAD_CID_011_V0_1` · `OPP19_REV_MS_V0_1`  
> **Contracts**: `SAC-v1` · `CEMB-v1` · docs/07  
> **Implementation**: `strategies/paaf/strat_sess_opp19_rev_01.py`  
> **Explicit**: ≠ `SIF_CID_007` / `STRAT_SESS_OPP19_01`（OD-Breakout）

## Freeze record

```text
================================================
SIF_CID_011_V0_1

strategy_id: STRAT_SESS_OPP19_REV_01
version:     0.1.0
lifecycle:   Candidate
Identity:    FROZEN ✓

Bindable:    NO
Testing:     NOT STARTED（needs SEVF Spec + Fill + Observation）
Verified:    NO
Alpha:       NONE
CID_002–010: NOT forks · Alpha paths remain CLOSED / PAUSED
CID_007:     NOT merged · OD-Breakout remains CLOSED
================================================
```

## 1. Frozen StrategyIdentity

| Field | Frozen value |
|-------|--------------|
| `strategy_id` | `STRAT_SESS_OPP19_REV_01` |
| `version` | `0.1.0` |
| `source_revision` | *(set on binding commit)* |
| `git_anchor_head` | *(same)* |
| `source_manifest` | §2 |
| `source_hash` | `731c908d810d6c5f61400ceaeb06beb37a8436bc2f8503261ba2fecd86060593` |
| `parameter_manifest` | §3 |
| `parameter_hash` | `2f8f2170dc94cfa63ac9e99bfd365d239be4c4186672c5db54143ae0d21b8f71` |
| `market_scope` | `UNBOUND_AT_ASSET` |
| `execution_model` | §4 |
| `evidence_lineage` | `[]` |
| `class_tags` | `["session","opening_drive","reversal"]` |
| `context_independence` | `true` |
| `not_fabricated_for_context` | `true`（seed from legacy OD_REV path） |
| `detector_binding` | `OPP19_REV@1.0.0` |
| `campaign_id` | `CID_011` |
| `morphology_spec` | `OPP19_REV_MS_V0_1` |

## 2. Frozen `source_manifest`

```json
[
  {
    "path": "strategies/paaf/detectors/opp19_opening_drive_reversal.py",
    "sha256": "410b0df9913d871ec9b2441d172f719b0ea56b4a691f85f12b04754cea3ae01c"
  },
  {
    "path": "strategies/paaf/strat_sess_opp19_rev_01.py",
    "sha256": "7f7b7786b6333a0386cfbb546c423f19b80f5b03553d78b1816b7a09ed538846"
  }
]
```

## 3. Frozen `parameter_manifest`

```json
{
  "atr_period": {"type": "int", "unit": "bars", "value": 14},
  "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
  "max_bar1_range_atr": {"type": "float", "unit": "atr_multiple", "value": 2.5},
  "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
  "min_bar1_range_atr": {"type": "float", "unit": "atr_multiple", "value": 0.3},
  "morning_cutoff_minute": {"type": "int", "unit": "minute", "value": 25},
  "night_cutoff_minute": {"type": "int", "unit": "minute", "value": 25},
  "opening_rev_body_ratio": {"type": "float", "unit": "fraction", "value": 0.45},
  "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0}
}
```

## 4. Frozen `execution_model`

```text
signal_timeframe:     5m
risk_timeframe:       1m
order_entry:          stop order at detector entry（high/low）
stop:                 from OPP19_REV DetectionResult.stop
target:               entry ± risk_reward × |entry−stop|
sizing:               fixed_size
max_hold:             max_hold_bars on 1m
rollover:             on_rollover_adjust + detector.adjust_levels
```

## 5. Explicit non-grants

```text
❌ Observation / KEEP / Verified / Bindable / Alpha / Production by Freeze alone
❌ Resume CID_003–010 · merge with CID_007
❌ OD-Breakout under this identity
```

## 6. Next

```text
SEVF Spec → H_MECH Fill → Offline Observation（rb/2024）
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | SIF_CID_011_V0_1 FROZEN · Delegation-25AS |
