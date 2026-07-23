# Strategy Identity Freeze — CID_009 / STRAT_REV_OPP15_01@0.1.0

> **Type**: Candidate Identity Freeze（≠ Bindable · ≠ Testing evidence · ≠ Alpha）  
> **Status**: **FROZEN** ✓  
> **Freeze ID**: `SIF_CID_009_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AM  
> **Design**: `NSAD_CID_009_V0_1` · `OPP15_MS_V0_1`  
> **Contracts**: `SAC-v1` · `CEMB-v1` · docs/07  
> **Implementation**: `strategies/paaf/strat_rev_opp15_01.py`

## Freeze record

```text
================================================
SIF_CID_009_V0_1

strategy_id: STRAT_REV_OPP15_01
version:     0.1.0
lifecycle:   Candidate
Identity:    FROZEN ✓

Bindable:    NO
Testing:     NOT STARTED（needs SEVF Spec + Fill + Observation）
Verified:    NO
Alpha:       NONE
CID_002–008: NOT forks · Alpha paths remain CLOSED / PAUSED
================================================
```

## 1. Frozen StrategyIdentity

| Field | Frozen value |
|-------|--------------|
| `strategy_id` | `STRAT_REV_OPP15_01` |
| `version` | `0.1.0` |
| `source_revision` | `8e3acd15b953ef8d3f8640e21711d4265e42abc8`（binding bytes first committed） |
| `git_anchor_head` | `8e3acd15b953ef8d3f8640e21711d4265e42abc8` |
| `source_manifest` | §2 |
| `source_hash` | `1b0f5858d8d22371906085cdf974b8378e60d6bdb8c3924a509bfce62e9cb8a1` |
| `parameter_manifest` | §3 |
| `parameter_hash` | `960b1ae8abdf5011f6d7977bf99c4bae7a8f8264721afca0488e687b539af9f6` |
| `market_scope` | `UNBOUND_AT_ASSET` |
| `execution_model` | §4 |
| `evidence_lineage` | `[]` |
| `class_tags` | `["exhaustion","wedge","reversal"]` |
| `context_independence` | `true` |
| `not_fabricated_for_context` | `true`（seed from legacy OPP15 Path A + wedge scanner） |
| `detector_binding` | `OPP15@1.0.0` |
| `campaign_id` | `CID_009` |
| `morphology_spec` | `OPP15_MS_V0_1` |

## 2. Frozen `source_manifest`

```json
[
  {
    "path": "strategies/paaf/detectors/opp15_wedge_path_a.py",
    "sha256": "f0a03146a171b5c70874622a26d237004a942952e10442e88e74a3f0c4979c44"
  },
  {
    "path": "strategies/paaf/morphology/wedge.py",
    "sha256": "71015c7c1b178e2c2406e34c0419c8f77d425d27828f8eaa5dfdf13fe9011956"
  },
  {
    "path": "strategies/paaf/strat_rev_opp15_01.py",
    "sha256": "2ab2f4ef56b8b1f6469a791ebe37117c68dae2242f3dfcc303d966572154e7d8"
  }
]
```

## 3. Frozen `parameter_manifest`

```json
{
  "atr_period": {"type": "int", "unit": "bars", "value": 14},
  "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
  "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
  "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
  "strong_bar_atr_mult": {"type": "float", "unit": "atr_multiple", "value": 1.0},
  "strong_bar_body_ratio": {"type": "float", "unit": "fraction", "value": 0.6},
  "wedge_alpha_threshold": {"type": "float", "unit": "fraction", "value": 0.85},
  "wedge_arm_trigger_max_bars": {"type": "int", "unit": "bars", "value": 4},
  "wedge_n_min": {"type": "int", "unit": "bars", "value": 3}
}
```

## 4. Frozen `execution_model`

```text
signal_timeframe:     5m
risk_timeframe:       1m
order_entry:          stop order at detector entry（high/low）
stop:                 from OPP15 DetectionResult.stop（p3 ± tick）
target:               entry ± risk_reward × |entry−stop|
sizing:               fixed_size
max_hold:             max_hold_bars on 1m
rollover:             on_rollover_adjust + detector.adjust_levels
```

## 5. Explicit non-grants

```text
❌ Observation / KEEP / Verified / Bindable / Alpha / Production by Freeze alone
❌ Resume CID_003–008
❌ Path B' / MTF under this identity
❌ Bit-identical pa_cta OPP15 claim
```

## 6. Next（须另授）

```text
DONE: STRAT_RO15_EXP001 H_MECH KEEP（rb/2024 · attributed=435）
Next: H_EDGE diagnostic Fill · OR · H_MECH OOS/multi-symbol · OR · Pause
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | SIF_CID_009_V0_1 FROZEN · Delegation-25AM |
| 2026-07-23 | `source_revision` → `8e3acd15b953ef8d3f8640e21711d4265e42abc8` |
| 2026-07-23 | Lifecycle note · EXP001 KEEP · Delegation-25AM |
