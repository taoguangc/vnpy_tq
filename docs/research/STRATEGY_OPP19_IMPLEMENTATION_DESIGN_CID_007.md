# PAAF OPP19 Implementation Design — CID_007

> **Type**: Implementation Design（≠ Observation · ≠ Alpha）  
> **Status**: **FROZEN** ✓  
> **Design ID**: `OID_CID_007_OPP19_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AE  
> **Parents**: `NSAD_CID_007_V0_1` · `OPP19_MS_V0_1`

## Design record

```text
================================================
OID_CID_007_OPP19_V0_1

Deliverables under this auth:
  • strategies/paaf/detectors/opp19_opening_drive_breakout.py
  • strategies/paaf/strat_sess_opp19_01.py
  • SIF_CID_007_V0_1 Identity Freeze
  • unit tests（FSM smoke）

OUT: Observation / SEVF Fill / H_EDGE / Bindable / Production / OD_REV
================================================
```

## Architecture

```text
Market Data → ContextEngine.update（orchestration only）
           → detector.note_bar_datetime(bar.datetime)
           → OPP19OpeningDriveBreakoutDetector.detect（ignores Context）
           → Strategy stop-entry / 1m risk
```

## Files

| Path | Role |
|------|------|
| `opp19_opening_drive_breakout.py` | Pure detector · OPP19@1.0.0 · explicit FSM |
| `strat_sess_opp19_01.py` | Orchestrator `STRAT_SESS_OPP19_01@0.1.0` |

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | OID FROZEN · Delegation-25AE |
