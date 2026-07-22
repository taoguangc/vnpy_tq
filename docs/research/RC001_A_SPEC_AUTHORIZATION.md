# RC001-A — Controlled Experiment Spec Authorization

> **Type**: Explicit Spec Authorization（≠ Spec Confirmation · ≠ Execution · ≠ Backtest）  
> **Status**: **GRANTED** ✓ · Spec **WRITTEN** · Confirmation **PENDING**  
> **Date**: 2026-07-21  
> **Command**: `Authorize RC001-A Controlled Experiment Spec`  
> **Prerequisite**: [`RC001_A_CONTRACT_REVIEW.md`](RC001_A_CONTRACT_REVIEW.md) — **PASS**  
> **Spec**: [`RC001_A_CONTROLLED_EXPERIMENT_SPEC.md`](RC001_A_CONTROLLED_EXPERIMENT_SPEC.md)

### Authorization（binding）

```text
================================================
Authorize RC001-A Controlled Experiment Spec

Decision: GRANTED ✓

Allows:
  - Freeze RQ / Dataset / Universe / Window
  - Freeze CTRL/FILT execution protocol
  - Freeze Evaluation Contract + Outcome Mapping
  - Freeze Negative Evidence handling

Does NOT authorize:
  - Spec Confirmation（separate）
  - Execution Authorization
  - Backtest
  - Parameter / Filter / OPP16 modification
  - Return optimization
================================================
```
