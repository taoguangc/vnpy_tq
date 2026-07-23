# Strategy Identity Freeze — CID_006 / STRAT_TREND_OPP08_01@0.1.0

> **Type**: Candidate Identity Freeze（≠ Bindable · ≠ Testing evidence · ≠ Alpha）  
> **Status**: **FROZEN** ✓  
> **Freeze ID**: `SIF_CID_006_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25Z  
> **Design**: `NSAD_CID_006_V0_1` · `OPP08_MS_V0_1` · `OID_CID_006_OPP08_V0_1`  
> **Contracts**: `SAC-v1` · `CEMB-v1` · docs/07  
> **Implementation**: `strategies/paaf/strat_trend_opp08_01.py`

## Freeze record

```text
================================================
SIF_CID_006_V0_1

strategy_id: STRAT_TREND_OPP08_01
version:     0.1.0
lifecycle:   Candidate
Identity:    FROZEN ✓

Bindable:    NO
Testing:     NOT STARTED（needs SEVF Spec + Fill + Observation）
Verified:    NO
Alpha:       NONE
CID_002–005: NOT forks · Alpha paths remain CLOSED / PAUSED
================================================
```

## 1. Frozen StrategyIdentity

| Field | Frozen value |
|-------|--------------|
| `strategy_id` | `STRAT_TREND_OPP08_01` |
| `version` | `0.1.0` |
| `source_revision` | `9eebac61dafeb712fb052498438cdd248afbf570`（binding bytes first committed） |
| `git_anchor_head` | `9eebac61dafeb712fb052498438cdd248afbf570` |
| `source_manifest` | §2 |
| `source_hash` | `0a6023e581b8547d42c10a30f05324f0c841d131cbbd748ade4ad7476fd66f14` |
| `parameter_manifest` | §3 |
| `parameter_hash` | `5c48a70f7666d033d340799e4fdf19972aeadfc15c98b068f85521ab32d0163e` |
| `market_scope` | `UNBOUND_AT_ASSET` |
| `execution_model` | §4 |
| `evidence_lineage` | `[]` |
| `class_tags` | `["trend","breakout","momentum"]` |
| `context_independence` | `true` |
| `not_fabricated_for_context` | `true`（seed from legacy OPP08 mixin extract） |
| `detector_binding` | `OPP08@1.0.0` |
| `campaign_id` | `CID_006` |
| `morphology_spec` | `OPP08_MS_V0_1` |

## 2. Frozen `source_manifest`

```json
[
  {
    "path": "strategies/paaf/detectors/opp08_strong_breakout.py",
    "sha256": "ec1bac496d1354069dca0f16146365ba2dad83abd0daa13ea8fce1952393b902"
  },
  {
    "path": "strategies/paaf/strat_trend_opp08_01.py",
    "sha256": "49fb9aa7ed3e74007a6b913b23e7a1dfb149c72bf75e1aa02970c813869d95da"
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
  "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
  "strong_bar_atr_mult": {"type": "float", "unit": "atr_multiple", "value": 1.0},
  "strong_bar_body_ratio": {"type": "float", "unit": "fraction", "value": 0.6}
}
```

## 4. Frozen `execution_model`

```text
signal_timeframe:     5m
risk_timeframe:       1m
order_entry:          stop order at detector entry（high/low trigger）
stop:                 from OPP08 DetectionResult.stop
target:               entry ± risk_reward × |entry−stop| when detector target absent
sizing:               fixed_size
max_hold:             max_hold_bars on 1m
rollover:             on_rollover_adjust
```

## 5. Explicit non-grants

```text
❌ Observation / KEEP / Verified / Bindable / Alpha / Production
❌ Resume CID_003–005
❌ Bit-identical pa_cta OPP08 claim
```

## 6. Next（须另授）

```text
DONE: STRAT_TO08_EXP001 H_MECH KEEP（rb/2024 · attributed=1456）
Next: H_EDGE diagnostic Fill · OR · H_MECH OOS/multi-symbol · OR · Pause
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | SIF_CID_006_V0_1 FROZEN · Delegation-25Z |
| 2026-07-23 | `source_revision` → `9eebac61dafeb712fb052498438cdd248afbf570` |
| 2026-07-23 | Lifecycle note · EXP001 KEEP · Delegation-25AA |
