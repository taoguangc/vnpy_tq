# PAAF OPP17 Implementation Design — CID_005

> **Type**: Implementation Design（≠ Observation · ≠ Alpha）  
> **Status**: **FROZEN** ✓  
> **Design ID**: `OID_CID_005_OPP17_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25T  
> **Parents**: `NSAD_CID_005_V0_1` · `OPP17_MS_V0_1`

## Design record

```text
================================================
OID_CID_005_OPP17_V0_1

Deliverables under this auth:
  • strategies/paaf/detectors/opp17_climax_reversal.py
  • strategies/paaf/strat_rev_opp17_01.py
  • SIF_CID_005_V0_1 Identity Freeze
  • unit tests（morphology smoke）

OUT: Observation / SEVF Fill / H_EDGE / Bindable / Production
================================================
```

## Architecture

```text
Market Data → ContextEngine.update（orchestration only）
           → OPP17ClimaxReversalDetector.detect（ignores Context）
           → Strategy stop-entry / 1m risk
           → trade log
```

## Files

| Path | Role |
|------|------|
| `opp17_climax_reversal.py` | Pure detector · OPP17@1.0.0 |
| `strat_rev_opp17_01.py` | Orchestrator `STRAT_REV_OPP17_01@0.1.0` |

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | OID FROZEN · Delegation-25T |
