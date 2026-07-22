# SEVF Fill — STRAT_BS02_EXP005（H_MECH smoke · v0.1.1）

> **Status**: **PRE-REGISTERED** ✓  
> **Experiment ID**: `STRAT_BS02_EXP005`  
> **Identity**: `SIF_CID_002_V0_1_1`（@0.1.1）  
> **Authorization**: Delegation-50B  
> **Purpose**: Mechanism smoke after rollover repair（not Alpha）

## Hypothesis（H_MECH）

> Under rb/2024 and docs/07, `STRAT_TREND_BROOKS_SCALP_02@0.1.1` produces ≥1 auditable closed round-trip with exit_reason ∈ {STOP,TARGET,TIME_STOP}, identity hashes match freeze, and the run does **not** emit the missing-`on_rollover_adjust` WARN.

## Scope

Same as EXP001（continuity）: rb · 2024-01-01..2024-12-31 · warmup 2023-12-01.

## Decision rule

| Outcome | Rule |
|---------|------|
| KEEP | EXP001 H_MECH audit rule **and** no `未实现 on_rollover_adjust` WARN in engine output |
| HOLD | zero trades or incomplete audit（but hook present） |
| REVERT | hash mismatch **or** missing-hook WARN still present **or** no detector attribution |

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Pre-registered under Delegation-50B |
