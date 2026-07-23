# Strategy Identity Freeze — STRAT_TREND_BROOKS_SCALP_02@0.2.0

> **Type**: Candidate Identity Freeze（positioning lineage）  
> **Status**: **FROZEN** ✓ · **SAC field amendment** under Delegation-50D（hashes unchanged）  
> **Freeze ID**: `SIF_CID_002_V0_2_0`  
> **Date**: 2026-07-22  
> **Authorization**: `Authorize Implementation of Positioning Lineage 0.2.0`（user: **A**）  
> **Amendment**: Delegation-50D · `BGC-CID_002-v1`（G1/G3/G4 closure）  
> **Parent**: `SIF_CID_002_V0_1_1` / `@0.1.1`（immutable）  
> **Charter**: [`STRATEGY_PAAF_POSITIONING_CHARTER_BROOKS_SCALP_V020.md`](STRATEGY_PAAF_POSITIONING_CHARTER_BROOKS_SCALP_V020.md)  
> **Pipeline**: [`STRATEGY_CONSUMPTION_PIPELINE_ATTESTATION_CID_002.md`](STRATEGY_CONSUMPTION_PIPELINE_ATTESTATION_CID_002.md)

## Freeze record

```text
================================================
SIF_CID_002_V0_2_0

strategy_id: STRAT_TREND_BROOKS_SCALP_02
version:     0.2.0
lifecycle:   Verified（H_CAPITAL_GATE · E2）· Research Bindable RISK surface
change:      risk-fraction sizing · hard_max_lots · cost-aware equity kill-switch
detector:    BROOKS_SCALP_FP@0.1.0（unchanged）
Bindable:    YES（Capital-Gated Research Consumer · BDR_CID_002_V0_1）
Verified:    YES（narrow · VR_CID_002_RISK_V0_2_0 · ≠ Production）
Alpha:       NONE
================================================
```

## Identity fields

| Field | Value |
|-------|--------|
| `strategy_id` | `STRAT_TREND_BROOKS_SCALP_02` |
| `version` | `0.2.0` |
| `source_revision` | `833ae4740e6da3e2e3a42899d2bd4229f61785d6`（G5；source_hash unchanged） |
| `source_hash` | `5c089251ac301cf7d5c8f72c25960d5a1e50b90907319d0e6bd54fa3880e2499` |
| `parameter_hash` | `7ff1fe9976ba809dce8f38325c33e6b7bf11a0817b2dce6d372f32258a7da346` |
| `market_scope` | `UNBOUND_AT_ASSET`（CC-v1：EXP must declare scope） |
| `detector_binding` | `BROOKS_SCALP_FP@0.1.0` |
| `lineage_parent` | `SIF_CID_002_V0_1_1` |
| `evidence_lineage` | `["STRAT_BS02_EXP008","STRAT_BS02_EXP009","STRAT_BS02_EXP010"]` |
| `class_tags` | `["trend","positioning"]` |
| `context_independence` | `true`（inherits；detect ignores Context） |
| `not_fabricated_for_context` | `true` |
| `architecture_attestation` | see §5 |
| `execution_model` | see §4 |
| `consumer_contract` | `CC-CID_002-v1` · Surface=`RISK` |

### `source_manifest`

```json
[
  {
    "path": "strategies/paaf/brooks_scalp_paaf_strategy.py",
    "sha256": "5cdc3c4fa47e70ae524e3225cbce04787341f227f0c47ad7d9fc95fccb3dfaef"
  },
  {
    "path": "strategies/paaf/brooks_scalp_paaf_strategy_v011.py",
    "sha256": "dec3b51eb326e3bfeb9930752fb945aee9275f58375bee1dc48b7d58843b2bd5"
  },
  {
    "path": "strategies/paaf/brooks_scalp_paaf_strategy_v020.py",
    "sha256": "3723f01a24b139495587744b77f4b031751926e1fbca2c588b4c8347c9e79b1c"
  },
  {
    "path": "strategies/paaf/detectors/brooks_scalp_first_pullback.py",
    "sha256": "3ffd6a027d92a914e438ccc0e6cc797aa319c9d2a79ec779a29fc74ec8126fad"
  }
]
```

### `parameter_manifest`（G1）

```json
{
  "atr_period": {"type": "int", "unit": "bars", "value": 20},
  "capital_floor_ratio": {"type": "float", "unit": "fraction_of_capital", "value": 0.5},
  "ema_period": {"type": "int", "unit": "bars", "value": 20},
  "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
  "hard_max_lots": {"type": "int", "unit": "contracts", "value": 1},
  "max_hold_bars": {"type": "int", "unit": "bars", "value": 10},
  "pullback_atr": {"type": "float", "unit": "atr_multiple", "value": 0.2},
  "risk_per_trade": {"type": "float", "unit": "fraction_of_equity", "value": 0.005},
  "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
  "sizing_mode": {"type": "str", "unit": "enum", "value": "RISK_FRACTION_OF_CAPITAL"},
  "trend_leg_atr": {"type": "float", "unit": "atr_multiple", "value": 1.0}
}
```

`parameter_hash` = SHA256(canonical JSON) = `7ff1fe9976ba809dce8f38325c33e6b7bf11a0817b2dce6d372f32258a7da346`.

## 4. `execution_model`（G3）

```text
signal_timeframe:     1m
order_style:          stop entry after first-pullback DetectionResult
stop / target:        structural stop + risk_reward·R target（from Detector）
time_stop:            max_hold_bars（Strategy orchestration）
sizing_rule_class:    RISK_FRACTION_OF_CAPITAL
  risk_per_trade:     0.005 of equity_est
  hard_max_lots:      1
  lots=0:             skip trade（no force）
  capital_floor:      0.5 × initial_capital → flatten + halt
cost_binding:         PROJECT_FROZEN_DATA_PROTOCOL → docs/07_DATA_SPEC.md v1.0.0
fill_binding:         VNPY_CTA_BACKTEST_ENGINE_DEFAULTS_AT_EXP_REGISTRATION
fee/slippage numbers: not invented at asset freeze（resolved at EXP registration）
```

```text
Consumers MUST NOT inherit fixed_size semantics from @0.1.x when calling @0.2.0.
```

## 5. Architecture attestation（G4）

```text
Target boundary:
  Context → Detector Registry → Risk → Execution → Logger

Attested for @0.2.0:
  ✓ Morphology unchanged（BROOKS_SCALP_FP@0.1.0）
  ✓ Parent rollover repair retained（V011）
  ✓ Risk wrapper only adds sizing + kill-switch
  ✓ Context not in signal path
  ✓ Consumer Contract CC-CID_002-v1 Surface=RISK
  ✓ Pipeline CPA_CID_002_V0_1
  ✗ Registry catalog wiring still not required（direct construct）
  ✗ equity_est ≈ engine balance（may diverge）；kill uses equity_est
  ✗ Bindable not claimed
  ✗ git commit of binding bytes pending（G5）
```

## What this is / is not

```text
IS: Candidate positioning identity for capital-safety consumption tests
IS: SAC-complete freeze body after 50D amendment（same hashes）
IS NOT: erasure of @0.1.0 / @0.1.1 mechanism evidence
IS NOT: Verified-as-Alpha / Production
IS: Bindable Capital-Gated Research Consumer（BDR_CID_002_V0_1）
IS NOT: claim that H_MECH improved
```

## Capital-gate smoke（implementation）

| EXP | Outcome | Note |
|-----|---------|------|
| EXP008 | **REVERT** | cost-blind `equity_est` → kill never fired；engine balance≤0 |
| EXP009 | **KEEP** | cost-aware equity + friction-in-lot-gate；kill_events=1；no capital≤0 |
| EXP010 | **KEEP** | multi-symbol {rb,i,MA} capital portability（G6） |

## Machine record

`research/output/evidence/STRATEGY_IDENTITY_FREEZE_CID_002_V020/identity_freeze.json`

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | 0.2.0 Candidate Identity Freeze after A-authorized implementation |
| 2026-07-22 | SAC field amendment（G1/G3/G4）under Delegation-50D · hashes unchanged |
| 2026-07-22 | evidence_lineage append EXP010（Delegation-100E · G6） |
| 2026-07-22 | G5：`source_revision` → `833ae4740e6da3e2e3a42899d2bd4229f61785d6` |
| 2026-07-22 | Lifecycle → Verified（H_CAPITAL_GATE · E2）via `VR_CID_002_RISK_V0_2_0` |
| 2026-07-22 | Bindable GRANTED（RISK）via `BDR_CID_002_V0_1` |
