# Strategy Identity Freeze — STRAT_REV_OPP16_01@0.2.0

> **Type**: Candidate Identity Freeze（positioning / capital lineage）  
> **Status**: **FROZEN** ✓  
> **Freeze ID**: `SIF_CID_003_V0_2_0`  
> **Date**: 2026-07-23  
> **Authorization**: `Authorize Implementation of Positioning Lineage 0.2.0`（user: **A**）  
> **Parent**: `SIF_CID_003_V0_1_1` / `@0.1.1`（immutable · H_MECH Verified）  
> **Charter**: [`STRATEGY_PAAF_POSITIONING_CHARTER_OPP16_V020.md`](STRATEGY_PAAF_POSITIONING_CHARTER_OPP16_V020.md)

## Freeze record

```text
================================================
SIF_CID_003_V0_2_0

strategy_id: STRAT_REV_OPP16_01
version:     0.2.0
lifecycle:   Candidate（positioning / capital）
change:      risk-fraction sizing · hard_max_lots · equity kill-switch
detector:    OPP16@1.0.0（unchanged）
Bindable:    NO
Verified:    NO on RISK surface yet（needs H_CAPITAL_GATE EXP）
Alpha:       NONE
MECH @0.1.1: UNCHANGED（Verified H_MECH · E3 retained）
================================================
```

## 1. Frozen StrategyIdentity

| Field | Frozen value |
|-------|--------------|
| `strategy_id` | `STRAT_REV_OPP16_01` |
| `version` | `0.2.0` |
| `source_revision` | `120e604dd1fc2cb5dda85a69264e2ae10b537de3`（@0.2.0 positioning impl tip） |
| `git_anchor_head` | `120e604dd1fc2cb5dda85a69264e2ae10b537de3` |
| `source_hash` | `0e796e226b5906f22bdc4ce622f522788985a05525d2f65ae05e40fb2c474012` |
| `parameter_hash` | `fce3f995d1421ada2152e591362700ed2a24d93c7ff3259394261f254cd7aa22` |
| `market_scope` | `UNBOUND_AT_ASSET` |
| `detector_binding` | `OPP16@1.0.0` |
| `lineage_parent` | `SIF_CID_003_V0_1_1` |
| `evidence_lineage` | `[]` |
| `class_tags` | `["mean_reversion","reversal","positioning"]` |
| `context_independence` | `true` |
| `consumer_surface` | `RISK`（capital）· do not cite as MECH Verified |
| `campaign_id` | `CID_003` |

## 2. Frozen `source_manifest`

```json
[
  {
    "path": "strategies/paaf/adapters/vnpy_adapter.py",
    "sha256": "76d0257d457882f6076a75ea7c9ffb095d214c5b7d924d1a5b2a77f8da46e9d7"
  },
  {
    "path": "strategies/paaf/detectors/opp16_two_bar_reversal.py",
    "sha256": "ddb8378defa95ed1e2f3ccdd3cfd2ee3fbc25816a576524c21b6a42284ae9954"
  },
  {
    "path": "strategies/paaf/strat_rev_opp16_01.py",
    "sha256": "1a67cc5188514ef39e0db819a556b6c5435624b745b5f77e8aa9cd483d2c24d8"
  },
  {
    "path": "strategies/paaf/strat_rev_opp16_01_v011.py",
    "sha256": "8736f7ffc980b82d5e7d33e8bd7368c42e6457fc330f90b615f6185c2dc6b2c2"
  },
  {
    "path": "strategies/paaf/strat_rev_opp16_01_v020.py",
    "sha256": "6f69417c8ee7d1a26fb65eca6a30babb5cae114c792749b2f808a1b24388b3d5"
  }
]
```

## 3. Frozen `parameter_manifest`

```json
{
  "body_ratio": {"type": "float", "unit": "fraction", "value": 0.5},
  "capital_floor_ratio": {"type": "float", "unit": "fraction_of_capital", "value": 0.5},
  "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
  "hard_max_lots": {"type": "int", "unit": "contracts", "value": 1},
  "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
  "risk_per_trade": {"type": "float", "unit": "fraction_of_equity", "value": 0.005},
  "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
  "sizing_mode": {"type": "str", "unit": "enum", "value": "RISK_FRACTION_OF_CAPITAL"}
}
```

## 4. Execution model（delta vs @0.1.1）

```text
signal_timeframe:     5m（unchanged）
risk_timeframe:       1m（unchanged）+ equity kill-switch on 1m
order_entry:          stop · lots from _compute_lots（not bare fixed_size）
sizing:               RISK_FRACTION_OF_CAPITAL · hard_max_lots=1
kill:                 equity_est ≤ capital_floor_ratio × initial_capital
                      → flatten + halt entries；exit_reason may be KILL_SWITCH
rollover:             inherited on_rollover_adjust
```

## 5. Explicit non-grants

```text
❌ H_CAPITAL_GATE KEEP / Verified（needs new EXP）
❌ Bindable / Alpha / Production
❌ Rewrite @0.1.1 MECH Verified package
❌ Observation under this Freeze alone
```

## 6. Next（须另授）

```text
DONE: SEVF Spec V0_2_0 + Fill STRAT_RO16_EXP007 PRE-REGISTERED
Next: Authorize Offline Observation for STRAT_RO16_EXP007
  — OR — Pause CID_003
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | @0.2.0 Candidate Identity Freeze |
| 2026-07-23 | `source_revision` → `120e604dd1fc2cb5dda85a69264e2ae10b537de3` |
| 2026-07-23 | Next updated · EXP007 Fill PRE-REGISTERED |
