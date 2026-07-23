# Context × RISK Composition Design — CID_003

> **Type**: Composition Experiment Design（≠ Fill · ≠ Observation · ≠ Production）  
> **Status**: **DESIGNED** ✓ · **FROZEN**  
> **Design ID**: `CCRD_CID_003_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25I（`授权你决定25次`）  
> **Parents**: `CCED_CID_003_V0_1` · `BDR_CID_003_V0_1` · `SIF_CID_003_V0_2_0` · `PBDR_CID_003_V0_1` · Decision 019  
> **Closes（design-only）**: PBRR residual **R-CTX-RISK** design gap（EXP still OPEN）

## Design record

```text
================================================
CCRD_CID_003_V0_1

Purpose: Define how Filter F1 may compose with RISK @0.2.0
         under Decision 019 — without collapsing surfaces
         or claiming Alpha / Production.

Observation: CTX_CID003_EXP004 CLOSED KEEP（first composition EXP）
Production chase: remains PAUSED（PBDR WITHHOLD）
================================================
```

## 1. Why composition is now eligible

```text
MECH-only Context path COMPLETE for first continuity stack:
  EXP001 KEEP · EXP002 OOS KEEP · EXP003 multi-symbol KEEP

RISK @0.2.0 is Research Bindable · Verified H_CAPITAL_GATE E3

PBDR still WITHHOLDS Production — composition design ≠ Production unlock.
```

## 2. Bound objects（must not collapse）

| Layer | Binding | Role |
|-------|---------|------|
| Morphology | `OPP16@1.0.0` | unchanged |
| Signal / MECH parent | `@0.1.1` bytes | **not mutated** |
| Capital surface | `RISK` · `@0.2.0` · `SIF_CID_003_V0_2_0` | sizing · hard_max · kill-switch |
| Context | `A1-CTX-PS-v1.0.0` · `F1_EXPANSION_ONLY` | Filter / Permission only |
| Contract | `CC-CID_003-v1` | cite Surface=`RISK` when claims touch capital |

```text
Composition rule:
  Context decides ALLOW/DENY entry permission
  RISK decides size / halt / kill
  Context MUST NOT set lots or risk_per_trade
  RISK MUST NOT reinterpret Context state as edge score
```

## 3. Proposed adapter shape（implementation later）

```text
Opp16CtxFilterV020 = subclass StratRevOpp1601StrategyV020
  + same F1 / CXSD gate as Opp16CtxFilterV011
  + override _submit_stop_entry only（permission before super）
  + MUST NOT edit strat_rev_opp16_01.py / _v011.py / _v020.py G5 bytes

experiment_id stamped per Fill（e.g. CTX_CID003_EXP004）
```

## 4. First composition hypothesis family（not filled）

```text
H_CTX_RISK_COMP（shape）:
  Under declared scope and frozen RISK @0.2.0 identity,
  applying Filter F1 changes the auditable allowed-entry /
  closed-trade set vs unfiltered RISK baseline（N0/N1/D）
  while:
    • Context never generates entries
    • Context never supplies sizing alpha
    • RISK sizing / kill-switch remain the only capital controls
```

```text
PnL / Sharpe MUST NOT be the primary KEEP/REVERT gate.
Kill-switch trips are descriptive attribution · not Alpha.
```

## 5. Mandatory bindings when Fill later authorized

```text
• new experiment_id（suggested: CTX_CID003_EXP004）
• RISK source_hash / parameter_hash from SIF_CID_003_V0_2_0
• Surface ID = RISK in all metadata
• Filter F1 identical to EXP001–003
• docs/07 data protocol · pre-registered decision rule
• Adapter subclass only · G5 RISK/MECH binding files untouched
```

## 6. Suggested first scope（Fill-time · not authorized now）

| Field | Suggested default |
|-------|-------------------|
| symbol | `rb`（single-symbol first） |
| period | `2024` |
| arms | B0=`V020` · B1=`Opp16CtxFilterV020` |
| continuity later | OOS / multi-symbol = new EXP ids |

## 7. Explicit non-claims / non-grants

```text
❌ Observation / KEEP under this design alone
❌ Production Bindable / E4 / live Context routing
❌ Alpha / H_EDGE reopen
❌ Collapse MECH KEEP + RISK KEEP + CTX KEEP into one edge story
❌ Mutate @0.2.0 Verified bytes to “fit” Context
```

## 8. Status

```text
DESIGN: FROZEN · CCRD_CID_003_V0_1
CTX_CID003_EXP004: CLOSED · KEEP（rb/2024 · RISK · F1）
CTX_CID003_EXP005: CLOSED · KEEP（rb/2025 temporal OOS · RISK · F1）
Further composition EXPs: new experiment_id + authorization required
Production chase: PAUSED（PBDR_CID_003_V0_1）
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | Design FROZEN under Delegation-25I |
| 2026-07-23 | CTX_CID003_EXP004 KEEP · CLOSED（Delegation-25J） |
| 2026-07-23 | CTX_CID003_EXP005 KEEP · CLOSED（Delegation-25K） |
