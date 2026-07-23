# Strategy Identity Freeze — CID_005 / STRAT_REV_OPP17_01@0.1.0

> **Type**: Candidate Identity Freeze（≠ Bindable · ≠ Testing evidence · ≠ Alpha）  
> **Status**: **FROZEN** ✓  
> **Freeze ID**: `SIF_CID_005_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25T  
> **Design**: `NSAD_CID_005_V0_1` · `OPP17_MS_V0_1` · `OID_CID_005_OPP17_V0_1`  
> **Contracts**: `SAC-v1` · `CEMB-v1` · docs/07  
> **Implementation**: `strategies/paaf/strat_rev_opp17_01.py`

## Freeze record

```text
================================================
SIF_CID_005_V0_1

strategy_id: STRAT_REV_OPP17_01
version:     0.1.0
lifecycle:   Candidate
Identity:    FROZEN ✓

Bindable:    NO
Testing:     NOT STARTED（needs SEVF Spec + Fill + Observation）
Verified:    NO
Alpha:       NONE
CID_002/003/004: NOT forks · Alpha paths remain CLOSED / PAUSED
================================================
```

## 1. Frozen StrategyIdentity

| Field | Frozen value |
|-------|--------------|
| `strategy_id` | `STRAT_REV_OPP17_01` |
| `version` | `0.1.0` |
| `source_revision` | `d0de567337145d75c66547c3603031c76c721fed`（binding bytes first committed） |
| `git_anchor_head` | `d0de567337145d75c66547c3603031c76c721fed` |
| `source_manifest` | §2 |
| `source_hash` | `9d85cf960f30715524f7224bdf3dd9750ce4fd1ad86a79d9122789c75e5cb576` |
| `parameter_manifest` | §3 |
| `parameter_hash` | `40ef1e1d594294e89e9872f08c5ac5d057dc36156081784e030c072fd19b0816` |
| `market_scope` | `UNBOUND_AT_ASSET` |
| `execution_model` | §4 |
| `evidence_lineage` | `[]` |
| `class_tags` | `["mean_reversion","climax","exhaustion"]` |
| `context_independence` | `true` |
| `not_fabricated_for_context` | `true`（seed from legacy OPP17 mixin extract） |
| `detector_binding` | `OPP17@1.0.0` |
| `campaign_id` | `CID_005` |
| `morphology_spec` | `OPP17_MS_V0_1` |

## 2. Frozen `source_manifest`

```json
[
  {
    "path": "strategies/paaf/detectors/opp17_climax_reversal.py",
    "sha256": "24dbeae32ea968fb5747e3e68cc50c7d89571a70dd507f26e2a20a96e7abf7c0"
  },
  {
    "path": "strategies/paaf/strat_rev_opp17_01.py",
    "sha256": "f45cc5182d512e3506f4bcbe356023c822b233cf8689e4d16a26fa1e326d3189"
  }
]
```

## 3. Frozen `parameter_manifest`

```json
{
  "atr_period": {"type": "int", "unit": "bars", "value": 14},
  "climax_range_atr": {"type": "float", "unit": "atr_multiple", "value": 2.5},
  "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
  "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
  "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0}
}
```

## 4. Frozen `execution_model`

```text
signal_timeframe:     5m
risk_timeframe:       1m
order_entry:          stop order at detector entry（high/low trigger）
stop:                 from OPP17 DetectionResult.stop
target:               entry ± risk_reward × |entry−stop| when detector target absent
sizing:               fixed_size
max_hold:             max_hold_bars on 1m
rollover:             on_rollover_adjust
```

## 5. Explicit non-grants

```text
❌ Observation / KEEP / Verified / Bindable / Alpha / Production
❌ Resume CID_003 / CID_004
❌ Bit-identical pa_cta OPP17 claim
```

## 6. Next（须另授）

```text
Authorize SEVF Spec + Fill for H_MECH EXP001
  — OR — leave Candidate idle
NOT: H_EDGE before H_MECH · parameter shopping
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | SIF_CID_005_V0_1 FROZEN · Delegation-25T |
| 2026-07-23 | `source_revision` → pending first binding commit |
