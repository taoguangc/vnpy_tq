# PAAF OPP12 Implementation Design — CID_004

> **Type**: Implementation Design（≠ Observation · ≠ Alpha）  
> **Status**: **FROZEN** ✓  
> **Design ID**: `OID_CID_004_OPP12_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25O  
> **Parents**: `NSAD_CID_004_V0_1` · `OPP12_MS_V0_1`

## Design record

```text
================================================
OID_CID_004_OPP12_V0_1

Deliverables under this auth:
  • strategies/paaf/detectors/opp12_overshoot_fail.py
  • strategies/paaf/strat_rev_opp12_01.py
  • SIF_CID_004_V0_1 Identity Freeze
  • unit tests（morphology smoke）

OUT: Observation / SEVF Fill / H_EDGE / Bindable / Production
================================================
```

## Architecture

```text
Market Data → ContextEngine.update（orchestration only）
           → OPP12OvershootFailDetector.detect（ignores Context）
           → Strategy stop-entry / 1m risk
           → trade log
```

## Files

| Path | Role |
|------|------|
| `opp12_overshoot_fail.py` | Pure detector · OPP12@1.0.0 |
| `strat_rev_opp12_01.py` | Orchestrator `STRAT_REV_OPP12_01@0.1.0` |

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | OID FROZEN · Delegation-25O |
