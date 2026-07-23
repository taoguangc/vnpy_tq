# Strategy Identity Freeze — CID_003 / STRAT_REV_OPP16_01@0.1.0

> **Type**: Candidate Identity Freeze（≠ Bindable · ≠ Testing evidence · ≠ Alpha）  
> **Status**: **FROZEN** ✓  
> **Freeze ID**: `SIF_CID_003_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: `Authorize Strategy Identity Freeze for CID_003 / STRAT_REV_OPP16_01@0.1.0`  
> **Design**: [`STRATEGY_NEW_ASSET_DESIGN_CID_003.md`](STRATEGY_NEW_ASSET_DESIGN_CID_003.md) · `NSAD_CID_003_V0_1`  
> **Contracts**: `SAC-v1` · `CEMB-v1` · docs/07  
> **Implementation**: `strategies/paaf/strat_rev_opp16_01.py`

## Freeze record

```text
================================================
SIF_CID_003_V0_1

strategy_id: STRAT_REV_OPP16_01
version:     0.1.0
lifecycle:   Candidate
Identity:    FROZEN ✓

Bindable:    NO
Testing:     NOT STARTED（needs SEVF Spec + Fill + Observation）
Verified:    NO
Alpha:       NONE
CID_002:     NOT a fork · Alpha path remains CLOSED
================================================
```

## 1. Frozen StrategyIdentity

| Field | Frozen value |
|-------|--------------|
| `strategy_id` | `STRAT_REV_OPP16_01` |
| `version` | `0.1.0` |
| `source_revision` | `966d7cab0d11c3f835b39533872cb8ead6f26e62`（binding bytes first committed；source_hash unchanged） |
| `git_anchor_head` | `966d7cab0d11c3f835b39533872cb8ead6f26e62` |
| `source_manifest` | §2 |
| `source_hash` | `f87cdcc43e74060f23c08fa06364f0be90c538a1576566a0034ba096f0adc220` |
| `parameter_manifest` | §3 |
| `parameter_hash` | `76b124f47414af2da2e0cdfdc6afcd5025d2cca8ae3a5583ba667cc7e1e31c57` |
| `market_scope` | `UNBOUND_AT_ASSET`（every EXP must declare scope） |
| `execution_model` | §4 |
| `evidence_lineage` | `[]` |
| `class_tags` | `["mean_reversion","reversal"]` |
| `context_independence` | `true`（OPP16 ignores Context；ContextEngine orchestration only） |
| `not_fabricated_for_context` | `true`（seed from inventory OPP16 Candidate；not built to force Context result） |
| `architecture_attestation` | §5 |
| `detector_binding` | `OPP16@1.0.0` |
| `campaign_id` | `CID_003` |

## 2. Frozen `source_manifest`

```json
[
  {
    "path": "strategies/paaf/detectors/opp16_two_bar_reversal.py",
    "sha256": "ddb8378defa95ed1e2f3ccdd3cfd2ee3fbc25816a576524c21b6a42284ae9954"
  },
  {
    "path": "strategies/paaf/strat_rev_opp16_01.py",
    "sha256": "1a67cc5188514ef39e0db819a556b6c5435624b745b5f77e8aa9cd483d2c24d8"
  }
]
```

## 3. Frozen `parameter_manifest`

```json
{
  "body_ratio": {"type": "float", "unit": "fraction", "value": 0.5},
  "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
  "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
  "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0}
}
```

```text
body_ratio matches OPP16 DEFAULT_BODY_RATIO（no re-optimization）.
risk_reward used only when detector target is absent（orchestrator RR fill）.
```

## 4. Frozen `execution_model`

```text
signal_timeframe:     5m（BarGenerator → on_5min_bar → ArrayManager）
risk_timeframe:       1m（stop / target / time-stop）
order_entry:          stop order at detector entry
stop:                 from OPP16 DetectionResult.stop
target:               detector.target if set；else entry ± risk_reward × |entry−stop|
sizing:               fixed_size contracts
max_hold:             max_hold_bars on 1m
rollover:             on_rollover_adjust shifts entry/stop/target/_entry_fill
fill_binding:         research EXPs use CEMB-v1 / docs/07 defaults at EXP registration
```

## 5. Architecture attestation

```text
✓ Detector: OPP16TwoBarReversalDetector — pure detect；no orders
✓ Strategy: StratRevOpp1601Strategy — orchestration only；no pattern math
✓ Context:  published for pipeline；not used as trade gate by OPP16
✓ Risk:     stop/target/time-stop in strategy on_bar（1m）；no separate RISK surface yet
```

## 6. Explicit non-grants

```text
❌ Bindable / Verified / Alpha
❌ Observation / SEVF Fill
❌ Parameter search
❌ Reopen CID_002 H_EDGE
❌ Production / Epoch 7
```

## 7. Next（须另授）

```text
Authorize SEVF Specification for CID_003
  — OR — Authorize SEVF Fill for first H_MECH EXP（if Spec bundled）
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | SIF_CID_003_V0_1 FROZEN |
