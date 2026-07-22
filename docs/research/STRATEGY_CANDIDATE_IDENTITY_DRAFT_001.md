# Candidate Identity Draft — STRAT_CAND_001 Brooks Scalp Source

> **Type**: Candidate Identity Draft（≠ Identity Freeze · ≠ Testing · ≠ Backtest）  
> **Status**: **DRAFT_COMPLETE_FOR_REVIEW** ✓ · recovery **WORKING_TREE_RESTORE**  
> **Draft ID**: `CID_001_BROOKS_SCALP_V0_1`  
> **Protocol**: [`SCIDR-v1`](STRATEGY_CANDIDATE_IDENTITY_DRAFT_SOURCE_RECOVERY_FREEZE.md)  
> **Candidate**: `STRAT_CAND_001_BROOKS_SCALP_SOURCE`  
> **Date**: 2026-07-22  
> **Authorization**: Five-round delegated decision — decision 4；updated under twenty-round delegation（ADAP / CEMB）；restore under user path **A**  
> **ADAP**: [`STRATEGY_ARCHITECTURE_DEVIATION_ACCEPTANCE_PROTOCOL_FREEZE.md`](STRATEGY_ARCHITECTURE_DEVIATION_ACCEPTANCE_PROTOCOL_FREEZE.md) — **T2 + T4**  
> **CEMB**: [`STRATEGY_CANDIDATE_EXECUTION_MARKET_BINDING_PROTOCOL_FREEZE.md`](STRATEGY_CANDIDATE_EXECUTION_MARKET_BINDING_PROTOCOL_FREEZE.md)  
> **Restore review**: [`STRATEGY_CANDIDATE_WORKING_TREE_RESTORE_CID_001.md`](STRATEGY_CANDIDATE_WORKING_TREE_RESTORE_CID_001.md) — **RESTORE_COMPLETE**  
> **Freeze readiness**: [`STRATEGY_CANDIDATE_IDENTITY_FREEZE_READINESS_CID_001.md`](STRATEGY_CANDIDATE_IDENTITY_FREEZE_READINESS_CID_001.md) — **NOT READY**  
> **Rewrite charter**: [`STRATEGY_PAAF_REWRITE_CHARTER_BROOKS_SCALP.md`](STRATEGY_PAAF_REWRITE_CHARTER_BROOKS_SCALP.md) — design only  
> **Machine record**: `research/output/evidence/STRATEGY_CANDIDATE_IDENTITY_DRAFT_001/identity_draft.json`

## Draft record

```text
================================================
CANDIDATE IDENTITY DRAFT CID_001

provisional strategy_id:  STRAT_TREND_BROOKS_SCALP_01
provisional version:      0.1.0-draft
recovery_mode:            WORKING_TREE_RESTORE
Identity Freeze:          NOT STARTED
Working-tree restore:     COMPLETE（blob-exact LF）
Backtest:                 NONE
================================================
```

## 1. Identity fields（draft）

| Field | Draft value | Status |
|-------|-------------|--------|
| `strategy_id` | `STRAT_TREND_BROOKS_SCALP_01` | provisional label |
| `version` | `0.1.0-draft` | provisional |
| `source_revision` | `e2bfc0cf390a0a059fc04dce182082009e685a5b` | observed |
| `source_manifest` | binding modules below | observed |
| `source_hash` | `89a6021b186f1e1a0a86d02093e87bcb8616a84cb5b03071ad66e1ebfae1a987` | computed per SAC-v1 |
| `parameter_manifest` | class defaults below | observed from source |
| `parameter_hash` | `3ff061891488a9d9f5641cf147efc1e70c8d4cb8410540858d8b727bd485d1ab` | computed |
| `market_scope` | `UNBOUND_AT_ASSET`（CEMB-v1；EXP must declare） | protocol-bound |
| `execution_model` | partial signal/risk + CEMB cost/fill binding | see §2 |
| `evidence_lineage` | empty | Candidate-level only |
| `class_tags` | `["trend"]` | from SCAP admission |
| `context_independence` | attested independent at source classification | draft |
| `not_fabricated_for_context` | true（historical pre-RC001-B source） | draft |
| `architecture_attestation` | ADAP **T2 ACCEPT_TESTING_LEGACY** + **T4 REQUIRE_PAAF_REWRITE** for Bindable | frozen acceptance |

### Binding `source_manifest`

```json
[
  {
    "path": "strategies/brooks_scalp/__init__.py",
    "sha256": "3fe8ea0db447f6ed43a5fbb53400c98fe96aed308a070f0058661362ab76dea6"
  },
  {
    "path": "strategies/brooks_scalp/brooks_scalp.py",
    "sha256": "cff5bdbbd4495c7c0aa438c1747de9cbe997a18f53e868cd4f04e009b60d9a85"
  },
  {
    "path": "strategies/brooks_scalp/rollover_strategy.py",
    "sha256": "3bdb48813c05520f0b8ccc2f45c9146ef1968c6dafc2d8f22ebac88074a83149"
  }
]
```

Non-binding tooling（not in `source_hash`）:

```text
strategies/brooks_scalp/backtest.py
strategies/brooks_scalp/backtest_tick.py
```

### `parameter_manifest`（observed defaults）

```json
{
  "atr_period": {"type": "int", "unit": "bars", "value": 20},
  "ema_period": {"type": "int", "unit": "bars", "value": 20},
  "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
  "max_hold_bars": {"type": "int", "unit": "bars", "value": 10},
  "pullback_atr": {"type": "float", "unit": "atr_multiple", "value": 0.2},
  "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
  "trend_leg_atr": {"type": "float", "unit": "atr_multiple", "value": 1.0}
}
```

## 2. Execution model（observable + CEMB binding）

```text
signal_timeframe:     1m（docstring / on_bar; no BarGenerator）
order_style:          stop entry after pullback state
stop / target:        structural stop + 1R target（risk_reward=1.0）
time_stop:            max_hold_bars=10
sizing_rule_class:    fixed_size
cost_binding:         PROJECT_FROZEN_DATA_PROTOCOL → docs/07_DATA_SPEC.md v1.0.0
fill_binding:         VNPY_CTA_BACKTEST_ENGINE_DEFAULTS_AT_EXP_REGISTRATION
fee/slippage numbers: not invented in draft（resolved at EXP registration）
```

## 3. Architecture attestation（ADAP-v1）

```text
Target PAAF boundary:
  Context → Detector Registry → Risk → Execution → Logger

This source:
  legacy CtaTemplate encapsulates pattern FSM + entry + exits
  → ADAP T2 ACCEPT_TESTING_LEGACY
  → ADAP T4 REQUIRE_PAAF_REWRITE for Bindable
  → Bindable on these exact bytes: BLOCKED
```

## 4. Missing / blocking for Identity Freeze

```text
• asset-level or first-EXP market_scope package（currently UNBOUND_AT_ASSET）
• evidence_lineage for Testing path
• formal Identity Freeze authorization
• Bindable still blocked by T4 regardless
• working-tree loadability: CLEARED by path A restore（hashes MATCH）
```

```text
DRAFT_COMPLETE_FOR_REVIEW
        ≠
Identity Freeze
        ≠
Testing-eligible under SEVF-v1
        ≠
Bindable
```

## 5. Recovery decision

```text
recovery_mode: WORKING_TREE_RESTORE ✓（user path A · 2026-07-22）
Working tree: strategies/brooks_scalp/ PRESENT
Binding hashes: MATCH CID_001 source_manifest
Prior mode: REFERENCE_ONLY_IN_GIT（superseded for recovery status only）
```

## 6. Downstream charters

```text
Identity Freeze readiness: NOT READY
PAAF Rewrite Charter PRC-BROOKS_SCALP-v1: frozen design only
Implementation: NOT AUTHORIZED
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Identity Draft produced; recovery held as REFERENCE_ONLY_IN_GIT |
| 2026-07-22 | ADAP T2+T4 · CEMB cost/fill binding · Freeze readiness NOT READY |
| 2026-07-22 | User path A · WORKING_TREE_RESTORE complete · hashes MATCH |
