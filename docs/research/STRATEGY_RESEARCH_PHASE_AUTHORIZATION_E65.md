# Strategy Research Phase — Authorization（Epoch 6.5）

> **Type**: Phase Authorization（≠ Observation · ≠ Alpha claim · ≠ Production）  
> **Status**: **GRANTED** ✓（**Design scope**）  
> **Date**: 2026-07-23  
> **Command**: `Authorize Offline Alpha Evidence Research Design`  
> **User rationale**: Alpha is now the largest unknown; defer Epoch 7 / Production / CSD mainline  
> **Positioning**: [`EPOCH_6_5_POSITIONING.md`](../releases/EPOCH_6_5_POSITIONING.md)  
> **Design**: [`STRATEGY_ALPHA_EVIDENCE_RESEARCH_DESIGN_CID_002.md`](STRATEGY_ALPHA_EVIDENCE_RESEARCH_DESIGN_CID_002.md)

## Authorization Record（binding）

```text
================================================
Authorize Offline Alpha Evidence Research Design
→ Epoch 6.5 Strategy Alpha Validation

Decision: GRANTED ✓（Design only）

Active Phase:     Offline Alpha Evidence Research（Design）
Epoch 6 toolkit:  remains CLOSED（E6C_RT_V0_1）
Epoch 7:          remains POSITIONED · NOT ACTIVE
CSD impl:         NOT authorized（CSDIC insufficient）

Alpha claim:      NONE（Design does not admit Alpha）
Production:       WITHHELD · not this phase
================================================
```

## 1. What this authorizes

```text
Allows:
  · Epoch 6.5 positioning
  · Alpha Evidence Research Design（H_EDGE layers · gates · route）
  · Documentation of Candidate vs Verified thresholds
  · Planning new experiment_id families（no run yet）

Does NOT authorize（this command alone）:
  · Observation / backtest / CSV generation
  · Parameter search / PnL chase
  · Mutating CID_002 frozen identity bytes
  · Alpha Candidate / Alpha Verified stamps
  · Epoch 7 / Production Bindable / live
  · CSD Implementation
```

## 2. Scope constraints（user-stated）

```text
✓ Do not change CID_002 binding identity for Closed evidence
✓ New experiment_id for any future Alpha/edge EXPs
✓ No parameter optimization
✓ PnL not used as tuning objective
✓ Goal = judge Alpha Candidate existence（not maximize return）
```

## 3. Priority order（accepted）

| Priority | Work | Role |
|----------|------|------|
| 1 | Alpha Evidence Research | Largest unknown |
| 2 | New strategy asset research | After/ beside FAIL or capacity |
| 3 | CSD | Engineering · deferred |
| 4 | Production Bindable | Last |

## 4. Next command（when Design accepted）

```text
Authorize SEVF Fill for H_EDGE / STRAT_BS02_EXP0xx
  — OR — Authorize Offline Alpha Evidence Observation
  — OR — revise Design first
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | GRANTED · Design scope |
